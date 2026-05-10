# ResearchPulse API 🔬

> **Academic paper tracking and AI summarization backend** — built with FastAPI, PostgreSQL, Redis, and Gemini AI.

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-13%20Passing-brightgreen?logo=pytest)](https://pytest.org)
[![Live](https://img.shields.io/badge/Live-Render-46E3B7?logo=render)](https://researchpulse-ed5h.onrender.com/docs)

---

## 🌐 Live Demo

**API Base URL:** https://researchpulse-ed5h.onrender.com  
**Swagger Docs:** https://researchpulse-ed5h.onrender.com/docs  
**ReDoc:** https://researchpulse-ed5h.onrender.com/redoc

> ⚠️ Free tier — first request may take 50s to wake up.

---

## ✨ Features

- 🔐 **JWT Authentication** — Register, login, protected routes
- 📄 **Paper CRUD** — Add, update, delete, and list research papers
- 🔍 **arXiv Integration** — Search and fetch papers directly from arXiv
- 🤖 **AI Summarization** — Gemini AI-powered abstract summarization
- ⚡ **Redis Caching** — 236x faster repeated queries
- 🗂️ **Tags & Notes** — Organize papers with custom tags and notes
- 📬 **Weekly Digest** — Get a digest of unread papers
- ☁️ **File Upload** — Cloudinary-powered PDF/file storage
- 🛡️ **Rate Limiting** — Redis-backed request throttling (429)
- 🐳 **Docker Ready** — Full docker-compose setup
- ✅ **13 Tests** — Pytest suite for auth and papers endpoints

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy + Alembic |
| Cache | Redis |
| Auth | JWT (python-jose) + bcrypt |
| AI | Google Gemini AI |
| Storage | Cloudinary |
| Testing | Pytest + httpx |
| Deploy | Docker + Render |

---

## 📁 Project Structure

```
researchpulse/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── api/
│   │   ├── auth.py          # Register, login, /me
│   │   ├── papers.py        # Full paper CRUD + digest
│   │   └── files.py         # Cloudinary file upload
│   ├── core/
│   │   ├── config.py        # Pydantic settings
│   │   ├── security.py      # JWT + password hashing
│   │   ├── dependencies.py  # Auth middleware
│   │   └── limiter.py       # Redis rate limiting
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/
│   │   ├── arxiv.py         # arXiv API integration
│   │   ├── ai.py            # Gemini AI summarization
│   │   ├── cache.py         # Redis caching layer
│   │   ├── digest.py        # Weekly digest service
│   │   └── storage.py       # Cloudinary integration
│   └── db/                  # Database session + base
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_auth.py         # Auth endpoint tests
│   └── test_papers.py       # Papers endpoint tests
├── alembic/                 # Database migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- PostgreSQL
- Redis
- Docker (optional)

### 1. Clone the repo

```bash
git clone https://github.com/vedantgonbare/researchpulse.git
cd researchpulse
```

### 2. Set up environment

```bash
cp .env.example .env
# Fill in your values in .env
```

### 3. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/docs** 🎉

---

## 🐳 Docker Setup

```bash
docker-compose up --build
```

This starts:
- 🐘 PostgreSQL on port 5432
- 🔴 Redis on port 6379
- 🚀 FastAPI on port 8000

Run migrations inside Docker:
```bash
docker exec researchpulse_api alembic upgrade head
```

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | ❌ | Create a new account |
| POST | `/auth/login` | ❌ | Get JWT token |
| GET | `/auth/me` | ✅ | Get current user |

### Papers
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/papers/` | ✅ | List all your papers |
| POST | `/papers/` | ✅ | Add a paper |
| GET | `/papers/search?q=` | ❌ | Search arXiv |
| GET | `/papers/digest` | ✅ | Weekly digest |
| POST | `/papers/digest/mark-read` | ✅ | Mark papers as read |
| GET | `/papers/{id}` | ✅ | Get paper by ID |
| PATCH | `/papers/{id}` | ✅ | Update paper |
| DELETE | `/papers/{id}` | ✅ | Delete paper |
| POST | `/papers/{id}/summarize` | ✅ | AI summarize |

### Files
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/files/upload` | ✅ | Upload file to Cloudinary |

---

## ✅ Running Tests

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_auth.py::test_register_success PASSED
tests/test_auth.py::test_register_duplicate_email PASSED
tests/test_auth.py::test_login_success PASSED
tests/test_auth.py::test_login_wrong_password PASSED
tests/test_auth.py::test_get_me_authenticated PASSED
tests/test_auth.py::test_get_me_unauthenticated PASSED
tests/test_papers.py::test_get_papers_authenticated PASSED
tests/test_papers.py::test_get_papers_unauthenticated PASSED
tests/test_papers.py::test_search_papers PASSED
tests/test_papers.py::test_get_digest_authenticated PASSED
tests/test_papers.py::test_update_nonexistent_paper PASSED
tests/test_papers.py::test_delete_nonexistent_paper PASSED
tests/test_papers.py::test_root_endpoint PASSED

13 passed in 4.10s ✅
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/researchpulse
SECRET_KEY=your-secret-key-here-min-32-chars
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your-gemini-api-key-here
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
DEBUG=True
```

---

## 📈 Performance

- **Redis caching** delivers **236x faster** response times on repeated paper lookups
- Background tasks for marking papers as read (non-blocking)
- Rate limiting prevents abuse (429 on exceeded limits)

---

## 🗺️ Roadmap

- [ ] Email notifications for weekly digest
- [ ] Frontend dashboard (React)
- [ ] Semantic paper recommendations
- [ ] Multi-user collaboration on paper collections
- [ ] Citation graph visualization

---

## 👨‍💻 Author

**Vedant Gonbare**  
[![GitHub](https://img.shields.io/badge/GitHub-vedantgonbare-181717?logo=github)](https://github.com/vedantgonbare)

---

git add README.md