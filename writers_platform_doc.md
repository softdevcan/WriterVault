# Yazarlar Platformu - Proje Yapısı ve Geliştirme Rehberi

## 1. Proje Genel Bakış

### 1.1 Amaç
Yazarlar için modern, sürdürülebilir ve geliştirilebilir bir içerik paylaşım platformu.

### 1.2 Teknoloji Stack
- **Frontend:** Next.js 14 (App Router) + JavaScript
- **Backend:** FastAPI + Python 3.1+
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0
- **Authentication:** JWT + FastAPI Security
- **Styling:** Tailwind CSS + shadcn/ui
- **State Management:** Zustand
- **API Client:** Tanstack Query (React Query)
- **Validation:** Pydantic (Backend) + Zod (Frontend)

### 1.3 Proje Yapısı (Monorepo)
```
literati-platform/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py    # Environment variables
│   │   │   └── database.py    # Database configuration
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── article.py
│   │   │   ├── comment.py
│   │   │   └── category.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── article.py
│   │   │   ├── comment.py
│   │   │   └── auth.py
│   │   ├── repositories/      # Data access layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── article.py
│   │   │   └── comment.py
│   │   ├── services/          # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── article.py
│   │   │   └── email.py
│   │   ├── api/              # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── deps.py       # Dependencies
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── articles.py
│   │   │       └── comments.py
│   │   ├── core/             # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py   # JWT, password hashing
│   │   │   ├── exceptions.py # Custom exceptions
│   │   │   └── utils.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── conftest.py
│   │       ├── test_auth.py
│   │       └── test_articles.py
│   ├── alembic/              # Database migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile
├── frontend/                  # Next.js Frontend
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── profile/
│   │   │   ├── articles/
│   │   │   └── admin/
│   │   ├── components/       # React components
│   │   │   ├── ui/          # shadcn/ui components
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── Sidebar.tsx
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── RegisterForm.tsx
│   │   │   ├── articles/
│   │   │   │   ├── ArticleCard.tsx
│   │   │   │   ├── ArticleEditor.tsx
│   │   │   │   └── ArticleList.tsx
│   │   │   └── common/
│   │   │       ├── LoadingSpinner.tsx
│   │   │       └── ErrorBoundary.tsx
│   │   ├── lib/              # Utilities
│   │   │   ├── api.ts        # API client
│   │   │   ├── auth.ts       # Auth utilities
│   │   │   ├── utils.ts      # General utilities
│   │   │   └── validations.ts # Zod schemas
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useArticles.ts
│   │   │   └── useUsers.ts
│   │   ├── store/            # Zustand stores
│   │   │   ├── auth.ts
│   │   │   └── ui.ts
│   │   └── types/            # TypeScript types
│   │       ├── api.ts
│   │       ├── auth.ts
│   │       └── article.ts
│   ├── public/
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml
├── .gitignore
├── README.md
└── docs/
    ├── api.md
    ├── deployment.md
    └── development.md
```

## 2. Backend Detayları (FastAPI)

### 2.1 Core Yapı

#### 2.1.1 Settings (config/settings.py)
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Email
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### 2.1.2 Database Models (models/user.py)
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.config.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    bio = Column(Text)
    avatar_url = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    articles = relationship("Article", back_populates="author")
    comments = relationship("Comment", back_populates="author")
```

#### 2.1.3 Repository Pattern (repositories/base.py)
```python
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.config.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
```

#### 2.1.4 Service Layer (services/article.py)
```python
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.article import ArticleRepository
from app.repositories.user import UserRepository
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.models.article import Article
from app.core.exceptions import NotFoundError, PermissionError

class ArticleService:
    def __init__(self):
        self.article_repo = ArticleRepository()
        self.user_repo = UserRepository()
    
    def create_article(self, db: Session, article_data: ArticleCreate, author_id: int) -> Article:
        # Validate author exists
        author = self.user_repo.get(db, author_id)
        if not author:
            raise NotFoundError("Author not found")
        
        # Create article
        article_dict = article_data.dict()
        article_dict['author_id'] = author_id
        article_dict['slug'] = self._generate_slug(article_data.title)
        
        return self.article_repo.create(db, article_dict)
    
    def get_article(self, db: Session, article_id: int) -> Article:
        article = self.article_repo.get(db, article_id)
        if not article:
            raise NotFoundError("Article not found")
        return article
    
    def _generate_slug(self, title: str) -> str:
        # Implement slug generation logic
        pass
```

### 2.2 API Yapısı

#### 2.2.1 Dependencies (api/deps.py)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.core.security import verify_token
from app.repositories.user import UserRepository
from app.models.user import User

security = HTTPBearer()

def get_current_user(
    token: str = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    user_id = verify_token(token.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_repo = UserRepository()
    user = user_repo.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

## 3. Frontend Detayları (Next.js)

### 3.1 API Client (lib/api.ts)
```typescript
import { QueryClient } from '@tanstack/react-query'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  setToken(token: string) {
    this.token = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }

    return response.json()
  }

  // Auth endpoints
  async login(credentials: LoginCredentials) {
    return this.request<AuthResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
  }

  // Article endpoints
  async getArticles(params?: GetArticlesParams) {
    const queryString = params ? `?${new URLSearchParams(params)}` : ''
    return this.request<ArticleResponse[]>(`/api/v1/articles${queryString}`)
  }

  async createArticle(article: CreateArticleRequest) {
    return this.request<ArticleResponse>('/api/v1/articles', {
      method: 'POST',
      body: JSON.stringify(article),
    })
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})
```

### 3.2 Custom Hooks (hooks/useAuth.ts)
```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api'
import { useAuthStore } from '@/store/auth'

