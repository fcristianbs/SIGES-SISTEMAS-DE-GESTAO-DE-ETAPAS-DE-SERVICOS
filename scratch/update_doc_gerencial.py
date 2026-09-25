import os

doc_path = os.path.join(os.path.dirname(__file__), "..", "docs", "checklists", "relatorio_executivo_gerencial_cdu_v5.md")

with open(doc_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """## 7. Visão dos Próximos Passos: Módulo Financeiro e Conciliação (Bloco 5)

Abaixo está o quadro das funcionalidades planejadas para o **Bloco 5**, que completará o ciclo ponta a ponta do faturamento até o recebimento:

| Status | Módulo / Funcionalidade | Objetivo Operacional e de Negócio | Etapa Prevista |
| :---: | :--- | :--- | :---: |
| ⏳ **[ ]** | **Telas de Gestão de Faturamento (Telas 04 e 05)** | Telas dedicadas para fechamento com a Distribuidora, controle de datas de validação e emissão de notas fiscais (Status 08 ao 13). | **Bloco 5** |
| ⏳ **[ ]** | **Conciliação Automática de Pagamentos** | Importação da planilha de pagamento da Distribuidora com confronto automático: ordens 100% batidas vão para "Finalizado", divergências são isoladas para análise. | **Bloco 5** |
| ⏳ **[ ]** | **Comparador Dinâmico de Valores (Status 11)** | Interface comparando `Valor Medido vs. Valor Pago` por item de serviço para justificar e contestar cortes da Distribuidora. | **Bloco 5** |
| ⏳ **[ ]** | **Gestão de Disputas e Glosas (Status 12 e 13)** | Acompanhamento de recursos e cobrança de serviços pagos a menor para recuperação de receita contratual. | **Bloco 5** |

---

## 📊 Síntese Executiva de Maturidade do Projeto

* **Bloco 1 (Performance e Infraestrutura):** 100% Concluído e em Produção.
* **Bloco 2 (Comunicação e Linha do Tempo):** 100% Concluído e em Produção.
* **Bloco 3 (Pendências Operacionais e Prazos SLA):** 100% Concluído e em Produção.
* **Bloco 4 (Automação da Medição e Lotes Inteligentes):** 100% Concluído e Homologado.
* **Recursos Transversais (Perfis, Segurança, Auditoria e Carga):** 100% Concluídos.
* **Status Geral da Solução:** **80% do escopo total concluído**, com toda a esteira operacional, de campo e medição blindada e validada."""

replacement = """## 7. Módulo Financeiro, Faturamento e Conciliação Automática (Bloco 5)
*Objetivo Gerencial: Garantir o fechamento financeiro, a conciliação automatizada de recebimentos com a Distribuidora e a recuperação ativa de receitas glosadas.*

### [x] 7.1 Validação Formal de Faturamento e Competência Financeira
* **Como Funciona na Prática:**
  * O sistema exige obrigatoriamente a confirmação da **Data de Validação** para autorizar o avanço dos serviços do Status 08 para o faturamento (Status 09), além da atribuição do **Mês de Emissão** (competência `MM/AAAA`).
  * Permite validar dezenas de serviços faturados simultaneamente via barra de ferramentas superior.
* **Ganho Operacional / Objetivo:**
  * Disciplina financeira e auditoria contábil: nenhuma ordem é enviada para cobrança ou conciliação sem data oficial de validação e competência formalmente definidas.

### [x] 7.2 Fotografia Instantânea Pré-Fechamento ("Relatório ANTES")
* **Como Funciona na Prática:**
  * Antes de qualquer importação de arquivos de retorno bancário ou pagamento da Distribuidora, o sistema gera automaticamente um **Snapshot Imutável**.
  * Esse registro grava a fotografia exata do lote (ordens, valores faturados, status original e clientes).
* **Ganho Operacional / Objetivo:**
  * Rastreabilidade e blindagem jurídica: preserva o histórico de cobrança original, permitindo comprovar a qualquer momento o valor cobrado antes de qualquer glosa aplicada pela Distribuidora.

### [x] 7.3 Fechamento Automático de Pagamentos (Confronto Transacional)
* **Como Funciona na Prática:**
  * O sistema cruza os valores faturados pela Cosampa com os valores pagos pela Distribuidora:
    * **100% Batido:** A ordem é aprovada e direcionada imediatamente para **14. Faturado Total (Finalizado)**, sendo trancada com cadeado contra qualquer modificação.
    * **Com Divergência / Glosa:** A ordem é isolada no **Status 11 (Conciliado com Divergências)** com o cálculo automático da diferença e notificação registrada na Linha do Tempo.
* **Ganho Operacional / Objetivo:**
  * Eliminação de conferências manuais em planilhas: processamento instantâneo de centenas de pagamentos, separando automaticamente o que está quitado do que necessita de contestação.

### [x] 7.4 Comparador Dinâmico Bilateral de Itens e Gestão de Evidências (SharePoint)
* **Como Funciona na Prática:**
  * Para serviços com corte de pagamento, o painel exibe o confronto detalhado item a item do baremo (Quantidade/Valor Realizado pela Cosampa vs Pago pela Distribuidora vs Diferença).
  * O analista só consegue tramitar a ordem para cobrança se registrar a **Justificativa Técnica** na Linha do Tempo e o link comprobatório das evidências no **SharePoint**.
* **Ganho Operacional / Objetivo:**
  * Recuperação de receita: fornece subsídios técnicos e documentais incontestáveis para reaver valores cortados indevidamente pela contratante.

### [x] 7.5 Gestão de Disputas Contratuais e Prazos de Reapresentação
* **Como Funciona na Prática:**
  * Serviços encaminhados para recurso exigem a definição formal do **Mês de Reapresentação**.
  * Ao iniciar a disputa (Status 13), o sistema atribui a custódia nominal da ordem ao analista responsável e monitora os prazos de resposta do cliente.
* **Ganho Operacional / Objetivo:**
  * Controle de prazos e alçadas: impede que créditos a receber caiam no esquecimento, garantindo cobrança sistemática das receitas retidas.

### [x] 7.6 Blindagem e Imutabilidade das Ordens Concluídas (Status 14)
* **Como Funciona na Prática:**
  * Ordens 100% faturadas e recebidas recebem selo de trancamento `🔒 REGISTRO FINALIZADO E TRANCADO` e têm seus botões de tramitação desabilitados.
  * O backend bloqueia categoricamente qualquer tentativa de reabertura ou alteração cadastral.
* **Ganho Operacional / Objetivo:**
  * Integridade do balanço contábil: nenhuma ordem já recebida e contabilizada pode ser alterada acidentalmente na operação.

---

## 📊 Síntese Executiva de Maturidade do Projeto

| Bloco Operacional | Escopo de Negócio | Status de Entrega | Impacto Gerencial |
| :--- | :--- | :---: | :--- |
| **Bloco 1: Infraestrutura & Performance** | Alta volumetria e navegação sem travamentos | ✅ 100% Concluído | Estabilidade e agilidade operacional contínua |
| **Bloco 2: Motor Colaborativo & Timeline** | Linha do tempo, menções e notificações | ✅ 100% Concluído | Centralização da comunicação em um só lugar |
| **Bloco 3: Pendências, SLA & Hierarquia** | Prazos de campo, travas de avanço e equipes | ✅ 100% Concluído | Eliminação de atrasos e rastreabilidade total |
| **Bloco 4: Automação da Medição & Lotes** | Trava de origem, bypass comercial e lotes tolerantes | ✅ 100% Concluído | Aceleração do faturamento e blindagem contra glosas |
| **Bloco 5: Faturamento, Conciliação & Disputas** | Confronto automático, snapshot prévio e recuperação de glosas | ✅ 100% Concluído | Garantia do fluxo de caixa e blindagem de receita |
| **Governança & Segurança** | Perfis de tela, permissões por cargo e auditoria global | ✅ 100% Concluído | Governança corporativa, conformidade e compliance |

> [!NOTE]
> **Status Geral do Projeto:** **100% DO ESCOPO CONCLUÍDO E HOMOLOGADO**. A esteira completa do SIGES — desde a importação da ordem de campo até o recebimento financeiro e conciliação final — encontra-se plenamente construída, testada de ponta a ponta e pronta para operação."""

content_norm = content.replace("\r\n", "\n")
target_norm = target.replace("\r\n", "\n")
replacement_norm = replacement.replace("\r\n", "\n")

if target_norm in content_norm:
    new_content = content_norm.replace(target_norm, replacement_norm)
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Relatório gerencial atualizado com sucesso!")
else:
    print("Target não encontrado no relatório gerencial!")
