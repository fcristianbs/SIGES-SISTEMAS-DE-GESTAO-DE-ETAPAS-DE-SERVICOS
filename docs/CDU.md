# Especificação de Casos de Uso (CDU) - SIGES
**Sistema de Gestão de Etapas de Serviços - Esteira GPM / Cosampa**

---

## 1. Introdução e Atores do Sistema

Este documento apresenta a especificação detalhada dos **Casos de Uso (CDU)** da plataforma **SIGES**, mapeando os requisitos funcionais descritos na especificação operacional para o padrão de engenharia de software de Casos de Uso. O sistema opera como uma grande esteira baseada em uma tabela centralizadora com exibição dinâmica e parametrizável de colunas por Tela e Status.

### 1.1 Atores do Sistema

| Ator | Descrição |
| :--- | :--- |
| **Analista de Fechamento** | Operador responsável pelo time de faturamento e medição. Realiza a conferência de medições, correção de divergências financeiras, exportações de dados e tratativa de serviços rejeitados pelo cliente que afetam o fechamento administrativo. |
| **Supervisor de Campo** | Responsável técnico pelas equipes operacionais em campo. Atua na correção de pendências físicas, de fotos, materiais, croquis e documentação técnica de campo. |
| **Coordenador Operacional** | Perfil de gerência técnica superior. Possui visualização consolidada e controle hierárquico sobre os Supervisores e Equipes de Campo sob sua tutela. |
| **Representante da Distribuidora / Cliente** | Ator externo ou interface interna do cliente responsável pela validação formal das medições enviadas pela Cosampa. |
| **Sistema GPM / Sistema de Origem** | Sistema externo integrado que fornece os inputs operacionais de campo (SOBs, fotos, materiais, dados de equipes) para a esteira do SIGES. |

---

## 2. Regras de Negócio Transversais (RNs)

As regras abaixo são aplicáveis de forma global e transversal a todos os Casos de Uso descritos neste documento:

*   **RN-01 (Log de Auditoria e Rastreabilidade):** Toda e qualquer alteração de dados efetuada na tabela ou em formulários anexos de uma SOB (incluindo alterações cadastrais, preenchimento de justificativas, anexos ou transições de status) deve registrar obrigatoriamente um registro em log contendo:
    *   Identificação única do usuário logado (nome e matrícula);
    *   Timestamp completo (data, hora, minuto e segundo);
    *   Identificação do campo alterado;
    *   Valor anterior e o Novo Valor gravado.
*   **RN-02 (Visualização Dinâmica de Colunas):** O sistema deve carregar automaticamente a *Estrutura Padrão da Tabela* (colunas básicas listadas no Dicionário de Dados) e injetar dinamicamente as colunas complementares requeridas de acordo com o Status e Tela selecionados pelo usuário.
*   **RN-03 (Bloqueio de Avanço por Pendências):** A existência de qualquer item de pendência técnica ou administrativa ativa (em aberto) atua como um travamento rígido no sistema. O SIGES deve **bloquear** o avanço do serviço para qualquer etapa de faturamento ou validação do cliente, forçando sua tramitação exclusiva dentro do fluxo de pendências até a resolução total.
*   **RN-04 (Retorno Automático de Pendências - Medição):** Quando um serviço está sob tratativa de pendências (Status 02, Status 06 ou Status 07) e possui itens de pendência parametrizados (como Fotos, Materiais, Documentação, etc.), no momento exato em que o Supervisor ou Analista marcar **100% dos itens como TRATADOS**, o sistema deve realizar a transição automatizada do status do serviço de volta para **01. Aguardando Conferência** (ou para **03. Aguardando Envio para Validação**, conforme regra específica da tela), sem a necessidade de intervenção manual do usuário.
*   **RN-05 (Filtro Hierárquico de Operação):** Nas telas e status de pendências operacionais, o sistema deve pré-aplicar um filtro de visualização respeitando a hierarquia funcional de campo:
    $$\text{Coordenador} \rightarrow \text{Supervisor} \rightarrow \text{Equipe} \rightarrow \text{Membros da Equipe}$$
    O Supervisor só visualiza pendências de suas equipes diretas. O usuário possui a prerrogativa de desativar voluntariamente o filtro para consultas de apoio entre pares.

