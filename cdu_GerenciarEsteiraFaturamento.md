# Especificação de Requisitos Funcionais

## Caso de Uso (CDU-01) - Gerenciar Tramitação de Serviços na Esteira de Faturamento (Satélite GPM)

## Histórico de Versões

| Data       | Versão | Descrição                                                                                 | Autor                       |
| :--------- | :----- | :---------------------------------------------------------------------------------------- | :-------------------------- |
| 14/08/2026 | 1.0     | Criação do caso de uso a partir do levantamento da reunião e protótipo da Esteira GPM | Equipe de Engenharia / SIGES |

---

## 1. Nome do Caso de Uso

**Gerenciar Tramitação de Serviços na Esteira de Faturamento**

## 2. Objetivo

Permitir que os analistas e gestores das áreas de **Fechamento**, **Operação** e **Faturamento** visualizem, filtrem, façam a gestão de pendências operacionais, monitorem prazos/SLAs por etapa, realizem tramitações (individuais ou em lote) e consultem o histórico de transição dos serviços executados, integrando dados sincronizados do sistema oficial GPM.

## 3. Tipo de Caso de Uso

**Concreto**

## 4. Atores

### 4.1 Primário

* **Analista Operacional / Gestor (Fechamento, Operação ou Faturamento):** Interage diretamente com a interface web para consultar filas, aplicar filtros, tratar pendências e alterar o status dos serviços.

### 4.2 Secundário

* **Sistema Satélite GPM (Serviço de Sincronização / Backend):** Fornece os dados atualizados das ordens de serviço (SOB), notas de medição, faturamento e valores por atividade via rotina de integração periódica.

---

## 5. Precondições

1. O usuário deve estar autenticado na plataforma com um perfil de acesso válido (**Fechamento**, **Operação** ou **Faturamento**).
2. A base de serviços deve ter sido previamente sincronizada pela automação de extração do GPM a partir da data de corte definida.

---

## 6. Fluxo Principal

* **P1.** O Analista acessa a plataforma de gestão da esteira.
* **P2.** O sistema identifica o perfil do usuário logado e exibe a tela inicial (**Gerencial**) com o menu lateral, filtros globais (período, contrato, tipo, área, status e busca), indicadores-chave (KPIs de serviços ativos, valor total na esteira, tempo médio e SLAs estourados) e gráficos de distribuição por macroetapa e gargalos.
* **P3.** O Analista navega para a tela operacional correspondente à sua atribuição através do menu lateral (ex.: **01. Medição** ou **02. Pendências**). **[A1]** **[A2]**
* **P4.** O sistema lista os serviços filtrados na tabela principal, exibindo identificador (SOB), status atual, tipo de obra/serviço, contrato, nota/NF, data de entrada na etapa, valor medido e indicador visual de SLA.
* **P5.** O Analista seleciona um ou múltiplos serviços da listagem através dos checkboxes de seleção.
* **P6.** O Analista aciona uma ação de tramitação no painel lateral de tratativas:
  * **P6.1.** Clica em **"Tramitar selecionados"** para avançar para a próxima etapa padrão sugerida (ex.: 01 → 03). **[A3]**
  * **P6.2.** Seleciona um status específico no dropdown e clica em **"Aplicar aos selecionados"**. **[A4]**
  * **P6.3.** Marca os tipos de pendências e clica em **"Enviar para 02. Pendências"**. **[A5]**
* **P7.** O sistema valida as permissões do perfil, move os serviços para a nova etapa, registra a transição no histórico com a data atual e exibe notificação (*toast*) de confirmação da operação.
* **P8.** O sistema atualiza os contadores, indicadores de SLA e a listagem de serviços da tela em tempo real.
* **P9.** O caso de uso é finalizado.

---

## 7. Fluxos Alternativos

### A1. Aplicação e Salvamento de Filtros Personalizados (Presets)

