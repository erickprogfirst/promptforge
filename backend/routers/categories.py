"""
routers/categories.py — Endpoints CRUD para categorias
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/categories", tags=["Categorias"])


@router.get("/", response_model=list[schemas.CategoryResponse], summary="Listar categorias")
def list_categories(db: Session = Depends(get_db)):
    """Lista todas as categorias."""
    return db.query(models.Category).order_by(models.Category.name).all()


@router.post("/", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED, summary="Criar categoria")
def create_category(data: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """Cria uma nova categoria. Retorna 409 se o nome já existir."""
    if db.query(models.Category).filter(models.Category.name == data.name).first():
        raise HTTPException(status_code=409, detail="Categoria já existe.")
    category = models.Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir categoria")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Remove uma categoria (os prompts ficam sem categoria)."""
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.")
    db.delete(category)
    db.commit()
