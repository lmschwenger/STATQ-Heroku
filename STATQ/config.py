import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    try:
       SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://','postgresql://') 
    except:
       'sqlite:///site.db'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    ALLOWED_FILE_EXTENSIONS = ["CSV"]
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    print(str(MAIL_SERVER)+'...'+str(MAIL_USERNAME)+'...'+str(MAIL_PASSWORD))
