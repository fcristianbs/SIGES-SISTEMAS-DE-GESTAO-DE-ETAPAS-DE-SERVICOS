import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.db import get_db_connection

def migrate():
    conn = get_db_connection()
    if not conn:
        print("Erro: Não foi possível conectar ao banco de dados.")
        sys.exit(1)

    try:
        with conn.cursor() as cur:
            # 1. Colunas na tabela servicos
            cur.execute("SHOW COLUMNS FROM servicos LIKE 'data_validacao'")
            if not cur.fetchone():
                print("Adicionando coluna data_validacao em servicos...")
                cur.execute("ALTER TABLE servicos ADD COLUMN data_validacao datetime NULL AFTER data_primeira_validacao")

            cur.execute("SHOW COLUMNS FROM servicos LIKE 'mes_emissao'")
            if not cur.fetchone():
                print("Adicionando coluna mes_emissao em servicos...")
                cur.execute("ALTER TABLE servicos ADD COLUMN mes_emissao varchar(20) NULL AFTER sistema_faturamento")

            cur.execute("SHOW COLUMNS FROM servicos LIKE 'responsavel_disputa'")
            if not cur.fetchone():
                print("Adicionando coluna responsavel_disputa em servicos...")
                cur.execute("ALTER TABLE servicos ADD COLUMN responsavel_disputa varchar(100) NULL AFTER mes_reapresentacao")

            cur.execute("SHOW COLUMNS FROM servicos LIKE 'sharepoint_url'")
            if not cur.fetchone():
                print("Adicionando coluna sharepoint_url em servicos...")
                cur.execute("ALTER TABLE servicos ADD COLUMN sharepoint_url varchar(500) NULL AFTER responsavel_disputa")

            # 2. Tabela de snapshots da conciliação
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conciliacao_snapshots (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    evento_id VARCHAR(50) NOT NULL,
                    servico_id VARCHAR(50) NOT NULL,
                    status_id_anterior INT NOT NULL,
                    valor_faturado DECIMAL(12,2) NULL,
                    valor_pago_anterior DECIMAL(12,2) NULL,
                    dados_servico_json LONGTEXT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_evento (evento_id),
                    INDEX idx_servico (servico_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            print("Tabela conciliacao_snapshots verificada/criada.")

            # 3. Colunas para o comparador bilateral em baremo_itens
            cur.execute("SHOW COLUMNS FROM baremo_itens LIKE 'valor_pago_item'")
            if not cur.fetchone():
                print("Adicionando colunas de comparador bilateral em baremo_itens...")
                cur.execute("ALTER TABLE baremo_itens ADD COLUMN quantidade_paga float NULL AFTER valor_medido")
                cur.execute("ALTER TABLE baremo_itens ADD COLUMN valor_pago_item decimal(12,2) NULL AFTER quantidade_paga")
                cur.execute("ALTER TABLE baremo_itens ADD COLUMN divergencia_item decimal(12,2) NULL AFTER valor_pago_item")

            conn.commit()
            print("Migração do Bloco 5 concluída com sucesso no MySQL!")
    except Exception as e:
        print(f"Erro durante migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
