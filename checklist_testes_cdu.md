# 📋 Master Checklist de Testes: Fluxo Completo SIGES (CDU V1, V2 e V3)

Este documento foi consolidado a partir das regras de negócio especificadas nos Manuais de Casos de Uso (CDU V1, V2 e V3). Siga-o passo a passo para garantir que o sistema está 100% robusto em todos os seus ciclos.

---

## 🟢 CDU V1: O Fluxo Essencial do Serviço
*(Testando o clico de vida básico da "Linha de Produção")*

### A. Triagem e Envio para Campo
- [ ] Logue com um usuário de perfil "Programação" ou "Master".
- [ ] Vá na tela de **Medição (01)**.
- [ ] Encontre um serviço com Status 1 (Acompanhamento Obra).
- [ ] Selecione este serviço e o transfira para alguma equipe de campo (Status 2 - Execução Terceiro).
- [ ] **Validação:** Verifique se o serviço saiu da tela de Medição e agora está visível no Cockpit Gerencial / Equipes em Campo.

### B. O Retorno do Campo (Simulação)
- [ ] No Cockpit Gerencial, selecione o serviço que está em campo (Status 2).
- [ ] Retorne este serviço, simulando que a equipe finalizou e entregou o SOB.
- [ ] **Validação:** Verifique se o serviço voltou para o Status 1 na tela de Medição.

### C. Faturamento Básico
- [ ] Na aba Medição, selecione um serviço (Status 1) que esteja com a documentação 100% correta.
- [ ] Aprove a medição e envie para o Status 3 (Faturamento).
- [ ] Vá na aba de Faturamento e confirme o faturamento desse serviço (Status 5 - Finalizado).

---

## 🟡 CDU V2: Tratativas de Pendências e Distribuidora
*(Testando os sub-fluxos, bloqueios e painéis de Pendências)*

### A. Bloqueio de Validação (RN-03)
- [ ] Na tela de Medição, encontre um serviço que possua o selo **"Pendências Ativas"**.
- [ ] Tente enviar esse serviço para Faturamento (Status 3).
- [ ] **Validação:** O sistema deve **bloquear a ação** e exibir a mensagem: *"Bloqueado! Existem pendências ativas que impedem o avanço para validação/faturamento."*

### B. Geração e Tratativa de Pendência Operacional
- [ ] Na tela de Medição, selecione um serviço normal e gere uma **Pendência Operacional (Cosampa)** para ele.
- [ ] Vá até o menu **04. Pendências** -> Sub-aba **Operacional**. O serviço deve aparecer aqui.
- [ ] Selecione o serviço e clique para tratar. Simule a resolução da pendência.
- [ ] **Validação:** Se era a única pendência, o sistema deve liberar o serviço para seguir o fluxo.

### C. Fluxo de Pendência Distribuidora (Enel/Equatorial)
- [ ] Na tela de Medição, selecione um serviço e envie ele para **Pendências Distribuidora** (Status 4).
- [ ] Ao enviar, observe se aparece o alerta confirmando o envio.
- [ ] Vá até o menu **04. Pendências** -> Sub-aba **Distribuidora (Equatorial/Enel)**.
- [ ] **Validação:** Confirme que o serviço está lá e não sumiu no "limbo".
- [ ] Verifique se o "Mês Inicial de Medição" dele foi congelado na competência correta para não prejudicar as metas.

### D. Checkbox Mestre (O Bug Corrigido)
- [ ] Dentro do modal de Tratativas, clique no checkbox mestre para "Marcar Todos".
- [ ] Clique novamente para desmarcar.
- [ ] **Validação:** Ele deve desmarcar todos os itens corretamente.

---

## 🔵 CDU V3: Importador Dinâmico e Auditoria
*(Testando a automação em massa e rastreabilidade)*

### A. O Upload e o Cabeçalho
- [ ] Clique no botão de Importar Planilha.
- [ ] Envie um arquivo Excel real.
- [ ] **Passo 1:** Verifique se ele lê as abas corretamente.
- [ ] **Passo 2 (Teste Crítico):** Verifique se o sistema mostra *todas* as linhas, incluindo a linha 0, e se ao selecionar a linha 0, ele adota seus valores como nome das colunas reais (sem engolir nada).

### B. O Mapeamento Seguro
- [ ] **Passo 3:** Tente sincronizar deixando o `Número do Serviço` (Chave) em branco no mapeamento.
- [ ] **Validação:** O sistema DEVE exibir um erro vermelho bloqueando a sincronização.
- [ ] Mapeie o `Número do Serviço` e pelo menos mais um campo (Ex: `Código PEP Obra`).

### C. Sincronização Inteligente (Auto-Sync)
- [ ] Na sua planilha, o número do serviço deve estar sem o prefixo (Ex: apenas `732627`).
- [ ] Clique em "Confirmar e Sincronizar".
- [ ] **Validação Visual:** O modal deve assumir o estado de tela de carregamento completa com o texto "Sincronizando Banco de Dados...".
- [ ] **Validação de Sync:** O sistema deve injetar o "SOB-" sozinho, achar o registro no banco e atualizar os valores de sucesso. O alerta final dirá quantos serviços foram salvos.

### D. Rastreabilidade Suprema (O Log Global)
- [ ] Após finalizar a importação, feche o importador e clique sobre um dos serviços atualizados para abrir seus detalhes (Gaveta lateral).
- [ ] Clique em **"Visualizar Histórico (Auditoria)"**.
- [ ] **Validação:** Deve existir uma linha gerada contendo algo como: *"Importador alterou 'Código PEP Obra' no serviço SOB-732627: De: Vazio Para: PEP-XXXX"*.
- [ ] Abra o terminal do VSCode e rode o comando `.venv\Scripts\python backend\ver_logs.py`.
- [ ] **Validação:** A mesma informação limpa e formatada deve aparecer listada no terminal.
