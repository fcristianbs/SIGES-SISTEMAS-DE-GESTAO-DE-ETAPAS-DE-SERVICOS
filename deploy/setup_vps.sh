#!/usr/bin/env bash
# ==============================================================================
# SIGES - PROVISIONAMENTO AUTOMATIZADO DE VPS (UBUNTU / DEBIAN)
# Instala Python 3, Caddy Server, Gunicorn e configura o serviço Systemd.
# ==============================================================================

set -e

echo "=========================================================="
echo "🚀 INICIANDO SETUP DO SERVIDOR SIGES NA VPS"
echo "=========================================================="

if [ "$EUID" -ne 0 ]; then
  echo "❌ Por favor, execute este script como root ou com sudo."
  exit 1
fi

APP_DIR="/var/www/siges"
BRANCH="main"

echo "📦 1. Atualizando repositórios do sistema..."
apt-get update && apt-get upgrade -y

echo "📦 2. Instalando ferramentas essenciais e Python 3..."
apt-get install -y python3 python3-pip python3-venv git curl ufw \
    debian-keyring debian-archive-keyring apt-transport-https

echo "🌐 3. Instalando o Caddy Server oficial..."
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg --yes
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update
apt-get install -y caddy

echo "📁 4. Configurando diretório da aplicação em $APP_DIR..."
mkdir -p "$APP_DIR"
chown -R www-data:www-data "$APP_DIR"

echo "🐍 5. Criando ambiente virtual Python e instalando dependências..."
if [ ! -d "$APP_DIR/.venv" ]; then
    sudo -u www-data python3 -m venv "$APP_DIR/.venv"
fi

if [ -f "$APP_DIR/requirements.txt" ]; then
    sudo -u www-data "$APP_DIR/.venv/bin/pip" install --upgrade pip
    sudo -u www-data "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
fi

echo "⚙️ 6. Configurando serviço Systemd do SIGES..."
if [ -f "$APP_DIR/deploy/siges.service" ]; then
    cp "$APP_DIR/deploy/siges.service" /etc/systemd/system/siges.service
    systemctl daemon-reload
    systemctl enable siges
fi

echo "⚙️ 7. Configurando Caddy Server..."
if [ -f "$APP_DIR/deploy/Caddyfile" ]; then
    cp "$APP_DIR/deploy/Caddyfile" /etc/caddy/Caddyfile
    systemctl reload caddy || systemctl restart caddy
fi

echo "🛡️ 8. Configurando Firewall UFW (SSH, HTTP, HTTPS)..."
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "=========================================================="
echo "✅ SETUP CONCLUÍDO COM SUCESSO!"
echo "➡️ Configure seu arquivo .env em $APP_DIR/.env"
echo "➡️ Em seguida, inicie o serviço com: systemctl start siges"
echo "=========================================================="
