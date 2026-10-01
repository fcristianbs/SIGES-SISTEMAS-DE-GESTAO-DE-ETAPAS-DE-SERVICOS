"""
Validação Integral da Nova Arquitetura Modular e Blueprints do SIGES
"""
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import create_app

def run_tests():
    print("=" * 70)
    print("TESTE DE INTEGRIDADE: NOVA ARQUITETURA MODULAR (FLASK BLUEPRINTS)")
    print("=" * 70)

    app = create_app("testing")
    client = app.test_client()

    endpoints = [
        ("/api/status", 200, "status"),
        ("/api/supervisores", 200, None),
        ("/api/parametros/pendencias", 200, "cosampa"),
        ("/api/dashboard/kpis", 200, "servicos_ativos"),
        ("/api/servicos?limit=5", 200, "data"),
        ("/api/perfis_tela?user_id=1", 200, None),
        ("/api/perfis", 200, "Master"),
        ("/api/usuarios", 200, None)
    ]

    for url, expected_code, expected_key in endpoints:
        resp = client.get(url)
        assert resp.status_code == expected_code, f"Falha em {url}: esperado {expected_code}, obtido {resp.status_code}"
        if expected_key:
            data = resp.get_json()
            assert expected_key in data, f"Chave {expected_key} não encontrada em {url}: {data}"
        print(f"  [OK] GET {url} -> {resp.status_code}")

    # Teste de Login
    login_resp = client.post("/api/auth/login", json={"email": "admin@cosampa.com.br"})
    assert login_resp.status_code == 200, f"Falha no login: {login_resp.status_code}"
    login_data = login_resp.get_json()
    assert login_data.get("status") == "sucesso"
    assert login_data.get("usuario", {}).get("perfil") == "Master"
    print("  [OK] POST /api/auth/login -> Sucesso (Perfil Master retornado)")

    print("=" * 70)
    print("TODAS AS ROTAS DOS BLUEPRINTS RESPONDERAM COM 100% DE SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
