# ==========================================================================
# SIGES - SISTEMA DE GESTÃO DE ETAPAS DE SERVIÇOS (COSAMPA)
# Base de Dados Mock e Estruturas de Domínio para Testes e Desenvolvimento
# ==========================================================================

PERFIS_DB = {
    "Master": {
        "nome": "Master",
        "descricao": "Administrador Master com controle total de acessos",
        "is_master": True,
        "telas": ["gerencial", "medicao", "pendencias", "faturamento", "conciliacoes", "finalizados", "relatorios", "gestao_acessos"]
    },
    "Fechamento": {
        "nome": "Fechamento",
        "descricao": "Gestão de medições e fechamento de serviços",
        "is_master": False,
        "telas": ["gerencial", "medicao", "pendencias", "finalizados", "relatorios"]
    },
    "Operação": {
        "nome": "Operação",
        "descricao": "Tratativa de pendências operacionais",
        "is_master": False,
        "telas": ["gerencial", "pendencias", "finalizados", "relatorios"]
    },
    "Faturamento": {
        "nome": "Faturamento",
        "descricao": "Acesso às etapas de faturamento e conciliação",
        "is_master": False,
        "telas": ["gerencial", "medicao", "pendencias", "faturamento", "conciliacoes", "finalizados", "relatorios"]
    }
}

USUARIOS_DB = [
    {"id": 1, "nome": "Administrador Master", "email": "admin@cosampa.com.br", "perfil": "Master", "telas_custom": None},
    {"id": 2, "nome": "Carlos Fechamento", "email": "carlos@cosampa.com.br", "perfil": "Fechamento", "telas_custom": None},
    {"id": 3, "nome": "Fernanda Operação", "email": "fernanda@cosampa.com.br", "perfil": "Operação", "telas_custom": None},
    {"id": 4, "nome": "Roberto Faturamento", "email": "roberto@cosampa.com.br", "perfil": "Faturamento", "telas_custom": None}
]

# Amostragem de serviços fiel às imagens do protótipo
SERVICOS_DB = [
    {"id": "SOB-2026-0341", "ct": "A", "ob": "Vila Prudente", "tp": "Rede", "st": 1, "v": 12400.0, "d": 2, "nota": "NM-0873", "data": "11/08", "dep": "—", "area": "Fechamento"},
    {"id": "SOB-2026-0347", "ct": "A", "ob": "Vila Prudente", "tp": "Medidor", "st": 1, "v": 980.0, "d": 5, "nota": "NM-0879", "data": "08/08", "dep": "—", "area": "Fechamento"},
    {"id": "SOB-2026-0352", "ct": "B", "ob": "Jd. Ângela", "tp": "Transformador", "st": 1, "v": 38200.0, "d": 1, "nota": "NM-0881", "data": "12/08", "dep": "—", "area": "Fechamento"},
    
    # Serviços com Pendências Operacionais (Imagens do Protótipo)
    {
        "id": "SOB-2026-0298", "ct": "A", "ob": "Penha", "tp": "Rede", "st": 2, "v": 21500.0, "d": 9, "nota": "NM-0830", "data": "04/08", "dep": "Operação", "area": "Operação", "ret": "Fotos e materiais",
        "pend": [
            {"t": "Fotos", "tr": False, "det": "Reenviar foto em alta definição da caixa de barramento.", "anx": None},
            {"t": "Materiais", "tr": False, "det": "Confirmar código do conector cunha instalado em campo.", "anx": None}
        ]
    },
    {
        "id": "SOB-2026-0301", "ct": "B", "ob": "Capela do Socorro", "tp": "Ramal", "st": 2, "v": 3400.0, "d": 6, "nota": "NM-0835", "data": "07/08", "dep": "Operação", "area": "Operação", "ret": "Documentação",
        "pend": [
            {"t": "Documentos", "tr": False, "det": "Anexar termo de responsabilidade assinado pelo cliente.", "anx": None},
            {"t": "Retorno", "tr": False, "det": "Justificar horário atípico de atendimento no ramal.", "anx": None}
        ]
    },
    {
        "id": "SOB-2026-0315", "ct": "C", "ob": "Itaquera", "tp": "Poste", "st": 2, "v": 7250.0, "d": 3, "nota": "NM-0840", "data": "10/08", "dep": "Operação", "area": "Operação", "ret": "Foto do prumo",
        "pend": [
            {"t": "Fotos", "tr": False, "det": "Reenviar foto com o prumo mecânico visível ao lado do poste.", "anx": None}
        ]
    },
    {
        "id": "SOB-2026-0322", "ct": "A", "ob": "Tatuapé", "tp": "Rede", "st": 2, "v": 5600.0, "d": 4, "nota": "NM-0844", "data": "09/08", "dep": "Operação", "area": "Operação",
        "pend": [
            {"t": "Materiais", "tr": False, "det": "Verificar boletim de medição de isoladores.", "anx": None},
            {"t": "Outros", "tr": True, "det": "Vistoria prévia já realizada pelo supervisor.", "anx": "Relatorio_Vistoria.pdf"}
        ]
    },
    {
        "id": "SOB-2026-0328", "ct": "B", "ob": "Mooca", "tp": "Ramal", "st": 2, "v": 4800.0, "d": 8, "nota": "NM-0846", "data": "05/08", "dep": "Operação", "area": "Operação",
        "pend": [
            {"t": "Fotos", "tr": False, "det": "Incluir foto do lacre de segurança.", "anx": None},
            {"t": "Documentos", "tr": True, "det": "ART devidamente quitada anexada.", "anx": "ART_Quitada.pdf"}
        ]
    },

    {"id": "SOB-2026-0289", "ct": "A", "ob": "Penha", "tp": "Rede", "st": 3, "v": 45900.0, "d": 1, "nota": "NM-0851", "data": "12/08", "dep": "—", "area": "Fechamento"},
    {"id": "SOB-2026-0293", "ct": "B", "ob": "Grajaú", "tp": "Transformador", "st": 3, "v": 61300.0, "d": 3, "nota": "NM-0854", "data": "10/08", "dep": "—", "area": "Fechamento"},
    {"id": "SOB-2026-0269", "ct": "B", "ob": "Parelheiros", "tp": "Rede", "st": 5, "v": 18700.0, "d": 2, "nota": "NM-0842", "data": "11/08", "dep": "—", "area": "Fechamento", "ret": "Baremo divergente na ativ..."},
    {"id": "SOB-2026-0216", "ct": "A", "ob": "Sapopemba", "tp": "Rede", "st": 10, "v": 33500.0, "d": 7, "nota": "NF-4460", "data": "06/08", "dep": "Conciliação", "area": "Fechamento", "ret": "Divergência de R$ 1.240 ..."},
    {"id": "SOB-2026-0209", "ct": "B", "ob": "Pirituba", "tp": "Transformador", "st": 11, "v": 41200.0, "d": 9, "nota": "NF-4447", "data": "04/08", "dep": "Conciliação", "area": "Fechamento", "ret": "Pago a menor: R$ 38.900"},
    {"id": "SOB-2026-0198", "ct": "A", "ob": "Lapa", "tp": "Rede", "st": 12, "v": 27600.0, "d": 12, "nota": "NF-4431", "data": "01/08", "dep": "Conciliação", "area": "Fechamento", "ret": "Em disputa desde 01/08"}
]
