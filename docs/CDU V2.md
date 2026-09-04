# PROTOTIPO INICIAL DA ESTEIRA

## 1. Visão Geral e Arquitetura da Solução

O sistema foi concebido como uma grande esteira operacional baseada em uma estrutura de tabela dinâmica centralizada. Nem todas as colunas são exibidas automaticamente de forma global; a visualização é composta por uma **Estrutura Padrão de Colunas Básicas** somada às colunas específicas exigidas por cada **Tela Agregadora** e seus respectivos **Status (Etapas)**.

A progressão dos serviços ao longo da esteira segue uma cronologia orientada aos status, onde as telas atuam como agregadores visuais para perfis de acesso específicos (Operação, Fechamento e Validação).

### 1.0 Regras Universais da Plataforma

*   **Auditoria Global (Log Integrado):** Qualquer alteração realizada no sistema, em qualquer campo (incluindo mudanças de status, inclusão de anexos, justificativas ou edições de dados), **deve obrigatoriamente gerar um registro imutável de Log de Auditoria**, contendo data, hora, usuário responsável e o valor anterior/novo.
*   **Gestão de Pendências em Aberto:** A existência de uma pendência em aberto não gera um registro separado rastreável fora da esteira. O próprio serviço em si, enquanto possuir qualquer pendência pendente de resolução, fica bloqueado pelo sistema, permitindo **exclusivamente o remanejamento para uma etapa/status de pendência** correspondente até sua integral quitação.

---

### 1.1 Estrutura Padrão da Tabela (Colunas Básicas)

A visualização base da esteira estrutura a rastreabilidade operacional estabelecendo um vínculo direto e hierárquico entre a gestão, a liderança e as equipes de campo:

*   **Vínculo Estrutural de Liderança e Equipes:**
    *   **Centro de Serviço (`centro_servico`):** Unidade organizacional mãe.
    *   **Coordenador (`Coordenador`):** Vinculado ao Centro de Serviço, atua como líder dos Supervisores.
    *   **Supervisor (`Supervisor`):** Vinculado ao Coordenador, atua como líder direto das equipes de campo.
    *   **Equipe (`equipe`):** Agregador operacional chave vinculado diretamente ao Supervisor.
    *   **Membros da Equipe (`membros_equipe`):** Colaboradores alocados na equipe (Encarregados, Eletricistas, Motoristas).
*   **Campos de Identificação Rápida da Tabela Padrão:**
    *   `num_servico` / `tdc`
    *   `situacao_servico`
    *   `Cliente`
    *   `tipo_servico`
    *   `dta_exec_srv`

---

### 1.2 Mapeamento Completo de Dados (Input / Integração GPM)

Abaixo está o detalhamento dos campos de input inicial provenientes da base auxiliar e integração com o sistema GPM:

