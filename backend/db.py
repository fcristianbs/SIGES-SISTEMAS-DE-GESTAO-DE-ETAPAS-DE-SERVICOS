"""
db.py - Fachada de retrocompatibilidade para o SIGES
Delega para os novos repositórios e serviços modulares em backend.app
"""
import os
import sys

# Garante path para importação
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database.connection import get_db_connection, get_db_cursor
from backend.app.database.repositories.servicos_repo import (
    buscar_servicos_paginados as buscar_servicos_db,
    obter_opcoes_filtro as obter_opcoes_filtro_db,
    obter_parametros_pendencias as obter_parametros_pendencias_db,
    obter_servico_por_id,
    obter_servico_por_chave,
    atualizar_campos_servico
)
from backend.app.database.repositories.auditoria_repo import (
    registrar_log_auditoria,
    buscar_logs_auditoria,
    registrar_acao_global,
    inserir_comentario as inserir_comentario_db,
    buscar_comentarios as buscar_comentarios_db
)
from backend.app.database.repositories.conciliacao_repo import (
    buscar_snapshot_conciliacao as buscar_snapshot_conciliacao_db
)
from backend.app.database.repositories.perfis_repo import (
    listar_perfis_tela,
    criar_perfil_tela,
    obter_perfil_tela_por_id,
    atualizar_perfil_tela,
    listar_todos_perfis_tela,
    obter_perfis_vinculados_usuario,
    atualizar_perfis_usuario
)
from backend.app.services.tramitacao_service import (
    tramitar_servico as tramitar_servico_db,
    atualizar_dados_servico as atualizar_dados_servico_db
)
from backend.app.services.conciliacao_service import (
    gerar_snapshot_conciliacao as gerar_snapshot_conciliacao_db,
    fechar_evento_conciliacao as fechar_evento_conciliacao_db,
    obter_comparador_bilateral as obter_comparador_bilateral_db,
    salvar_comparador_bilateral as salvar_comparador_bilateral_db
)
from backend.app.services.importacao_service import (
    processar_importacao_dinamica
)

CONTRATOS_PERMITIDOS = [
    'MULTISERVICOS C.SUL',
    'MULTISERVICOS LESTE',
    'MULTISERVICOS SUL'
]
