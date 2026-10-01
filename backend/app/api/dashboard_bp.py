from flask import Blueprint, jsonify
from backend.app.database.repositories.servicos_repo import (
    buscar_servicos_paginados,
    obter_opcoes_filtro
)

dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.route("/api/dashboard/kpis", methods=["GET"])
def kpis():
    res = buscar_servicos_paginados(limit=500)
    base = res.get("data", [])
    ativos = [s for s in base if s.get("st", 1) not in (13, 14, 15)]
    valor_total = sum(s.get("v", 0) for s in ativos)
    estourados = [s for s in ativos if s.get("d", 0) > 5]
    
    status_counts = {}
    for s in base:
        st = s.get("st", 1)
        status_counts[st] = status_counts.get(st, 0) + 1
        
    opcoes_filtro = obter_opcoes_filtro()
        
    return jsonify({
        "servicos_ativos": len(ativos),
        "valor_esteira": valor_total,
        "sla_estourado_count": len(estourados),
        "total_geral": res.get("total", 0),
        "status_counts": status_counts,
        "opcoes_filtro": opcoes_filtro
    })
