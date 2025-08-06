import os
from tree_sitter import Parser
from tree_sitter_languages import get_language
from app.core_analysis.state import AgentState, CodeUnit
from app.utils.openai_client import openai_client

# TODO: Make this language-agnostic
# Temporarily disabled due to tree-sitter compatibility issues
# PYTHON_LANGUAGE = get_language('python')

def get_python_parser():
    # parser = Parser()
    # parser.set_language(PYTHON_LANGUAGE)
    # return parser
    return None  # Temporarily disabled

def get_docstring_prompt(language, code):
    return f"""
    Gere uma docstring em formato Markdown para a seguinte função em {language}. A documentação deve incluir:
    1. Uma breve descrição do propósito da função.
    2. Uma descrição de cada parâmetro, seu tipo e finalidade.
    3. Uma descrição do valor de retorno.

    CÓDIGO:
    ```{language}
    {code}
    ```
    """

async def document_code_unit(unit: CodeUnit, language: str) -> str:
    prompt = get_docstring_prompt(language, unit['raw_code'])
    messages = [{"role": "user", "content": prompt}]
    
    try:
        response = await openai_client.create_chat_completion(
            model="gpt-4o",
            messages=messages,
            temperature=0.2,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error generating documentation for {unit['unit_name']}: {e}")
        return "Failed to generate documentation."

async def run(state: AgentState) -> AgentState:
    print("--- Running Deconstructor Agent ---")
    clone_path = state['clone_path']
    language = state['language']
    
    if language != 'python':
        print(f"Language '{language}' not supported for deconstruction.")
        state['code_units'] = []
        return state

    parser = get_python_parser()
    if parser is None:
        print("Parser temporarily disabled due to tree-sitter compatibility issues.")
        state['code_units'] = []
        state['processing_log'] = ["Deconstructor temporarily disabled"]
        return state
        
    code_units = []

    for root, _, files in os.walk(clone_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code = f.read()
                
                tree = parser.parse(bytes(code, "utf8"))
                
                # Query for functions and classes
                query_str = """
                (function_definition
                  name: (identifier) @function.name)
                (class_definition
                  name: (identifier) @class.name)
                """
                query = PYTHON_LANGUAGE.query(query_str)
                captures = query.captures(tree.root_node)

                for node, capture_name in captures:
                    unit_type = 'function' if 'function' in capture_name else 'class'
                    unit_name = node.text.decode('utf8')
                    raw_code = node.parent.text.decode('utf8')
                    
                    code_unit = CodeUnit(
                        file_path=file_path,
                        unit_name=unit_name,
                        unit_type=unit_type,
                        raw_code=raw_code,
                        documentation=None,
                        vulnerabilities=[]
                    )
                    
                    documentation = await document_code_unit(code_unit, language)
                    code_unit['documentation'] = documentation
                    code_units.append(code_unit)

    state['code_units'] = code_units
    state['processing_log'] = [f"Deconstructed and documented {len(code_units)} code units."]
    return state