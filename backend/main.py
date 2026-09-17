"""
main.py — Entrypoint da aplicação FastAPI

Para rodar:
    uvicorn main:app --reload

Acesse a documentação interativa em:
    http://localhost:8000/docs
"""

from dotenv import load_dotenv
load_dotenv()  # Carrega variáveis do .env antes de qualquer import que precise delas

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# Importa todos os modelos para que o SQLAlchemy os reconheça ao criar as tabelas
import models  # noqa: F401

from routers import prompts, categories, tags
from routers import generate

# ─── Cria as tabelas no banco se não existirem ───────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── Aplicação ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="PromptForge API",
    description="Sistema gerador e gerenciador de prompts para IAs 🔨",
    version="1.0.0",
)

# CORS liberado para o frontend local (index.html aberto via file://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(prompts.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(generate.router)


@app.get("/", tags=["Status"], summary="Verificar status da API")
def root():
    return {"status": "ok", "app": "PromptForge", "docs": "/docs"}
