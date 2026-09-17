"""
routers/prompts.py — Endpoints completos para prompts

Conceitos de BD aplicados aqui:
- SELECT com JOIN (category + tags)
- Filtros dinâmicos (WHERE)
- LIKE para busca textual
- UPDATE parcial (PATCH)
- Versionamento automático antes de salvar edição
- Incremento de contador (use_count)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from database import get_db
import models, schemas

router = APIRouter(prefix="/prompts", tags=["Prompts"])


def _get_or_404(db: Session, prompt_id: int) -> models.Prompt:
    prompt = db.query(models.Prompt).options(
        joinedload(models.Prompt.category),
        joinedload(models.Prompt.tags),
        joinedload(models.Prompt.versions),
    ).filter(models.Prompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt não encontrado.")
    return prompt


# ─── Listar / buscar ─────────────────────────────────────────────────────────
@router.get("/", response_model=list[schemas.PromptResponse], summary="Listar prompts")
def list_prompts(
    search:      str  = Query(None,  description="Busca por título ou conteúdo"),
    category_id: int  = Query(None,  description="Filtrar por categoria"),
    tag_id:      int  = Query(None,  description="Filtrar por tag"),
    favorite:    bool = Query(None,  description="Somente favoritos"),
    skip:        int  = Query(0,     ge=0),
    limit:       int  = Query(20,    ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Lista prompts com filtros opcionais.
    Demonstra: WHERE dinâmico, LIKE, JOIN com filtragem.
    """
    q = db.query(models.Prompt).options(
        joinedload(models.Prompt.category),
        joinedload(models.Prompt.tags),
    )

    if search:
        # LIKE nos dois campos — equivalente a: WHERE title LIKE '%x%' OR content LIKE '%x%'
        q = q.filter(or_(
            models.Prompt.title.ilike(f"%{search}%"),
            models.Prompt.content.ilike(f"%{search}%"),
        ))

    if category_id is not None:
        q = q.filter(models.Prompt.category_id == category_id)

    if favorite is not None:
        q = q.filter(models.Prompt.is_favorite == favorite)

    if tag_id is not None:
        # JOIN com a tabela associativa para filtrar por tag
        q = q.join(models.prompt_tags).filter(models.prompt_tags.c.tag_id == tag_id)

    return q.order_by(models.Prompt.updated_at.desc()).offset(skip).limit(limit).all()


# ─── Detalhe ─────────────────────────────────────────────────────────────────
@router.get("/{prompt_id}", response_model=schemas.PromptDetailResponse, summary="Buscar prompt por ID")
def get_prompt(prompt_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, prompt_id)


# ─── Criar ───────────────────────────────────────────────────────────────────
@router.post("/", response_model=schemas.PromptDetailResponse, status_code=status.HTTP_201_CREATED, summary="Criar prompt")
def create_prompt(data: schemas.PromptCreate, db: Session = Depends(get_db)):
    tag_ids = data.tag_ids
    prompt_data = data.model_dump(exclude={"tag_ids"})
    prompt = models.Prompt(**prompt_data)

    # Associa tags (valida existência antes)
    if tag_ids:
        tags = db.query(models.Tag).filter(models.Tag.id.in_(tag_ids)).all()
        if len(tags) != len(tag_ids):
            raise HTTPException(status_code=400, detail="Um ou mais tag_ids inválidos.")
        prompt.tags = tags

    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    # Salva versão inicial
    version = models.PromptVersion(prompt_id=prompt.id, version=1, content=prompt.content)
    db.add(version)
    db.commit()

    return _get_or_404(db, prompt.id)


# ─── Atualizar (PATCH) ────────────────────────────────────────────────────────
@router.patch("/{prompt_id}", response_model=schemas.PromptDetailResponse, summary="Atualizar prompt")
def update_prompt(prompt_id: int, data: schemas.PromptUpdate, db: Session = Depends(get_db)):
    """
    Atualização parcial.
    Se o conteúdo mudar, salva uma nova versão automaticamente (audit trail).
    """
    prompt = _get_or_404(db, prompt_id)
    update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})

    # Detecta mudança de conteúdo para versionar
    content_changed = "content" in update_data and update_data["content"] != prompt.content

    for field, value in update_data.items():
        setattr(prompt, field, value)

    if data.tag_ids is not None:
        tags = db.query(models.Tag).filter(models.Tag.id.in_(data.tag_ids)).all()
        prompt.tags = tags

    if content_changed:
        next_version = len(prompt.versions) + 1
        version = models.PromptVersion(
            prompt_id=prompt.id,
            version=next_version,
            content=update_data["content"],
        )
        db.add(version)

    db.commit()
    return _get_or_404(db, prompt_id)


# ─── Registrar uso ────────────────────────────────────────────────────────────
@router.post("/{prompt_id}/use", response_model=schemas.PromptResponse, summary="Registrar uso do prompt")
def use_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Incrementa o contador de uso — útil para analytics de prompts mais usados."""
    prompt = db.get(models.Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt não encontrado.")
    prompt.use_count += 1
    db.commit()
    db.refresh(prompt)
    return prompt


# ─── Favoritar ────────────────────────────────────────────────────────────────
@router.post("/{prompt_id}/favorite", response_model=schemas.PromptResponse, summary="Alternar favorito")
def toggle_favorite(prompt_id: int, db: Session = Depends(get_db)):
    """Alterna o status de favorito do prompt."""
    prompt = db.get(models.Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt não encontrado.")
    prompt.is_favorite = not prompt.is_favorite
    db.commit()
    db.refresh(prompt)
    return prompt


# ─── Deletar ──────────────────────────────────────────────────────────────────
@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir prompt")
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    prompt = db.get(models.Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt não encontrado.")
    db.delete(prompt)
    db.commit()


# ─── Histórico de versões ─────────────────────────────────────────────────────
@router.get("/{prompt_id}/versions", response_model=list[schemas.PromptVersionResponse], summary="Histórico de versões")
def get_versions(prompt_id: int, db: Session = Depends(get_db)):
    """Retorna todas as versões de um prompt em ordem cronológica."""
    prompt = db.get(models.Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt não encontrado.")
    return (
        db.query(models.PromptVersion)
        .filter(models.PromptVersion.prompt_id == prompt_id)
        .order_by(models.PromptVersion.version)
        .all()
    )
