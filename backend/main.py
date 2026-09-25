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
from db import (
    get_db_connection, buscar_servicos_db, obter_opcoes_filtro_db, tramitar_servico_db, 
    buscar_logs_auditoria, registrar_log_auditoria, atualizar_dados_servico_db, 
    processar_importacao_dinamica, inserir_comentario_db, buscar_comentarios_db, 
    obter_parametros_pendencias_db, gerar_snapshot_conciliacao_db, 
    buscar_snapshot_conciliacao_db, fechar_evento_conciliacao_db, 
    obter_comparador_bilateral_db, salvar_comparador_bilateral_db
)
from etl_sync import executar_sincronizacao_etl
import json
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
    coordenador = request.args.get("coordenador", "todos")
    busca = request.args.get("busca", "")
    periodo = request.args.get("periodo", "30d")
    limit = int(request.args.get("limit", 100))
    skip = int(request.args.get("skip", 0))
    
    status_in = request.args.get("status_in")

    dados_reais = buscar_servicos_db(
        contrato=contrato, 
        tipo=tipo, 
        status_id=status_id, 
        supervisor=supervisor,
        coordenador=coordenador,
        busca=busca, 
        periodo=periodo, 
        limit=limit, 
        skip=skip,
        status_in=status_in
    )
    return jsonify(dados_reais)

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

@app.route("/api/servicos/<servico_id>/comentarios", methods=["GET"])
def obter_comentarios(servico_id):
    comentarios = buscar_comentarios_db(servico_id)
    return jsonify(comentarios)

@app.route("/api/servicos/<servico_id>/comentarios", methods=["POST"])
def adicionar_comentario(servico_id):
    data = request.json or {}
    usuario_id = data.get("usuario_id")
    usuario_nome = data.get("usuario_nome")
    texto = data.get("texto", "").strip()
    
    if not usuario_id or not texto:
        return jsonify({"status": "erro", "mensagem": "Usuário e texto são obrigatórios."}), 400
        
    res = inserir_comentario_db(servico_id, usuario_id, usuario_nome, texto)
    if res["status"] == "sucesso":
        return jsonify(res), 201
    return jsonify(res), 500

@app.route("/api/parametros/pendencias", methods=["GET"])
def obter_parametros_pendencias():
    return jsonify(obter_parametros_pendencias_db())

@app.route("/api/servicos/lote/tramitar", methods=["POST"])
def tramitar_lote():
    """ CDU V5 - Bloco 4: Tramitação em Lote com Mecânica de Falha Parcial Inteligente """
    data = request.json or {}
    servico_ids = data.get("servico_ids", [])
    novo_status = data.get("novo_status_id")
    dados_extras = data.get("dados_extras", {})
    usuario_nome = data.get("usuario_nome", "Analista Fechamento")
    usuario_email = data.get("usuario_email", "analista@cosampa.com.br")

    if not servico_ids or not novo_status:
        return jsonify({"status": "erro", "mensagem": "servico_ids e novo_status_id são obrigatórios"}), 400

    sucessos = 0
    sucessos_ids = []
    erros = []
    for sid in servico_ids:
        if dados_extras:
            atualizar_dados_servico_db(sid, dados_extras, usuario_nome, usuario_email)
        res = tramitar_servico_db(sid, int(novo_status), usuario_nome, usuario_email)
        if res.get("status") == "sucesso":
            sucessos += 1
            sucessos_ids.append(sid)
        else:
            erros.append({"id": sid, "erro": res.get("mensagem")})

    status_resp = "sucesso" if sucessos > 0 else "erro"
    codigo_http = 200 if (sucessos > 0 or not erros) else 400

    return jsonify({
        "status": status_resp,
        "sucessos": sucessos,
        "sucessos_ids": sucessos_ids,
        "falhas": len(erros),
        "erros": erros,
        "total": len(servico_ids),
        "mensagem": f"{sucessos} serviço(s) tramitado(s) com sucesso. {len(erros)} falha(s)."
    }), codigo_http

