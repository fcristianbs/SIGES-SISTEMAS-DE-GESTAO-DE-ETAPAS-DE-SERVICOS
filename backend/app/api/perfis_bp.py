from flask import Blueprint, jsonify, request
from backend.data import USUARIOS_DB
from backend.app.database.repositories.perfis_repo import (
    listar_perfis_tela,
    criar_perfil_tela,
    obter_perfil_tela_por_id,
    atualizar_perfil_tela,
    listar_todos_perfis_tela,
    obter_perfis_vinculados_usuario,
    atualizar_perfis_usuario
)

perfis_bp = Blueprint("perfis_bp", __name__)


@perfis_bp.route("/api/perfis_tela", methods=["GET"])
def get_perfis_tela():
    user_id = int(request.args.get("user_id", 0))
    user = next((u for u in USUARIOS_DB if u["id"] == user_id), None)
    can_create_global = bool(user and user.get("criar_perfis_tela"))

    rows = listar_perfis_tela(user_id, can_create_global=can_create_global)
    return jsonify(rows)


@perfis_bp.route("/api/perfis_tela", methods=["POST"])
def post_perfil_tela():
    data = request.json or {}
    user_id = int(data.get("criado_por_id", 0))
    user = next((u for u in USUARIOS_DB if u["id"] == user_id), None)
    
    if not user:
        return jsonify({"erro": "Usuário não autenticado ou inválido"}), 401

    nome = data.get("nome", "Novo Perfil")
    colunas_visiveis = data.get("colunas_visiveis", [])
    tipo_solicitado = data.get("tipo", "privado")
    tipo = tipo_solicitado if user.get("criar_perfis_tela") else "privado"

    try:
        resultado = criar_perfil_tela(
            nome=nome,
            colunas_visiveis=colunas_visiveis,
            criado_por_id=user_id,
            tipo=tipo
        )
        return jsonify(resultado), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@perfis_bp.route("/api/perfis_tela/<int:perfil_id>", methods=["PUT"])
def put_perfil_tela(perfil_id):
    data = request.json or {}
    user_id = int(data.get("user_id", 0))
    user = next((u for u in USUARIOS_DB if u["id"] == user_id), None)
    
    if not user:
        return jsonify({"erro": "Não autorizado"}), 401

    perfil = obter_perfil_tela_por_id(perfil_id)
    if not perfil:
        return jsonify({"erro": "Perfil não encontrado"}), 404
    
    if perfil['tipo'] == 'global' and not user.get("criar_perfis_tela"):
        return jsonify({"erro": "Você não tem permissão para editar um perfil global."}), 403

    colunas_visiveis = data.get("colunas_visiveis", [])
    try:
        atualizar_perfil_tela(perfil_id, colunas_visiveis)
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@perfis_bp.route("/api/perfis_tela/todos", methods=["GET"])
def get_todos_perfis_tela():
    rows = listar_todos_perfis_tela()
    return jsonify(rows)


@perfis_bp.route("/api/usuarios/<int:user_id>/perfis_tela", methods=["GET"])
def get_perfis_usuario(user_id):
    ids = obter_perfis_vinculados_usuario(user_id)
    return jsonify(ids)


@perfis_bp.route("/api/usuarios/<int:user_id>/perfis_tela", methods=["PUT"])
def put_perfis_usuario(user_id):
    data = request.json or {}
    perfis = data.get("perfis", [])
    try:
        atualizar_perfis_usuario(user_id, perfis)
        return jsonify({"status": "sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
