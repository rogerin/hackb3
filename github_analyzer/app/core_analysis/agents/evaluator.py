import os
import json
from app.core_analysis.state import AgentState, DocumentationScore
from app.utils.openai_client import openai_client

async def run(state: AgentState) -> AgentState:
    print("--- Running Evaluator Agent ---")
    clone_path = state['clone_path']
    
    readme_path = os.path.join(clone_path, 'README.md')
    if not os.path.exists(readme_path):
        state['existing_doc_score'] = DocumentationScore(score=0.0, reasoning="No README.md file found.")
        state['processing_log'] = ["No README.md file found."]
        return state

    with open(readme_path, 'r') as f:
        readme_content = f.read()

    prompt = f"""
    You are a senior software architect tasked with evaluating the quality of a project's documentation.
    Evaluate the following text based strictly on the following rubric:

    1.  **Installation and Setup Guide (Weight: 40%):** Does the document clearly explain how to install dependencies and configure the project for execution?
    2.  **API/Usage Clarity and Comprehensiveness (Weight: 30%):** Does the document describe the main features, endpoints, or functions and how to use them?
    3.  **Example Quality (Weight: 30%):** Are there practical and functional code examples?

    For each criterion, assign a score from 1 (very poor) to 5 (excellent). Calculate a final weighted score (from 0.0 to 1.0) and provide a brief justification for your assessment.

    Respond ONLY with a JSON object in the following format:
    {{
      "score": <float_from_0.0_to_1.0>,
      "reasoning": "<your_summary_justification>"
    }}

    DOCUMENTATION TO EVALUATE:
    ---
    {readme_content}
    """

    messages = [{"role": "user", "content": prompt}]
    
    try:
        response = await openai_client.create_chat_completion(
            model="gpt-4o",
            messages=messages,
            temperature=0.2,
        )
        
        response_text = response['choices'][0]['message']['content']
        score_data = json.loads(response_text)
        
        state['existing_doc_score'] = DocumentationScore(
            score=score_data['score'],
            reasoning=score_data['reasoning']
        )
        state['processing_log'] = [f"Documentation evaluated with score: {score_data['score']}"]

    except Exception as e:
        print(f"Error evaluating documentation: {e}")
        state['error'] = str(e)
        state['processing_log'] = [f"Failed to evaluate documentation: {e}"]

    return state
