import os
from flask import Flask, send_from_directory
from backend.app.config import config_by_name
from backend.app.database.connection import init_db_pool
from backend.app.extensions import init_extensions
from backend.app.api import register_blueprints
from backend.app.core.exceptions import register_error_handlers


def create_app(config_name="default"):
    """
    Application Factory Pattern para o SIGES.
    Cria e configura a instância da aplicação Flask.
    """
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
    
    app = Flask(__name__, static_folder=frontend_dir)
    
    # 1. Carrega configurações do ambiente
    cfg = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(cfg)
    
    # 2. Inicializa o Pool de Conexões persistente
    init_db_pool(cfg)
    
    # 3. Inicializa extensões (CORS, etc.)
    init_extensions(app)
    
    # 4. Registra os Blueprints modulares
    register_blueprints(app)
    
    # 5. Registra Global Error Handlers
    register_error_handlers(app)
    
    # 6. Rotas para entrega do Frontend estático (Desenvolvimento Local)
    @app.route("/")
    def serve_root():
        return send_from_directory(app.static_folder, "login.html")

    @app.route("/<path:path>")
    def serve_static(path):
        if os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "login.html")

    return app
