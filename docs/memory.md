# Memória e Contexto do Projeto - SIGES

Esta nota central atua como o mapa mental e histórico do projeto **SIGES (Sistema de Gestão de Etapas de Serviços)**. Use a visualização de gráfico do Obsidian para navegar.

## 🎯 Objetivo do Projeto
- Sistema web completo (Flask + Vanilla JS) para gerenciar o ciclo de vida e etapas das SOBs (Ordens de Serviço).
- Permite controle avançado de fluxo em esteira: Triagem, Execução, Pendências, Faturamento.
- Contempla um **Sistema Inteligente de Importação e Sincronização Dinâmica (Auto-Sync)** de planilhas externas (Excel/CSV) com a base de dados centralizada (MySQL), poupando trabalho manual através do mapeamento De-Para inteligente.

## 📖 Casos de Uso e Regras de Negócio (CDUs)
Navegue pela evolução da nossa engenharia de software através das documentações vinculadas:
- [[CDU]]: Documentação base inicial. Onde definimos a estrutura raiz do fluxo de Medição, Cockpit, Status e regras universais.
- [[CDU V2]]: Evolução dos requisitos. Introduziu regras complexas como a aba exclusiva de Pendências Distribuidora, trava contra avanços indevidos e tratativas pontuais.
- [[CDUV3]]: Especificação técnica atualizada do poderoso Importador Inteligente (CDU-08), com foco em segurança, painel UI dinâmico, ignorar células em branco e o Motor Global de Auditoria. Define os perfis: [[Analista de Fechamento]] e [[Administrador Master]].

## 🤖 Regras para o Antigravity (Meu Comportamento)
1. Antes de gerar código ou propor soluções para importação, consulte sempre a especificação atual em [[CDUV3]].
2. Para lógicas de bloqueio ou distribuição de abas, respeite fielmente o definido no [[CDU V2]].
3. Ao criar ou alterar telas de upload, mapeamento de colunas ou sincronização, valide se as permissões de acesso respeitam os perfis definidos no sistema.
4. Antes de apagar arquivos de código, tenha atenção máxima às rotas do Flask importadas globalmente no `main.py`.
5. **Todas as alterações e novas decisões devem ser registradas aqui ou em uma nota vinculada para nutrir essa rede do Obsidian.**

## 🛠️ Tecnologias e Pilha Ativa
- **Backend:** Python, Flask, Pandas, PyMySQL
- **Banco de Dados:** MySQL Hospedado (via `.env`)
- **Frontend:** Vanilla JavaScript, HTML5 puro, CSS sem frameworks.
- **Gerenciador de Dependências:** `requirements.txt` sob `.venv`
