# 🧪 Checklist de Testes do Bloco 1 (Infraestrutura e Performance)

Este checklist serve para você testar e validar pessoalmente se o Bloco 1 foi implementado com sucesso na aplicação rodando no seu ambiente local. 

---

## 1. Teste de Persistência de Sessão (LocalStorage)
*Objetivo: Garantir que a interface retenha as escolhas do usuário após uma atualização da página.*

- [x] Acesse a página inicial (Gerencial ou Medição).
- [x] Na barra superior de filtros, altere o **Contrato** (ex: para "MULTISERVICOS SUL").
- [x] Mude para a **página 2** (ou qualquer outra) na tabela de serviços lá no final da tela.
- [x] **Pressione F5** (Atualizar a página).
- [x] **Validação:** A barra de filtros deve permanecer com o contrato que você escolheu.
- [x] **Validação:** A paginação deve continuar exibindo a página 2 (veja a indicação de paginação no final da tabela).

## 2. Teste de Lazy Loading e Paginação (Server-Side)
*Objetivo: Garantir que o sistema só carregue a amostragem necessária sem congelar o navegador.*

- [x] Abra o **Console do Navegador (F12) -> Aba Network (Rede)**.
- [x] Atualize a página e clique no endpoint `/api/servicos` que vai aparecer na lista de requisições.
- [x] **Validação 1:** Clique na aba `Payload` ou observe a URL. Ela deve conter os parâmetros `skip=0` e `limit=10`.
- [x] **Validação 2:** Clique na aba `Preview` ou `Response`. O retorno não deve ser uma lista solta de itens, mas sim um objeto contendo:
  ```json
  {
    "data": [ ... 10 itens ... ],
    "total": X (onde X é o número total real de serviços no seu banco)
  }
  ```

- [x] Clique no botão **"Próxima »"** ou no botão "2" na tabela. 
- [x] Verifique a aba Network novamente: Uma nova requisição deve ser feita para `/api/servicos`, desta vez com `skip=10`.

## 3. Teste de Integridade dos KPIs do Dashboard
*Objetivo: Garantir que mesmo a tabela puxando apenas 10 linhas, os gráficos continuam lendo a totalidade do banco.*

- [x] Vá para a tela Inicial / Gerencial.
- [x] Observe os cards superiores, especificamente o valor do card **"Serviços na Esteira"**.
- [ ] **Validação:** O número do card "Serviços na Esteira" deve refletir o total geral de serviços no seu banco (ex: 2.000), e **NÃO** o número 10 (que é o que está carregado na tabela).
- [ ] Observe o gráfico de "Serviços por Status". As barras coloridas não devem representar as quantidades apenas dos 10 serviços visíveis, mas a contagem total de todos os registros reais.

## 4. Teste de Filtragem Direcionada (status_in)
*Objetivo: Garantir que a paginação server-side saiba isolar contextos de página.*

- [ ] Navegue pelo menu lateral e clique em **02. Pendências**.
- [ ] Aperte F12 para ver a aba Network novamente e observe a chamada para `/api/servicos`.
- [ ] **Validação:** A URL deverá conter o parâmetro `status_in=2,4,6,7`. Isso prova que o backend puxou do banco de dados 10 registros que *obrigatoriamente* são pendências operacionais ou da distribuidora.

---

> [!TIP]
> **Como testar rapidamente:** Rode seu backend com `python backend/main.py` (ou Flask), e abra o frontend no seu navegador local. Faça os passos acima. Se todos estiverem com o comportamento esperado, o Bloco 1 está homologado e robusto!


---

# Checklist de Validação: Bloco 2 (Motor Colaborativo)

Este checklist serve como registro formal de testes para homologar as entregas do Bloco 2. Realize os passos abaixo no navegador e marque as caixas após validar.

## 1. Teste de Acesso e Carregamento (Drawer)
*Objetivo: Validar se a interface da Timeline foi corretamente anexada ao painel de detalhes do serviço.*

- [x] Atualize a página do sistema (F5).
- [x] Clique em qualquer serviço na tabela (ex: tela Gerencial ou Medição) para abrir o Painel Lateral (Drawer).
- [x] Role a aba até encontrar a nova seção **"💬 Timeline & Comentários"**.
- [x] **Validação:** A timeline deve exibir o indicador de carregamento (spinner) por uma fração de segundo e logo após exibir "Nenhuma interação registrada nesta SOB" (caso seja a primeira vez abrindo este serviço) sem exigir nenhum clique adicional.