* **A1.1.** No passo **P2** ou **P4**, o Analista altera os seletores de filtros (ex.: Contrato, Tipo de Serviço, Período) ou digita um termo no campo de busca.
* **A1.2.** O sistema atualiza dinamicamente as tabelas, gráficos e contadores para refletir apenas os registros correspondentes aos critérios aplicados.
* **A1.3.** O Analista clica em **"+ Salvar preset"**.
* **A1.4.** O sistema exibe um campo de texto para digitação do nome do preset.
* **A1.5.** O Analista insere o nome desejado e clica em **"Salvar"**.
* **A1.6.** O sistema adiciona o novo atalho à barra de presets, permitindo aplicação futura em 1 clique.

### A2. Consulta e Tratativa de Pendências Operacionais (Tela 02)

* **A2.1.** No passo **P3**, o Analista acessa a tela **02. Pendências**.
* **A2.2.** O sistema lista os serviços bloqueados por pendência (status 02 ou 06) e exibe o gráfico de pendências por tipo (Fotos, Documentos, Materiais, Retorno, Outros).
* **A2.3.** O Analista clica sobre uma linha da tabela para focar o serviço.
* **A2.4.** O sistema abre o painel lateral de tratativas exibindo a lista de pendências abertas para aquele serviço, barra de progresso e campos de justificativa/anexos.
* **A2.5.** O Analista marca um item de pendência como tratado (**✓**), insere o detalhamento da tratativa e opcionalmente registra contador de anexos.
* **A2.6.** Se **todas** as pendências do serviço forem marcadas como tratadas:
  * **A2.6.1.** O sistema automaticamente altera o status do serviço de volta para **01. Aguardando Conferência** (ou remove o bloqueio). **[RN-04]**
  * **A2.6.2.** O sistema exibe a mensagem: *"[ID do Serviço] — todas as pendências tratadas. Retornou para 01. Aguardando Conferência"*.
* **A2.7.** O sistema retorna ao passo **P4**.

### A3. Tramitação Rápida Sequencial ("Baixar / Tramitar")

* **A3.1.** No passo **P6.1**, para cada serviço selecionado, o sistema consulta a tabela de transição direta (`NEXT_MAP`):
  * Status **01** (Aguardando Conferência) $\rightarrow$ **03** (Aguard. Envio p/ Validação)
  * Status **03** (Aguard. Envio p/ Validação) $\rightarrow$ **04** (Aguard. Validação do Cliente)
  * Status **05** (Rejeitado Fechamento) $\rightarrow$ **03** (Aguard. Envio p/ Validação)
  * Status **10** (Conciliado c/ Divergências) $\rightarrow$ **03** (Aguard. Envio p/ Validação)
* **A3.2.** Para serviços cujo status não possua próxima etapa inequívoca (ex.: status de decisão múltipla), o sistema mantém o serviço inalterado e emite alerta instruindo o uso da opção "Alterar status".
* **A3.3.** O sistema executa o passo **P7**.

### A4. Tramitação em Massa do Fluxo Comercial (Status 01 $\rightarrow$ 07)

* **A4.1.** No passo **P6.2**, o Analista seleciona múltiplos serviços do tipo comercial ou validados em lote.
* **A4.2.** No dropdown "Novo status", seleciona **"07 · Validado — Aguard. Autorização"**.
* **A4.3.** O sistema valida a transição em lote, atualiza todos os itens selecionados para a etapa 07 de forma atômica e prossegue para o passo **P7**.

### A5. Abertura do Drawer de Detalhamento e Baremo

* **A5.1.** A qualquer momento na listagem, o Analista clica sobre uma linha de serviço ou no botão **"Abrir ↗"**.
* **A5.2.** O sistema abre uma gaveta lateral (*drawer*) detalhada contendo:
  * Cabeçalho com SOB, valor total e badge do status atual.
  * Metadados completos: Contrato, Obra, Tipo, Área Responsável, Nota, Data de Entrada e tempo de permanência na etapa com SLA.
  * Tabela de Baremo / Atividades (Código, Descrição, Quantidade, Valor Medido, Valor Pago e Diferença $\Delta$).
  * Lista detalhada de pendências e observações registradas.
  * Histórico vertical de transição de etapas com timestamps.
  * Botão de redirecionamento externo **"Abrir no GPM ↗"**. **[RN-02]**
* **A5.3.** O Analista clica no botão de fechar (`×`) ou pressiona a tecla `Esc`.
* **A5.4.** O sistema fecha o drawer e retorna à listagem.

