# Manual do Usuário - WebPlan

Bem-vindo ao **WebPlan - Torre de Controle Operacional**. Este manual foi criado para ajudar você a entender o conceito por trás da ferramenta e, principalmente, como utilizá-la no seu dia a dia para registrar e acompanhar impedimentos.

---

## 1. O Conceito Base
O WebPlan foi desenhado para gerenciar **Impedimentos**. 
Um impedimento é qualquer problema que faça uma equipe de campo parar de trabalhar ou perder eficiência (exemplo: *veículo quebrado, falta de material, chuva, equipamento em manutenção*). 

O sistema permite que você:
- **Registre** o que aconteceu e com qual equipe.
- **Calcule** automaticamente quanto tempo foi perdido e o impacto financeiro dessa parada.
- **Acompanhe** o SLA (Prazo) de solução do responsável pela tratativa.

---

## 2. Acesso à Plataforma
1. Acesse o link da plataforma no seu navegador.
2. Na tela de login, insira seu **E-mail Corporativo Autorizado**.
3. **Não há necessidade de senha no momento**, o controle é feito pela lista de e-mails permitidos.
   - *Se o sistema informar que você não tem acesso, solicite o cadastro a um Gestor (Perfil Master).*

Existem dois tipos de perfis:
- **Operador:** Preenche e edita a planilha de impedimentos.
- **Master:** Faz tudo que o Operador faz + adiciona novos usuários + cadastra novas opções (equipes, causas, departamentos).

---

## 3. O Painel e a Planilha

Ao entrar, você verá seus Projetos/Planilhas. Clique em **"Acessar Planilha"** no projeto da Torre de Controle.

### Inserindo um Impedimento
A tela da planilha se parece muito com o Excel, mas é toda conectada ao banco de dados em tempo real.
1. No canto superior direito, clique no botão azul **"+ Inserir Novo Registro"**.
2. Uma nova linha aparecerá.
3. Preencha os dados da **esquerda para a direita**.

> [!IMPORTANT]  
> **Salvamento Automático:** Não procure um botão de "Salvar". Sempre que você digitar algo em um campo e clicar fora dele (ou trocar uma opção na lista), o sistema salva sozinho. Um indicador no topo direito mostrará **"Sincronizado"**.

### Dicas de Preenchimento (Usabilidade)

- **Cálculo de Horas e Dinheiro:**
  Ao preencher a `Data/Hora Início` e a `Data/Hora Solução`, a coluna **"Tempo Indisponível"** será calculada sozinha. O sistema também usará a coluna `Valor/Dia` para calcular o **"Impacto Financeiro"**.

- **Filtros Inteligentes (Cascata):**
  Na seção "Processo Impactado", a ordem importa! Se você selecionar o `Departamento` primeiro, as colunas seguintes (`Centro de Serviço`, `Equipe`, `Gestor`) vão exibir **apenas** as opções que pertencem àquele departamento, facilitando muito a sua busca.

- **Chamado e Data do Chamado:**
  Para registrar os tickets abertos junto às áreas de apoio (como Frota ou TI), utilize as colunas `Chamado` e `Data Chamado` localizadas na área de "O Problema".

- **SLA Automático:**
  Preencha a coluna `Prazo Ação` (quando o problema deveria ser resolvido). O sistema comparará essa data com o dia de hoje (ou com a `Data Conclusão`) e marcará a coluna de SLA com cores: **Verde (No Prazo)** ou **Vermelho (Atrasado)**.

---

## 4. Configurações Avançadas (Apenas Perfil Master)

Se você possui perfil Master, você tem duas responsabilidades adicionais vitais para manter o sistema limpo:

### A. Gerenciar Data Sources (Opções da Planilha)
Ao lado da aba "Planilha", existe a aba **"Data Sources"**.
Aqui você cadastra e desativa os itens que aparecem nas listas suspensas (dropdowns) da planilha.

- **Não apague, desative:** Se uma Equipe ou Supervisor foi desligado, **não** os exclua (para não quebrar o histórico). Apenas desligue a "chavinha" de ativo. A opção sumirá das opções de seleção da planilha, mas os registros antigos continuarão mostrando o nome correto.
- **Adicionando novas:** Selecione a categoria no menu esquerdo (ex: *Causa Primária*), clique em "Nova Opção" e digite o nome. Ela aparecerá instantaneamente para todos os operadores.

### B. Gestão de Usuários
No topo da página, clique no link **Usuários**.
- Para liberar um acesso, clique em **Novo Colaborador**, informe o nome e o e-mail, e defina se ele será Operador ou Master.
- Para revogar o acesso de alguém, clique em editar e desligue a permissão de acesso, ou clique no ícone vermelho de lixeira.
