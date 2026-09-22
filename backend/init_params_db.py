import os
from db import get_db_connection

def setup_parametros():
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_correcao_cosampa (
                id INT AUTO_INCREMENT PRIMARY KEY,
                categoria VARCHAR(100),
                descricao VARCHAR(200),
                ativo BOOLEAN DEFAULT TRUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_correcao_distribuidora (
                id INT AUTO_INCREMENT PRIMARY KEY,
                descricao VARCHAR(200),
                ativo BOOLEAN DEFAULT TRUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            
            # Seed
            cursor.execute("SELECT COUNT(*) as c FROM itens_correcao_cosampa")
            if cursor.fetchone()['c'] == 0:
                cursor.execute("INSERT INTO itens_correcao_cosampa (categoria, descricao) VALUES (%s, %s)", ("Fotos", "Fotos de baixa qualidade"))
                cursor.execute("INSERT INTO itens_correcao_cosampa (categoria, descricao) VALUES (%s, %s)", ("Fotos", "Sem evidência do serviço"))
                cursor.execute("INSERT INTO itens_correcao_cosampa (categoria, descricao) VALUES (%s, %s)", ("Materiais", "Materiais aplicados incorretamente"))
                cursor.execute("INSERT INTO itens_correcao_cosampa (categoria, descricao) VALUES (%s, %s)", ("Materiais", "Materiais retirados incorretamente"))
                cursor.execute("INSERT INTO itens_correcao_cosampa (categoria, descricao) VALUES (%s, %s)", ("Documentação", "Sem Croqui anexado"))
                cursor.execute("INSERT INTO itens_correcao_cosampa (categoria, descricao) VALUES (%s, %s)", ("Documentação", "Croqui incorreto"))
                
            cursor.execute("SELECT COUNT(*) as c FROM itens_correcao_distribuidora")
            if cursor.fetchone()['c'] == 0:
                cursor.execute("INSERT INTO itens_correcao_distribuidora (descricao) VALUES (%s)", ("Vozes não cadastradas no Contrato",))
                cursor.execute("INSERT INTO itens_correcao_distribuidora (descricao) VALUES (%s)", ("Serviço não despachado para Cosampa",))
                cursor.execute("INSERT INTO itens_correcao_distribuidora (descricao) VALUES (%s)", ("Ordem já faturada",))
                
        conn.commit()
        print("Tabelas de parametros criadas e populadas.")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    setup_parametros()
