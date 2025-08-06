import os
import shutil
from git import Repo, GitCommandError
from app.core_analysis.state import AgentState

async def run(state: AgentState) -> AgentState:
    print("--- Running Triage Agent ---")
    repo_url = state['repo_url']
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    clone_path = f"/tmp/{repo_name}"

    try:
        if os.path.exists(clone_path):
            print(f"Repository already exists at {clone_path}. Pulling latest changes.")
            repo = Repo(clone_path)
            origin = repo.remotes.origin
            origin.pull()
        else:
            print(f"Cloning repository from {repo_url} to {clone_path}.")
            Repo.clone_from(repo_url, clone_path)
        
        state['clone_path'] = clone_path
        state['error'] = None
        state['processing_log'] = [f"Successfully cloned/updated repository at {clone_path}"]

    except GitCommandError as e:
        print(f"Error during git operation: {e}")
        state['error'] = str(e)
        state['processing_log'] = [f"Failed to clone/update repository: {e}"]

    return state
