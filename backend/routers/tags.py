"""
routers/tags.py — Endpoints CRUD para tags
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("/", response_model=list[schemas.TagResponse], summary="Listar tags")
def list_tags(db: Session = Depends(get_db)):
    return db.query(models.Tag).order_by(models.Tag.name).all()


@router.post("/", response_model=schemas.TagResponse, status_code=status.HTTP_201_CREATED, summary="Criar tag")
def create_tag(data: schemas.TagCreate, db: Session = Depends(get_db)):
    if db.query(models.Tag).filter(models.Tag.name == data.name).first():
        raise HTTPException(status_code=409, detail="Tag já existe.")
    tag = models.Tag(**data.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir tag")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.get(models.Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag não encontrada.")
    db.delete(tag)
    db.commit()
