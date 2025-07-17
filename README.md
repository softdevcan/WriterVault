# Writers Platform

Yazarlar için modern bir içerik paylaşım platformu.

## Proje Yapısı

```
writers/
├── backend/          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── requirements.txt
│   └── env.example
├── frontend/         # Next.js Frontend
│   ├── src/
│   ├── package.json
│   └── env.local.example
├── writers_platform_doc.md
└── README.md
```

## Teknoloji Stack

- **Backend:** FastAPI + Python 3.11+
- **Frontend:** Next.js 14 (App Router) + TypeScript
- **Styling:** Tailwind CSS

## Geliştirme

### Backend Kurulum

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Backend Çalıştırma

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Kurulum

```bash
cd frontend
npm install
```

### Frontend Çalıştırma

```bash
cd frontend
npm run dev
```

## API Endpoints

- **GET /** - Ana endpoint
- **GET /health** - Health check endpoint

## Lisans

MIT 