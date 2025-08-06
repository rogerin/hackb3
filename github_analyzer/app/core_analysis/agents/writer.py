import os
from app.core_analysis.state import AgentState

async def run(state: AgentState) -> AgentState:
    print("--- Running Writer Agent ---")
    clone_path = state['clone_path']
    final_report = state['final_report']
    
    readme_path = os.path.join(clone_path, 'README.md')
    
    if os.path.exists(readme_path):
        os.rename(readme_path, f"{readme_path}.old")
        
    with open(readme_path, 'w') as f:
        f.write(final_report)
        
    state['processing_log'] = [f"Final report written to {readme_path}"]
    
    return state
