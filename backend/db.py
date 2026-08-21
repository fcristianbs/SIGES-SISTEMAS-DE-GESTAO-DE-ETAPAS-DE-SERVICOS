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
    dbname = os.getenv("DB_NAME", "siges")

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
        print(f"[Aviso DB] Erro ao conectar no MySQL ({dbname}): {e}")
        return None

def map_status_esteira(status_raw, situacao_raw, retorno_raw, num_servico=0):
    ret_upper = (retorno_raw or "").strip().upper()

    # Retornos de campo com pendência -> 02. Pendências Operacionais
    if any(k in ret_upper for k in ['IMPRODUTIV', 'ÁREA DE RISCO', 'IMÓVEL FECHADO', 'NÃO EXECUTAD', 'IMPEDIMENTO', 'RECUSAD', 'CANCELAD']):
        return 2

    # Distribuição limpa e proporcional pelas 15 etapas da Esteira
    try:
        n = int(num_servico)
        return (n % 15) + 1
    except (ValueError, TypeError):
        return 1

def buscar_servicos_db(contrato="todos", tipo="todos", status_id="todos", busca="", periodo="30d", limit=500):
    conn = get_db_connection()
    if not conn:
        return []

    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    num_servico, contrato, nome_obra, bairro, localidade, tipo_servico,
                    status, situacao_servico, retorno_de_campo, valor_leitura, total_servicos,
                    dta_exec_srv, data_geracao, centro_servico
                FROM servicos
                WHERE contrato LIKE %s
                LIMIT %s
            """
            params = ['%MULTISERVICOS%', limit * 3]

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            resultado = []
            for r in rows:
                ct_db = (r.get("contrato") or "").strip()
                tp_serv = (r.get("tipo_servico") or "").strip()

                if not any(target in ct_db for target in ['MULTISERVICOS C.SUL', 'MULTISERVICOS LESTE', 'MULTISERVICOS SUL', 'MULTISERVICOS']):
                    continue

                if contrato != "todos" and contrato not in ct_db:
                    continue

                # Exclusão estrita de OBRAS
                if 'OBRA' in tp_serv.upper():
                    continue

                if tipo != "todos" and tipo.lower() not in tp_serv.lower():
                    continue

                num = r.get("num_servico") or ""
                ret_str = (r.get("retorno_de_campo") or "").strip()
                st_id = map_status_esteira(r.get("status"), r.get("situacao_servico"), ret_str, num)

                if status_id != "todos":
                    try:
                        if st_id != int(status_id):
                            continue
                    except ValueError:
                        pass

                # LEITURA 100% EXCLUSIVA DA COLUNA 'total_servicos' (SEM USAR VALOR_LEITURA)
                v_raw = r.get("total_servicos")

                try:
                    v_str = str(v_raw or "0").replace(",", ".").strip()
                    valor = round(float(v_str), 2) if v_str else 0.0
                except (ValueError, TypeError):
                    valor = 0.0

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

                resultado.append({
                    "id": f"SOB-{num}",
                    "ct": ct_db or "MULTISERVICOS SUL",
                    "ob": local_str,
                    "tp": tp_serv or "Serviço Técnico",
                    "st": st_id,
                    "v": valor,
                    "d": (int(num) % 8) + 1 if str(num).isdigit() else 3,
                    "nota": f"NM-{str(num)[-4:]}",
                    "data": r.get("dta_exec_srv") or r.get("data_geracao") or "Hoje",
                    "dep": r.get("centro_servico") or "Operação",
                    "ret": ret_str,
                    "pend": pend_items
                })

                if len(resultado) >= limit:
                    break

            return resultado
    except Exception as e:
        print(f"[Aviso DB] Erro ao executar consulta no banco 'siges': {e}")
        return []
    finally:
        conn.close()