## 2. Teste de Gravação e Persistência (Backend)
*Objetivo: Garantir que os dados digitados estão sendo gravados de forma permanente e imutável no banco de dados.*

- [x] No mesmo serviço aberto, vá até a caixa de texto da Timeline e digite uma mensagem de teste (ex: "Iniciando a reanálise financeira deste contrato.").
- [x] Clique no botão **"Enviar"**.
- [x] **Validação 1:** A mensagem deve aparecer imediatamente na lista logo acima, exibindo seu nome, data e hora. A caixa de texto deve ficar limpa.
- [x] Feche o Painel Lateral (clicando no 'X' no canto superior).
- [x] Clique **no mesmo serviço** para reabrir o Painel.
- [x] **Validação 2:** O comentário feito anteriormente deve ser carregado com sucesso automaticamente assim que abrir o painel, provando a persistência no banco de dados MySQL.

## 3. Teste do Formatador Visual de Menções (Regex)
*Objetivo: Garantir que a lógica de texto identifica blocos iniciados com '@' e os transforma em tags de destaque visual.*

- [x] Na caixa de texto da Timeline, digite um comentário simulando uma notificação (ex: "Por favor, verificar documentação @joao_silva").
- [x] Clique em **"Enviar"**.
- [x] **Validação:** O comentário deve aparecer na lista e o termo `@joao_silva` deve ser renderizado como um "badge" destacado (fundo azul claro, texto em azul escuro/negrito), diferenciando-o do resto da frase.

## 4. Teste de Segregação por Serviço
*Objetivo: Garantir que comentários de um serviço não "vazem" para outro.*

- [x] Feche o Painel Lateral atual (onde você deixou 2 comentários de teste).
- [x] Clique em um **outro serviço diferente** na tabela para abrir o Painel Lateral dele.
- [x] Role até a Timeline.
- [x] **Validação:** O sistema deve carregar e exibir "Nenhuma interação registrada nesta SOB". Os comentários feitos no serviço anterior não devem aparecer aqui.


---

# Checklist de Validação: Bloco 3 (Módulo de Pendências)

Este checklist serve como registro formal de testes para homologar as entregas do Bloco 3. Realize os passos abaixo no navegador e marque as caixas após validar.

## 1. Teste de Hierarquia Automática (Gestão de Visão)
*Objetivo: Validar se o sistema impõe filtros iniciais baseados no cargo.*

- [x] Acesse o sistema e no topo mude o Perfil de 'Master' para 'Supervisor' ou 'Coordenador'.
- [x] Atualize a página (F5).
- [x] **Validação:** Na barra de filtros, a caixa "Supervisores (RN-05)" ou "Coordenadores (RN-05)" deve aparecer pré-selecionada com o seu nome (ex: "👑 Carlos Eduardo" ou "👤 Roberto Santos"), mostrando apenas os serviços subordinados a você.
- [x] Clique na caixa de filtro que foi pré-selecionada e altere para "Todos" (Limpar Filtro).
- [x] **Validação:** O sistema deve obedecer e voltar a exibir a visão global da filial.

## 2. Teste de Parâmetros Dinâmicos (Banco de Dados)
*Objetivo: Validar se as caixinhas de erro não são mais fixas no código.*

- [x] Acesse a aba **Medição (01)** pelo menu lateral esquerdo.
- [x] Selecione pelo menos 1 serviço (marcando a caixinha à esquerda da linha).
- [x] Na caixa cinza à direita, desça até **Pendência Cosampa (Status 02)** e **Pendência Distribuidora (Status 04)**.
- [x] **Validação:** As caixinhas de seleção (checkboxes) agora devem listar categorias como "Fotos", "Materiais" e "Documentação". Estas vêm diretamente do banco de dados (tabela `itens_correcao_cosampa`).

## 3. Teste de Reprogramação e SLA
*Objetivo: Testar a esteira de ida e volta da Pendência e as travas de reprogramação.*

