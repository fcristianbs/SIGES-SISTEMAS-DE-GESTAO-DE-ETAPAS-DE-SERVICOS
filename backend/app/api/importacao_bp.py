import os
import pandas as pd
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from backend.app.services.importacao_service import processar_importacao_dinamica

importacao_bp = Blueprint("importacao_bp", __name__)


def get_upload_folder():
    folder = current_app.config.get("UPLOAD_FOLDER", "/tmp")
    os.makedirs(folder, exist_ok=True)
    return folder


@importacao_bp.route("/api/servicos/upload-temp", methods=["POST"])
def upload_temp_planilha():
    if 'file' not in request.files:
        return jsonify({"status": "erro", "mensagem": "Nenhum arquivo enviado"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "erro", "mensagem": "Nenhum arquivo selecionado"}), 400
        
    filename = secure_filename(file.filename)
    upload_folder = get_upload_folder()
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    try:
        xl = pd.ExcelFile(filepath)
        abas = xl.sheet_names
        return jsonify({"arquivo_temp_id": filename, "abas": abas})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro ao ler arquivo: {str(e)}"}), 500


@importacao_bp.route("/api/servicos/pre-visualizar", methods=["POST"])
def pre_visualizar_planilha():
    data = request.json or {}
    arquivo_temp_id = data.get("arquivo_temp_id")
    aba = data.get("aba_selecionada")
    linha_cabecalho = data.get("linha_cabecalho", 0)
    
    if not arquivo_temp_id or not aba:
        return jsonify({"status": "erro", "mensagem": "Arquivo ou aba não informados"}), 400
        
    upload_folder = get_upload_folder()
    filepath = os.path.join(upload_folder, arquivo_temp_id)
    try:
        # Lê as primeiras 10 linhas para preview sem engolir a primeira linha (header=None)
        df = pd.read_excel(filepath, sheet_name=aba, header=None, nrows=10)
        raw_linhas = df.to_dict(orient='records')
        
        # Limpeza 100% segura usando Python nativo
        linhas_limpas = []
        for row in raw_linhas:
            clean_row = {}
            for k, v in row.items():
                if pd.isna(v) or str(v).strip() in ['nan', 'NaN', 'NaT', 'None', '<NA>', '']:
                    clean_row[str(k)] = None
                else:
                    clean_row[str(k)] = str(v)
            linhas_limpas.append(clean_row)
            
        colunas = [str(c) for c in df.columns]
        return jsonify({"colunas": colunas, "linhas": linhas_limpas})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


@importacao_bp.route("/api/servicos/importar-dinamico", methods=["POST"])
def importar_dinamico_planilha():
    data = request.json or {}
    arquivo_temp_id = data.get("arquivo_temp_id")
    aba = data.get("aba_selecionada")
    linha_cabecalho = data.get("linha_cabecalho", 0)
    mapeamento = data.get("mapeamento", {})
    usuario_nome = data.get("usuario_nome", "Importador")
    
    upload_folder = get_upload_folder()
    filepath = os.path.join(upload_folder, arquivo_temp_id)
    if not os.path.exists(filepath):
        return jsonify({"status": "erro", "mensagem": "Arquivo não encontrado no servidor"}), 404
        
    res = processar_importacao_dinamica(filepath, aba, linha_cabecalho, mapeamento, usuario_nome)
    return jsonify(res)
