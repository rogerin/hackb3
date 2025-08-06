
Documentação Técnica: Projeto de Análise Inteligente de Repositórios GitHub
Parte 1: Arquitetura Fundamental e Configuração do Ambiente
Esta seção estabelece a base do projeto. Uma fundação robusta e bem organizada é fundamental para a escalabilidade e a manutenibilidade. Será definida a macroarquitetura do sistema, estabelecida uma estrutura de projeto limpa e configurado um ambiente de implantação pronto para produção desde o início.

1.1. Blueprint do Sistema

A arquitetura do sistema foi projetada para separar claramente as responsabilidades entre a interface do usuário, a integração com o GitHub e o pipeline de análise assíncrono. Este design modular garante que cada componente possa ser desenvolvido, testado e mantido de forma independente, aumentando a robustez geral do sistema.

O fluxo de dados e controle pode ser visualizado da seguinte forma:

Interação do Usuário e Configuração: O processo começa com o usuário interagindo com a interface web fornecida pela aplicação FastAPI. O usuário se autentica através do fluxo GitHub OAuth2. Uma vez autenticado, a aplicação utiliza o token de acesso para interagir com a API do GitHub, permitindo que o usuário liste seus repositórios e selecione um para análise.

Orquestração do Webhook: Após a seleção de um repositório, a aplicação FastAPI faz uma chamada programática à API do GitHub para registrar um novo webhook. Este webhook é configurado especificamente para monitorar eventos de push no branch principal (por exemplo, main ou master).
Disparo do Pipeline (Trigger): Quando um desenvolvedor executa um git push para o repositório monitorado, o GitHub envia uma notificação de evento (payload) via uma requisição HTTP POST para um endpoint de ingestão específico na aplicação FastAPI.

Processamento Assíncrono: O endpoint de ingestão da FastAPI é projetado para ser altamente responsivo. Sua principal função é validar a autenticidade do payload do webhook e, em seguida, iniciar o pipeline de análise como uma tarefa em segundo plano (BackgroundTask). Isso permite que a aplicação retorne imediatamente uma resposta 200 OK ao GitHub, evitando timeouts.
Execução do Pipeline de Agentes: A tarefa em segundo plano invoca o núcleo de análise do sistema, que é um grafo de agentes construído com LangGraph. Este StateGraph gerencia um estado central (AgentState) que é passado sequencialmente através de uma série de agentes especializados (Micro Componentes de Processamento - MCPs).

Ciclo de Análise: Cada agente no grafo executa uma tarefa específica: clonar o repositório, analisar a linguagem, analisar o código-fonte usando ferramentas avançadas de parsing, interagir com a API REST da OpenAI para gerar documentação e realizar análises de segurança. Os resultados de cada agente atualizam o AgentState central.

Geração do Relatório Final: O último agente no grafo sintetiza todas as informações coletadas no AgentState e utiliza um modelo de linguagem avançado (LLM) para gerar um relatório final detalhado no formato readme.md. Este arquivo é então salvo, completando o ciclo.

Esta arquitetura garante que a interação do usuário seja rápida e que o processamento pesado e demorado seja executado de forma assíncrona, sem impactar a performance da interface web ou a confiabilidade da comunicação com o GitHub.

1.2. Estrutura de Projeto Recomendada

A organização do código-fonte é crucial para a manutenibilidade de aplicações complexas. A estrutura adotada aqui segue as melhores práticas para projetos FastAPI de grande escala, priorizando a separação de responsabilidades e a modularidade por domínio de funcionalidade em vez de por tipo de arquivo.

A aplicação é dividida em dois domínios principais: a interface web (app/api), que lida com todas as interações HTTP, e o núcleo de análise (app/core_analysis), que contém a lógica de processamento intensivo com LangGraph. Esta separação garante que as complexidades do pipeline de IA não se misturem com a lógica do servidor web. O uso do APIRouter da FastAPI é fundamental para essa modularidade, permitindo que cada conjunto de endpoints relacionados (autenticação, webhooks, repositórios) seja definido em seu próprio módulo e depois incluído na aplicação principal. Essa abordagem não apenas organiza o código, mas também facilita a colaboração da equipe e a escalabilidade futura.

A seguir, a estrutura de diretórios detalhada:

