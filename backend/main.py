from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys

# Carrega variáveis de ambiente do arquivo .env caso exista
try:
    from dotenv import load_dotenv
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(root_dir, '.env'))
except ImportError:
    pass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data import PERFIS_DB, USUARIOS_DB, SERVICOS_DB
from db import buscar_servicos_db
from etl_sync import executar_bootstrap_30dias, executar_sincronizacao_incremental

app = Flask(__name__, static_folder="../frontend")
CORS(app)

@app.route("/")
def serve_root():
    return send_from_directory(app.static_folder, "login.html")

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "login.html")

@app.route("/api/auth/login", methods=["POST"])
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
            "telas_custom": None
        }
        USUARIOS_DB.append(user)

    perfil = PERFIS_DB.get(user["perfil"], PERFIS_DB["Master"])

    return jsonify({
        "status": "sucesso",
        "usuario": user,
        "perfil": perfil
    })

@app.route("/api/status", methods=["GET"])
def status_api():
    return jsonify({
        "app": "SIGES - API Flask Enxuta",
        "status": "online",
        "database_raw": os.getenv("DB_NAME", "siges"),
        "database_app": "siges_app"
    })

# --- ENDPOINTS PIPELINE ETL DE INGESTÃO (siges -> siges_app) ---
@app.route("/api/etl/sync", methods=["POST"])
def disparar_etl_sync():
    data = request.json or {}
    tipo_sync = data.get("tipo", "bootstrap") # 'bootstrap' ou 'incremental'

    if tipo_sync == "incremental":
        res = executar_sincronizacao_incremental()
    else:
        res = executar_bootstrap_30dias(limit=data.get("limit", 300))

    return jsonify(res)

@app.route("/api/servicos", methods=["GET"])
def listar_servicos():
    contrato = request.args.get("contrato", "todos")
    tipo = request.args.get("tipo", "todos")
    status_id = request.args.get("status_id", "todos")
    busca = request.args.get("busca", "")

    # Busca estritamente do banco real MySQL siges (retorna [] se vazio, sem alternar para mocks)
    dados_reais = buscar_servicos_db(contrato=contrato, tipo=tipo, status_id=status_id, busca=busca)
    resultado = dados_reais if dados_reais is not None else []

    return jsonify(resultado)

@app.route("/api/dashboard/kpis", methods=["GET"])
def kpis():
    dados_reais = buscar_servicos_db(limit=500)
    base = dados_reais if dados_reais is not None else []
    ativos = [s for s in base if s.get("st", 1) not in (13, 14, 15)]
    valor_total = sum(s.get("v", 0) for s in ativos)
    estourados = [s for s in ativos if s.get("d", 0) > 5]
    return jsonify({
        "servicos_ativos": len(ativos),
        "valor_esteira": valor_total,
        "sla_estourado_count": len(estourados),
        "total_geral": len(base)
    })

@app.route("/api/usuarios", methods=["GET", "POST"])
def gerenciar_usuarios():
    if request.method == "POST":
        data = request.json or {}
        novo = {
            "id": len(USUARIOS_DB) + 1,
            "nome": data.get("nome", "Novo Usuário"),
            "email": data.get("email", ""),
            "perfil": data.get("perfil", "Operação"),
            "telas_custom": None
        }
        USUARIOS_DB.append(novo)
        return jsonify(novo), 201

    return jsonify(USUARIOS_DB)

@app.route("/api/usuarios/<int:user_id>/permissoes", methods=["PUT"])
def atualizar_permissoes_usuario(user_id):
    user = next((u for u in USUARIOS_DB if u["id"] == user_id), None)
    if not user:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    data = request.json or {}
    user["telas_custom"] = data.get("telas", [])
    return jsonify(user)

@app.route("/api/perfis", methods=["GET"])
def listar_perfis():
    return jsonify(PERFIS_DB)

@app.route("/api/perfis/<nome_perfil>/permissoes", methods=["PUT"])
def atualizar_permissoes(nome_perfil):
    if nome_perfil not in PERFIS_DB:
        return jsonify({"erro": "Perfil não encontrado"}), 404
    data = request.json or {}
    PERFIS_DB[nome_perfil]["telas"] = data.get("telas", [])
    return jsonify(PERFIS_DB[nome_perfil])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"Servidor Flask SIGES iniciado em http://localhost:{port}")
    app.run(debug=True, host="0.0.0.0", port=port)
