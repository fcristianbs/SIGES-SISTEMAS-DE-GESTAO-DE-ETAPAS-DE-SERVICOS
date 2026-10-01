#!/usr/bin/env bash
# ==============================================================================
# SIGES - SCRIPT DE ATUALIZAÇÃO CONTÍNUA (DEPLOY RÁPIDO)
# Executa git pull, atualiza dependências e recarrega serviços sem downtime.
# ==============================================================================

set -e

APP_DIR="/var/www/siges"

echo "🔄 [1/4] Atualizando código fonte com o repositório..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD || echo "master")
git pull origin "$CURRENT_BRANCH"

echo "📦 [2/4] Atualizando dependências do Python..."
"$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

echo "⚙️ [3/4] Atualizando arquivos de configuração..."
if [ -f "$APP_DIR/deploy/Caddyfile" ]; then
    sudo cp "$APP_DIR/deploy/Caddyfile" /etc/caddy/Caddyfile
    sudo systemctl reload caddy
fi

if [ -f "$APP_DIR/deploy/siges.service" ]; then
    sudo cp "$APP_DIR/deploy/siges.service" /etc/systemd/system/siges.service
    sudo systemctl daemon-reload
fi

echo "🚀 [4/4] Reiniciando serviço SIGES WSGI..."
sudo systemctl restart siges

echo "=========================================================="
echo "✅ DEPLOY FINALIZADO COM SUCESSO!"
echo "=========================================================="
sudo systemctl status siges --no-pager -l
