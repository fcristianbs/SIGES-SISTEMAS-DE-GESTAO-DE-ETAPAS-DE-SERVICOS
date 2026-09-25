import sys
import os
import pymysql
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from db import get_db_connection, tramitar_servico_db, atualizar_dados_servico_db, gerar_snapshot_conciliacao_db, buscar_snapshot_conciliacao_db, fechar_evento_conciliacao_db, obter_comparador_bilateral_db, salvar_comparador_bilateral_db

def testar_bloco_5():
    print("================================================================================")
    print("INICIANDO SUITE DE TESTES AUTOMATIZADOS - BLOCO 5 (CDU V5)")
    print("================================================================================")
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    conn.autocommit(True)
    
    # 0. Preparação de SOBs de teste no banco
    sob_fat_08 = "SOB-TEST-FAT-08"
    sob_con_09 = "SOB-TEST-CON-09"
    sob_evt_10a = "SOB-TEST-EVT-10A"
    sob_evt_10b = "SOB-TEST-EVT-10B"
    
    sobs = [sob_fat_08, sob_con_09, sob_evt_10a, sob_evt_10b]
    
    for s in sobs:
        cursor.execute("DELETE FROM conciliacao_snapshots WHERE servico_id = %s", (s,))
        cursor.execute("DELETE FROM comentarios_internos WHERE servico_id = %s", (s,))
        cursor.execute("DELETE FROM baremo_itens WHERE servico_id = %s", (s,))
        cursor.execute("DELETE FROM logs_auditoria WHERE servico_id = %s", (s,))
        cursor.execute("DELETE FROM servicos WHERE id = %s", (s,))
    
    # Inserir SOB 08
    cursor.execute("""
        INSERT INTO servicos (id, num_servico, status_id, valor, data_validacao, mes_emissao, cliente, contrato, origem_sistema)
        VALUES (%s, '99908', 8, 1500.00, NULL, NULL, 'ENEL DISTRIBUICAO', 'CT-2026-ENEL', 'Eorder')
    """, (sob_fat_08,))
    
    # Inserir SOB 09
    cursor.execute("""
        INSERT INTO servicos (id, num_servico, status_id, valor, data_validacao, mes_emissao, cliente, contrato, origem_sistema)
        VALUES (%s, '99909', 9, 2200.00, '2026-09-25 10:00:00', NULL, 'ENEL DISTRIBUICAO', 'CT-2026-ENEL', 'Eorder')
    """, (sob_con_09,))
    
    # Inserir SOB 10A (Será 100% batida)
    cursor.execute("""
        INSERT INTO servicos (id, num_servico, status_id, valor, data_validacao, mes_emissao, cliente, contrato, origem_sistema)
        VALUES (%s, '99910A', 10, 3000.00, '2026-09-25 10:00:00', '09/2026', 'ENEL DISTRIBUICAO', 'CT-2026-ENEL', 'Eorder')
    """, (sob_evt_10a,))
    
    # Inserir SOB 10B (Terá divergência/corte)
    cursor.execute("""
        INSERT INTO servicos (id, num_servico, status_id, valor, data_validacao, mes_emissao, cliente, contrato, origem_sistema)
        VALUES (%s, '99910B', 10, 4500.00, '2026-09-25 10:00:00', '09/2026', 'ENEL DISTRIBUICAO', 'CT-2026-ENEL', 'Eorder')
    """, (sob_evt_10b,))
    
    # Inserir itens de baremo para SOB 10B
    cursor.execute("""
        INSERT INTO baremo_itens (servico_id, codigo_item, descricao, quantidade, valor_medido)
        VALUES 
        (%s, 'BAR-001', 'Substituição de Poste DT 11/600', 1, 3000.00),
        (%s, 'BAR-002', 'Lançamento de Cabo Multiplexado 70mm', 150, 1500.00)
    """, (sob_evt_10b, sob_evt_10b))
    
    conn.commit()
    print("-> Setup inicial de dados de teste concluído com sucesso.")

    # -------------------------------------------------------------------------
    # TESTE 1: Validação de Faturamento (Status 08 -> 09)
    # -------------------------------------------------------------------------
    print("\n--- TESTE 1: Validação de Faturamento (Status 08 -> 09) ---")
    
    # Tentativa de avanço direto sem data_validacao (deve ser rejeitado)
    res_bloq = tramitar_servico_db(sob_fat_08, 9, "Analista Faturamento")
    assert res_bloq.get("status") in ("bloqueado", "erro"), "FALHA: Deveria bloquear avanço 08->09 sem data_validacao"
    print("  [OK] Bloqueio verificado: avanço sem data_validacao foi recusado com:", res_bloq.get("mensagem"))

    # Atribuir data_validacao e tramitar
    atualizar_dados_servico_db(sob_fat_08, {"data_validacao": "2026-09-25 14:00:00"}, "Analista Faturamento")
    res_ok = tramitar_servico_db(sob_fat_08, 9, "Analista Faturamento")
    assert res_ok.get("status") == "sucesso", f"FALHA ao tramitar 08->09 com data_validacao: {res_ok}"
    
    cursor.execute("SELECT status_id, data_validacao FROM servicos WHERE id = %s", (sob_fat_08,))
    row = cursor.fetchone()
    assert row["status_id"] == 9, "FALHA: Status_id deveria ser 9"
    assert row["data_validacao"] is not None, "FALHA: data_validacao não foi gravada"
    print("  [OK] Sucesso: 08 -> 09 liberado com data_validacao preenchida.")

    # -------------------------------------------------------------------------
    # TESTE 2: Mês de Emissão obrigatório (Status 09 -> 10)
    # -------------------------------------------------------------------------
    print("\n--- TESTE 2: Mês de Emissão obrigatório (Status 09 -> 10) ---")
    
    # Tentativa sem mes_emissao
    res_bloq2 = tramitar_servico_db(sob_con_09, 10, "Analista Faturamento")
    assert res_bloq2.get("status") in ("bloqueado", "erro"), "FALHA: Deveria bloquear avanço 09->10 sem mes_emissao"
    print("  [OK] Bloqueio verificado: avanço sem mes_emissao foi recusado com:", res_bloq2.get("mensagem"))

    # Atribuir mes_emissao e tramitar
    atualizar_dados_servico_db(sob_con_09, {"mes_emissao": "09/2026"}, "Analista Faturamento")
    res_ok2 = tramitar_servico_db(sob_con_09, 10, "Analista Faturamento")
    assert res_ok2.get("status") == "sucesso", f"FALHA ao tramitar 09->10 com mes_emissao: {res_ok2}"
    
    cursor.execute("SELECT status_id, mes_emissao FROM servicos WHERE id = %s", (sob_con_09,))
    row = cursor.fetchone()
    assert row["status_id"] == 10, "FALHA: Status_id deveria ser 10"
    assert row["mes_emissao"] == "09/2026", "FALHA: mes_emissao incorreto"
    print("  [OK] Sucesso: 09 -> 10 liberado com mes_emissao '09/2026'.")

    # -------------------------------------------------------------------------
    # TESTE 3: Snapshot Pré-Importação ('Relatório ANTES' - Evento de Conciliação)
    # -------------------------------------------------------------------------
    print("\n--- TESTE 3: Snapshot Pré-Importação ('Relatório ANTES') ---")
    evt_id = "EVT-TESTE-20260925"
    res_snap = gerar_snapshot_conciliacao_db([sob_evt_10a, sob_evt_10b], evt_id)
    assert res_snap.get("status") == "sucesso", f"FALHA ao gerar snapshot: {res_snap}"
    assert res_snap.get("total_snapshots") == 2, "FALHA: Quantidade de snapshots gerados incorreta"
    
    lista_snap = buscar_snapshot_conciliacao_db(evt_id)
    assert len(lista_snap) == 2, f"FALHA: Deveria retornar 2 snapshots, retornou {len(lista_snap)}"
    print(f"  [OK] Snapshot gerado e consultado com sucesso para {len(lista_snap)} serviços no evento '{evt_id}'.")

    # -------------------------------------------------------------------------
    # TESTE 4: Fechamento Transacional de Evento de Conciliação
    # -------------------------------------------------------------------------
    print("\n--- TESTE 4: Fechamento Automático do Evento de Conciliação ---")
    # SOB 10A: Faturado = 3000.00, Pago = 3000.00 (100% batido -> Status 14)
    # SOB 10B: Faturado = 4500.00, Pago = 3800.00 (Glosado 700.00 -> Status 11)
    itens_pgto = [
        {"id": sob_evt_10a, "num_servico": "99910A", "valor_pago": 3000.00},
        {"id": sob_evt_10b, "num_servico": "99910B", "valor_pago": 3800.00}
    ]
    
    res_fechamento = fechar_evento_conciliacao_db(evt_id, itens_pgto, "Analista Fechamento", "analista@cosampa.com.br")
    assert res_fechamento.get("status") == "sucesso", f"FALHA no fechamento do evento: {res_fechamento}"
    assert res_fechamento.get("finalizados") == 1, "FALHA: Deveria ter 1 finalizado (Status 14)"
    assert res_fechamento.get("divergentes") == 1, "FALHA: Deveria ter 1 divergente (Status 11)"
    
    cursor.execute("SELECT status_id, valor_pago_cliente, divergencia_conciliacao FROM servicos WHERE id = %s", (sob_evt_10a,))
    row_10a = cursor.fetchone()
    assert row_10a["status_id"] == 14, f"FALHA: SOB 10A deveria estar no status 14, mas está em {row_10a['status_id']}"
    assert float(row_10a["valor_pago_cliente"]) == 3000.00, "FALHA: valor_pago_cliente incorreto"
    print("  [OK] SOB 10A (100% batido): Direcionada com sucesso para Status 14 (FATURADO TOTAL)!")
    
    cursor.execute("SELECT status_id, valor_pago_cliente, divergencia_conciliacao FROM servicos WHERE id = %s", (sob_evt_10b,))
    row_10b = cursor.fetchone()
    assert row_10b["status_id"] == 11, f"FALHA: SOB 10B deveria estar no status 11, mas está em {row_10b['status_id']}"
    assert float(row_10b["valor_pago_cliente"]) == 3800.00, "FALHA: valor_pago_cliente incorreto"
    assert "700.00" in row_10b["divergencia_conciliacao"], "FALHA: divergencia_conciliacao não registrada corretamente"
    cursor.execute("SELECT texto FROM comentarios_internos WHERE servico_id = %s", (sob_evt_10b,))
    coments = cursor.fetchall()
    assert any("Conciliação Automática" in c["texto"] for c in coments), "FALHA: Notificação automática na timeline não encontrada"
    print("  [OK] SOB 10B (Glosado R$ 700): Direcionada com sucesso para Status 11 com notificação na Timeline!")

    # -------------------------------------------------------------------------
    # TESTE 5: Comparador Dinâmico Bilateral (Status 11)
    # -------------------------------------------------------------------------
    print("\n--- TESTE 5: Comparador Dinâmico Bilateral (Status 11) ---")
    comp_dados = obter_comparador_bilateral_db(sob_evt_10b)
    assert comp_dados.get("status") == "sucesso", f"FALHA ao obter comparador bilateral: {comp_dados}"
    assert len(comp_dados.get("itens", [])) == 2, "FALHA: Deveria retornar os 2 itens de baremo"
    print(f"  [OK] Comparador Bilateral retornou {len(comp_dados['itens'])} itens com colunas de divergência.")

    # Tentativa de avanço 11 -> 12 sem justificativa (deve bloquear)
    res_bloq11 = tramitar_servico_db(sob_evt_10b, 12, "Analista Fechamento")
    assert res_bloq11.get("status") in ("bloqueado", "erro"), "FALHA: Deveria bloquear 11->12 sem justificativa na Timeline"
    print("  [OK] Bloqueio verificado: avanço sem justificativa foi recusado com:", res_bloq11.get("mensagem"))

    # Tramitação com Justificativa e Link do SharePoint
    res_tram12 = salvar_comparador_bilateral_db(
        servico_id=sob_evt_10b,
        novo_status_id=12,
        justificativa="Glosada medição de cabo pela distribuidora. Evidências anexadas no SharePoint.",
        sharepoint_url="https://cosampa.sharepoint.com/sites/obras/99910B_evidencias.pdf",
        usuario_nome="Analista Fechamento",
        usuario_email="analista@cosampa.com.br"
    )
    assert res_tram12.get("status") == "sucesso", f"FALHA ao tramitar para 12: {res_tram12}"
    
    cursor.execute("SELECT status_id, sharepoint_url FROM servicos WHERE id = %s", (sob_evt_10b,))
    row_12 = cursor.fetchone()
    assert row_12["status_id"] == 12, "FALHA: Status_id deveria ser 12"
    assert "sharepoint.com" in row_12["sharepoint_url"], "FALHA: SharePoint URL não foi gravada"
    print("  [OK] Sucesso: 11 -> 12 tramitado com Justificativa na Timeline e Link SharePoint.")

    # -------------------------------------------------------------------------
    # TESTE 6: Cobrar Cliente e Disputa Contratual (Status 12 -> 13)
    # -------------------------------------------------------------------------
    print("\n--- TESTE 6: Cobrar Cliente e Disputa Contratual (Status 12 -> 13) ---")
    
    # Tentativa sem mes_reapresentacao (deve bloquear)
    res_bloq12 = tramitar_servico_db(sob_evt_10b, 13, "Analista Fechamento")
    assert res_bloq12.get("status") in ("bloqueado", "erro"), "FALHA: Deveria bloquear 12->13 sem mes_reapresentacao"
    print("  [OK] Bloqueio verificado: avanço sem mes_reapresentacao foi recusado com:", res_bloq12.get("mensagem"))

    # Tramitar com mes_reapresentacao
    res_tram13 = salvar_comparador_bilateral_db(
        servico_id=sob_evt_10b,
        novo_status_id=13,
        mes_reapresentacao="11/2026",
        usuario_nome="Gestor Contratual Cosampa",
        usuario_email="gestor@cosampa.com.br"
    )
    assert res_tram13.get("status") == "sucesso", f"FALHA ao tramitar para 13: {res_tram13}"
    
    cursor.execute("SELECT status_id, mes_reapresentacao, responsavel_disputa FROM servicos WHERE id = %s", (sob_evt_10b,))
    row_13 = cursor.fetchone()
    assert row_13["status_id"] == 13, "FALHA: Status_id deveria ser 13"
    assert row_13["mes_reapresentacao"] == "11/2026", "FALHA: mes_reapresentacao incorreto"
    assert row_13["responsavel_disputa"] == "Gestor Contratual Cosampa", "FALHA: responsavel_disputa não atribuído"
    print("  [OK] Sucesso: 12 -> 13 tramitado com Mês de Reapresentação (11/2026) e Responsável pela Disputa.")

    # -------------------------------------------------------------------------
    # TESTE 7: Imutabilidade do Status 14 (FATURADO TOTAL - FINALIZADO)
    # -------------------------------------------------------------------------
    print("\n--- TESTE 7: Imutabilidade do Status 14 ---")
    res_imutavel = tramitar_servico_db(sob_evt_10a, 8, "Analista Faturamento")
    assert res_imutavel.get("status") in ("bloqueado", "erro"), "FALHA: Status 14 deveria ser imutável contra tramitação"
    assert ("protegido" in res_imutavel.get("mensagem").lower() or "bloqueado" in res_imutavel.get("mensagem").lower()), "FALHA: Mensagem de bloqueio do status 14 não exibida"
    print("  [OK] Imutabilidade do Status 14 garantida: serviço bloqueado e protegido contra alterações.")

    # Limpeza
    for s in sobs:
        cursor.execute("DELETE FROM conciliacao_snapshots WHERE servico_id = %s", (s,))
        cursor.execute("DELETE FROM comentarios_internos WHERE servico_id = %s", (s,))
        cursor.execute("DELETE FROM baremo_itens WHERE servico_id = %s", (s,))
        cursor.execute("DELETE FROM logs_auditoria WHERE servico_id = %s", (s,))
        cursor.execute("DELETE FROM servicos WHERE id = %s", (s,))
    conn.commit()
    conn.close()

    print("\n================================================================================")
    print("TODOS OS 7 TESTES AUTOMATIZADOS DO BLOCO 5 PASSARAM COM 100% DE SUCESSO!")
    print("================================================================================")

if __name__ == "__main__":
    testar_bloco_5()
