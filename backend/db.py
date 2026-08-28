import os
import sys
from datetime import datetime

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
    
    dbname = os.getenv("DB_APP_NAME", "siges_app")
    if not dbname or dbname == "siges":
        dbname = "siges_app"

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

def registrar_log_auditoria(servico_id, usuario_nome, usuario_email, campo_alterado, valor_anterior, novo_valor):
    """ RN-01: Log de Auditoria e Rastreabilidade """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO logs_auditoria 
                    (servico_id, usuario_nome, usuario_email, data_hora, campo_alterado, valor_anterior, novo_valor)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(sql, (servico_id, usuario_nome, usuario_email, now_str, campo_alterado, str(valor_anterior), str(novo_valor)))
        conn.commit()
        return True
    except Exception as e:
        print(f"[Erro Auditoria] Falha ao gravar log: {e}")
        return False
    finally:
        conn.close()

def buscar_logs_auditoria(servico_id):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM logs_auditoria WHERE servico_id = %s ORDER BY id DESC"
            cursor.execute(sql, (servico_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"[Erro Auditoria] {e}")
        return []
    finally:
        conn.close()

def buscar_servicos_db(contrato="todos", tipo="todos", status_id="todos", supervisor="todos", busca="", periodo="30d", limit=500):
    """
    Busca os dados EXCLUSIVAMENTE do banco secundário (siges_app.servicos)
    retornando todas as 36 colunas do Dicionário de Dados do CDU.md.
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
                    retorno_campo, cod_pep_obra, tdc, origem_sistema, incidencia, solicitante,
                    id_cliente, cliente, endereco, cod_turno, placa_veiculo, modelo_veiculo,
                    coordenador, supervisor, equipe, membros_equipe, obs_servico,
                    tipo_equipe, tipo_obra, sistema_faturamento, mes_medicao_inicial,
                    data_primeira_validacao, data_programacao
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

            if supervisor != "todos":
                sql += " AND supervisor = %s"
                params.append(supervisor)

            if busca:
                sql += " AND (id LIKE %s OR num_servico LIKE %s OR nome_obra LIKE %s OR contrato LIKE %s OR bairro LIKE %s OR localidade LIKE %s OR supervisor LIKE %s OR cod_pep_obra LIKE %s OR tdc LIKE %s)"
                b_str = f"%{busca}%"
                params.extend([b_str, b_str, b_str, b_str, b_str, b_str, b_str, b_str, b_str])

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
                if st_id in (2, 4, 6, 7):
                    p_tipo = ret_str.split('-')[1] if '-' in ret_str else (ret_str or "Pendência de Campo")
                    pend_items = [
                        {"t": "Evidências de Fotos", "tr": False, "det": f"Inconformidade: {ret_str}", "anx": None},
                        {"t": "Materiais Aplicados", "tr": False, "det": "Aguardando confirmação em campo", "anx": None}
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
                    "pend": pend_items,

                    # COLUNAS DO DICIONÁRIO DE DADOS EXPANDIDO (CDU.md)
                    "pep": r.get("cod_pep_obra") or f"PEP-{r.get('id')}",
                    "tdc": r.get("tdc") or f"TDC-{r.get('id')}",
                    "origem": r.get("origem_sistema") or "PDA",
                    "incidencia": r.get("incidencia") or f"INC-{r.get('id')}",
                    "solicitante": r.get("solicitante") or "Solicitante GPM",
                    "id_cliente": r.get("id_cliente") or "CLI-100",
                    "cliente": r.get("cliente") or "Cliente Cosampa",
                    "endereco": r.get("endereco") or local_str,
                    "turno": r.get("cod_turno") or "TURNO-1",
                    "placa": r.get("placa_veiculo") or "ABC-1234",
                    "modelo_veiculo": r.get("modelo_veiculo") or "Toyota Hilux",
                    "coordenador": r.get("coordenador") or "Carlos Eduardo",
                    "supervisor": r.get("supervisor") or "Roberto Santos",
                    "equipe": r.get("equipe") or "EQP-1",
                    "membros": r.get("membros_equipe") or "João Silva; Pedro Santos",
                    "obs": r.get("obs_servico") or "Serviço executado conforme padrão",
                    "tipo_equipe": r.get("tipo_equipe") or "Linha Viva",
                    "tipo_obra": r.get("tipo_obra") or "Manutenção de Rede",
                    "sistema_faturamento": r.get("sistema_faturamento") or "",
                    "mes_medicao_inicial": r.get("mes_medicao_inicial") or "",
                    "data_primeira_validacao": str(r.get("data_primeira_validacao")) if r.get("data_primeira_validacao") else "",
                    "data_programacao": str(r.get("data_programacao")) if r.get("data_programacao") else ""
                })

            return resultado
    except Exception as e:
        print(f"[Aviso DB] Erro ao consultar banco secundário 'siges_app': {e}")
        return []
    finally:
        conn.close()

def tramitar_servico_db(servico_id, novo_status_id, usuario_nome="Analista Fechamento", usuario_email="analista@cosampa.com.br"):
    """
    Tramita o status do serviço registrando Log de Auditoria (RN-01)
    e aplicando o travamento rígido por pendências (RN-03).
    """
    conn = get_db_connection()
    if not conn:
        return {"status": "erro", "mensagem": "Falha na conexão com o banco"}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT status_id FROM servicos WHERE id = %s", (servico_id,))
            row = cursor.fetchone()
            if not row:
                return {"status": "erro", "mensagem": "Serviço não encontrado"}
            
            status_atual = row["status_id"]

            # RN-03: Bloqueio de avanço se estiver em pendência
            if status_atual in (2, 4, 6) and novo_status_id in (3, 5, 7, 8, 13):
                return {"status": "bloqueado", "mensagem": "RN-03: Bloqueado! Existem pendências ativas que impedem o avanço para validação/faturamento."}

            cursor.execute("UPDATE servicos SET status_id = %s, updated_at = NOW() WHERE id = %s", (novo_status_id, servico_id))
            conn.commit()

        # RN-01: Log de Auditoria
        registrar_log_auditoria(servico_id, usuario_nome, usuario_email, "status_id", status_atual, novo_status_id)

        return {"status": "sucesso", "status_anterior": status_atual, "novo_status": novo_status_id}
    except Exception as e:
        print(f"[Erro Tramitação] {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()
