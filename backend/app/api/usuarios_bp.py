from flask import Blueprint, jsonify, request
from backend.data import USUARIOS_DB, PERFIS_DB

usuarios_bp = Blueprint("usuarios_bp", __name__)


@usuarios_bp.route("/api/usuarios", methods=["GET", "POST"])
def gerenciar_usuarios():
    if request.method == "POST":
        data = request.json or {}
        novo = {
            "id": len(USUARIOS_DB) + 1,
            "nome": data.get("nome", "Novo Usuário"),
            "email": data.get("email", ""),
            "perfil": data.get("perfil", "Operação"),
            "telas_custom": None,
            "criar_perfis_tela": False
        }
        USUARIOS_DB.append(novo)
        return jsonify(novo), 201

    return jsonify(USUARIOS_DB)


@usuarios_bp.route("/api/usuarios/<int:user_id>/permissoes", methods=["PUT"])
def atualizar_permissoes_usuario(user_id):
    user = next((u for u in USUARIOS_DB if u["id"] == user_id), None)
    if not user:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    data = request.json or {}
    user["telas_custom"] = data.get("telas", [])
    return jsonify(user)


@usuarios_bp.route("/api/perfis", methods=["GET"])
def listar_perfis():
    return jsonify(PERFIS_DB)


@usuarios_bp.route("/api/perfis/<nome_perfil>/permissoes", methods=["PUT"])
def atualizar_permissoes(nome_perfil):
    if nome_perfil not in PERFIS_DB:
        return jsonify({"erro": "Perfil não encontrado"}), 404
    data = request.json or {}
    PERFIS_DB[nome_perfil]["telas"] = data.get("telas", [])
    return jsonify(PERFIS_DB[nome_perfil])
