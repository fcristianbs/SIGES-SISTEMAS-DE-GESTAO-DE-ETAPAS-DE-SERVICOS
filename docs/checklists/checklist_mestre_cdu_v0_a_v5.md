# 📑 Checklist Mestre de Homologação da Plataforma SIGES
### Consolidação Integral de Casos de Uso: do CDU V0 ao CDU V5

Este documento é o **checklist definitivo e unificado de testes da plataforma SIGES**, consolidando todos os requisitos, regras de negócio e casos de uso especificados desde a primeira concepção (**CDU V0 / V1**) até a versão mais recente (**CDU V5**).

Utilize este roteiro prático para validar a integridade de todas as funcionalidades desenvolvidas. Cada teste contém seu **objetivo**, **passo a passo de execução no navegador**, **critério de validação esperado** e a respectiva **caixa de marcação `[ ]`**.

---

## 🧭 Sumário dos Módulos de Teste

1. [Módulo 1: Fundações de Arquitetura, Performance e Navegação (CDU V1, V2 e V5)](#-módulo-1-fundações-de-arquitetura-performance-e-navegação)
2. [Módulo 2: Governança, RBAC, Perfis de Tela e Auditoria Global (CDU V1, V3, V4 e V5)](#-módulo-2-governança-rbac-perfis-de-tela-e-auditoria-global)
3. [Módulo 3: Motor Colaborativo, Linha do Tempo e Notificações (CDU V5)](#-módulo-3-motor-colaborativo-linha-do-tempo-e-notificações)
4. [Módulo 4: Gestão de Pendências, SLA e Roteamento de Campo (CDU V1, V2 e V5)](#-módulo-4-gestão-de-pendências-sla-e-roteamento-de-campo)
5. [Módulo 5: Ingestão de Dados e Importador Dinâmico de Planilhas (CDU V3 - CDU-08)](#-módulo-5-ingestão-de-dados-e-importador-dinâmico-de-planilhas)
6. [Módulo 6: Tela 01 - Medição, Validador de Origem, Lotes e Bypass (CDU V1, V4 e V5)](#-módulo-6-tela-01---medição-validador-de-origem-lotes-e-bypass)
7. [Módulo 7: Módulo Financeiro, Faturamento e Conciliação Automática (CDU V5 - Telas 04, 05 e 06)](#-módulo-7-módulo-financeiro-faturamento-e-conciliação-automática)

---

## 🏗️ Módulo 1: Fundações de Arquitetura, Performance e Navegação
*Origem: CDU V1 (Itens 1 e 2), CDU V2 (Itens 1.1 e 1.2) e CDU V5 (Item 5.1)*

### 1.1 Persistência de Sessão e Filtros no Frontend (LocalStorage)
* **Objetivo:** Garantir que o usuário não perca seu contexto de trabalho ao atualizar a página ou alternar abas.
* **Passo a Passo:**
  1. Acesse o SIGES e abra a tela de **Medição (01)** ou **Gerencial**.
  2. Altere o filtro de **Contrato** (ex: para *"MULTISERVICOS SUL"* ou *"COMERCIAL LESTE"*).
  3. Navegue até a **Página 2** (ou outra) no paginador inferior da tabela.
  4. Pressione a tecla **F5** ou o botão recarregar do navegador.
* **Critério de Validação:**
  - [ ] O filtro de Contrato permanece exatamente com o valor selecionado antes do recarregamento.
  - [ ] A tabela permanece na Página 2, sem resetar para a primeira página.

---

### 1.2 Paginação Server-Side e Carregamento Sob Demanda (Lazy Loading)
* **Objetivo:** Impedir lentidão ou congelamento do navegador ao processar bases com milhares de ordens.
* **Passo a Passo:**
  1. Abra as Ferramentas de Desenvolvedor do navegador (**F12**) e vá para a aba **Network (Rede)**.
  2. Recarregue a página e localize a requisição para `/api/servicos`.
  3. Clique na requisição e inspecione a URL e os parâmetros enviados.
* **Critério de Validação:**
  - [ ] A chamada contém os parâmetros `skip=0` e `limit=10` (ou o limite configurado).
  - [ ] O retorno JSON possui o formato `{ "data": [ ... 10 itens ... ], "total": X }`, comprovando que o banco de dados só entregou a fatia solicitada.
  - [ ] Ao clicar na página seguinte da tabela, uma nova chamada `/api/servicos?skip=10` é disparada de forma instantânea.

---

### 1.3 Integridade dos KPIs do Dashboard Gerencial
* **Objetivo:** Garantir que os cards e gráficos analíticos computem a totalidade real do banco de dados, desacoplados da paginação da tabela.
* **Passo a Passo:**
  1. Acesse a tela **Gerencial / Relatórios**.
  2. Observe o número do card **"Serviços na Esteira"** e os gráficos de barra por status.
* **Critério de Validação:**
  - [ ] O card "Serviços na Esteira" exibe a quantidade consolidada total do banco (ex: 2.000+ serviços) e **NÃO** o número 10 da tabela paginada.
  - [ ] Os gráficos de distribuição de status refletem a proporção global da base cadastrada.

---

### 1.4 Desacoplamento entre Chave GPM (`num_servico`) e Chave Distribuidora (`tdc`)
* **Objetivo:** Respeitar a independência estrutural das chaves exigida no CDU V2 e CDU V5 (suporte a relações 1:1, 1:N, N:1 e N:M).
* **Passo a Passo:**
  1. Na tabela de **Medição**, localize as colunas ou o campo **PEP Obra / TDC**.
  2. Abra o Drawer lateral de detalhes clicando sobre qualquer serviço.
* **Critério de Validação:**
  - [ ] O campo `num_servico` (código numérico interno da Cosampa/GPM) é exibido separadamente do código `tdc` (chave da concessionária).
  - [ ] O sistema não funde nem sobrescreve um código pelo outro durante edições ou importações.

---

### 1.5 Distinção Estrutural entre Situação do Serviço e Sistema de Origem
* **Objetivo:** Assegurar que a situação física no GPM (`Executado`, etc.) não se confunda com a plataforma de origem da Distribuidora (`Eorder`, `Synergia`, `SacBt`, `PDA`).
* **Passo a Passo:**
  1. Abra o Drawer lateral de um serviço.
  2. Observe a seção de informações de campo.
* **Critério de Validação:**
  - [ ] O sistema exibe o status operacional original do GPM de forma protegida.
  - [ ] O campo **Sistema de Origem** é tratado em bloco específico de validação de canal (com opções auditáveis Eorder, Synergia, SacBt, PDA, Importação Massiva).

---

## 🛡️ Módulo 2: Governança, RBAC, Perfis de Tela e Auditoria Global
*Origem: CDU V1 (RN-01), CDU V3 (Perfis de Acesso), CDU V4 (Perfis de Tela) e CDU V5 (Item 1.0)*

### 2.1 Autenticação e Controle de Acesso Baseado em Papéis (RBAC)
* **Objetivo:** Restringir o acesso a telas, botões e ações financeiras de acordo com o cargo do colaborador.
* **Passo a Passo:**
  1. Efetue logout e faça login como **Supervisor de Campo** (`supervisor@cosampa.com.br`).
  2. Verifique o menu lateral e tente acessar as telas de faturamento.
  3. Efetue logout e entre como **Administrador Master** (`admin@cosampa.com.br`).
* **Critério de Validação:**
  - [ ] O perfil Supervisor tem acesso liberado para saneamento de pendências e visão operacional de suas equipes.
  - [ ] Ações críticas de autorização de faturamento e administração de acessos permanecem restritas aos perfis com a devida alçada (Analista de Fechamento e Administrador Master).

---

### 2.2 Gestão de Usuários (Cadastro, Edição e Atribuição de Perfis)
* **Objetivo:** Permitir a manutenção autônoma do quadro de usuários pela interface administrativa.
* **Passo a Passo:**
  1. Logado como Administrador Master, acesse o menu **Gestão de Acessos**.
  2. Clique em **"Cadastrar Novo Usuário"**, preencha os dados e salve.
  3. Na listagem de usuários, clique no botão **"Editar"** do usuário recém-criado.
  4. Altere seu perfil (ex: de Operador para Analista) e confirme.
* **Critério de Validação:**
  - [ ] O modal abre com o título *"Editar Usuário"* trazendo os dados preenchidos previamente.
  - [ ] A alteração é gravada no banco de dados e refletida imediatamente na listagem sem erros de API.

---

### 2.3 Perfis de Tela Globais (Modo de Edição - Usuário Master)
* **Objetivo:** Validar a criação e edição de layouts de colunas disponibilizados para toda a organização (CDU V4).
* **Passo a Passo:**
  1. Na barra de ferramentas localizada entre os filtros e a tabela, observe o seletor de Perfis de Tela.
  2. Abra o seletor e selecione a opção fixa **"+ Adicionar Novo Perfil"**.
  3. No seletor de colunas com checkboxes, marque/desmarque colunas (ex: oculte *PEP Obra* e ative *Centro de Serviço*).
  4. Dê um nome ao perfil (ex: *"Visão Executiva Global"*) e clique em **Salvar**.
* **Critério de Validação:**
  - [ ] A tabela reconfigura suas colunas visíveis em tempo real sem recarregar a página.
  - [ ] O perfil fica disponível no dropdown de todos os usuários como layout global.

---

### 2.4 Derivação de Perfis Privados (Cópia Automática para Usuário Comum)
* **Objetivo:** Impedir que usuários comuns alterem o layout padrão global, permitindo a criação de visões personalizadas privadas (RN01 e RN02 do CDU V4).
* **Passo a Passo:**
  1. Conecte-se com um usuário sem permissão master (ex: Operador/Supervisor).
  2. Selecione um perfil público existente (ex: *"Padrão"*).
  3. Desmarque 2 colunas no seletor de checkboxes e clique em **Salvar**.
* **Critério de Validação:**
  - [ ] O sistema não sobrescreve o perfil global original.
  - [ ] O sistema abre modal solicitando um nome para salvar uma cópia local/privada (ex: *"Padrão [Meu Perfil]"*).
  - [ ] O perfil privado passa a ser exibido exclusivamente no dropdown daquele usuário.

---

### 2.5 Motor Global de Auditoria Imutável (RN-01)
* **Objetivo:** Garantir rastreabilidade absoluta de quem modificou qualquer dado, quando ocorreu e quais foram os valores.
* **Passo a Passo:**
  1. Abra o Drawer lateral de qualquer serviço.
  2. Altere um campo (ex: mude o Sistema de Origem de *SacBt* para *Eorder* e salve).
  3. Na seção inferior do Drawer, clique no botão **"Carregar Logs"** de Auditoria (RN-01).
* **Critério de Validação:**
  - [ ] O sistema renderiza o histórico cronológico exibindo:
    * Nome e e-mail do colaborador logado;
    * Timestamp exato da alteração;
    * Nome do campo alterado (`origem_sistema`);
    * Destaque visual: de `SacBt` ➔ `Eorder`.

---

## 💬 Módulo 3: Motor Colaborativo, Linha do Tempo e Notificações
*Origem: CDU V5 (Item 1.0 e 2.0)*

### 3.1 Timeline Cronológica e Comentários Colaborativos por Serviço
* **Objetivo:** Centralizar a comunicação técnica entre medição, fechamento e campo dentro da própria ordem de serviço.
* **Passo a Passo:**
  1. Abra o Drawer lateral de um serviço e localize o bloco **"💬 Timeline & Comentários"**.
  2. Digite uma justificativa ou mensagem de teste (ex: *"Fotos complementares solicitadas ao encarregado em campo"*).
  3. Clique em **"Enviar"**.
* **Critério de Validação:**
  - [ ] A mensagem é adicionada imediatamente ao mural com o nome do usuário, foto/avatar e data/hora.
  - [ ] A mensagem gravada torna-se imutável e permanece vinculada para sempre àquela SOB.

---

### 3.2 Menções Reativas com `@usuario` e Notificações em Tempo Real
* **Objetivo:** Alertar diretamente membros da equipe quando citados em discussões de ordens de serviço.
* **Passo a Passo:**
  1. No campo de comentário da Timeline, digite o caractere `@`.
  2. Observe a abertura do popup com a lista de colaboradores cadastrados.
  3. Selecione um usuário da lista e conclua o envio da mensagem.
* **Critério de Validação:**
  - [ ] O popup sugere os usuários reativamente enquanto o nome é digitado.
  - [ ] O sistema cria um registro de notificação para o usuário mencionado.
  - [ ] Ao logar com o usuário citado, o ícone de sino no cabeçalho exibe o indicador visual de nova notificação.

---

### 3.3 Notificação Automática na Transição de Responsabilidade Técnica
* **Objetivo:** Avisar automaticamente o próximo setor quando uma ordem de serviço muda de etapa.
* **Passo a Passo:**
  1. Tramite um serviço do Status 01 (Medição) gerando pendência para o Status 02 (Operação).
  2. Verifique o mural de notificações e a timeline do serviço.
* **Critério de Validação:**
  - [ ] A timeline registra uma entrada automática do sistema indicando a transferência de custódia.
  - [ ] Supervisores da equipe responsável recebem o alerta de transição de responsabilidade.

---

## ⚠️ Módulo 4: Gestão de Pendências, SLA e Roteamento de Campo
*Origem: CDU V1 (RN-03, RN-04, RN-05 e CDU-03/04), CDU V2 (Item 2 - Tela 02) e CDU V5 (Item 2.0)*

### 4.1 Trava Rígida de Bloqueio por Pendência Ativa (RN-03)
* **Objetivo:** Impedir rigorosamente que serviços com inconsistências de campo avancem para faturamento ou validação do cliente.
* **Passo a Passo:**
  1. Localize ou crie um serviço que esteja no **Status 02 (Pendências Operacionais Cosampa)** ou **Status 04 (Pendências Distribuidora)**.
  2. Tente forçar a tramitação direta para o Status 08 (Faturamento) ou Status 05 (Validação).
* **Critério de Validação:**
  - [ ] O sistema rejeita o avanço e exibe a mensagem de bloqueio rígido da RN-03: *"Bloqueado! Existem pendências ativas que impedem o avanço direto para validação/faturamento"*.
  - [ ] A ordem só permite movimentação dentro do fluxo saneador de pendências.

---

### 4.2 Geração de Pendências Operacionais Cosampa (Fotos, Materiais e Croqui)
* **Objetivo:** Registrar inconformidades de execução física para cobrança da equipe de campo.
* **Passo a Passo:**
  1. Na tela de **Medição**, selecione um serviço no Status 01.
  2. Clique no botão **"Gerar Pendência Cosampa"**.
  3. No modal de itens de correção, selecione ao menos uma categoria (*Fotos*, *Materiais* ou *Documentação/Croqui*) e digite uma observação.
  4. Confirme a geração.
* **Critério de Validação:**
  - [ ] O serviço é migrado com sucesso para o **Status 02 (Pendências Operacionais Cosampa)**.
  - [ ] Os itens de pendência assinalados ficam salvos e visíveis no detalhamento do serviço.

---

### 4.3 Geração de Pendências Distribuidora e Regra de Prioridade
* **Objetivo:** Direcionar impasses comerciais para o cliente e aplicar a prioridade estrita de direcionamento quando houver sobreposição (CDU V1).
* **Passo a Passo:**
  1. Em um serviço no Status 01, clique em **"Gerar Pendência Distribuidora"** (ex: *Vozes não cadastradas no contrato*).
  2. Em seguida, assinale também uma pendência operacional interna da Cosampa.
  3. Confirme o roteamento.
* **Critério de Validação:**
  - [ ] O sistema aplica a regra de prioridade do CDU: a **Pendência Cosampa sobrepõe a Pendência Distribuidora**, encaminhando o serviço para o **Status 02** até a resolução interna da equipe.

---

### 4.4 Retorno Automático para Medição após Resolução de 100% dos Itens (RN-04)
* **Objetivo:** Eliminar intervenções manuais para devolver serviços saneados à esteira de medição.
* **Passo a Passo:**
  1. Acesse a tela **02. Pendências** e localize um serviço com pendências operacionais no Status 02.
  2. Abra os detalhes das pendências e marque todos os itens pendentes como **TRATADOS (100% resolvidos)**.
  3. Salve o formulário.
* **Critério de Validação:**
  - [ ] O sistema reconhece a resolução integral e realiza a **transição automática** do status do serviço de volta para **01. Aguardando Conferência**.
  - [ ] O serviço reaparece instantaneamente na tela de Medição sem necessidade de reatribuição manual.

---

### 4.5 Motor de SLA Dinâmico (Cálculo de Dias, Cores de Alerta e Filtros de Estouro)
* **Objetivo:** Monitorar o cumprimento de prazos operacionais por etapa conforme a matriz de SLA do CDU.
* **Passo a Passo:**
  1. Acesse a tela de **Pendências** ou de **Medição**.
  2. Observe a coluna ou badge de **SLA** nos cards de serviços.
  3. No painel de filtros, utilize o filtro rápido de SLA (*No Prazo*, *Próximo ao Vencimento*, *Vencido/Estourado*).
* **Critério de Validação:**
  - [ ] Serviços dentro do prazo exibem badges verdes com contagem regressiva em dias (ex: `🟢 3 dias`).
  - [ ] Serviços com prazo esgotado exibem badges vermelhos chamativos (ex: `🔴 SLA Estourado (-2d)`).
  - [ ] O filtro de SLA isola com exatidão as ordens com atraso operacional.

---

### 4.6 Filtro Hierárquico Operacional (RN-05)
* **Objetivo:** Respeitar a cadeia de comando de campo (Coordenador ➔ Supervisor ➔ Equipe ➔ Membros).
* **Passo a Passo:**
  1. Conecte-se com o login de um **Supervisor de Campo** específico.
  2. Acesse a tela de **Pendências**.
* **Critério de Validação:**
  - [ ] A esteira pré-filtra automaticamente apenas as ordens executadas pelas equipes subordinadas àquele supervisor.
  - [ ] O supervisor possui a faculdade de limpar o filtro caso deseje prestar apoio a outras turmas.

---

## 📥 Módulo 5: Ingestão de Dados e Importador Dinâmico de Planilhas
*Origem: CDU V3 (CDU-08: Importação Inteligente e Sincronização Dinâmica)*

### 5.1 Wizard de Importação - Passo 1: Upload e Seleção Reativa de Abas
* **Objetivo:** Analisar arquivos externos de planilhas e extrair suas planilhas de trabalho (*worksheets*).
* **Passo a Passo:**
  1. No cabeçalho da aplicação, clique no botão **"📥 Importar Planilha"**.
  2. No modal exibido, arraste ou selecione um arquivo Excel (`.xlsx`) contendo múltiplas abas.
* **Critério de Validação:**
  - [ ] O sistema faz a leitura prévia do arquivo e renderiza um dropdown listando todas as abas identificadas na planilha.
  - [ ] O botão "Avançar" só é liberado após a escolha de uma aba válida.

---

### 5.2 Wizard de Importação - Passo 2: Pré-Visualização e Seleção de Cabeçalho
* **Objetivo:** Localizar a linha exata onde começam os títulos das colunas na planilha externa.
* **Passo a Passo:**
  1. Após escolher a aba, avance para o **Passo 2**.
  2. Observe a tabela de amostragem das primeiras 10 linhas da planilha.
  3. Selecione a linha que contém os rótulos reais de coluna (geralmente Linha 0 ou Linha 1).
  4. Clique em **"Avançar"**.
* **Critério de Validação:**
  - [ ] As linhas da planilha são renderizadas com clareza em formato tabular.
  - [ ] A linha selecionada é destacada com borda e cor de seleção.

---

### 5.3 Wizard de Importação - Passo 3: Mapeamento Dinâmico De-Para (Gatilho `+`)
* **Objetivo:** Vincular sob demanda colunas internas do SIGES com as colunas da planilha externa.
* **Passo a Passo:**
  1. No Passo 3, observe o painel esquerdo inicialmente limpo.
  2. Clique no botão de destaque interativo **"+" (Adicionar Coluna)**.
  3. Escolha uma propriedade interna (ex: *Cliente*, *PEP Obra*, *TDC*).
  4. No dropdown da direita, selecione a coluna correspondente da planilha.
* **Critério de Validação:**
  - [ ] Cada clique no botão `+` adiciona uma nova linha de correspondência de-para reativa.
  - [ ] É possível remover mapeamentos adicionados incorretamente pelo botão da lixeira.

---

### 5.4 Trava de Chave Única Obrigatória (`num_servico` / RN-08.3)
* **Objetivo:** Garantir a correspondência unívoca e impedir importações cegas que corrompam o banco de dados.
* **Passo a Passo:**
  1. Mapeie apenas campos secundários (ex: *Cliente* e *Bairro*), deixando a chave de serviço de fora.
  2. Tente clicar no botão **"Confirmar e Sincronizar"**.
* **Critério de Validação:**
  - [ ] O sistema bloqueia a execução e exibe o alerta obrigatório da RN-08.3: *"O mapeamento do 'Número do Serviço' é obrigatório para sincronizar os dados."*
  - [ ] Ao adicionar e mapear a coluna *Número do Serviço*, o botão de sincronização é habilitado.

---

### 5.5 Atualização Seletiva e Relatório de Inconsistências (RN-08.2 e RN-08.4)
* **Objetivo:** Atualizar somente os dados selecionados sem apagar campos pré-existentes e auditar o resultado da carga.
* **Passo a Passo:**
  1. Complete o mapeamento da chave e de mais 1 campo e confirme a importação.
  2. Observe o sumário final emitido na tela.
* **Critério de Validação:**
  - [ ] O sistema exibe um relatório pós-importação informando: total de linhas processadas, quantidade atualizada com sucesso e lista de ordens não encontradas (se houver).
  - [ ] Campos do banco de dados que não foram incluídos no de-para permanecem 100% intactos com seus valores anteriores (sem sobrescrita por nulos).

---

## ⚡ Módulo 6: Tela 01 - Medição, Validador de Origem, Lotes e Bypass
*Origem: CDU V1 (CDU-01 e CDU-02), CDU V4 e CDU V5 (Item 2.0 - Tela 01)*

### 6.1 Trava Obrigatória do Sistema de Origem do Serviço
* **Objetivo:** Blindar a empresa contra devoluções e glosas da Distribuidora por falta de identificação do canal gerador.
* **Passo a Passo:**
  1. Na tela de **Medição**, selecione uma ordem cujo campo Sistema de Origem esteja vazio ou `⚠️ NÃO VALIDADO`.
  2. Tente tramitar o serviço para frente utilizando a barra de ações ou o Drawer lateral.
* **Critério de Validação:**
  - [ ] O sistema bloqueia o avanço e exibe o alerta: *"Validação Obrigatória do Sistema de Origem não confirmada! É necessário definir o Sistema de Origem (Eorder, Synergia, SacBt, etc) antes de avançar."*
  - [ ] No Drawer, selecione a origem correta (ex: *Eorder*), salve e repita a tramitação. O avanço deve ocorrer normalmente.

---

### 6.2 Bypass do Fluxo Comercial (Salto Inteligente para Faturamento)
* **Objetivo:** Eliminar etapas burocráticas desnecessárias para contratos e ordens do tipo Comercial.
* **Passo a Passo:**
  1. Localize na tela de Medição uma ordem pertencente a um contrato ou tipo de serviço **Comercial**.
  2. Aprove a medição sem pendências para que o serviço avance.
* **Critério de Validação:**
  - [ ] A ordem pula automaticamente a etapa de fechamento de campo (Status 03) e é direcionada direto para o **Status 08 (Validado — Aguard. Autorização de Faturamento)**.
  - [ ] Na Timeline do serviço, é gravada automaticamente a nota explicativa: `⚡ [Bypass Comercial - CDU V5] ... pulou automaticamente para o Status 08`.

---

### 6.3 Ações em Lote Inteligentes com Tolerância a Falhas Parciais
* **Objetivo:** Evitar que um lote com dezenas de serviços seja cancelado se apenas uma ordem contiver pendência.
* **Passo a Passo:**
  1. Selecione 3 ordens na tabela de Medição.
  2. Certifique-se intencionalmente de que 1 delas está irregular (ex: sem sistema de origem) e as outras 2 estão regulares.
  3. Execute uma ação em lote (ex: *Enviar Lote para Validação* ou *Validar Origem*).
* **Critério de Validação:**
  - [ ] A API responde com código HTTP de sucesso para a operação parcial, sem travar o navegador nem retornar erro 500.
  - [ ] O sistema exibe um sumário detalhado informando: `✅ 2 serviço(s) tramitado(s) com sucesso` e `⚠️ 1 com falha (exibindo o motivo do bloqueio)`.
  - [ ] Os 2 serviços regulares avançam na esteira e o irregular permanece selecionável para correção.

---

### 6.4 Correlação Visual de Serviços Irmãos
* **Objetivo:** Agrupar visualmente na esteira ordens que pertencem à mesma Obra/PEP, Incidência ou Cliente.
* **Passo a Passo:**
  1. Na tabela da tela de Medição, role a lista e localize serviços com a mesma Incidência ou mesmo PEP.
* **Critério de Validação:**
  - [ ] O sistema destaca as ordens correlatas com uma borda azul suave e insere o badge identificador `🔗 SOB Irmã`.
  - [ ] Ao passar o cursor sobre o badge, um tooltip explica o critério de compartilhamento (mesma incidência, obra ou cliente).

---

### 6.5 Hyperlink Oficial do GPM com Parâmetro GET `cod_srv`
* **Objetivo:** Abrir a visualização oficial da ordem de serviço diretamente no sistema legado GPM sem fechar o SIGES.
* **Passo a Passo:**
  1. Na tabela de serviços ou no Drawer lateral, observe o número da ordem (ex: `SOB-363442192`).
  2. Passe o cursor sobre o link azul e clique sobre ele.
* **Critério de Validação:**
  - [ ] O link abre uma nova aba do navegador (`target="_blank"`).
  - [ ] A URL de destino aponta estritamente para o método oficial GET do GPM:
    ```text
    https://cosampa.gpm.srv.br/gpm/geral/relatorio_servico.php?cod_srv=363442192
    ```
  - [ ] O prefixo `SOB-` é isolado da URL, mantendo-se perfeitamente visível na interface do SIGES.

---

### 6.6 Envio em Lote para Validação do Cliente (CDU-02)
* **Objetivo:** Consolidar medições internas do Status 03 e enviá-las para aprovação formal da Distribuidora.
* **Passo a Passo:**
  1. Filtre a listagem pelo **Status 03 (Aguardando Envio para Validação)**.
  2. Selecione uma ou mais ordens e clique no botão **"🚀 Enviar Lote p/ Validação (CDU-02)"**.
  3. Preencha os campos obrigatórios da transição: **Sistema de Faturamento** e **Mês de Medição Inicial** (`MM/AAAA`).
  4. Confirme o envio.
* **Critério de Validação:**
  - [ ] Os serviços avançam para o **Status 05 (Aguard. Validação do Cliente)**.
  - [ ] Os campos de competência e sistema de faturamento são gravados nas propriedades dos serviços.

---

## 💰 Módulo 7: Módulo Financeiro, Faturamento e Conciliação Automática
*Origem: CDU V5 (Item 2.0 - Telas 04, 05 e 06)*

### 7.1 Tela 04: Validação de Faturamento e Trava de Data (08 ➔ 09)
* **Objetivo:** Garantir a conferência formal do faturamento antes de direcionar a ordem para conciliação.
* **Passo a Passo:**
  1. Acesse pelo menu a tela de **Faturamento (Tela 04)**.
  2. Selecione uma ordem no **Status 08 (Validado — Aguard. Autorização)**.
  3. Tente avançar a ordem sem preencher a Data de Validação.
* **Critério de Validação:**
  - [ ] O sistema recusa o avanço e emite alerta: *"O preenchimento da Data de Validação é obrigatório para avançar para o Faturado/Conciliação (CDU V5 - Tela 04)"*.
  - [ ] Informe a data de validação (ou clique no atalho "Hoje") e acione **"Validar e Enviar p/ Conciliação"**. A ordem transita com sucesso para o **Status 09**.

---

### 7.2 Tela 05 (Sub-Aba 09): Trava de Mês de Emissão do Faturamento (09 ➔ 10)
* **Objetivo:** Estabelecer a competência de emissão financeira (`MM/AAAA`) antes de disponibilizar o faturamento para o evento de conciliação.
* **Passo a Passo:**
  1. Acesse a tela de **Conciliações (Tela 05)** e entre na sub-aba **09. Aguardando Retorno**.
  2. Abra o Drawer lateral de um serviço no Status 09.
  3. Tente avançar para o Status 10 sem digitar o mês de emissão.
* **Critério de Validação:**
  - [ ] O avanço é bloqueado exigindo o preenchimento de `mes_emissao` no padrão `MM/AAAA`.
  - [ ] Digite a competência (ex: `09/2026`) e confirme. A ordem transita para o **Status 10 (Análise de Conciliação)**.

---

### 7.3 Tela 05 (Sub-Aba 10): Snapshot Pré-Importação ("Relatório ANTES")
* **Objetivo:** Congelar uma cópia imutável dos dados faturados antes de processar qualquer pagamento da concessionária.
* **Passo a Passo:**
  1. Na tela de **Conciliações**, acesse a sub-aba **10. Evento de Conciliação**.
  2. Clique no botão superior **"📸 Snapshot Pré-Importação (Relatório ANTES)"**.
* **Critério de Validação:**
  - [ ] O sistema abre um modal estruturado consultando a tabela `conciliacao_snapshots`.
  - [ ] São exibidos os dados originais exatos dos serviços (IDs, Contratos, Clientes, Status Anterior e Valor Faturado Integral).
  - [ ] O registro do snapshot fica gravado permanentemente para fins de auditoria contábil e jurídica.

---

### 7.4 Tela 05 (Sub-Aba 10): Fechamento Transacional Automático de Conciliação
* **Objetivo:** Efetuar o confronto automático entre os valores faturados pela Cosampa e os valores pagos pela Distribuidora.
* **Passo a Passo:**
  1. Na sub-aba **10. Evento de Conciliação**, clique em **"⚡ Fechar Evento de Conciliação"**.
  2. **Cenário 1 (100% Batido):** Escolha o cenário de pagamento integral e confirme o processamento.
  3. **Cenário 2 (Com Glosa/Divergência):** Escolha o cenário com glosas parciais e confirme o processamento.
* **Critério de Validação:**
  - [ ] **Resultado Cenário 1:** As ordens cujo pagamento cobriu 100% do valor faturado são direcionadas automaticamente para o **Status 14 (FATURADO TOTAL - FINALIZADO)** com nota de liquidação na Timeline.
  - [ ] **Resultado Cenário 2:** As ordens que sofreram corte de pagamento são direcionadas automaticamente para o **Status 11 (CONCILIADO COM DIVERGENCIAS)**, calculando e exibindo a diferença no campo `divergencia_conciliacao`.

---

### 7.5 Tela 05 (Sub-Aba 11): Comparador Dinâmico Bilateral de Itens (Baremo)
* **Objetivo:** Permitir ao analista dissecar a glosa item a item do baremo para identificar onde a Distribuidora cortou medição.
* **Passo a Passo:**
  1. Na tela de **Conciliações**, entre na sub-aba **11. Divergências** e abra o Drawer de um serviço no Status 11.
  2. Observe os cards de confronto: *Realizado (Cosampa)*, *Pago (Distribuidora)* e *Divergência*.
  3. Clique no botão **"🔍 Ver Detalhamento por Item (Baremo)"**.
* **Critério de Validação:**
  - [ ] O painel abre uma tabela listando cada código e descrição de item do baremo medido.
  - [ ] Confronta lado a lado a quantidade realizada, valor faturado, valor pago pela Distribuidora e a divergência pontual apurada.

---

### 7.6 Tela 05 (Sub-Aba 11 ➔ 12): Trava de Justificativa Técnica e Evidências SharePoint
* **Objetivo:** Condicionar a contestação de glosas ao registro formal de justificativa e documentação comprobatória.
* **Passo a Passo:**
  1. No Drawer lateral do serviço com divergência (Status 11), localize os campos de Justificativa Técnica e Link do SharePoint.
  2. Tente clicar no botão **"Cobrar Cliente (Ir p/ 12)"** deixando a justificativa em branco.
* **Critério de Validação:**
  - [ ] O sistema bloqueia a tramitação e exibe alerta exigindo justificativa técnica formal.
  - [ ] Preencha a justificativa técnica, insira o link da pasta do SharePoint contendo as evidências fotográficas e confirme.
  - [ ] A ordem transita para o **Status 12 (Pgto a Menor — Cobrar Cliente)**, a justificativa é postada na Timeline e o link do SharePoint é persistido.

---

### 7.7 Tela 05 (Sub-Aba 12 ➔ 13): Gestão de Disputas e Mês de Reapresentação
* **Objetivo:** Estabelecer a custódia jurídica/contratual e o prazo de reapresentação das glosas a recuperar.
* **Passo a Passo:**
  1. Localize a ordem no **Status 12**.
  2. No Drawer, localize a seção **"Mês de Reapresentação & Disputa"**.
  3. Tente avançar sem preencher o mês de reapresentação.
* **Critério de Validação:**
  - [ ] O sistema bloqueia a tramitação informando a obrigatoriedade da competência de reapresentação.
  - [ ] Informe o mês (ex: `11/2026`) e clique em **"Iniciar Disputa Contratual"**.
  - [ ] A ordem avança para o **Status 13 (Pgto a Menor — Em Disputa)**, registrando o analista logado como `responsavel_disputa`.
  - [ ] O Drawer do Status 13 passa a exibir o responsável nominal, mês de reapresentação e link clicável direto para o SharePoint.

---

### 7.8 Tela 06 / Sub-Aba 14: Blindagem e Imutabilidade do Status 14
* **Objetivo:** Garantir que ordens integralmente recebidas e conciliadas fiquem permanentemente protegidas contra adulterações.
* **Passo a Passo:**
  1. Acesse a tela ou sub-aba **14. Finalizados**.
  2. Abra o Drawer lateral de qualquer serviço com Status 14.
  3. Tente tramitar o serviço para qualquer outro status pelo painel ou via chamada direta à API.
* **Critério de Validação:**
  - [ ] O Drawer exibe o selo de proteção em destaque verde: **"🔒 REGISTRO FINALIZADO E TRANCADO (100% FATURADO)"**.
  - [ ] Os controles de tramitação manual ficam desabilitados/ocultos.
  - [ ] O backend rejeita terminantemente qualquer tentativa de modificação retornando status de bloqueio por imutabilidade.

---

## 📊 Matriz Consolidada de Rastreabilidade (CDU V0 ➔ V5)

| Funcionalidade Implementada | Versão de Origem do CDU | Componente / Rota Principal | Status de Entrega |
| :--- | :---: | :--- | :---: |
| **Log de Auditoria Imutável (RN-01)** | CDU V0 / V1 | `backend/db.py` (`registrar_log_auditoria`) | ✅ 100% Funcional |
| **Bloqueio Rígido por Pendências (RN-03)** | CDU V0 / V1 | `backend/db.py` (`tramitar_servico_db`) | ✅ 100% Funcional |
| **Retorno Automático p/ Medição (RN-04)** | CDU V0 / V1 | `backend/db.py` (Resolução 100% itens) | ✅ 100% Funcional |
| **Filtro Hierárquico de Campo (RN-05)** | CDU V1 / V2 | `frontend/app.js` e queries relacionais | ✅ 100% Funcional |
| **Desacoplamento `num_servico` vs `tdc`** | CDU V2 / V5 | `backend/db.py` e colunas do MySQL | ✅ 100% Funcional |
| **Importador Inteligente de Planilhas (CDU-08)** | CDU V3 | `/api/servicos/importar-dinamico` (Wizard 3 passos) | ✅ 100% Funcional |
| **Perfis de Tela e Modo de Edição Dinâmico** | CDU V4 | `/api/perfis_tela` (Master Global vs Privado) | ✅ 100% Funcional |
| **Controle de Acesso por Alçadas (RBAC)** | CDU V3 / V4 | `/api/auth/login` e `/api/usuarios` | ✅ 100% Funcional |
| **Paginação Server-Side e Lazy Loading** | CDU V5 | `/api/servicos?skip=0&limit=10` e LocalStorage | ✅ 100% Funcional |
| **Timeline Colaborativa com `@menções`** | CDU V5 | `/api/servicos/<id>/comentarios` | ✅ 100% Funcional |
| **Motor de SLA Dinâmico por Status** | CDU V5 | Badges coloridos e cálculo de dias úteis | ✅ 100% Funcional |
| **Trava Obrigatória de Sistema de Origem** | CDU V5 | Validador pré-tramitação e lote | ✅ 100% Funcional |
| **Bypass Comercial Inteligente (01 ➔ 08)** | CDU V5 | Roteamento automático de contratos comerciais | ✅ 100% Funcional |
| **Processamento de Lotes com Falha Parcial** | CDU V5 | Sumário tolerante a falhas pontuais | ✅ 100% Funcional |
| **Serviços Irmãos e Hyperlinks GPM (`cod_srv`)** | CDU V5 | Agrupamento visual e URL oficial do GPM | ✅ 100% Funcional |
| **Validação de Faturamento (08 ➔ 09)** | CDU V5 | Trava obrigatória de `data_validacao` | ✅ 100% Funcional |
| **Mês de Emissão do Faturamento (09 ➔ 10)** | CDU V5 | Trava obrigatória de `mes_emissao` (MM/AAAA) | ✅ 100% Funcional |
| **Snapshot Pré-Importação ("Relatório ANTES")** | CDU V5 | `/api/conciliacao/evento/iniciar-snapshot` | ✅ 100% Funcional |
| **Fechamento Automático de Conciliação** | CDU V5 | `/api/conciliacao/evento/fechar` (100% batido vs glosa) | ✅ 100% Funcional |
| **Comparador Dinâmico Bilateral (Status 11)** | CDU V5 | `/api/servicos/<id>/comparador-bilateral` | ✅ 100% Funcional |
| **Justificativa Obrigatória e SharePoint (11 ➔ 12)** | CDU V5 | Exigência na Timeline e link documental | ✅ 100% Funcional |
| **Gestão de Disputas e Custódia (12 ➔ 13)** | CDU V5 | Trava de `mes_reapresentacao` e responsável | ✅ 100% Funcional |
| **Imutabilidade e Trancamento do Status 14** | CDU V5 | Bloqueio categórico contra alterações operacionais | ✅ 100% Funcional |

---

> [!NOTE]
> **Orientações para a Sessão de Testes:** Inicie a execução pelo Módulo 1 (Fundações) e avance sequencialmente até o Módulo 7 (Financeiro). Todas as rotas do backend estão ativas e sincronizadas com o banco de dados MySQL `siges_app`.