@app.route("/api/servicos/lote/enviar-validacao", methods=["POST"])
def enviar_lote_validacao():
    """ CDU-02 / CDU V5 Bloco 4: Consolidar e Enviar para Validação com Falha Parcial Inteligente """
    data = request.json or {}
    ids = data.get("servico_ids", [])
    sistema_fat = data.get("sistema_faturamento", "Eorder")
    mes_inicial = data.get("mes_medicao_inicial", "")
    usuario_nome = data.get("usuario_nome", "Analista Fechamento")

    if not mes_inicial:
        return jsonify({"status": "erro", "mensagem": "Mês de Medição Inicial (MM/AAAA) é obrigatório."}), 400

    sucessos = 0
    sucessos_ids = []
    erros = []
    for sid in ids:
        res = tramitar_servico_db(sid, 5, usuario_nome)
        if res.get("status") == "sucesso":
            registrar_log_auditoria(sid, usuario_nome, "analista@cosampa.com.br", "sistema_faturamento", "", sistema_fat)
            registrar_log_auditoria(sid, usuario_nome, "analista@cosampa.com.br", "mes_medicao_inicial", "", mes_inicial)
            sucessos += 1
            sucessos_ids.append(sid)
        else:
            erros.append({"id": sid, "erro": res.get("mensagem")})

    if sucessos > 0:
        desc_tech = {"lote_tamanho": len(ids), "sucessos": sucessos, "sistema_fat": sistema_fat, "mes_inicial": mes_inicial}
        desc_human = f"{usuario_nome} enviou em lote {sucessos} serviço(s) para validação do cliente (Sistema: {sistema_fat}, Mês: {mes_inicial})."
        from db import registrar_acao_global
        registrar_acao_global(usuario_nome, "analista@cosampa.com.br", "ENVIO_LOTE_VALIDACAO", "LOTE", desc_tech, desc_human)

    status_resp = "sucesso" if sucessos > 0 else "erro"
    codigo_http = 200 if (sucessos > 0 or not erros) else 400

    return jsonify({
        "status": status_resp,
        "tramitados": sucessos,
        "sucessos": sucessos,
        "sucessos_ids": sucessos_ids,
        "falhas": len(erros),
        "erros": erros,
        "total": len(ids),
        "mensagem": f"{sucessos} serviço(s) enviado(s) para validação. {len(erros)} falha(s)."
    }), codigo_http

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

# ==============================================================================
# CDU V5 - BLOCO 5: ROTAS DE FATURAMENTO E CONCILIAÇÃO (TELAS 04 E 05)
# ==============================================================================

@app.route("/api/faturamento/validar-lote", methods=["POST"])
def validar_lote_faturamento():
    """ CDU V5 - Tela 04: Validação e avanço para Conciliação (Status 08 -> 09) """
    data = request.json or {}
    servico_ids = data.get("servico_ids", [])
    data_validacao = data.get("data_validacao", "")
    usuario_nome = data.get("usuario_nome", "Analista Faturamento")
    usuario_email = data.get("usuario_email", "faturamento@cosampa.com.br")

    if not servico_ids or not data_validacao:
        return jsonify({"status": "erro", "mensagem": "servico_ids e data_validacao são obrigatórios."}), 400

    sucessos = 0
    sucessos_ids = []
    erros = []
    for sid in servico_ids:
        atualizar_dados_servico_db(sid, {"data_validacao": data_validacao}, usuario_nome, usuario_email)
        res = tramitar_servico_db(sid, 9, usuario_nome, usuario_email)
        if res.get("status") == "sucesso":
            sucessos += 1
            sucessos_ids.append(sid)
        else:
            erros.append({"id": sid, "erro": res.get("mensagem")})

    status_resp = "sucesso" if sucessos > 0 else "erro"
    codigo_http = 200 if (sucessos > 0 or not erros) else 400
    return jsonify({
        "status": status_resp,
        "sucessos": sucessos,
        "sucessos_ids": sucessos_ids,
        "falhas": len(erros),
        "erros": erros,
        "mensagem": f"{sucessos} serviço(s) validado(s) para faturamento e enviados para conciliação (Status 09)."
    }), codigo_http

