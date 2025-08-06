#!/usr/bin/env python3
"""
Script para configurar e executar a aplicação com ngrok
"""

import subprocess
import sys
import time
import json
import requests
from pathlib import Path

def check_ngrok_installed():
    """Verifica se o ngrok está instalado"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok está instalado")
            return True
        else:
            print("❌ ngrok não encontrado")
            return False
    except FileNotFoundError:
        print("❌ ngrok não está instalado")
        return False

def get_ngrok_url():
    """Obtém a URL pública do ngrok"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        tunnels = response.json()
        
        for tunnel in tunnels['tunnels']:
            if tunnel['config']['addr'] == 'http://localhost:8088':
                return tunnel['public_url']
        
        return None
    except:
        return None

def update_env_file(ngrok_url):
    """Atualiza o arquivo .env com a URL do ngrok"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado")
        return False
    
    # Ler o arquivo atual
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Atualizar ou adicionar BASE_URL
    lines = content.split('\n')
    updated = False
    
    for i, line in enumerate(lines):
        if line.startswith('BASE_URL='):
            lines[i] = f'BASE_URL={ngrok_url}'
            updated = True
            break
    
    if not updated:
        lines.append(f'BASE_URL={ngrok_url}')
    
    # Escrever de volta
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Arquivo .env atualizado com BASE_URL={ngrok_url}")
    return True

def main():
    print("🚀 Configurando GitHub Analyzer com ngrok...\n")
    
    # Verificar se ngrok está instalado
    if not check_ngrok_installed():
        print("\n📦 Para instalar o ngrok:")
        print("1. Acesse: https://ngrok.com/download")
        print("2. Ou use: brew install ngrok (macOS)")
        sys.exit(1)
    
    print("\n📋 Instruções de configuração:")
    print("1. Execute este script: python setup_ngrok.py")
    print("2. Em outro terminal, execute: ngrok http 8088")
    print("3. Configure o GitHub OAuth App com a URL fornecida")
    print("4. Execute a aplicação: python -m uvicorn app.main:app --host 127.0.0.1 --port 8088")
    
    print("\n⏳ Aguardando ngrok na porta 8088...")
    print("Execute em outro terminal: ngrok http 8088")
    
    # Aguardar ngrok estar disponível
    max_attempts = 30
    for attempt in range(max_attempts):
        ngrok_url = get_ngrok_url()
        if ngrok_url:
            print(f"\n✅ ngrok detectado: {ngrok_url}")
            
            # Atualizar arquivo .env
            update_env_file(ngrok_url)
            
            print(f"\n🔧 Configure seu GitHub OAuth App:")
            print(f"   Homepage URL: {ngrok_url}")
            print(f"   Authorization callback URL: {ngrok_url}/api/auth/callback")
            
            print(f"\n🌐 Acesse sua aplicação em: {ngrok_url}")
            print("\n✅ Configuração completa!")
            break
        
        time.sleep(2)
        if attempt % 5 == 0:
            print(f"   Tentativa {attempt + 1}/{max_attempts}...")
    else:
        print("\n❌ Timeout aguardando ngrok. Certifique-se de que está executando 'ngrok http 8088'")

if __name__ == "__main__":
    main()