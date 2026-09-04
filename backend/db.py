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
                    data_primeira_validacao, data_programacao,
                    valor_pago_cliente, mes_reapresentacao, divergencia_conciliacao
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
                    "data_programacao": str(r.get("data_programacao")) if r.get("data_programacao") else "",
                    "valor_pago": float(r.get("valor_pago_cliente") or 0.0),
                    "mes_reapresentacao": r.get("mes_reapresentacao") or "",
                    "divergencia_conciliacao": r.get("divergencia_conciliacao") or ""
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

            # RN-03: Bloqueio de avanço se estiver em pendência (só permite retornar para 1 ou 3)
            if status_atual in (2, 4, 6, 7) and novo_status_id not in (1, 3):
                return {"status": "bloqueado", "mensagem": "RN-03: Bloqueado! Existem pendências ativas que impedem o avanço direto para validação/faturamento."}

            cursor.execute("UPDATE servicos SET status_id = %s, updated_at = NOW() WHERE id = %s", (novo_status_id, servico_id))
            conn.commit()

        # RN-01: Log de Auditoria
        registrar_log_auditoria(servico_id, usuario_nome, usuario_email, "status_id", status_atual, novo_status_id)

        # Log Global de Ações
        desc_tech = {"de": status_atual, "para": novo_status_id}
        desc_human = f"{usuario_nome} tramitou o serviço {servico_id} do status 0{status_atual} para 0{novo_status_id}."
        registrar_acao_global(usuario_nome, usuario_email, "TRAMITACAO_STATUS", servico_id, desc_tech, desc_human)

        return {"status": "sucesso", "status_anterior": status_atual, "novo_status": novo_status_id}
    except Exception as e:
        print(f"[Erro Tramitação] {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()

def atualizar_dados_servico_db(servico_id, dados, usuario_nome="Analista", usuario_email="analista@cosampa.com.br"):
    """
    Atualiza campos específicos de um serviço e gera log de auditoria (RN-01).
    """
    conn = get_db_connection()
    if not conn:
        return {"status": "erro", "mensagem": "Falha na conexão"}
    
    try:
        with conn.cursor() as cursor:
            # Pega valores antigos para o log
            cursor.execute("SELECT * FROM servicos WHERE id = %s", (servico_id,))
            old_row = cursor.fetchone()
            if not old_row:
                return {"status": "erro", "mensagem": "Serviço não encontrado"}
            
            updates = []
            params = []
            logs_gerados = []
            
            for k, v in dados.items():
                # Ignorar chaves que não devem ser atualizadas diretamente ou que não existem
                if k in ["id", "status_id", "created_at", "updated_at"]:
                    continue
                updates.append(f"{k} = %s")
                params.append(v)
                old_val = old_row.get(k)
                if old_val != v:
                    logs_gerados.append((k, old_val, v))
            
            if not updates:
                return {"status": "sucesso", "mensagem": "Nenhum dado alterado."}
                
            updates.append("updated_at = NOW()")
            sql = f"UPDATE servicos SET {', '.join(updates)} WHERE id = %s"
            params.append(servico_id)
            
            cursor.execute(sql, tuple(params))
            conn.commit()
            
        for campo, val_ant, val_novo in logs_gerados:
            registrar_log_auditoria(servico_id, usuario_nome, usuario_email, campo, val_ant, val_novo)
            
            # Log Global de Ações
            desc_tech = {"campo": campo, "de": str(val_ant), "para": str(val_novo)}
            desc_human = f"{usuario_nome} atualizou '{campo}' de '{val_ant}' para '{val_novo}' no serviço {servico_id}."
            registrar_acao_global(usuario_nome, usuario_email, "EDICAO_DADOS", servico_id, desc_tech, desc_human)
            
        return {"status": "sucesso"}
    except Exception as e:
        print(f"[Erro Atualização DB] {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()

import json

def registrar_acao_global(usuario_nome, usuario_email, acao_tipo, entidade_id, descricao_tecnica, descricao_humanizada):
    """ Grava log detalhado de ação de negócio no sistema """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        if isinstance(descricao_tecnica, dict):
            descricao_tecnica = json.dumps(descricao_tecnica, ensure_ascii=False)
            
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO registro_acoes 
                    (data_hora, usuario_nome, usuario_email, acao_tipo, entidade_id, descricao_tecnica, descricao_humanizada)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(sql, (
                now_str, 
                usuario_nome, 
                usuario_email, 
                acao_tipo, 
                str(entidade_id), 
                descricao_tecnica, 
                descricao_humanizada
            ))
        conn.commit()
        return True
    except Exception as e:
        print(f"[Erro Log Ação] Falha ao gravar registro global: {e}")
        return False
    finally:
        conn.close()

import pandas as pd

def processar_importacao_dinamica(temp_file_path, aba, header_idx, mapeamento_de_para, usuario_nome="Importador", usuario_email="importador@cosampa.com.br"):
    """
    Carrega o arquivo temporario via pandas e faz o update na base.
    Ignora valores nulos da planilha, nao alterando o registro original.
    """
    try:
        df = pd.read_excel(temp_file_path, sheet_name=aba, header=header_idx)
        # Substitui nulos ou NaN do pandas por None (python)
        df = df.where(pd.notnull(df), None)
    except Exception as e:
        print(f"[Erro Processar Excel] {e}")
        return {"status": "erro", "mensagem": f"Erro ao ler a planilha: {str(e)}"}

    coluna_chave_interna = 'num_servico'
    # Procurar qual coluna do excel foi mapeada para 'num_servico'
    coluna_chave_planilha = None
    for int_col, ext_col in mapeamento_de_para.items():
        if int_col == coluna_chave_interna:
            coluna_chave_planilha = ext_col
            break
            
    if not coluna_chave_planilha:
        return {"status": "erro", "mensagem": "O mapeamento do 'Número do Serviço' é obrigatório."}

    sucessos = 0
    falhas = []
    
    conn = get_db_connection()
    if not conn:
        return {"status": "erro", "mensagem": "Falha de conexão com o BD."}
        
    try:
        with conn.cursor() as cursor:
            for idx, row in df.iterrows():
                chave_valor = row.get(coluna_chave_planilha)
                if not chave_valor:
                    continue
                    
                chave_str = str(chave_valor).strip()
                if not chave_str.startswith("SOB-"):
                    chave_str = f"SOB-{chave_str}"
                    
                set_clauses = []
                values = []
                campos_alterados = {}
                
                # Para evitar loops complexos buscando valores antigos (RN-01),
                # faremos um SELECT para pegar o estado antigo da OS
                cursor.execute("SELECT * FROM servicos WHERE num_servico = %s", (chave_str,))
                old_row = cursor.fetchone()
                
                if not old_row:
                    falhas.append(chave_str)
                    continue

                for col_interna, col_planilha in mapeamento_de_para.items():
                    if col_interna == coluna_chave_interna:
                        continue 
                    
                    if col_planilha in row:
                        val_novo = row[col_planilha]
                        # Ignorar valores em branco do excel (conforme feedback)
                        if val_novo is None or str(val_novo).strip() == "":
                            continue
                            
                        # Verifica se realmente houve mudanca
                        val_antigo = old_row.get(col_interna)
                        if str(val_antigo) != str(val_novo):
                            set_clauses.append(f"{col_interna} = %s")
                            # Convertemos para string nativa para evitar problemas com JSON/pymysql com datas/tempos
                            values.append(str(val_novo))
                            campos_alterados[col_interna] = {"antigo": str(val_antigo), "novo": str(val_novo)}
                
                if not set_clauses:
                    sucessos += 1 # Conta como sucesso mesmo se nada mudou (ja tava certo)
                    continue
                    
                set_clauses.append("updated_at = NOW()")
                query = f"UPDATE servicos SET {', '.join(set_clauses)} WHERE num_servico = %s"
                values.append(chave_str)
                
                cursor.execute(query, tuple(values))
                if cursor.rowcount > 0:
                    sucessos += 1
                    # Logs (RN-01)
                    servico_id = old_row["id"]
                    for k, v in campos_alterados.items():
                        registrar_log_auditoria(servico_id, usuario_nome, usuario_email, k, v["antigo"], v["novo"])
                        
                    # Log Global
                    desc_tech = {"modificacoes": campos_alterados, "via": "IMPORTACAO_EXCEL"}
                    desc_human = f"{usuario_nome} importou dados atualizando {len(campos_alterados)} campo(s) via Planilha."
                    registrar_acao_global(usuario_nome, usuario_email, "EDICAO_DADOS_LOTE", servico_id, desc_tech, desc_human)

        conn.commit()
    except Exception as e:
        print(f"[Erro Importacao] {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()
        
    return {"status": "concluido", "atualizados": sucessos, "nao_encontrados": falhas}
