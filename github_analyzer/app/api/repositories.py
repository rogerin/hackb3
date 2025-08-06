from fastapi import APIRouter, Depends, Request, HTTPException
from app.api.auth import get_user, oauth
from app.config import settings

router = APIRouter()

@router.get("/repositories")
async def list_repositories(request: Request, user: dict = Depends(get_user)):
    token = {'access_token': user['access_token']}
    resp = await oauth.github.get('user/repos?sort=updated&per_page=100', token=token)
    resp.raise_for_status()
    return resp.json()

@router.post("/repositories/{owner}/{repo}/select")
async def select_repository(owner: str, repo: str, request: Request, user: dict = Depends(get_user)):
    # Construir URL do webhook usando o domínio da aplicação
    base_url = settings.base_url
    if 'ngrok' in str(request.url) or 'tunnel' in str(request.url):
        # Se estivermos usando ngrok, usar a URL do request
        base_url = f"{request.url.scheme}://{request.url.netloc}"
    
    webhook_url = f"{base_url}/api/webhook/event"
    
    hook_data = {
        "name": "web",
        "active": True,
        "events": ["push"],
        "config": {
            "url": webhook_url,
            "content_type": "json",
            "secret": settings.webhook_secret,
        },
    }
    
    token = {'access_token': user['access_token']}
    resp = await oauth.github.post(
        f"repos/{owner}/{repo}/hooks",
        token=token,
        json=hook_data,
    )
    
    try:
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create webhook: {str(e)}")

    return resp.json()
