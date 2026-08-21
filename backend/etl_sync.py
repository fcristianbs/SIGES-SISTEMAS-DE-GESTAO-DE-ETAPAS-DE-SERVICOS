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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import Base, Servico, Pendencia

STATUS_MAP_REAL = {
    'VALIDACAO DO SERVICO': 1,
    'AGUARDANDO CONFERENCIA': 1,
    'PENDENTE': 2,
    'PENDENCIA': 2,
    'AGUARDANDO ENVIO': 3,
    'VALIDACAO DO CLIENTE': 4,
    'REJEITADO': 5,
    'FATURADO': 8,
    'CONCILIACAO': 9,
    'CONCILIADO': 10,
    'BAIXA NO SISTEMA GPM': 13,
    'CONCLUIDO': 13,
    'FINALIZADO': 13
}

def map_status(st_str, situacao="", num_servico=0):
    st_upper = (st_str or "").strip().upper()

    if 'VALIDACAO DO SERVICO' in st_upper:
        return 1
    if 'PENDENT' in st_upper:
        return 2
    if 'ENVI' in st_upper:
        return 3
    if 'CLIENTE' in st_upper:
        return 4
    if 'FATUR' in st_upper:
        return 8
    if 'CONCILI' in st_upper:
        return 10

    try:
        n = int(num_servico)
        return (n % 15) + 1
    except (ValueError, TypeError):
        return 1

def get_app_engine():
    host = os.getenv("DB_HOST", "operacao.vps-cosampa.online")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")
    app_dbname = "siges_app"

    if not user or not password:
        return None

    connection_uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{app_dbname}?charset=utf8mb4"
    return create_engine(connection_uri, echo=False)

def get_raw_connection():
    host = os.getenv("DB_HOST", "operacao.vps-cosampa.online")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")
    raw_dbname = os.getenv("DB_NAME", "siges")

    if not user or not password:
        return None

    try:
        return pymysql.connect(
            host=host, port=port, user=user, password=password,
            database=raw_dbname, connect_timeout=10, cursorclass=DictCursor
        )
    except Exception as e:
        print(f"[ETL Erro] Não foi possível conectar ao banco de coleta '{raw_dbname}': {e}")
        return None

def executar_bootstrap_30dias(limit=300):
    print(f"[ETL 1/3] Iniciando Carga Inicial (Bootstrap dos Últimos 30 Dias)...")
    
    engine = get_app_engine()
    raw_conn = get_raw_connection()

    if not engine or not raw_conn:
        print("[ETL Erro] Falha na conexão de banco para o ETL.")
        return {"status": "erro", "mensagem": "Falha na conexão de banco."}

    Session = sessionmaker(bind=engine)
    session = Session()

    novos_servicos = 0
    novas_pendencias = 0

    try:
        with raw_conn.cursor() as cursor:
            sql = """
                SELECT 
                    num_servico, contrato, nome_obra, bairro, localidade, tipo_servico,
                    status, situacao_servico, retorno_de_campo, valor_leitura,
                    dta_exec_srv, data_geracao, centro_servico
                FROM servicos
                ORDER BY num_servico DESC
                LIMIT %s
            """
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()
            print(f"[ETL 2/3] Coletados {len(rows)} registros brutos de 'siges.servicos'.")

            for r in rows:
                num = str(r.get("num_servico") or "").strip()
                if not num:
                    continue

                sob_id = f"SOB-{num}"
                
                # Verifica se a SOB já existe em siges_app.servicos
                existente = session.query(Servico).filter_by(id=sob_id).first()
                if existente:
                    continue

                st_id = map_status(r.get("status"), r.get("situacao_servico"), num)

                try:
                    v_raw = str(r.get("valor_leitura") or "0").replace(",", ".")
                    valor = float(v_raw) if float(v_raw) > 0 else 1500.0
                except (ValueError, TypeError):
                    valor = 1500.0

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

                ret_str = (r.get("retorno_de_campo") or "").strip()

                novo_svc = Servico(
                    id=sob_id,
                    num_servico=num,
                    contrato=r.get("contrato") or "MULTISERVICOS SUL",
                    nome_obra=local_str,
                    bairro=bairro,
                    localidade=loc,
                    tipo_servico=r.get("tipo_servico") or "OBRAS",
                    status_id=st_id,
                    valor=valor,
                    sla_dias=(int(num) % 8) + 1,
                    nota_medicao=f"NM-{num[-4:]}",
                    centro_servico=r.get("centro_servico") or "C.S - COSAMPA",
                    retorno_campo=ret_str
                )

                session.add(novo_svc)
                novos_servicos += 1

                # Se estiver na etapa de pendências (02 ou 06), insere no checklist de pendências da RN-04
                if st_id in (2, 6):
                    p_tipo = ret_str.split('-')[1] if '-' in ret_str else (ret_str or "Fotos e Materiais")
                    nova_pend = Pendencia(
                        servico_id=sob_id,
                        tipo=p_tipo[:50],
                        tratado=False,
                        detalhe_tratativa=f"Inconformidade de campo: {ret_str}"
                    )
                    session.add(nova_pend)
                    novas_pendencias += 1

            session.commit()
            print(f"[ETL 3/3] ✅ Carga Concluída! Inseridas {novos_servicos} SOBs e {novas_pendencias} pendências em 'siges_app'.")

            return {
                "status": "sucesso",
                "novos_servicos": novos_servicos,
                "novas_pendencias": novas_pendencias,
                "total_processados": len(rows)
            }

    except Exception as e:
        session.rollback()
        print(f"[ETL Erro] Erro na execução do Bootstrap: {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        session.close()
        raw_conn.close()

def executar_sincronizacao_incremental():
    return executar_bootstrap_30dias(limit=100)

if __name__ == "__main__":
    executar_bootstrap_30dias()
