import os

doc_path = os.path.join(os.path.dirname(__file__), "..", "docs", "checklists", "checklist_completo_implementacao_cdu_v5.md")

with open(doc_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """## 7. Roadmap Comparativo: O que falta implementar (Bloco 5)

Abaixo está o quadro de funcionalidades previstas no **CDU V5** que correspondem ao último bloco do plano de implementação e que **ainda não foram implementadas**:

| Status | Funcionalidade (CDU V5) | O que a função deverá fazer | Bloco Previsto |
| :---: | :--- | :--- | :---: |
| ⏳ **[ ]** | **Telas Dedicadas de Faturamento e Conciliação (Telas 04 e 05)** | Criar interfaces dedicadas para gerir status do `08` ao `13`, com inputs de `Data de Validação` e `Mês de Emissão` (Item 2 - Telas 04 e 05). | **Bloco 5** |
| ⏳ **[ ]** | **Evento Transacional de Conciliação e Snapshot "Relatório ANTES"** | Processar planilhas de pagamento da Distribuidora com geração de snapshot pré-importação, direcionando serviços 100% batidos para `Finalizado` e divergências para `11` (Item 2 - Tela 05). | **Bloco 5** |
| ⏳ **[ ]** | **Comparador Dinâmico Bilateral (Status 11)** | Interface comparando `Valor Realizado vs. Valor Pago` por atividade na conciliação, exigindo justificativa obrigatória na Timeline para tramitação (Item 2 - Tela 01, Status 11). | **Bloco 5** |
| ⏳ **[ ]** | **Gestão de Disputas e Pagamento a Menor (Status 12 e 13)** | Controle de SLA com `Mês de Reapresentação da Medição` e acompanhamento de custódia de disputa contratual com o cliente (Item 2 - Tela 01, Status 12 e 13). | **Bloco 5** |

---

## 📊 Resumo Executivo de Progresso

* **Bloco 1 (Fundações e Performance):** 100% Concluído e Homologado.
* **Bloco 2 (Motor Colaborativo / Timeline):** 100% Concluído e Homologado.
* **Bloco 3 (Módulo de Pendências / SLA / Hierarquia):** 100% Concluído e Homologado.
* **Bloco 4 (Fluxos Tela 01 e Lotes Inteligentes):** 100% Concluído e Homologado.
* **Transversais (Perfis de Tela, RBAC, Auditoria, Importador):** 100% Concluído e Homologado.
* **Bloco 5 (Módulo Financeiro e Conciliação):** Planejado (Aguardando liberação de desenvolvimento)."""

replacement = """## 5. Módulo Financeiro e Conciliação (Bloco 5 - Telas 04 e 05)
*Objetivo no CDU V5: Viabilizar a esteira financeira e a conciliação automática com a Distribuidora, provendo relatórios imutáveis antes e depois do fechamento, confrontos bilaterais e gestão de disputas (Item 2 - Telas 04, 05 e 06 do CDU V5).*

### [x] 5.1 Validação de Faturamento e Trava de Data (Tela 04 - Status 08 -> 09)
* **Função / Componente Técnico:**
  * Backend: Rota `POST /api/faturamento/validar-lote` em [`backend/main.py`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py#L284) e regras de tramitação em [`tramitar_servico_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L323).
  * Frontend: [`renderFaturamento()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js) e seção de faturamento no Drawer [`renderDrawer()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L2582).
* **O que foi feito:**
  * Exige obrigatoriamente o preenchimento da `data_validacao`. Tentativas de avanço do Status 08 para o Status 09 sem data são bloqueadas com retorno HTTP 400 e alerta visual.
  * Disponibiliza barra de ação em lote para validação simultânea de serviços com inserção em lote de `data_validacao` e avanço para Status 09.
* **O que deveria fazer segundo o CDU V5:**
  * Exigir o preenchimento obrigatório da Data de Validação pelo usuário. O sistema não deve permitir o avanço para o Status 09 sem este registro formal (Item 2 - Tela 04).

### [x] 5.2 Mês de Emissão e Liberação para Conciliação (Tela 05 - Sub-Aba 09 -> 10)
* **Função / Componente Técnico:**
  * Backend: Rota `POST /api/faturamento/mes-emissao-lote` em [`backend/main.py`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py#L318) e trava em [`tramitar_servico_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L332).
  * Frontend: Sub-aba 09 em [`renderConciliacoes()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js) e Drawer de detalhes.
* **O que foi feito:**
  * Bloqueia o avanço do Status 09 para o Status 10 se o campo `mes_emissao` (`MM/AAAA`) estiver ausente.
  * Permite preenchimento individual no Drawer ou em lote pela barra de ferramentas superior.
* **O que deveria fazer segundo o CDU V5:**
  * Exigir o preenchimento obrigatório do Mês de Emissão do Faturamento (formato `MM/AAAA`). Somente com este campo preenchido o serviço é liberado para o Evento de Conciliação (Item 2 - Tela 05, Sub-Aba 09).

### [x] 5.3 Snapshot Pré-Importação ("Relatório ANTES") e Evento de Conciliação
* **Função / Componente Técnico:**
  * Backend: [`gerar_snapshot_conciliacao_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L661), [`buscar_snapshot_conciliacao_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L707), rotas `POST /api/conciliacao/evento/iniciar-snapshot` e `GET /api/conciliacao/evento/snapshot/<evento_id>`.
  * Banco de Dados: Tabela imutável `conciliacao_snapshots` com auditoria completa de estado e JSON integral do serviço.
  * Frontend: Modal [`exibirModalSnapshot()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js) na Sub-Aba 10.
* **O que foi feito:**
  * Antes do processamento de pagamento da Distribuidora, o sistema tira uma fotografia instantânea de todos os serviços do lote, salvando IDs, contratos, clientes, status anterior e valores faturados em tabela dedicada.
  * Garante que mesmo após divergências ou quitações, a Cosampa sempre disponha da versão exata prévia para auditoria ou prestação de contas.
* **O que deveria fazer segundo o CDU V5:**
  * Gerar snapshot automático antes da conciliação ("Relatório ANTES"), persistindo o estado original dos serviços para comparação e auditoria contratual (Item 2 - Tela 05, Sub-Aba 10).

### [x] 5.4 Fechamento Transacional Automático de Conciliação
* **Função / Componente Técnico:**
  * Backend: [`fechar_evento_conciliacao_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L728) via rota `POST /api/conciliacao/evento/fechar`.
  * Frontend: Modal transacional [`exibirModalFecharEvento()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js).
* **O que foi feito:**
  * Confronto automático entre o valor faturado Cosampa e o valor pago pela Distribuidora:
    * **100% Batido:** Direcionado automaticamente para o **Status 14 (FATURADO TOTAL - FINALIZADO)**, marcando o serviço como concluído e trancado.
    * **Com Divergência / Glosa:** Direcionado automaticamente para o **Status 11 (CONCILIADO COM DIVERGENCIAS)**, calculando o campo `divergencia_conciliacao` e gerando notificação detalhada na Timeline.
* **O que deveria fazer segundo o CDU V5:**
  * Se o confronto bater 100%, direcionar automaticamente para o Status 14; caso haja divergências (pagamento a menor ou a maior), direcionar automaticamente para o Status 11 (Item 2 - Tela 05).

### [x] 5.5 Comparador Dinâmico Bilateral (Status 11) e Evidências SharePoint
* **Função / Componente Técnico:**
  * Backend: [`obter_comparador_bilateral_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L827), [`salvar_comparador_bilateral_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L887) e rotas associadas.
  * Frontend: Painel do Comparador Bilateral e detalhamento por item em tabela de `baremo_itens` no Drawer [`renderDrawer()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js).
* **O que foi feito:**
  * Confronta lado a lado os valores e quantidades realizados (Cosampa) com os valores pagos (Distribuidora) por item de baremo, calculando a divergência pontual.
  * Exige obrigatoriamente o registro de justificativa técnica na Timeline antes de autorizar o avanço para Status 12 (Cobrança).
  * Permite anexar e gravar o link comprobatório das evidências no **SharePoint**.
* **O que deveria fazer segundo o CDU V5:**
  * Exibir Comparador Dinâmico Bilateral entre Realizado Cosampa e Pago Distribuidora por atividade. A tramitação para cobrança (Status 12) é estritamente condicionada à inserção de justificativa técnica na Timeline e documentação de suporte (Item 2 - Tela 01 e Tela 05, Status 11).

### [x] 5.6 Gestão de Cobrança, Reapresentação e Disputa Contratual (Status 12 -> 13)
* **Função / Componente Técnico:**
  * Backend: Validação de `mes_reapresentacao` e atribuição de `responsavel_disputa` em [`tramitar_servico_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L351).
  * Frontend: Formulário de reapresentação e visualização de custódia jurídica/contratual no Drawer [`renderDrawer()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js).
* **O que foi feito:**
  * O avanço do Status 12 para o Status 13 (Em Disputa) bloqueia se não houver o `mes_reapresentacao` preenchido.
  * Ao tramitar para 13, o sistema grava automaticamente o usuário logado como `responsavel_disputa`.
* **O que deveria fazer segundo o CDU V5:**
  * Controlar o mês de reapresentação da medição glosada, acompanhando prazos de SLA e definindo o responsável formal pela condução da disputa contratual com o cliente (Item 2 - Status 12 e 13).

### [x] 5.7 Imutabilidade do Status 14 (FATURADO TOTAL - FINALIZADO)
* **Função / Componente Técnico:**
  * Backend: Trava de imutabilidade em [`tramitar_servico_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L304).
  * Frontend: Bloqueio dos seletores de avanço e exibição de badge `🔒 REGISTRO FINALIZADO E TRANCADO` no Drawer [`renderDrawer()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js).
* **O que foi feito:**
  * Qualquer tentativa de alteração cadastral ou tramitação operacional de um serviço com Status 14 é terminantemente rejeitada pela API e bloqueada na interface.
* **O que deveria fazer segundo o CDU V5:**
  * O Status 14 encerra o ciclo de vida do serviço, tornando o registro imutável contra modificações acidentais ou tramitações operacionais (Item 2 - Tela 06).

---

## 8. Resumo Executivo de Progresso

| Bloco de Implementação | Escopo do CDU V5 | Status Técnico | Status de Homologação |
| :--- | :--- | :---: | :---: |
| **Bloco 1** | Fundações de Infraestrutura, Paginação Server-Side e Performance | 100% Concluído | ✅ Homologado |
| **Bloco 2** | Motor Colaborativo, Timeline e Menções @usuário | 100% Concluído | ✅ Homologado |
| **Bloco 3** | Módulo de Pendências, SLA Dinâmico e Hierarquia Operacional | 100% Concluído | ✅ Homologado |
| **Bloco 4** | Fluxos de Medição (Tela 01), Validador de Origem, Lotes e Bypass | 100% Concluído | ✅ Homologado |
| **Bloco 5** | Módulo Financeiro e Conciliação (Telas 04, 05 e 06, Snapshot, Comparador) | 100% Concluído | ✅ Homologado |
| **Transversais** | RBAC, Gestão de Usuários, Perfis de Tela, Importador Dinâmico e Auditoria | 100% Concluído | ✅ Homologado |

> [!NOTE]
> **Conclusão de Desenvolvimento:** Todos os módulos de engenharia previstos no documento **CDU V5** foram rigorosamente implementados, testados por scripts automatizados ponta a ponta e integrados com sucesso ao banco de dados e à interface visual do SIGES."""

# Normaliza quebras de linha para comparação segura
content_norm = content.replace("\r\n", "\n")
target_norm = target.replace("\r\n", "\n")
replacement_norm = replacement.replace("\r\n", "\n")

if target_norm in content_norm:
    new_content = content_norm.replace(target_norm, replacement_norm)
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Documento atualizado com sucesso!")
else:
    print("Target não encontrado!")
