from backend.app.database.connection import get_db_cursor


def obter_opcoes_filtro():
    """ Retorna listas de valores únicos para preencher os Selects de filtro no Frontend. """
    try:
        with get_db_cursor() as cursor:
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
    except Exception as e:
        print(f"[Erro Filtro Options] {e}")
        return {"contratos": [], "tipos": [], "supervisores": [], "coordenadores": []}


def obter_parametros_pendencias():
    """ Retorna os itens ativos de correção de pendências (Cosampa e Distribuidora) """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id, categoria, descricao FROM itens_correcao_cosampa WHERE ativo = 1 ORDER BY categoria, id")
            cosampa = cursor.fetchall()
            
            cursor.execute("SELECT id, descricao FROM itens_correcao_distribuidora WHERE ativo = 1 ORDER BY id")
            distribuidora = cursor.fetchall()
            
            return {"cosampa": cosampa, "distribuidora": distribuidora}
    except Exception as e:
        print(f"[Erro Parametros Pendencias] {e}")
        return {"cosampa": [], "distribuidora": []}


def obter_servico_por_id(servico_id):
    """ Busca um serviço por id numérico ou chave primária """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM servicos WHERE id = %s", (servico_id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"[Erro Obter Servico {servico_id}] {e}")
        return None


def obter_servico_por_chave(chave):
    """ Busca um serviço por id ou num_servico """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM servicos WHERE id = %s OR num_servico = %s", (chave, chave))
            return cursor.fetchone()
    except Exception as e:
        print(f"[Erro Obter Servico Chave {chave}] {e}")
        return None


def buscar_servicos_paginados(contrato="todos", tipo="todos", status_id="todos", 
                              supervisor="todos", coordenador="todos", busca="", 
                              periodo="30d", limit=100, skip=0, status_in=None):
    """
    Busca os serviços no MySQL secundário (siges_app.servicos)
    com paginação, contagem total e ordenação pela transmissão mais recente.
    """
    try:
        with get_db_cursor() as cursor:
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
                params.extend([term] * 9)

            # Contagem Total
            cursor.execute("SELECT COUNT(id) as total " + base_sql, params)
            total_count = cursor.fetchone()['total']

            # Busca paginada com ordenação pela transmissão mais recente
            sql = f"""
                SELECT 
                    id, num_servico, contrato, nome_obra, bairro, localidade, tipo_servico,
                    status_id, valor, sla_dias, nota_medicao, data_execucao, centro_servico,
                    retorno_campo, cod_pep_obra, tdc, origem_sistema, incidencia, solicitante,
                    id_cliente, cliente, endereco, cod_turno, placa_veiculo, modelo_veiculo,
                    coordenador, supervisor, equipe, membros_equipe, obs_servico,
                    tipo_equipe, tipo_obra, sistema_faturamento, mes_medicao_inicial,
                    data_primeira_validacao, data_validacao, data_programacao, mes_emissao,
                    valor_pago_cliente, mes_reapresentacao, divergencia_conciliacao,
                    responsavel_disputa, sharepoint_url
                {base_sql}
                ORDER BY COALESCE(updated_at, '2000-01-01') DESC, id DESC LIMIT %s OFFSET %s
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
                if dt_val:
                    if hasattr(dt_val, "strftime"):
                        dt_str = dt_val.strftime("%d/%m/%Y")
                    else:
                        dt_s = str(dt_val).strip()
                        parts = dt_s.split("-")
                        if len(parts) == 3 and len(parts[0]) == 4:
                            dt_str = f"{parts[2][:2]}/{parts[1]}/{parts[0]}"
                        else:
                            dt_str = dt_s
                else:
                    dt_str = "Hoje"

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
                    "data_raw": str(dt_val) if dt_val else "",
                    "dep": r.get("centro_servico") or "Operação",
                    "ret": ret_str,
                    "pend": pend_items,

                    # DICIONÁRIO DE DADOS EXPANDIDO (CDU)
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
        print(f"[Erro Repositório Serviços] {e}")
        return {"data": [], "total": 0}


def atualizar_campos_servico(servico_id, updates_dict):
    """
    Executa a atualização de campos arbitrários de um serviço no banco de dados.
    Retorna o número de linhas afetadas.
    """
    if not updates_dict:
        return 0

    updates = []
    params = []
    for k, v in updates_dict.items():
        if k in ["id", "created_at"]:
            continue
        updates.append(f"{k} = %s")
        params.append(v)

    updates.append("updated_at = NOW()")
    sql = f"UPDATE servicos SET {', '.join(updates)} WHERE id = %s"
    params.append(servico_id)

    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, tuple(params))
            return cursor.rowcount
    except Exception as e:
        print(f"[Erro Update Servico {servico_id}] {e}")
        raise
