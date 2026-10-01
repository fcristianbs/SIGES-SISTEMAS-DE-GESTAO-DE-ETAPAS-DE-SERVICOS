from backend.app.api.auth_bp import auth_bp
from backend.app.api.servicos_bp import servicos_bp
from backend.app.api.tramitacao_bp import tramitacao_bp
from backend.app.api.faturamento_bp import faturamento_bp
from backend.app.api.conciliacao_bp import conciliacao_bp
from backend.app.api.perfis_bp import perfis_bp
from backend.app.api.colaboracao_bp import colaboracao_bp
from backend.app.api.importacao_bp import importacao_bp
from backend.app.api.dashboard_bp import dashboard_bp
from backend.app.api.usuarios_bp import usuarios_bp


def register_blueprints(app):
    """Registra todos os Blueprints na aplicação Flask"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(servicos_bp)
    app.register_blueprint(tramitacao_bp)
    app.register_blueprint(faturamento_bp)
    app.register_blueprint(conciliacao_bp)
    app.register_blueprint(perfis_bp)
    app.register_blueprint(colaboracao_bp)
    app.register_blueprint(importacao_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(usuarios_bp)
