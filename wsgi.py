import os
import sys

# Adiciona a raiz do projeto ao path de execução
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import create_app

# Instância oficial de produção para o servidor WSGI (Gunicorn)
app = create_app("production")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
