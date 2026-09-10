# Especificação Técnica: Perfis de Tela e Modo de Edição

Este documento especifica os requisitos de engenharia e regras de negócio para a implementação do sistema de **Perfis de Tela** e **Modo de Edição**, permitindo que os usuários configurem de forma dinâmica quais colunas são exibidas nas tabelas do sistema. O agente de desenvolvimento **antigravity** deverá seguir este documento como especificação técnica oficial.

---

## 1. Visão Geral do Sistema

Atualmente, cada tela do sistema possui uma tabela estática com dados predefinidos. O objetivo deste projeto é introduzir uma camada de customização dinâmica chamada **Perfis de Tela**.

- **Usuários com privilégios administrativos (Master):** poderão criar e gerenciar perfis globais de visualização de colunas, além de gerenciar permissões de acesso.
- **Usuários comuns (sem permissão de criação global):** poderão consumir esses perfis e criar suas próprias derivações privadas de visualização, aumentando a usabilidade e flexibilidade operacional.

---

## 2. Atores do Sistema

- **Usuário Master (Com Permissão de Criação):** Administrador com permissão de escrita e edição em perfis globais e controle de gestão de acessos.
- **Usuário Comum (Sem Permissão de Criação):** Usuário final que pode visualizar perfis globais e criar/salvar suas próprias derivações privadas.
- **Agente Executor (antigravity):** Motor de desenvolvimento responsável por implementar rotas, banco de dados e interfaces especificadas.

---

## 3. Requisitos Funcionais (RF)

