# Nexora — AI Knowledge & Workflow Assistant

> A full-stack AI knowledge assistant built with RAG, persistent conversations, source attribution, and LLM provider abstraction.

[Live Demo](https://nexora-ai-chi-nine.vercel.app) · [GitHub Repository](https://github.com/priyaphalswal9-ui/enterprise-ai-assistant)

---

## Key Features

- JWT-based authentication
- Persistent conversations and messages
- Document upload and processing
- Gemini-based embeddings
- Qdrant vector search
- Multi-stage RAG pipeline
- Query rewriting
- Semantic reranking
- Relative relevance filtering
- Maximum Marginal Relevance (MMR)
- Source attribution
- SSE-based response streaming
- Gemini and Ollama provider abstraction
- Retrieval evaluation

---

## System Architecture

```text
                         ┌──────────────────────┐
                         │     React + Vite     │
                         │       Frontend       │
                         └──────────┬───────────┘
                                    │
                               HTTP / SSE
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │       Backend        │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      Authentication         Conversations           Documents
          + JWT              + Messages              + Ingestion
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      AI Service      │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
             ┌─────────────┐                ┌────────────────┐
             │ RAG Pipeline│                │Provider Factory │
             └──────┬──────┘                └───────┬────────┘
                    │                               │
                    ▼                         ┌─────┴─────┐
             ┌─────────────┐                  │           │
             │Qdrant Cloud │                  ▼           ▼
             │Vector Search│               Gemini       Ollama
             └──────┬──────┘              Production     Local
                    │
                    ▼
             Retrieved Context
                    │
                    ▼
                   LLM
                    │
                    ▼
             Answer + Sources
                    │
                    ▼
                SSE Stream
                    │
                    ▼
                Frontend
```

---

## Query Flow

```text
User Query
    ↓
React Frontend
    ↓
FastAPI API
    ↓
JWT Authentication
    ↓
Conversation Context
    ↓
AI Service
    ↓
Query Rewriting
    ↓
Candidate Retrieval
    ↓
Deduplication
    ↓
Semantic Reranking
    ↓
Relative Relevance Filtering
    ↓
MMR
    ↓
Final Context
    ↓
Prompt Construction
    ↓
LLM
    ↓
Answer + Sources
    ↓
SSE Stream
    ↓
React Frontend
```

---

## RAG Pipeline

Nexora uses a multi-stage retrieval pipeline instead of directly passing the initial top-k vector search results to the LLM.

```text
                         User Query
                             │
                             ▼
                    Conditional Rewrite
                             │
                             ▼
                    Candidate Retrieval
                             │
                             ▼
                       Deduplication
                             │
                             ▼
                    Semantic Reranking
                             │
                             ▼
                 Relative Relevance Filter
                             │
                             ▼
                            MMR
                             │
                             ▼
                      Final Context
                             │
                             ▼
                            LLM
                             │
                             ▼
                     Answer + Sources
```

### Query Rewriting

The query can be reformulated when useful before retrieval to improve the search query while preserving the user's intended meaning.

### Semantic Reranking

Initial vector retrieval produces a candidate set. Nexora then semantically reranks the candidates before selecting the final context.

### Relative Relevance Filtering

Candidates are filtered relative to the strongest retrieved result.

```text
candidate_score >= 0.65 × best_score
```

### Maximum Marginal Relevance (MMR)

MMR balances:

```text
Relevance + Diversity
```

This helps reduce redundant chunks while retaining useful information in the final context.

```text
Candidate Chunks
       ↓
Relevance + Diversity
       ↓
      MMR
       ↓
Final Context
```

---

## Document Ingestion

```text
Document Upload
      ↓
Supabase Storage
      ↓
Text Extraction
      ↓
Chunking
      ↓
Gemini Embeddings
      ↓
Qdrant Cloud
```

Retrieved chunks retain source information for answer attribution.

---

## LLM Provider Architecture

Nexora uses a provider abstraction so the AI service is not tightly coupled to a single LLM provider.

```text
                    ┌──────────────┐
                    │  AI Service  │
                    └──────┬───────┘
                           │
                    Provider Factory
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
        ┌───────────────┐     ┌───────────────┐
        │    Gemini     │     │    Ollama     │
        │  Production   │     │     Local     │
        └───────────────┘     └───────────────┘
```

### Production

- Gemini 2.5 Flash — generation
- Gemini Embedding 2 — embeddings

### Local Development

- Ollama — local LLM experimentation

The deployed backend uses Gemini through its API and does not depend on a locally running Ollama instance.

---

## Authentication & Persistence

Nexora uses JWT-based authentication for protected API endpoints.

```text
                    User
                     │
                     ▼
              Login / Register
                     │
                     ▼
                FastAPI Auth
                     │
                     ▼
                 JWT Token
                     │
                     ▼
            Protected API Requests
                     │
                     ▼
              JWT Verification
                     │
                     ▼
              Authorized User
```

PostgreSQL stores persistent application data:

```text
Users
  │
  ├── Conversations
  │       │
  │       └── Messages
  │
  └── Authentication Data
```

SQLAlchemy is used for database interaction and Alembic for schema migrations.

---

## Streaming

Responses are streamed using Server-Sent Events (SSE).

```text
LLM Generation
      ↓
FastAPI
      ↓
SSE Stream
      ↓
React Frontend
      ↓
Incremental Response
```

---

## Source Attribution

For document-grounded questions, retrieved chunks retain source information.

```text
Document
   ↓
Chunks
   ↓
Embeddings
   ↓
Qdrant
   ↓
Retrieved Chunks
   ↓
Context
   ↓
LLM
   ↓
Answer + Sources
```

---

## Evaluation

A small manually prepared retrieval evaluation set was used to check whether expected information was retrieved correctly.

| Metric | Result |
|---|---:|
| Hit@3 | 5/5 — 100% |
| MRR | 1.00 |

For the five test cases:

- The expected relevant result appeared within the top 3 in all cases.
- The relevant result appeared at rank 1 in all cases.

These results are an initial retrieval sanity check and should not be interpreted as production-scale retrieval performance.

LLM-as-a-judge evaluation was also explored, with results varying across evaluator models.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite |
| Backend | FastAPI, Python |
| Database | PostgreSQL |
| ORM / Migrations | SQLAlchemy, Alembic |
| Vector Database | Qdrant Cloud |
| Storage | Supabase Storage |
| LLM | Gemini 2.5 Flash |
| Embeddings | Gemini Embedding 2 |
| Local LLM | Ollama |
| AI Workflows | LangGraph |
| Streaming | Server-Sent Events |
| Deployment | Vercel, Render |

---

## Project Structure

```text
enterprise-ai-assistant/
│
├── backend/
│   └── app/
│       ├── api/
│       │   └── v1/
│       │       ├── auth.py
│       │       ├── conversations.py
│       │       ├── documents.py
│       │       ├── evaluations.py
│       │       └── messages.py
│       │
│       ├── ai/
│       │   ├── ai_service.py
│       │   ├── base_provider.py
│       │   ├── context_builder.py
│       │   ├── gemini_provider.py
│       │   ├── ollama_provider.py
│       │   ├── provider_factory.py
│       │   ├── rag_prompt.py
│       │   ├── system_prompt.py
│       │   ├── tools.py
│       │   ├── tool_executor.py
│       │   └── tool_registry.py
│       │
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       └── main.py
│
├── frontend/
├── README.md
└── .gitignore
```

---

## Deployment

```text
React + Vite
     ↓
   Vercel
     ↓
 FastAPI
     ↓
  Render
     │
     ├── PostgreSQL
     ├── Qdrant Cloud
     ├── Supabase Storage
     └── Gemini API
```

Production AI flow:

```text
Frontend
   ↓
Render Backend
   ↓
AI Service
   ↓
Gemini API
```

Production does not depend on a local Ollama server.

---

## Deployment Health Checks

The deployed application was verified across the main system layers.

```text
Frontend
   ↓
Backend API
   ↓
Authentication
   ↓
Database
   ↓
Document Upload
   ↓
Vector Retrieval
   ↓
Gemini Generation
   ↓
SSE Streaming
   ↓
Source Attribution
```

### Verified

- Frontend deployment loads successfully
- Backend deployment is reachable
- FastAPI API documentation is available
- Authentication flow works
- Protected API requests work
- Conversations persist in PostgreSQL
- Documents can be uploaded
- Document processing works
- Vector retrieval works through Qdrant
- Gemini generation works in production
- SSE response streaming works
- Source attribution works for document-grounded responses

---

## Local Setup

### Backend

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the required dependencies and configure environment variables for:

- PostgreSQL
- Gemini API
- Qdrant
- Supabase
- JWT
- CORS

Run the backend:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

### Optional Ollama

Ollama can be used for local LLM experimentation.

It is not required for the deployed application.

---

## Live Demo

[Open Nexora](https://nexora-ai-chi-nine.vercel.app)

---

## Demo Video

A walkthrough of Nexora will be shared on LinkedIn.

_Link will be added after the LinkedIn demo post is published._

---

## What I Learned

Nexora helped me understand how an LLM-powered application is engineered beyond the chatbot interface.

Key areas covered:

- RAG and vector retrieval
- Query rewriting
- Semantic reranking
- Maximum Marginal Relevance
- LLM provider abstraction
- FastAPI backend architecture
- PostgreSQL persistence
- JWT authentication
- SSE streaming
- Retrieval evaluation
- Local and cloud deployment

---

## Future Improvements

- Larger retrieval evaluation datasets
- Automated retrieval regression tests
- Better document metadata and filtering
- Support for additional document types
- Additional tool integrations
- Observability and tracing
- Stronger document-level access control

---

## Repository

[GitHub — Nexora](https://github.com/priyaphalswal9-ui/enterprise-ai-assistant)

---

## Final Perspective

Nexora started with a simple question:

> What does it actually take to build an AI assistant beyond the chatbot interface?

The project became an opportunity to work through that question across the full application stack — from frontend and APIs to databases, document ingestion, retrieval, LLM providers, evaluation, and deployment.
