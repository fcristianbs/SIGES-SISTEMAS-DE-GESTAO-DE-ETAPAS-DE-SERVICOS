from flask import jsonify

def register_error_handlers(app):
    """Registra manipuladores globais de erro para respostas JSON padronizadas"""
    
    @app.errorhandler(400)
    def bad_request(error):
        msg = getattr(error, "description", "Requisição inválida.")
        return jsonify({"status": "erro", "codigo": 400, "mensagem": msg}), 400

    @app.errorhandler(404)
    def not_found(error):
        msg = getattr(error, "description", "Recurso não encontrado.")
        return jsonify({"status": "erro", "codigo": 404, "mensagem": msg}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"status": "erro", "codigo": 500, "mensagem": "Erro interno do servidor."}), 500
