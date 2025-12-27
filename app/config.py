import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    PROJECT_NAME = os.getenv('PROJECT_NAME', 'TradeFlow AI')
    VERSION = os.getenv('VERSION', '1.0.0')
    API_V1_STR = os.getenv('API_V1_STR', '/api')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://tvk002006_db_user:iamdariyalmogger@mogger.zfl7uwb.mongodb.net/?appName=mogger')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'tradeflow')
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    STORAGE_BUCKET = os.getenv('STORAGE_BUCKET')
    STORAGE_REGION = os.getenv('STORAGE_REGION')
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    ENABLE_AI_EXTRACTION = os.getenv('ENABLE_AI_EXTRACTION', 'True').lower() == 'true'
    
    REDIS_URL = os.getenv('REDIS_URL')
    
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    EMAIL_FROM = os.getenv('EMAIL_FROM')
    ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'False').lower() == 'true'
    ENABLE_SMS_NOTIFICATIONS = os.getenv('ENABLE_SMS_NOTIFICATIONS', 'False').lower() == 'true'
    
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173')
    
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 100))

