from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from app.api import auth, repositories, webhooks
from app.config import settings

app = FastAPI(title="GitHub Analyzer", description="Análise inteligente de repositórios GitHub")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Incluir routers da API
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(repositories.router, prefix="/api", tags=["repositories"])
app.include_router(webhooks.router, prefix="/api", tags=["webhooks"])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página inicial - verifica se usuário está autenticado"""
    user = request.session.get('user')
    if user:
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal com lista de repositórios"""
    user = request.session.get('user')
    if not user:
        return templates.TemplateResponse("login.html", {"request": request})
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
