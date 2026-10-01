import json
from backend.app.database.connection import get_db_cursor


def listar_perfis_tela(user_id, can_create_global=False):
    """
    Retorna os perfis de tela visíveis para o usuário:
    - Se can_create_global (Master): vê todos.
    - Se comum: vê globais, privados criados por ele e compartilhados.
    """
    try:
        with get_db_cursor() as cursor:
            if can_create_global:
                cursor.execute("SELECT * FROM perfis_tela ORDER BY tipo ASC, id ASC")
            else:
                sql = """
                    SELECT p.* FROM perfis_tela p
                    LEFT JOIN perfil_tela_usuario pu ON p.id = pu.perfil_id AND pu.usuario_id = %s
                    WHERE p.tipo = 'global' 
                       OR p.criado_por_id = %s 
                       OR pu.id IS NOT NULL
                    GROUP BY p.id
                    ORDER BY p.tipo ASC, p.id ASC
                """
                cursor.execute(sql, (user_id, user_id))

            rows = cursor.fetchall()
            for r in rows:
                if isinstance(r.get('colunas_visiveis'), str):
                    try:
                        cols = json.loads(r['colunas_visiveis'])
                        # Garante remoção de svc_data redundante
                        r['colunas_visiveis'] = [c for c in cols if c != "svc_data"]
                    except Exception:
                        r['colunas_visiveis'] = []
            return rows
    except Exception as e:
        print(f"[Erro Listar Perfis Tela] {e}")
        return []


def criar_perfil_tela(nome, colunas_visiveis, criado_por_id, tipo="privado"):
    """ Cria um novo perfil de tela com suas colunas visíveis """
    # Purga qualquer ocorrência de svc_data
    colunas_limpas = [c for c in colunas_visiveis if c != "svc_data"]
    sql = "INSERT INTO perfis_tela (nome, colunas_visiveis, criado_por_id, tipo) VALUES (%s, %s, %s, %s)"
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (nome, json.dumps(colunas_limpas), criado_por_id, tipo))
            novo_id = cursor.lastrowid
            return {
                "id": novo_id,
                "nome": nome,
                "colunas_visiveis": colunas_limpas,
                "tipo": tipo
            }
    except Exception as e:
        print(f"[Erro Criar Perfil Tela] {e}")
        raise


def obter_perfil_tela_por_id(perfil_id):
    """ Retorna um perfil de tela específico """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM perfis_tela WHERE id = %s", (perfil_id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"[Erro Obter Perfil Tela {perfil_id}] {e}")
        return None


def atualizar_perfil_tela(perfil_id, colunas_visiveis):
    """ Atualiza as colunas visíveis de um perfil de tela existente """
    colunas_limpas = [c for c in colunas_visiveis if c != "svc_data"]
    sql = "UPDATE perfis_tela SET colunas_visiveis = %s WHERE id = %s"
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(sql, (json.dumps(colunas_limpas), perfil_id))
            return cursor.rowcount
    except Exception as e:
        print(f"[Erro Atualizar Perfil Tela {perfil_id}] {e}")
        raise


def listar_todos_perfis_tela():
    """ Lista todos os perfis para a tela de Gestão de Acessos """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT id, nome, tipo, criado_por_id FROM perfis_tela ORDER BY tipo ASC, id ASC")
            return cursor.fetchall()
    except Exception as e:
        print(f"[Erro Listar Todos Perfis] {e}")
        return []


def obter_perfis_vinculados_usuario(user_id):
    """ Retorna a lista de IDs de perfis de tela vinculados a um usuário """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT perfil_id FROM perfil_tela_usuario WHERE usuario_id = %s", (user_id,))
            rows = cursor.fetchall()
            return [r['perfil_id'] for r in rows]
    except Exception as e:
        print(f"[Erro Perfis Usuario {user_id}] {e}")
        return []


def atualizar_perfis_usuario(user_id, perfil_ids):
    """ Atualiza a lista de perfis de tela vinculados a um usuário """
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM perfil_tela_usuario WHERE usuario_id = %s", (user_id,))
            for p_id in perfil_ids:
                cursor.execute("INSERT INTO perfil_tela_usuario (usuario_id, perfil_id) VALUES (%s, %s)", (user_id, p_id))
            return True
    except Exception as e:
        print(f"[Erro Atualizar Perfis Usuario {user_id}] {e}")
        raise
