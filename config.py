import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    
class Config:
    # Базовые настройки
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    
    # Настройки SQLite по умолчанию
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///links.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    # Специфические настройки для разработки
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_links.db'


class ProductionConfig(Config):
    # Настройки для MySQL
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:"
        f"{os.environ.get('DB_PASSWORD', '')}@"
        f"{os.environ.get('DB_HOST', 'localhost')}/"
        f"{os.environ.get('DB_NAME', 'links_db')}"
    )
    DEBUG = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_links.db'


# Выбор конфигурации
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'test': TestConfig
}