- [x] Ainda na tela de **Medição (01)**, selecione um serviço.
- [x] Marque um dos erros (ex: "Sem evidência do serviço").
- [x] Clique em **"Gerar Pendência Cosampa (02)"**. O serviço vai sumir da tela.
- [x] No menu lateral, clique em **Pendências (02/04)**.
- [x] Ache o serviço que você enviou e clique nele.
- [x] **Validação 1:** No painel lateral direito (Drawer), o status deve ser laranja (02. Pendências Operacionais) e deve ter um balão vermelho apontando ⏳ **Atraso SLA: X dias**.
- [x] Marque a caixinha "Necessita Reprogramar Visitada em Campo".
- [x] Tente clicar no botão azul embaixo "Salvar Tratativa & Retorno Automático" **sem colocar a data**.
- [x] **Validação 2:** O sistema deve barrar com um alerta dizendo "Preencha a Data da Programação...".
- [x] Coloque uma data no campo de Reprogramação e clique no botão azul novamente.
- [x] **Validação 3:** O serviço deve sumir da tela e voltar para **Medição (01)**, salvando as informações.


---

# Checklist de Validação: Bloco 4 (Fluxos de Tela 01 e Lotes Inteligentes)

Este checklist serve como registro formal de testes para homologar as entregas do Bloco 4. Realize os passos abaixo no navegador e marque as caixas após validar.

## 1. Teste de Validação de Sistema de Origem (Trava da Tela 01)
*Objetivo: Impedir que serviços avancem sem a confirmação do sistema de origem.*

- [ ] Na aba **Medição (01)**, selecione um serviço que possua o campo "Sistema de Origem" vazio ou não validado.
- [ ] Tente tramitá-lo para qualquer status usando a barra de ferramentas em lote ou o painel lateral.
- [ ] **Validação 1:** O sistema deve bloquear a ação e exibir um alerta exigindo o preenchimento/confirmação do "Sistema de Origem".
- [ ] Preencha o sistema de origem, salve e tente tramitar novamente.
- [ ] **Validação 2:** O serviço deve tramitar com sucesso.

## 2. Teste do Bypass Comercial (Salto de Status)
*Objetivo: Validar o roteamento customizado para contratos Comerciais.*

- [ ] Na aba **Medição (01)**, encontre ou cadastre um serviço cujo contrato seja **Comercial**.
- [ ] Aprove a medição sem pendências para que o serviço avance.
- [ ] **Validação:** Verifique a timeline ou faça uma busca. O status do serviço deve ter pulado diretamente para o **Status 08 (Faturamento)**, sem passar pelo Status 03 (Fechamento).

## 3. Teste de Lotes Inteligentes (Falha Parcial)
*Objetivo: Garantir que um lote inteiro não falhe se apenas um serviço estiver irregular.*

- [ ] Na aba **Medição (01)**, selecione múltiplos serviços (ex: 3 serviços).
- [ ] Certifique-se intencionalmente de que 1 deles está com um erro bloqueante (ex: falta de preenchimento do Sistema de Origem ou pendência obrigatória não preenchida).
- [ ] Clique em um botão de ação em lote (ex: Enviar Lote para Validação).
- [ ] **Validação 1:** A requisição deve ser concluída sem erro global da API (sem retornar código 500 ou travar a tela).
- [ ] **Validação 2:** O sistema deve exibir um *sumário/toast* claro informando que "2 serviços foram tramitados com sucesso" e "1 falhou (exibindo o motivo do erro na tela)".
- [ ] Confirme que os serviços corretos sumiram da tela (foram tramitados) e o irregular permaneceu.

## 4. Teste de Serviços Irmãos e Hyperlinks
*Objetivo: Validar os refinamentos visuais da Grid da Tela 01.*

- [ ] Na aba **Medição (01)**, observe a tabela que lista os serviços.
- [ ] Identifique serviços que pertencem à mesma Obra/Cliente e ao mesmo Contrato.
- [ ] **Validação 1:** O sistema deve agrupá-res visualmente, destacando a conexão (Serviços Irmãos) - como através de um indicativo visual (ex: ícone de árvore ou indentação/cor agrupada).
- [ ] Observe a coluna correspondente à ID no sistema parceiro (GPM) ou o Número do Serviço.
- [ ] **Validação 2:** Deve existir um link azul/clicável que, ao ser pressionado, simula ou abre uma nova aba direcionada ao GPM.


---