github_analyzer/
├──.dockerignore
├──.env
├── docker-compose.yml
├── Dockerfile.prod
├── gunicorn.conf.py
├── requirements.txt
└── app/
    ├── __init__.py
    ├── main.py             # Instanciação principal da aplicação FastAPI e inclusão dos routers
    ├── config.py           # Gerenciamento de configurações com Pydantic (chaves de API, segredos)
    ├── api/                # Endpoints voltados para a web (interface com o usuário e GitHub)
    │   ├── __init__.py
    │   ├── auth.py         # Fluxo de autenticação GitHub OAuth2
    │   ├── webhooks.py     # Endpoint de ingestão para os webhooks do GitHub
    │   └── repositories.py # Endpoints para listar e selecionar repositórios
    ├── core_analysis/      # O pipeline de análise com LangGraph (backend assíncrono)
    │   ├── __init__.py
    │   ├── graph.py        # Definição e compilação do StateGraph
    │   ├── state.py        # Definição do TypedDict AgentState
    │   └── agents/         # Lógica individual de cada agente (MCPs)
    │       ├── __init__.py
    │       ├── triage.py
    │       ├── profiler.py
    │       ├── deconstructor.py
    │       ├── security.py
    │       ├── evaluator.py
    │       ├── evolution.py
    │       └── synthesizer.py
    └── utils/              # Utilitários compartilhados
        ├── __init__.py
        ├── github_client.py  # Cliente REST para a API do GitHub
        └── openai_client.py  # Cliente REST para a API da OpenAI
1.3. Configuração de Ambiente e Dependências

A configuração correta do ambiente e a gestão de dependências são essenciais para a reprodutibilidade e estabilidade do projeto.

Arquivo requirements.txt

Este arquivo lista todas as bibliotecas Python necessárias para o projeto. A instalação pode ser feita com o comando pip install -r requirements.txt.

# Web Framework e Servidor ASGI/WSGI
fastapi
uvicorn
gunicorn

# Orquestração de Agentes e Modelos de Linguagem
langgraph
langchain-core  # Para modelos de dados como BaseMessage
langchain-openai # Apenas para modelos Pydantic, não para o cliente

# Clientes HTTP e APIs
httpx           # Para chamadas RESTful assíncronas
requests        # Para chamadas síncronas, se necessário
authlib         # Para o fluxo OAuth2 com o GitHub

# Análise de Código e Git
GitPython       # Para clonar e interagir com repositórios Git
tree-sitter     # Núcleo da biblioteca de parsing
tree-sitter-languages # Gramáticas pré-compiladas para várias linguagens
guesslang       # Para detecção de linguagem de programação

# Utilitários e Configuração
python-dotenv   # Para carregar variáveis de ambiente do arquivo.env
pydantic-settings # Para gerenciamento de configurações tipadas
Arquivo de Ambiente .env

Este arquivo armazena todas as chaves de API, segredos e configurações sensíveis, mantendo-as fora do controle de versão. Um arquivo .env.example deve ser criado com a mesma estrutura, mas com valores de placeholder.

# GitHub OAuth Application Credentials
GITHUB_CLIENT_ID="seu_client_id_do_github"
GITHUB_CLIENT_SECRET="seu_client_secret_do_github"

# OpenAI API Key
OPENAI_API_KEY="sk-sua_chave_de_api_da_openai"

# Application Secrets
# Use `openssl rand -hex 32` para gerar valores seguros
WEBHOOK_SECRET="um_segredo_forte_e_aleatorio_para_validacao_do_webhook"
SESSION_SECRET_KEY="um_segredo_forte_e_aleatorio_para_sessoes_de_usuario"
1.4. Dockerização para Produção

A containerização com Docker garante um ambiente de implantação consistente e isolado. Para este projeto, uma configuração de produção é fornecida desde o início, utilizando Gunicorn como um gerenciador de processos para os workers Uvicorn, uma prática recomendada para aplicações FastAPI em produção. Esta abordagem permite que a aplicação utilize múltiplos núcleos de CPU, gerencie reinicializações de workers e lide com um volume maior de requisições concorrentes de forma eficiente. Uma simples execução com 

uvicorn é adequada para desenvolvimento, mas inadequada para a resiliência e performance exigidas em um ambiente de produção.

Dockerfile.prod

Este Dockerfile utiliza uma construção multi-stage para criar uma imagem final otimizada, menor e mais segura, contendo apenas as dependências de tempo de execução.

Dockerfile
# --- Estágio de Build ---
# Usa uma imagem Python completa para instalar dependências, incluindo as de compilação
FROM python:3.11-slim as builder

WORKDIR /usr/src/app

# Instala dependências do sistema necessárias para compilar algumas bibliotecas Python
RUN apt-get update && apt-get install -y build-essential

# Copia e instala as dependências Python
COPY requirements.txt.
RUN pip wheel --no-cache-dir --wheel-dir /usr/src/app/wheels -r requirements.txt

# --- Estágio Final ---
# Usa uma imagem Python slim para a imagem final, reduzindo o tamanho
FROM python:3.11-slim

WORKDIR /code

