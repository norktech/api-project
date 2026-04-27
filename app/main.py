from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger
import sys

from app.config import get_settings
from app.database import Base, engine
from app.middleware import LoggingMiddleware
from app.auth import verify_token, hash_password, verify_password, create_token
from app.schemas import TokenResponse, LoginRequest
from app.routes import books, stats

# ── Settings ──────────────────────────────────────────────────
settings = get_settings()

# ── Logging ───────────────────────────────────────────────────
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>")
logger.add("logs/api.log", rotation="10 MB", retention="30 days", level="INFO")

# ── Rate Limiter ──────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title=settings.API_TITLE,
    description="""
## NorkTech Books API v3.0

Professional REST API for scraped book data.

### Features
- 🔐 JWT Authentication
- 📄 Pagination & Filtering
- 📊 Statistics
- 🛡️ Rate Limiting
- 📝 Request Logging
- 🌐 CORS Support

### How to authenticate
1. POST /auth/login with credentials
2. Copy the access_token
3. Click **Authorize** and paste the token
""",
    version=settings.API_VERSION,
    contact={"name": "NorkTech", "url": "https://github.com/norktech"},
    license_info={"name": "MIT"}
)

# ── Middleware ────────────────────────────────────────────────
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Database ──────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Users ─────────────────────────────────────────────────────
USERS = {
    settings.ADMIN_USERNAME: hash_password(settings.ADMIN_PASSWORD)
}

# ── Auth Routes ───────────────────────────────────────────────
@app.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    username = credentials.username
    password = credentials.password
    if username not in USERS or not verify_password(password, USERS[username]):
        logger.warning(f"Failed login attempt for user: {username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(username)
    return {"access_token": token, "token_type": "bearer"}

# ── General Routes ────────────────────────────────────────────
@app.get("/", tags=["General"])
def home():
    return {
        "api": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "online",
        "docs": "/docs",
        "github": "https://github.com/norktech"
    }

@app.get("/health", tags=["General"])
def health():
    return {"status": "healthy", "version": settings.API_VERSION}

# ── Routers ───────────────────────────────────────────────────
app.include_router(books.router)
app.include_router(stats.router)