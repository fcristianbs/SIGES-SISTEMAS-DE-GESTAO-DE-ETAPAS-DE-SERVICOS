import os
from flask import Blueprint, jsonify, request
from backend.data import USUARIOS_DB, PERFIS_DB

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    
    user = next((u for u in USUARIOS_DB if u["email"].lower() == email), None)
    if not user:
        user = {
            "id": len(USUARIOS_DB) + 1,
            "nome": email.split("@")[0].title(),
            "email": email,
            "perfil": "Master",
            "telas_custom": None,
            "criar_perfis_tela": True
        }
        USUARIOS_DB.append(user)

    perfil = PERFIS_DB.get(user["perfil"], PERFIS_DB["Master"])

    return jsonify({
        "status": "sucesso",
        "usuario": user,
        "perfil": perfil
    })


@auth_bp.route("/api/status", methods=["GET"])
def status_api():
    return jsonify({
        "app": "SIGES - Sistema de Gestão de Etapas de Serviços",
        "status": "online",
        "database_raw": "siges",
        "database_app": os.getenv("DB_APP_NAME", "siges_app")
    })
