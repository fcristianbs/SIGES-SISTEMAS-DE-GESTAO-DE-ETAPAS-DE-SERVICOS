from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Habilita CORS para o front-end SPA

# --- DADOS MOCK EM MEMÓRIA ---
PERFIS_DB = {
    "Master": {
        "nome": "Master",
        "descricao": "Administrador Master com controle total de acessos",
        "is_master": True,
        "telas": ["gerencial", "medicao", "pendencias", "faturamento", "conciliacoes", "finalizados", "relatorios", "gestao_acessos"]
    },
    "Fechamento": {
        "nome": "Fechamento",
        "descricao": "Gestão de medições e fechamento de serviços",
        "is_master": False,
        "telas": ["gerencial", "medicao", "pendencias", "finalizados", "relatorios"]
    },
    "Operação": {
        "nome": "Operação",
        "descricao": "Tratativa de pendências operacionais",
        "is_master": False,
        "telas": ["gerencial", "pendencias", "finalizados", "relatorios"]
    },
    "Faturamento": {
        "nome": "Faturamento",
        "descricao": "Acesso às etapas de faturamento e conciliação",
        "is_master": False,
        "telas": ["gerencial", "medicao", "pendencias", "faturamento", "conciliacoes", "finalizados", "relatorios"]
    }
}

USUARIOS_DB = [
    {"id": 1, "nome": "Administrador Master", "email": "admin@cosampa.com.br", "perfil": "Master"},
    {"id": 2, "nome": "Carlos Fechamento", "email": "carlos@cosampa.com.br", "perfil": "Fechamento"},
    {"id": 3, "nome": "Fernanda Operação", "email": "fernanda@cosampa.com.br", "perfil": "Operação"},
    {"id": 4, "nome": "Roberto Faturamento", "email": "roberto@cosampa.com.br", "perfil": "Faturamento"}
]

SERVICOS_DB = [
    {"id": "SOB-2026-0341", "ct": "A", "ob": "Vila Prudente", "tp": "Rede", "st": 1, "v": 12400.0, "d": 11, "nota": "NM-0873"},
    {"id": "SOB-2026-0347", "ct": "A", "ob": "Vila Prudente", "tp": "Medidor", "st": 1, "v": 980.0, "d": 8, "nota": "NM-0879"},
    {"id": "SOB-2026-0352", "ct": "B", "ob": "Jd. Ângela", "tp": "Transformador", "st": 1, "v": 38200.0, "d": 12, "nota": "NM-0881"},
    {"id": "SOB-2026-0298", "ct": "A", "ob": "Penha", "tp": "Rede", "st": 2, "v": 21500.0, "d": 4, "pend": [{"t": "Fotos", "tr": False}, {"t": "Materiais", "tr": False}]},
    {"id": "SOB-2026-0301", "ct": "B", "ob": "Capela do Socorro", "tp": "Ramal", "st": 2, "v": 3400.0, "d": 7, "pend": [{"t": "Documentos", "tr": False}, {"t": "Retorno", "tr": False}]},
    {"id": "SOB-2026-0315", "ct": "C", "ob": "Itaquera", "tp": "Poste", "st": 2, "v": 7250.0, "d": 10, "pend": [{"t": "Fotos", "tr": False}]},
    {"id": "SOB-2026-0289", "ct": "A", "ob": "Penha", "tp": "Rede", "st": 3, "v": 45900.0, "d": 12, "nota": "NM-0851"},
    {"id": "SOB-2026-0276", "ct": "A", "ob": "Mooca", "tp": "Rede", "st": 4, "v": 78500.0, "d": 6, "nota": "NM-0812"},
    {"id": "SOB-2026-0269", "ct": "B", "ob": "Parelheiros", "tp": "Rede", "st": 5, "v": 18700.0, "d": 11, "nota": "NM-0842", "ret": "Baremo divergente"},
    {"id": "SOB-2026-0248", "ct": "A", "ob": "Belém", "tp": "Rede", "st": 7, "v": 52000.0, "d": 11, "nota": "NM-0790"},
    {"id": "SOB-2026-0237", "ct": "B", "ob": "Santo Amaro", "tp": "Rede", "st": 8, "v": 66800.0, "d": 3, "nota": "NF-4521"},
    {"id": "SOB-2026-0216", "ct": "A", "ob": "Sapopemba", "tp": "Rede", "st": 10, "v": 33500.0, "d": 6, "nota": "NF-4460", "ret": "Divergência R$ 1.240"},
    {"id": "SOB-2026-0187", "ct": "A", "ob": "Sé", "tp": "Rede", "st": 13, "v": 15300.0, "d": 8, "nota": "NF-4432"}
]

# --- ENDPOINTS FLASK API ---
@app.route("/")
def home():
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
    return jsonify({
        "servicos_ativos": len(ativos),
        "valor_esteira": valor_total,
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
            "perfil": data.get("perfil", "Operação")
        }
        USUARIOS_DB.append(novo)
        return jsonify(novo), 201

    return jsonify(USUARIOS_DB)

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
    app.run(debug=True, host="0.0.0.0", port=8000)