### A6. Sincronização Manual / Consulta de Atualização do GPM

* **A6.1.** No cabeçalho superior, o Analista visualiza o badge com o tempo decorrido desde a última carga de dados (ex.: *"GPM · atualizado há 12 min"*).
* **A6.2.** O Analista clica no botão de sincronização (**⟳**).
* **A6.3.** O sistema requisita a sincronização com o banco satélite e atualiza o marcador para *"GPM · atualizado agora"*.

---

## 8. Fluxos de Exceção

### E1. Violação de Perfil de Acesso

* **E1.1.** No passo **P3**, caso o usuário tente acessar uma tela para a qual seu perfil não possui permissão (ex.: Perfil *Operação* tentando acessar a tela *01. Medição* ou *03. Faturamento*):
* **E1.2.** O sistema bloqueia a navegação, exibe um alerta explicativo (*"O perfil [Perfil] não tem acesso a [Tela]."*), e redireciona o usuário para a tela **Gerencial**.

### E2. Tentativa de Tramitação sem Seleção de Itens

* **E2.1.** No passo **P6**, o Analista clica em uma ação de tramitação com a lista de seleção vazia.
* **E2.2.** O sistema exibe um alerta toast: *"Selecione ao menos um serviço na tabela."* e não realiza alterações no banco de dados.

### E3. Envio para Pendência sem Tipo Selecionado

* **E3.1.** No passo **P6.3**, o Analista clica em "Enviar para 02. Pendências" sem marcar nenhum dos checkboxes de tipo (Fotos, Documentos, etc.).
* **E3.2.** O sistema exibe o aviso: *"Marque ao menos um tipo de pendência."* e aborta a operação.

---

## 9. Pós-condições

1. O status do serviço é atualizado no banco de dados da plataforma e refletido em todas as visões (Gerencial, Medição, Pendências e Relatórios).
2. O histórico de transições do serviço registra o novo status, data e usuário responsável.
3. O contador de tempo na etapa (SLA) é reiniciado para a nova etapa alcançada.
4. Nenhuma foto ou dado mestre oficial é sobrescrito na plataforma, preservando a integridade do GPM.

---

## 10. Regras de Negócio (RN)

| ID | Nome da Regra | Descrição e Comportamento |
| :--- | :--- | :--- |
| **RN-01** | **Repositório Oficial GPM** | O GPM é a fonte primária e oficial de dados cadastrais, fotos e medições. A plataforma satélite atua exclusivamente na gestão de fluxo, tempos, pendências e conciliação. |
| **RN-02** | **Não Armazenamento de Fotos** | A plataforma não armazena arquivos de imagens no banco de dados local. A visualização e conferência de fotos ocorrem via link direto para a tela do serviço no GPM. |
| **RN-03** | **Fluxo Unificado de 15 Status** | Todos os tipos de serviço seguem uma esteira lógica composta por 15 status distribuídos entre 5 macroetapas (Medição, Pendências, Faturamento, Conciliação e Finalizado). |
| **RN-04** | **Retorno Automático de Pendência** | Quando todas as pendências vinculadas a um serviço nos status `02` ou `06` são marcadas como tratadas, o sistema automaticamente avança o serviço para o status `01. Aguardando Conferência`. |
| **RN-05** | **Atribuição Padrão de Pendência** | Se um serviço for movido para o status `02` via "Alterar status" sem checklist selecionado, o sistema cria automaticamente uma pendência genérica do tipo `"Outros"`. |
| **RN-06** | **Matriz de Permissões por Perfil** | • **Fechamento:** Acesso a Gerencial, Medição, Pendências, Finalizados e Relatórios.<br>• **Operação:** Acesso a Gerencial, Pendências, Finalizados e Relatórios.<br>• **Faturamento:** Acesso a todas as telas (Gerencial, Medição, Pendências, Faturamento, Conciliações, Finalizados e Relatórios). |
| **RN-07** | **Prazos de SLA por Etapa** | Controle de dias na etapa para destaque de gargalos:<br>• `01` (3 dias) • `02` (5 dias) • `03` (2 dias) • `04` (7 dias) • `05` (3 dias) • `06` (5 dias) • `07` (3 dias) • `08` (10 dias) • `09` (5 dias) • `10` (4 dias) • `11` (7 dias) • `12` (15 dias) • `13 a 15` (Sem SLA). |
| **RN-08** | **Data de Corte sem Carga Histórica** | A plataforma não realiza carga retroativa de serviços finalizados de anos anteriores; o monitoramento se inicia a partir da data de implantação/corte. |

