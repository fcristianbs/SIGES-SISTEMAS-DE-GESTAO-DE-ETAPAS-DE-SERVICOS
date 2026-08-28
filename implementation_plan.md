# Plano de Implementação - Alinhamento do SIGES com a Especificação Detalhada de Casos de Uso (CDU.md)

Este plano apresenta o diagnóstico comparativo entre o que já construímos no **SIGES** e as novas regras de negócio e Casos de Uso detalhados em [`CDU.md`](file:///c:/git/SIGES-SISTEMAS%20DE%20GESTAO%20DE%20ETAPAS-DE-SERVICOS/CDU.md).

---

## 🔍 1. Diagnóstico Comparativo (O que já temos vs. O que o `CDU.md` exige)

### ✅ Recursos Já Construídos e Alinhados:
- **Infraestrutura Backend & Banco Secundário**: Conexão com o MySQL real (`operacao.vps-cosampa.online`), banco `siges_app` isolado, pipeline ETL (`backend/etl_sync.py`) lendo da base bruta `siges` em < 1ms.
- **Estrutura das 15 Etapas da Esteira**: Mapeamento dos 15 status operacionais, cores, badges e fluxo de visualização.
- **Painéis e Paginação**: Aba Gerencial com KPIs, gráfico de barras, distribuição por macroetapa, radar da operação com paginação instantânea em memória (0ms).
- **Filtros Globais**: Filtros por Período, Contrato, Tipo de Serviço, Status (01 a 15) e Busca textual.

---

### ⚠️ Novas Funcionalidades e Lacunas Identificadas (Gaps a Implementar):

| Domínio / CDU | Regra no `CDU.md` | Estado Atual no Sistema | Ação Necessária |
| :--- | :--- | :--- | :--- |
| **Transversal** | **RN-01: Log de Auditoria** | Histórico básico em memória local | Criar tabela `logs_auditoria` em `siges_app` e registrar usuário, timestamp, campo alterado, valor anterior e novo valor. |
| **Transversal** | **RN-02: Colunas Dinâmicas** | Exibição de colunas fixas na tabela | Alternar colunas exibidas na tabela centralizadora conforme a Tela e Status selecionados (ex: Vozes, Materiais, PEP, TDC). |
| **Transversal** | **RN-03 & RN-04: Retorno Automático** | Resolução manual de pendências | Ao marcar 100% dos itens de pendência como **TRATADO**, transitar automaticamente o status do serviço de volta para **01** (ou **03**). |
| **Transversal** | **RN-05: Filtro Hierárquico** | Sem filtro por Supervisor/Equipe | Adicionar campos de Supervisor/Coordenador/Equipe nas SOBs e botão de alternância "Desativar Filtro Hierárquico". |
| **Tela 01 (Medição)** | **CDU-01: Confirmação de Origem & Irmãos** | Sem agrupamento visual de SOBs | Exibir serviços "irmãos" (mesma incidência/obra) agrupados e modal com opção de gerar "Pendência Cosampa" (02) ou "Pendência Distribuidora" (04). |
| **Tela 01 (Medição)** | **CDU-02: Consolidar e Enviar para Validação** | Botão de avançar genérico | Modal de envio em lote no Status **03** solicitando **Sistema de Faturamento** e **Mês de Medição Inicial** (MM/AAAA). |
| **Tela 01 (Medição)** | **CDU-03: Divergências Financeiras (Conciliação)** | Exibição padrão no Status 11 | Layout em blocos paralelos (Valor Pago pelo Cliente *vs.* Valor Realizado Cosampa), link SharePoint e escolha (Cobrança Complementar -> Status 12/13). |
| **Tela 02 (Pendências)** | **CDU-04: Tratativa de Campo e Reprogramação** | Drawer básico de pendência | Modal expansivo com lista de inconsistências, botão `+ Anexo`, justificativa textual, checkbox `TRATADO` por item e fluxo `Necessita Reprogramar` (data obrigatória). |
| **Tela 02 (Pendências)** | **CDU-05: Pendências Distribuidora** | Tratativa misturada | Painel isolado para Status **04** com cadastro de andamento comercial ("Em Negociação", "Aprovado Excepcionalmente", "Voz Cadastrada") -> avança direto para 03. |
| **Tela 03 (Validação)** | **CDU-06: Validação do Cliente & Carga em Lote** | Sem upload de lote de rejeições | Aprovação com campo **Data de 1ª Validação** (botão autopreencher) -> Status 07; Rejeição manual/lote (CSV/XLSX) roteando para 06 (Fechamento) ou 07 (Operação). |
| **Tela 03 (Validação)** | **CDU-07: Tratar Rejeição pelo Fechamento** | Fluxo genérico | Status 06 permite ajuste administrativo e reenvio direto para Status 03. |
| **Dados** | **Dicionário de Dados Expandido (36 colunas)** | 14 colunas no banco `siges_app` | Expandir o schema da tabela `siges_app.servicos` para comportar PEP Obra (`cod_pep_obra`), TDC (`tdc`), Coordenador, Supervisor, Equipe, Membros, Veículo, etc. |

---

## 📐 2. Alterações Propostas por Componente

---

### Componente 1: Banco de Dados Secundário (`siges_app`) & Modelos ORM

#### 1.1 Expansão da Tabela `siges_app.servicos`
Adicionar as colunas do Dicionário de Dados do `CDU.md`:
- `cod_pep_obra`, `tdc`, `origem_sistema`, `incidencia`, `solicitante`, `id_cliente`, `cliente`, `endereco`, `cod_turno`, `placa_veiculo`, `modelo_veiculo`, `coordenador`, `supervisor`, `equipe`, `membros_equipe`, `obs_servico`, `latitude_servico`, `longitude_servico`, `inicio_desloc`, `fim_desloc`, `inicio_exec`, `fim_exec`, `tipo_equipe`, `tipo_obra`.

#### 1.2 [NOVA TABELA] `siges_app.logs_auditoria`
```sql
CREATE TABLE IF NOT EXISTS logs_auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    servico_id VARCHAR(50) NOT NULL,
    usuario_nome VARCHAR(100) NOT NULL,
    usuario_email VARCHAR(100) NOT NULL,
    data_hora DATETIME NOT NULL,
    campo_alterado VARCHAR(100) NOT NULL,
    valor_anterior TEXT,
    novo_valor TEXT,
    INDEX idx_servico (servico_id)
);
```

#### 1.3 [NOVA TABELA] `siges_app.itens_pendencia`
```sql
CREATE TABLE IF NOT EXISTS itens_pendencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    servico_id VARCHAR(50) NOT NULL,
    tipo_origem ENUM('COSAMPA', 'DISTRIBUIDORA') NOT NULL,
    item_codigo VARCHAR(100) NOT NULL, -- ex: 'FOTO_EVIDENCIA', 'MATERIAL_ERRADO', 'CROQUI', 'VOZ_NAO_CADASTRADA'
    descricao TEXT,
    tratado BOOLEAN DEFAULT FALSE,
    anexo_url VARCHAR(255),
    justificativa TEXT,
    data_tratativa DATETIME,
    usuario_tratativa VARCHAR(100),
    INDEX idx_servico (servico_id)
);
```

---

### Componente 2: Pipeline ETL (`backend/etl_sync.py`)

- Atualizar o script ETL para ler todas as 36 colunas correspondentes na base bruta `siges.servicos` (como `cod_pep_obra`, `coordenador`, `supervisor`, `equipe`, `tdc`) e inseri-las em `siges_app.servicos`.

---

### Componente 3: Endpoints Backend Flask (`backend/main.py` e `backend/db.py`)

- **`/api/servicos/<id>/tramitar` [POST]**: Processa a transição de status com verificação rígida da **RN-03** (bloqueia avanço se houver pendência ativa) e grava histórico na **RN-01**.
- **`/api/servicos/<id>/pendencias` [GET/POST/PUT]**: Registra novas pendências Cosampa/Distribuidora, atualiza status individual dos itens e executa o **retorno automático de status (RN-04)** ao atingir 100% de resolução.
- **`/api/servicos/lote/enviar-validacao` [POST]**: Executa o envio em lote (CDU-02) exigindo `sistema_faturamento` e `mes_medicao_inicial`.
- **`/api/servicos/lote/importar-rejeicoes` [POST]**: Processa planilha Excel/CSV com rejeições do cliente (CDU-06) aplicando o roteamento automático.
- **`/api/servicos/<id>/auditoria` [GET]**: Retorna a linha do tempo e histórico completo de alterações da SOB.

---

### Componente 4: Interface do Usuário (`frontend/app.js` e Estilos CSS)

- **RN-02 (Colunas Dinâmicas)**: Ajustar a renderização da tabela centralizadora para injetar/remover colunas conforme a tela (Medição exibe Vozes/Materiais; Pendências exibe Supervisor/Equipe/Inconformidades; Validação exibe Datas de Envio/Faturamento).
- **RN-05 (Filtro Hierárquico)**: Adicionar na barra superior o toggle "Filtro Hierárquico (Supervisor)" que restringe as linhas ao supervisor logado.
- **Modal de Tratativa de Pendências (CDU-04 / RN-04)**:
  - Exibir checklist de itens de correção com status visual (Pendente / Tratado).
  - Botão de upload para anexo de novas evidências (`+ Anexo`).
  - Campo "Necessita Reprogramar" abrindo seletor de data obrigatório.
  - Atualização automática em tempo real assim que 100% dos itens forem marcados como tratados.
- **Modal de Auditoria (RN-01)**:
  - Adicionar botão "Histórico de Auditoria" no drawer de cada SOB mostrando a linha do tempo com autor, data/hora e valores alterados.
- **Modal de Envio em Lote (CDU-02)**:
  - Modal ao selecionar múltiplas SOBs no Status 03 exigindo Sistema de Faturamento e Mês Inicial (MM/AAAA).

---

## 🧪 3. Plano de Verificação e Testes

### Testes Automatizados Backend:
1. **Verificação da RN-03**: Tentar tramitar uma SOB com pendência ativa e validar retorno HTTP 400 (Bloqueado).
2. **Verificação da RN-04**: Resolver 100% dos itens de pendência em uma SOB no Status 02 e validar transição automática para Status 01.
3. **Verificação da RN-01**: Executar qualquer alteração e consultar a tabela `logs_auditoria` confirmando registro do log.

### Testes Manuais na Interface:
1. **Navegação de Colunas Dinâmicas**: Trocar entre as abas Medição, Pendências e Validação observando a mudança automática de colunas.
2. **Tratativa de Pendência com Anexo**: Abrir uma SOB com pendência, anexar arquivo, justificar, marcar "TRATADO" e ver a SOB migrar automaticamente de volta para a aba de Medição.
3. **Envio em Lote**: Selecionar 3 SOBs no Status 03, preencher os campos do lote e validar a migração em massa para o Status 05.
