import hmac
import hashlib
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from app.config import settings
from app.core_analysis.graph import app as analysis_graph
from app.core_analysis.state import AgentState

router = APIRouter()

def verify_signature(request: Request, body: bytes):
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(status_code=403, detail="Missing X-Hub-Signature-256 header")

    expected_signature = "sha256=" + hmac.new(
        settings.webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

async def run_analysis_pipeline(repo_url: str, commit_hash: str):
    initial_state = AgentState(
        repo_url=repo_url,
        clone_path="",
        language="",
        framework="",
        existing_doc_score=None,
        code_units=[],
        commit_analysis=[],
        final_report="",
        processing_log=[],
        error=None,
    )
    config = {"configurable": {"thread_id": commit_hash}}
    await analysis_graph.ainvoke(initial_state, config=config)

@router.post("/webhook/event", name="webhook_event")
async def webhook_event(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    verify_signature(request, body)
    
    payload = await request.json()
    
    if "repository" in payload and "clone_url" in payload["repository"] and "after" in payload:
        repo_url = payload["repository"]["clone_url"]
        commit_hash = payload["after"]
        background_tasks.add_task(run_analysis_pipeline, repo_url, commit_hash)

    return {"message": "Webhook received"}