# Cria um usuário não-root para executar a aplicação por segurança
RUN useradd --create-home appuser
USER appuser

# Copia as dependências pré-compiladas do estágio de build
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt.
RUN pip install --no-cache-dir /wheels/*

# Copia o código da aplicação
COPY --chown=appuser:appuser./app./app
COPY --chown=appuser:appuser gunicorn.conf.py.

# Expõe a porta em que o Gunicorn estará escutando
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
gunicorn.conf.py

Este arquivo de configuração permite que o Gunicorn ajuste dinamicamente o número de workers com base nos recursos de CPU disponíveis no host, otimizando a performance.

Python
import multiprocessing
import os

# Configurações do Gunicorn
bind = "0.0.0.0:8000"

# Calcula o número de workers dinamicamente
# A regra geral é (2 * número de CPUs) + 1
workers = (multiprocessing.cpu_count() * 2) + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Configurações de logging
loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"
docker-compose.yml

Este arquivo orquestra a construção e execução do container, gerenciando a passagem de variáveis de ambiente e o mapeamento de portas.

YAML
version: '3.8'

services:
  web:
    build:
      context:.
      dockerfile: Dockerfile.prod
    container_name: github_analyzer_app
    env_file:
      -.env
    ports:
      - "8000:8000"
    restart: unless-stopped
Parte 2: Interface Web e Integração com o GitHub
Esta seção detalha a construção dos componentes voltados para o usuário. O objetivo é criar uma experiência segura e fluida para que o usuário conecte sua conta do GitHub, selecione um repositório e automatize a configuração do pipeline de análise.

2.1. Autenticação Segura com o GitHub

Para interagir com a API do GitHub em nome do usuário, a aplicação implementará o fluxo de autorização OAuth2 "Authorization Code Flow". Este é o fluxo mais seguro para aplicações web, pois o token de acesso nunca é exposto diretamente ao navegador do usuário. A biblioteca 

authlib será utilizada para simplificar a implementação deste fluxo complexo.

O processo de autenticação envolverá dois endpoints principais em app/api/auth.py:

GET /login/github: Este endpoint iniciará o fluxo OAuth2. Ele não contém lógica complexa; sua única responsabilidade é redirecionar o navegador do usuário para a página de autorização do GitHub, incluindo o client_id da aplicação e os scopes necessários (por exemplo, repo para acessar repositórios e admin:repo_hook para criar webhooks).

GET /auth/callback: Após o usuário autorizar a aplicação no GitHub, ele será redirecionado de volta para este endpoint. A URL de callback conterá um code temporário. A lógica deste endpoint irá:

Receber o code temporário.

Fazer uma requisição segura (server-to-server) para o endpoint de token do GitHub, trocando o code, client_id e client_secret por um access_token permanente.

Armazenar o access_token de forma segura na sessão do usuário. A sessão será gerenciada pela FastAPI, utilizando um SESSION_SECRET_KEY para assinar os cookies de sessão.

Redirecionar o usuário para uma página de dashboard ou seleção de repositórios.

Para proteger os endpoints subsequentes, uma dependência da FastAPI será criada para verificar se o usuário está autenticado e possui um token válido na sessão.

2.2. Gerenciamento de Repositórios e Orquestração de Webhooks

Uma vez que o usuário esteja autenticado, ele poderá gerenciar quais de seus repositórios serão analisados pela ferramenta.

GET /api/repositories: Este endpoint, protegido pela dependência de autenticação, utilizará o access_token do usuário para fazer uma chamada à API do GitHub (GET /user/repos). Ele retornará uma lista dos repositórios do usuário, que será exibida na interface.

POST /api/repositories/{owner}/{repo}/select: Quando o usuário seleciona um repositório para análise, a interface fará uma chamada para este endpoint. A lógica deste endpoint é crucial para a automação:

Ele utilizará o access_token para fazer uma chamada à API do GitHub para criar um webhook no repositório especificado (POST /repos/{owner}/{repo}/hooks).
O corpo da requisição para criar o webhook será cuidadosamente configurado:

name: "web".
active: true.

events: ["push"], para que o webhook seja acionado apenas em eventos de push.
config:

url: O endereço público do nosso endpoint de ingestão (ex: https://sua-app.com/api/webhook/event).

content_type: "json".

secret: O WEBHOOK_SECRET definido no arquivo .env. Este segredo é usado pelo GitHub para assinar cada payload enviado, permitindo que nossa aplicação verifique sua autenticidade.
2.3. O Endpoint de Ingestão

O endpoint /api/webhook/event em app/api/webhooks.py é a porta de entrada para o pipeline de análise. Ele deve ser robusto, seguro e rápido.

Validação de Segurança: A primeira e mais importante etapa é a validação da assinatura do payload. Cada requisição do GitHub incluirá um header X-Hub-Signature-256. A lógica do endpoint calculará um hash HMAC-SHA256 do corpo da requisição usando o WEBHOOK_SECRET e o comparará com o valor do header. Se não corresponderem, a requisição é descartada com um status 403 Forbidden. Isso previne ataques de falsificação e garante que apenas eventos legítimos do GitHub acionem o pipeline.
Iniciação da Tarefa em Segundo Plano: Após a validação, o endpoint extrairá as informações relevantes do payload JSON, como a URL de clone do repositório e o hash do último commit. Em seguida, ele iniciará o pipeline de análise do LangGraph como uma BackgroundTask.

O uso de BackgroundTasks é uma decisão arquitetural crítica. O sistema de webhooks do GitHub espera uma resposta rápida (geralmente em menos de 10 segundos). Se um endpoint demorar muito para responder, o GitHub considerará a entrega como falha. Após várias falhas consecutivas, o webhook pode ser desativado automaticamente. Como o pipeline de análise completo pode levar vários minutos, executá-lo de forma síncrona bloquearia a resposta e levaria a falhas. Ao delegar a execução para uma 

BackgroundTask, o endpoint pode retornar um 200 OK imediatamente após a validação, garantindo a saúde e a confiabilidade do webhook, que é o gatilho central de toda a automação do sistema.

Parte 3: O Núcleo Agente: Arquitetando o Pipeline LangGraph
Este é o cérebro da aplicação, onde a lógica de análise complexa é orquestrada. Utilizaremos LangGraph para construir um sistema de agentes stateful, que é mais flexível e poderoso do que um pipeline linear simples. Ele permite ciclos, ramificações condicionais e um gerenciamento de estado centralizado, tornando o sistema mais robusto e extensível.

3.1. A Definição do Estado Central (state.py)

O coração de um StateGraph é seu objeto de estado. Este objeto funciona como uma memória compartilhada que flui através de todos os agentes (nós) no grafo, carregando consigo os resultados de cada etapa do processamento. Definir este estado de forma clara e tipada desde o início é crucial, pois cria um contrato explícito sobre os dados que cada agente pode consumir e produzir. Utilizaremos 

typing.TypedDict para esta definição, pois oferece verificação de tipos estática, o que ajuda a prevenir bugs em tempo de desenvolvimento.

Uma característica poderosa do LangGraph que será utilizada é a anotação Annotated[list, operator.add]. Para campos que são listas cumulativas, como um log de processamento, esta anotação permite que um agente retorne apenas o novo item a ser adicionado. O LangGraph se encarrega de anexá-lo à lista existente no estado, simplificando a lógica de atualização dentro de cada agente.

A seguir, a estrutura detalhada do AgentState:

Python
# Em app/core_analysis/state.py

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
    existing_doc_score: Optional
    code_units: List[CodeUnit]
    commit_analysis: List[CommitInfo]
    final_report: str
    
    # Lista cumulativa de logs ou erros
    processing_log: Annotated[List[str], operator.add]
    error: Optional[str]
3.2. O Grafo de Agentes (graph.py)

O StateGraph é o orquestrador que define o fluxo de controle. Cada etapa principal do pipeline de análise será um nó no grafo, e as transições entre eles serão as arestas.

O fluxo será definido da seguinte forma:

Ponto de Entrada (START): O grafo começa e a primeira tarefa é delegada ao triage_agent.

Nós (Agentes): Cada função de agente (definida na Parte 4) será adicionada como um nó ao grafo. Ex: graph.add_node("triage", triage_agent).

Arestas (Fluxo de Controle): As conexões entre os nós definem a sequência de execução.

START → triage

triage → profiler (Esta será uma aresta condicional)

profiler → evaluator

evaluator → deconstructor

deconstructor → security

security → evolution

evolution → synthesizer

synthesizer → END

Lógica Condicional: Para tornar o grafo mais robusto, uma aresta condicional será implementada após o agente triage. Uma função de roteamento verificará o campo error no AgentState. Se o clone do repositório falhar (e o campo error for preenchido), o fluxo será desviado para um nó de tratamento de erro que pode registrar a falha e terminar o grafo graciosamente. Caso contrário, o fluxo continua para o agente profiler. Isso evita que o pipeline inteiro falhe por um erro inicial.
3.3. Persistência de Estado e o "Cérebro" (brain.json)

A solicitação de um brain.json para salvar o "contexto e linha de pensamento" será implementada usando o sistema de checkpointing nativo do LangGraph. Esta abordagem é superior a simplesmente salvar o estado final, pois captura o estado completo da aplicação 

após cada etapa.

A implementação utilizará um FileSaver, que é um tipo de "checkpointer" que serializa o AgentState para um arquivo JSON. Ao compilar o grafo, este checkpointer será fornecido. A cada invocação do grafo, um ID de thread (por exemplo, o hash do commit) será usado para que cada execução tenha seu próprio histórico de estados.

Isso traz benefícios de terceira ordem que vão além da simples solicitação do usuário:

Auditabilidade Completa: O brain.json se tornará um registro detalhado de cada decisão e resultado intermediário, mostrando como o sistema chegou ao relatório final.

Depuração Avançada: Depurar sistemas baseados em LLMs é notoriamente difícil devido à sua natureza não determinística. Com o brain.json, será possível inspecionar o estado exato antes e depois de cada agente, identificando facilmente onde uma análise pode ter falhado ou produzido um resultado inesperado.

Resumibilidade: Em caso de falhas transitórias (por exemplo, um erro de rede ao chamar a API da OpenAI), o pipeline pode ser potencialmente retomado do último checkpoint bem-sucedido, economizando tempo e recursos computacionais.

Parte 4: Implementação dos Agentes: Um Mergulho Profundo nos MCPs
Cada agente é uma função Python que recebe o AgentState atual e retorna um dicionário contendo apenas os campos do estado que ele modificou. Esta abordagem de atualização parcial mantém a lógica de cada agente focada e simples.

4.1. Agente 1: Triagem e Inicialização (triage.py)

Responsabilidade: Preparar o ambiente de análise clonando ou atualizando o repositório de código.

Ferramenta Principal: Biblioteca GitPython.
Lógica de Execução:

Recebe a repo_url e um clone_path base do estado inicial.

Verifica se o diretório no clone_path já existe.

Se existir, instancia um objeto Repo e executa repo.remotes.origin.pull() para buscar as atualizações mais recentes.

Se não existir, executa Repo.clone_from(repo_url, clone_path) para criar um novo clone local.

Utiliza um bloco try...except GitCommandError para capturar possíveis falhas (ex: URL inválida, problemas de permissão). Em caso de erro, preenche o campo error no estado.

Retorna a atualização do estado: {"clone_path": "caminho/completo/para/o/repo", "error": None} em caso de sucesso.

4.2. Agente 2: Perfil do Projeto (profiler.py)

Responsabilidade: Identificar as tecnologias primárias usadas no projeto para contextualizar as análises subsequentes.

Ferramentas Principais: Módulos os e json da biblioteca padrão, e a biblioteca guesslang.
Lógica de Execução:

Percorre a estrutura de arquivos do clone_path.

Procura por arquivos de gerenciamento de dependências, como requirements.txt (Python) , 

package.json (Node.js) , 

pom.xml (Maven/Java), etc.

Se encontrados, lê o conteúdo desses arquivos para identificar frameworks e bibliotecas chave (ex: "fastapi", "django", "react", "spring-boot"). Esta é uma heurística de alta precisão.

Caso nenhum arquivo de dependência seja encontrado, utiliza a guesslang como fallback. A guesslang analisa o conteúdo de alguns arquivos de código-fonte para prever a linguagem de programação dominante com base em um modelo de deep learning.
Retorna a atualização do estado: {"language": "python", "framework": "fastapi"}.

4.3. Agente 3: Avaliador de Documentação (evaluator.py)

Responsabilidade: Avaliar quantitativamente a qualidade da documentação existente no projeto.

Ferramenta Principal: O cliente REST customizado openai_client.py.

Lógica de Execução:

Busca por arquivos de documentação comuns, como README.md, README.rst, ou a existência de um diretório /docs.

Se nenhum for encontrado, retorna um score de 0.0 e encerra.

Se encontrado, lê o conteúdo do arquivo principal de documentação.

Constrói um prompt estruturado e baseado em rubricas para um LLM. A engenharia de prompt aqui é vital: em vez de uma pergunta aberta como "Esta documentação é boa?", o prompt instrui o LLM a atuar como um avaliador técnico e pontuar a documentação em critérios específicos e ponderados, forçando uma saída quantitativa e justificada.
Exemplo de Prompt de Avaliação:

Você é um arquiteto de software sênior encarregado de avaliar a qualidade da documentação de um projeto. Avalie o texto a seguir com base estritamente na seguinte rubrica:

1.  **Guia de Instalação e Configuração (Peso: 40%):** O documento explica claramente como instalar as dependências e configurar o projeto para execução?
2.  **Clareza e Abrangência da API/Uso (Peso: 30%):** O documento descreve os principais recursos, endpoints ou funções e como usá-los?
3.  **Qualidade dos Exemplos (Peso: 30%):** Existem exemplos de código práticos e funcionais?

Para cada critério, atribua uma nota de 1 (muito ruim) a 5 (excelente). Calcule uma pontuação final ponderada (de 0.0 a 1.0) e forneça uma breve justificativa para sua avaliação.

Responda APENAS com um objeto JSON no seguinte formato:
{
  "score": <float_de_0.0_a_1.0>,
  "reasoning": "<sua_justificativa_resumida>"
}

DOCUMENTAÇÃO PARA AVALIAR:
---

Envia o prompt para a API da OpenAI e analisa a resposta JSON.

Retorna a atualização do estado: {"existing_doc_score": {"score": 0.75, "reasoning": "A documentação possui um bom guia de instalação, mas carece de exemplos de uso da API."}}.

4.4. Agente 4: Deconstrutor e Documentador de Código (deconstructor.py)

Responsabilidade: Analisar sintaticamente o código-fonte, extrair unidades lógicas (funções, classes) e gerar documentação para cada uma.

Ferramentas Principais: tree-sitter  e 

openai_client.py.

Lógica de Execução:

Esta é a etapa mais intensiva em computação. O agente percorre recursivamente o diretório do código-fonte.

Para cada arquivo de código (ex: .py, .js), ele utiliza tree-sitter para parseá-lo em uma Árvore de Sintaxe Abstrata (AST). A utilização de tree-sitter em vez de abordagens baseadas em regex é uma decisão arquitetural fundamental, pois fornece uma compreensão estrutural e precisa do código, imune a variações de formatação.
Usa consultas tree-sitter específicas da linguagem para encontrar todos os nós de definição de função e classe.
Para cada nó encontrado, extrai metadados importantes: o nome da função/classe, o tipo de nó e o bloco de código-fonte bruto correspondente.

Para cada unidade de código extraída, faz uma chamada direcionada a um LLM otimizado para código (como GPT-4o), com um prompt focado em documentação técnica.

Exemplo de Prompt de Documentação:

Gere uma docstring em formato Markdown para a seguinte função em [linguagem]. A documentação deve incluir:
1. Uma breve descrição do propósito da função.
2. Uma descrição de cada parâmetro, seu tipo e finalidade.
3. Uma descrição do valor de retorno.

CÓDIGO:
```[linguagem]
[código_bruto_da_função]
Coleta as respostas do LLM e as armazena.

Retorna a atualização do estado com uma lista de objetos CodeUnit: {"code_units": [...]}.

4.5. Agente 5: Analista de Segurança IA (SAST) (security.py)

Responsabilidade: Realizar uma análise de segurança estática (SAST) em cada unidade de código, procurando por padrões de vulnerabilidade comuns.

Ferramenta Principal: openai_client.py.

Lógica de Execução:

Itera sobre a lista code_units preenchida pelo agente anterior.

Para cada unidade de código, constrói um prompt de segurança. A eficácia deste agente depende criticamente da engenharia de prompt. Pesquisas indicam que LLMs podem ser eficazes em SAST, mas prompts genéricos levam a altas taxas de falsos positivos. O prompt deve ser contextualizado com a linguagem e o framework do projeto e instruir o modelo a procurar por classes específicas de vulnerabilidades.
Exemplo de Prompt SAST (para uma função Python/FastAPI):

Você é um especialista em segurança de aplicações (Pentester). Analise o seguinte trecho de código Python de uma aplicação FastAPI em busca de vulnerabilidades de segurança. Foque em vulnerabilidades do OWASP Top 10, como:
- Injeção de SQL (em queries diretas)
- Injeção de Comando (uso de os.system, subprocess)
- Desserialização Insegura (uso de pickle)
- Cross-Site Scripting (XSS) refletido (retornando dados do usuário sem sanitização)
- Path Traversal

Para cada vulnerabilidade encontrada, forneça um objeto JSON com os campos "cwe", "description" e "severity" ('High', 'Medium' ou 'Low'). Se nenhuma vulnerabilidade for encontrada, retorne uma lista vazia.

CÓDIGO PARA ANÁLISE:
```python
[código_bruto_da_função]
Envia o prompt para a API da OpenAI.

Analisa a resposta JSON e anexa a lista de vulnerabilidades encontradas ao objeto CodeUnit correspondente no estado.

Como esta operação modifica uma lista existente, o agente retorna o objeto code_units inteiro e atualizado.

4.6. Agente 6: Analista de Evolução (evolution.py)

Responsabilidade: Analisar o histórico recente de commits para fornecer um resumo da trajetória do projeto.

Ferramentas Principais: GitPython  e 

openai_client.py.

Lógica de Execução:

Utiliza repo.iter_commits('main', max_count=4) para obter os quatro commits mais recentes do branch principal.
Para cada objeto Commit, extrai o hash, autor, data e a mensagem completa do commit.

Usa um prompt simples para que um LLM resuma a intenção e o impacto do commit com base em sua mensagem.

Exemplo de Prompt de Resumo de Commit:

Resuma o propósito da seguinte mensagem de commit em uma única frase concisa:

"[mensagem_do_commit]"
Coleta os resumos e os monta em uma lista de objetos CommitInfo.

Retorna a atualização do estado: {"commit_analysis": [...]}.

Parte 5: Síntese, Relatório e Saída Final
Esta fase final consolida todos os dados estruturados coletados pelos agentes em um relatório coeso e legível por humanos. A qualidade da saída aqui depende diretamente da qualidade da engenharia de prompt final.

5.1. Agente 7: Sintetizador de Relatório (synthesizer.py)

Responsabilidade: Agregar todos os dados de análise do AgentState e preparar o contexto final para a geração do relatório.

Lógica de Execução:

Este agente é relativamente simples. Ele lê todos os campos relevantes do AgentState que foram preenchidos pelos agentes anteriores: language, framework, existing_doc_score, a lista completa de code_units (agora enriquecida com documentação e vulnerabilidades) e commit_analysis.

Ele formata todos esses dados em uma única e grande string JSON. Esta string servirá como o contexto completo e autocontido para o LLM final.

A principal tarefa deste agente é a transformação de dados, garantindo que o LLM receba um contexto limpo e bem-estruturado.

Em seguida, ele invoca o LLM com o "Master Prompt" (descrito abaixo) para gerar o relatório final em Markdown.

Retorna a atualização do estado: {"final_report": "<conteúdo_markdown_gerado>"}.

5.2. Engenharia do Master Prompt

Este é o prompt mais crítico de todo o pipeline. Seu objetivo é guiar um modelo poderoso (como o GPT-4o) para transformar os dados JSON brutos em um documento readme.md bem formatado, profissional e informativo.

A técnica chave aqui é o "prompting estruturado", onde o próprio prompt contém um template do resultado desejado. Em vez de pedir ao LLM para "criar um relatório", o prompt fornecerá uma estrutura Markdown com placeholders. Isso restringe a criatividade do modelo à geração de conteúdo dentro de uma estrutura predefinida, garantindo consistência e alta qualidade em todas as execuções.

Exemplo de Master Prompt:

Você é um redator técnico especialista e um analista de qualidade de software. Sua tarefa é gerar um relatório de análise de projeto abrangente e profissional no formato Markdown, com base nos dados JSON fornecidos. Siga estritamente a estrutura do template Markdown abaixo, preenchendo os placeholders com as informações do JSON.

**DADOS DE ANÁLISE (JSON):**
```json
{
  "repo_name": "exemplo/projeto-api",
  "language": "python",
  "framework": "fastapi",
  "existing_doc_score": {
    "score": 0.75,
    "reasoning": "A documentação possui um bom guia de instalação, mas carece de exemplos de uso da API."
  },
  "commit_analysis":,
  "code_units":
    }
  ]
}
TEMPLATE MARKDOWN (USE ESTA ESTRUTURA):

Relatório de Análise Inteligente para: {{repo_name}}
1. Visão Geral do Projeto
Linguagem Principal: {{language}}

Framework Detectado: {{framework}}

2. Análise da Documentação Existente
Pontuação de Qualidade: {{existing_doc_score.score | round(2)}} / 1.0

Avaliação do Analista IA: {{existing_doc_score.reasoning}}

3. Relatório de Análise de Segurança (SAST)
A análise estática identificou as seguintes potenciais vulnerabilidades. Recomenda-se uma revisão manual.

SeveridadeCWEDescriçãoLocalização
{% for unit in code_units %}{% for vuln in unit.vulnerabilities %}
| {{vuln.severity}} | {{vuln.cwe}} | {{vuln.description}} | {{unit.unit_name}} em {{unit.file_path}} |
{% endfor %}{% endfor %}

4. Documentação de Código Gerada por IA
A seguir, uma documentação detalhada para as funções e classes identificadas no projeto.

{% for unit in code_units %}

{{unit.unit_name}}

Localização: {{unit.file_path}}

{{unit.documentation}}
{% endfor %}

5. Evolução Recente do Projeto
Análise dos 4 commits mais recentes:
{% for commit in commit_analysis %}

Commit {{commit.hash[:7]}} por {{commit.author}}: {{commit.summary_of_changes}}
{% endfor %}

Relatório gerado automaticamente em {{ "now" | date:"%Y-%m-%d %H:%M:%S" }} UTC.


### 5.3. Saída e Comparação

A etapa final do grafo, após a geração do relatório pelo `synthesizer_agent`, é uma função utilitária simples que executa as seguintes ações:

1.  Lê o campo `final_report` do `AgentState`.
2.  Verifica se um arquivo `README.md` já existe no `clone_path`.
3.  Se existir, renomeia o arquivo existente para `README.md.old`.
4.  Escreve o novo conteúdo do relatório no arquivo `README.md`.
5.  (Opcional) Se um `README.md.old` existir, pode usar a biblioteca `difflib` do Python para gerar um diff entre a versão antiga e a nova, e adicionar este diff a um log de processamento para auditoria.

## Parte 6: O Checklist Completo de Implementação

Esta seção fornece a lista de tarefas detalhada e acionável solicitada, estruturada para guiar o desenvolvimento desde a configuração inicial até a implantação final.

### 6.1. Todolist do Zero à Produção

#### Fase 1: Configuração e Ambiente
- [x] Inicializar o repositório Git do projeto.
- [x] Criar a estrutura de diretórios conforme definido na Seção 1.2.
- [x] Criar e preencher o arquivo `requirements.txt` com todas as dependências.
- [x] Criar o arquivo `.env` a partir do template e preencher com as chaves de API e segredos.
- [x] Escrever o `Dockerfile.prod` e o `gunicorn.conf.py`.
- [x] Escrever o arquivo `docker-compose.yml` inicial.
- [x] Executar `docker-compose build` para verificar se o ambiente e as dependências estão corretos.

#### Fase 2: FastAPI e Autenticação com GitHub
- [x] Implementar os endpoints `/login/github` e `/auth/callback` em `app/api/auth.py`.
- [x] Configurar o gerenciamento de sessão da FastAPI para armazenar o token OAuth.
- [x] Criar uma dependência (`Depends`) para proteger endpoints que exigem autenticação.
- [x] Implementar o endpoint `GET /api/repositories` para listar os repositórios do usuário.
- [x] Implementar o endpoint `POST /api/repositories/{owner}/{repo}/select` com a lógica de criação de webhook via API do GitHub.

#### Fase 3: Webhook e Tarefa em Segundo Plano
- [x] Implementar o endpoint `POST /api/webhook/event` em `app/api/webhooks.py`.
- [x] Adicionar a lógica de validação de assinatura HMAC-SHA256.
- [x] Integrar a `BackgroundTasks` para iniciar o pipeline de análise (inicialmente, pode ser uma função stub que apenas registra uma mensagem).

#### Fase 4: Núcleo LangGraph
- [x] Implementar a `TypedDict` `AgentState` em `app/core_analysis/state.py`.
- [x] Criar arquivos stub para cada agente em `app/core_analysis/agents/`.
- [x] Definir o `StateGraph`, adicionar todos os nós (agentes stub) e as arestas (incluindo a condicional) em `app/core_analysis/graph.py`.
- [x] Compilar o grafo.
- [x] Conectar a invocação do grafo compilado à `BackgroundTask` no endpoint do webhook.
- [x] Configurar o `FileSaver` para persistir o estado no `brain.json`.

#### Fase 5: Implementação dos Agentes
- [x] Implementar a lógica completa do **Agente 1: Triagem** (`GitPython`).
- [x] Implementar a lógica completa do **Agente 2: Perfil do Projeto** (`guesslang` e parsing de arquivos de dependência).
- [x] Implementar a lógica completa do **Agente 3: Avaliador de Documentação** (chamada LLM com rubrica).
- [x] Implementar a lógica completa do **Agente 4: Deconstrutor de Código** (`tree-sitter` e chamadas LLM granulares).
- [x] Implementar a lógica completa do **Agente 5: Analista de Segurança** (chamada LLM SAST contextual).
- [x] Implementar a lógica completa do **Agente 6: Analista de Evolução** (`GitPython` e chamada LLM para resumo).

#### Fase 6: Relatório e Finalização
- [x] Implementar a lógica completa do **Agente 7: Sintetizador de Relatório**.
- [x] Construir e testar o "Master Prompt" para a geração do `readme.md`.
- [x] Implementar a lógica final de escrita de arquivo e comparação de versões.

#### Fase 7: Teste e Implantação
- [ ] Executar um teste completo do pipeline de ponta a ponta em um ambiente local.
- [ ] Revisar o `brain.json` gerado para verificar a correção do fluxo de estado.
- [ ] Revisar o `readme.md` final para garantir a qualidade e formatação.
- [ ] Fazer o deploy do container em um servidor de destino usando `docker-compose up -d`.
- [ ] Configurar a URL pública no aplicativo OAuth do GitHub.
- [ ] Realizar um teste final com o fluxo completo de autenticação e webhook no servidor de produção.
