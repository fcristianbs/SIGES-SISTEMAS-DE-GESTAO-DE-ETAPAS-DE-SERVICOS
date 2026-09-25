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