export function useAuth() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { user, setUser, clearUser } = useAuthStore()

  const loginMutation = useMutation({
    mutationFn: apiClient.login,
    onSuccess: (data) => {
      setUser(data.user)
      apiClient.setToken(data.access_token)
      queryClient.invalidateQueries({ queryKey: ['user'] })
      router.push('/dashboard')
    },
  })

  const logout = () => {
    clearUser()
    apiClient.setToken('')
    queryClient.clear()
    router.push('/login')
  }

  return {
    user,
    login: loginMutation.mutate,
    logout,
    isLoading: loginMutation.isPending,
  }
}
```

### 3.3 Zustand Store (store/auth.ts)
```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  username: string
  full_name: string
  is_admin: boolean
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  setUser: (user: User) => void
  clearUser: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: true }),
      clearUser: () => set({ user: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
)
```

## 4. Geliştirme Süreci

### 4.1 Geliştirme Ortamı Kurulumu

1. **Repository Clone**
   ```bash
   git clone <repository-url>
   cd literati-platform
   ```

2. **Backend Kurulum**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   pip install -r requirements-dev.txt
   ```

3. **Frontend Kurulum**
   ```bash
   cd frontend
   npm install
   ```

4. **Database Kurulum**
   ```bash
   # PostgreSQL kurulumu sonrası
   createdb literati_db
   cd backend
   alembic upgrade head
   ```

5. **Environment Variables**
   ```bash
   # backend/.env
   DATABASE_URL=postgresql://user:password@localhost/literati_db
   SECRET_KEY=your-secret-key
   
   # frontend/.env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### 4.2 Geliştirme Komutları

```bash
# Backend (FastAPI)
uvicorn app.main:app --reload --port 8000

# Frontend (Next.js)
npm run dev

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head

# Tests
pytest  # Backend
npm test  # Frontend
```

### 4.3 Özellik Geliştirme Süreci

1. **Planning Phase**
   - Özellik analizi ve tasarım
   - Database schema değişiklikleri
   - API endpoint planlaması

2. **Backend Development**
   - Model oluşturma/güncelleme
   - Repository layer geliştirme
   - Service layer business logic
   - API endpoints
   - Test yazma

3. **Frontend Development**
   - Type definitions
   - API client güncelleme
   - Custom hooks
   - Components
   - Pages/Routes

4. **Integration & Testing**
   - End-to-end testing
   - Performance testing
   - Security testing

## 5. Güvenlik ve Best Practices

### 5.1 Authentication & Authorization
- JWT token based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Rate limiting
- CORS configuration

### 5.2 Data Validation
- Pydantic models (backend)
- Zod schemas (frontend)
- Input sanitization
- SQL injection prevention

### 5.3 Error Handling
- Structured error responses
- Logging system
- Error boundary components
- Graceful degradation

### 5.4 Performance
- Database indexing
- Query optimization
- Caching strategies
- Image optimization
- Code splitting

## 6. Deployment ve DevOps

### 6.1 Docker Configuration
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 CI/CD Pipeline (GitHub Actions)
```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test Backend
        run: |
          cd backend
          pip install -r requirements-dev.txt
          pytest
      - name: Test Frontend
        run: |
          cd frontend
          npm install
          npm test
```

### 6.3 Monitoring ve Logging
- Sentry error tracking
- Prometheus metrics
- Structured logging
- Health check endpoints

## 7. Gelecek Geliştirmeler

### 7.1 Phase 1 (MVP)
- User authentication
- Article CRUD
- Basic admin panel
- Comment system

### 7.2 Phase 2 (Advanced Features)
- Advanced search
- User following system
- Email notifications
- Rich text editor

### 7.3 Phase 3 (Scale)
- Real-time features
- Mobile app
- Analytics dashboard
- API rate limiting

### 7.4 Phase 4 (Enterprise)
- Microservices migration
- Advanced caching
- CDN integration
- Multi-language support

## 8. Dokümantasyon ve Maintenance

### 8.1 Dokümantasyon
- API documentation (FastAPI auto-generated)
- Component documentation (Storybook)
- Architecture decision records
- User guides

### 8.2 Code Quality
- Pre-commit hooks
- ESLint/Prettier (frontend)
- Black/isort (backend)
- Type checking (mypy, TypeScript)

### 8.3 Testing Strategy
- Unit tests
- Integration tests
- E2E tests (Playwright)
- Performance tests

Bu proje yapısı, side project olarak başlayıp büyük bir platform haline gelene kadar sürdürülebilir ve geliştirilebilir bir temel sağlar. Modüler yapısı sayesinde her bileşen bağımsız olarak geliştirilebilir ve test edilebilir.