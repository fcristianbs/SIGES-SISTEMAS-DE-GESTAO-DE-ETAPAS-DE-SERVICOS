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

def test_connection():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(root_dir, '.env')
    
    if not os.path.exists(env_path):
        print(f"Erro: Arquivo .env nao encontrado em {env_path}")
        return

    config = parse_env(env_path)
    db_type = config.get("DB_TYPE", "mysql").lower()
    host = config.get("DB_HOST", "operacao.vps-cosampa.online")
    port = int(config.get("DB_PORT", 3306))
    user = config.get("DB_USER", "")
    password = config.get("DB_PASSWORD", "")
    dbname = config.get("DB_NAME", "")
    if not dbname or "NOME_DO_BANCO" in dbname or "SEU_BANCO" in dbname:
        dbname = None

    print(f"[CONECTANDO] Servidor {db_type.upper()} em {host}:{port}...")

    if db_type == "mysql":
        try:
            import pymysql
        except ImportError:
            print("Instalando PyMySQL para teste...")
            os.system(f"{sys.executable} -m pip install pymysql")
            import pymysql

        try:
            conn_args = {
                "host": host, "port": port, "user": user, "password": password,
                "connect_timeout": 10, "cursorclass": pymysql.cursors.DictCursor
            }
            if dbname:
                conn_args["database"] = dbname

            conn = pymysql.connect(**conn_args)
            print("[SUCESSO] Conexao estabelecida com o servidor MySQL!")
            
            with conn.cursor() as cursor:
                cursor.execute("SHOW DATABASES;")
                dbs = cursor.fetchall()
                print(f"\n[BANCOS DE DADOS] Bancos disponiveis ({len(dbs)}):")
                system_dbs = ('information_schema', 'performance_schema', 'mysql', 'sys')
                user_dbs = []
                for d in dbs:
                    name = list(d.values())[0]
                    if name not in system_dbs:
                        user_dbs.append(name)
                    print(f"  - {name}")

                for target_db in user_dbs:
                    print(f"\n[INSPECIONANDO BANCO] '{target_db}'")
                    try:
                        cursor.execute(f"USE `{target_db}`;")
                        cursor.execute("SHOW TABLES;")
                        tables = cursor.fetchall()
                        print(f"   Tabelas encontradas ({len(tables)}):")
                        for t in tables:
                            tname = list(t.values())[0]
                            print(f"     - {tname}")
                            cursor.execute(f"DESCRIBE `{tname}`;")
                            cols = cursor.fetchall()
                            for c in cols:
                                print(f"         * {c['Field']} ({c['Type']})")
                    except Exception as ex_db:
                        print(f"   Erro ao acessar {target_db}: {ex_db}")

            conn.close()
        except Exception as e:
            print(f"[ERRO] Erro ao conectar ao MySQL: {e}")

if __name__ == "__main__":
    test_connection()
