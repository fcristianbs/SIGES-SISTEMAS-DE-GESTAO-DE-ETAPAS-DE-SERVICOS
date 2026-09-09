from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
from werkzeug.utils import secure_filename
import pandas as pd

# Carrega variáveis de ambiente do arquivo .env caso exista
try:
    from dotenv import load_dotenv
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(root_dir, '.env'))
except ImportError:
    pass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data import PERFIS_DB, USUARIOS_DB, SERVICOS_DB
from db import buscar_servicos_db, tramitar_servico_db, buscar_logs_auditoria, registrar_log_auditoria, atualizar_dados_servico_db, processar_importacao_dinamica
from etl_sync import executar_sincronizacao_etl

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
        "database_raw": "siges",
        "database_app": os.getenv("DB_APP_NAME", "siges_app")
    })

# --- ENDPOINTS PIPELINE ETL DE INGESTÃO (siges -> siges_app) ---
@app.route("/api/etl/sync", methods=["POST"])
def disparar_etl_sync():
    data = request.json or {}
    limit = data.get("limit", 500)
    res = executar_sincronizacao_etl(limit=limit)
    return jsonify(res)

@app.route("/api/servicos", methods=["GET"])
def listar_servicos():
    contrato = request.args.get("contrato", "todos")
    tipo = request.args.get("tipo", "todos")
    status_id = request.args.get("status_id", "todos")
    supervisor = request.args.get("supervisor", "todos")
    busca = request.args.get("busca", "")

    dados_reais = buscar_servicos_db(contrato=contrato, tipo=tipo, status_id=status_id, supervisor=supervisor, busca=busca)
    resultado = dados_reais if dados_reais is not None else []

    return jsonify(resultado)

@app.route("/api/servicos/<servico_id>/tramitar", methods=["POST"])
def tramitar_servico(servico_id):
    data = request.json or {}
    novo_status = data.get("novo_status_id")
    usuario_nome = data.get("usuario_nome", "Analista Fechamento")
    usuario_email = data.get("usuario_email", "analista@cosampa.com.br")

    if not novo_status:
        return jsonify({"status": "erro", "mensagem": "novo_status_id é obrigatório"}), 400

    res = tramitar_servico_db(servico_id, int(novo_status), usuario_nome, usuario_email)
    if res.get("status") == "bloqueado":
        return jsonify(res), 400
    return jsonify(res)

@app.route("/api/servicos/<servico_id>", methods=["PUT"])
def atualizar_servico(servico_id):
    data = request.json or {}
    usuario_nome = data.pop("usuario_nome", "Analista Fechamento")
    usuario_email = data.pop("usuario_email", "analista@cosampa.com.br")

    if not data:
        return jsonify({"status": "erro", "mensagem": "Nenhum dado fornecido para atualização"}), 400

    res = atualizar_dados_servico_db(servico_id, data, usuario_nome, usuario_email)
    if res.get("status") == "erro":
        return jsonify(res), 400
    return jsonify(res)

@app.route("/api/servicos/<servico_id>/auditoria", methods=["GET"])
def obter_logs_auditoria(servico_id):
    logs = buscar_logs_auditoria(servico_id)
    return jsonify(logs)

@app.route("/api/servicos/lote/enviar-validacao", methods=["POST"])
def enviar_lote_validacao():
    """ CDU-02: Consolidar e Enviar para Validação do Cliente """
    data = request.json or {}
    ids = data.get("servico_ids", [])
    sistema_fat = data.get("sistema_faturamento", "Eorder")
    mes_inicial = data.get("mes_medicao_inicial", "")
    usuario_nome = data.get("usuario_nome", "Analista Fechamento")

    if not mes_inicial:
        return jsonify({"status": "erro", "mensagem": "Mês de Medição Inicial (MM/AAAA) é obrigatório."}), 400

    sucessos = 0
    for sid in ids:
        res = tramitar_servico_db(sid, 5, usuario_nome)
        if res.get("status") == "sucesso":
            registrar_log_auditoria(sid, usuario_nome, "analista@cosampa.com.br", "sistema_faturamento", "", sistema_fat)
            registrar_log_auditoria(sid, usuario_nome, "analista@cosampa.com.br", "mes_medicao_inicial", "", mes_inicial)
            sucessos += 1

    if sucessos > 0:
        desc_tech = {"lote_tamanho": len(ids), "sucessos": sucessos, "sistema_fat": sistema_fat, "mes_inicial": mes_inicial}
        desc_human = f"{usuario_nome} enviou em lote {sucessos} serviço(s) para validação do cliente (Sistema: {sistema_fat}, Mês: {mes_inicial})."
        # O tramitar_servico_db ja gerou logs para cada ID especifico, entao o ID aqui pode ser LOTE
        from db import registrar_acao_global
        registrar_acao_global(usuario_nome, "analista@cosampa.com.br", "ENVIO_LOTE_VALIDACAO", "LOTE", desc_tech, desc_human)

    return jsonify({"status": "sucesso", "tramitados": sucessos, "total": len(ids)})