| Nome do Campo | Descrição | Exemplo (se aplicável) |
| :--- | :--- | :--- |
| `contrato` | Departamento de cadastro da atividade | `CT-2023-COSAMPA` |
| `origem_sistema` | Formato de geração do Serviço no GPM (Criado no PDA, Obras, Pré-Despacho Manual ou Planilha de Importação) | `PDA` |
| `num_servico` | Código do serviço no sistema GPM | `SRV-987654` |
| `Incidência` | Ordem de atendimento caso não haja número de obra associado | `INC-2023-4521` |
| `tipo_servico` | Conceito de tipo da atividade executada (base auxiliar principal) | `Manutenção Preventiva BT` |
| `situacao_servico` | Status atual do serviço no GPM | `Executado` |
| `Id Cliente` | Código numérico identificador do Cliente no sistema da Distribuidora | `7845120` |
| `Cliente` | Nome completo do Cliente | `João da Silva` |
| `Solicitante` | Nome do solicitante do serviço | `Maria Oliveira` |
| `Bairro` | Bairro onde o serviço foi realizado | `Centro` |
| `Localidade` | Município do serviço | `Belém` |
| `endereco` | Endereço completo do local do serviço | `Av. Presidente Vargas, 100` |
| `cod_pep_obra` | Número da Obra associada ao serviço (será também o número da Ordem caso preenchido) | `PEP-BR-2023-089` |
| `tipo_retorno` | Descrição alfabética do Grupo macro de possíveis retornos de campo | `Concluído com Sucesso` |
| `Retorno de Campo` | Código Alfanumérico do serviço executado | `RET-001` |
| `Grupo Retorno de Campo` | Descrição alfabética do Grupo macro de retornos de campo | `Execução Comercial` |
| `inicio_desloc` | Início do Deslocamento (Data e Hora) | `2023-10-25 08:00:00` |
| `fim_desloc` | Fim do Deslocamento (Data e Hora) | `2023-10-25 08:30:00` |
| `inicio_exec` | Início da Execução (Data e Hora) | `2023-10-25 08:35:00` |
| `fim_exec` | Fim da Execução (Data e Hora) | `2023-10-25 10:00:00` |
| `cod_turno` | Código do turno de trabalho no GPM | `TRN-01` |
| `placa_veiculo` | Placa do Veículo utilizado | `ABC-1234` |
| `modelo_veiculo` | Modelo do Veículo utilizado | `Toyota Hilux` |
| `centro_servico` | Unidade de Organização / Centro de serviço responsável pela equipe | `CS-BELÉM` |
| `Coordenador` | Líder do Centro de Serviço (Gestor dos Supervisores) | `Carlos Eduardo` |
| `Supervisor` | Líder direto de equipes de campo | `Roberto Souza` |
| `equipe` | Equipe de campo (Agregador principal de pessoas) | `EQP-TURMA-A` |
| `membros_equipe` | Colaboradores membros da equipe naquele serviço específico | `Marcos (Encarregado), Pedro (Eletricista)` |
| `obs_servico` | Observações escritas pela equipe na execução da atividade | `Substituição de ramal concluída sem anomalias.` |
| `latitude_servico` | Ponto de Latitude (Geolocalização) | `-1.455833` |
| `longitude_servico` | Ponto de Longitude (Geolocalização) | `-48.490833` |
| `dta_exec_srv` | Data de execução do serviço | `2023-10-25` |
| `total_servicos` | Valor total dos serviços executados | `R$ 450,00` |
| `tipo_equipe` | Categorização das equipes pelo seu tipo | `Linha Viva` |
| `tipo_obra` | Categorização das Obras pelo seu Tipo | `Ampliação de Rede` |
| `tdc` | Código do serviço no sistema da Distribuidora (análogo ao `num_servico`) | `TDC-889977` |

---

## 2. Estrutura das Telas e Fluxo dos Status (Cronologia da Esteira)

---

### TELA 01: MEDIÇÃO
*Perfil Principal: Time de Fechamento / Análise Financeira*

#### `01.` AGUARDANDO CONFERENCIA
*   **Conceito:** Landing page dos serviços executados originados do sistema legado GPM.
*   **Visualização & Recursos:**
    *   Exibição dos dados básicos, vozes de atividades apontadas, materiais aplicados e materiais retirados.
    *   Links diretos para abertura do Turno, Serviço e Obra (se aplicável) no GPM.
    *   Listagem automatizada de "Serviços Irmãos":
        *   *Fluxo Emergencial:* Serviços com a mesma incidência e/ou mesma obra.
        *   *Fluxo Comercial:* Serviços com a mesma incidência e/ou mesmo cliente.
*   **Ações e Regras de Transição:**
    *   **Geração de Pendências:**
        *   *Botão "Gerar Pendência Cosampa":* Abre a seção "Itens de Correção Cosampa" (checkboxes + observação). Envia o serviço para o status `02. PENDENCIAS OPERACIONAIS COSAMPA`.
        *   *Botão "Gerar Pendência Distribuidora":* Abre a seção "Itens de Correção Distribuidora". Envia o serviço para `04. PENDENCIAS DISTRIBUIDORA`.
        *   *Regra de Sobreposição:* Se ambas forem geradas, a **Pendência Cosampa tem prioridade de direcionamento sobre a Pendência Distribuidora**. Permite ação individual ou em lote.
    *   **Aprovação / Avanço:**
        *   Validação obrigatória do campo **"Sistema de Origem do Serviço"** (ex: Eorder/Synergia para Comercial; Eorder/SacBt para Emergencial) individualmente ou em lote.
        *   Serviços sem pendência avançam para `03. AGUARDANDO ENVIO PARA VALIDACAO` (Fluxo Emergencial) ou `VALIDADO AGUARDANDO AUTORIZAÇÃO DE FATURAMENTO` (Fluxo Comercial).

#### `03.` AGUARDANDO ENVIO PARA VALIDACAO
*   **Conceito:** Depositório de serviços analisados pelo time de Fechamento que aguardam exportação/inserção no sistema de Faturamento da Distribuidora.
*   **Recursos:** Suporte à extração de dados nos formatos XLSX e CSV (separado por vírgulas).
*   **Campos Obrigatórios para Transição (`05. AGUARDANDO VALIDACAO DO CLIENTE`):**
    1.  *Sistema de Faturamento* (Múltipla escolha, parametrizável em tabela auxiliar).
    2.  *Mês de Medição Inicial* (Formato: `MM/AAAA`).

