"""
schemas.py — Schemas Pydantic para validação de entrada e saída da API

Conceito: separação entre o modelo de BD (ORM) e o contrato da API.
Cada entidade tem:
  - XxxBase     → campos comuns
  - XxxCreate   → campos necessários para criar
  - XxxUpdate   → campos opcionais para atualizar (PATCH)
  - XxxResponse → o que a API devolve (inclui id, timestamps)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ─── Tag ────────────────────────────────────────────────────────────────────
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, examples=["copywriting"])


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    model_config = {"from_attributes": True}


# ─── Category ───────────────────────────────────────────────────────────────
class CategoryBase(BaseModel):
    name:        str            = Field(..., min_length=1, max_length=100, examples=["Escrita"])
    description: Optional[str] = Field(None, max_length=255)


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id:         int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── PromptVersion ──────────────────────────────────────────────────────────
class PromptVersionResponse(BaseModel):
    id:       int
    version:  int
    content:  str
    saved_at: datetime

    model_config = {"from_attributes": True}


# ─── Prompt ─────────────────────────────────────────────────────────────────
class PromptBase(BaseModel):
    title:       str            = Field(..., min_length=1, max_length=200, examples=["Revisor de texto"])
    content:     str            = Field(..., min_length=1, examples=["Você é um revisor de textos especialista..."])
    description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None


class PromptCreate(PromptBase):
    tag_ids: list[int] = Field(default_factory=list, description="IDs das tags a associar")


class PromptUpdate(BaseModel):
    title:       Optional[str] = Field(None, min_length=1, max_length=200)
    content:     Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    category_id: Optional[int] = None
    is_favorite: Optional[bool] = None
    tag_ids:     Optional[list[int]] = None


class PromptResponse(PromptBase):
    id:          int
    is_favorite: bool
    use_count:   int
    created_at:  datetime
    updated_at:  datetime
    category:    Optional[CategoryResponse] = None
    tags:        list[TagResponse] = []

    model_config = {"from_attributes": True}


class PromptDetailResponse(PromptResponse):
    versions: list[PromptVersionResponse] = []

    model_config = {"from_attributes": True}
