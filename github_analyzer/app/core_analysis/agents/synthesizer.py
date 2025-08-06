import json
from datetime import datetime
from app.core_analysis.state import AgentState
from app.utils.openai_client import openai_client

def get_master_prompt(state: AgentState):
    repo_name = state['repo_url'].split('/')[-1].replace('.git', '')
    
    # Prepare data for the prompt
    data = {
        "repo_name": repo_name,
        "language": state['language'],
        "framework": state['framework'],
        "existing_doc_score": state.get('existing_doc_score'),
        "commit_analysis": state.get('commit_analysis', []),
        "code_units": state.get('code_units', [])
    }
    
    return f"""
    You are an expert technical writer and software quality analyst. Your task is to generate a comprehensive and professional project analysis report in Markdown format, based on the provided JSON data. Strictly follow the structure of the Markdown template below, filling in the placeholders with the information from the JSON.

    **ANALYSIS DATA (JSON):**
    ```json
    {json.dumps(data, indent=2)}
    ```

    **MARKDOWN TEMPLATE (USE THIS STRUCTURE):**

    # Intelligent Analysis Report for: {data['repo_name']}

    ## 1. Project Overview
    - **Primary Language:** {data['language']}
    - **Detected Framework:** {data['framework']}

    ## 2. Existing Documentation Analysis
    - **Quality Score:** {data['existing_doc_score']['score']:.2f} / 1.0
    - **AI Analyst Evaluation:** {data['existing_doc_score']['reasoning']}

    ## 3. Security Analysis Report (SAST)
    The static analysis identified the following potential vulnerabilities. Manual review is recommended.

    | Severity | CWE | Description | Location |
    |----------|-----|-------------|----------|
    {''.join([f'| {vuln["severity"]} | {vuln["cwe"]} | {vuln["description"]} | {unit["unit_name"]} in {unit["file_path"]} |\n' for unit in data['code_units'] for vuln in unit['vulnerabilities']])}

    ## 4. AI-Generated Code Documentation
    Below is detailed documentation for the functions and classes identified in the project.

    {''.join([f'### {unit["unit_name"]}\n**Location:** `{unit["file_path"]}`\n```markdown\n{unit["documentation"]}\n```\n' for unit in data['code_units']])}

    ## 5. Recent Project Evolution
    Analysis of the 4 most recent commits:
    {''.join([f'- **Commit `{commit["hash"][:7]}` by {commit["author"]}:** {commit["summary_of_changes"]}\n' for commit in data['commit_analysis']])}

    ---
    *Report automatically generated on {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC.*
    """

async def run(state: AgentState) -> AgentState:
    print("---" + " Running Synthesizer Agent ---")
    
    prompt = get_master_prompt(state)
    messages = [{"role": "user", "content": prompt}]
    
    try:
        response = await openai_client.create_chat_completion(
            model="gpt-4o",
            messages=messages,
            temperature=0.2,
            max_tokens=4000,
        )
        
        state['final_report'] = response['choices'][0]['message']['content']
        state['processing_log'] = ["Final report generated."]

    except Exception as e:
        print(f"Error generating final report: {e}")
        state['error'] = str(e)
        state['processing_log'] = [f"Failed to generate final report: {e}"]

    return state