---

## 3. Especificações de Casos de Uso (CDU)

### 3.1 TELA 01: MEDIÇÃO

#### CDU-01: Conferir e Tramitar Medição de Serviço
*   **ID:** CDU-01
*   **Ator Principal:** Analista de Fechamento
*   **Atores Secundários:** Sistema GPM (fornecedor de dados)
*   **Pré-condições:** 
    1. O serviço deve ter sido executado em campo e importado para a base do SIGES.
    2. O serviço deve estar no status **01. Aguardando Conferência**.
*   **Pós-condições:** O serviço é direcionado para a etapa de envio para validação ou entra em fluxo de pendências operacionais/comerciais.

##### Fluxo Principal (Tramitação Direta)
1. O Analista de Fechamento acessa a tela de **Medição** e seleciona um serviço no status **01. Aguardando Conferência**.
2. O sistema exibe a tabela centralizadora com as colunas padrão e estende dinamicamente para exibir as atividades de campo ("Vozes de Atividades"), materiais aplicados/retirados e hiperlinks diretos para consulta do Turno, Serviço e Obra no GPM.
3. O sistema exibe de forma agrupada na mesma tela os serviços considerados "irmãos" (mesma incidência/obra para fluxo emergencial; mesma incidência/cliente para fluxo comercial).
4. O Analista de Fechamento realiza a conferência das informações de campo.
5. O Analista de Fechamento realiza a **Confirmação Obrigatória** do campo "Sistema de Origem do Serviço" (ex: Eorder, Synergia, SacBt), corrigindo se necessário individualmente ou em lote.
6. O Analista seleciona a opção "Aprovar e Avançar Medição".
7. O sistema valida que não existem pendências em aberto (**RN-03**) para o registro.
8. O sistema realiza a transição de status do serviço:
    *   Para **03. Aguardando Envio para Validação** (em caso de Fluxo Emergencial);
    *   Para **Validado Aguardando Autorização de Faturamento** (em caso de Fluxo Comercial).
9. O sistema registra a transição no log de auditoria (**RN-01**).

##### Fluxo Alternativo A: Gerar Pendência Operacional Cosampa
6a. O Analista de Fechamento identifica divergências operacionais (problemas nas fotos de campo, materiais aplicados errados, falta de documentação).
7a. O Analista seleciona o botão **"Gerar Pendência Cosampa"**.
8a. O sistema abre a modal de formulário contendo a seção *Itens de Correção Cosampa* (Fotos, Materiais, Documentação/Croqui).
9a. O Analista marca as pendências identificadas (pelo menos uma) e preenche obrigatoriamente um campo descritivo de observação.
10a. O Analista confirma a geração de pendência.
11a. O sistema altera o status do serviço para **02. Pendências Operacionais Cosampa**, bloqueia o avanço para etapas de faturamento (**RN-03**) e registra a ação no log de auditoria (**RN-01**).

##### Fluxo Alternativo B: Gerar Pendência Cliente / Distribuidora
6b. O Analista de Fechamento identifica impasses de natureza contratual ou comercial que dependem de ação direta do cliente.
7b. O Analista seleciona o botão **"Gerar Pendência Distribuidora"**.
8b. O sistema abre o formulário de *Itens de Correção Distribuidora* (Vozes de atividades não cadastradas no contrato, serviço não despachado, ordem já faturada).
9b. O Analista seleciona o item aplicável e confirma.
10b. O sistema altera o status do serviço para **04. Pendências Distribuidora** e registra a ação no log de auditoria (**RN-01**).

*Nota: Em caso de coexistência de pendências Cosampa e Distribuidora geradas concomitantemente, o sistema aplicará prioridade estrita de ordenação e roteamento ao fluxo de Pendência Cosampa.*

---

#### CDU-02: Consolidar e Enviar para Validação do Cliente
*   **ID:** CDU-02
*   **Ator Principal:** Analista de Fechamento
*   **Pré-condições:** O serviço deve estar localizado no status **03. Aguardando Envio para Validação**.
*   **Pós-condições:** O serviço é direcionado para aprovação do cliente externo no status **05. Aguardando Validação do Cliente**.

