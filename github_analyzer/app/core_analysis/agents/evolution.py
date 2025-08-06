from git import Repo
from app.core_analysis.state import AgentState, CommitInfo
from app.utils.openai_client import openai_client

def get_commit_summary_prompt(message):
    return f"""
    Summarize the purpose of the following commit message in a single concise sentence:

    "{message}"
    """

async def summarize_commit(commit):
    prompt = get_commit_summary_prompt(commit.message)
    messages = [{"role": "user", "content": prompt}]
    
    try:
        response = await openai_client.create_chat_completion(
            model="gpt-4o",
            messages=messages,
            temperature=0.2,
            max_tokens=100,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error summarizing commit {commit.hexsha}: {e}")
        return "Failed to summarize commit."

async def run(state: AgentState) -> AgentState:
    print("--- Running Evolution Agent ---")
    clone_path = state['clone_path']
    
    try:
        repo = Repo(clone_path)
        commits = list(repo.iter_commits('main', max_count=4))
        
        commit_analysis = []
        for commit in commits:
            summary = await summarize_commit(commit)
            commit_info = CommitInfo(
                hash=commit.hexsha,
                author=commit.author.name,
                message=commit.message,
                summary_of_changes=summary,
            )
            commit_analysis.append(commit_info)
            
        state['commit_analysis'] = commit_analysis
        state['processing_log'] = [f"Analyzed {len(commits)} recent commits."]

    except Exception as e:
        print(f"Error analyzing commits: {e}")
        state['error'] = str(e)
        state['processing_log'] = [f"Failed to analyze commits: {e}"]

    return state
