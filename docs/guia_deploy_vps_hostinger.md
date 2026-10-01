# 🚀 Guia Passo a Passo: Deploy do SIGES na VPS Hostinger (Iniciante)

Este guia foi feito especialmente para quem **não tem experiência prévia com Linux ou servidores VPS**. Seguindo estas etapas, você colocará a plataforma **SIGES** no ar com segurança, alta performance e poderá gerenciar tudo diretamente da sua IDE como se estivesse no seu computador.

---

## 📋 Sumário
1. [O que você precisa ter em mãos (Painel da Hostinger)](#1-dados-de-acesso-hostinger)
2. [Configurando a IDE para Conectar na VPS (Remote SSH)](#2-configurar-a-ide)
3. [Primeiro Acesso ao Terminal da VPS](#3-primeiro-acesso-ao-terminal)
4. [Subindo o Repositório do SIGES](#4-subindo-o-repositório)
5. [Executando a Instalação Automatizada (Caddy + Python + Systemd)](#5-instalação-automatizada)
6. [Configurando as Variáveis de Ambiente (.env)](#6-configurando-o-env)
7. [Iniciando e Testando a Aplicação](#7-iniciando-e-testando)
8. [Como Fazer Atualizações Futuras em 1 Clique](#8-atualizações-futuras)

---

## 1. Dados de Acesso (Hostinger)

Acesse o painel da Hostinger ([hpanel.hostinger.com](https://hpanel.hostinger.com)) e vá até a aba **VPS**. Você encontrará:
* **Endereço IP da VPS:** Ex: `185.199.108.50`
* **Usuário:** Normalmente `root`
* **Senha do Root:** (A senha que você definiu ao criar a VPS na Hostinger)
* **Sistema Operacional:** Recomendado **Ubuntu 22.04 LTS** ou **Ubuntu 24.04 LTS** (se ainda não escolheu, selecione Ubuntu no painel).

---

## 2. Configurar a IDE para Gerenciar a VPS (Sem Sofrimento com Terminal)

Você pode programar, editar arquivos e ver os logs da VPS diretamente pelo seu **VS Code / Antigravity IDE** como se fossem pastas locais.

### Passo a Passo na IDE:
1. Abra sua IDE no Windows.
2. Vá até a aba de **Extensões** (`Ctrl + Shift + X`).
3. Pesquise por **`Remote - SSH`** (da Microsoft) e clique em **Instalar**.
4. No canto inferior esquerdo da IDE, aparecerá um ícone azul `><` (ou aperte `F1` e digite `Remote-SSH: Connect to Host...`).
5. Digite:
   ```bash
   root@IP_DA_SUA_VPS
   ```
   *(Substitua `IP_DA_SUA_VPS` pelo IP real fornecido pela Hostinger).*
6. Pressione `Enter`. Se perguntar o tipo de sistema operacional, escolha **Linux**.
7. Se aparecer uma mensagem sobre "Fingerprint" ou "Continue?", clique em **Continue**.
8. Digite a **Senha do Root** que você configurou na Hostinger.
9. **Pronto!** Uma nova janela da IDE abrirá conectada diretamente dentro do servidor Linux.
10. Vá em **Terminal -> Novo Terminal** na IDE. Você agora tem um terminal Linux aberto dentro do servidor!

---

## 3. Primeiro Acesso ao Terminal

Se preferir conectar pelo terminal do próprio Windows (PowerShell):
1. Abra o **PowerShell** no seu Windows.
2. Digite o comando:
   ```bash
   ssh root@IP_DA_SUA_VPS
   ```
3. Digite sua senha (atenção: no Linux a senha não aparece na tela enquanto você digita por segurança, apenas digite e aperte `Enter`).

---

## 4. Subindo o Repositório do SIGES

Com o terminal da VPS aberto:

### 1. Instalar o Git (se ainda não estiver instalado):
```bash
apt update && apt install -y git
```

### 2. Clonar o projeto na pasta padrão de servidores (`/var/www/siges`):
```bash
git clone https://github.com/fcristianbs/SIGES-SISTEMAS-DE-GESTAO-DE-ETAPAS-DE-SERVICOS.git /var/www/siges
```
*(Caso seu repositório seja privado, o Git solicitará seu usuário do GitHub e um Personal Access Token como senha).*

### 3. Entrar na pasta do projeto:
```bash
cd /var/www/siges
```

---

## 5. Instalação Automatizada (1 Único Comando)

Nós preparamos um script automatizado que faz todo o trabalho pesado de servidor Linux para você:
* Instala o **Caddy Server** oficial.
* Instala o **Python 3** e ferramentas de compilação.
* Cria o ambiente virtual isolado (`.venv`).
* Instala todas as bibliotecas necessárias (`requirements.txt`).
* Configura o serviço de inicialização automática no sistema (**Systemd**).
* Configura as regras de segurança no Firewall (UFW).

Execute no terminal:
```bash
chmod +x deploy/setup_vps.sh deploy/deploy.sh
sudo ./deploy/setup_vps.sh
```

Aguarde cerca de 1 a 2 minutos enquanto o script baixa e configura tudo automaticamente.

---

## 6. Configurando as Variáveis de Ambiente (.env)

Agora crie o arquivo de credenciais do banco de dados na VPS:

```bash
cp .env.example .env
nano .env
```
*(O comando `nano` abre um editor de texto simples no terminal).*

Preencha os dados com as suas credenciais reais do banco MySQL:
```ini
SECRET_KEY=sua-chave-secreta-producao-2026
DB_HOST=operacao.vps-cosampa.online
DB_PORT=3306
DB_USER=seu_usuario_do_banco
DB_PASSWORD=sua_senha_do_banco
DB_APP_NAME=siges_app
```

* Para **Salvar** no nano: Pressione `Ctrl + O`, depois aperte `Enter`.
* Para **Sair** do nano: Pressione `Ctrl + X`.

---

## 7. Iniciando e Testando a Aplicação

### 1. Iniciar o serviço do SIGES:
```bash
systemctl start siges
```

### 2. Verificar se o SIGES está rodando normalmente:
```bash
systemctl status siges
```
*Se aparecer `Active: active (running)` em verde, está funcionando perfeitamente!*

### 3. Testar no seu Navegador:
Abra o navegador no seu computador e acesse:
```text
http://IP_DA_SUA_VPS/
```
A tela de **Login do SIGES** já estará carregada e funcionando, conectada ao seu backend Gunicorn e ao banco de dados com Connection Pool!

---

## 🔒 7.1 Configurar Domínio Próprio e HTTPS Automático (Opcional)

Se você comprou um domínio (ex: `siges.minhaempresa.com.br`):
1. No painel onde você comprou o domínio, crie um **Apontamento do Tipo A**:
   * **Nome:** `@` ou `siges`
   * **Destino/IP:** O IP da sua VPS Hostinger.
2. Na VPS, edite o arquivo do Caddy:
   ```bash
   nano /etc/caddy/Caddyfile
   ```
3. Substitua `:80` pelo seu domínio:
   ```caddy
   siges.minhaempresa.com.br {
       root * /var/www/siges/frontend
       encode zstd gzip
       file_server

       handle /api/* {
           reverse_proxy 127.0.0.1:8000
       }
       try_files {path} {path}/ /login.html
   }
   ```
4. Salve (`Ctrl+O`, `Enter`, `Ctrl+X`) e recarregue o Caddy:
   ```bash
   systemctl reload caddy
   ```
*O **Caddy Server** emitirá seu certificado SSL (HTTPS com cadeado verde) de forma 100% automática em segundos!*

---

## 8. Como Fazer Atualizações Futuras em 1 Clique

Quando você fizer alterações no código no seu computador e subir para o GitHub (`git push`), para atualizar a VPS você só precisa rodar **1 comando**:

```bash
cd /var/www/siges && ./deploy/deploy.sh
```

Esse script faz tudo sozinho:
1. Puxa as alterações do GitHub (`git pull`).
2. Atualiza dependências do Python se houver novidades.
3. Recarrega as configurações do Caddy.
4. Reinicia o backend Gunicorn sem travar o site.
5. Exibe o status do servidor na tela.
