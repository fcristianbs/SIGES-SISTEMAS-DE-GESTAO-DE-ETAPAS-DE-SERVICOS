from flask import Blueprint, jsonify, request
from backend.app.database.repositories.servicos_repo import (
    buscar_servicos_paginados,
    obter_parametros_pendencias
)
from backend.app.services.tramitacao_service import atualizar_dados_servico
from backend.etl_sync import executar_sincronizacao_etl

servicos_bp = Blueprint("servicos_bp", __name__)


@servicos_bp.route("/api/servicos", methods=["GET"])
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

    dados_reais = buscar_servicos_paginados(
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


@servicos_bp.route("/api/servicos/<servico_id>", methods=["PUT"])
def atualizar_servico(servico_id):
    data = request.json or {}
    usuario_nome = data.pop("usuario_nome", "Analista Fechamento")
    usuario_email = data.pop("usuario_email", "analista@cosampa.com.br")

    if not data:
        return jsonify({"status": "erro", "mensagem": "Nenhum dado fornecido para atualização"}), 400

    res = atualizar_dados_servico(servico_id, data, usuario_nome, usuario_email)
    if res.get("status") == "erro":
        return jsonify(res), 400
    return jsonify(res)


@servicos_bp.route("/api/supervisores", methods=["GET"])
def listar_supervisores():
    res = buscar_servicos_paginados(limit=1000)
    dados = res.get("data", [])
    sups = sorted(list(set(s.get("supervisor") for s in dados if s.get("supervisor"))))
    return jsonify(sups)


@servicos_bp.route("/api/parametros/pendencias", methods=["GET"])
def obter_parametros_pendencias_rota():
    return jsonify(obter_parametros_pendencias())


@servicos_bp.route("/api/etl/sync", methods=["POST"])
def disparar_etl_sync():
    data = request.json or {}
    limit = data.get("limit", 500)
    res = executar_sincronizacao_etl(limit=limit)
    return jsonify(res)
