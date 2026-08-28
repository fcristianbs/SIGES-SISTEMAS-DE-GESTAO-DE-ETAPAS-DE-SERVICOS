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

def create_table_registro_acoes():
    conn = get_db_connection()
    if not conn:
        print("Falha na conexão com o banco de dados.")
        return

    try:
        with conn.cursor() as cursor:
            sql = """
            CREATE TABLE IF NOT EXISTS registro_acoes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                data_hora DATETIME NOT NULL,
                usuario_nome VARCHAR(255) NOT NULL,
                usuario_email VARCHAR(255) NOT NULL,
                acao_tipo VARCHAR(100) NOT NULL,
                entidade_id VARCHAR(100) NOT NULL,
                descricao_tecnica TEXT,
                descricao_humanizada TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(sql)
            conn.commit()
            print("Tabela 'registro_acoes' verificada/criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tabela registro_acoes: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_table_registro_acoes()
