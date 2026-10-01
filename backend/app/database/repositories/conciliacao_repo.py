import json
from datetime import datetime
from backend.app.database.connection import get_db_cursor


def inserir_snapshot_servico(evento_id, servico_id, status_id_anterior, valor_faturado, valor_pago_anterior, dados_servico_dict):
    """ Insere um registro imutável na tabela conciliacao_snapshots """
    sql = """
        INSERT INTO conciliacao_snapshots 
            (evento_id, servico_id, status_id_anterior, valor_faturado, valor_pago_anterior, dados_servico_json, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """
    srv_json = json.dumps(dados_servico_dict, default=str, ensure_ascii=False)
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(sql, (
            evento_id,
            servico_id,
            status_id_anterior,
            valor_faturado,
            valor_pago_anterior,
            srv_json
        ))
        return cursor.lastrowid


def buscar_snapshot_conciliacao(evento_id):
    """ Retorna todos os snapshots de um evento com dados do serviço vinculado """
    sql = """
        SELECT cs.id, cs.evento_id, cs.servico_id, cs.status_id_anterior, 
               cs.valor_faturado, cs.valor_pago_anterior, cs.created_at,
               s.contrato, s.num_servico, s.tdc, s.cliente, s.tipo_servico
        FROM conciliacao_snapshots cs
        LEFT JOIN servicos s ON s.id = cs.servico_id
        WHERE cs.evento_id = %s
        ORDER BY cs.id ASC
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (evento_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"[Erro Busca Snapshot] {e}")
        return []


def buscar_itens_baremo(servico_id):
    """ Busca os itens detalhados de baremo de um serviço """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM baremo_itens WHERE servico_id = %s", (servico_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"[Erro Itens Baremo {servico_id}] {e}")
        return []
