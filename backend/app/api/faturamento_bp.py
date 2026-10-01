from flask import Blueprint, jsonify, request
from backend.app.services.tramitacao_service import (
    tramitar_servico,
    atualizar_dados_servico
)

faturamento_bp = Blueprint("faturamento_bp", __name__)


@faturamento_bp.route("/api/faturamento/validar-lote", methods=["POST"])
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
        atualizar_dados_servico(sid, {"data_validacao": data_validacao}, usuario_nome, usuario_email)
        res = tramitar_servico(sid, 9, usuario_nome, usuario_email)
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


@faturamento_bp.route("/api/faturamento/mes-emissao-lote", methods=["POST"])
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
        atualizar_dados_servico(sid, {"mes_emissao": mes_emissao}, usuario_nome, usuario_email)
        res = tramitar_servico(sid, 10, usuario_nome, usuario_email)
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
