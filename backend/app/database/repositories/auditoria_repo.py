import json
from datetime import datetime
from backend.app.database.connection import get_db_cursor


def registrar_log_auditoria(servico_id, usuario_nome, usuario_email, campo_alterado, valor_anterior, novo_valor):
    """ RN-01: Log de Auditoria e Rastreabilidade """
    sql = """
        INSERT INTO logs_auditoria 
            (servico_id, usuario_nome, usuario_email, data_hora, campo_alterado, valor_anterior, novo_valor)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (
                servico_id,
                usuario_nome,
                usuario_email,
                now_str,
                campo_alterado,
                str(valor_anterior) if valor_anterior is not None else "",
                str(novo_valor) if novo_valor is not None else ""
            ))
        return True
    except Exception as e:
        print(f"[Erro Auditoria] Falha ao gravar log: {e}")
        return False


def buscar_logs_auditoria(servico_id):
    """ Retorna a lista de logs de auditoria de um serviço """
    sql = "SELECT * FROM logs_auditoria WHERE servico_id = %s ORDER BY id DESC"
    try:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (servico_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"[Erro Auditoria] {e}")
        return []


def registrar_acao_global(usuario_nome, usuario_email, acao_tipo, entidade_id, descricao_tecnica, descricao_humanizada):
    """ Grava log detalhado de ação de negócio no sistema """
    if isinstance(descricao_tecnica, dict):
        descricao_tecnica = json.dumps(descricao_tecnica, ensure_ascii=False)
        
    sql = """
        INSERT INTO registro_acoes 
            (data_hora, usuario_nome, usuario_email, acao_tipo, entidade_id, descricao_tecnica, descricao_humanizada)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (
                now_str, 
                usuario_nome, 
                usuario_email, 
                acao_tipo, 
                str(entidade_id), 
                descricao_tecnica, 
                descricao_humanizada
            ))
        return True
    except Exception as e:
        print(f"[Erro Log Ação] Falha ao gravar registro global: {e}")
        return False


def inserir_comentario(servico_id, usuario_id, usuario_nome, texto):
    """ Insere um comentário na timeline do serviço """
    sql = """
        INSERT INTO comentarios_internos (servico_id, usuario_id, usuario_nome, texto)
        VALUES (%s, %s, %s, %s)
    """
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (servico_id, usuario_id, usuario_nome, texto))
            novo_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM comentarios_internos WHERE id = %s", (novo_id,))
            comentario = cursor.fetchone()
        return {"status": "sucesso", "data": comentario}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}


def buscar_comentarios(servico_id):
    """ Retorna todos os comentários da timeline de um serviço """
    sql = """
        SELECT id, servico_id, usuario_id, usuario_nome, texto, criado_em 
        FROM comentarios_internos 
        WHERE servico_id = %s 
        ORDER BY criado_em ASC
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(sql, (servico_id,))
            return cursor.fetchall()
    except Exception as e:
        return []
