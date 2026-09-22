# 📋 Checklist Comparativo e Plano de Ação EXAUSTIVO (CDUV5)

Após uma segunda varredura minuciosa no documento **CDUV5.md** e o cruzamento detalhado com a arquitetura e código atuais do sistema (como no `main.py`), este documento compila **absolutamente todos** os requisitos, divididos no que já possuímos e nas lacunas que precisam de implementação.

---

## ✅ 1. O Que Já Está Sendo Atendido (Implementado)

- [x] **Auditoria e Logs de Ações (RN-01):** As rotas de tramitação, atualizações de campos e ações em lote (como `enviar_lote_validacao`) gravam os logs rastreáveis (`registrar_log_auditoria` e `registrar_acao_global`).
- [x] **Gestão de Perfis de Tela (CDUV4 integrando V5):** Backend preparado para criação, herança, compartilhamento e controle de perfis de tela (`Globais` vs `Privados`), amarrado ao controle de acessos (RBAC).
- [x] **Importação Dinâmica Inteligente (CDU-08):** Sistema de upload que aceita XLSX/CSV, pré-visualiza os dados em pandas e mapeia colunas livremente para fazer Upsert sem sobrescrever dados preexistentes, inclusive possuindo tratamento seguro para nulos.
- [x] **Fallback de Rejeição em Lote:** Na rota de importação de rejeições (`importar_rejeicoes_lote`), o backend já verifica se o destino está omisso e aplica o redirecionamento automático para o Status `06` (Fechamento).

---

## 🏗️ 2. A IMPLEMENTAR (Segunda Verificação Detalhada)

Esta seção foi aprofundada para capturar micro-regras e requisitos técnicos avançados exigidos pelo CDUV5 que ainda não estão presentes no código.

### 2.1 Requisitos de Infraestrutura e Banco de Dados (UI/UX - Seção 5 do CDUV5)
- [ ] **Paginação e Lazy Loading (Server-Side):**
  - Refatorar a rota `GET /api/servicos` para aceitar `skip` e `limit`. A versão atual carrega dados em massa, o que violará a exigência do V5 de suportar "centenas de milhares de linhas" sem congelar a interface.
- [ ] **Persistência de Sessão no Front-end (Local Storage / API):**
  - Implementar no front-end a retenção de layout: Ordenação ativa das colunas, largura (resize) das colunas, filtros aplicados e página atual devem sobreviver a um F5 (Refresh) ou navegação entre telas.
- [ ] **Falha Parcial Segura em Lotes (Bulk Operations):**
  - Ao processar envio para aprovação ou validações em lote, se um registro não atender aos requisitos (ex: falta de comentário), a transação do lote inteiro **NÃO** deve falhar. Apenas o registro infrator deve ser retido e o sistema deve gerar um "Sumário de Importação/Edição" mostrando o que passou e o que falhou.
- [ ] **Desacoplamento de Relacionamento `num_servico` vs `tdc`:**
  - Garantir na estrutura do banco que `tdc` seja tratado como entidade auxiliar cruzada (N:M, 1:N) e nunca como chave de substituição única ao `num_servico`.
- [ ] **Imutabilidade de Histórico:**
  - Garantir a nível de banco de dados (constraints/triggers) ou API que logs e comentários de timeline **nunca** possam sofrer "Soft Delete" ou edição posterior.

### 2.2 Sistema de Colaboração e Notificações (Timeline)
- [ ] **Nova Coluna / Estrutura: `comentarios_internos` (Timeline do Serviço):**
  - Criar um painel expansível no registro do serviço que atue como um "chat de discussão".
  - [ ] Ao adicionar um comentário, deve imbutir automaticamente o perfil, usuário logado, data e hora.
  - [ ] **Parser de Marcações (`@usuario`):** Mecanismo que varre o comentário e detecta as marcações.
- [ ] **Motor de Notificação de Transição de Responsabilidade:**
  - Quando o serviço pular do Fechamento para a Operação (ex: entra em Pendência), notificar in-app ou por e-mail o novo "dono" do serviço (o respectivo Supervisor ou Analista).

