# IA IESB — Arquitetura RAG Escalável (EKS + PgVector)

Documento de referência para a migração da arquitetura monolítica atual
para uma arquitetura desacoplada e escalável, mantendo AWS como provedor único.

---

## Sumário

- [Contexto e Motivação](#contexto-e-motivacao)
- [Visão Geral da Arquitetura](#visao-geral-da-arquitetura)
- [Componentes](#componentes)
- [Infraestrutura AWS](#infraestrutura-aws)
- [Banco de Dados Vetorial (PgVector)](#banco-de-dados-vetorial-pgvector)
- [Pipeline de Ingestão](#pipeline-de-ingestao)
- [Fluxo de Consulta em Tempo Real](#fluxo-de-consulta-em-tempo-real)
- [Deploy no EKS](#deploy-no-eks)
- [CI/CD](#cicd)
- [Segurança](#seguranca)
- [Observabilidade](#observabilidade)
- [Decisões de Design](#decisoes-de-design)
- [Checklist de Implementação](#checklist-de-implementacao)
- [Questões em Aberto](#questoes-em-aberto)

---

## Contexto e Motivação

### Arquitetura atual (monolítica)

| Característica | Estado atual |
|---|---|
| Runtime | Docker single-container via supervisord |
| Vetor DB | FAISS local (arquivo `index.faiss` dentro da imagem) |
| PDFs | Pasta local `pdfs/` copiada no build da imagem |
| Pipeline de ingestão | Executado manualmente antes do `docker build` |
| Escalamento | Vertical apenas (maior instância EB/App Runner) |
| Estado da sessão | Em memória no processo ADK (não persiste reinício) |
| Atualização do corpus | Rebuild completo da imagem Docker |

### Limitações que motivam a migração

- O índice FAISS cresce dentro da imagem Docker; uma atualização de PDF exige
  rebuild e redeploy completo, incluindo o build do Next.js.
- Um único container não permite escalar frontend e backend independentemente.
- Sem persistência do histórico de sessão entre restarts ou réplicas.
- FAISS `IndexFlatIP` faz busca exata (O(n)); com corpus grande, PgVector com
  índice HNSW oferece busca aproximada em O(log n) com controle de precisão.
- Impossível executar múltiplos jobs de ingestão em paralelo.

---

## Visão Geral da Arquitetura

```
Diagrama: docs/scalable-rag/diagrams/01-system-context.mmd
Diagrama: docs/scalable-rag/diagrams/02-containers.mmd
```

A nova arquitetura separa quatro domínios com ciclos de vida independentes:

| Domínio | Responsabilidade | Deploy |
|---|---|---|
| **Frontend** | Chat UI (Next.js) | EKS Deployment |
| **Backend API** | Agente RAG, tool calling, sessão | EKS Deployment |
| **Data Pipeline** | Ingestão de PDFs → embeddings → PgVector | EKS CronJob / Job |
| **Vector Database** | Armazenamento e busca semântica | RDS PostgreSQL + pgvector |

---

## Componentes

### Frontend — Next.js

- Mesma aplicação Next.js 15 atual (App Router, TypeScript)
- Compilado com `output: standalone` e servido como container separado
- Comunica com o backend via rota `/api/chat` (proxy server-side)
- Exposto publicamente via ALB Ingress na porta 443
- Sem estado próprio: qualquer réplica atende qualquer requisição

### Backend API — ADK Agent

- Servidor Google ADK (`adk web`) com `LlmAgent assistente_iesb`
- Tool `buscar_nos_guias` faz busca semântica no PgVector em vez do FAISS local
- `_BedrockClaude` (subclasse de `AnthropicLlm`) continua usando Claude Haiku 4.5
- `BedrockEmbedder` via Titan Embeddings v2 para vetorizar a query em runtime
- Sessão de conversa: armazenada no PgVector (tabela `sessions`) ou DynamoDB
- Credenciais AWS via IRSA (IAM Roles for Service Accounts) — sem chaves estáticas

### Data Pipeline — Ingest Job

- Kubernetes Job (trigger manual ou via S3 event) ou CronJob agendado
- Lê PDFs do bucket S3 `iesb-corpus/pdfs/`
- Executa o pipeline existente: manifest → extract → chunk → embed → store
- `PgVectorStore` substitui `FaissStore`: faz UPSERT por `chunk_id` (idempotente)
- Ao final registra metadados na tabela `documents` (status, páginas indexadas, timestamp)
- Pode ser disparado via `kubectl create job --from=cronjob/ingest-job` no CI/CD

### Vector Database — RDS PostgreSQL + pgvector

- Amazon RDS PostgreSQL 16, extensão `pgvector`
- Índice HNSW na coluna `embedding` (busca aproximada, alta performance)
- Acessível apenas por subnets privadas do EKS (Security Group dedicado)
- Credenciais gerenciadas pelo AWS Secrets Manager; injetadas via External Secrets Operator
- Multi-AZ standby opcional para produção
- Schema: ver seção [Banco de Dados Vetorial](#banco-de-dados-vetorial-pgvector)

---

## Infraestrutura AWS

```
Diagrama: docs/scalable-rag/diagrams/06-aws-infrastructure.mmd
```

### VPC e Redes

| Recurso | Configuração |
|---|---|
| VPC | `10.0.0.0/16` |
| Subnets públicas | 2 AZs — ALB, NAT Gateway |
| Subnets privadas | 2 AZs — EKS nodes, RDS |
| Internet Gateway | Entrada pública |
| NAT Gateway | Saída para Bedrock, ECR, S3 (endpoints privados recomendados) |

### Security Groups

| SG | Origem | Destino | Porta |
|---|---|---|---|
| `sg-alb` | `0.0.0.0/0` | ALB | 80, 443 |
| `sg-eks-nodes` | `sg-alb` | EKS node group | 30000–32767 |
| `sg-rds` | `sg-eks-nodes` | RDS | 5432 |

### Serviços AWS utilizados

| Serviço | Uso |
|---|---|
| Amazon EKS | Orquestração dos containers |
| Amazon RDS (PostgreSQL 16) | Banco vetorial com pgvector |
| Amazon S3 | Armazenamento dos PDFs originais |
| Amazon ECR | Registro privado das imagens Docker |
| AWS Bedrock | Claude Haiku 4.5 (LLM) + Titan Embeddings v2 |
| AWS Secrets Manager | Credenciais do banco de dados |
| AWS Certificate Manager | Certificado SSL para o ALB |
| AWS Load Balancer Controller | Ingress (ALB) no EKS |
| Amazon CloudWatch | Logs e métricas dos pods |
| Amazon Route 53 | DNS para o domínio do assistente |

### IAM — IRSA (IAM Roles for Service Accounts)

Dois roles distintos para princípio do menor privilégio:

**Role `iesb-backend-api`** (backend-api pod):

- `bedrock:InvokeModel` em `arn:aws:bedrock:us-east-1::foundation-model/*`
- `secretsmanager:GetSecretValue` na secret do banco

**Role `iesb-ingest-job`** (ingest-job pod):

- `bedrock:InvokeModel` em `arn:aws:bedrock:us-east-1::foundation-model/*`
- `s3:GetObject`, `s3:ListBucket` no bucket `iesb-corpus`
- `secretsmanager:GetSecretValue` na secret do banco

---

## Banco de Dados Vetorial (PgVector)

```
Diagrama: docs/scalable-rag/diagrams/07-pgvector-schema.mmd
```

### Extensão e índice

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Índice HNSW: busca aproximada, melhor performance em escala
CREATE INDEX chunks_embedding_hnsw_idx
    ON chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

### Tabelas

**`documents`** — registro de cada PDF ingerido:

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | `uuid` PK | Identificador único |
| `filename` | `text` | Nome do arquivo PDF |
| `s3_key` | `text` | Caminho no S3 |
| `total_pages` | `int` | Total de páginas do PDF |
| `indexed_pages` | `int` | Páginas efetivamente indexadas |
| `status` | `text` | `pending`, `indexing`, `done`, `error` |
| `indexed_at` | `timestamptz` | Última indexação bem-sucedida |
| `created_at` | `timestamptz` | Primeira inserção |

**`chunks`** — um registro por chunk de texto com seu embedding:

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | `bigint` PK | Hash SHA-1 derivado de source\|page\|ordinal |
| `document_id` | `uuid` FK | Referência a `documents.id` |
| `page` | `int` | Página de origem (1-based) |
| `section` | `text` | Título inferido da seção |
| `text` | `text` | Texto do chunk |
| `embedding` | `vector(1024)` | Embedding Titan v2 normalizado L2 |
| `created_at` | `timestamptz` | Timestamp de inserção |

**`sessions`** — histórico de conversas por usuário:

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | `uuid` PK | Session ID (gerado pelo frontend) |
| `user_id` | `text` | ID anônimo do usuário |
| `history` | `jsonb` | Array de mensagens `[{role, text}]` |
| `created_at` | `timestamptz` | Início da sessão |
| `updated_at` | `timestamptz` | Última mensagem |

### Query de busca semântica

```sql
SELECT id, source, page, section, text,
       1 - (embedding <=> $1::vector) AS similarity
FROM chunks
ORDER BY embedding <=> $1::vector
LIMIT $2;
```

O operador `<=>` usa distância de cosseno. Com vetores L2-normalizados (como
os do Titan v2), distância de cosseno e produto interno produzem o mesmo ranking.

---

## Pipeline de Ingestão

```
Diagrama: docs/scalable-rag/diagrams/03-ingest-pipeline.mmd
```

### Gatilho

| Modo | Mecanismo |
|---|---|
| Manual (atual) | `kubectl create job --from=cronjob/ingest-job` |
| Event-driven | S3 Event → SQS → Lambda → `kubectl` ou EKS Job |
| Agendado | CronJob Kubernetes (`schedule: "0 3 * * *"`) |

### Etapas do Job

1. Lê a lista de PDFs do bucket S3 (ou de uma SQS message)
2. Para cada PDF: download para `/tmp/`, executa o pipeline existente
3. `PgVectorStore.upsert(chunks)` — idempotente por `chunk_id`
4. Atualiza `documents.status = 'done'` e `indexed_at = now()`
5. Registra métricas no CloudWatch (chunks indexados, páginas, tempo)

### Idempotência

O `chunk_id` é o mesmo hash SHA-1 derivado de `source|page|ordinal` já usado
no FAISS. O UPSERT no PgVector usa `ON CONFLICT (id) DO UPDATE SET ...`, então
re-executar o job para o mesmo PDF atualiza os chunks sem duplicar.

---

## Fluxo de Consulta em Tempo Real

```
Diagrama: docs/scalable-rag/diagrams/04-query-flow.mmd
```

1. Usuário envia mensagem na UI Next.js
2. Next.js (`/api/chat/route.ts`) faz `POST /run` ao backend ADK
3. ADK `LlmAgent` detecta necessidade de contexto e invoca `buscar_nos_guias`
4. Tool vetoriza a query via Titan Embeddings v2 (Bedrock)
5. `PgVectorStore.search(k=4)` executa o SELECT com `<=>` no RDS
6. Os 4 chunks mais relevantes voltam como contexto para o LLM
7. `_BedrockClaude` chama Claude Haiku 4.5 com contexto + pergunta
8. Resposta retorna ao Next.js e exibida ao usuário

---

## Deploy no EKS

```
Diagrama: docs/scalable-rag/diagrams/05-eks-deployment.mmd
```

### Namespaces

| Namespace | Conteúdo |
|---|---|
| `iesb-prod` | `frontend`, `backend-api` Deployments + Services |
| `iesb-staging` | Espelho de prod para validação pré-deploy |
| `iesb-jobs` | `ingest-job` CronJob |
| `monitoring` | Prometheus + Grafana |

### Recursos Kubernetes por serviço

**frontend:**

```
Deployment       replicas: 2   image: ecr.../frontend:sha
HPA              minReplicas: 2   maxReplicas: 10   CPU: 70%
Service          ClusterIP :3000
ConfigMap        NEXT_PUBLIC_... env vars
```

**backend-api:**

```
Deployment       replicas: 2   image: ecr.../backend-api:sha
HPA              minReplicas: 2   maxReplicas: 10   CPU: 70%
Service          ClusterIP :8000
ServiceAccount   anotado com IRSA role iesb-backend-api
ExternalSecret   → Secrets Manager (DB_URL)
```

**ingest-job:**

```
CronJob          schedule: on-demand   image: ecr.../ingest-job:sha
ServiceAccount   anotado com IRSA role iesb-ingest-job
ExternalSecret   → Secrets Manager (DB_URL)
```

**Ingress (AWS Load Balancer Controller):**

```
/           → frontend:3000
/api/chat   → frontend:3000   (proxy interno para backend-api)
```

Nota: o frontend continua sendo o único ponto de entrada público. O
`backend-api` permanece ClusterIP (sem exposição direta).

### HPA e Resource Requests

| Container | CPU request | Mem request | CPU limit | Mem limit |
|---|---|---|---|---|
| frontend | 100m | 128Mi | 500m | 512Mi |
| backend-api | 200m | 256Mi | 1000m | 1Gi |
| ingest-job | 500m | 512Mi | 2000m | 2Gi |

---

## CI/CD

```
Diagrama: docs/scalable-rag/diagrams/08-ci-cd.mmd
```

### Pipeline sugerido (GitHub Actions)

**On pull request:**

- Lint (`eslint`, `mypy`)
- Testes unitários (`pytest`, `jest`)
- Build das imagens (sem push)

**On merge para `main`:**

1. Build e push das 3 imagens para ECR com tag `:sha` e `:latest`
2. Deploy em `iesb-staging` (`kubectl set image` ou `helm upgrade`)
3. Smoke tests contra staging
4. Deploy em `iesb-prod` (aprovação manual ou automático se smoke ok)
5. Se PDFs mudaram no PR: `kubectl create job --from=cronjob/ingest-job`

### Variáveis de ambiente no CI

| Variável | Origem |
|---|---|
| `AWS_ROLE_TO_ASSUME` | OIDC trust entre GitHub Actions e IAM |
| `ECR_REGISTRY` | Output do Terraform / valor fixo |
| `EKS_CLUSTER_NAME` | Parâmetro do workflow |
| `KUBECONFIG` | Gerado por `aws eks update-kubeconfig` |

---

## Segurança

| Controle | Implementação |
|---|---|
| Credenciais AWS | IRSA — sem chaves estáticas em variáveis de ambiente |
| Credenciais do banco | AWS Secrets Manager + External Secrets Operator |
| Tráfego externo | HTTPS via ACM + ALB; HTTP redireciona para HTTPS |
| Tráfego interno | ClusterIP — backend-api não exposto fora do cluster |
| Isolamento de rede | Security Groups restritivos; RDS sem acesso público |
| Imagem de container | `USER app` (não-root); imagens `slim`; scan no ECR |
| Secrets em código | `.gitignore` protege `.env`; CI usa OIDC |
| Pod Security | `readOnlyRootFilesystem: true` onde possível |

---

## Observabilidade

| Sinal | Ferramenta | O que monitorar |
|---|---|---|
| Logs | CloudWatch Logs / Fluent Bit | Erros de embedding, falhas de query SQL, exceções ADK |
| Métricas | CloudWatch + Prometheus | Latência p95 do chat, uso de CPU/mem, chunks indexados |
| Tracing | AWS X-Ray (opcional) | Tempo por etapa: embed → search → LLM |
| Alertas | CloudWatch Alarms | Erro 5xx > 1%, latência > 5s, job de ingestão falhou |
| Dashboard | Grafana | Painel unificado: infra + app metrics |

### Métricas de aplicação recomendadas

- `iesb_chat_latency_seconds` — latência end-to-end por requisição
- `iesb_bedrock_latency_seconds{model}` — latência de cada chamada Bedrock
- `iesb_pgvector_search_latency_seconds` — latência da busca vetorial
- `iesb_ingest_chunks_total{pdf}` — chunks indexados por PDF por execução
- `iesb_active_sessions` — sessões ativas

---

## Decisões de Design

### PgVector em vez de FAISS local

FAISS embutido na imagem exige rebuild completo para atualizar o corpus e não
permite múltiplas réplicas compartilharem o mesmo índice. PgVector em RDS é
acessível por todas as réplicas simultaneamente e atualiza sem downtime.
Com índice HNSW, a busca é O(log n), adequada para corpora maiores.

### EKS em vez de Elastic Beanstalk / App Runner

EKS permite escalar frontend e backend de forma independente, executar Jobs
de ingestão como cargas efêmeras e ter controle total sobre networking e IRSA.
O custo de operação é maior, mas a flexibilidade justifica para uma plataforma
que cresce com o corpus e a base de usuários.

### Separação frontend / backend

O frontend Next.js e o backend ADK têm padrões de carga muito diferentes:
o frontend é stateless e escala bem horizontalmente; o backend mantém sessão
ADK e pode precisar de mais CPU por request de LLM. Separar os deployments
permite dimensioná-los com HPAs independentes.

### IRSA em vez de chaves de acesso

Chaves estáticas (`AWS_ACCESS_KEY_ID`) exigem rotação manual e têm risco
de vazamento em logs. IRSA vincula uma IAM role a um ServiceAccount Kubernetes
via OIDC; as credenciais são temporárias (STS AssumeRoleWithWebIdentity) e
rotacionadas automaticamente.

### External Secrets Operator para credenciais do banco

Secrets do Kubernetes são base64, não criptografados em repouso por padrão.
O External Secrets Operator (ESO) sincroniza secrets do AWS Secrets Manager
para Kubernetes Secrets, aproveitando a criptografia e auditoria do Secrets Manager.

### PDFs no S3 em vez de pasta local

Com PDFs no S3 o pipeline de ingestão pode rodar em qualquer node do cluster
sem volume compartilhado. Também facilita auditoria (S3 versioning) e trigger
event-driven (S3 notifications).

---

## Checklist de Implementação

### Fase 1 — Infraestrutura base

- [ ] Provisionar VPC com subnets públicas e privadas (Terraform / CDK)
- [ ] Criar cluster EKS com node group `t3.medium` (2–6 nodes)
- [ ] Instalar AWS Load Balancer Controller no EKS
- [ ] Instalar External Secrets Operator no EKS
- [ ] Criar RDS PostgreSQL 16 com pgvector em subnet privada
- [ ] Criar secret no Secrets Manager com `DB_URL`
- [ ] Criar bucket S3 `iesb-corpus` com versionamento
- [ ] Criar repositórios ECR: `frontend`, `backend-api`, `ingest-job`
- [ ] Configurar IRSA: roles `iesb-backend-api` e `iesb-ingest-job`
- [ ] Emitir certificado ACM para o domínio
- [ ] Configurar Route 53 para apontar para o ALB

### Fase 2 — Banco de dados

- [ ] Executar `CREATE EXTENSION vector` no RDS
- [ ] Criar tabelas `documents`, `chunks`, `sessions`
- [ ] Criar índice HNSW na coluna `embedding`
- [ ] Validar conexão a partir de um pod de teste no EKS

### Fase 3 — Data Pipeline

- [ ] Implementar `PgVectorStore` (substitui `FaissStore`) com UPSERT
- [ ] Adaptar `build.py` para ler PDFs do S3 e gravar no PgVector
- [ ] Criar Dockerfile para `ingest-job`
- [ ] Criar manifesto Kubernetes CronJob / Job
- [ ] Configurar ExternalSecret para `DB_URL` no namespace `iesb-jobs`
- [ ] Testar execução do job e validar chunks no banco

### Fase 4 — Backend API

- [ ] Adaptar `agent.py`: `buscar_nos_guias` passa a usar `PgVectorStore`
- [ ] Criar Dockerfile para `backend-api` (separado do monolito)
- [ ] Criar manifesto Kubernetes: Deployment, Service, HPA, ExternalSecret
- [ ] Configurar ServiceAccount com IRSA role `iesb-backend-api`
- [ ] Testar endpoint `/run` diretamente via port-forward

### Fase 5 — Frontend

- [ ] Ajustar `route.ts`: `ADK_BASE_URL` aponta para `http://backend-api:8000`
- [ ] Criar Dockerfile para `frontend` (mesmo build atual)
- [ ] Criar manifesto Kubernetes: Deployment, Service, HPA
- [ ] Criar Ingress com anotações ALB (SSL, redirect HTTP→HTTPS)
- [ ] Testar UI completa end-to-end

### Fase 6 — CI/CD

- [ ] Criar pipeline GitHub Actions (lint → test → build → push → deploy)
- [ ] Configurar OIDC entre GitHub Actions e AWS IAM
- [ ] Configurar deploy automático para staging e manual para prod
- [ ] Adicionar step de trigger do ingest-job quando PDFs mudam

### Fase 7 — Observabilidade

- [ ] Instalar Fluent Bit no EKS para envio de logs ao CloudWatch
- [ ] Instalar Prometheus + Grafana (ou usar Amazon Managed Grafana)
- [ ] Criar dashboard com métricas de aplicação
- [ ] Configurar alertas no CloudWatch Alarms

---

## Questões em Aberto

| # | Questão | Impacto | Decisão pendente |
|---|---|---|---|
| 1 | Sessão de conversa: PgVector ou DynamoDB? | Backend Deployment | PgVector simplifica, DynamoDB escala melhor |
| 2 | Trigger de ingestão: manual, SQS event ou CronJob? | Data Pipeline | Depende da frequência de atualização dos PDFs |
| 3 | Multi-AZ para RDS? | Custo vs disponibilidade | Recomendado para prod |
| 4 | VPC endpoints para S3 e Bedrock? | Custo de NAT / segurança | Recomendado: elimina tráfego via NAT |
| 5 | Domínio público do assistente? | Frontend Ingress | Definir CNAME no Route 53 |
| 6 | Estratégia de atualização do corpus? | Data Pipeline | Upload manual ao S3 ou integração com sistema IESB |
| 7 | Retenção do histórico de sessão? | Banco de dados | LGPD: definir TTL e política de exclusão |
