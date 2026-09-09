Esta versão substitui a [[CDU V2]] e introduz o perfil de [[Analista de Fechamento]] e [[Administrador Master]]."

> **Contexto:** Parte do projeto SIGES. Veja a documentação central em [[memory]].

# 📘 CDU-08: Importação Inteligente e Sincronização Dinâmica de Planilhas

---

## 👥 1. Atores e Perfis de Acesso
*   **Analista de Fechamento**: Ator principal responsável pelo upload, mapeamento de colunas e confirmação de sincronização.
*   **Administrador do Sistema (Master)**: Responsável por parametrizar as colunas internas disponíveis para mapeamento.

---

## 📂 2. Pré-condições e Gatilhos
*   **Pré-condição 1**: O usuário deve possuir login ativo com perfil autorizado para realizar importações de dados.
*   **Pré-condição 2**: O arquivo a ser importado deve estar nos formatos válidos: `.xlsx`, `.xls` ou `.csv`.
*   **Gatilho**: O usuário acessa a tela de faturamento/medição e clica no botão **"Importar Planilha Externa"**.

---

## 📐 3. Fluxo Principal do Assistente (Wizard de 3 Passos)

O processo de importação é guiado por uma interface assistida e altamente interativa baseada em etapas:

### 📍 Passo 1: Upload e Seleção da Aba (Worksheet Ativa)
1. O sistema exibe uma área de arrastar-e-soltar (*Drag-and-Drop*) para arquivos.
2. O usuário faz o upload do arquivo.
3. O frontend envia temporariamente o arquivo para o backend, que analisa a estrutura do arquivo e retorna os metadados (incluindo todas as abas disponíveis).
4. O sistema renderiza reativamente um seletor dropdown (`<select>`) listando as abas identificadas na planilha.
5. O usuário escolhe a aba de onde os dados serão extraídos e clica em **"Avançar"**.

### 📍 Passo 2: Definição da Linha de Referência (Cabeçalho)
1. O backend lê as primeiras 10 linhas da aba selecionada e as exibe no frontend em formato de tabela de pré-visualização.
2. O sistema solicita ao usuário que selecione qual dessas linhas representa o cabeçalho (que contém os nomes das colunas). Por padrão, a **Linha 0** (primeira linha) é selecionada.
3. O usuário seleciona a linha desejada e clica em **"Avançar"**.
4. O backend extrai os nomes das colunas dessa linha específica para alimentar a próxima etapa do mapeamento.

### 📍 Passo 3: Mapeamento Reativo De-Para (Gatilho "+") e Sincronização
1. O sistema exibe uma tela dividida:
   *   **Painel Esquerdo (Colunas Internas do Sistema)**: Inicia vazio, exibindo apenas um botão de destaque interativo **"+" (Adicionar Coluna)**.
   *   **Painel Direito (Colunas da Planilha Externa)**: Exibe os dropdowns de correspondência.
2. Ao clicar no botão **"+"**, o sistema exibe um menu de seleção contendo a lista de colunas internas disponíveis do SIGES (ex: "Cliente", "PEP Obra", "TDC", "Valor Unitário").
3. O usuário seleciona uma coluna interna. O sistema renderiza dinamicamente uma linha contendo:
   *   *Esquerda*: O rótulo da coluna interna adicionada.
   *   *Direita*: Um menu dropdown contendo a listagem de colunas extraídas do cabeçalho da planilha externa no Passo 2.
4. O usuário seleciona a coluna correspondente no dropdown da direita.
5. **Chave de Sincronização Obrigatória**: O usuário é obrigado a adicionar e mapear a coluna interna **"Número do Serviço"** (ou campo de identificação único equivalente) à coluna externa correspondente.
6. Após mapear os campos desejados, o usuário clica em **"Confirmar e Sincronizar"**.

---

## ⚙️ 4. Regras de Negócio Mandatórias (RNs)

### 🔴 RN-08.1: Chave de Correspondência Exata (Upsert)
*   A sincronização é baseada no **Número do Serviço** (exemplo de formato esperado: `SOB-363547406` ou padrão Regex `SOB-[0-9]+`).
*   Se o identificador contido na linha da planilha externa coincidir de forma exata com o registro existente na tabela `siges_app.servicos`, o sistema atualiza as informações. Caso contrário, o registro é ignorado para atualização de dados (evitando a criação de duplicados involuntários).

