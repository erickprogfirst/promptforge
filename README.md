# PromptForge 🔨

> Sistema completo para **gerar, organizar e gerenciar prompts para IAs** — com geração automática via GPT-4o-mini.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-SQLAlchemy-003B57?style=flat&logo=sqlite&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat&logo=openai&logoColor=white)

---

## ✨ Funcionalidades

- **Gerenciador de prompts** — crie, edite, favorite e organize seus prompts
- **Gerador com IA** — formulário guiado que gera prompts profissionais via GPT-4o-mini
- **Categorias e Tags** — organize prompts com categorias e tags livres (N:N)
- **Histórico de versões** — cada edição salva um snapshot automático do conteúdo
- **Busca e filtros** — busca por texto, filtre por categoria, tag ou favoritos
- **Contador de uso** — saiba quais prompts você mais utiliza
- **API REST documentada** — Swagger UI em `/docs`

---

## 🖼️ Interface

Interface web em HTML/CSS/JS puro com tema escuro, sem dependências de framework.

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.10+ + FastAPI |
| Banco de dados | SQLite via SQLAlchemy 2.0 (ORM) |
| Validação | Pydantic v2 |
| IA | OpenAI API (GPT-4o-mini) |
| Frontend | HTML + CSS + JavaScript puro |

---

## 📁 Estrutura

```
promptforge/
├── backend/
│   ├── main.py              # Entrypoint FastAPI
│   ├── database.py          # Engine e sessão SQLite
│   ├── models.py            # Modelos ORM (tabelas)
│   ├── schemas.py           # Schemas Pydantic
│   ├── routers/
│   │   ├── prompts.py       # CRUD completo de prompts
│   │   ├── categories.py    # CRUD de categorias
│   │   ├── tags.py          # CRUD de tags
│   │   └── generate.py      # Geração via OpenAI
│   ├── .env.example         # Modelo de variáveis de ambiente
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Interface principal
│   ├── style.css            # Tema escuro
│   └── app.js               # Lógica do frontend
└── database/
    └── promptforge.db       # Gerado automaticamente
```

---

## 🚀 Como rodar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/erickprogfirst/promptforge.git
cd promptforge
```

### 2. Instale as dependências

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure a chave da OpenAI

```bash
cp .env.example .env
```

Edite o arquivo `.env` e insira sua chave:

```
OPENAI_API_KEY=sk-sua-chave-aqui
```

> Sem a chave, o gerenciador funciona normalmente. Só a funcionalidade de geração com IA fica indisponível.

### 4. Inicie o servidor

```bash
uvicorn main:app --reload
```

### 5. Abra o frontend

Abra o arquivo `frontend/index.html` diretamente no navegador.

| URL | Descrição |
|---|---|
| `frontend/index.html` | Interface principal |
| http://localhost:8000/docs | Documentação interativa da API |
| http://localhost:8000 | Health check da API |

---

## 🗄️ Modelo de dados

```
Category (1) ──< Prompt (N)
Prompt    (N) >──< Tag   (M)   via tabela prompt_tags
Prompt    (1) ──< PromptVersion (N)
```

**Conceitos de BD praticados:**
- Relacionamentos 1:N e N:N
- Tabela associativa (junction table)
- Cascade delete
- Índices compostos para busca
- Versionamento / audit trail

---

## 🤖 Gerador com IA

O formulário guiado coleta:

| Campo | Exemplo |
|---|---|
| Objetivo | "Revisar textos acadêmicos" |
| Público-alvo | "Estudantes universitários" |
| Tom | Formal / Casual / Técnico / Criativo / Direto |
| Formato | Texto / Lista / Passo a passo / Tabela / Markdown |
| Contexto | Detalhes extras (opcional) |

O backend envia esses parâmetros ao GPT-4o-mini e retorna um prompt profissional pronto para uso. O resultado pode ser copiado ou salvo diretamente no gerenciador.

---

## 🔒 Segurança

- A chave da OpenAI fica **somente no backend** (variável de ambiente)
- O frontend **nunca** acessa a chave diretamente
- O arquivo `.env` está no `.gitignore` e nunca é versionado

---

## 🤝 Como esse projeto foi criado

Este projeto foi desenvolvido de forma **colaborativa com o [IBM Bob](https://www.ibm.com/bob)**, um assistente de engenharia de software com IA.

O fluxo de desenvolvimento foi inteiramente conversacional — sem templates prontos, sem scaffolding automático. Cada arquivo foi discutido, projetado e implementado em conjunto:

| Etapa | O que foi feito |
|---|---|
| Modelagem do banco | Definição das tabelas, relacionamentos 1:N e N:N, junction table, índices e versionamento |
| Backend | FastAPI com routers, schemas Pydantic, ORM SQLAlchemy 2.0, dependency injection |
| Frontend | Interface completa em HTML/CSS/JS puro com tema escuro, modais, filtros e busca |
| Integração com IA | Rota de geração via OpenAI GPT-4o-mini com formulário guiado e salvamento direto |
| Segurança | `.gitignore`, `.env.example`, chave restrita na OpenAI, chave nunca exposta no frontend |
| Publicação | Repositório criado e publicado no GitHub via API, com README completo |

> Todo o código foi escrito do zero durante a conversa — nenhuma linha foi copiada de template externo.

---

## 📄 Licença

MIT