---

## 11. Requisitos Não Funcionais (RNF)

* **RNF-01 (Identidade Visual Corporativa):** Layout moderno e profissional com paleta institucional Cosampa (Verde Primário `#1c5f4b`, Fundo Neutro `#edf0ef`, Superfícies `#ffffff` e tipografia *Public Sans* com *Spline Sans Mono* para dados numéricos).
* **RNF-02 (Desempenho e Responsividade):** A interface deve renderizar listagens com paginação virtual e permitir filtragem instantânea sem recarregamento de página.
* **RNF-03 (Sincronização Periódica):** Automação em segundo plano com intervalo de atualização configurado para ~15 minutos por data de última modificação ou 4 rotinas diárias em lote.
* **RNF-04 (Compatibilidade):** Suporte total em navegadores corporativos modernos (Google Chrome, Microsoft Edge, Firefox).

---

## 12. Ponto de Extensão

* **PE-01 (Crítica Automática GPM × e-Order):** Módulo futuro de conciliação algorítmica para identificação automática de divergências de faturamento sem necessidade de triagem humana inicial.

---

## 13. Frequência de Utilização

Uso contínuo diário e intensivo durante todo o expediente operacional pelas equipes de Fechamento, Operação e Faturamento da Cosampa.

---

## 14. Interface Visual

### 14.1 Mapeamento dos Elementos de Interface

| ID do Elemento | Nome do Componente | Tipo de Componente | Formato / Opções | Regra / Comportamento |
| :--- | :--- | :--- | :--- | :--- |
| **UI-01** | **Menu Lateral Retrátil** | Menu de Navegação | Ícones + Rótulos das 6 telas | Permite colapsar (62px) ou fixar aberto (236px); bloqueia telas fora do perfil. |
| **UI-02** | **Badge de Sincronização GPM** | Badge Interativo | `GPM · atualizado há X min` + Botão ⟳ | Exibe status da base e dispara sincronização manual. |
| **UI-03** | **Seletor de Perfil** | Dropdown (`<select>`) | `Fechamento`, `Operação`, `Faturamento` | Altera em tempo real as permissões de telas e abas disponíveis. |
| **UI-04** | **Barra de Filtros Globais** | Container de Filtros | Período, Contrato, Tipo, Área, Status, Busca | Filtra dinamicamente as tabelas e KPIs da tela ativa. |
| **UI-05** | **Chips de Presets** | Botões de Filtro Rápido | Nome do preset + Botão `×` de remoção | Aplica combinações salvas de filtros com 1 clique. |
| **UI-06** | **Cards de Indicadores (KPIs)** | Tiles Numéricos | Valores em R$ mil/mi, Quantidades, Tempo | Exibe somatório de serviços ativos, valor parado e média de permanência. |
| **UI-07** | **Gráfico de Status / Gargalos** | Gráfico de Barras | 15 Barras coloridas por macroetapa | Destaque visual em vermelho para etapas com SLA estourado. |
| **UI-08** | **Tabela de Serviços** | Grid de Dados Interativo | Checkbox, Status, SOB, Obra, Nota, Data, Valor, SLA | Suporta ordenação, clique na linha para drawer e seleção múltipla. |
| **UI-09** | **Painel de Tratativas** | Card Lateral Fixo | Dropdown de status, Tramitar, Checklist pendências | Executa movimentação individual ou em lote dos itens selecionados. |
| **UI-10** | **Checklist de Pendências** | Lista de Seleção com Check | Fotos, Documentos, Materiais, Retorno, Outros | Permite marcar itens como tratados com recálculo automático da barra de progresso. |
| **UI-11** | **Drawer de Detalhamento** | Gaveta Lateral Deslizante | Metadados, Baremo, Histórico, Botão GPM | Exibe raio-x completo do serviço e histórico de passagens. |
| **UI-12** | **Notificação Toast** | Alerta Flutuante | Mensagem de texto com auto-dismiss (4.2s) | Informa sucesso de tramitações, erros e avisos de sincronização. |

