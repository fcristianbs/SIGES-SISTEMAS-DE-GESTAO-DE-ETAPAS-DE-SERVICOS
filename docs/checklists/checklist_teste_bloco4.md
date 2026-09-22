# Checklist de Validação: Bloco 4 (Fluxos de Tela 01 e Lotes Inteligentes)

Este checklist serve como registro formal de testes para homologar as entregas do Bloco 4. Realize os passos abaixo no navegador e marque as caixas após validar.

## 1. Teste de Validação de Sistema de Origem (Trava da Tela 01)
*Objetivo: Impedir que serviços avancem sem a confirmação do sistema de origem.*

- `[ ]` Na aba **Medição (01)**, selecione um serviço que possua o campo "Sistema de Origem" vazio ou não validado.
- `[ ]` Tente tramitá-lo para qualquer status usando a barra de ferramentas em lote ou o painel lateral.
- `[ ]` **Validação 1:** O sistema deve bloquear a ação e exibir um alerta exigindo o preenchimento/confirmação do "Sistema de Origem".
- `[ ]` Preencha o sistema de origem, salve e tente tramitar novamente.
- `[ ]` **Validação 2:** O serviço deve tramitar com sucesso.

## 2. Teste do Bypass Comercial (Salto de Status)
*Objetivo: Validar o roteamento customizado para contratos Comerciais.*

- `[ ]` Na aba **Medição (01)**, encontre ou cadastre um serviço cujo contrato seja **Comercial**.
- `[ ]` Aprove a medição sem pendências para que o serviço avance.
- `[ ]` **Validação:** Verifique a timeline ou faça uma busca. O status do serviço deve ter pulado diretamente para o **Status 08 (Faturamento)**, sem passar pelo Status 03 (Fechamento).

## 3. Teste de Lotes Inteligentes (Falha Parcial)
*Objetivo: Garantir que um lote inteiro não falhe se apenas um serviço estiver irregular.*

- `[ ]` Na aba **Medição (01)**, selecione múltiplos serviços (ex: 3 serviços).
- `[ ]` Certifique-se intencionalmente de que 1 deles está com um erro bloqueante (ex: falta de preenchimento do Sistema de Origem ou pendência obrigatória não preenchida).
- `[ ]` Clique em um botão de ação em lote (ex: Enviar Lote para Validação).
- `[ ]` **Validação 1:** A requisição deve ser concluída sem erro global da API (sem retornar código 500 ou travar a tela).
- `[ ]` **Validação 2:** O sistema deve exibir um *sumário/toast* claro informando que "2 serviços foram tramitados com sucesso" e "1 falhou (exibindo o motivo do erro na tela)".
- `[ ]` Confirme que os serviços corretos sumiram da tela (foram tramitados) e o irregular permaneceu.

## 4. Teste de Serviços Irmãos e Hyperlinks
*Objetivo: Validar os refinamentos visuais da Grid da Tela 01.*

- `[ ]` Na aba **Medição (01)**, observe a tabela que lista os serviços.
- `[ ]` Identifique serviços que pertencem à mesma Obra/Cliente e ao mesmo Contrato.
- `[ ]` **Validação 1:** O sistema deve agrupá-res visualmente, destacando a conexão (Serviços Irmãos) - como através de um indicativo visual (ex: ícone de árvore ou indentação/cor agrupada).
- `[ ]` Observe a coluna correspondente à ID no sistema parceiro (GPM) ou o Número do Serviço.
- `[ ]` **Validação 2:** Deve existir um link azul/clicável que, ao ser pressionado, simula ou abre uma nova aba direcionada ao GPM.
