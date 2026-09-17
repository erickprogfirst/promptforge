"""
models.py — Modelos ORM (mapeamento objeto-relacional)

Diagrama de relacionamentos:
  Category (1) ──< Prompt (N)
  Prompt    (N) >──< Tag   (M)   via tabela prompt_tags
  Prompt    (1) ──< PromptVersion (N)

Conceitos de BD praticados:
- Chaves primárias e estrangeiras
- Relacionamento 1:N e N:N
- Tabela associativa (junction table)
- Auto-referência de timestamps
- Índices para buscas eficientes
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Table, Boolean, Index
)
from sqlalchemy.orm import relationship
from database import Base


# ─── Tabela associativa N:N entre Prompt e Tag ─────────────────────────────
# Conceito: junction table resolve o relacionamento muitos-para-muitos
prompt_tags = Table(
    "prompt_tags",
    Base.metadata,
    Column("prompt_id", Integer, ForeignKey("prompts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id",    Integer, ForeignKey("tags.id",    ondelete="CASCADE"), primary_key=True),
)


# ─── Category ───────────────────────────────────────────────────────────────
class Category(Base):
    __tablename__ = "categories"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    # Relacionamento reverso: acessa category.prompts
    prompts = relationship("Prompt", back_populates="category")


# ─── Tag ────────────────────────────────────────────────────────────────────
class Tag(Base):
    __tablename__ = "tags"

    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    # Relacionamento N:N via tabela prompt_tags
    prompts = relationship("Prompt", secondary=prompt_tags, back_populates="tags")


# ─── Prompt ─────────────────────────────────────────────────────────────────
class Prompt(Base):
    __tablename__ = "prompts"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    content     = Column(Text, nullable=False)
    description = Column(String(500), nullable=True)
    is_favorite = Column(Boolean, default=False)
    use_count   = Column(Integer, default=0)  # quantas vezes foi usado
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # FK para Category (1:N)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category    = relationship("Category", back_populates="prompts")

    # N:N com Tag
    tags = relationship("Tag", secondary=prompt_tags, back_populates="prompts")

    # 1:N com versões (histórico)
    versions = relationship("PromptVersion", back_populates="prompt", cascade="all, delete-orphan")

    # Índice composto para buscas por título + favoritos
    __table_args__ = (
        Index("ix_prompts_title_favorite", "title", "is_favorite"),
    )


# ─── PromptVersion (histórico de versões) ───────────────────────────────────
class PromptVersion(Base):
    """
    Guarda um snapshot do conteúdo toda vez que um prompt é editado.
    Conceito: versionamento / auditoria de dados.
    """
    __tablename__ = "prompt_versions"

    id         = Column(Integer, primary_key=True, index=True)
    prompt_id  = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    version    = Column(Integer, nullable=False)  # 1, 2, 3 ...
    content    = Column(Text, nullable=False)
    saved_at   = Column(DateTime, default=datetime.utcnow)

    prompt = relationship("Prompt", back_populates="versions")
