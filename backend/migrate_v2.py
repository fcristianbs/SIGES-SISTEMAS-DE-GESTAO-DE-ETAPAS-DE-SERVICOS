import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(root_dir, '.env'))
except ImportError:
    pass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db import get_db_connection

def migrate():
    conn = get_db_connection()
    if not conn:
        print("Falha na conexão com banco!")
        return

    columns_to_add = [
        ("valor_pago_cliente", "DECIMAL(10,2) DEFAULT 0.0"),
        ("mes_reapresentacao", "VARCHAR(20) DEFAULT ''"),
        ("divergencia_conciliacao", "TEXT")
    ]
    
    with conn.cursor() as cursor:
        for col_name, col_type in columns_to_add:
            try:
                sql = f"ALTER TABLE servicos ADD COLUMN {col_name} {col_type}"
                cursor.execute(sql)
                print(f"Coluna {col_name} adicionada com sucesso.")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"Coluna {col_name} já existe.")
                else:
                    print(f"Erro ao adicionar coluna {col_name}: {e}")
        conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
