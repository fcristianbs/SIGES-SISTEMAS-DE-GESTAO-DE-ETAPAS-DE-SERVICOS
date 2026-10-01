# 🏗️ Plano de Implementação: Reestruturação Modular (Blueprints) & Deploy em VPS

Este documento estabelece o **Plano de Implementação Detalhado** para refatorar a arquitetura da plataforma **SIGES**, migrando o backend monolítico atual (`main.py` e `db.py`) para um **modelo em camadas (Clean Architecture com Flask Blueprints)** e preparando todos os scripts e arquivos de configuração para implantação em produção em uma máquina **VPS Linux (Ubuntu/Debian)**.

---

## 🎯 Objetivos Centrais

1. **Modularização Rígida:** Eliminar os arquivos monolíticos `main.py` (~730 linhas) e `db.py` (~930 linhas), dividindo-os em **Blueprints por domínio**, **Camada de Repositórios (SQL puro)** e **Camada de Serviços (Regras de Negócio do CDU V0 a V5)**.
2. **Alta Performance & Conexões (Pool):** Substituir o `pymysql.connect` individual a cada requisição por um **Connection Pool persistente**, eliminando travamentos de TCP e latência de handshake sob concorrência.
3. **Padrão Application Factory (`create_app`):** Permitir inicialização isolada para desenvolvimento, testes automatizados e produção.
4. **Pronto para VPS (Gunicorn + Caddy Server + Systemd):** Configurar o **Caddy Server** para entrega de alta performance do frontend estático, proxy reverso para os workers Gunicorn, com **HTTPS automático (Zero-Config SSL/TLS)** e HTTP/2 + HTTP/3 nativos.
5. **Zero Regressão de Regras de Negócio:** Garantir que 100% dos fluxos e travas homologados (Bypass Comercial, Trava de Origem, Comparador Bilateral, Status 14 Imutável, Retorno RN-04, SLA e Timeline) continuem funcionando sem qualquer alteração para o frontend.

---

## 📐 Arquitetura Alvo

```
backend/
├── app/
│   ├── __init__.py                # Application Factory (create_app)
│   ├── config.py                  # Configurações (Dev, Prod, Test)
│   ├── extensions.py              # Pool de Conexão, CORS, Logging
│   │
│   ├── api/                       # CAMADA HTTP (BLUEPRINTS)
│   │   ├── __init__.py            # Registro centralizado de Blueprints
│   │   ├── servicos_bp.py         # /api/servicos (Listagem paginada, filtros, busca)
│   │   ├── tramitacao_bp.py       # /api/servicos/.../tramitar, lote/tramitar
│   │   ├── medicao_bp.py          # /api/servicos/lote/enviar-validacao, rejeicoes
│   │   ├── conciliacao_bp.py      # /api/conciliacao/*, upload, snapshots
│   │   ├── perfis_bp.py           # /api/perfis_tela (CDU V4)
│   │   ├── colaboracao_bp.py      # /api/comentarios, auditoria (CDU V5)
│   │   ├── importacao_bp.py       # /api/importacao (CDU-08 Wizard)
│   │   ├── dashboard_bp.py        # /api/dashboard/kpis
│   │   └── usuarios_bp.py         # /api/usuarios
│   │
│   ├── services/                  # CAMADA DE REGRAS DE NEGÓCIO (BUSINESS LOGIC)
│   │   ├── tramitacao_service.py  # RN-01 a RN-05, Bypass, Trava Origem, Imutabilidade
│   │   ├── conciliacao_service.py # Snapshot ANTES, Comparador Bilateral, Baixa automática
│   │   └── importacao_service.py  # Pandas ETL, sanitização de cabeçalhos
│   │
│   ├── database/                  # CAMADA DE ACESSO A DADOS (DATA ACCESS LAYER)
│   │   ├── connection.py          # Gerenciador de Connection Pool (DBUtils / SQLAlchemy)
│   │   ├── servicos_repo.py       # Queries dinâmicas de listagem e contagem
│   │   ├── perfis_repo.py         # CRUD de perfis_tela e vínculos
│   │   ├── conciliacao_repo.py    # Snapshots e tabela de conciliação
│   │   └── auditoria_repo.py      # Gravação de logs_auditoria e comentários
│   │
│   └── core/                      # TRANSVERSAIS
│       ├── exceptions.py          # Exceções customizadas e Global Error Handler
│       └── logging.py             # Configuração de Logs Estruturados
│
├── wsgi.py                        # Entrypoint oficial para Gunicorn
├── gunicorn.conf.py               # Configurações do servidor WSGI
└── deploy/                        # ARTEFATOS DE INFRAESTRUTURA PARA A VPS
    ├── Caddyfile                  # Configuração Caddy (Proxy + Estáticos + TLS Automático + zstd)
    ├── siges.service              # Unit File do Systemd para execução contínua
    ├── setup_vps.sh               # Script de instalação e provisionamento do servidor
    └── deploy.sh                  # Script de atualização rápida (Git Pull + Reload)
```

