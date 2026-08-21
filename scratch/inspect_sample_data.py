import pymysql
import os
import sys

# Garante saída UTF-8 no Windows Console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def parse_env(filepath):
    env_vars = {}
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env_vars[k.strip()] = v.strip()
    return env_vars

def diagnosticar():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = parse_env(os.path.join(root_dir, '.env'))

    host = config.get("DB_HOST", "operacao.vps-cosampa.online")
    port = int(config.get("DB_PORT", 3306))
    user = config.get("DB_USER", "")
    password = config.get("DB_PASSWORD", "")
    dbname = config.get("DB_NAME", "siges")

    print(f"=== AMOSTRAGEM RÁPIDA DE DADOS REAIS DO BANCO {dbname} ===")
    conn = pymysql.connect(
        host=host, port=port, user=user, password=password, database=dbname,
        connect_timeout=5, cursorclass=pymysql.cursors.DictCursor
    )
    
    with conn.cursor() as cursor:
        # Busca 20 registros recentes de forma ultrarrápida
        cursor.execute("""
            SELECT num_servico, contrato, nome_obra, bairro, localidade, tipo_servico, 
                   status, situacao_servico, retorno_de_campo, valor_leitura, dta_exec_srv, data_geracao
            FROM servicos 
            LIMIT 20;
        """)
        rows = cursor.fetchall()

        statuses = set()
        contratos = set()
        tipos = set()
        situacoes = set()

        for r in rows:
            if r.get('status'): statuses.add(r['status'])
            if r.get('contrato'): contratos.add(r['contrato'])
            if r.get('tipo_servico'): tipos.add(r['tipo_servico'])
            if r.get('situacao_servico'): situacoes.add(r['situacao_servico'])

        print(f"\n📌 STATUS ENCONTRADOS NA AMOSTRA: {list(statuses)}")
        print(f"\n📌 CONTRATOS ENCONTRADOS: {list(contratos)}")
        print(f"\n📌 TIPOS DE SERVIÇO ENCONTRADOS: {list(tipos)}")
        print(f"\n📌 SITUAÇÕES ENCONTRADAS: {list(situacoes)}")

        print("\n--- AMOSTRA DETALHADA DE 3 REGISTROS ---")
        for idx, r in enumerate(rows[:3], 1):
            print(f"\n[Registro {idx}]")
            for k, v in r.items():
                print(f"  • {k}: {v}")

    conn.close()

if __name__ == "__main__":
    diagnosticar()
