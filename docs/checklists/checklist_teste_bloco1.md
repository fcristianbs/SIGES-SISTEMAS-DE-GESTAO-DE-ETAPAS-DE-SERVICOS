# 🧪 Checklist de Testes do Bloco 1 (Infraestrutura e Performance)

Este checklist serve para você testar e validar pessoalmente se o Bloco 1 foi implementado com sucesso na aplicação rodando no seu ambiente local. 

---

## 1. Teste de Persistência de Sessão (LocalStorage)
*Objetivo: Garantir que a interface retenha as escolhas do usuário após uma atualização da página.*

- `[x]` Acesse a página inicial (Gerencial ou Medição).
- `[x]` Na barra superior de filtros, altere o **Contrato** (ex: para "MULTISERVICOS SUL").
- `[x]` Mude para a **página 2** (ou qualquer outra) na tabela de serviços lá no final da tela.
- `[x]` **Pressione F5** (Atualizar a página).
- `[x]` **Validação:** A barra de filtros deve permanecer com o contrato que você escolheu.
- `[x]` **Validação:** A paginação deve continuar exibindo a página 2 (veja a indicação de paginação no final da tabela).

## 2. Teste de Lazy Loading e Paginação (Server-Side)
*Objetivo: Garantir que o sistema só carregue a amostragem necessária sem congelar o navegador.*

- `[x]` Abra o **Console do Navegador (F12) -> Aba Network (Rede)**.
- `[x]` Atualize a página e clique no endpoint `/api/servicos` que vai aparecer na lista de requisições.
- `[x]` **Validação 1:** Clique na aba `Payload` ou observe a URL. Ela deve conter os parâmetros `skip=0` e `limit=10`.
- `[x]` **Validação 2:** Clique na aba `Preview` ou `Response`. O retorno não deve ser uma lista solta de itens, mas sim um objeto contendo:
  ```json
  {
    "data": [ ... 10 itens ... ],
    "total": X (onde X é o número total real de serviços no seu banco)
  }
  ```
- `[x]` Clique no botão **"Próxima »"** ou no botão "2" na tabela. 
- `[x]` Verifique a aba Network novamente: Uma nova requisição deve ser feita para `/api/servicos`, desta vez com `skip=10`.

## 3. Teste de Integridade dos KPIs do Dashboard
*Objetivo: Garantir que mesmo a tabela puxando apenas 10 linhas, os gráficos continuam lendo a totalidade do banco.*

- `[x]` Vá para a tela Inicial / Gerencial.
- `[x]` Observe os cards superiores, especificamente o valor do card **"Serviços na Esteira"**.
- `[ ]` **Validação:** O número do card "Serviços na Esteira" deve refletir o total geral de serviços no seu banco (ex: 2.000), e **NÃO** o número 10 (que é o que está carregado na tabela).
- `[ ]` Observe o gráfico de "Serviços por Status". As barras coloridas não devem representar as quantidades apenas dos 10 serviços visíveis, mas a contagem total de todos os registros reais.

## 4. Teste de Filtragem Direcionada (status_in)
*Objetivo: Garantir que a paginação server-side saiba isolar contextos de página.*

- `[ ]` Navegue pelo menu lateral e clique em **02. Pendências**.
- `[ ]` Aperte F12 para ver a aba Network novamente e observe a chamada para `/api/servicos`.
- `[ ]` **Validação:** A URL deverá conter o parâmetro `status_in=2,4,6,7`. Isso prova que o backend puxou do banco de dados 10 registros que *obrigatoriamente* são pendências operacionais ou da distribuidora.

---

> [!TIP]
> **Como testar rapidamente:** Rode seu backend com `python backend/main.py` (ou Flask), e abra o frontend no seu navegador local. Faça os passos acima. Se todos estiverem com o comportamento esperado, o Bloco 1 está homologado e robusto!
