from datetime import datetime
from backend.app.database.connection import get_db_cursor
from backend.app.database.repositories.conciliacao_repo import (
    inserir_snapshot_servico,
    buscar_itens_baremo
)
from backend.app.database.repositories.auditoria_repo import (
    registrar_log_auditoria,
    inserir_comentario
)
from backend.app.database.repositories.servicos_repo import obter_servico_por_id
from backend.app.services.tramitacao_service import tramitar_servico


def gerar_snapshot_conciliacao(servico_ids, evento_id=None):
    """
    CDU V5 - Tela 05 (Item 2 - Status 10):
    Gera um snapshot imutável ("Relatório ANTES") do estado dos serviços 
    antes da conciliação/importação da planilha de pagamentos.
    """
    if not evento_id:
        evento_id = f"EVT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    try:
        total_gravados = 0
        for sid in servico_ids:
            srv = obter_servico_por_id(sid)
            if not srv:
                continue

            st_ant = srv.get("status_id") or 9
            v_fat = srv.get("valor") or 0.0
            v_pago_ant = srv.get("valor_pago_cliente") or 0.0

            inserir_snapshot_servico(
                evento_id=evento_id,
                servico_id=sid,
                status_id_anterior=st_ant,
                valor_faturado=v_fat,
                valor_pago_anterior=v_pago_ant,
                dados_servico_dict=srv
            )
            total_gravados += 1

        return {"status": "sucesso", "evento_id": evento_id, "total_snapshots": total_gravados}
    except Exception as e:
        print(f"[Erro Snapshot Conciliação] {e}")
        return {"status": "erro", "mensagem": str(e)}


def fechar_evento_conciliacao(evento_id, itens_pagamento, usuario_nome="Analista Fechamento", usuario_email="analista@cosampa.com.br"):
    """
    CDU V5 - Tela 05 (Item 2 - Status 10):
    Executa o fechamento do evento de conciliação:
    - Se o valor pago bater 100% com o valor executado: avança para 14 (FATURADO TOTAL - FINALIZADO) e bloqueia.
    - Se houver divergência de valor: avança para 11 (CONCILIADO COM DIVERGENCIAS),
      calcula DIVERGÊNCIA DA CONCILIAÇÃO e grava ocorrência na Timeline.
    """
    finalizados = 0
    divergentes = 0
    detalhes = []

    try:
        # Primeiro, gera o snapshot de segurança caso ainda não exista para o evento
        sids = [it.get("id") or it.get("num_servico") for it in itens_pagamento if it.get("id") or it.get("num_servico")]
        gerar_snapshot_conciliacao(sids, evento_id)

        for item in itens_pagamento:
            sid = item.get("id") or item.get("num_servico")
            v_pago = float(item.get("valor_pago") or 0.0)

            with get_db_cursor() as cursor:
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
                with get_db_cursor(commit=True) as cursor:
                    cursor.execute("""
                        UPDATE servicos 
                        SET status_id = %s, valor_pago_cliente = %s, divergencia_conciliacao = %s, updated_at = NOW() 
                        WHERE id = %s
                    """, (novo_st, v_pago, div_str, real_id))

                inserir_comentario(
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
                with get_db_cursor(commit=True) as cursor:
                    cursor.execute("""
                        UPDATE servicos 
                        SET status_id = %s, valor_pago_cliente = %s, divergencia_conciliacao = %s, updated_at = NOW() 
                        WHERE id = %s
                    """, (novo_st, v_pago, div_str, real_id))

                inserir_comentario(
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


def obter_comparador_bilateral(servico_id):
    """
    CDU V5 - Tela 01 (Item 2 - Status 11):
    Retorna os dados do Comparador Dinâmico Bilateral:
    Atividade Executada (Valor Realizado) vs. Atividade Paga (Valor Pago).
    """
    try:
        srv = obter_servico_por_id(servico_id)
        if not srv:
            return {"status": "erro", "mensagem": "Serviço não encontrado"}

        itens = buscar_itens_baremo(servico_id)

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


def salvar_comparador_bilateral(servico_id, novo_status_id, justificativa="", mes_reapresentacao="", sharepoint_url="", usuario_nome="Analista Fechamento", usuario_email="analista@cosampa.com.br"):
    """
    CDU V5 - Tela 01 (Status 11 -> 12 -> 13):
    Salva a tratativa do Comparador Bilateral, injeta a justificativa na Timeline
    e tramita o serviço.
    """
    try:
        with get_db_cursor(commit=True) as cursor:
            # 1. Se informou novo sharepoint_url, atualiza
            if sharepoint_url:
                cursor.execute("UPDATE servicos SET sharepoint_url = %s WHERE id = %s", (sharepoint_url, servico_id))
            
            # 2. Se informou mes_reapresentacao, atualiza
            if mes_reapresentacao:
                cursor.execute("UPDATE servicos SET mes_reapresentacao = %s WHERE id = %s", (mes_reapresentacao, servico_id))
                registrar_log_auditoria(servico_id, usuario_nome, usuario_email, "mes_reapresentacao", "", mes_reapresentacao)

        # 3. Insere a justificativa na Timeline
        if justificativa and justificativa.strip():
            inserir_comentario(
                servico_id=servico_id,
                usuario_id=1,
                usuario_nome=usuario_nome,
                texto=f"⚖️ [Justificativa de Divergência - CDU V5]: {justificativa.strip()}"
            )

        # 4. Tramita o serviço
        return tramitar_servico(servico_id, novo_status_id, usuario_nome, usuario_email)
    except Exception as e:
        print(f"[Erro Salvar Comparador] {e}")
        return {"status": "erro", "mensagem": str(e)}
