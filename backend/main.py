"""
main.py - Entrypoint de desenvolvimento local para o SIGES
Utiliza a Application Factory (create_app) com hot-reloading e entrega do frontend estático.
"""
import os
import sys

# Garante inclusão do diretório raiz no path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import create_app

app = create_app("development")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print("=" * 60)
    print(f"🚀 Servidor SIGES Modular iniciado com sucesso!")
    print(f"📡 API e Frontend ativos em: http://localhost:{port}")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=port)