##### Fluxo Principal
1. O Analista de Fechamento acessa a tela de **Medição** e filtra pelos serviços em lote no status **03. Aguardando Envio para Validação**.
2. O sistema exibe a lista de medições validadas pelo time interno de fechamento prontas para inserção nos sistemas de faturamento da Distribuidora.
3. O Analista seleciona um ou múltiplos serviços na tabela através dos checkboxes de seleção.
4. O Analista preenche os campos obrigatórios da transição:
    *   **Sistema de Faturamento** (campo de múltipla escolha parametrizável via tabela auxiliar);
    *   **Mês de Medição Inicial** (campo de texto ou calendário formatado como MM/AAAA).
5. O Analista de Fechamento confirma o envio em lote.
6. O sistema valida o preenchimento de todos os campos obrigatórios selecionados.
7. O sistema altera o status dos serviços selecionados para **05. Aguardando Validação do Cliente** e grava os logs de auditoria correspondentes (**RN-01**).

##### Fluxo Alternativo A: Exportação de Medições analisadas
3a. O Analista seleciona a ação de exportação de dados na tabela de lote.
4a. O sistema disponibiliza o download imediato das linhas selecionadas nos formatos unificados de planilha **XLSX** ou arquivo **CSV**.

---

#### CDU-03: Tratar Divergências Financeiras de Conciliação (Reanalisar)
*   **ID:** CDU-03
*   **Ator Principal:** Analista de Fechamento
*   **Pré-condições:** O faturamento do serviço foi processado pelo cliente e retornou com discrepâncias, posicionando o serviço no status **11. Conciliado com Divergências (Reanalisar)**.
*   **Pós-condições:** A divergência financeira é justificada e o serviço é reapresentado ou encaminhado para as etapas de pagamento complementar.

##### Fluxo Principal
1. O Analista de Fechamento seleciona a SOB no status **11. Conciliado com Divergências**.
2. O sistema reconfigura dinamicamente o layout visual della tabela para o modo de **Comparação Financeiro-Operacional**, destacando em blocos paralelos as informações de:
    *   Valores Pagos (Informados na planilha do cliente) *vs.* Valores Realizados (Apontados pela Cosampa).
3. O sistema apresenta um link direto parametrizável para o download ou visualização do arquivo de conciliação original hospedado no SharePoint.
4. O Analista de Fechamento analisa a divergência exibida no campo obrigatório pré-preenchido **Divergência da Conciliação**.
5. O Analista preenche o campo de justificativa técnica formal da reanálise.
6. O Analista decide pela tratativa financeira aplicável:
    *   **Encaminhar para Cobrança Complementar:** O Analista move o serviço para o status **12. Conciliado com Pagamento a Menor (Cobrar do Cliente)**. O sistema passa a exigir obrigatoriamente o preenchimento do campo *Mês de Reapresentação da Medição* e, após o preenchimento, migra o serviço para o status **13. Conciliado com Pagamento a Menor (Em Disputa)**, registrando o ID do usuário logado como o responsável ativo pelo pleito.
    *   **Encaminhar para Encerramento/Disputa Direta:** O Analista encaminha o serviço para as etapas de encerramento total ou parcial com base no desfecho da conciliação.
7. O sistema grava a tratativa e todas as alterações no histórico de auditoria (**RN-01**).

---

### 3.2 TELA 02: PENDÊNCIAS

#### CDU-04: Tratar Pendências Operacionais Cosampa (RN-04)
*   **ID:** CDU-04
*   **Ator Principal:** Supervisor de Campo
*   **Ator Secundário:** Coordenador Operacional
*   **Pré-condições:** O serviço deve estar no status **02. Pendências Operacionais Cosampa** ou **07. Rejeitado na Validação (Operação)**.
*   **Pós-condições:** A pendência de campo é sanada e o serviço retorna automaticamente à esteira de conferência técnica ou de faturamento.

