import os
import sys
from contextlib import contextmanager
import pymysql
from pymysql.cursors import DictCursor
from dbutils.pooled_db import PooledDB
from backend.app.config import Config

_pool = None

def init_db_pool(config_class=None):
    """Inicializa o pool de conexões persistente com o MySQL secundário (siges_app)"""
    global _pool
    cfg = config_class or Config

    host = cfg.DB_HOST
    port = cfg.DB_PORT
    user = cfg.DB_USER
    password = cfg.DB_PASSWORD
    dbname = cfg.DB_APP_NAME

    if not user or not password:
        print("[Aviso DB Pool] Credenciais de banco não configuradas.")
        return None

    try:
        _pool = PooledDB(
            creator=pymysql,
            maxconnections=getattr(cfg, "DB_MAX_OVERFLOW", 20),
            mincached=2,
            maxcached=getattr(cfg, "DB_POOL_SIZE", 10),
            blocking=True,
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname,
            cursorclass=DictCursor,
            charset="utf8mb4",
            ping=1  # Verifica e reconecta automaticamente caso a conexão tenha caído
        )
        return _pool
    except Exception as e:
        print(f"[Erro DB Pool] Falha ao inicializar PooledDB: {e}")
        return None


def get_db_connection():
    """
    Retorna uma conexão ativa extraída do Connection Pool.
    Ao chamar conn.close(), a conexão é devolvida ao Pool e NÃO destruída.
    """
    global _pool
    if _pool is None:
        init_db_pool()
        
    if _pool is None:
        return None

    try:
        conn = _pool.connection()
        if not hasattr(conn, "autocommit"):
            def _autocommit(on):
                c = conn
                while hasattr(c, "_con"):
                    c = c._con
                if hasattr(c, "autocommit"):
                    c.autocommit(on)
            conn.autocommit = _autocommit
        return conn
    except Exception as e:
        print(f"[Erro DB Pool] Falha ao obter conexão do pool: {e}")
        return None


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager seguro para obter cursor DictCursor e gerenciar commit/rollback
    e devolução automática da conexão ao pool.
    
    Exemplo de uso:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE servicos SET ...")
    """
    conn = get_db_connection()
    if conn is None:
        raise ConnectionError("Não foi possível obter uma conexão com o banco de dados via Connection Pool.")
    
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        if commit:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
