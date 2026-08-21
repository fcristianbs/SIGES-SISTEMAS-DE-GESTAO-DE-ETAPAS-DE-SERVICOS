import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.models import Base
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable

def gerar_ddl():
    print("-- ==========================================================================")
    print("-- DDL SQL PARA CRIAÇÃO DAS TABELAS DO BANCO OPERACIONAL: siges_app")
    print("-- Execute os comandos abaixo dentro do seu MySQL após criar o banco siges_app")
    print("-- ==========================================================================\n")

    print("CREATE DATABASE IF NOT EXISTS `siges_app` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("USE `siges_app`;\n")

    engine = create_engine("mysql+pymysql://localhost/siges_app")

    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(engine)).strip()
        print(f"{ddl};\n")

if __name__ == "__main__":
    gerar_ddl()
