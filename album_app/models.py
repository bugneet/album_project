from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)    
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.OneToOneField('UsersAppUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'authtoken_token'

        
class Board(models.Model):
    board_no = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    contents = models.TextField()
    id = models.ForeignKey('UsersAppUser', models.DO_NOTHING, db_column='id', blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)
    photoid = models.ForeignKey('PhotoTable', models.DO_NOTHING, db_column='photoid', blank=True, null=True)
    board_photo_tag = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'board'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UsersAppUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Liked(models.Model):
    likeno = models.AutoField(primary_key=True)
    board_no = models.ForeignKey(Board, models.DO_NOTHING, db_column='board_no', related_name='liked_posts')
    id = models.ForeignKey('UsersAppUser', models.DO_NOTHING, db_column='id')
    likedate = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'liked'


class PhotoTable(models.Model):
    photoid = models.AutoField(primary_key=True)
    photohash = models.CharField(max_length=50)
    phototag = models.CharField(max_length=200, blank=True, null=True)
    photodate = models.DateTimeField(blank=True, null=True)
    uploaddate = models.DateTimeField(blank=True, null=True)
    image = models.CharField(max_length=200, blank=True, null=True)
    id = models.ForeignKey('UsersAppUser', models.DO_NOTHING, db_column='id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'photo_table'


class RecommendContents(models.Model):
    contents_id = models.AutoField(primary_key=True)
    phototag = models.CharField(max_length=50, blank=True, null=True)       
    contents_name = models.CharField(max_length=100)
    contents_link = models.CharField(max_length=100, blank=True, null=True) 
    contents_image = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recommend_contents'


class Reply(models.Model):
    rno = models.AutoField(primary_key=True)
    board_no = models.ForeignKey(Board, models.DO_NOTHING, db_column='board_no',  related_name='replies')
    replytext = models.CharField(max_length=1000)
    id = models.ForeignKey('UsersAppUser', models.DO_NOTHING, db_column='id')
    regdate = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reply'


class UsersAppUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    user_name = models.CharField(max_length=30)
    user_address = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'users_app_user'


class UsersAppUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UsersAppUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_app_user_groups'
        unique_together = (('user', 'group'),)


class UsersAppUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UsersAppUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_app_user_user_permissions'
        unique_together = (('user', 'permission'),)

class Photo(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='Upload/') 

    def __str__(self):
        return self.title