#### `06.` REJEITADO NA VALIDACAO (FECHAMENTO)
*   **Conceito:** Serviços rejeitados pelo cliente cujas correções cabem ao time de Fechamento.
*   **Ações:** Visualização da seção "Itens de Correção Cosampa" para tratativas e ajustes das inconsistências apontadas.
*   **Retorno:** Após o tratamento de todos os itens, o serviço retorna para `03. AGUARDANDO ENVIO PARA VALIDACAO`.

#### `11.` CONCILIADO COM DIVERGENCIAS (REANALISAR)
*   **Conceito:** Serviços faturados e conciliados que retornaram com divergências entre a Medição executada e a paga.
*   **Visualização & Interface Ajustada:**
    *   Exibição do campo `DIVERGÊNCIA DA CONCILIAÇÃO` (originado da análise de conciliação).
    *   O layout de exibição das Atividades é modificado para apresentar comparativamente o **Serviço Executado vs. Serviço/Valor Pago**.
    *   Link direto de acesso à planilha padronizada original armazenada no SharePoint.
*   **Ação Obrigatória:** O responsável deve preencher uma justificativa detalhada esclarecendo a causa do problema antes de permitir a transição de status.

#### `12.` CONCILIADO COM PAGAMENTO A MENOR (COBRAR DO CLIENTE)
*   **Conceito:** Proveniente da reanálise de divergências (`11`), quando identificado que uma cobrança complementar deve ser enviada ao cliente.
*   **Campos Obrigatórios:** Preenchimento do campo `Mês de Reapresentação da Medição` para controle do tempo de processamento.
*   **Transição:** Ao reapresentar, migra para `13. CONCILIADO COM PAGAMENTO A MENOR (EM DISPUTA)`, registrando o usuário logado como responsável pelo acompanhamento.

#### `13.` CONCILIADO COM PAGAMENTO A MENOR (EM DISPUTA)
*   **Conceito:** Custódia de serviços aguardando o complemento do pagamento por parte do cliente.
*   **Saída:** Liberado para transição para as etapas de Finalização conforme o desfecho da disputa.

---

### TELA 02: PENDÊNCIAS
*Perfil Principal: Operação de Campo (Supervisores, Coordenadores)*

#### Visibilidade Hierárquica Padrão da Tela de Pendências
Usuários acessam a tela com um **filtro pré-aplicado por sua árvore hierárquica**:
$$\text{Coordenador} \longrightarrow \text{Supervisores subordinados} \longrightarrow \text{Equipes de campo}$$
*Nota: O usuário possui a prerrogativa de desfiltrar a visão para consultar pendências pertencentes a seus pares.*

#### `02.` PENDENCIAS OPERACIONAIS COSAMPA
*   **Conceito:** Recebe serviços rejeitados pelo time de Fechamento que exigem correção da Operação.
*   **Campos Chave & Ações:**
    *   Seção **"Itens de Correção Cosampa"**: Exibição dos botões de pendência acionados. Cada botão abre um campo de texto para explicação do supervisor e um campo para upload de anexos.
    *   Campo Marcável **"Necessita Reprogramar"**: Ao ser marcado, exige a inserção da **Data de Programação**.
    *   Exibição das datas do serviço e da data de entrada neste status.
*   **Retorno:** Sanadas todas as pendências, o serviço retorna automaticamente para `01. AGUARDANDO CONFERENCIA`.

#### `04.` PENDENCIAS DISTRIBUIDORA
*   **Conceito:** Serviços bloqueados por impedimentos de responsabilidade exclusiva da Distribuidora (Cliente).
*   **Campos Chave & Exigências:**
    *   Seção **"Itens de Correção Distribuidora"** (Obrigatória): O Responsável pela Medição deve registrar e atualizar o status do retorno/resposta do cliente.
*   **Retorno:** Sanadas as pendências, o serviço retorna para `03. AGUARDANDO ENVIO PARA VALIDACAO`.

#### `07.` REJEITADO NA VALIDACAO (OPERACAO)
*   **Conceito:** Serviços rejeitados na validação do cliente que exigem correção da equipe de Operação.
*   **Funcionamento:** Idêntico ao status `02`, exigindo tratativa na seção "Itens de Correção", justificativa do supervisor e anexos.
*   **Retorno:** Tratadas todas as pendências, o serviço avança para `03. AGUARDANDO ENVIO PARA VALIDACAO`.

