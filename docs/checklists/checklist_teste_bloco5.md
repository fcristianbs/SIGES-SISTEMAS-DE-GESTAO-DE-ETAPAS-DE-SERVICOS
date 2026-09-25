# Checklist de Validação: Bloco 5 (Módulo Financeiro e Conciliação - Telas 04 e 05)

Este checklist serve como registro formal de testes para homologar as entregas do **Bloco 5**, em conformidade integral com o caderno de especificações **CDU V5**. Realize os passos abaixo na interface web ou via testes integrados e marque as caixas após validar.

---

## 1. Teste de Validação de Faturamento (Tela 04 - Status 08 -> 09)
*Objetivo: Garantir que nenhum faturamento avance sem a conferência formal da data de validação.*

- [x] Acesse a tela de **Faturamento (Tela 04)**.
- [x] Selecione um ou mais serviços no **Status 08 (Validado — Aguard. Autorização)**.
- [x] Tente avançar o serviço sem informar a **Data de Validação**.
- [x] **Validação 1:** O sistema deve bloquear a tramitação com alerta explicativo (*"O preenchimento da Data de Validação é obrigatório para avançar para o Faturado/Conciliação"*).
- [x] Preencha o campo de Data de Validação (pelo botão "Hoje" ou calendário) e clique em **"Validar e Enviar p/ Conciliação (Status 09)"** (individual ou via barra de ação em lote).
- [x] **Validação 2:** O serviço deve ser tramitado com sucesso para o **Status 09 (Faturado — Aguard. Conciliação)** e a data de validação deve ser gravada no banco de dados.

---

## 2. Teste do Mês de Emissão do Faturamento (Tela 05 - Sub-Aba 09 -> 10)
*Objetivo: Assegurar a competência financeira antes de disponibilizar o serviço para o evento de conciliação.*

- [x] Acesse a tela de **Conciliações (Tela 05)** e entre na sub-aba **09. Aguardando Retorno**.
- [x] Selecione um serviço e abra o Drawer lateral ou utilize a barra de lote.
- [x] Tente tramitar para o **Status 10** sem informar o **Mês de Emissão**.
- [x] **Validação 1:** O sistema deve bloquear o avanço exigindo o formato `MM/AAAA`.
- [x] Informe o mês de competência (ex: `09/2026`) e clique em **"Definir Mês e Liberar p/ Conciliação"**.
- [x] **Validação 2:** O serviço deve avançar para o **Status 10 (Análise de Conciliação)**, ficando elegível para confronto no Evento de Conciliação.

---

## 3. Teste do Evento de Conciliação e Snapshot Pré-Importação ("Relatório ANTES" - Sub-Aba 10)
*Objetivo: Garantir rastreabilidade total e confronto automático com a planilha de pagamento da Distribuidora.*

- [x] Na tela de **Conciliações**, acesse a sub-aba **10. Evento de Conciliação**.
- [x] Observe os serviços aguardando fechamento transacional.
- [x] Clique no botão **"📸 Snapshot Pré-Importação (Relatório ANTES)"**.
- [x] **Validação 1:** O sistema deve abrir modal com o registro imutável do lote antes da importação, exibindo IDs, contratos, clientes, status anterior e valores faturados gravados na tabela `conciliacao_snapshots`.
- [x] Clique em **"⚡ Fechar Evento de Conciliação"**.
- [x] **Cenário A (100% Batido):** Processe confronto integral sem divergências.
  - **Validação 2:** Os serviços com valor pago igual ao faturado devem ser direcionados automaticamente para o **Status 14 (FATURADO TOTAL - FINALIZADO)** com registro de sucesso na Timeline.
- [x] **Cenário B (Com Divergência / Glosa):** Processe confronto onde o valor pago é inferior ao faturado.
  - **Validação 3:** Os serviços com corte devem ser direcionados automaticamente para o **Status 11 (Conciliado com Divergências)** com o cálculo da divergência persistido e notificação automática na Timeline.

---

## 4. Teste do Comparador Dinâmico Bilateral (Tela 05 - Sub-Aba 11 -> 12)
*Objetivo: Viabilizar a análise minuciosa entre Realizado Cosampa vs Pago Distribuidora com exigência de justificativa técnica e comprovação.*

- [x] Na tela de **Conciliações**, acesse a sub-aba **11. Divergências**.
- [x] Abra o Drawer de um serviço no **Status 11**.
- [x] **Validação 1:** O painel deve exibir o Comparador Dinâmico Bilateral com 3 cards destacados: **Realizado (Cosampa)**, **Pago (Distribuidora)** e **Divergência / Glosa**.
- [x] Clique no botão **"🔍 Ver Detalhamento por Item (Baremo)"**.
- [x] **Validação 2:** A tabela deve listar os itens individuais medidos confrontados com a quantidade e valor pago, apontando exatamente onde ocorreu a glosa.
- [x] Tente clicar em **"Cobrar Cliente (Ir p/ 12)"** sem preencher a Justificativa Técnica.
- [x] **Validação 3:** O sistema deve bloquear a ação exigindo justificativa técnica formal na Timeline.
- [x] Preencha a justificativa técnica, insira o link do documento comprobatório no **SharePoint** e clique em **"Cobrar Cliente"**.
- [x] **Validação 4:** O serviço deve avançar para o **Status 12 (Pgto a Menor — Cobrar Cliente)**, o link do SharePoint deve ser gravado e a justificativa deve constar na Timeline.

---

## 5. Teste de Cobrança e Início de Disputa Contratual (Tela 05 - Sub-Aba 12 -> 13)
*Objetivo: Controlar o ciclo de vida da reapresentação das glosas e atribuição de responsabilidade jurídica/contratual.*

- [x] Acesse a sub-aba de divergências filtrando pelo **Status 12**.
- [x] Abra o serviço e verifique o formulário **"Mês de Reapresentação & Disputa"**.
- [x] Tente avançar para o **Status 13** sem preencher o **Mês de Reapresentação**.
- [x] **Validação 1:** O sistema deve bloquear o avanço informando que a competência de reapresentação é obrigatória.
- [x] Preencha o Mês de Reapresentação (ex: `11/2026`) e clique em **"Iniciar Disputa Contratual (Avança p/ 13)"**.
- [x] **Validação 2:** O serviço deve avançar para o **Status 13 (Pgto a Menor — Em Disputa)**, registrando automaticamente o usuário logado como `responsavel_disputa`.
- [x] No Status 13, confirme a exibição clara do Responsável pela Disputa, Mês de Reapresentação e link direto para as evidências no SharePoint.

---

## 6. Teste de Imutabilidade do Status 14 (Tela 06 / Finalizados)
*Objetivo: Blindar serviços totalmente conciliados contra modificações indevidas.*

- [x] Acesse a tela ou sub-aba **14. Finalizados**.
- [x] Abra o Drawer de um serviço finalizado.
- [x] **Validação 1:** O Drawer deve exibir banner verde em destaque: **"🔒 REGISTRO FINALIZADO E TRANCADO (100% FATURADO)"**.
- [x] **Validação 2:** Os controles de tramitação manual devem ficar desabilitados/ocultos.
- [x] Tente tramitar o serviço via chamada direta de API ou comando operacional.
- [x] **Validação 3:** O backend deve rejeitar categoricamente qualquer tentativa de tramitação de um serviço no Status 14, retornando bloqueio por imutabilidade.
