# 🔧 Configuração GitHub OAuth com ngrok

Este guia explica como configurar a autenticação GitHub OAuth para desenvolvimento local usando ngrok.

## 📋 Pré-requisitos

1. **ngrok instalado**
   ```bash
   # macOS
   brew install ngrok
   
   # Ou baixe de: https://ngrok.com/download
   ```

2. **Conta ngrok (opcional, mas recomendado)**
   - Crie uma conta em https://ngrok.com/
   - Faça login: `ngrok authtoken SEU_TOKEN`

## 🚀 Passo a Passo

### 1. Configurar GitHub OAuth App

1. Acesse: https://github.com/settings/developers
2. Clique em **"New OAuth App"**
3. Preencha temporariamente:
   - **Application name**: `GitHub Analyzer - Dev`
   - **Homepage URL**: `http://localhost:8088`
   - **Authorization callback URL**: `http://localhost:8088/api/auth/callback`
4. Clique **"Register application"**
5. Copie o **Client ID** e **Client Secret**

### 2. Configurar Variáveis de Ambiente

Edite o arquivo `.env` e atualize:

```env
GITHUB_CLIENT_ID="seu_client_id_aqui"
GITHUB_CLIENT_SECRET="seu_client_secret_aqui"
```

### 3. Executar com ngrok

#### Terminal 1: Iniciar ngrok
```bash
cd github_analyzer
ngrok http 8088
```

Você verá algo como:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:8088
```

#### Terminal 2: Detectar URL do ngrok (opcional)
```bash
python setup_ngrok.py
```

#### Terminal 3: Iniciar aplicação
```bash
cd github_analyzer
python -m uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload
```

### 4. Atualizar GitHub OAuth App

1. Volte para https://github.com/settings/developers
2. Clique no seu OAuth App
3. Atualize as URLs:
   - **Homepage URL**: `https://abc123.ngrok.io` (substitua pela sua URL do ngrok)
   - **Authorization callback URL**: `https://abc123.ngrok.io/api/auth/callback`
4. Clique **"Update application"**

### 5. Testar a Aplicação

1. Acesse: `https://abc123.ngrok.io` (sua URL do ngrok)
2. Clique em **"Entrar com GitHub"**
3. Autorize a aplicação
4. Você deve ser redirecionado para o dashboard com seus repositórios

## 🔍 Solução de Problemas

### Erro: "redirect_uri_mismatch"
- Certifique-se de que a URL no GitHub OAuth App está **exatamente** igual à URL do ngrok
- Inclua o protocolo `https://` e a rota `/api/auth/callback`

### ngrok não encontrado
```bash
# Verificar se está instalado
ngrok version

# Instalar no macOS
brew install ngrok

# Ou baixar: https://ngrok.com/download
```

### Aplicação não carrega
- Verifique se a aplicação está rodando na porta 8088
- Confirme que o ngrok está apontando para localhost:8088
- Verifique os logs da aplicação

### Erro de autenticação
- Confirme que CLIENT_ID e CLIENT_SECRET estão corretos no .env
- Verifique se a URL de callback no GitHub está correta

## 📝 URLs Importantes

- **GitHub OAuth Apps**: https://github.com/settings/developers
- **ngrok Dashboard**: http://localhost:4040 (quando ngrok estiver rodando)
- **Aplicação Local**: https://SEU_NGROK_URL.ngrok.io

## 🔄 Workflow Completo

```bash
# Terminal 1: ngrok
ngrok http 8088

# Terminal 2: Aplicação
python -m uvicorn app.main:app --host 127.0.0.1 --port 8088 --reload

# Terminal 3: Helper (opcional)
python setup_ngrok.py
```

## 🎯 Resultado Esperado

Após a configuração, você deve conseguir:

1. ✅ Acessar a aplicação via URL do ngrok
2. ✅ Fazer login com GitHub
3. ✅ Ver lista de repositórios
4. ✅ Configurar webhooks em repositórios
5. ✅ Receber notificações de push via webhook

---

**💡 Dica**: Salve a URL do ngrok, pois ela muda a cada reinicialização (exceto se você tiver conta paga).