##### Fluxo Principal (Tratativa de Campo)
1. O Supervisor de Campo acessa a tela de **Pendências**.
2. O sistema detecta o perfil do usuário logado e aplica automaticamente o **Filtro Hierárquico de Operação (RN-05)**, exibindo de forma exclusiva os serviços com pendências sob responsabilidade direta de suas equipes subordinadas.
3. O Supervisor seleciona um serviço listado e abre o painel expansivo de tratativas.
4. O sistema exibe o bloco *Itens de Correção Cosampa* contendo a lista parametrizável de erros gerados no CDU-01 ou CDU-06 (ex: Fotos sem evidência, erro de materiais, croqui incorreto).
5. O Supervisor de Campo realiza a tratativa física em campo e anexa as novas evidências requeridas clicando no botão **"+ Anexo"** do respectivo item com erro.
6. O Supervisor insere uma justificativa/explicação textual obrigatória sobre a correção executada no campo de observações do item correspondente.
7. O Supervisor marca o checkbox do respectivo item de correção indicando o status de **"TRATADO"**.
8. O Supervisor clica em "Salvar Tratativa".
9. O sistema verifica se todos os itens de correção vinculados ao serviço foram marcados como "TRATADOS" (**RN-04**).
10. Sendo verificado 100% de itens tratados, o sistema executa as seguintes ações automáticas:
    *   Transita o status do serviço de volta para **01. Aguardando Conferência** (se a origem era o status 02);
    *   Transita o status do serviço de volta para **03. Aguardando Envio para Validação** (se a origem era o status 07).
11. O sistema remove os bloqueios de avanço do registro (**RN-03**) e grava os históricos detalhados de auditoria das resoluções no log (**RN-01**).

##### Fluxo Alternativo A: Desativação do Filtro de Hierarquia
2a. O Supervisor ou Coordenador Operacional deseja consultar pendências de uma equipe parceira ou sob tutela de outro supervisor.
3a. O usuário clica na opção "Desativar Filtro Hierárquico".
4a. O sistema remove as restrições hierárquicas e disponibiliza todos os serviços da base para busca, respeitando os níveis gerais de segurança.

##### Fluxo Alternativo B: Necessidade de Reprogramação de Serviço
5b. O Supervisor de Campo identifica que a correção da pendência exige uma nova visita de campo/deslocamento que não pode ser realizada no dia atual.
6b. O Supervisor marca a opção **"Necessita Reprogramar"**.
7b. O sistema abre e torna obrigatório o preenchimento do campo **"Data da Programação"** (formato DD/MM/AAAA).
8b. O Supervisor define a nova data programada e salva o registro.
9b. O sistema altera a programação do serviço, mantendo-o no status de pendência, gera a atualização no log de auditoria (**RN-01**) e alerta o time de planejamento e controle.

---

#### CDU-05: Monitorar e Tratar Pendências de Distribuidora
*   **ID:** CDU-05
*   **Ator Principal:** Analista de Fechamento (como Responsável da Medição)
*   **Pré-condições:** O serviço deve estar associado ao status **04. Pendências Distribuidora**.
*   **Pós-condições:** O impasse comercial junto ao cliente é sanado e o registro é liberado para faturamento.

##### Fluxo Principal
1. O Analista de Fechamento acessa a tela de **Pendências** e filtra o painel de visualização dinâmica para o status **04. Pendências Distribuidora**.
2. O sistema exibe o bloco *Itens de Correção Distribuidora* associado à medição.
3. O Analista de Fechamento atua como o ponto de contato operacional e insere as informações de andamento da negociação junto à distribuidora.
4. O Analista atualiza o campo de status da tratativa da distribuidora (ex: "Em Negociação", "Aprovado Excepcionalmente", "Voz Cadastrada") no formulário específico de Itens de Correção.
5. Após formalização e aceite do item pendente por parte da distribuidora, o Analista marca o item de correção distribuidora como resolvido.
6. O sistema executa a alteração do status do serviço diretamente para **03. Aguardando Envio para Validação** e libera o registro das amarras de bloqueio de avanço (**RN-03**), registrando a auditoria (**RN-01**).

---

### 3.3 TELA 03: VALIDAÇÃO

