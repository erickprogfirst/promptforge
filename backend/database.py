"""
database.py — Conexão com SQLite via SQLAlchemy

Conceitos de BD:
- Engine: representa a conexão com o banco
- Session: unidade de trabalho (transação)
- Base: classe base para os modelos ORM
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Caminho do arquivo SQLite (criado automaticamente na primeira execução)
DATABASE_URL = "sqlite:///../database/promptforge.db"

# check_same_thread=False necessário para SQLite com múltiplos requests
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True,  # Mostra as queries SQL no console — ótimo para aprendizado!
)

# Fábrica de sessões — cada request recebe sua própria sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base que todos os modelos ORM herdam."""
    pass


def get_db():
    """
    Dependency injection do FastAPI.
    Garante que a sessão seja fechada após cada request (padrão Unit of Work).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
