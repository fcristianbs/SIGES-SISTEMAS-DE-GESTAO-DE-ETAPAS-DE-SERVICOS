import os
import sys

# Garante saída UTF-8 no Windows Console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Carrega variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(root_dir, '.env'))
except ImportError:
    pass

import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.models import Base, Perfil, Usuario

def criar_banco_e_tabelas():
    host = os.getenv("DB_HOST", "operacao.vps-cosampa.online")
    port = int(os.getenv("DB_PORT", 3306))
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")
    app_dbname = "siges_app"

    if not user or not password:
        print("[ERRO] Credenciais DB_USER ou DB_PASSWORD nao encontradas no .env")
        return

    print(f"[1/4] Conectando ao MySQL em {host}:{port} para criar o banco '{app_dbname}'...")

    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password, connect_timeout=10
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{app_dbname}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"[2/4] Banco de dados '{app_dbname}' verificado/criado com SUCESSO!")
        conn.close()
    except Exception as e:
        print(f"[ERRO] Erro ao criar o banco '{app_dbname}': {e}")
        return

    print(f"[3/4] Criando todas as tabelas em '{app_dbname}' via SQLAlchemy...")
    connection_uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{app_dbname}?charset=utf8mb4"
    engine = create_engine(connection_uri, echo=False)

    try:
        Base.metadata.create_all(engine)
        print(f"[3/4] TODAS AS TABELAS FORAM CRIADAS COM SUCESSO NO BANCO '{app_dbname}'!")
    except Exception as e:
        print(f"[ERRO] Falha ao criar tabelas: {e}")
        return

    print(f"[4/4] Inserindo registros iniciais de Perfis e Usuarios...")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if session.query(Perfil).count() == 0:
            p_master = Perfil(nome="Master", descricao="Administrador Master com controle total", is_master=True, telas=["gerencial", "medicao", "pendencias", "faturamento", "conciliacoes", "finalizados", "relatorios", "gestao_acessos"])
            p_fechamento = Perfil(nome="Fechamento", descricao="Gestao de medicoes e fechamento", is_master=False, telas=["gerencial", "medicao", "pendencias", "finalizados", "relatorios"])
            p_operacao = Perfil(nome="Operacao", descricao="Tratativa de pendencias operacionais", is_master=False, telas=["gerencial", "pendencias", "finalizados", "relatorios"])
            p_faturamento = Perfil(nome="Faturamento", descricao="Etapas de faturamento e conciliacao", is_master=False, telas=["gerencial", "medicao", "pendencias", "faturamento", "conciliacoes", "finalizados", "relatorios"])

            session.add_all([p_master, p_fechamento, p_operacao, p_faturamento])
            session.commit()
            print("  - Perfis iniciais inseridos: Master, Fechamento, Operacao, Faturamento")

            p_m = session.query(Perfil).filter_by(nome="Master").first()
            p_f = session.query(Perfil).filter_by(nome="Fechamento").first()
            p_o = session.query(Perfil).filter_by(nome="Operacao").first()
            p_fat = session.query(Perfil).filter_by(nome="Faturamento").first()

            u1 = Usuario(nome="Administrador Master", email="admin@cosampa.com.br", perfil_id=p_m.id)
            u2 = Usuario(nome="Carlos Fechamento", email="carlos@cosampa.com.br", perfil_id=p_f.id)
            u3 = Usuario(nome="Fernanda Operacao", email="fernanda@cosampa.com.br", perfil_id=p_o.id)
            u4 = Usuario(nome="Roberto Faturamento", email="roberto@cosampa.com.br", perfil_id=p_fat.id)

            session.add_all([u1, u2, u3, u4])
            session.commit()
            print("  - Usuarios iniciais inseridos: admin, carlos, fernanda, roberto")
        else:
            print("  - Perfis e usuarios ja estavam gravados.")

        print(f"\n[SUCESSO] PROCESSO CONCLUIDO COM SUCESSO! Banco '{app_dbname}' totalmente operacional!")

    except Exception as e:
        session.rollback()
        print(f"[ERRO] Erro ao inserir dados iniciais: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    criar_banco_e_tabelas()