---

## 🗂️ Fases de Implementação Propostas

### 🔹 FASE 1: Fundação de Configuração e Pool de Conexões
* **Arquivos Criados:**
  * `backend/app/config.py`: Separação das configurações por ambiente (`Config`, `DevelopmentConfig`, `ProductionConfig`). Leitura segura de variáveis do `.env` (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY`).
  * `backend/app/database/connection.py`: Implementação do **Connection Pool** reutilizável (usando `DBUtils.PooledDB` ou pool de conexão persistente com fallback e healthcheck).
  * `backend/app/extensions.py`: Centralizador de extensões (CORS, Pool, Limiter).

---

### 🔹 FASE 2: Camada de Acesso a Dados (Repositories)
* **Objetivo:** Isolar as consultas SQL puras de `backend/db.py`, sem misturar com validações de regras de negócio.
* **Arquivos Criados:**
  * `backend/app/database/servicos_repo.py`: Funções `buscar_servicos_paginados()`, `obter_servico_por_id()`, `atualizar_campos_servico()`. Preservando rigorosamente a ordenação `ORDER BY COALESCE(updated_at, '2000-01-01') DESC, id DESC`.
  * `backend/app/database/perfis_repo.py`: Funções para listar, criar e atualizar `perfis_tela` (garantindo ausência da chave `svc_data`).
  * `backend/app/database/conciliacao_repo.py`: Gravação de snapshots na tabela `conciliacao_snapshots`, busca de extratos.
  * `backend/app/database/auditoria_repo.py`: Inserção atômica em `logs_auditoria`, `comentarios_internos` e `historico_acoes`.

---

### 🔹 FASE 3: Camada de Serviços e Regras de Negócio (Services)
* **Objetivo:** Centralizar todas as lógicas operacionais e travas do CDU em arquivos testáveis e independentes de HTTP.
* **Arquivos Criados:**
  * `backend/app/services/tramitacao_service.py`:
    * Trava de Imutabilidade do Status 14 (🔒).
    * Trava RN-03 (bloqueio de avanço com pendências ativas).
    * Trava de Sistema de Origem Obrigatório.
    * Bypass Comercial (salto automático de 01 para 08).
    * Retorno automático RN-04.
    * Validações de Faturamento (08 ➡️ 09 com data) e Conciliação (09 ➡️ 10 com mês de emissão).
    * Validação de Justificativa na Timeline para Status 11 ➡️ 12 e Custódia Nominal para Status 12 ➡️ 13.
  * `backend/app/services/conciliacao_service.py`:
    * Geração do snapshot "Relatório ANTES" pré-importação.
    * Processamento e conciliação automática (100% batido ➡️ Status 14 vs divergências/glosas ➡️ Status 11).
  * `backend/app/services/importacao_service.py`:
    * Leitura de arquivos `.xlsx` e `.csv` via Pandas com sanitização de cabeçalhos e chave primária obrigatória `num_servico` (CDU-08).

---

### 🔹 FASE 4: Modularização em Flask Blueprints (API HTTP)
* **Objetivo:** Substituir as 730 linhas do `main.py` por rotas modulares organizadas em subpastas.
* **Arquivos Criados:**
  * `backend/app/__init__.py`: Factory `create_app(config_name)`.
  * `backend/app/api/servicos_bp.py`: Rota `/api/servicos`.
  * `backend/app/api/tramitacao_bp.py`: Rotas `/api/servicos/<id>/tramitar` e `/api/servicos/lote/tramitar`.
  * `backend/app/api/medicao_bp.py`: Rotas de envio em lote (CDU-02) e rejeições (CDU-06).
  * `backend/app/api/conciliacao_bp.py`: Rotas de conciliação automática, upload e histórico de snapshots.
  * `backend/app/api/perfis_bp.py`: Rotas de perfis de tela (`/api/perfis_tela`).
  * `backend/app/api/colaboracao_bp.py`: Rotas de comentários, menções `@` e logs de auditoria.
  * `backend/app/api/dashboard_bp.py`: Rotas de KPIs globais agregados.
  * `backend/app/api/usuarios_bp.py`: Rotas de gestão de colaboradores e papéis.
  * `backend/app/core/exceptions.py`: Handlers para erros 400, 404, 500 retornando JSON padronizado.

---

### 🔹 FASE 5: Entrypoints de Execução e Retrocompatibilidade
* **Objetivo:** Permitir que o projeto rode tanto em modo de desenvolvimento local quanto sob servidores WSGI em produção.
* **Arquivos Criados/Modificados:**
  * `backend/wsgi.py`: Entrypoint limpo chamando `create_app("production")`.
  * `backend/gunicorn.conf.py`: Configurações de workers (`bind = "127.0.0.1:8000"`, `workers = 4`, `timeout = 120`).
  * `backend/main.py`: Adaptado para instanciar `app = create_app("development")`, mantendo compatibilidade caso alguém execute `python backend/main.py`.

---

### 🔹 FASE 6: Infraestrutura e Automação de Deploy na VPS (Caddy Server)
* **Objetivo:** Entregar todos os scripts e configurações para colocar a aplicação rodando no ar na VPS com o moderno **Caddy Server**.
* **Arquivos Criados na pasta `deploy/`:**
  * `deploy/Caddyfile`:
    * Configuração limpa e declarativa com emissão e renovação automática de certificados SSL/TLS (sem certbot).
    * Suporte automático a HTTP/2 e HTTP/3 (QUIC) e compressão `zstd gzip`.
    * Servir arquivos estáticos do frontend (`file_server` para `/var/www/siges/frontend`).
    * Reverse proxy transparente para `/api/*` direcionando para `127.0.0.1:8000` (Gunicorn).
  * `deploy/siges.service`:
    * Arquivo de serviço do Systemd (`/etc/systemd/system/siges.service`).
    * Configurado com `Restart=always`, usuário de serviço e variáveis de ambiente.
  * `deploy/setup_vps.sh`:
    * Script automatizado para preparar a VPS do zero no Ubuntu/Debian (atualiza pacotes, adiciona repositório oficial do Caddy e instala via `apt`, instala Python 3, Git, cria ambiente virtual `.venv`).
  * `deploy/deploy.sh`:
    * Script de atualização em 1 comando para deploy contínuo (`git pull`, `pip install -r requirements.txt`, `caddy reload` e `systemctl restart siges`).

---

### 🔹 FASE 7: Validação e Testes de Integridade
* **Validação Automatizada:**
  * Executar as suítes de teste de integração existentes (`scratch/test_bloco5.py`, `scratch/test_transicao_telas.py`).
  * Testar todos os endpoints para confirmar que as respostas JSON permanecem 100% idênticas ao contrato original esperado pelo frontend `app.js`.

---

## 🔒 Garantias de Segurança e Não-Regressão

| Risco Potencial | Medida Mitigatória no Plano |
|---|---|
| Quebra de contratos da API com o frontend | Todos os nomes de campos, URLs de endpoints e payloads JSON foram preservados exatamente iguais. |
| Perda de travas do CDU (Bypass, Origem, Status 14) | As regras foram extraídas intactas para `tramitacao_service.py` e testadas via scripts automatizados. |
| Esgotamento de conexões MySQL na VPS | Implementação de Connection Pool com reutilização de conexões e fechamento seguro em context manager. |
| Queda inesperada do processo em produção | Gerenciamento via `Systemd` com reinício em menos de 1 segundo em caso de crash. |
| Complexidade de SSL e renovação de certificados | O **Caddy Server** lida de forma 100% autônoma com certificados Let's Encrypt / ZeroSSL, sem necessidade de cron jobs ou certbot. |
| Latência na entrega de arquivos do frontend | Caddy servirá diretamente HTML, CSS e JS da memória com compactação moderna `zstd/gzip` e HTTP/3. |