### 🔴 RN-08.2: Atualização Seletiva (Mapeamento Sob Demanda)
*   Apenas as propriedades explicitamente adicionadas e mapeadas no Passo 3 do Wizard pelo usuário serão atualizadas.
*   Qualquer coluna interna do banco de dados que não tenha sido adicionada pelo painel de mapeamento **deve** permanecer intacta com seus valores pré-existentes.

### 🔴 RN-08.3: Validação de Chave e Trava de Execução
*   O sistema impede a conclusão da importação se a chave obrigatória de identificação única (**Número do Serviço**) não estiver ativamente mapeada.
*   Ao tentar finalizar sem esse campo de-para, o modal exibe um alerta impeditivo com a mensagem: `"O mapeamento do 'Número do Serviço' é obrigatório para sincronizar os dados."`

### 🔴 RN-08.4: Relatório de Inconsistências Pós-Importação
*   Ao término da operação, o sistema não deve falhar silenciosamente. Ele deve exibir na tela um sumário contendo:
    *   Quantidade total de linhas processadas.
    *   Quantidade de registros atualizados com sucesso.
    *   Lista de Número do Serviço contidos na planilha que não foram encontrados na base do SIGES (inconsistências).

### 🔴 RN-08.5: Rastreabilidade (Relação com RN-01)
*   Toda e qualquer alteração gerada através da importação de planilha deve acionar disparadores para gravar logs de auditoria na tabela `logs_auditoria` contendo o usuário logado executor, data/hora da importação, campo modificado, valor anterior e novo valor do registro atualizado.

---

## 📐 5. Arquitetura Técnica e Especificações para os Desenvolvedores

### 💻 Frontend (Multi-page SPA Híbrida / JS Vanilla)
Para manter o alinhamento com `frontend/app.js`, utilize o padrão reativo da Store para controlar o estado do assistente.

#### Estrutura do Estado na Store (`importacaoWizard`):
```javascript
const wizardStore = {
  state: {
    arquivoTempId: null,
    abasDisponiveis: [],
    abaSelecionada: "",
    linhasPrevisualizacao: [],
    linhaCabecalhoIndex: 0,
    colunasPlanilha: [],
    colunasInternasDisponiveis: [
      { id: "num_servico", label: "Número do Serviço (Chave)" },
      { id: "cod_pep_obra", label: "Código PEP Obra" },
      { id: "tdc", label: "Código TDC" },
      { id: "cliente", label: "Cliente" },
      { id: "supervisor", label: "Supervisor" },
      { id: "coordenador", label: "Coordenador" },
      { id: "total_servicos", label: "Total dos Serviços" }
    ],
    mapeamentoAtivo: {} // Estrutura: { col_interna_id: col_planilha_nome }
  },
  // Métodos reativos para atualizar e renderizar a interface baseada nas alterações
};
```

---

### 🐍 Backend (Flask / Python REST API)

#### 1. Endpoint para Processar Upload Inicial e Extrair Metadados
*   **Rota**: `/api/servicos/upload-temp`
*   **Método**: `POST`
*   **Content-Type**: `multipart/form-data`
*   **Retorno (JSON)**:
    ```json
    {
      "arquivo_temp_id": "temp_6152a6b2.xlsx",
      "abas": ["Medicao_Agosto", "Pendencias_Operacionais", "Parametros"]
    }
    ```

#### 2. Endpoint para Obter Pré-visualização de Linhas e Colunas
*   **Rota**: `/api/servicos/pre-visualizar`
*   **Método**: `POST`
*   **Payload (JSON)**:
    ```json
    {
      "arquivo_temp_id": "temp_6152a6b2.xlsx",
      "aba_selecionada": "Medicao_Agosto"
    }
    ```
*   **Retorno (JSON)**: Retorna as primeiras 10 linhas em formato de matriz e detecta a estrutura do arquivo.

