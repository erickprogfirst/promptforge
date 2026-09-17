"""
routers/generate.py — Geração de prompts via OpenAI

Recebe parâmetros de um formulário guiado e retorna um prompt
profissional gerado pelo GPT-4o-mini.
"""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI, AuthenticationError, RateLimitError

router = APIRouter(prefix="/generate", tags=["Gerador IA"])

# Cliente OpenAI inicializado com a variável de ambiente OPENAI_API_KEY
_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-..."):
            raise HTTPException(
                status_code=503,
                detail="Chave da OpenAI não configurada. Defina OPENAI_API_KEY no arquivo .env.",
            )
        _client = OpenAI(api_key=api_key)
    return _client


# ─── Schema de entrada ────────────────────────────────────────────────────────
class GenerateRequest(BaseModel):
    objetivo: str = Field(..., min_length=5, max_length=300,
                          description="O que você quer que a IA faça?",
                          examples=["Revisar e melhorar textos acadêmicos"])
    publico:  str = Field(..., min_length=2, max_length=100,
                          description="Para quem é esse prompt?",
                          examples=["Estudantes universitários"])
    tom:      str = Field(..., description="Tom da resposta da IA",
                          examples=["formal", "casual", "técnico", "criativo", "direto"])
    formato:  str = Field(..., description="Formato de saída esperado",
                          examples=["texto corrido", "lista", "passo a passo", "tabela", "markdown"])
    contexto: Optional[str] = Field(None, max_length=500,
                                    description="Contexto ou detalhes extras (opcional)")


class GenerateResponse(BaseModel):
    prompt: str
    tokens_usados: int


# ─── Endpoint ─────────────────────────────────────────────────────────────────
@router.post("/", response_model=GenerateResponse, summary="Gerar prompt com IA")
def generate_prompt(data: GenerateRequest):
    """
    Recebe parâmetros de um formulário guiado e usa o GPT-4o-mini
    para gerar um prompt profissional pronto para uso.
    """
    client = get_client()

    # Monta o meta-prompt que instrui o GPT a criar o prompt
    system = (
        "Você é um especialista em engenharia de prompts para IAs generativas. "
        "Sua tarefa é criar prompts claros, detalhados e eficazes com base nos "
        "parâmetros fornecidos pelo usuário. "
        "Retorne APENAS o prompt final, sem explicações, sem aspas, sem prefixos."
    )

    partes = [
        f"Crie um prompt profissional com as seguintes características:",
        f"- Objetivo: {data.objetivo}",
        f"- Público-alvo: {data.publico}",
        f"- Tom: {data.tom}",
        f"- Formato de saída esperado: {data.formato}",
    ]
    if data.contexto:
        partes.append(f"- Contexto adicional: {data.contexto}")

    user_message = "\n".join(partes)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user_message},
            ],
            temperature=0.7,
            max_tokens=800,
        )
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Chave da OpenAI inválida.")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Limite de requisições da OpenAI atingido. Tente novamente em instantes.")

    prompt_gerado = response.choices[0].message.content.strip()
    tokens = response.usage.total_tokens

    return GenerateResponse(prompt=prompt_gerado, tokens_usados=tokens)
