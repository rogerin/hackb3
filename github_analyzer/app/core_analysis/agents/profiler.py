import os
import json
from app.core_analysis.state import AgentState

async def run(state: AgentState) -> AgentState:
    print("--- Running Profiler Agent ---")
    clone_path = state['clone_path']
    language = "Unknown"
    framework = "Unknown"

    # Python
    if os.path.exists(os.path.join(clone_path, 'requirements.txt')):
        language = 'python'
        with open(os.path.join(clone_path, 'requirements.txt'), 'r') as f:
            content = f.read()
            if 'fastapi' in content:
                framework = 'fastapi'
            elif 'django' in content:
                framework = 'django'
    
    # Node.js
    elif os.path.exists(os.path.join(clone_path, 'package.json')):
        language = 'javascript'
        with open(os.path.join(clone_path, 'package.json'), 'r') as f:
            data = json.load(f)
            dependencies = data.get('dependencies', {})
            if 'react' in dependencies:
                framework = 'react'
            elif 'express' in dependencies:
                framework = 'express'

    # Java
    elif os.path.exists(os.path.join(clone_path, 'pom.xml')):
        language = 'java'
        with open(os.path.join(clone_path, 'pom.xml'), 'r') as f:
            content = f.read()
            if 'spring-boot' in content:
                framework = 'spring-boot'

    state['language'] = language
    state['framework'] = framework
    state['processing_log'] = [f"Detected language: {language}, framework: {framework}"]
    
    return state