### 2.3 Mudanças de Layout nas Telas e Novas Regras Visuais
- [ ] **Links Diretos para GPM:**
  - Na grid da Medição (Status 01), os campos que possuem identificadores (Turno, Serviço, Obra) devem renderizar *hiperlinks* clicáveis que remetam à estrutura legada.
- [ ] **Agrupamento de "Serviços Irmãos":**
  - A interface deve exibir visualmente, ao selecionar um serviço, quais outros registros compartilham a mesma obra (Fluxo Emergencial) ou o mesmo cliente (Fluxo Comercial).
- [ ] **Filtro Hierárquico Automático (Tela 02 - Pendências):**
  - Ao carregar a tela, a API deve detectar quem está logado: Coordenadores só veem seus supervisores, Supervisores só veem suas equipes. O front-end deve exibir um botão "Limpar Filtro de Hierarquia".
- [ ] **Tabelas Auxiliares Configuráveis (Motivos de Pendência):**
  - Criar CRUD e rotas para tabelas auxiliares que alimentem os dropdowns/checkboxes dos "Itens de Correção Cosampa" (Fotos, Materiais, Croqui) e "Itens de Correção Distribuidora", retirando o *hardcode*.

### 2.4 Novos Fluxos da Esteira e Transição de Status
- [ ] **Confirmação de Sistema de Origem (Bloqueio no Status 01):**
  - Não permitir o avanço do status 01 sem que o Analista confirme/valide o campo "Sistema de Origem" (Eorder, Synergia, etc).
- [ ] **Bypass do Fluxo Comercial (Transição 01 → 08):**
  - Modificar a lógica de transição: Serviços classificados como comerciais não vão para o Status 03, avançam **diretamente para o Status 08**.
- [ ] **Painel Expansivo de Correções e Upload de Evidências:**
  - Nas transições de pendência (Status 02, 04, 07), exibir painéis que exijam digitação na Timeline de Comentários, botão explícito de upload de mídias de comprovação, e o checkbox "Necessita Reprogramar" que, se ativo, obriga o preenchimento de `Data de Programação`.
- [ ] **Monitor de SLA em Tela:**
  - Na tela de Pendências, renderizar lado a lado a Data de Execução Original e a Data de Entrada no Status de Pendência, com um alerta de "Dias de Atraso".

### 2.5 Novas Telas e Módulo Financeiro (Telas 04 e 05)
- [ ] **Criação da Tela 04: FATURAMENTO (Status 08):**
  - Tela que suporta a ingestão e imputação do campo obrigatório `DATA DE VALIDAÇÃO`.
- [ ] **Criação da Tela 05: CONCILIAÇÃO (Status 09 ao 13):**
  - [ ] **Status 09:** Implementar input obrigatório de `MÊS DE EMISSÃO`.
  - [ ] **Status 10 (Evento de Importação de Conciliação):** 
    - Transação complexa: Ao subir planilha de retorno financeiro, gerar **Snapshot (Relatório ANTES)**.
    - Exibir extração amostragem.
    - Botão "Encerrar Evento" que checa baterimento. Se sucesso: avança para `FATURADO TOTAL`. Se divergência: avança para `Status 11`.
  - [ ] **Status 11 (Reanálise com Comparador Bilateral):**
    - Se um serviço recai aqui, o Grid padrão **muda seu formato visual** para dividir a tela: `Valor Executado` vs `Valor Pago`.
    - Geração automática do valor no campo `DIVERGÊNCIA DA CONCILIAÇÃO`.
    - Bloqueio sistêmico: Só pode avançar para o status 12 ou finalização se houver uma Justificativa Técnica postada na Timeline de Comentários.
  - [ ] **Status 12 e 13:** Exigência de preenchimento de SLA de cobrança no campo `Mês de Reapresentação`.

---

**Resumo da Análise:** A segunda verificação confirma que o *core* funcional básico existe, mas as camadas que transformam a plataforma num sistema **colaborativo e seguro** (Timeline, Notificações, snapshots financeiros, validações estritas de tela) formam o grosso do backlog pendente.
