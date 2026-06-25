# Assistente IESB — RAG com FAISS + Google ADK

Agente que responde dúvidas de alunos sobre **Extensão Curricularizada** e
**Atividades Complementares** do IESB, usando recuperação (RAG) sobre dois guias
em PDF. Pré-processamento → índice FAISS → agente Google ADK, tudo em uma imagem
Docker enxuta.

## Por que estas escolhas

**FAISS** (a seu pedido) pela portabilidade e custo: índice local, sem
lock-in de vector DB gerenciado. O `Embedder` e o `PdfExtractor` são abstratos,
então trocar de backend não reescreve o pipeline.

**Embeddings via Gemini (`gemini-embedding-001`), não locais.** O agente já
depende da API Gemini (é o LLM do ADK), então embeddar pela mesma API **não
adiciona dependência** e mantém a imagem pequena — `sentence-transformers`
traria o torch (~2 GB). Para independência total de API, há
`LocalFastEmbedEmbedder` (ONNX, sem torch) — veja "Variantes".

**Filtragem agressiva de páginas.** Os PDFs são infográficos com muito ruído:
- *Guia de Extensão* (72 p.): mantidas só **11–36**. Descartadas 1–10 (capa,
  sumário, listas de coordenadores — que saem embaralhadas na extração — e
  créditos) e **37–72** (planner em branco: calendários, "Top 5", diário).
- *Guia de Atividades Complementares* (24 p.): mantidas **2–22**. Descartadas
  capa e anexos em branco (formulários só com linhas).

Resultado: **47 páginas úteis → 67 chunks**. A seleção fica em
`ingest/manifest.py`.

**Chunking por página inteira.** As páginas são cartões autocontidos (um tópico
cada). Chunk por página preserva o tópico e tolera a intercalação de colunas que
a extração de texto causa em páginas de 2 colunas (ex.: regras de PS por
modalidade). Páginas longas são divididas em janelas com sobreposição.

## Estrutura

```
ingest/            # pré-processamento (funções puras + Pydantic)
  models.py        #   contratos imutáveis: RawPage, Chunk, IndexedChunk...
  manifest.py      #   quais páginas indexar + detector de lixo
  extract.py       #   PdfExtractor: pdftotext (default) | visão Gemini
  chunk.py         #   chunking por página + inferência de seção
  embed.py         #   Embedder: Gemini (default) | fastembed local
  store.py         #   FaissStore: build/save/load/search (índice + docstore)
  build.py         #   CLI: PDFs -> índice FAISS
assistente_iesb/   # agente ADK (root_agent + tool de recuperação)
pdfs/              # PDFs de origem
index/             # saída do build: index.faiss + chunks.jsonl
data/              # chunks.preview.jsonl (prévia do corpus indexado)
```

## Como rodar

### 1. Instalar e construir o índice
```bash
pip install -r requirements.txt
sudo apt-get install -y poppler-utils      # pdftotext/pdftoppm
export GEMINI_API_KEY=...                    # https://aistudio.google.com/apikey
make build                                   # PDFs -> index/index.faiss + chunks.jsonl
```

### 2. Rodar local
```bash
make run                                     # adk web em http://localhost:8000
# ou: adk run assistente_iesb   (CLI)
```

### 3. Docker (imagem pequena, índice pré-construído)
```bash
make build                                   # gera index/ primeiro
docker build -t iesb-rag .
docker run --rm -p 8000:8000 -e GEMINI_API_KEY=$GEMINI_API_KEY iesb-rag
```

### Alternativa: construir o índice dentro da imagem (sem vazar a chave)
```bash
DOCKER_BUILDKIT=1 docker build -f Dockerfile.selfbuild \
  --secret id=gemini,env=GEMINI_API_KEY -t iesb-rag .
```

## Variantes

| Objetivo                                     | Comando                                                             |
|----------------------------------------------|---------------------------------------------------------------------|
| Qualidade máxima (colunas/tabelas via visão) | `make build-vision`                                                 |
| Embeddings 100% locais (sem API)             | `pip install fastembed` e `python -m ingest.build --embedder local` |
| Mais/menos contexto por resposta             | env `RETRIEVAL_TOP_K`                                               |

## Notas

- **Modelo de embedding:** `gemini-embedding-001`. O antigo `text-embedding-004`
  foi descontinuado em 14/01/2026. Em dimensão truncada (768) ele não normaliza
  a saída — o `GeminiEmbedder` normaliza em L2, e o índice usa produto interno
  (= cosseno).
- **Versão do ADK:** fixada em `<2.0` porque o ADK 2.0 trouxe breaking changes
  na API de agentes. O padrão usado (`LlmAgent` + função como tool) é estável no
  ramo 1.x.
- **Reindexar** quando um guia mudar: regerar `index/` com `make build`. Como o
  corpus é pequeno, leva segundos.