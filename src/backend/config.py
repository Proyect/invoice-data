from decouple import config
import os

# JWT Settings
SECRET_KEY_JWT = config("SECRET_KEY_JWT", default="your_super_secret_jwt_key_here_make_it_long_and_random_123456789")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)

# Database Settings
DATABASE_URL = config("DATABASE_URL", default="sqlite:///./test.db")

# Redis Settings (para RQ)
REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_DB = config("REDIS_DB", default=0, cast=int)
REDIS_URL = config("REDIS_URL", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

# YOLO models path - CORREGIDO PARA WINDOWS LOCAL
YOLO_MODELS_PATH = config("YOLO_MODELS_PATH", default=r"C:\Users\amdiaz\Desktop\code\Python\v.13.13\invoice-data\src\backend\models\yolo_models")

# Project Root
PROJECT_ROOT = config("PROJECT_ROOT", default=r"C:\Users\amdiaz\Desktop\code\Python\v.13.13\invoice-data\src\backend")

# Storage Settings
LOCAL_STORAGE_PATH = config("LOCAL_STORAGE_PATH", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploaded_documents_local"))