@app.route("/api/faturamento/mes-emissao-lote", methods=["POST"])
def mes_emissao_lote():
    """ CDU V5 - Tela 05: Atribuir Mês de Emissão e liberar para Conciliação (Status 09 -> 10) """
    data = request.json or {}
    servico_ids = data.get("servico_ids", [])
    mes_emissao = data.get("mes_emissao", "")
    usuario_nome = data.get("usuario_nome", "Analista Faturamento")
    usuario_email = data.get("usuario_email", "faturamento@cosampa.com.br")

    if not servico_ids or not mes_emissao:
        return jsonify({"status": "erro", "mensagem": "servico_ids e mes_emissao (MM/AAAA) são obrigatórios."}), 400

    sucessos = 0
    sucessos_ids = []
    erros = []
    for sid in servico_ids:
        atualizar_dados_servico_db(sid, {"mes_emissao": mes_emissao}, usuario_nome, usuario_email)
        res = tramitar_servico_db(sid, 10, usuario_nome, usuario_email)
        if res.get("status") == "sucesso":
            sucessos += 1
            sucessos_ids.append(sid)
        else:
            erros.append({"id": sid, "erro": res.get("mensagem")})

    status_resp = "sucesso" if sucessos > 0 else "erro"
    codigo_http = 200 if (sucessos > 0 or not erros) else 400
    return jsonify({
        "status": status_resp,
        "sucessos": sucessos,
        "sucessos_ids": sucessos_ids,
        "falhas": len(erros),
        "erros": erros,
        "mensagem": f"{sucessos} serviço(s) com Mês de Emissão ({mes_emissao}) liberados para Conciliação (Status 10)."
    }), codigo_http

@app.route("/api/conciliacao/evento/iniciar-snapshot", methods=["POST"])
def iniciar_snapshot_conciliacao():
    """ CDU V5 - Tela 05: Gerar Snapshot Pré-Importação ('Relatório ANTES') """
    data = request.json or {}
    servico_ids = data.get("servico_ids", [])
    evento_id = data.get("evento_id")

    if not servico_ids:
        return jsonify({"status": "erro", "mensagem": "servico_ids é obrigatório."}), 400

    res = gerar_snapshot_conciliacao_db(servico_ids, evento_id)
    return jsonify(res)

@app.route("/api/conciliacao/evento/snapshot/<evento_id>", methods=["GET"])
def obter_snapshot_conciliacao(evento_id):
    """ CDU V5 - Tela 05: Consultar 'Relatório ANTES' do Evento de Conciliação """
    snapshots = buscar_snapshot_conciliacao_db(evento_id)
    return jsonify({
        "status": "sucesso",
        "evento_id": evento_id,
        "total": len(snapshots),
        "data": snapshots
    })

@app.route("/api/conciliacao/evento/fechar", methods=["POST"])
def fechar_evento_conciliacao():
    """ CDU V5 - Tela 05: Fechamento Transacional do Evento com Conciliação Automática """
    data = request.json or {}
    evento_id = data.get("evento_id") or "EVT-PADRAO"
    itens_pagamento = data.get("itens_pagamento", [])
    usuario_nome = data.get("usuario_nome", "Analista Fechamento")
    usuario_email = data.get("usuario_email", "analista@cosampa.com.br")

    if not itens_pagamento:
        return jsonify({"status": "erro", "mensagem": "itens_pagamento é obrigatório."}), 400

    res = fechar_evento_conciliacao_db(evento_id, itens_pagamento, usuario_nome, usuario_email)
    return jsonify(res)

