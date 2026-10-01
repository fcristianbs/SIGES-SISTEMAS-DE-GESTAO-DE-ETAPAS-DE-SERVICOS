from flask import Blueprint, jsonify, request
from backend.app.database.repositories.auditoria_repo import (
    buscar_logs_auditoria,
    buscar_comentarios,
    inserir_comentario
)

colaboracao_bp = Blueprint("colaboracao_bp", __name__)


@colaboracao_bp.route("/api/servicos/<servico_id>/auditoria", methods=["GET"])
def obter_logs_auditoria_rota(servico_id):
    logs = buscar_logs_auditoria(servico_id)
    return jsonify(logs)


@colaboracao_bp.route("/api/servicos/<servico_id>/comentarios", methods=["GET"])
def obter_comentarios_rota(servico_id):
    comentarios = buscar_comentarios(servico_id)
    return jsonify(comentarios)


@colaboracao_bp.route("/api/servicos/<servico_id>/comentarios", methods=["POST"])
def adicionar_comentario_rota(servico_id):
    data = request.json or {}
    usuario_id = data.get("usuario_id")
    usuario_nome = data.get("usuario_nome")
    texto = data.get("texto", "").strip()
    
    if not usuario_id or not texto:
        return jsonify({"status": "erro", "mensagem": "Usuário e texto são obrigatórios."}), 400
        
    res = inserir_comentario(servico_id, usuario_id, usuario_nome, texto)
    if res["status"] == "sucesso":
        return jsonify(res), 201
    return jsonify(res), 500
