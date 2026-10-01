from flask import Blueprint, jsonify, request
from backend.app.services.tramitacao_service import (
    tramitar_servico,
    atualizar_dados_servico
)
from backend.app.database.repositories.auditoria_repo import (
    registrar_log_auditoria,
    registrar_acao_global
)

tramitacao_bp = Blueprint("tramitacao_bp", __name__)


@tramitacao_bp.route("/api/servicos/<servico_id>/tramitar", methods=["POST"])
def tramitar_servico_rota(servico_id):
    data = request.json or {}
    novo_status = data.get("novo_status_id")
    usuario_nome = data.get("usuario_nome", "Analista Fechamento")
    usuario_email = data.get("usuario_email", "analista@cosampa.com.br")

    if not novo_status:
        return jsonify({"status": "erro", "mensagem": "novo_status_id é obrigatório"}), 400

    res = tramitar_servico(servico_id, int(novo_status), usuario_nome, usuario_email)
    if res.get("status") == "bloqueado":
        return jsonify(res), 400
    return jsonify(res)


@tramitacao_bp.route("/api/servicos/lote/tramitar", methods=["POST"])
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
            atualizar_dados_servico(sid, dados_extras, usuario_nome, usuario_email)
        res = tramitar_servico(sid, int(novo_status), usuario_nome, usuario_email)
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


@tramitacao_bp.route("/api/servicos/lote/enviar-validacao", methods=["POST"])
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
        res = tramitar_servico(sid, 5, usuario_nome)
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


@tramitacao_bp.route("/api/servicos/lote/importar-rejeicoes", methods=["POST"])
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

        res = tramitar_servico(sid, status_destino, usuario_nome)
        if res.get("status") == "sucesso":
            registrar_log_auditoria(sid, usuario_nome, "cliente@distribuidora.com", "motivo_rejeicao_cliente", "", motivo)
            sucessos += 1

    return jsonify({
        "status": "sucesso",
        "processados": sucessos,
        "total": len(rejeicoes),
        "roteamento_padrao": "Status 06 (Rejeitado Fechamento)"
    })