@app.route("/api/servicos/<id>/comparador-bilateral", methods=["GET"])
def obter_comparador_bilateral(id):
    """ CDU V5 - Tela 01 (Status 11): Obter Comparador Bilateral (Realizado vs Pago) """
    res = obter_comparador_bilateral_db(id)
    return jsonify(res)

@app.route("/api/servicos/<id>/tramitar-divergencia", methods=["POST"])
def tramitar_divergencia(id):
    """ CDU V5 - Tela 01 (Status 11 -> 12 -> 13): Tramitar com Justificativa e SLA """
    data = request.json or {}
    novo_status_id = data.get("novo_status_id")
    justificativa = data.get("justificativa", "")
    mes_reapresentacao = data.get("mes_reapresentacao", "")
    sharepoint_url = data.get("sharepoint_url", "")
    usuario_nome = data.get("usuario_nome", "Analista Fechamento")
    usuario_email = data.get("usuario_email", "analista@cosampa.com.br")

    if not novo_status_id:
        return jsonify({"status": "erro", "mensagem": "novo_status_id é obrigatório."}), 400

    res = salvar_comparador_bilateral_db(
        servico_id=id,
        novo_status_id=int(novo_status_id),
        justificativa=justificativa,
        mes_reapresentacao=mes_reapresentacao,
        sharepoint_url=sharepoint_url,
        usuario_nome=usuario_nome,
        usuario_email=usuario_email
    )
    return jsonify(res)

@app.route("/api/supervisores", methods=["GET"])
def listar_supervisores():
    res = buscar_servicos_db(limit=1000)
    dados = res.get("data", [])
    sups = sorted(list(set(s.get("supervisor") for s in dados if s.get("supervisor"))))
    return jsonify(sups)

@app.route("/api/dashboard/kpis", methods=["GET"])
def kpis():
    res = buscar_servicos_db(limit=500)
    base = res.get("data", [])
    ativos = [s for s in base if s.get("st", 1) not in (13, 14, 15)]
    valor_total = sum(s.get("v", 0) for s in ativos)
    estourados = [s for s in ativos if s.get("d", 0) > 5]
    
    status_counts = {}
    for s in base:
        st = s.get("st", 1)
        status_counts[st] = status_counts.get(st, 0) + 1
        
    opcoes_filtro = obter_opcoes_filtro_db()
        
    return jsonify({
        "servicos_ativos": len(ativos),
        "valor_esteira": valor_total,
        "sla_estourado_count": len(estourados),
        "total_geral": res.get("total", 0),
        "status_counts": status_counts,
        "opcoes_filtro": opcoes_filtro
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

# --- CDU-04: PERFIS DE TELA E MODO DE EDIÇÃO ---

@app.route("/api/perfis_tela", methods=["GET"])
def get_perfis_tela():
    user_id = int(request.args.get("user_id", 0))
    user = next((u for u in USUARIOS_DB if u["id"] == user_id), None)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"erro": "Erro de conexão com o banco"}), 500
        
    try:
        with conn.cursor() as cursor:
            if user and user.get("criar_perfis_tela"):
                # Master vê tudo
                cursor.execute("SELECT * FROM perfis_tela ORDER BY tipo ASC, id ASC")
            else:
                # Comum vê Globais, Seus Privados e Compartilhados com Ele
                sql = """
                    SELECT p.* FROM perfis_tela p
                    LEFT JOIN perfil_tela_usuario pu ON p.id = pu.perfil_id AND pu.usuario_id = %s
                    WHERE p.tipo = 'global' 
                       OR p.criado_por_id = %s 
                       OR pu.id IS NOT NULL
                    GROUP BY p.id
                    ORDER BY p.tipo ASC, p.id ASC
                """
                cursor.execute(sql, (user_id, user_id))
            
            rows = cursor.fetchall()
            for r in rows:
                if isinstance(r['colunas_visiveis'], str):
                    r['colunas_visiveis'] = json.loads(r['colunas_visiveis'])
            return jsonify(rows)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/perfis_tela", methods=["POST"])