| ID | Nome | Descrição | Prioridade |
| :--- | :--- | :--- | :--- |
| **RF01** | Gestão de Perfis de Tela (Global) | Permitir que o Usuário Master crie, edite e salve perfis de visualização de colunas para as tabelas. | Alta (Blocos #1 e #2) |
| **RF02** | Controle de Acessos e Permissões na Gestão de Usuários | Disponibilizar na tela de Gestão de Usuários a permissão/flag `"Criar Perfis de Tela"`. | Alta (Bloco #3) |
| **RF03** | Visualização e Consumo de Perfis | Garantir que todos os usuários (com ou sem permissão de criação) consigam selecionar e visualizar os perfis de tela ativos. | Alta (Bloco #4) |
| **RF04** | Interface de Configuração (Modo de Edição) | Disponibilizar uma barra de ferramentas entre a área de filtros e a tabela principal contendo os controles de gerenciamento de perfil. | Alta (Bloco #5) |
| **RF05** | Clonagem/Derivação de Base de Perfil | Ao selecionar um perfil existente e criar um novo, o sistema deve clonar as configurações do perfil ativo como ponto de partida. | Média (Bloco #6) |
| **RF06** | Gestão de Acesso a Perfis Específicos | O Usuário Master poderá definir quais usuários têm acesso a quais perfis globais por meio de dropdown multi-select. | Média (Bloco #7) |
| **RF07** | Derivação de Perfis por Usuário Comum (Privados) | Permitir que o Usuário Comum clone um perfil master, altere as colunas e salve-o como derivação pessoal (Perfil Privado), sem alterar o original. | Média (Bloco #8) |
| **RF08** | Compartilhamento de Perfis Customizados | Permitir que o Usuário Master visualize os perfis privados de todos os usuários na gestão de acessos e os compartilhe com outros membros. | Baixa (Bloco #9) |

---

## 4. Regras de Negócio (RN)

- **RN01 — Imutabilidade de Perfis Globais por Usuários Comuns:** Um usuário sem a permissão `"Criar Perfis de Tela"` não pode, sob hipótese alguma, sobrescrever ou salvar alterações diretamente em um perfil global criado por um Usuário Master.
- **RN02 — Escopo de Escrita (Derivação):** Quando um Usuário Comum altera as colunas de um perfil global, a ação de salvar deve obrigatoriamente acionar a criação de uma cópia local/privada do perfil (ex.: `"Perfil Master [Cópia de Usuário]"`).
- **RN03 — Herança Base de Configuração:** Todo novo perfil criado deve herdar a configuração do perfil ativo no momento do acionamento de `"+ Adicionar Novo Perfil"`. Caso nenhum perfil esteja selecionado, deve herdar a visualização padrão (*default*) da aplicação.
- **RN04 — Visibilidade de Perfis na Gestão:** O Usuário Master terá uma seção dedicada denominada `"Perfis Custom de Usuários"` no seletor de permissões de perfil para gerenciar e auditar perfis privados criados por usuários comuns.

---

## 5. Especificação de Interface (UI/UX)

A barra de controle de perfis deve ser posicionada horizontalmente **entre o bloco de filtros e a tabela de dados**, contendo os seguintes elementos na ordem descrita:

1. **Seletor de Perfil (Dropdown):**
   - Lista todos os perfis ativos disponíveis para o usuário autenticado.
   - Ao final da lista, exibe uma opção fixa: `"+ Adicionar Novo Perfil"` (ou campo de input embutido) para iniciar o fluxo de criação.
2. **Seletor de Colunas (Dropdown com Checkboxes):**
   - Lista todas as colunas disponíveis na tabela atual.
   - Usuário marca/desmarca os checkboxes para ocultar ou exibir colunas em tempo real reativamente.
3. **Botão "Salvar":**
   - **Usuário Master:** Salva as alterações diretamente no perfil global selecionado.
   - **Usuário Comum:** Exibe modal de confirmação para salvar como um "Perfil Privado Derivado".

### Estrutura do Menu de Gestão de Acessos (Visão do Administrador)
Na área de administração/gestão de usuários:
- Dropdown com a listagem de perfis do sistema.
- Cada item do dropdown possui checkboxes para associação de múltiplos usuários.
- Seção inferior expansível: `"Perfis Custom de Usuários"`, exibindo os perfis privados criados pelos usuários comuns para permitir compartilhamento com a equipe.

---

## 6. Casos de Uso (CDU)

### CDU-01: Criar e Derivar Perfis de Tela
- **Ator Principal:** Usuário (Master ou Comum)
- **Pré-condições:** Usuário autenticado na plataforma.

#### Fluxo Principal (Usuário Master)
1. O usuário acessa a tela de listagem de dados.
2. Na barra de perfis (entre filtros e tabela), clica no **Seletor de Perfil** e seleciona o `"Perfil Padrão"`.
3. O usuário altera as colunas ativas utilizando o **Seletor de Colunas (Checkbox)**.
4. O usuário clica na opção `"+ Adicionar Novo Perfil"` no final do seletor.
5. O sistema gera um novo perfil temporário herdando a visibilidade configurada no passo 3.
6. O usuário insere um nome para o novo perfil e clica em **Salvar**.
7. O sistema persiste o perfil globalmente e o disponibiliza para os usuários selecionados na gestão de acessos.

#### Fluxo Alternativo A (Usuário Comum criando perfil derivado)
1. O Usuário Comum seleciona um perfil global existente (ex.: `"Perfil Financeiro"`).
2. O usuário desmarca 2 colunas no **Seletor de Colunas**.
3. Ao clicar em **Salvar**, o sistema detecta que o usuário não possui permissão de escrita no perfil global.
4. O sistema exibe o modal: *"Você está alterando um perfil público. Salve como um perfil privado para manter suas alterações."* com um campo de texto para o nome do novo perfil.
5. O usuário informa `"Meu Perfil Financeiro"` e confirma.
6. O sistema salva o perfil como de propriedade exclusiva do usuário comum (tipo `privado`).

---

## 7. Critérios de Aceite para o Agente antigravity

### Back-end e Banco de Dados
- [ ] Criar tabela `perfis_tela` contendo os campos:
  - `id`
  - `nome`
  - `colunas_visiveis` (JSON / Array)
  - `criado_por_id`
  - `tipo` (`global` ou `privado`)
- [ ] Criar tabela de relacionamento para gestão de acesso: `perfil_tela_usuario`.
- [ ] Adicionar flag booleana `criar_perfis_tela` no schema de permissões do usuário.
- [ ] Implementar políticas de segurança na API (RBAC) garantindo que usuários comuns não possam atualizar registros com `tipo = 'global'`.

### Front-end e UI/UX
- [ ] Implementar a barra de ferramentas posicionada entre os filtros e a grid de dados.
- [ ] Configurar reatividade imediata na tabela ao marcar/desmarcar checkboxes de colunas.
- [ ] Ao clicar em `"+ Adicionar Novo Perfil"` a partir de um perfil selecionado, herdar integralmente a seleção de colunas ativa.
- [ ] Implementar dropdown multi-select na tela de gestão de usuários com a seção expansível `"Perfis Custom de Usuários"`.