from decouple import config
import os

# JWT Settings
SECRET_KEY_JWT = config("SECRET_KEY_JWT")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)

# Database Settings
DATABASE_URL = config("DATABASE_URL")

# Redis Settings (para RQ)
REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_DB = config("REDIS_DB", default=0, cast=int)
REDIS_URL = config("REDIS_URL", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

#YOLO models path
YOLO_MODELS_PATH = config("YOLO_MODELS_PATH", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models/yolo_models'))    

# Project Root
PROJECT_ROOT= config("PROJECT_ROOT", default=os.path.join(os.path.dirname(os.path.abspath(__file__))))


# Storage Settings
# si es necesario implementar
LOCAL_STORAGE_PATH = config("LOCAL_STORAGE_PATH", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploaded_documents_local"))
# S3_BUCKET_NAME = config("S3_BUCKET_NAME", default="your-s3-bucket")
# AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
# AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")