#### 3. Endpoint para Executar Sincronização Dinâmica (Processamento Otimizado)
*   **Rota**: `/api/servicos/importar-dinamico`
*   **Método**: `POST`
*   **Payload (JSON)**:
    ```json
    {
      "arquivo_temp_id": "temp_6152a6b2.xlsx",
      "aba_selecionada": "Medicao_Agosto",
      "linha_cabecalho": 0,
      "mapeamento": {
        "num_servico": "Nº OS",
        "cod_pep_obra": "Código PEP",
        "cliente": "Nome do Cliente Final"
      }
    }
    ```

#### 🛠️ Lógica de Upsert/Update Otimizada (Pandas / SQL no Backend):
Para evitar timeouts causados por loops repetitivos de queries SQL, o backend deve carregar o chunk em DataFrame, validar o mapeamento e gerar uma execução em lote de atualização baseada na chave:

```python
import pandas as pd
from backend.db import get_connection

def processar_importacao_dinamica(temp_file_path, aba, header_idx, mapeamento_de_para):
    # 1. Carregar DataFrame baseado nas decisões do usuário
    df = pd.read_excel(temp_file_path, sheet_name=aba, header=header_idx)
    
    # Substituir valores nulos por None para inserção SQL limpa
    df = df.where(pd.notnull(df), None)
    
    # Filtrar o mapeamento invertido para mapear as colunas da planilha para o sistema
    # mapeamento_de_para: {coluna_interna: coluna_planilha}
    coluna_chave_interna = 'num_servico'
    coluna_chave_planilha = mapeamento_de_para.get(coluna_chave_interna)
    
    sucessos = 0
    falhas = []
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        for idx, row in df.iterrows():
            chave_valor = row.get(coluna_chave_planilha)
            if not chave_valor:
                continue
                
            # Validar formato de chave ex: SOB-XXXX
            if not str(chave_valor).startswith("SOB-"):
                # Caso o ID esteja puro, aplicar máscara
                chave_valor = f"SOB-{chave_valor}"
                
            # Construir dinamicamente a cláusula SET para as colunas mapeadas
            set_clauses = []
            values = []
            
            for col_interna, col_planilha in mapeamento_de_para.items():
                if col_interna == coluna_chave_interna:
                    continue # Não atualizar a chave primária
                
                if col_planilha in row:
                    set_clauses.append(f"{col_interna} = %s")
                    values.append(row[col_planilha])
            
            if not set_clauses:
                continue # Nenhum campo mapeado além da chave
                
            query = f"UPDATE servicos SET {', '.join(set_clauses)} WHERE num_servico = %s"
            values.append(chave_valor)
            
            cursor.execute(query, tuple(values))
            if cursor.rowcount > 0:
                sucessos += 1
                # Logar a auditoria aqui (ou disparar via trigger/fila de auditoria)
            else:
                falhas.append(str(chave_valor))
                
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
        
    return {"status": "concluido", "atualizados": sucessos, "nao_encontrados": falhas}
```

---

## 🧪 6. Critérios de Aceite para QA (Garantia de Qualidade)
- [ ] **Validação de Aba**: Ao carregar um arquivo de 3 abas, o seletor dropdown do Passo 1 deve listar exatamente os nomes das 3 planilhas ativas.
- [ ] **Indicação de Cabeçalho**: O Passo 2 deve permitir alternar a linha de cabeçalho da visualização dinâmica e, ao mudar da Linha 0 para a Linha 1, atualizar os nomes das colunas disponíveis de forma instantânea.
- [ ] **Mapeamento Dinâmico**: Ao clicar em "+", as colunas internas já mapeadas devem desaparecer da lista de escolha para evitar mapeamentos duplicados da mesma coluna interna.
- [ ] **Bloqueio de Chave Primária**: O botão "Confirmar e Sincronizar" no Passo 3 deve permanecer desabilitado (not-allowed) enquanto a coluna "Número do Serviço" não for vinculada a algum campo da planilha externa.
- [ ] **Proteção de Dados Omitidos**: Rodar uma sincronização mapeando apenas "Cliente" e validar se os dados cadastrais pré-existentes de "Supervisor", "PEP Obra" e "TDC" permanecem inalterados no banco de dados.
- [ ] **Conformidade de Auditoria**: Verificar se a execução da importação dinâmica insere uma entrada correspondente para cada alteração de campo de cada registro na tabela de logs de auditoria real do sistema.
