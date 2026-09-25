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

def obter_opcoes_filtro_db():
    """ Retorna listas de valores únicos para preencher os Selects de filtro no Frontend. """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT contrato FROM servicos WHERE contrato IS NOT NULL AND contrato != ''")
            contratos = [r['contrato'] for r in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT tipo_servico FROM servicos WHERE tipo_servico IS NOT NULL AND tipo_servico != ''")
            tipos = [r['tipo_servico'] for r in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT supervisor FROM servicos WHERE supervisor IS NOT NULL AND supervisor != ''")
            supervisores = [r['supervisor'] for r in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT coordenador FROM servicos WHERE coordenador IS NOT NULL AND coordenador != ''")
            coordenadores = [r['coordenador'] for r in cursor.fetchall()]
            
            return {
                "contratos": sorted(contratos),
                "tipos": sorted(tipos),
                "supervisores": sorted(supervisores),
                "coordenadores": sorted(coordenadores)
            }
    finally:
        conn.close()

def buscar_servicos_db(contrato="todos", tipo="todos", status_id="todos", supervisor="todos", coordenador="todos", busca="", periodo="30d", limit=100, skip=0, status_in=None):
    """
    Busca os dados EXCLUSIVAMENTE do banco secundário (siges_app.servicos)
    retornando todas as colunas do Dicionário de Dados do CDU.md,
    com paginação (limit/skip) e contagem total.
    """
    conn = get_db_connection()
    if not conn:
        return {"data": [], "total": 0}

    try:
        with conn.cursor() as cursor:
            # Construir query base
            base_sql = "FROM servicos WHERE 1=1"
            params = []

            if contrato != "todos":
                base_sql += " AND contrato = %s"
                params.append(contrato)

            if tipo != "todos":
                base_sql += " AND tipo_servico = %s"
                params.append(tipo)

            if status_id != "todos":
                try:
                    base_sql += " AND status_id = %s"
                    params.append(int(status_id))
                except ValueError:
                    pass
            elif status_in:
                # Expects a list of ints or a comma-separated string
                if isinstance(status_in, str):
                    status_in = [int(x.strip()) for x in status_in.split(',') if x.strip().isdigit()]
                if status_in:
                    placeholders = ','.join(['%s'] * len(status_in))
                    base_sql += f" AND status_id IN ({placeholders})"
                    params.extend(status_in)

            if supervisor != "todos":
                base_sql += " AND supervisor = %s"
                params.append(supervisor)
                
            if coordenador != "todos":
                base_sql += " AND coordenador = %s"
                params.append(coordenador)

            if busca:
                base_sql += " AND (id LIKE %s OR num_servico LIKE %s OR nome_obra LIKE %s OR contrato LIKE %s OR bairro LIKE %s OR localidade LIKE %s OR supervisor LIKE %s OR cod_pep_obra LIKE %s OR tdc LIKE %s)"
                term = f"%{busca}%"
                params.extend([term]*9)

            # Contagem Total
            cursor.execute("SELECT COUNT(id) as total " + base_sql, params)
            total_count = cursor.fetchone()['total']

            # Busca paginada
            sql = f"""
                SELECT 
                    id, num_servico, contrato, nome_obra, bairro, localidade, tipo_servico,
                    status_id, valor, sla_dias, nota_medicao, data_execucao, centro_servico,
                    retorno_campo, cod_pep_obra, tdc, origem_sistema, incidencia, solicitante,
                    id_cliente, cliente, endereco, cod_turno, placa_veiculo, modelo_veiculo,
                    coordenador, supervisor, equipe, membros_equipe, obs_servico,
                    tipo_equipe, tipo_obra, sistema_faturamento, mes_medicao_inicial,
                    data_primeira_validacao, data_programacao,
                    valor_pago_cliente, mes_reapresentacao, divergencia_conciliacao
                {base_sql}
                ORDER BY id DESC LIMIT %s OFFSET %s
            """
            params_busca = list(params) + [limit, skip]
            cursor.execute(sql, params_busca)
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
                    "origem": r.get("origem_sistema") or "",
                    "origem_sistema": r.get("origem_sistema") or "",
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
                    "data_validacao": str(r.get("data_validacao")) if r.get("data_validacao") else (str(r.get("data_primeira_validacao")) if r.get("data_primeira_validacao") else ""),
                    "mes_emissao": r.get("mes_emissao") or "",
                    "data_programacao": str(r.get("data_programacao")) if r.get("data_programacao") else "",
                    "valor_pago": float(r.get("valor_pago_cliente") or 0.0),
                    "mes_reapresentacao": r.get("mes_reapresentacao") or "",
                    "divergencia_conciliacao": r.get("divergencia_conciliacao") or "",
                    "responsavel_disputa": r.get("responsavel_disputa") or "",
                    "sharepoint_url": r.get("sharepoint_url") or ""
                })

            return {"data": resultado, "total": total_count}
    except Exception as e:
        print(f"[Aviso DB] Erro ao consultar banco secundário 'siges_app': {e}")
        return {"data": [], "total": 0}
    finally:
        conn.close()

def tramitar_servico_db(servico_id, novo_status_id, usuario_nome="Analista Fechamento", usuario_email="analista@cosampa.com.br"):
    """
    Tramita o status do serviço registrando Log de Auditoria (RN-01),
    aplicando o travamento rígido por pendências (RN-03),
    a Validação Obrigatória do Sistema de Origem (CDU V5 Bloco 4),
    o Bypass do Fluxo Comercial (CDU V5 Bloco 4) e
    as Validações de Faturamento e Conciliação (CDU V5 Bloco 5).
    """
    conn = get_db_connection()
    if not conn:
        return {"status": "erro", "mensagem": "Falha na conexão com o banco"}

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, num_servico, status_id, contrato, tipo_servico, tipo_obra, origem_sistema, 
                       data_validacao, data_primeira_validacao, mes_emissao, mes_reapresentacao, valor, valor_pago_cliente
                FROM servicos WHERE id = %s
            """, (servico_id,))
            row = cursor.fetchone()
            if not row:
                return {"status": "erro", "mensagem": "Serviço não encontrado"}
            
            status_atual = row["status_id"]
            origem = (row.get("origem_sistema") or "").strip()
            contrato = (row.get("contrato") or "").strip().upper()
            tp_servico = (row.get("tipo_servico") or "").strip().upper()
            tp_obra = (row.get("tipo_obra") or "").strip().upper()

            # Imutabilidade: Status 14 (FATURADO TOTAL - FINALIZADO) trancado
            if status_atual == 14 and usuario_email != "admin@cosampa.com.br":
                return {
                    "status": "bloqueado",
                    "mensagem": f"Serviço {servico_id}: Bloqueado! Este serviço já está no status FATURADO TOTAL (FINALIZADO) e é protegido contra qualquer alteração."
                }

            # RN-03: Bloqueio de avanço se estiver em pendência (só permite retornar para 1 ou 3)
            if status_atual in (2, 4, 6, 7) and novo_status_id not in (1, 3):
                return {"status": "bloqueado", "mensagem": f"Serviço {servico_id}: Bloqueado! Existem pendências ativas que impedem o avanço direto para validação/faturamento (RN-03)."}

            # CDU V5 - Bloco 4: Validação Obrigatória de Origem
            if status_atual == 1 and novo_status_id not in (2, 4):
                if not origem or origem in ("NÃO VALIDADO", "PENDENTE"):
                    return {
                        "status": "bloqueado",
                        "mensagem": f"Serviço {servico_id}: Validação Obrigatória do Sistema de Origem não confirmada! É necessário definir o Sistema de Origem (Eorder, Synergia, SacBt, etc) antes de avançar."
                    }

            # CDU V5 - Bloco 5: Validação da Tela 04 (Faturamento 08 -> 09)
            if status_atual == 8 and novo_status_id == 9:
                dt_val = row.get("data_validacao") or row.get("data_primeira_validacao")
                if not dt_val:
                    return {
                        "status": "bloqueado",
                        "mensagem": f"Serviço {servico_id}: O preenchimento da Data de Validação é obrigatório para avançar para o Faturado/Conciliação (CDU V5 - Tela 04)."
                    }

            # CDU V5 - Bloco 5: Validação da Tela 05 (Conciliação 09 -> 10)
            if status_atual == 9 and novo_status_id == 10:
                mes_em = (row.get("mes_emissao") or "").strip()
                if not mes_em:
                    return {
                        "status": "bloqueado",
                        "mensagem": f"Serviço {servico_id}: O preenchimento do Mês de Emissão (MM/AAAA) é obrigatório para iniciar a Conciliação (CDU V5 - Tela 05)."
                    }

            # CDU V5 - Bloco 5: Validação do Status 11 -> 12 (Divergências -> Cobrar)
            if status_atual == 11 and novo_status_id == 12:
                cursor.execute("""
                    SELECT COUNT(*) as cnt FROM comentarios_internos 
                    WHERE servico_id = %s AND (INSTR(texto, 'Justificativa') > 0 OR (usuario_nome != 'Conciliador Automático SIGES' AND usuario_nome != 'Sistema SIGES'))
                """, (servico_id,))
                c_row = cursor.fetchone()
                if not c_row or c_row["cnt"] == 0:
                    return {
                        "status": "bloqueado",
                        "mensagem": f"Serviço {servico_id}: É obrigatório registrar uma justificativa técnica da divergência na Timeline antes de avançar para cobrança (CDU V5 - Status 11)."
                    }

            # CDU V5 - Bloco 5: Validação do Status 12 -> 13 (Cobrar -> Em Disputa)
            if status_atual == 12 and novo_status_id == 13:
                mes_reap = (row.get("mes_reapresentacao") or "").strip()
                if not mes_reap:
                    return {
                        "status": "bloqueado",
                        "mensagem": f"Serviço {servico_id}: O preenchimento do Mês de Reapresentação da Medição é obrigatório para submeter a disputa (CDU V5 - Status 12)."
                    }
                cursor.execute("UPDATE servicos SET responsavel_disputa = %s WHERE id = %s", (usuario_nome, servico_id))

            # CDU V5 - Bloco 4: Bypass do Fluxo Comercial (Salto de Status 01 -> 08)
            is_comercial = ("COMERCIAL" in contrato) or ("COMERCIAL" in tp_servico) or ("COMERCIAL" in tp_obra)
            bypass_aplicado = False
            if status_atual == 1 and novo_status_id == 3 and is_comercial:
                novo_status_id = 8
                bypass_aplicado = True

            cursor.execute("UPDATE servicos SET status_id = %s, updated_at = NOW() WHERE id = %s", (novo_status_id, servico_id))
            conn.commit()

        # RN-01: Log de Auditoria
        registrar_log_auditoria(servico_id, usuario_nome, usuario_email, "status_id", status_atual, novo_status_id)

        # Se houve Bypass Comercial, registra no histórico / timeline
        if bypass_aplicado:
            try:
                inserir_comentario_db(
                    servico_id=servico_id,
                    usuario_id=1,
                    usuario_nome="Sistema SIGES",
                    texto="⚡ [Bypass Comercial - CDU V5] Serviço de fluxo Comercial aprovado na Medição: pulou automaticamente para o Status 08 (Validado Aguardando Faturamento)."
                )
            except Exception as e_cmt:
                print(f"[Aviso Timeline Bypass] {e_cmt}")

        # Log Global de Ações
        desc_tech = {"de": status_atual, "para": novo_status_id, "bypass_comercial": bypass_aplicado}
        desc_human = f"{usuario_nome} tramitou o serviço {servico_id} do status 0{status_atual} para 0{novo_status_id}."
        if bypass_aplicado:
            desc_human += " (Bypass Comercial aplicado: direcionado direto para Status 08)"
        registrar_acao_global(usuario_nome, usuario_email, "TRAMITACAO_STATUS", servico_id, desc_tech, desc_human)

        return {
            "status": "sucesso",
            "status_anterior": status_atual,
            "novo_status": novo_status_id,
            "bypass_comercial": bypass_aplicado
        }
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

def inserir_comentario_db(servico_id, usuario_id, usuario_nome, texto):
    conn = get_db_connection()
    if not conn:
        return {"status": "erro", "mensagem": "Falha na conexão"}
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO comentarios_internos (servico_id, usuario_id, usuario_nome, texto)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (servico_id, usuario_id, usuario_nome, texto))
            novo_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM comentarios_internos WHERE id = %s", (novo_id,))
            comentario = cursor.fetchone()
        conn.commit()
        return {"status": "sucesso", "data": comentario}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()

def buscar_comentarios_db(servico_id):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT id, servico_id, usuario_id, usuario_nome, texto, criado_em 
                FROM comentarios_internos 
                WHERE servico_id = %s 
                ORDER BY criado_em ASC
            """
            cursor.execute(sql, (servico_id,))
            return cursor.fetchall()
    except Exception as e:
        return []
    finally:
        conn.close()

def obter_parametros_pendencias_db():
    conn = get_db_connection()
    if not conn: return {"cosampa": [], "distribuidora": []}
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, categoria, descricao FROM itens_correcao_cosampa WHERE ativo = 1 ORDER BY categoria, id")
            cosampa = cursor.fetchall()
            
            cursor.execute("SELECT id, descricao FROM itens_correcao_distribuidora WHERE ativo = 1 ORDER BY id")
            distribuidora = cursor.fetchall()
            
            return {"cosampa": cosampa, "distribuidora": distribuidora}
    except Exception as e:
        return {"cosampa": [], "distribuidora": []}
    finally:
        conn.close()

# ==============================================================================
# CDU V5 - BLOCO 5: FUNÇÕES DE CONCILIAÇÃO E COMPARADOR BILATERAL
# ==============================================================================

def gerar_snapshot_conciliacao_db(servico_ids, evento_id=None):
    """
    CDU V5 - Tela 05 (Item 2 - Status 10):
    Gera um snapshot imutável ("Relatório ANTES") do estado dos serviços 
    antes da conciliação/importação da planilha de pagamentos.
    """
    conn = get_db_connection()
    if not conn:
        return {"status": "erro", "mensagem": "Falha na conexão com o banco"}
    
    if not evento_id:
        evento_id = f"EVT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    try:
        total_gravados = 0
        with conn.cursor() as cursor:
            for sid in servico_ids:
                cursor.execute("SELECT * FROM servicos WHERE id = %s", (sid,))
                srv = cursor.fetchone()
                if not srv:
                    continue
                
                srv_json = json.dumps(srv, default=str, ensure_ascii=False)
                st_ant = srv.get("status_id") or 9
                v_fat = srv.get("valor") or 0.0
                v_pago_ant = srv.get("valor_pago_cliente") or 0.0

                cursor.execute("""
                    INSERT INTO conciliacao_snapshots 
                        (evento_id, servico_id, status_id_anterior, valor_faturado, valor_pago_anterior, dados_servico_json, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (evento_id, sid, st_ant, v_fat, v_pago_ant, srv_json))
                total_gravados += 1

            conn.commit()
        return {"status": "sucesso", "evento_id": evento_id, "total_snapshots": total_gravados}
    except Exception as e:
        print(f"[Erro Snapshot Conciliação] {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()

def buscar_snapshot_conciliacao_db(evento_id):
    """
    Retorna os registros do snapshot do 'Relatório ANTES' para auditoria e conferência.
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT cs.id, cs.evento_id, cs.servico_id, cs.status_id_anterior, 
                       cs.valor_faturado, cs.valor_pago_anterior, cs.created_at,
                       s.contrato, s.num_servico, s.tdc, s.cliente, s.tipo_servico
                FROM conciliacao_snapshots cs
                LEFT JOIN servicos s ON s.id = cs.servico_id
                WHERE cs.evento_id = %s
                ORDER BY cs.id ASC
            """, (evento_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"[Erro Busca Snapshot] {e}")
        return []
    finally:
        conn.close()

def fechar_evento_conciliacao_db(evento_id, itens_pagamento, usuario_nome="Analista Fechamento", usuario_email="analista@cosampa.com.br"):
    """
    CDU V5 - Tela 05 (Item 2 - Status 10):
    Executa o fechamento do evento de conciliação:
    - Se o valor pago bater 100% com o valor executado: avança para 14 (FATURADO TOTAL - FINALIZADO) e bloqueia.
    - Se houver divergência de valor: avança para 11 (CONCILIADO COM DIVERGENCIAS),
      calcula DIVERGÊNCIA DA CONCILIAÇÃO e grava ocorrência na Timeline.
    """
    conn = get_db_connection()
    if not conn:
        return {"status": "erro", "mensagem": "Falha na conexão com o banco"}

    finalizados = 0
    divergentes = 0
    detalhes = []

    try:
        # Primeiro, gera o snapshot de segurança caso ainda não exista para o evento
        sids = [it.get("id") or it.get("num_servico") for it in itens_pagamento if it.get("id") or it.get("num_servico")]
        gerar_snapshot_conciliacao_db(sids, evento_id)

        for item in itens_pagamento:
            sid = item.get("id") or item.get("num_servico")
            v_pago = float(item.get("valor_pago") or 0.0)

            with conn.cursor() as cursor:
                cursor.execute("SELECT id, num_servico, valor, valor_pago_cliente, status_id FROM servicos WHERE id = %s OR num_servico = %s", (sid, sid))
                srv = cursor.fetchone()
                if not srv:
                    detalhes.append({"id": sid, "status": "nao_encontrado"})
                    continue

                real_id = srv["id"]
                v_fat = float(srv.get("valor") or 0.0)
                dif = round(v_fat - v_pago, 2)

                if abs(dif) < 0.01:
                    # 100% Batido! Finalizado
                    novo_st = 14
                    div_str = ""
                    cursor.execute("""
                        UPDATE servicos 
                        SET status_id = %s, valor_pago_cliente = %s, divergencia_conciliacao = %s, updated_at = NOW() 
                        WHERE id = %s
                    """, (novo_st, v_pago, div_str, real_id))
                    conn.commit()

                    inserir_comentario_db(
                        servico_id=real_id,
                        usuario_id=1,
                        usuario_nome="Conciliador Automático SIGES",
                        texto=f"✅ [Conciliação Automática - CDU V5] Evento '{evento_id}': Pagamento 100% batido com a Distribuidora (R$ {v_pago:.2f}). Serviço encerrado em FATURADO TOTAL (FINALIZADO)."
                    )
                    registrar_log_auditoria(real_id, usuario_nome, usuario_email, "status_id", srv["status_id"], novo_st)
                    finalizados += 1
                    detalhes.append({"id": real_id, "resultado": "finalizado", "valor_faturado": v_fat, "valor_pago": v_pago, "status_id": novo_st})
                else:
                    # Com Divergência! Status 11
                    novo_st = 11
                    div_str = f"R$ {dif:.2f}"
                    tipo_div = "a menor (possível glosa)" if dif > 0 else "a maior"
                    cursor.execute("""
                        UPDATE servicos 
                        SET status_id = %s, valor_pago_cliente = %s, divergencia_conciliacao = %s, updated_at = NOW() 
                        WHERE id = %s
                    """, (novo_st, v_pago, div_str, real_id))
                    conn.commit()

                    inserir_comentario_db(
                        servico_id=real_id,
                        usuario_id=1,
                        usuario_nome="Conciliador Automático SIGES",
                        texto=f"⚠️ [Conciliação Automática - CDU V5] Evento '{evento_id}': Divergência identificada {tipo_div}! Valor Faturado: R$ {v_fat:.2f} vs Valor Pago: R$ {v_pago:.2f} (Diferença: {div_str}). Serviço encaminhado para reanálise no Status 11."
                    )
                    registrar_log_auditoria(real_id, usuario_nome, usuario_email, "status_id", srv["status_id"], novo_st)
                    registrar_log_auditoria(real_id, usuario_nome, usuario_email, "divergencia_conciliacao", "", div_str)
                    divergentes += 1
                    detalhes.append({"id": real_id, "resultado": "divergente", "valor_faturado": v_fat, "valor_pago": v_pago, "diferenca": dif, "status_id": novo_st})

        return {
            "status": "sucesso",
            "evento_id": evento_id,
            "total_processados": len(detalhes),
            "finalizados": finalizados,
            "divergentes": divergentes,
            "detalhes": detalhes
        }
    except Exception as e:
        print(f"[Erro Fechamento Evento] {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()

def obter_comparador_bilateral_db(servico_id):
    """
    CDU V5 - Tela 01 (Item 2 - Status 11):
    Retorna os dados do Comparador Dinâmico Bilateral:
    Atividade Executada (Valor Realizado) vs. Atividade Paga (Valor Pago).
    """
    conn = get_db_connection()
    if not conn:
        return {"status": "erro", "mensagem": "Falha na conexão com o banco"}

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM servicos WHERE id = %s", (servico_id,))
            srv = cursor.fetchone()
            if not srv:
                return {"status": "erro", "mensagem": "Serviço não encontrado"}

            # Busca itens de baremo_itens
            cursor.execute("SELECT * FROM baremo_itens WHERE servico_id = %s", (servico_id,))
            itens = cursor.fetchall()

            # Se não houver itens detalhados cadastrados, monta linha de atividade com o valor do serviço
            if not itens:
                v_fat = float(srv.get("valor") or 0.0)
                v_pago = float(srv.get("valor_pago_cliente") or 0.0)
                itens = [{
                    "id": 1,
                    "servico_id": servico_id,
                    "codigo_item": srv.get("num_servico") or servico_id,
                    "descricao": srv.get("tipo_servico") or "Atividade Principal Executada",
                    "quantidade": 1.0,
                    "valor_medido": v_fat,
                    "quantidade_paga": 1.0 if v_pago > 0 else 0.0,
                    "valor_pago_item": v_pago,
                    "divergencia_item": round(v_fat - v_pago, 2)
                }]

            sharepoint = srv.get("sharepoint_url") or f"https://cosampa.sharepoint.com/sites/medicoes/comprovantes/{srv.get('num_servico')}"

            return {
                "status": "sucesso",
                "servico": {
                    "id": srv["id"],
                    "num_servico": srv["num_servico"],
                    "contrato": srv["contrato"],
                    "tipo_servico": srv["tipo_servico"],
                    "cliente": srv["cliente"],
                    "status_id": srv["status_id"],
                    "valor": float(srv["valor"] or 0.0),
                    "valor_pago": float(srv["valor_pago_cliente"] or 0.0),
                    "divergencia": srv.get("divergencia_conciliacao") or f"R$ {float(srv['valor'] or 0.0) - float(srv['valor_pago_cliente'] or 0.0):.2f}",
                    "mes_reapresentacao": srv.get("mes_reapresentacao") or "",
                    "responsavel_disputa": srv.get("responsavel_disputa") or "",
                    "sharepoint_url": sharepoint
                },
                "itens": itens
            }
    except Exception as e:
        print(f"[Erro Comparador Bilateral] {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()

def salvar_comparador_bilateral_db(servico_id, novo_status_id, justificativa="", mes_reapresentacao="", sharepoint_url="", usuario_nome="Analista Fechamento", usuario_email="analista@cosampa.com.br"):
    """
    CDU V5 - Tela 01 (Status 11 -> 12 -> 13):
    Salva a tratativa do Comparador Bilateral, injeta a justificativa na Timeline
    e tramita o serviço.
    """
    conn = get_db_connection()
    if not conn:
        return {"status": "erro", "mensagem": "Falha na conexão com o banco"}

    try:
        with conn.cursor() as cursor:
            # 1. Se informou novo sharepoint_url, atualiza
            if sharepoint_url:
                cursor.execute("UPDATE servicos SET sharepoint_url = %s WHERE id = %s", (sharepoint_url, servico_id))
            
            # 2. Se informou mes_reapresentacao, atualiza
            if mes_reapresentacao:
                cursor.execute("UPDATE servicos SET mes_reapresentacao = %s WHERE id = %s", (mes_reapresentacao, servico_id))
                registrar_log_auditoria(servico_id, usuario_nome, usuario_email, "mes_reapresentacao", "", mes_reapresentacao)

            conn.commit()

        # 3. Insere a justificativa na Timeline
        if justificativa and justificativa.strip():
            inserir_comentario_db(
                servico_id=servico_id,
                usuario_id=1,
                usuario_nome=usuario_nome,
                texto=f"⚖️ [Justificativa de Divergência - CDU V5]: {justificativa.strip()}"
            )

        # 4. Tramita o serviço
        return tramitar_servico_db(servico_id, novo_status_id, usuario_nome, usuario_email)
    except Exception as e:
        print(f"[Erro Salvar Comparador] {e}")
        return {"status": "erro", "mensagem": str(e)}
    finally:
        conn.close()