---

### TELA 03: VALIDAÇÃO
*Perfil Principal: Gestão de Validação e Interface com Cliente*

#### `05.` AGUARDANDO VALIDACAO DO CLIENTE
*   **Conceito:** Serviços submetidos ao aceite do cliente.
*   **Fluxo de Aprovação:**
    *   Em caso de **Validação**: Avança para `VALIDADO AGUARDANDO AUTORIZACAO DE FATURAMENTO` acompanhado da inserção da **Data da 1ª Validação** (disponibilizar atalho/botão "Inserir Data de Hoje").
*   **Fluxo de Rejeição:**
    *   Abre as seções "Item de Correção Cosampa" e "Item de Correção Distribuidora".
    *   O usuário direciona o serviço para `06. REJEITADO NA VALIDACAO (FECHAMENTO)` ou `07. REJEITADO NA VALIDACAO (OPERACAO)`.
*   **Processamento em Lote via Planilha:**
    *   Aceita importação de planilha padronizada de Validação.
    *   *Regra Fallback:* Caso a planilha de lote omita o destino final de rejeição, o sistema aplicará por padrão o status `06. REJEITADO NA VALIDACAO (FECHAMENTO)` para direcionamento prévio pela equipe de fechamento.

---

## 3. Parametrização das Tabelas Auxiliares de Pendências

Os modelos abaixo constituem a base parametrizável dos **Itens de Correção**, devendo permitir edição em lote e configurações independentes no módulo administrativo do sistema:

### 3.1 Molde: Itens de Correção Cosampa
1.  **Fotos:**
    *   Fotos de baixa qualidade
    *   Sem evidência do serviço
2.  **Materiais:**
    *   Materiais aplicados incorretamente
    *   Materiais retirados incorretamente
3.  **Documentação:**
    *   Sem Croqui anexado
    *   Croqui incorreto

### 3.2 Molde: Itens de Correção Distribuidora
1.  Vozes não cadastradas no Contrato
2.  Serviço não despachado para Cosampa
3.  Ordem já faturada

---

## 4. Resumo Matriz de Transição de Status

| Status de Origem | Condição / Ação | Status de Destino | Tela de Destino |
| :--- | :--- | :--- | :--- |
| **01. AGUARDANDO CONFERENCIA** | Gerar Pendência Cosampa | 02. PENDENCIAS OPERACIONAIS COSAMPA | 02. PENDENCIAS |
| **01. AGUARDANDO CONFERENCIA** | Gerar Pendência Distribuidora | 04. PENDENCIAS DISTRIBUIDORA | 02. PENDENCIAS |
| **01. AGUARDANDO CONFERENCIA** | Validação sem pendências (Emergencial) | 03. AGUARDANDO ENVIO PARA VALIDACAO | 01. MEDICAO |
| **02. PENDENCIAS OPERACIONAIS** | Resolver todas as pendências | 01. AGUARDANDO CONFERENCIA | 01. MEDICAO |
| **03. AGUARDANDO ENVIO VALIDACAO** | Informar Faturamento + Mês Inicial | 05. AGUARDANDO VALIDACAO DO CLIENTE | 03. VALIDAÇÃO |
| **04. PENDENCIAS DISTRIBUIDORA** | Resolver resposta Distribuidora | 03. AGUARDANDO ENVIO PARA VALIDACAO | 01. MEDICAO |
| **05. AGUARDANDO VALIDACAO CLIENTE** | Rejeição apontada (Operação) | 07. REJEITADO NA VALIDACAO (OPERACAO) | 02. PENDENCIAS |
| **05. AGUARDANDO VALIDACAO CLIENTE** | Rejeição apontada (Fechamento) | 06. REJEITADO NA VALIDACAO (FECHAMENTO) | 01. MEDICAO |
| **06. REJEITADO VALID (FECHAMENTO)**| Tratativa concluída | 03. AGUARDANDO ENVIO PARA VALIDACAO | 01. MEDICAO |
| **07. REJEITADO VALID (OPERACAO)**  | Tratativa concluída | 03. AGUARDANDO ENVIO PARA VALIDACAO | 01. MEDICAO |
| **11. CONCILIADO C/ DIVERGÊNCIA**   | Identificada cobrança ao cliente | 12. CONCILIADO C/ PAGTO MENOR (COBRAR) | 01. MEDICAO |
| **12. CONCILIADO PAGTO (COBRAR)**   | Preencher Mês Reapresentação | 13. CONCILIADO C/ PAGTO MENOR (DISPUTA)| 01. MEDICAO |