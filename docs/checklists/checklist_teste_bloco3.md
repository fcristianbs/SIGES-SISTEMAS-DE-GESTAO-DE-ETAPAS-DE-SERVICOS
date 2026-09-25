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