@app.route("/api/servicos/lote/importar-rejeicoes", methods=["POST"])
def importar_rejeicoes_lote():
    """ CDU-06 / CDU-07: Importação em Lote de Rejeições do Cliente com Roteamento Automático """
    data = request.json or {}
    rejeicoes = data.get("rejeicoes", [])
    usuario_nome = data.get("usuario_nome", "Analista Fechamento")

    sucessos = 0
    for r in rejeicoes:
        sid = r.get("id")
        motivo = r.get("motivo", "Rejeição informada pelo cliente")
        destino_tipo = r.get("destino", "") # 'operacao' ou 'fechamento'

        # RN de Roteamento Padrão: Se omitido, direciona automaticamente para Status 06 (Fechamento)
        status_destino = 7 if destino_tipo.lower() == 'operacao' else 6

        res = tramitar_servico_db(sid, status_destino, usuario_nome)
        if res.get("status") == "sucesso":
            registrar_log_auditoria(sid, usuario_nome, "cliente@distribuidora.com", "motivo_rejeicao_cliente", "", motivo)
            sucessos += 1

    return jsonify({
        "status": "sucesso",
        "processados": sucessos,
        "total": len(rejeicoes),
        "roteamento_padrao": "Status 06 (Rejeitado Fechamento)"
    })

@app.route("/api/supervisores", methods=["GET"])
def listar_supervisores():
    dados = buscar_servicos_db(limit=500)
    sups = sorted(list(set(s.get("supervisor") for s in dados if s.get("supervisor"))))
    return jsonify(sups)

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

# --- CDU-08: IMPORTACAO DE PLANILHAS ---
UPLOAD_FOLDER = '/tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/api/servicos/upload-temp", methods=["POST"])
def upload_temp_planilha():
    if 'file' not in request.files:
        return jsonify({"status": "erro", "mensagem": "Nenhum arquivo enviado"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "erro", "mensagem": "Nenhum arquivo selecionado"}), 400
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        xl = pd.ExcelFile(filepath)
        abas = xl.sheet_names
        return jsonify({"arquivo_temp_id": filename, "abas": abas})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro ao ler arquivo: {str(e)}"}), 500

@app.route("/api/servicos/pre-visualizar", methods=["POST"])
def pre_visualizar_planilha():
    data = request.json or {}
    arquivo_temp_id = data.get("arquivo_temp_id")
    aba = data.get("aba_selecionada")
    linha_cabecalho = data.get("linha_cabecalho", 0)
    
    if not arquivo_temp_id or not aba:
        return jsonify({"status": "erro", "mensagem": "Arquivo ou aba não informados"}), 400
        
    filepath = os.path.join(UPLOAD_FOLDER, arquivo_temp_id)
    try:
        # Le apenas as primeiras 10 linhas para preview sem engolir a primeira linha (header=None)
        df = pd.read_excel(filepath, sheet_name=aba, header=None, nrows=10)
        
        # Converte para dict bruto
        raw_linhas = df.to_dict(orient='records')
        
        # Limpeza 100% segura usando Python nativo (livre de regressoes do pandas com None/NaN)
        linhas_limpas = []
        for row in raw_linhas:
            clean_row = {}
            for k, v in row.items():
                # Se for NaN real do pandas/numpy ou string de nulo, vira None (null no JSON)
                if pd.isna(v) or str(v).strip() in ['nan', 'NaN', 'NaT', 'None', '<NA>', '']:
                    clean_row[str(k)] = None
                else:
                    # Converte forcadamente datas e tempos para string para evitar erro de serializacao
                    clean_row[str(k)] = str(v)
            linhas_limpas.append(clean_row)
            
        colunas = [str(c) for c in df.columns]
        return jsonify({"colunas": colunas, "linhas": linhas_limpas})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route("/api/servicos/importar-dinamico", methods=["POST"])
def importar_dinamico_planilha():
    data = request.json or {}
    arquivo_temp_id = data.get("arquivo_temp_id")
    aba = data.get("aba_selecionada")
    linha_cabecalho = data.get("linha_cabecalho", 0)
    mapeamento = data.get("mapeamento", {})
    usuario_nome = data.get("usuario_nome", "Importador")
    
    filepath = os.path.join(UPLOAD_FOLDER, arquivo_temp_id)
    if not os.path.exists(filepath):
        return jsonify({"status": "erro", "mensagem": "Arquivo não encontrado no servidor"}), 404
        
    res = processar_importacao_dinamica(filepath, aba, linha_cabecalho, mapeamento, usuario_nome)
    return jsonify(res)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"Servidor Flask SIGES iniciado em http://localhost:{port}")
    app.run(debug=True, host="0.0.0.0", port=port)
