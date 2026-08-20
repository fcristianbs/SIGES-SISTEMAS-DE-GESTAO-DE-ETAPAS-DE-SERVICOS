from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys

# Garante a importação do módulo data.py independente de onde o servidor for executado
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data import PERFIS_DB, USUARIOS_DB, SERVICOS_DB

app = Flask(__name__, static_folder="../frontend")
CORS(app) # Habilita CORS para requisições do front-end SPA

# --- ROTA DE SERVIR PÁGINAS E ARQUIVOS ESTÁTICOS DO FRONTEND ---
@app.route("/")
def serve_root():
    return send_from_directory(app.static_folder, "login.html")

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "login.html")

# --- ENDPOINT DE AUTENTICAÇÃO / LOGIN ---
@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    
    # Busca usuário cadastrado ou cria sessão de teste
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

# --- ENDPOINTS FLASK REST API ---
@app.route("/api/status", methods=["GET"])
def status_api():
    return jsonify({"app": "SIGES - API Flask Enxuta", "status": "online"})

@app.route("/api/servicos", methods=["GET"])
def listar_servicos():
    contrato = request.args.get("contrato", "todos")
    tipo = request.args.get("tipo", "todos")
    status_id = request.args.get("status_id", "todos")
    busca = request.args.get("busca", "")

    resultado = SERVICOS_DB
    if contrato != "todos":
        resultado = [s for s in resultado if s["ct"] == contrato]
    if tipo != "todos":
        resultado = [s for s in resultado if s["tp"] == tipo]
    if status_id != "todos":
        try:
            st_num = int(status_id)
            resultado = [s for s in resultado if s["st"] == st_num]
        except ValueError:
            pass
    if busca:
        q = busca.lower()
        resultado = [s for s in resultado if q in f"{s['id']} {s['ob']} {s['tp']}".lower()]

    return jsonify(resultado)

@app.route("/api/dashboard/kpis", methods=["GET"])
def kpis():
    ativos = [s for s in SERVICOS_DB if s["st"] not in (13, 14, 15)]
    valor_total = sum(s["v"] for s in ativos)
    estourados = [s for s in ativos if s.get("d", 0) > 5]
    return jsonify({
        "servicos_ativos": len(ativos),
        "valor_esteira": valor_total,
        "sla_estourado_count": len(estourados),
        "total_geral": len(SERVICOS_DB)
    })

# --- GESTÃO DE ACESSOS DO USUÁRIO MASTER ---
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
    print("Servidor Flask SIGES iniciado em http://localhost:8000")
    app.run(debug=True, host="0.0.0.0", port=5001)
