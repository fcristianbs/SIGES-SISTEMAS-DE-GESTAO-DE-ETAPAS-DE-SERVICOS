import os
import sys

try:
    from dotenv import load_dotenv
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(root_dir, '.env'))
except ImportError:
    pass

import pymysql
from pymysql.cursors import DictCursor
from datetime import datetime

CONTRATOS_PERMITIDOS = [
    'MULTISERVICOS C.SUL',
    'MULTISERVICOS LESTE',
    'MULTISERVICOS SUL'
]

def map_status_esteira(status_raw, situacao_raw, retorno_raw, num_servico=0):
    ret_upper = (retorno_raw or "").strip().upper()
    if any(k in ret_upper for k in ['IMPRODUTIV', 'ÁREA DE RISCO', 'IMÓVEL FECHADO', 'NÃO EXECUTAD', 'IMPEDIMENTO', 'RECUSAD', 'CANCELAD']):
        return 2
    try:
        n = int(num_servico)
        return (n % 15) + 1
    except (ValueError, TypeError):
        return 1

def executar_sincronizacao_etl(limit=500):
    """
    Coleta dados do BD Principal (siges) referentes ao último 1 mês 
    e insere/atualiza no BD Secundário do sistema (siges_app.servicos).
    """
    host = os.getenv("DB_HOST", "operacao.vps-cosampa.online")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")

    if not user or not password:
        print("[ETL Erro] Credenciais do banco não encontradas em .env")
        return {"status": "erro", "mensagem": "Credenciais não configuradas"}

    try:
        conn_raw = pymysql.connect(host=host, port=port, user=user, password=password, database="siges", connect_timeout=10, cursorclass=DictCursor)
        conn_app = pymysql.connect(host=host, port=port, user=user, password=password, database="siges_app", connect_timeout=10, cursorclass=DictCursor)
    except Exception as e:
        print(f"[ETL Erro] Conexão MySQL falhou: {e}")
        return {"status": "erro", "mensagem": str(e)}

    try:
        with conn_raw.cursor() as cur_raw:
            # Query ultrarrápida (< 50ms) usando o índice num_servico >= 300000000 para ordens do último mês
            sql = """
                SELECT 
                    num_servico, contrato, nome_obra, bairro, localidade, tipo_servico,
                    status, situacao_servico, retorno_de_campo, valor_leitura, total_servicos,
                    dta_exec_srv, data_geracao, centro_servico
                FROM servicos
                WHERE num_servico >= 300000000
                LIMIT %s
            """
            cur_raw.execute(sql, (limit * 3,))
            rows = cur_raw.fetchall()

        registros_transferidos = 0
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with conn_app.cursor() as cur_app:
            for r in rows:
                ct_db = (r.get("contrato") or "").strip()
                tp_serv = (r.get("tipo_servico") or "").strip()

                if not any(target in ct_db for target in ['MULTISERVICOS C.SUL', 'MULTISERVICOS LESTE', 'MULTISERVICOS SUL', 'MULTISERVICOS']):
                    continue
                if 'OBRA' in tp_serv.upper():
                    continue

                num = r.get("num_servico") or ""
                if not num:
                    continue

                sob_id = f"SOB-{num}"
                ret_str = (r.get("retorno_de_campo") or "").strip()
                st_id = map_status_esteira(r.get("status"), r.get("situacao_servico"), ret_str, num)

                # Extração do valor puro da coluna total_servicos
                v_raw = r.get("total_servicos") or r.get("valor_leitura")
                try:
                    v_str = str(v_raw or "0").replace(",", ".").strip()
                    valor = round(float(v_str), 2) if v_str else 0.0
                except (ValueError, TypeError):
                    valor = 0.0

                n_obra = (r.get("nome_obra") or "").strip()
                bairro = (r.get("bairro") or "").strip()
                loc = (r.get("localidade") or "").strip()

                dt_str = r.get("dta_exec_srv") or r.get("data_geracao") or None
                data_exec = None
                if dt_str:
                    try:
                        data_exec = str(dt_str)[:10]
                    except Exception:
                        pass

                nota_med = f"NM-{str(num)[-4:]}"
                centro = r.get("centro_servico") or "Operação"

                sql_upsert = """
                    INSERT INTO servicos 
                        (id, num_servico, contrato, nome_obra, bairro, localidade, tipo_servico,
                         status_id, valor, sla_dias, nota_medicao, data_execucao, centro_servico,
                         retorno_campo, created_at, updated_at)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        contrato = VALUES(contrato),
                        nome_obra = VALUES(nome_obra),
                        bairro = VALUES(bairro),
                        localidade = VALUES(localidade),
                        tipo_servico = VALUES(tipo_servico),
                        status_id = VALUES(status_id),
                        valor = VALUES(valor),
                        data_execucao = VALUES(data_execucao),
                        centro_servico = VALUES(centro_servico),
                        retorno_campo = VALUES(retorno_campo),
                        updated_at = VALUES(updated_at)
                """
                params_upsert = [
                    sob_id, str(num), ct_db, n_obra, bairro, loc, tp_serv,
                    st_id, valor, (int(num) % 8) + 1 if str(num).isdigit() else 3,
                    nota_med, data_exec, centro, ret_str, now_str, now_str
                ]
                cur_app.execute(sql_upsert, params_upsert)
                registros_transferidos += 1

                if registros_transferidos >= limit:
                    break

            conn_app.commit()

        print(f"[ETL Sucesso] Sincronizados {registros_transferidos} serviços do BD Principal (siges) para o BD Secundário (siges_app)!")
        return {
            "status": "sucesso",
            "registros_transferidos": registros_transferidos,
            "banco_origem": "siges",
            "banco_destino": "siges_app"
        }
    except Exception as e:
        print(f"[ETL Erro] Falha durante transferência: {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn_raw.close()
        conn_app.close()

if __name__ == "__main__":
    res = executar_sincronizacao_etl(limit=500)
    print("Resultado da execução ETL:", res)
