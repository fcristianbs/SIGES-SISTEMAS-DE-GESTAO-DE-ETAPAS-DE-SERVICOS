# Checklist de Testes da Esteira SIGES (CDU V2)

Utilize este roteiro prático para validar se todos os fluxos e regras de negócio do novo CDU V2 estão operando corretamente na sua máquina local ou ambiente de testes. 

Siga as etapas marcando cada item validado.

---

## 🛠️ CDU-01 / CDU-02: Tela 01 - Medição (Ações em Lote)

> **Pré-requisito:** Acesse a tela `01. Medição` logado preferencialmente com o perfil de *Fechamento* ou *Master*.

- [ ] **Validação da Tabela Padrão:** Verifique se as colunas da tabela centralizadora exibem corretamente os novos campos combinados: **Serviço e Data** (ex: `10928374 · 2023-10-25`) e **Cliente / Contrato**.
- [ ] **Gerar Pendência Cosampa (Status 02):**
  - [ ] Selecione 1 ou mais serviços no Status `01. Aguardando Conferência`.
  - [ ] No painel direito, marque itens no grupo "Pendência Cosampa (Status 02)", como *Fotos (S/ Evidência...)*.
  - [ ] Clique em **Gerar Pendência Cosampa (02)**.
  - [ ] **Resultado Esperado:** O sistema deve exibir um *toast* de sucesso, a tabela deve atualizar a linha para vermelho (Status 02), e um log de auditoria deve ser gerado no banco.
- [ ] **Gerar Pendência Distribuidora (Status 04):**
  - [ ] Selecione outros serviços no Status `01. Aguardando Conferência`.
  - [ ] No painel direito, marque itens no grupo "Pendência Distribuidora (Status 04)", como *Vozes não cadastradas*.
  - [ ] Clique em **Gerar Pend. Distribuidora (04)**.
  - [ ] **Resultado Esperado:** O status do serviço deve migrar para `04. Pendências Distribuidora` (cor amarelada/laranja).

---

## 🛑 CDU-04 / CDU-05: Tela 02 - Pendências (Tratativas)

> **Pré-requisito:** Acesse a tela `02. Pendências` para testar os retornos automáticos e travas operacionais.

- [ ] **Tratativa de Pendência Operacional Cosampa:**
  - [ ] Clique na linha de um serviço no Status `02` (gerado no teste anterior). A gaveta lateral se abrirá.
  - [ ] Localize o quadro "Itens de Correção Cosampa (RN-04)".
  - [ ] Preencha a justificativa em texto e marque todos os itens como **"TRATADO"**.
  - [ ] Clique em **Salvar Tratativa de Campo**.
  - [ ] **Resultado Esperado:** Assim que 100% dos itens estiverem tratados, a SOB deverá retornar automaticamente para o Status `01. Aguardando Conferência`.
- [ ] **Tratativa de Pendência Distribuidora:**
  - [ ] Abra a gaveta de um serviço no Status `04`. O título deverá refletir "Itens de Correção Distribuidora".
  - [ ] Marque os itens como "TRATADO" e salve.
  - [ ] **Resultado Esperado:** O serviço não deve voltar para o Status 01, mas sim avançar de forma direta para o Status `03. Aguard. Envio p/ Validação`.
- [ ] **Teste de Bloqueio (Travamento RN-03):**
  - [ ] Abra a gaveta de um serviço no Status `02` ou `04`.
  - [ ] No bloco "Tramitar Status (CDU-01 / RN-03)", tente forçar a alteração direta para Status `03` ou `05` **sem** tratar os itens.
  - [ ] **Resultado Esperado:** O sistema (backend) deve barrar a ação exibindo o alerta de que existem pendências ativas impedindo o avanço.

---

## ✅ CDU-06: Tela 03 - Validação (Aprovação ou Rejeição)

> **Pré-requisito:** Localize ou tramita manualmente uma SOB para o Status `05. Aguard. Validação do Cliente` e abra sua gaveta de Detalhamento.

- [ ] **Aprovar Medição e Registrar Data:**
  - [ ] Observe que a gaveta renderizou o novo quadro verde "Aprovar Medição (Cliente)".
  - [ ] Clique no botão cinza **Hoje**. Verifique se o campo "Data da 1ª Validação" foi preenchido automaticamente com a data de hoje.
  - [ ] Clique em **Aprovar Medição**.
  - [ ] **Resultado Esperado:** O serviço tramita para `08. Validado — Aguard. Autorização`, sumindo do Status 05, e a data é persistida no banco de dados.

---

## 💸 CDU-03: Conciliação Financeira e Disputas (Status 11, 12, 13)

> **Pré-requisito:** Force o avanço de um serviço qualquer na gaveta para o Status `11. Conciliado c/ Divergências`. Após recarregar, abra a gaveta deste serviço novamente.

- [ ] **Status 11: Analisar Divergência e Cobrar:**
  - [ ] Verifique se a gaveta exibe o **Comparativo Financeiro-Operacional** (blocos Valor Executado vs. Valor Pago).
  - [ ] Preencha o campo de "Justificativa da Divergência da Conciliação".
  - [ ] Clique em **Cobrar Cliente (Ir p/ 12)**.
  - [ ] **Resultado Esperado:** O serviço deve tramitar para o Status 12 e salvar a justificativa digitada.
- [ ] **Status 12: Mês de Reapresentação:**
  - [ ] Abra novamente a gaveta deste mesmo serviço (agora no Status 12).
  - [ ] A interface deverá exibir o quadro roxo "Mês de Reapresentação". Selecione um mês/ano no calendário.
  - [ ] Clique em **Iniciar Disputa (Avança p/ 13)**.
  - [ ] **Resultado Esperado:** O serviço migra para o Status 13, fechando o ciclo de disputa financeira.

---

## 📜 Log de Auditoria Global (RN-01)

- [ ] **Checar Rastros no BD:** 
  - [ ] Na gaveta de qualquer serviço que você tramitou nos testes acima, desça até a última aba ("Histórico de Auditoria") e clique em **Carregar Logs**.
  - [ ] **Resultado Esperado:** Devem estar listadas todas as mudanças de `status_id` que ocorreram, bem como os novos campos `divergencia_conciliacao`, `data_primeira_validacao` e `mes_reapresentacao` que foram editados na seção de Conciliação e Validação.
