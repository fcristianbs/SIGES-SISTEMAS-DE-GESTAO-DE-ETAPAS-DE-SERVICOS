import os
import sys

# Carrega variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(root_dir, '.env'))
except ImportError:
    pass

import pymysql
from pymysql.cursors import DictCursor

CONTRATOS_PERMITIDOS = [
    'MULTISERVICOS C.SUL',
    'MULTISERVICOS LESTE',
    'MULTISERVICOS SUL'
]

def get_db_connection():
    host = os.getenv("DB_HOST", "operacao.vps-cosampa.online")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")
    # CONECTA EXCLUSIVAMENTE AO BD SECUNDÁRIO CRIADO PARA O SISTEMA (siges_app)
    dbname = os.getenv("DB_APP_NAME", "siges_app")

    if not user or not password:
        return None

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname,
            connect_timeout=10,
            cursorclass=DictCursor
        )
        return conn
    except Exception as e:
        print(f"[Aviso DB] Erro ao conectar no banco secundário MySQL ({dbname}): {e}")
        return None

def buscar_servicos_db(contrato="todos", tipo="todos", status_id="todos", busca="", periodo="30d", limit=500):
    """
    Busca os dados EXCLUSIVAMENTE do banco de dados secundário do sistema (siges_app.servicos).
    Não realiza nenhuma consulta direta no banco bruto de carga (siges).
    """
    conn = get_db_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    id, num_servico, contrato, nome_obra, bairro, localidade, tipo_servico,
                    status_id, valor, sla_dias, nota_medicao, data_execucao, centro_servico,
                    retorno_campo
                FROM servicos
                WHERE 1=1
            """
            params = []

            if contrato != "todos":
                sql += " AND contrato = %s"
                params.append(contrato)

            if tipo != "todos":
                sql += " AND tipo_servico = %s"
                params.append(tipo)

            if status_id != "todos":
                try:
                    sql += " AND status_id = %s"
                    params.append(int(status_id))
                except ValueError:
                    pass

            if busca:
                sql += " AND (id LIKE %s OR num_servico LIKE %s OR nome_obra LIKE %s OR contrato LIKE %s OR bairro LIKE %s OR localidade LIKE %s)"
                b_str = f"%{busca}%"
                params.extend([b_str, b_str, b_str, b_str, b_str, b_str])

            sql += " ORDER BY id DESC LIMIT %s"
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            resultado = []
            for r in rows:
                st_id = r.get("status_id") or 1
                ret_str = (r.get("retorno_campo") or "").strip()

                n_obra = (r.get("nome_obra") or "").strip()
                bairro = (r.get("bairro") or "").strip()
                loc = (r.get("localidade") or "").strip()

                if n_obra:
                    local_str = n_obra
                elif bairro and loc:
                    local_str = f"{bairro} · {loc}"
                elif loc:
                    local_str = loc
                else:
                    local_str = "Cosampa - SP"

                pend_items = []
                if st_id in (2, 6):
                    p_tipo = ret_str.split('-')[1] if '-' in ret_str else (ret_str or "Pendência de Campo")
                    pend_items = [
                        {"t": p_tipo[:20], "tr": False, "det": f"Inconformidade de campo: {ret_str}", "anx": None}
                    ]

                try:
                    val_float = float(r.get("valor") or 0.0)
                except (ValueError, TypeError):
                    val_float = 0.0

                dt_val = r.get("data_execucao")
                dt_str = str(dt_val) if dt_val else "Hoje"

                resultado.append({
                    "id": r.get("id") or f"SOB-{r.get('num_servico')}",
                    "ct": r.get("contrato") or "MULTISERVICOS SUL",
                    "ob": local_str,
                    "tp": r.get("tipo_servico") or "Serviço Técnico",
                    "st": st_id,
                    "v": val_float,
                    "d": r.get("sla_dias") or 3,
                    "nota": r.get("nota_medicao") or f"NM-{str(r.get('num_servico'))[-4:]}",
                    "data": dt_str,
                    "dep": r.get("centro_servico") or "Operação",
                    "ret": ret_str,
                    "pend": pend_items
                })

            return resultado
    except Exception as e:
        print(f"[Aviso DB] Erro ao consultar banco secundário 'siges_app': {e}")
        return []
    finally:
        conn.close()
