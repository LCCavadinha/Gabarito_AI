from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///gabarito.db", echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Professor(Base):
    __tablename__ = "professores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    turmas = relationship("Turma", back_populates="professor", cascade="all, delete-orphan")


class Turma(Base):
    __tablename__ = "turmas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    professor_id = Column(Integer, ForeignKey("professores.id"), nullable=False)
    professor = relationship("Professor", back_populates="turmas")
    alunos = relationship("Aluno", back_populates="turma", cascade="all, delete-orphan")
    provas = relationship("Prova", back_populates="turma", cascade="all, delete-orphan")


class Aluno(Base):
    __tablename__ = "alunos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    matricula = Column(String, unique=True, nullable=False)
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    turma = relationship("Turma", back_populates="alunos")
    notas = relationship("Nota", back_populates="aluno", cascade="all, delete-orphan")


class Prova(Base):
    __tablename__ = "provas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    turma = relationship("Turma", back_populates="provas")
    questoes = relationship("Questao", back_populates="prova", cascade="all, delete-orphan", order_by="Questao.numero")
    notas = relationship("Nota", back_populates="prova", cascade="all, delete-orphan")


class Questao(Base):
    __tablename__ = "questoes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(Integer, nullable=False)
    peso = Column(Float, nullable=False)
    alternativa_correta = Column(String(1), nullable=False)
    prova_id = Column(Integer, ForeignKey("provas.id"), nullable=False)
    prova = relationship("Prova", back_populates="questoes")
    __table_args__ = (UniqueConstraint("prova_id", "numero"),)


class Nota(Base):
    __tablename__ = "notas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pontuacao = Column(Float, nullable=False)
    respostas_json = Column(String)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    prova_id = Column(Integer, ForeignKey("provas.id"), nullable=False)
    aluno = relationship("Aluno", back_populates="notas")
    prova = relationship("Prova", back_populates="notas")
    __table_args__ = (UniqueConstraint("aluno_id", "prova_id"),)


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
