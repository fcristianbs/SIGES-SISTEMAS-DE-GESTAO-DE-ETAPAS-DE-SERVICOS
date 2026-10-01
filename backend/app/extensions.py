from flask_cors import CORS

cors = CORS()

def init_extensions(app):
    """Inicializa as extensões do Flask na aplicação"""
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
