# IA IESB — Assistente Virtual RAG

Agente conversacional que responde dúvidas de alunos do IESB sobre
**Extensão Curricularizada** e **Atividades Complementares**, com base nos
guias oficiais em PDF.

A arquitetura combina recuperação vetorial local (FAISS) com geração via
AWS Bedrock (Claude Haiku 4.5). O frontend é uma aplicação Next.js com
identidade visual do IESB. Tudo empacotado em uma única imagem Docker
implantável na AWS.

---

## Sumario

- [Arquitetura](#arquitetura)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Pre-requisitos](#pre-requisitos)
- [Variaveis de ambiente](#variaveis-de-ambiente)
- [Atualizar o indice](#atualizar-o-indice)
- [Rodar localmente](#rodar-localmente)
- [Docker](#docker)
- [Deploy na AWS](#deploy-na-aws)
- [Decisoes de design](#decisoes-de-design)

---

## Arquitetura

### Pipeline de ingestao (build-time)

Fonte Mermaid: [`docs/ingest-pipeline.mmd`](docs/ingest-pipeline.mmd)

Executado uma vez, fora da imagem Docker, sempre que os PDFs mudarem.

```
pdfs/
  Guia_da_Extensao_Curricular.pdf
  Guia_de_Atividades_Complementares_Atualizado_10_02_2026.pdf
  Guia de Curricularizacao da Extensao_vf.pdf
         |
         | make build
         v
  ingest/manifest.py
    filtra paginas por PDF (faixas curadas + heuristica de lixo)
         |
         v
  ingest/extract.py
    PdftotextLayoutExtractor  ->  lista de RawPage
    (pdftotext -layout, uma pagina por vez)
         |
         v
  ingest/chunk.py
    chunk por pagina inteira
    paginas longas: janelas com sobreposicao (max 1400 chars, overlap 150)
    inferencia de secao pelo primeiro titulo da pagina
         |
         v
  ingest/embed.py
    BedrockEmbedder
    Amazon Titan Embeddings v2  (1024 dims, normalizado L2)
    via boto3 / AWS Bedrock Runtime
         |
         v
  ingest/store.py
    FaissStore.build()
    IndexFlatIP  (produto interno = cosseno entre vetores unitarios)
         |
         v
index/
  index.faiss      vetores de embedding (1024-dim)
  chunks.jsonl     docstore: texto, fonte, pagina, secao
```

### Fluxo de consulta (runtime)

Fonte Mermaid: [`docs/runtime-query-flow.mmd`](docs/runtime-query-flow.mmd)

```
Navegador
    |
    |  HTTP  porta 80
    v
+-----------------------------------------------+
|  Docker Container  assistente-iesb:latest      |
|                                                |
|  +------------------+   +-------------------+ |
|  |  Next.js         |   |  ADK Web Server   | |
|  |  0.0.0.0:3000    |   |  127.0.0.1:8000   | |
|  |                  |   |                   | |
|  |  page.tsx        |   |  LlmAgent         | |
|  |  Chat UI         |   |  assistente_iesb  | |
|  |                  |   |                   | |
|  |  /api/chat  -------->  POST /run         | |
|  |  proxy +         |   |  gerencia sessao  | |
|  |  session mgmt    |   |        |          | |
|  +------------------+   |        v          | |
|                         |  buscar_nos_guias | |
|                         |  (tool RAG)       | |
|                         |        |          | |
|                         |        v          | |
|                         |  BedrockEmbedder  | |
|                         |  embed_query()    | |
|                         |        |          | |
|                         |        v          | |
|                         |  FaissStore       | |
|                         |  .search(k=4)     | |
|                         |        |          | |
|                         |  chunks relevantes| |
|                         |        |          | |
|                         |        v          | |
|                         |  _BedrockClaude   | |
|                         |  gera resposta    | |
|                         +-------------------+ |
|                                  |            |
|         supervisord gerencia os dois processos|
+-----------------------------------------------+
                   |
         AWS Bedrock  us-east-1
           Claude Haiku 4.5
           Titan Embeddings v2
```

---

## Estrutura do projeto

```
.
|-- Dockerfile               imagem multi-stage (Node 22 + Python 3.13)
|-- Dockerfile.selfbuild     alternativa: build do indice dentro da imagem
|-- docker-compose.yml       orquestracao para local e AWS Elastic Beanstalk
|-- supervisord.conf         gerencia ADK (8000) e Next.js (3000) no container
|-- Makefile                 atalhos: build, docker-build, docker-run, ...
|-- requirements.txt         dependencias Python (runtime)
|-- pyproject.toml           metadados e dependencias do projeto
|-- uv.lock                  lockfile reproduzivel (uv)
|
|-- docs/                    diagramas Mermaid das arquiteturas
|   |-- ingest-pipeline.mmd  pipeline de ingestao (build-time)
|   \-- runtime-query-flow.mmd  fluxo de consulta (runtime)
|
|-- pdfs/                    PDFs de origem (fonte da verdade do corpus)
|-- index/                   saida do pipeline de ingestao
|   |-- index.faiss          vetores FAISS (IndexFlatIP, 1024-dim)
|   \-- chunks.jsonl         docstore: um JSON por linha
|
|-- ingest/                  pipeline de pre-processamento (funcoes puras)
|   |-- models.py            contratos Pydantic: RawPage, Chunk, IndexedChunk, RetrievedChunk
|   |-- manifest.py          faixas de paginas uteis por PDF + detector de lixo
|   |-- extract.py           PdftotextLayoutExtractor | GeminiVisionExtractor
|   |-- chunk.py             chunking por pagina + janelas com sobreposicao
|   |-- embed.py             BedrockEmbedder | GeminiEmbedder | LocalFastEmbedEmbedder
|   |-- store.py             FaissStore: build / save / load / search
|   \-- build.py             CLI: python -m ingest.build --pdfs ./pdfs --out ./index
|
|-- assistente_iesb/         agente Google ADK
|   |-- agent.py             root_agent, tool buscar_nos_guias, _BedrockClaude
|   \-- prompt.py            instrucoes do sistema
|
\-- frontend/                aplicacao Next.js 15 (TypeScript)
    |-- next.config.ts       output: standalone
    |-- package.json
    \-- src/
        \-- app/
            |-- layout.tsx   fonte: Source Sans 3, favicon IESB
            |-- page.tsx     chat UI: header, bolhas, input, avatar IESB
            |-- globals.css  identidade visual IESB (#CC0000, #353B48)
            \-- api/
                \-- chat/
                    \-- route.ts   proxy para ADK + gerencia sessao
```

---

## Pre-requisitos

| Requisito | Versao minima | Uso |
|---|---|---|
| Python | 3.13 | pipeline de ingestao e agente ADK |
| uv | qualquer | gerenciador de pacotes Python |
| Node.js | 22 | build e runtime do Next.js |
| poppler-utils | qualquer | `pdftotext` para extracao de texto |
| Docker + Compose | qualquer | build e execucao da imagem |
| Conta AWS | - | Bedrock (Claude Haiku 4.5 + Titan Embeddings v2) |

Instalar dependencias Python e poppler:

```bash
uv sync
sudo apt-get install -y poppler-utils
```

---

## Variaveis de ambiente

| Variavel                | Obrigatoria | Padrao                                        | Descricao                                 |
|-------------------------|-------------|-----------------------------------------------|-------------------------------------------|
| `AWS_ACCESS_KEY_ID`     | sim*        | -                                             | Credencial AWS                            |
| `AWS_SECRET_ACCESS_KEY` | sim*        | -                                             | Credencial AWS                            |
| `AWS_DEFAULT_REGION`    | recomendado | `us-east-1`                                   | Regiao do Bedrock                         |
| `AGENT_MODEL`           | nao         | `us.anthropic.claude-haiku-4-5-20251001-v1:0` | Modelo Bedrock para o LLM                 |
| `INDEX_DIR`             | nao         | `index`                                       | Caminho para o indice FAISS               |
| `RETRIEVAL_TOP_K`       | nao         | `4`                                           | Numero de chunks recuperados por consulta |
| `PORT`                  | nao         | `3000`                                        | Porta do servidor Next.js                 |

*Em implantacoes na AWS com IAM role no container, as credenciais sao injetadas
automaticamente pelo servico de metadados — as variaveis podem ser omitidas.

Para desenvolvimento local, crie um arquivo `.env` na raiz do projeto:

```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
```

Carregue antes de qualquer comando:

```bash
set -a && source .env && set +a
```

---

## Atualizar o indice

Sempre que um PDF for adicionado, removido ou atualizado, reconstrua o indice:

```bash
make build
```

O que acontece:
1. Os PDFs em `./pdfs/` sao lidos e filtrados conforme `ingest/manifest.py`
2. Cada pagina util e transformada em um ou mais chunks
3. Os chunks sao embeddados via Amazon Titan Embeddings v2 (AWS Bedrock)
4. O indice FAISS e o docstore sao salvos em `./index/`

Ao adicionar um novo PDF, inclua a faixa de paginas uteis em `ingest/manifest.py`:

```python
KEEP_RANGES: dict[str, list[tuple[int, int]]] = {
    "nome-do-arquivo.pdf": [(pagina_inicial, pagina_final)],
    ...
}
```

Apos reconstruir o indice, reconstrua e suba a imagem Docker para que o
container use o corpus atualizado.

---

## Rodar localmente

### Apenas o agente (sem frontend)

```bash
set -a && source .env && set +a
.venv/bin/adk web --host 0.0.0.0 --port 8000 .
# Interface ADK disponivel em http://localhost:8000
```

### Frontend em modo desenvolvimento

Em um segundo terminal:

```bash
cd frontend
npm run dev
# Interface em http://localhost:3000
```

O Next.js em modo dev encaminha `/api/chat` para o ADK em `localhost:8000`
(configurado em `src/app/api/chat/route.ts` via `ADK_BASE_URL`).

---

## Docker

### Comandos

```bash
make docker-build    # reconstroi a imagem assistente-iesb:latest
make docker-run      # sobe o container em background (porta 80)
make docker-stop     # para e remove o container
make docker-logs     # acompanha os logs em tempo real
```

### Ciclo completo apos adicionar PDFs

```bash
set -a && source .env && set +a
make build && make docker-build && make docker-run
```

A aplicacao fica disponivel em `http://localhost`.

### Detalhes da imagem

```
Stage 1  node:22-slim
  npm ci
  next build  (output: standalone)

Stage 2  python:3.13-slim
  apt: nodejs 22 (NodeSource)
  pip: supervisor, google-adk, anthropic[bedrock], boto3, faiss-cpu, ...
  COPY: ingest/, assistente_iesb/, index/
  COPY: .next/standalone/, .next/static/, public/
  USER: app (nao-root)
  supervisord: adk web (127.0.0.1:8000) + node server.js (0.0.0.0:3000)
  EXPOSE: 3000
```

---

## Deploy na AWS

### Elastic Beanstalk

1. Construa e publique a imagem no ECR:

```bash
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS \
    --password-stdin <conta>.dkr.ecr.us-east-1.amazonaws.com

docker tag assistente-iesb:latest \
  <conta>.dkr.ecr.us-east-1.amazonaws.com/assistente-iesb:latest

docker push <conta>.dkr.ecr.us-east-1.amazonaws.com/assistente-iesb:latest
```

2. No `docker-compose.yml`, substitua `build: .` pela referencia ao ECR:

```yaml
services:
  app:
    image: <conta>.dkr.ecr.us-east-1.amazonaws.com/assistente-iesb:latest
```

1. Crie um ambiente Elastic Beanstalk com a plataforma Docker e faca o
   deploy do `docker-compose.yml`.

2. Configure as variaveis de ambiente no painel do EB ou via IAM role
   com permissoes para o Bedrock (`bedrock:InvokeModel`). Com IAM role,
   as variaveis `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` nao sao
   necessarias.

### App Runner

1. Publique a imagem no ECR (mesmo passo acima).
2. Crie um servico App Runner apontando para a imagem ECR.
3. Defina a porta `3000` como porta do container.
4. Associe uma IAM role com permissao `bedrock:InvokeModel`.
5. Configure `AWS_DEFAULT_REGION=us-east-1` nas variaveis de ambiente
   do servico.

---

## Decisoes de design

### RAG com FAISS local

O corpus e pequeno e fixo (tres PDFs, ~120 chunks). FAISS com `IndexFlatIP`
(busca exata por produto interno) e instantaneo para esse volume e elimina
a dependencia de um vector database gerenciado. O `FaissStore` encapsula
index e docstore em dois arquivos copiados para dentro da imagem no build.

### Chunking por pagina

Os PDFs do IESB sao infograficos com um topico por pagina. Chunkar a pagina
inteira preserva o topico, evita fragmentar regras no meio e tolera a
intercalacao de colunas que a extracao de texto produz em paginas de 2 colunas.
Paginas longas (> 1400 caracteres) sao divididas em janelas com sobreposicao
de 150 caracteres.

### Filtragem agressiva de paginas

Indexar capas, sumarios, listas de coordenadores e planners em branco degrada
a recuperacao. A selecao e curada manualmente em `ingest/manifest.py` e
complementada pela heuristica `looks_like_filler` para reprocessamentos futuros.

| PDF                                  | Total | Indexadas     | Descartadas                            |
|--------------------------------------|-------|---------------|----------------------------------------|
| Guia da Extensao Curricular          | 72 p. | 11-36 (26 p.) | capa, sumario, planner                 |
| Guia de Atividades Complementares    | 24 p. | 2-22 (21 p.)  | capa, formularios                      |
| Guia de Curricularizacao da Extensao | 49 p. | 10-45 (36 p.) | capa, coordenadores, paginas em branco |

### AWS Bedrock para LLM e embeddings

O projeto usa exclusivamente AWS como provedor de IA, eliminando dependencias
do Google (genai/Gemini). O `_BedrockClaude` e uma subclasse de `AnthropicLlm`
do ADK 1.x que substitui o cliente padrao `AsyncAnthropic` pelo
`AsyncAnthropicBedrock`, sem alterar o framework de agentes. O `BedrockEmbedder`
usa o Amazon Titan Embeddings v2 (1024 dims, multilingual) via boto3.

A autenticacao segue a cadeia padrao do boto3: variaveis de ambiente em
desenvolvimento, IAM role na AWS.

### Google ADK como framework de agentes

O ADK fornece o servidor web, gerenciamento de sessao, ciclo de tool-calling e
interface de chat integrada. A versao e fixada em `<2.0` porque o ADK 2.0
introduziu breaking changes na API de agentes. O padrao `LlmAgent` + funcao
Python como tool e estavelno ramo 1.x.

### Next.js standalone + supervisord

O Next.js e compilado com `output: standalone` para um bundle minimo sem
`node_modules` completo. O `supervisord` gerencia os dois processos (ADK e
Next.js) em um unico container, com restart automatico em caso de falha. O ADK
fica em `127.0.0.1:8000` (interno) e o Next.js em `0.0.0.0:3000` (exposto).
O Next.js proxeia as chamadas de chat para o ADK via a rota `/api/chat`,
eliminando problemas de CORS.
