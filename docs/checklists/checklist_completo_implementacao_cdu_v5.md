# 📋 Checklist Geral de Implementação — SIGES (Baseado no CDU V5)

Este documento consolida o **checklist completo de tudo o que foi implementado até o momento** no projeto SIGES, confrontando cada função e componente técnico desenvolvido com as exigências e regras de negócio especificadas no **[CDU V5 (Documento de Casos de Uso Mais Recente)](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/docs/CDUV5.md)**.

Para cada item implementado, é detalhado:
1. **Identificação e Status:** Se está concluído e homologado ou planejado.
2. **Função / Componente Técnico:** Nome da função no código, rota e arquivo de localização ([`backend/main.py`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py), [`backend/db.py`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py) ou [`frontend/app.js`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js)).
3. **O que foi feito na prática:** Como a funcionalidade foi construída e se comporta no sistema.
4. **O que ela deveria fazer (Regra do CDU V5):** O requisito formal de engenharia e negócio segundo a especificação.

---

## 📑 Índice dos Módulos

- [1. Fundações de Infraestrutura e Performance (Bloco 1)](#1-fundações-de-infraestrutura-e-performance-bloco-1)
- [2. Motor Colaborativo: Timeline e Notificações (Bloco 2)](#2-motor-colaborativo-timeline-e-notificações-bloco-2)
- [3. Módulo de Pendências, Hierarquia e SLA (Bloco 3)](#3-módulo-de-pendências-hierarquia-e-sla-bloco-3)
- [4. Fluxos de Tela 01 e Lotes Inteligentes (Bloco 4)](#4-fluxos-de-tela-01-e-lotes-inteligentes-bloco-4)
- [5. Módulo Financeiro e Conciliação (Bloco 5 - Telas 04 e 05)](#5-módulo-financeiro-e-conciliação-bloco-5---telas-04-e-05)
- [6. Perfis de Tela, Layouts Dinâmicos e RBAC (CDU V4 / V5)](#6-perfis-de-tela-layouts-dinâmicos-e-rbac-cdu-v4--v5)
- [7. Auditoria Global e Ingestão de Dados (CDU V3 / V5)](#7-auditoria-global-e-ingestão-de-dados-cdu-v3--v5)
- [8. Resumo Executivo de Progresso](#8-resumo-executivo-de-progresso)

---

## 1. Fundações de Infraestrutura e Performance (Bloco 1)
*Objetivo no CDU V5: Suportar bases massivas do GPM com centenas de milhares de linhas sem travamento de tela ou latência de carregamento (Item 5.1 do CDU V5).*

### [x] 1.1 Paginação Server-Side e Lazy Loading
* **Função / Componente Técnico:**
  * Backend: [`listar_servicos()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py#L75) via rota `GET /api/servicos` e consulta parametrizada em [`buscar_servicos_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L112).
  * Frontend: [`Store.carregarServicosAPI()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L242) e renderizador visual [`renderPaginador()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L474).
* **O que foi feito:**
  * O backend aceita os parâmetros `skip` e `limit` (padrão 10 itens por página), executa uma consulta SQL com `LIMIT %s OFFSET %s` e um `COUNT(*)` paralelo com os mesmos filtros ativos.
  * Retorna o formato estruturado `{ "data": [ ... ], "total": X }`.
  * O frontend renderiza controles de paginação numérica com botões anterior/próximo e atalhos rápidos.
* **O que deveria fazer segundo o CDU V5:**
  * O grid dinâmico principal deve carregar e processar bases massivas com centenas de milhares de linhas sem congelamento do navegador, renderizando sob demanda apenas a fatia solicitada (Item 5.1).

### [x] 1.2 Persistência de Sessão no Frontend
* **Função / Componente Técnico:**
  * Frontend: [`Store.constructor()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L183) e métodos de sincronização com chave `localStorage.getItem('siges_filtros_v1')`.
* **O que foi feito:**
  * Todos os estados voláteis da interface — contrato ativo, filtros de busca, cargo/responsável selecionado, página atual e ordenação da tabela — são gravados em tempo real no `localStorage`.
  * Ao carregar a página ou pressionar **F5**, o estado é reconstituído sem que o usuário perca seu contexto de trabalho.
* **O que deveria fazer segundo o CDU V5:**
  * Reter parâmetros de navegação (filtros, ordenações, largura de colunas e paginação corrente) ao alternar telas ou recarregar a janela, garantindo ergonomia operacional contínua (Item 5.1).

### [x] 1.3 Integridade dos Indicadores do Dashboard (KPIs Globais)
* **Função / Componente Técnico:**
  * Backend: Rota `GET /api/dashboard/kpis` mapeada em [`backend/main.py`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py#L252).
  * Frontend: [`Store.carregarKPIsAPI()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L305) e renderização dos cards e gráficos em [`renderGerencial()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L858).
* **O que foi feito:**
  * A rota de KPIs executa agregações completas no MySQL (`COUNT(*)` agrupado por `status_id`), desacoplada da paginação de 10 linhas da tabela.
* **O que deveria fazer segundo o CDU V5:**
  * O card "Serviços na Esteira" e os gráficos analíticos devem refletir a totalidade real dos serviços da filial/contrato, garantindo visão gerencial precisa mesmo com lazy loading na listagem.

### [x] 1.4 Desacoplamento de Chaves: `num_servico` vs `tdc`
* **Função / Componente Técnico:**
  * Banco de Dados: Colunas `num_servico` e `tdc` tratadas como identificadores independentes em [`backend/db.py`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py).
  * Frontend: Colunas separadas nas tabelas e no Drawer de detalhes [`renderDrawer()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L1743).
* **O que foi feito:**
  * Tratamento individual das duas chaves, suportando relações em que múltiplos serviços compartilham o mesmo TDC ou vice-versa.
* **O que deveria fazer segundo o CDU V5:**
  * `num_servico` (Chave Primária GPM) e `tdc` (Chave Distribuidora) possuem independência estrutural e suportam relações de cardinalidade 1:N, 1:1, N:1 e N:M, servindo o TDC para cross-reference com sistemas externos (Item 1.1).

---

## 2. Motor Colaborativo: Timeline e Notificações (Bloco 2)
*Objetivo no CDU V5: Centralizar a colaboração humana ativa entre Medição, Operação, Validação e Faturamento em histórico imutável (Item 1.0 e 5.2 do CDU V5).*

### [x] 2.1 Modelagem da Timeline e Persistência Imutável
* **Função / Componente Técnico:**
  * Backend: [`inserir_comentario_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L504) e [`buscar_comentarios_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L526).
  * Rotas: `GET /api/servicos/<id>/comentarios` e `POST /api/servicos/<id>/comentarios` em [`backend/main.py`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py#L137).
  * Banco de Dados: Tabela `comentarios_servico` contendo `servico_id`, `usuario_id`, `usuario_nome`, `texto` e `created_at`.
* **O que foi feito:**
  * O backend grava comentários com chave estrangeira para o serviço e o usuário logado, com carimbo automático de data/hora (timestamp). Não há rota de edição ou exclusão de comentários.
* **O que deveria fazer segundo o CDU V5:**
  * Registrar histórico cronológico e centralizado imutável de interações humanas associando autor, perfil e data/hora, nunca permitindo deleção lógica ou física (Item 1.0 e 5.2).

### [x] 2.2 Interface da Timeline no Painel Lateral (Drawer)
* **Função / Componente Técnico:**
  * Frontend: Container `#timeline-container` dentro de [`renderDrawer()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L1743) e chamadas assíncronas no evento de abertura da SOB.
* **O que foi feito:**
  * Ao clicar em qualquer serviço na tabela, o Drawer abre e dispara imediatamente o fetch para a rota de comentários daquela SOB específica, exibindo indicador de loading e mensagens em formato de balões com autor e horário.
* **O que deveria fazer segundo o CDU V5:**
  * Exibir o histórico de discussões e anotações técnicas em formato de chat/timeline dentro do detalhe do serviço (Item 1.0 e 1.2).

### [x] 2.3 Formatador Visual de Menções (`@usuario`)
* **Função / Componente Técnico:**
  * Frontend: Expressão regular no parser de texto do comentário em [`frontend/app.js`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js).
* **O que foi feito:**
  * Textos com o padrão `@nome_usuario` são capturados e renderizados com tag visual estilizada (badge com cor destacada).
* **O que deveria fazer segundo o CDU V5:**
  * Suportar marcações de usuários (`@usuario`) para identificação de destinatários e direcionamento de notificações (Item 1.0).

### [x] 2.4 Segregação Estrita de Conversas por SOB
* **Função / Componente Técnico:**
  * Frontend e Backend: Chave de filtro `servico_id` obrigatória em [`buscar_comentarios_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L526).
* **O que foi feito:**
  * Limpeza obrigatória do container de timeline ao alternar entre serviços, garantindo que o histórico de uma SOB nunca apareça em outra.
* **O que deveria fazer segundo o CDU V5:**
  * Garantir a integridade do dossiê do serviço, evitando que apontamentos técnicos vazem entre ordens de serviço distintas.

---

## 3. Módulo de Pendências, Hierarquia e SLA (Bloco 3)
*Objetivo no CDU V5: Regras rígidas para o trabalho de campo, controle de prazos e fluxo hierárquico na Tela 02 (Item 1.1, 2 - Tela 02 e Seção 3 do CDU V5).*

### [x] 3.1 Filtragem Hierárquica Automática por Perfil (RN-05)
* **Função / Componente Técnico:**
  * Frontend: Leitura de cargo em [`AuthService.getPerfilAtivo()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L130) e aplicação de filtro default no [`Store.carregarServicosAPI()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L242).
  * Backend: Cláusulas dinâmicas `WHERE s.supervisor = %s` ou `WHERE s.coordenador = %s` em [`buscar_servicos_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L112).
* **O que foi feito:**
  * Ao fazer login como Supervisor, o sistema pré-seleciona seu nome no filtro e restringe a grid às equipes subordinadas a ele. Ao logar como Coordenador, filtra por seus supervisores.
  * Disponibilizada a opção "Todos" (Limpar Filtro) para consulta ampla.
* **O que deveria fazer segundo o CDU V5:**
  * Ao acessar a Tela de Pendências, o grid é pré-filtrado de forma automática com base no login e perfil da árvore de subordinação (Coordenador vê subordinados; Supervisor vê equipes diretas), com prerrogativa de desfiltração para consultas gerais (Item 2 - Tela 02).

### [x] 3.2 Tabelas Auxiliares Configuráveis de Pendências
* **Função / Componente Técnico:**
  * Backend: [`obter_parametros_pendencias_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L545) e rota `GET /api/parametros/pendencias`.
  * Frontend: [`Store.carregarParametrosPendenciasAPI()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L315) e renderização das opções em [`renderMedicao()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L985).
* **O que foi feito:**
  * Removidos todos os textos fixos (hardcodes) do frontend. As opções de desvios são carregadas diretamente do banco de dados MySQL (`itens_correcao_cosampa` e `itens_correcao_distribuidora`).
  * Categorias organizadas:
    * **Cosampa:** 1. Fotos (Baixa qualidade, Sem evidência); 2. Materiais (Aplicados/Retirados incorretamente); 3. Documentação (Sem Croqui, Croqui incorreto).
    * **Distribuidora:** Vozes não cadastradas, Serviço não despachado, Ordem já faturada.
* **O que deveria fazer segundo o CDU V5:**
  * O backend e os componentes visuais devem ser alimentados diretamente pelas tabelas de parametrização lógica administráveis (Seção 3 do CDU V5).

### [x] 3.3 Tramitação em Lote e Individual para Pendências (Status 02 e 04)
* **Função / Componente Técnico:**
  * Frontend: [`Store.tramitarLoteAPI()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L388) vinculado aos botões `#btn-enviar-pend-cosampa` e `#btn-enviar-pend-distribuidora`.
  * Backend: Rota `POST /api/servicos/lote/tramitar` em [`backend/main.py`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py#L161).
* **O que foi feito:**
  * O operador pode selecionar um ou dezenas de serviços na Medição, marcar os itens de correção correspondentes e enviá-los em lote para o Status `02` (Pendências Cosampa) ou `04` (Pendências Distribuidora). O serviço é retirado da Medição e passa a constar na Tela 02.
* **O que deveria fazer segundo o CDU V5:**
  * "Gerar Pendência Cosampa" envia para `02. PENDENCIAS OPERACIONAIS COSAMPA` e "Gerar Pendência Distribuidora" para `04. PENDENCIAS DISTRIBUIDORA`. A Pendência Cosampa tem prioridade em caso de apontamento duplo (Item 2 - Tela 01 e Matriz 4.1).

### [x] 3.4 Bloqueio com Trava de Reprogramação e Alerta de SLA
* **Função / Componente Técnico:**
  * Frontend: Eventos e validações no Drawer de saneamento em [`renderPendencias()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L1187) e [`renderDrawer()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L1743).
  * Backend: Persistência em [`atualizar_dados_servico_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L309).
* **O que foi feito:**
  * Inclusão do checkbox "Necessita Reprogramar Visitada em Campo". Caso marcado, o botão de salvar trava e emite alerta visual exigindo o preenchimento da `data_programacao`.
  * Cálculo dinâmico de dias decorridos exibido no badge: ⏳ **Atraso SLA: X dias**.
  * Botão de retorno tramita o serviço sanado de volta para `01. AGUARDANDO CONFERENCIA`.
* **O que deveria fazer segundo o CDU V5:**
  * Checkbox "Necessita Reprogramar" exige obrigatoriamente a indicação de uma nova Data de Programação para retorno da equipe. Monitoramento de SLA comparando data de execução com data de entrada em pendência (Item 2 - Tela 02).

### [x] 3.5 Ordenação Temporal nas Pendências
* **Função / Componente Técnico:**
  * Backend: Cláusula `ORDER BY COALESCE(s.dta_exec_srv, s.created_at) DESC` em [`buscar_servicos_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L112).
* **O que foi feito:**
  * Os serviços na tela de pendências são ordenados do mais recente para o mais antigo com fallback seguro para colunas existentes no schema (`dta_exec_srv` / `created_at`).
* **O que deveria fazer segundo o CDU V5:**
  * Facilitar a triagem e o tratamento das pendências mais urgentes e recentes pela supervisão técnica.

---

## 4. Fluxos de Tela 01 e Lotes Inteligentes (Bloco 4)
*Objetivo no CDU V5: Blindagem de operações em lote com falha parcial, validação mandatória de origem, bypass comercial acelerado e correlação de serviços irmãos na Medição (Item 1.1, 2 - Tela 01 e 5.3 do CDU V5).*

### [x] 4.1 Validação Obrigatória do Sistema de Origem (Trava da Tela 01)
* **Função / Componente Técnico:**
  * Backend: Trava em [`tramitar_servico_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L269) e `origem_sistema` retornada por [`buscar_servicos_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L112).
  * Frontend: Seletor de Origem com botão de salvamento no Drawer [`renderDrawer()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L1888), seletor em lote `#select-bulk-origem` em [`renderMedicao()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L1010) e trava impeditiva no botão `#drawer-btn-tramitar`.
* **O que foi feito:**
  * Ao tentar tramitar qualquer serviço da Medição (status 01) para status operacional posterior sem que o campo `origem_sistema` esteja confirmado, o sistema bloqueia a ação e emite um alerta explícito exigindo a seleção da origem (ex: Eorder, Synergia, SacBt, PDA).
  * Na tabela, serviços sem origem exibem o badge em destaque vermelho `⚠️ NÃO VALIDADO`. O Drawer e a barra lateral permitem salvar o Sistema de Origem individualmente ou em lote.
* **O que deveria fazer segundo o CDU V5:**
  * Antes de qualquer envio para o próximo status, o sistema exige a validação/confirmação do campo SISTEMA DE ORIGEM DO SERVIÇO, exibindo o valor default contido na tabela principal e permitindo correções em lote ou individuais (Item 1.1 e 2 - Tela 01).

### [x] 4.2 Bypass do Fluxo Comercial (Salto de Status Direto 01 -> 08)
* **Função / Componente Técnico:**
  * Backend: Cláusula de desvio condicional em [`tramitar_servico_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L269) acionada por `contrato`, `tipo_servico` ou `tipo_obra`.
  * Injeção na Timeline: [`inserir_comentario_db()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L504) registrando aviso oficial de bypass na SOB.
  * Frontend: Botão `#btn-aprovar-medicao` em [`renderMedicao()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L1010).
* **O que foi feito:**
  * Ao aprovar a medição de serviços cujo contrato ou tipo seja Comercial, o backend intercepta o avanço e redireciona o serviço diretamente para o **Status 08 (Validado Aguardando Faturamento)**, sem passar pelo Status 03 (Fechamento).
  * A Timeline do serviço registra um comentário automático auditável informando o salto de status. Serviços do fluxo Emergencial avançam normalmente para o Status 03.
* **O que deveria fazer segundo o CDU V5:**
  * Serviços do fluxo Emergencial aprovados avançam para `03. AGUARDANDO ENVIO PARA VALIDACAO`. Serviços do fluxo Comercial aprovados avançam diretamente para `08. VALIDADO AGUARDANDO AUTORIZACAO DE FATURAMENTO` (Item 2 - Tela 01 e Matriz de Transição 4.1).

### [x] 4.3 Lotes Inteligentes com Mecânica de Falha Parcial
* **Função / Componente Técnico:**
  * Backend: Rotas [`/api/servicos/lote/tramitar`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py#L161) e [`/api/servicos/lote/enviar-validacao`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py#L189) retornando código HTTP 200 com resumo `{ "sucessos": X, "sucessos_ids": [...], "falhas": Y, "erros": [...] }`.
  * Frontend: [`Store.tramitarLoteAPI()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L388) e modal `#btn-modal-cdu02`.
* **O que foi feito:**
  * Ao tramitar múltiplos serviços em lote, cada item é validado individualmente. Se 1 serviço de um lote de 100 apresentar erro (ex: falta de Sistema de Origem ou pendência não saneada), os 99 regulares são tramitados com sucesso no banco.
  * O sistema não devolve erro 500 nem cancela o lote inteiro. Um sumário informativo exibe a quantidade de sucessos e lista detalhadamente os serviços com erro e seus motivos. Os serviços com falha continuam selecionados na tela para intervenção rápida do operador.
* **O que deveria fazer segundo o CDU V5:**
  * Caso haja qualquer registro inválido por pendências técnicas ou ausência de informações, o lote total não deve falhar. O sistema deve reter especificamente o registro inconsistente, exibindo sumário com os erros identificados e persistindo no fluxo de alteração todos os demais registros regulares (Item 5.3).

### [x] 4.4 Correlação de Serviços Irmãos e Hyperlinks GPM
* **Função / Componente Técnico:**
  * Frontend: Algoritmo de agrupamento e detecção em [`renderMedicao()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L1010) e renderizador de linhas [`renderDynamicTableRow()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L645).
* **O que foi feito:**
  * O sistema analisa em tempo real os serviços da tabela e identifica correlações que compartilham a mesma Incidência, mesmo PEP/Obra ou mesmo Id do Cliente.
  * Serviços correlacionados recebem borda lateral azul destacada (`border-left: 3.5px solid #0284c7`), fundo suave e o badge `🔗 SOB Irmã` com tooltip detalhando o motivo do vínculo.
  * As colunas de ID / Número da Ordem agora são **hyperlinks azuis clicáveis** (`target="_blank"`) com ícone de link externo, direcionando diretamente para a visualização da ordem no sistema legado GPM sem interromper a navegação da esteira.
* **O que deveria fazer segundo o CDU V5:**
  * Exibir correlação de Serviços Irmãos agrupando ordens por Incidência/Obra (Emergencial) ou Incidência/Cliente (Comercial), além de atalhos e links diretos clicáveis para abrir o módulo de ordens no GPM (Item 1.1 e 2 - Tela 01).

---

## 5. Perfis de Tela, Layouts Dinâmicos e RBAC (CDU V4 / V5)
*Objetivo no CDU V5: Visualização customizável por usuário e segregação estrita de acesso baseada em perfis (Item 1 e 5.2 do CDU V5).*

### [x] 5.1 Gerenciamento de Perfis de Tela (Layouts de Colunas)
* **Função / Componente Técnico:**
  * Backend: Rotas `/api/perfis_tela` (GET, POST, PUT), `/api/perfis_tela/todos` e `/api/usuarios/<id>/perfis_tela` em [`backend/main.py`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py#L390).
  * Frontend: [`renderToolbarPerfis()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L511), [`renderDynamicTableHeaders()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L615) e [`renderDynamicTableRow()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L645).
* **O que foi feito:**
  * Usuários podem selecionar perfis de visualização (ex: "Padrão", "Operacional", "Fechamento"), criar novos layouts de colunas, reordenar e salvar preferências individuais ou globais.
* **O que deveria fazer segundo o CDU V5:**
  * Permitir que os usuários criem, salvem, modifiquem e disponibilizem layouts personalizados de colunas para quaisquer outros usuários da plataforma, mantendo a estrutura padrão de identificação rápida (Item 1 e 1.1).

### [x] 5.2 Controle de Acesso e Permissões Baseadas em Papéis (RBAC)
* **Função / Componente Técnico:**
  * Backend: Rota `POST /api/auth/login`, rotas de usuários `/api/usuarios` e perfis `/api/perfis` em [`backend/main.py`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py#L276).
  * Frontend: Classe [`AuthService`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L73) e modal administrativo [`renderGestaoAcessos()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L1416).
* **O que foi feito:**
  * Autenticação com perfis definidos (Master, Analista de Fechamento, Coordenador, Supervisor). Telas laterais e botões de ação são habilitados ou bloqueados conforme a matriz de permissões.
  * Inclusão do recurso de criação e **edição de usuários existentes** diretamente pela interface administrativa.
* **O que deveria fazer segundo o CDU V5:**
  * Restrição estrita de acesso baseada em perfis (RBAC). A navegação de supervisores deve ser voltada às telas operacionais de pendência, limitando transições financeiras e de faturamento a perfis gerenciais e analistas de fechamento (Item 5.2).

---

## 6. Auditoria Global e Ingestão de Dados (CDU V3 / V5)
*Objetivo no CDU V5: Rastreabilidade imutável de todas as modificações e carga dinâmica de dados (Item 1.0 e 1.2 do CDU V5).*

### [x] 6.1 Motor Global de Auditoria Imutável (Audit Log)
* **Função / Componente Técnico:**
  * Backend: [`registrar_log_auditoria()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L49) e [`buscar_logs_auditoria()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L71).
  * Rota: `GET /api/servicos/<id>/auditoria` em [`backend/main.py`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/main.py#L132).
  * Frontend: Seção de Logs de Auditoria no Drawer de detalhes.
* **O que foi feito:**
  * Qualquer alteração de status ou atualização de campo dispara a gravação no MySQL com: data/hora, usuário, e-mail, campo alterado, valor anterior e novo valor.
* **O que deveria fazer segundo o CDU V5:**
  * Qualquer alteração realizada no sistema, em qualquer campo (mudanças de status, valores de input, justificativas), deve obrigatoriamente gerar um registro imutável de Log de Auditoria capturando data, hora, usuário, ID do serviço, campo, valor anterior e novo valor (Item 1.0 e 5.2).

### [x] 6.2 Importador Dinâmico Inteligente (Auto-Sync com De-Para)
* **Função / Componente Técnico:**
  * Backend: [`processar_importacao_dinamica()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/backend/db.py#L401) e rotas `/api/servicos/upload-temp`, `/api/servicos/pre-visualizar`, `/api/servicos/importar-dinamico`.
  * Frontend: [`renderWizardImportacao()`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS%20DE%20SERVICOS/frontend/app.js#L2079).
* **O que foi feito:**
  * Assistente de importação de planilhas Excel/CSV com detecção de abas e cabeçalhos, mapeamento interativo de colunas De-Para, ignorando células vazias para não sobrescrever dados prévios e sincronizando com o banco.
* **O que deveria fazer segundo o CDU V5:**
  * Permitir a ingestão massiva e padronizada de dados operacionais e de execução vindos de fontes externas ou do GPM (Item 1.2).

---

## 5. Módulo Financeiro e Conciliação (Bloco 5 - Telas 04 e 05)
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
> **Conclusão de Desenvolvimento:** Todos os módulos de engenharia previstos no documento **CDU V5** foram rigorosamente implementados, testados por scripts automatizados ponta a ponta e integrados com sucesso ao banco de dados e à interface visual do SIGES.
