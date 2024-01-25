import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'album_project.settings')
import django
django.setup()

from django.utils import timezone
from faker import Faker
from random import choice
from album_app.models import PhotoTable, Board, UsersAppUser, Liked, Reply

fake = Faker()

def generate_fake_photos(number=10):
    for _ in range(number):
        phototag = fake.word()
        photodate = fake.date_time_this_decade()
        uploaddate = fake.date_time_this_decade()

        # Generate a random image URL from Lorem Picsum
        image_url = f'https://picsum.photos/200/300/?random={fake.random_int(min=1, max=1000)}'

        new_photo = PhotoTable(
            phototag=phototag,
            photodate=photodate,
            uploaddate=uploaddate,
            image=image_url
        )
        new_photo.save()

def generate_fake_boards(number=10):
    photos = PhotoTable.objects.all()

    for _ in range(number):
        title = fake.sentence()
        contents = fake.paragraph()
        user = choice(UsersAppUser.objects.all())
        created_time = fake.date_time_this_decade()
        photo = choice(photos)

        new_board = Board(
            title=title,
            contents=contents,
            id=user,
            created_time=created_time,
            photoid=photo
        )
        new_board.save()


def generate_fake_users(number=5):
    for _ in range(number):
        username = fake.user_name()
        email = fake.email()
        password = fake.password()

        new_user = UsersAppUser(
            username=username,
            email=email,
            password=password,
            date_joined=timezone.now(),
            is_superuser=fake.boolean(chance_of_getting_true=50),
            is_staff=fake.boolean(chance_of_getting_true=50),
            is_active=True  # You can modify this value based on your needs
        )
        new_user.save()

def generate_fake_data():
    generate_fake_users()
    generate_fake_photos()
    generate_fake_boards()

if __name__ == "__main__":
    generate_fake_data()