#### CDU-06: Validar Medição Junto ao Cliente
*   **ID:** CDU-06
*   **Ator Principal:** Representante da Distribuidora / Cliente (ou Analista de Fechamento operando por procuração)
*   **Pré-condições:** O serviço deve estar localizado no status **05. Aguardando Validação do Cliente**.
*   **Pós-condições:** O serviço é validado para faturamento total ou retorna para tratamento de divergências técnicas na esteira operacional.

##### Fluxo Principal (Aprovação da Medição)
1. O usuário acessa a tela de **Validação** e seleciona serviços no status **05. Aguardando Validação do Cliente**.
2. O sistema abre o detalhamento da medição contendo os dados consolidados enviados e materiais aplicados.
3. O usuário seleciona a opção "Aprovar Medição".
4. O sistema abre o campo obrigatório **Data de 1ª Validação**, disponibilizando um botão de atalho rápido para autopreencher com a data/hora atual do servidor.
5. O usuário confirma a aprovação.
6. O sistema realiza a transição do status do serviço para **Validado Aguardando Autorização de Faturamento** e armazena os dados do aprovador e carimbo de tempo no log histórico de auditoria (**RN-01**).

##### Fluxo Alternativo A: Rejeição Manual de Medição
3a. O Representante do Cliente identifica inconformidades físicas ou de valores na medição.
4a. O usuário seleciona a opção "Rejeitar Medição".
5a. O sistema exibe uma caixa de diálogo dinâmica exigindo a classificação da rejeição.
6a. O usuário aponta os itens de correção necessários, preenchendo as seções de correção correspondentes:
    *   Se as inconsistências forem administrativas/financeiras do faturamento: o sistema direciona o serviço para o status **06. Rejeitado na Validação (Fechamento)**;
    *   Se as inconsistências forem operacionais de campo (fotos, materiais executados, croquis): o sistema direciona o serviço para o status **07. Rejeitado na Validação (Operação)**, voltando a aplicar as travas operacionais (**RN-03**).
7a. O sistema registra a rejeição e as razões apontadas no log de auditoria (**RN-01**).

##### Fluxo Alternativo B: Carga e Importação de Rejeição em Lote
3b. O Analista de Fechamento recebe do cliente uma planilha consolidando as rejeições de medição do período.
4b. O Analista acessa o portal de importação de dados da tela de validação e realiza o upload do arquivo Excel ou CSV.
5b. O sistema executa a leitura das linhas da planilha, validando as referências das SOBs.
6b. O sistema analisa a coluna de direcionamento de rejeição contida na planilha para roteamento automático:
    *   Se na planilha de carga em lote o destino da rejeição for omitido ou não parametrizado, o sistema aplica a **RN de Roteamento Padrão**: direciona o serviço automaticamente para o status **06. Rejeitado na Validação (Fechamento)**.
7b. O sistema atualiza em massa as SOBs impactadas e disponibiliza um relatório técnico detalhado contendo a quantidade de sucessos, erros de consistência de dados e os status finais de destino.

---

#### CDU-07: Tratar Rejeição de Validação pelo Fechamento
*   **ID:** CDU-07
*   **Ator Principal:** Analista de Fechamento
*   **Pré-condições:** O serviço deve estar localizado no status **06. Rejeitado na Validação (Fechamento)**.
*   **Pós-condições:** O serviço é corrigido administrativamente e avança de volta para a fila de envio no status **03. Aguardando Envio para Validação**.

##### Fluxo Principal
1. O Analista de Fechamento acessa a tela de **Medição** e filtra pelos serviços em status **06. Rejeitado na Validação (Fechamento)**.
2. O sistema apresenta em tela o formulário de dados cadastrais e as seções com os *Itens de Correção Cosampa* (Fotos, Materiais, Documentação/Croqui) apontados na rejeição.
3. O Analista de Fechamento realiza os ajustes administrativos ou financeiros necessários.
4. O Analista preenche a justificativa de correção e marca cada item resolvido como **"TRATADO"**.
5. O Analista seleciona o botão "Salvar e Reenviar".
6. O sistema valida que todos os itens de correção vinculados ao serviço foram resolvidos (**RN-04**).
7. O sistema realiza a transição do status para **03. Aguardando Envio para Validação**, remove os bloqueios (**RN-03**) e grava a ação no log de auditoria (**RN-01**).

