from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Numeric, Float, Date, DateTime, BigInteger, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Perfil(Base):
    __tablename__ = 'perfis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), unique=True, nullable=False, index=True)
    descricao = Column(String(255), nullable=True)
    is_master = Column(Boolean, default=False, nullable=False)
    telas = Column(JSON, nullable=False, default=list)

    usuarios = relationship("Usuario", back_populates="perfil")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "is_master": self.is_master,
            "telas": self.telas
        }

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    perfil_id = Column(Integer, ForeignKey('perfis.id'), nullable=False)
    telas_custom = Column(JSON, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    perfil = relationship("Perfil", back_populates="usuarios")
    historico_tramitacoes = relationship("HistoricoTramitacao", back_populates="usuario")
    pendencias_tratadas = relationship("Pendencia", back_populates="usuario_tratativa")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "perfil": self.perfil.nome if self.perfil else None,
            "telas_custom": self.telas_custom,
            "ativo": self.ativo
        }

class Servico(Base):
    __tablename__ = 'servicos'

    id = Column(String(50), primary_key=True) # Ex: SOB-363559559
    num_servico = Column(String(50), unique=True, nullable=False, index=True)
    contrato = Column(String(100), nullable=True, index=True)
    nome_obra = Column(String(200), nullable=True)
    bairro = Column(String(100), nullable=True)
    localidade = Column(String(100), nullable=True)
    tipo_servico = Column(String(100), nullable=True, index=True)
    status_id = Column(Integer, nullable=False, default=1, index=True) # 1 a 15
    valor = Column(Numeric(12, 2), default=0.00)
    sla_dias = Column(Integer, default=3)
    nota_medicao = Column(String(50), nullable=True)
    data_execucao = Column(Date, nullable=True)
    centro_servico = Column(String(100), nullable=True)
    retorno_campo = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pendencias = relationship("Pendencia", back_populates="servico", cascade="all, delete-orphan")
    baremo_itens = relationship("BaremoItem", back_populates="servico", cascade="all, delete-orphan")
    historico_tramitacoes = relationship("HistoricoTramitacao", back_populates="servico", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "num_servico": self.num_servico,
            "ct": self.contrato or "A",
            "ob": self.nome_obra or f"{self.bairro or ''} · {self.localidade or ''}".strip(" · "),
            "tp": self.tipo_servico or "Rede",
            "st": self.status_id,
            "v": float(self.valor or 0),
            "d": self.sla_dias,
            "nota": self.nota_medicao or f"NM-{self.num_servico[-4:]}",
            "data": self.data_execucao.strftime('%Y-%m-%d') if self.data_execucao else "Hoje",
            "dep": self.centro_servico or "—",
            "ret": self.retorno_campo or "",
            "pend": [p.to_dict() for p in self.pendencias]
        }

class Pendencia(Base):
    __tablename__ = 'pendencias'

    id = Column(Integer, primary_key=True, autoincrement=True)
    servico_id = Column(String(50), ForeignKey('servicos.id'), nullable=False, index=True)
    tipo = Column(String(50), nullable=False) # Fotos, Materiais, Documentos, Retorno, Outros
    tratado = Column(Boolean, default=False, nullable=False) # Flag da RN-04
    detalhe_tratativa = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    servico = relationship("Servico", back_populates="pendencias")
    usuario_tratativa = relationship("Usuario", back_populates="pendencias_tratadas")
    anexos = relationship("Anexo", back_populates="pendencia", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "t": self.tipo,
            "tr": self.tratado,
            "det": self.detalhe_tratativa or "",
            "anx": [a.nome_arquivo for a in self.anexos]
        }

class Anexo(Base):
    __tablename__ = 'anexos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pendencia_id = Column(Integer, ForeignKey('pendencias.id'), nullable=False, index=True)
    nome_arquivo = Column(String(255), nullable=False)
    caminho_storage = Column(String(500), nullable=False)
    tamanho_bytes = Column(BigInteger, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    pendencia = relationship("Pendencia", back_populates="anexos")

class BaremoItem(Base):
    __tablename__ = 'baremo_itens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    servico_id = Column(String(50), ForeignKey('servicos.id'), nullable=False, index=True)
    codigo_item = Column(String(20), nullable=False)
    descricao = Column(String(255), nullable=False)
    quantidade = Column(Float, default=1.0)
    valor_medido = Column(Numeric(12, 2), default=0.00)

    servico = relationship("Servico", back_populates="baremo_itens")

    def to_dict(self):
        return {
            "cod": self.codigo_item,
            "desc": self.descricao,
            "qtd": self.quantidade,
            "med": float(self.valor_medido or 0)
        }

class HistoricoTramitacao(Base):
    __tablename__ = 'historico_tramitacao'

    id = Column(Integer, primary_key=True, autoincrement=True)
    servico_id = Column(String(50), ForeignKey('servicos.id'), nullable=False, index=True)
    status_de = Column(Integer, nullable=False)
    status_para = Column(Integer, nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    observacao = Column(Text, nullable=True)
    data_tramitacao = Column(DateTime, default=datetime.utcnow)

    servico = relationship("Servico", back_populates="historico_tramitacoes")
    usuario = relationship("Usuario", back_populates="historico_tramitacoes")