### 14.2 Protótipo de Interface (Wireframe Estrutural Low-Fi)

```text
=========================================================================================================
 [C] COSAMPA - ESTEIRA DE FATURAMENTO               Satélite GPM | [● GPM · atualizado há 5 min ⟳] [Perfil: Fechamento ▾]
=========================================================================================================
 [★ Gerencial]   | [Agosto/2026 ▾] [Todos os Contratos ▾] [Todos os Tipos ▾] [Status: Todos ▾] [Buscar SOB...  ]
 [01 Medição ]   | Presets: ( Dist. Leste · 7 dias [×] )  [+ Salvar preset]
 [02 Pendên. ]   +---------------------------------------------------------------------------------------+
 [03 Faturam.]   |  SERVIÇOS NA ESTEIRA     VALOR NA ESTEIRA       POR MACROETAPA       TEMPO MÉDIO/SLA  |
 [04 Concilia]   |        21                     R$ 562,4 mil      [■■■■■■■■■■□□□□□]         6.8 dias    |
 [05 Finaliz.]   +---------------------------------------------------------------------------------------+
 [C·R Relató.]   | [✓] STATUS  | SERVIÇO / OBRA      | NOTA    | DATA   | VALOR (R$) | SLA    | TRATATIVAS
                 |---------------------------------------------------------------------------------------
                 | [ ] 01 Conf | SOB-2026-0341 · Rede| NM-0873 | 02/08  | 12.400,00  | 11d (!) | [3 sel.]
                 | [x] 01 Conf | SOB-2026-0347 · Med | NM-0879 | 05/08  |    980,00  |  8d (!) | [Novo status... ▾]
                 | [x] 02 Pend | SOB-2026-0298 · Penh| NM-0851 | 09/08  | 21.500,00  |  4d (✓) | [Aplicar status  ]
                 | [ ] 03 Envio| SOB-2026-0289 · Red | NM-0812 | 01/08  | 45.900,00  | 12d (!) | [Tramitar selec. ]
                 | [ ] 07 Valid| SOB-2026-0248 · Bel | NM-0790 | 02/08  | 52.000,00  | 11d (!) | [Enviar p/ Pend. ]
=========================================================================================================
```

---

## 15. Dicionário de Dados e Estrutura de Estado

| Variável / Campo | Tipo de Dado | Exemplo / Domínio | Descrição e Finalidade |
| :--- | :--- | :--- | :--- |
| `id` (SOB) | String | `"SOB-2026-0341"` | Código identificador único da Ordem de Serviço. |
| `ct` (Contrato) | String (Enum) | `'A'`, `'B'`, `'C'` | Contrato vinculado (`Dist. Leste`, `Dist. Sul`, etc.). |
| `ob` (Obra) | String | `"Vila Prudente"` | Nome/localidade do projeto da obra. |
| `tp` (Tipo) | String | `"Rede"`, `"Transformador"` | Tipologia do ativo/serviço elétrico. |
| `st` (Status) | Integer (1..15) | `1` a `15` | Código numérico do status atual na esteira de 15 etapas. |
| `v` (Valor) | Float / Currency | `12400.00` | Valor monetário medido total da OS em Reais (R$). |
| `d` (Data Ref.) | Integer / Date | `11` (11/08) | Data ou dia de entrada na etapa atual para cálculo de SLA. |
| `nota` | String | `"NM-0873"`, `"NF-4521"` | Número da Nota de Medição ou Nota Fiscal emitida. |
| `ret` (Retorno) | String | `"Divergência Baremo"` | Mensagem descritiva de motivo de devolução ou reprovação. |
| `pend` | Array de Objetos | `[{t: 'Fotos', tr: false}]` | Lista de pendências com tipo (`t`), tratada (`tr`), detalhe (`det`) e anexos (`ax`). |
| `bar` (Baremo) | Array de Objetos | `[{cod, desc, med, pago}]` | Itens de atividades contratadas com valores medidos e pagos. |
| `hist` | Array de Objetos | `[{st: 1, d: 9}]` | Histórico com a cronologia de etapas percorridas pela OS. |

