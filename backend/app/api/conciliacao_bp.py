from flask import Blueprint, jsonify, request
from backend.app.services.conciliacao_service import (
    gerar_snapshot_conciliacao,
    fechar_evento_conciliacao,
    obter_comparador_bilateral,
    salvar_comparador_bilateral
)
from backend.app.database.repositories.conciliacao_repo import (
    buscar_snapshot_conciliacao
)

conciliacao_bp = Blueprint("conciliacao_bp", __name__)


@conciliacao_bp.route("/api/conciliacao/evento/iniciar-snapshot", methods=["POST"])
def iniciar_snapshot_conciliacao():
    """ CDU V5 - Tela 05: Gerar Snapshot Pré-Importação ('Relatório ANTES') """
    data = request.json or {}
    servico_ids = data.get("servico_ids", [])
    evento_id = data.get("evento_id")

    if not servico_ids:
        return jsonify({"status": "erro", "mensagem": "servico_ids é obrigatório."}), 400

    res = gerar_snapshot_conciliacao(servico_ids, evento_id)
    return jsonify(res)


@conciliacao_bp.route("/api/conciliacao/evento/snapshot/<evento_id>", methods=["GET"])
def obter_snapshot_conciliacao(evento_id):
    """ CDU V5 - Tela 05: Consultar 'Relatório ANTES' do Evento de Conciliação """
    snapshots = buscar_snapshot_conciliacao(evento_id)
    return jsonify({
        "status": "sucesso",
        "evento_id": evento_id,
        "total": len(snapshots),
        "data": snapshots
    })


@conciliacao_bp.route("/api/conciliacao/evento/fechar", methods=["POST"])
def fechar_evento_conciliacao_rota():
    """ CDU V5 - Tela 05: Fechamento Transacional do Evento com Conciliação Automática """
    data = request.json or {}
    evento_id = data.get("evento_id") or "EVT-PADRAO"
    itens_pagamento = data.get("itens_pagamento", [])
    usuario_nome = data.get("usuario_nome", "Analista Fechamento")
    usuario_email = data.get("usuario_email", "analista@cosampa.com.br")

    if not itens_pagamento:
        return jsonify({"status": "erro", "mensagem": "itens_pagamento é obrigatório."}), 400

    res = fechar_evento_conciliacao(evento_id, itens_pagamento, usuario_nome, usuario_email)
    return jsonify(res)


@conciliacao_bp.route("/api/servicos/<id>/comparador-bilateral", methods=["GET"])
def obter_comparador_bilateral_rota(id):
    """ CDU V5 - Tela 01 (Status 11): Obter Comparador Bilateral (Realizado vs Pago) """
    res = obter_comparador_bilateral(id)
    return jsonify(res)


@conciliacao_bp.route("/api/servicos/<id>/tramitar-divergencia", methods=["POST"])
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

    res = salvar_comparador_bilateral(
        servico_id=id,
        novo_status_id=int(novo_status_id),
        justificativa=justificativa,
        mes_reapresentacao=mes_reapresentacao,
        sharepoint_url=sharepoint_url,
        usuario_nome=usuario_nome,
        usuario_email=usuario_email
    )
    return jsonify(res)