def criar_perfil_tela():
    data = request.json or {}
    user_id = int(data.get("criado_por_id", 0))
    user = next((u for u in USUARIOS_DB if u["id"] == user_id), None)
    
    if not user:
        return jsonify({"erro": "Usuário não autenticado ou inválido"}), 401

    nome = data.get("nome", "Novo Perfil")
    colunas_visiveis = data.get("colunas_visiveis", [])
    tipo_solicitado = data.get("tipo", "privado")
    tipo = tipo_solicitado if user.get("criar_perfis_tela") else "privado"

    conn = get_db_connection()
    if not conn:
        return jsonify({"erro": "Erro banco"}), 500

    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO perfis_tela (nome, colunas_visiveis, criado_por_id, tipo) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (nome, json.dumps(colunas_visiveis), user_id, tipo))
            novo_id = cursor.lastrowid
        conn.commit()
        return jsonify({"id": novo_id, "nome": nome, "colunas_visiveis": colunas_visiveis, "tipo": tipo}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/perfis_tela/<int:perfil_id>", methods=["PUT"])
def atualizar_perfil_tela(perfil_id):
    data = request.json or {}
    user_id = int(data.get("user_id", 0))
    user = next((u for u in USUARIOS_DB if u["id"] == user_id), None)
    
    if not user:
        return jsonify({"erro": "Não autorizado"}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({"erro": "Erro banco"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM perfis_tela WHERE id = %s", (perfil_id,))
            perfil = cursor.fetchone()
            if not perfil:
                return jsonify({"erro": "Perfil não encontrado"}), 404
            
            if perfil['tipo'] == 'global' and not user.get("criar_perfis_tela"):
                return jsonify({"erro": "Você não tem permissão para editar um perfil global."}), 403

            colunas_visiveis = data.get("colunas_visiveis", [])
            sql = "UPDATE perfis_tela SET colunas_visiveis = %s WHERE id = %s"
            cursor.execute(sql, (json.dumps(colunas_visiveis), perfil_id))
        conn.commit()
        return jsonify({"status": "sucesso"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/perfis_tela/todos", methods=["GET"])
def get_todos_perfis_tela():
    # Apenas para a tela de Gestão de Acessos
    conn = get_db_connection()
    if not conn:
        return jsonify({"erro": "Erro de conexão com o banco"}), 500
        
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nome, tipo, criado_por_id FROM perfis_tela ORDER BY tipo ASC, id ASC")
            rows = cursor.fetchall()
            return jsonify(rows)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/usuarios/<int:user_id>/perfis_tela", methods=["GET"])
def get_perfis_usuario(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"erro": "Erro de conexão com o banco"}), 500
        
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT perfil_id FROM perfil_tela_usuario WHERE usuario_id = %s", (user_id,))
            rows = cursor.fetchall()
            return jsonify([r['perfil_id'] for r in rows])
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/usuarios/<int:user_id>/perfis_tela", methods=["PUT"])
def atualizar_perfis_usuario(user_id):
    data = request.json or {}
    perfis = data.get("perfis", [])
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"erro": "Erro de conexão com o banco"}), 500
        
    try:
        with conn.cursor() as cursor:
            # Apaga os antigos
            cursor.execute("DELETE FROM perfil_tela_usuario WHERE usuario_id = %s", (user_id,))
            # Insere os novos
            for p_id in perfis:
                cursor.execute("INSERT INTO perfil_tela_usuario (usuario_id, perfil_id) VALUES (%s, %s)", (user_id, p_id))
        conn.commit()
        return jsonify({"status": "sucesso"})
    except Exception as e:
        conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f"Servidor Flask SIGES iniciado em http://localhost:{port}")
    app.run(debug=True, host="0.0.0.0", port=port)
