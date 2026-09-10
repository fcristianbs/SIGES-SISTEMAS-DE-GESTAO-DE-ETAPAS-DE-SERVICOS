import os
import sys
import json
import pymysql
from pymysql.cursors import DictCursor

try:
    from dotenv import load_dotenv
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(root_dir, '.env'))
except ImportError:
    pass

def get_db_connection():
    host = os.getenv("DB_HOST", "operacao.vps-cosampa.online")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")
    dbname = os.getenv("DB_APP_NAME", "siges_app")
    
    if not user or not password:
        print("Credenciais de banco não configuradas no .env")
        return None

    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password,
            database=dbname, connect_timeout=10, cursorclass=DictCursor
        )
        return conn
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

def migrate():
    conn = get_db_connection()
    if not conn:
        print("Falha ao conectar no banco para migração.")
        return
        
    try:
        with conn.cursor() as cursor:
            # 1. Tabela perfis_tela
            print("Criando tabela perfis_tela...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS perfis_tela (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(150) NOT NULL,
                    colunas_visiveis JSON NOT NULL,
                    criado_por_id INT NOT NULL,
                    tipo ENUM('global', 'privado') NOT NULL DEFAULT 'privado',
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            # 2. Tabela perfil_tela_usuario
            print("Criando tabela perfil_tela_usuario...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS perfil_tela_usuario (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    perfil_id INT NOT NULL,
                    usuario_id INT NOT NULL,
                    FOREIGN KEY (perfil_id) REFERENCES perfis_tela(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # 3. Inserir Perfil Global Padrão (se não existir)
            cursor.execute("SELECT id FROM perfis_tela WHERE nome = 'Perfil Padrão' AND tipo = 'global'")
            if not cursor.fetchone():
                print("Criando 'Perfil Padrão' global...")
                # Colunas essenciais default:
                default_cols = ["sel", "st", "ob", "pep_tdc", "cliente", "origem", "v", "ret"]
                
                cursor.execute("""
                    INSERT INTO perfis_tela (nome, colunas_visiveis, criado_por_id, tipo)
                    VALUES (%s, %s, %s, %s)
                """, ("Perfil Padrão", json.dumps(default_cols), 1, 'global'))
            
        conn.commit()
        print("Migração V4 (Perfis de Tela) concluída com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"Erro durante a migração: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
