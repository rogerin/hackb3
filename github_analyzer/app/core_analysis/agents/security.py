import json
from app.core_analysis.state import AgentState, Vulnerability
from app.utils.openai_client import openai_client

def get_sast_prompt(language, framework, code):
    return f"""
    You are an application security specialist (Pentester). Analyze the following snippet of {language} code from a {framework} application for security vulnerabilities. Focus on vulnerabilities from the OWASP Top 10, such as:
    - SQL Injection (in direct queries)
    - Command Injection (use of os.system, subprocess)
    - Insecure Deserialization (use of pickle)
    - Reflected Cross-Site Scripting (XSS) (returning user data without sanitization)
    - Path Traversal

    For each vulnerability found, provide a JSON object with the fields "cwe", "description", and "severity" ('High', 'Medium', or 'Low'). If no vulnerabilities are found, return an empty list.

    CODE FOR ANALYSIS:
    ```{language}
    {code}
    ```
    """

async def analyze_code_unit_for_vulnerabilities(unit, language, framework):
    prompt = get_sast_prompt(language, framework, unit['raw_code'])
    messages = [{"role": "user", "content": prompt}]
    
    try:
        response = await openai_client.create_chat_completion(
            model="gpt-4o",
            messages=messages,
            temperature=0.2,
        )
        
        response_text = response['choices'][0]['message']['content']
        vulnerabilities_data = json.loads(response_text)
        
        return [Vulnerability(**vuln) for vuln in vulnerabilities_data]
    except Exception as e:
        print(f"Error analyzing {unit['unit_name']} for vulnerabilities: {e}")
        return []

async def run(state: AgentState) -> AgentState:
    print("--- Running Security Agent ---")
    language = state['language']
    framework = state['framework']
    
    for unit in state['code_units']:
        unit['vulnerabilities'] = await analyze_code_unit_for_vulnerabilities(unit, language, framework)

    state['processing_log'] = ["Security analysis completed."]
    return state
