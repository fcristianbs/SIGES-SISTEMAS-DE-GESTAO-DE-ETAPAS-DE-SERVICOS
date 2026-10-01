from backend.app.database.connection import get_db_cursor
from backend.app.database.repositories.auditoria_repo import (
    registrar_log_auditoria, 
    registrar_acao_global, 
    inserir_comentario
)
from backend.app.database.repositories.servicos_repo import obter_servico_por_id


def tramitar_servico(servico_id, novo_status_id, usuario_nome="Analista Fechamento", usuario_email="analista@cosampa.com.br"):
    """
    Tramita o status do serviço aplicando rigorosamente:
    - Imutabilidade do Status 14 (🔒)
    - Trava RN-03 (bloqueio por pendências ativas)
    - CDU V5 Bloco 4: Validação Obrigatória do Sistema de Origem
    - CDU V5 Bloco 4: Bypass do Fluxo Comercial (Salto 01 -> 08)
    - CDU V5 Bloco 5: Validação da Tela 04 (08 -> 09) e Tela 05 (09 -> 10)
    - CDU V5 Bloco 5: Justificativa Técnica (11 -> 12) e Custódia Nominal (12 -> 13)
    - Logs de Auditoria (RN-01) e Registro Global de Ações
    """
    try:
        with get_db_cursor() as cursor:
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
            return {
                "status": "bloqueado", 
                "mensagem": f"Serviço {servico_id}: Bloqueado! Existem pendências ativas que impedem o avanço direto para validação/faturamento (RN-03)."
            }

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
            with get_db_cursor() as cursor:
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
            with get_db_cursor(commit=True) as cursor:
                cursor.execute("UPDATE servicos SET responsavel_disputa = %s WHERE id = %s", (usuario_nome, servico_id))

        # CDU V5 - Bloco 4: Bypass do Fluxo Comercial (Salto de Status 01 -> 08)
        is_comercial = ("COMERCIAL" in contrato) or ("COMERCIAL" in tp_servico) or ("COMERCIAL" in tp_obra)
        bypass_aplicado = False
        if status_atual == 1 and novo_status_id == 3 and is_comercial:
            novo_status_id = 8
            bypass_aplicado = True

        # Executa a atualização com marcação de updated_at para a ordenação mais recente
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE servicos SET status_id = %s, updated_at = NOW() WHERE id = %s", (novo_status_id, servico_id))

        # RN-01: Log de Auditoria
        registrar_log_auditoria(servico_id, usuario_nome, usuario_email, "status_id", status_atual, novo_status_id)

        # Se houve Bypass Comercial, registra no histórico / timeline
        if bypass_aplicado:
            try:
                inserir_comentario(
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
        print(f"[Erro Tramitação Service] {e}")
        return {"status": "erro", "mensagem": str(e)}


def atualizar_dados_servico(servico_id, dados, usuario_nome="Analista", usuario_email="analista@cosampa.com.br"):
    """
    Atualiza campos específicos de um serviço e gera log de auditoria (RN-01).
    """
    try:
        old_row = obter_servico_por_id(servico_id)
        if not old_row:
            return {"status": "erro", "mensagem": "Serviço não encontrado"}

        updates = []
        params = []
        logs_gerados = []

        for k, v in dados.items():
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

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, tuple(params))

        for campo, val_ant, val_novo in logs_gerados:
            registrar_log_auditoria(servico_id, usuario_nome, usuario_email, campo, val_ant, val_novo)
            desc_tech = {"campo": campo, "de": str(val_ant), "para": str(val_novo)}
            desc_human = f"{usuario_nome} atualizou '{campo}' de '{val_ant}' para '{val_novo}' no serviço {servico_id}."
            registrar_acao_global(usuario_nome, usuario_email, "EDICAO_DADOS", servico_id, desc_tech, desc_human)

        return {"status": "sucesso"}
    except Exception as e:
        print(f"[Erro Atualização Dados Service] {e}")
        return {"status": "erro", "mensagem": str(e)}
