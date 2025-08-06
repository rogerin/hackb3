from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings

router = APIRouter()

oauth = OAuth()
oauth.register(
    name='github',
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'repo admin:repo_hook'},
)

async def get_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

@router.get('/login/github')
async def login_github(request: Request):
    # Usar a URL base da configuração ou detectar automaticamente
    base_url = settings.base_url
    if 'ngrok' in str(request.url) or 'tunnel' in str(request.url):
        # Se estivermos usando ngrok, usar a URL do request
        base_url = f"{request.url.scheme}://{request.url.netloc}"
    
    redirect_uri = f"{base_url}/api/auth/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get('/auth/callback')
async def auth_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)
    
    # Buscar informações do usuário do GitHub
    user_response = await oauth.github.get('user', token=token)
    user_info = user_response.json()
    
    # Salvar token e informações do usuário na sessão
    request.session['user'] = {
        'access_token': token['access_token'],
        'login': user_info.get('login'),
        'name': user_info.get('name'),
        'avatar_url': user_info.get('avatar_url'),
        'id': user_info.get('id')
    }
    
    return RedirectResponse(url='/dashboard')

@router.get('/logout')
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url='/')
