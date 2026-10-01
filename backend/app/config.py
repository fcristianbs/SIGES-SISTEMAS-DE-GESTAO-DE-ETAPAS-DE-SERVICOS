import os
from dotenv import load_dotenv

# Carrega .env da raiz do projeto caso exista
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
env_path = os.path.join(base_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)


class Config:
    """Configurações base compartilhadas por todos os ambientes"""
    SECRET_KEY = os.getenv("SECRET_KEY", "siges-secret-production-key-2026")
    
    # Configurações do Banco MySQL secundário (siges_app)
    DB_HOST = os.getenv("DB_HOST", "operacao.vps-cosampa.online")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_APP_NAME = os.getenv("DB_APP_NAME", "siges_app")
    
    # Pool de Conexão
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 20))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", 1800))
    
    # Uploads temporários
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(base_dir, "scratch", "uploads"))
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024  # 64 MB max upload


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento local"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuração para produção na VPS (Gunicorn + Caddy)"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuração para execução de testes automatizados"""
    DEBUG = True
    TESTING = True


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}
