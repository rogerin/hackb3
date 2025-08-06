import operator
from typing import TypedDict, List, Dict, Optional
from typing_extensions import Annotated

class DocumentationScore(TypedDict):
    """Estrutura para armazenar a pontuação da documentação existente."""
    score: float  # Pontuação normalizada de 0.0 a 1.0
    reasoning: str  # Justificativa do LLM para a pontuação

class Vulnerability(TypedDict):
    """Estrutura para uma vulnerabilidade de segurança encontrada."""
    cwe: str
    description: str
    severity: str  # 'High', 'Medium', 'Low'

class CodeUnit(TypedDict):
    """Representa uma unidade de código atômica (função, classe, etc.)."""
    file_path: str
    unit_name: str
    unit_type: str  # 'function', 'class', 'endpoint'
    raw_code: str
    documentation: Optional[str]  # Documentação gerada pela IA
    vulnerabilities: List[Vulnerability]

class CommitInfo(TypedDict):
    """Informações sobre um commit recente."""
    hash: str
    author: str
    message: str
    summary_of_changes: str

class AgentState(TypedDict):
    """O estado central que flui através do grafo de agentes."""
    repo_url: str
    clone_path: str
    language: str
    framework: str
    existing_doc_score: Optional[DocumentationScore]
    code_units: List[CodeUnit]
    commit_analysis: List[CommitInfo]
    final_report: str
    
    # Lista cumulativa de logs ou erros
    processing_log: Annotated[List[str], operator.add]
    error: Optional[str]
