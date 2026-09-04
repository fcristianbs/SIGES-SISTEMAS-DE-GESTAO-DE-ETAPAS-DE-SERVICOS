import os
import sys

# Garante que o python consiga importar o db.py mesmo estando rodando na pasta raiz ou dentro de backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from db import get_db_connection

def listar_logs():
    print("="*80)
    print(" BUSCANDO OS ÚLTIMOS 20 LOGS DE AUDITORIA NO BANCO DE DADOS... ")
    print("="*80)
    
    conn = get_db_connection()
    if not conn:
        print("Erro: Não foi possível conectar ao banco de dados.")
        return
        
    try:
        with conn.cursor() as cursor:
            # Busca os últimos 20 logs ordenados do mais recente para o mais antigo
            sql = """
                SELECT id, servico_id, usuario_nome, data_hora, campo_alterado, valor_anterior, novo_valor 
                FROM logs_auditoria 
                ORDER BY data_hora DESC 
                LIMIT 20
            """
            cursor.execute(sql)
            logs = cursor.fetchall()
            
            if not logs:
                print("Nenhum log encontrado no banco de dados.")
                return
                
            for log in logs:
                # Tratamento visual
                data_formatada = log['data_hora'].strftime("%d/%m/%Y %H:%M:%S") if log['data_hora'] else "Desconhecido"
                servico = log['servico_id']
                user = log['usuario_nome']
                campo = log['campo_alterado']
                antigo = log['valor_anterior'] if log['valor_anterior'] else "Vazio"
                novo = log['novo_valor'] if log['novo_valor'] else "Vazio"
                
                print(f"[{data_formatada}] {user} alterou '{campo}' no serviço {servico}:")
                print(f"    - De:   {antigo}")
                print(f"    - Para: {novo}")
                print("-" * 80)
                
    except Exception as e:
        print(f"Ocorreu um erro ao buscar os logs: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    listar_logs()
