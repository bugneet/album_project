DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",  # 엔진
        "NAME": "final_project_db",  # 데이터베이스 이름
        "USER": "root",  # 사용자
        "PASSWORD": "1234",  # 비밀번호
        "HOST": "localhost",  # 호스트
        "PORT": "3306",  # 포트번호
    }
}

# SECRET_KEY
# settings.py 에서 복사하고
# settings.py 의 SECRET_KEY는 주석 처리함
SECRET_KEY = "django-insecure-k#&pt4nsw+oqr7n*x68xdpcj&ri(gj@=@&6ss4&j+8wb_$53km"
