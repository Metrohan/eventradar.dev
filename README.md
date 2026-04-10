# TechEventRadar - Modern Full-Stack Refactor

Complete refactor from Flask to **FastAPI + React** architecture.

## 🏗️ Architecture

- **Backend**: FastAPI with PostgreSQL, JWT auth, REST API
- **Frontend**: React 18 + Vite, React Query, Bootstrap 5
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Deployment**: Docker Compose

## 🚀 Quick Start

### Docker (Recommended)
```bash
docker-compose up -d
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development
```bash
# Backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend  
cd frontend
npm install
npm run dev
```

## 📁 Structure
```
├── app/              # FastAPI backend source
│   ├── api/          # REST endpoints
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic validation
│   └── services/     # Business logic
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
├── scripts/          # Scraper and maintenance scripts
└── docker-compose.yml
```

## 🔄 Migration Summary

| Flask → FastAPI | Templates → React | Forms → React Hook Form |
|----------------|------------------|------------------------|
| Routes → REST API | HTML → Components | Server → Client |
| Sessions → JWT | Jinja2 → JSX | Validation → Pydantic |

## ✨ Features
- Event management (CRUD)
- Admin dashboard
- Event requests & suggestions
- Announcements
- JWT authentication
- Auto-generated API docs

## 🔧 Environment
```env
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_me

# Frontend
VITE_API_URL=http://localhost:8000
```

## 📚 API Endpoints
- `GET /api/events` - Public events
- `POST /api/admin/login` - Admin auth
- `GET /api/admin/events` - Admin events
- `POST /api/admin/events` - Create event
- Full docs at `/docs`

