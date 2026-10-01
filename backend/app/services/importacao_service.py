import pandas as pd
from backend.app.database.connection import get_db_cursor
from backend.app.database.repositories.auditoria_repo import (
    registrar_log_auditoria,
    registrar_acao_global
)


def processar_importacao_dinamica(temp_file_path, aba, header_idx, mapeamento_de_para, usuario_nome="Importador", usuario_email="importador@cosampa.com.br"):
    """
    Carrega o arquivo temporário via pandas e realiza a atualização dinâmica na base.
    Ignora valores nulos da planilha, não alterando o registro original.
    """
    try:
        df = pd.read_excel(temp_file_path, sheet_name=aba, header=header_idx)
        # Substitui nulos ou NaN do pandas por None
        df = df.where(pd.notnull(df), None)
    except Exception as e:
        print(f"[Erro Processar Excel] {e}")
        return {"status": "erro", "mensagem": f"Erro ao ler a planilha: {str(e)}"}

    coluna_chave_interna = 'num_servico'
    coluna_chave_planilha = None
    for int_col, ext_col in mapeamento_de_para.items():
        if int_col == coluna_chave_interna:
            coluna_chave_planilha = ext_col
            break
            
    if not coluna_chave_planilha:
        return {"status": "erro", "mensagem": "O mapeamento do 'Número do Serviço' é obrigatório."}

    sucessos = 0
    falhas = []
    
    try:
        for idx, row in df.iterrows():
            chave_valor = row.get(coluna_chave_planilha)
            if not chave_valor:
                continue
                
            chave_str = str(chave_valor).strip()
            if not chave_str.startswith("SOB-"):
                chave_str = f"SOB-{chave_str}"
                
            set_clauses = []
            values = []
            campos_alterados = {}
            
            with get_db_cursor() as cursor:
                cursor.execute("SELECT * FROM servicos WHERE num_servico = %s", (chave_str,))
                old_row = cursor.fetchone()
            
            if not old_row:
                falhas.append(chave_str)
                continue

            for col_interna, col_planilha in mapeamento_de_para.items():
                if col_interna == coluna_chave_interna:
                    continue 
                
                if col_planilha in row:
                    val_novo = row[col_planilha]
                    if val_novo is None or str(val_novo).strip() == "":
                        continue
                        
                    val_antigo = old_row.get(col_interna)
                    if str(val_antigo) != str(val_novo):
                        set_clauses.append(f"{col_interna} = %s")
                        values.append(str(val_novo))
                        campos_alterados[col_interna] = {"antigo": str(val_antigo), "novo": str(val_novo)}
            
            if not set_clauses:
                sucessos += 1
                continue
                
            set_clauses.append("updated_at = NOW()")
            query = f"UPDATE servicos SET {', '.join(set_clauses)} WHERE num_servico = %s"
            values.append(chave_str)
            
            with get_db_cursor(commit=True) as cursor:
                cursor.execute(query, tuple(values))
                if cursor.rowcount > 0:
                    sucessos += 1
                    servico_id = old_row["id"]
                    for k, v in campos_alterados.items():
                        registrar_log_auditoria(servico_id, usuario_nome, usuario_email, k, v["antigo"], v["novo"])
                        
                    desc_tech = {"modificacoes": campos_alterados, "via": "IMPORTACAO_EXCEL"}
                    desc_human = f"{usuario_nome} importou dados atualizando {len(campos_alterados)} campo(s) via Planilha."
                    registrar_acao_global(usuario_nome, usuario_email, "EDICAO_DADOS_LOTE", servico_id, desc_tech, desc_human)

        return {"status": "concluido", "atualizados": sucessos, "nao_encontrados": falhas}
    except Exception as e:
        print(f"[Erro Importação] {e}")
        return {"status": "erro", "mensagem": str(e)}