---

## 4. Dicionário de Dados do Protótipo (Mapeamento de Entrada / GPM)

Os campos abaixo são mapeados a partir da integração com a base do GPM e devem ser integrados ao banco de dados e expostos de forma parametrizada na tabela centralizadora:

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `contrato` | Texto | Departamento ou contrato de cadastro da atividade | "ST-2023-01" |
| `origem_sistema` | Lista | Formato de geração do Serviço no GPM (PDA, Obras, Manual, Planilha) | "PDA" |
| `num_servico` | Alfanumérico | Código identificador único do serviço no GPM | "10928374" |
| `incidencia` | Alfanumérico | Ordem de atendimento em caso de ausência de número de obra | "INC-9982" |
| `tipo_servico` | Texto | Conceito do tipo da atividade executada | "Manutenção Preventiva" |
| `situacao_servico` | Texto | Status atual da ordem de serviço no GPM | "Executado" |
| `id_cliente` | Alfanumérico | Código numérico identificador do Cliente na Distribuidora | "7654321" |
| `cliente` | Texto | Nome completo do Cliente | "João da Silva" |
| `solicitante` | Texto | Nome ou identificação da entidade solicitante do serviço | "Maria Oliveira" |
| `bairro` | Texto | Bairro do local da execução do serviço | "Centro" |
| `localidade` | Texto | Município onde o serviço foi executado | "São Paulo" |
| `endereco` | Texto | Endereço completo do local do serviço | "Av. Paulista, 1000" |
| `cod_pep_obra` | Alfanumérico | Número da Obra associada (Número da Ordem se preenchido) | "PEP-0012938" |
| `tipo_retorno` | Texto | Descrição alfabética do grupo macro de possíveis retornos de campo | "Executado com Sucesso" |
| `retorno_campo` | Alfanumérico | Código Alfanumérico do serviço executado | "RET-01" |
| `grupo_retorno` | Texto | Descrição alfabética do Grupo macro de possíveis retornos | "Concluído" |
| `inicio_desloc` | DateTime | Data e Hora do Início do Deslocamento | "2023-10-25 08:00:00" |
| `fim_desloc` | DateTime | Data e Hora do Fim do Deslocamento | "2023-10-25 08:30:00" |
| `inicio_exec` | DateTime | Data e Hora do Início da Execução | "2023-10-25 08:31:00" |
| `fim_exec` | DateTime | Data e Hora do Fim da Execução | "2023-10-25 10:00:00" |
| `cod_turno` | Alfanumérico | Código do turno registrado no GPM | "TURNO-A1" |
| `placa_veiculo` | Texto | Placa do Veículo utilizado na execução | "ABC-1234" |
| `modelo_veiculo` | Texto | Modelo do Veículo utilizado | "Ford Ka" |
| `centro_servico` | Texto | Unidade Organizacional (Centro de Serviço responsável) | "CS-SUL" |
| `coordenador` | Texto | Líder do Centro de Serviço e dos Supervisores | "Carlos Eduardo" |
| `supervisor` | Texto | Líder direto das equipes de campo | "Roberto Santos" |
| `equipe` | Texto | Identificador da equipe de campo | "EQP-12" |
| `membros_equipe` | Texto | Colaboradores que compõem a equipe no serviço | "Pedro; Ana; Marcos" |
| `obs_servico` | Texto | Observações registradas pela equipe em campo | "Substituição realizada" |
| `latitude_servico`| Decimal | Ponto de Latitude da execução | "-23.550520" |
| `longitude_servico`| Decimal | Ponto de Longitude da execução | "-46.633308" |
| `dta_exec_srv` | Date | Data de realização da atividade | "2023-10-25" |
| `total_servicos` | Monetário | Valor total dos serviços executados | 1500.00 |
| `tipo_equipe` | Texto | Categorização do perfil da equipe | "Linha Viva" |
| `tipo_obra` | Texto | Categorização das Obras pelo seu Tipo | "Expansão de Rede" |
| `tdc` | Alfanumérico | Código do serviço no sistema da Distribuidora (análogo ao `num_servico`) | "TDC-88392" |