---

## 16. Matriz de Rastreabilidade

| ID Requisito | Funcionalidade Mapeada | Passos do Caso de Uso | Elementos da Interface | Regra de Negócio Vinculada |
| :--- | :--- | :--- | :--- | :--- |
| **RF-01** | Visão Gerencial e KPIs | P2 | UI-04, UI-06, UI-07 | RN-03, RN-07 |
| **RF-02** | Filtragem Global e Presets | P4, A1.1 a A1.6 | UI-04, UI-05 | RN-08 |
| **RF-03** | Fila de Medição e Seleção em Lote | P4, P5 | UI-08 | RN-03 |
| **RF-04** | Tramitação Sequencial Direta | P6.1, A3.1 a A3.3 | UI-09 | RN-03, RN-07 |
| **RF-05** | Alteração Direta de Status em Massa | P6.2, A4.1 a A4.3 | UI-09 | RN-03, RN-06 |
| **RF-06** | Gestão e Tratativa de Pendências | A2.1 a A2.7 | UI-10 | RN-04, RN-05 |
| **RF-07** | Detalhamento, Histórico e Baremo | A5.1 a A5.4 | UI-11 | RN-01, RN-02 |
| **RF-08** | Sincronização Satélite GPM | A6.1 a A6.3 | UI-02 | RN-01, RNF-03 |
| **RF-09** | Restrição de Acesso por Perfil | P3, E1.1, E1.2 | UI-01, UI-03 | RN-06 |

---

## 17. Critérios de Aceite

* [ ] **CA-01 (Avanço Automático por Resolução de Pendências):** Ao marcar como tratadas todas as pendências de um serviço em `02. Pendências` ou `06. Rejeitado Operação`, o sistema move o serviço imediatamente para `01. Aguardando Conferência`.
* [ ] **CA-02 (Integridade de Tramitação em Lote):** A seleção de múltiplos itens e aplicação do status `07` (Fluxo Comercial) atualiza todos os registros selecionados sem inconsistência de estado.
* [ ] **CA-03 (Controle e Destaque de SLA):** Serviços que ultrapassam a quantidade de dias estipulada para seu status atual exibem o indicador visual em vermelho e constam no gráfico de gargalos da tela Gerencial.
* [ ] **CA-04 (Isolamento de Fotos e Link Externo):** O detalhamento do serviço não armazena fotos no banco de dados e fornece um botão funcional com redirecionamento para a respectiva OS no sistema GPM.
* [ ] **CA-05 (Consistência de Permissões de Perfil):** O perfil *Operação* não consegue visualizar ou tramitar itens restritos à *Medição* ou *Faturamento*, sendo redirecionado com mensagem informativa.
* [ ] **CA-06 (Auditoria e Histórico de Transição):** Toda mudança de status gera um registro no histórico do serviço contendo status anterior, novo status e data.

---

## 18. Checklist de Validação do Artefato (CDU)

### 18.1 Estrutura mínima
* [X] Nome do caso de uso iniciado com verbo no infinitivo.
* [X] Objetivo claro, direto e focado no domínio de faturamento/esteira de serviços.
* [X] Tipo do caso de uso informado (Concreto).
* [X] Atores primário e secundário identificados corretamente.
* [X] Precondições e pós-condições registradas.
* [X] Fluxo principal completo com alternâncias entre ator e sistema.
* [X] Fluxos alternativos cobrindo filtros, pendências, tramitações e drawer de detalhamento.
* [X] Fluxos de exceção cobrindo controle de perfil e validações de tela.
* [X] Regras de negócio e requisitos não funcionais mapeados.

### 18.2 Qualidade e Consistência
* [X] Ações descritas no presente do indicativo com linguagem clara e concisa.
* [X] Rastreabilidade completa entre requisitos (RF), passos, elementos de UI e Regras de Negócio (RN).
* [X] Dicionário de dados aderente ao modelo do protótipo e do banco de dados satélite.
