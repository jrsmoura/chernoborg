"""Agente ADK que responde dúvidas de alunos com base nos guias do IESB.

LLM:       Claude Haiku 4.5 via AWS Bedrock (AnthropicLlm subclasse com
           AsyncAnthropicBedrock como transporte).
Embedder:  Amazon Titan Embeddings v2 via boto3.

Auth:      boto3 credential chain — env vars (AWS_ACCESS_KEY_ID /
           AWS_SECRET_ACCESS_KEY) ou IAM role da instância/task.
"""

from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path

from anthropic import AsyncAnthropicBedrock
from google.adk.agents import LlmAgent
from google.adk.models.anthropic_llm import AnthropicLlm

from ingest.embed import BedrockEmbedder
from ingest.store import FaissStore

_INDEX_DIR = Path(os.environ.get("INDEX_DIR", "index"))
_MODEL = os.environ.get("AGENT_MODEL", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
_TOP_K = int(os.environ.get("RETRIEVAL_TOP_K", "4"))


class _BedrockClaude(AnthropicLlm):
    """Claude via AWS Bedrock usando o transporte nativo do SDK Anthropic.

    Não precisa de ANTHROPIC_API_KEY — usa credenciais AWS do boto3.
    """

    @cached_property
    def _anthropic_client(self) -> AsyncAnthropicBedrock:  # type: ignore[override]
        return AsyncAnthropicBedrock(
            aws_region=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        )


_store = FaissStore.load(_INDEX_DIR)
_embedder = BedrockEmbedder()


def buscar_nos_guias(pergunta: str) -> dict:
    """Busca trechos relevantes nos guias oficiais do IESB.

    Cobre o Guia de Extensão Curricularizada e o Guia de Atividades
    Complementares (regras, prazos, trilhas, avaliação P1/PS, validação de
    horas, procedimentos no Aluno Online).

    Args:
        pergunta: a dúvida do aluno, em linguagem natural.

    Returns:
        Um dicionário com 'status' e 'trechos': cada trecho traz o texto e a
        'fonte' (guia + página) para citação.
    """
    query_vec = _embedder.embed_query(pergunta)
    resultados = _store.search(query_vec, k=_TOP_K)
    if not resultados:
        return {"status": "vazio", "trechos": []}
    return {
        "status": "ok",
        "trechos": [
            {"fonte": r.chunk.citation(), "texto": r.chunk.text, "score": round(r.score, 3)}
            for r in resultados
        ],
    }


_INSTRUCAO = """\
Você é o assistente virtual do IESB para dúvidas sobre Extensão Curricularizada \
e Atividades Complementares. Responda em português, de forma clara e objetiva.

Regras:
1. Para QUALQUER pergunta sobre regras, prazos, trilhas, avaliação, horas ou \
procedimentos, chame a ferramenta `buscar_nos_guias` antes de responder.
2. Baseie a resposta APENAS nos trechos retornados. Não invente regras, prazos \
ou números que não estejam nos trechos.
3. Cite a fonte ao final, no formato (Fonte: <guia>, p. <página>).
4. Atenção a distinções importantes nos trechos, como regras diferentes por \
modalidade (EaD/Híbrido vs Presencial) — não as misture.
5. Se os trechos não cobrirem a pergunta, diga que não encontrou a informação \
nos guias e oriente o aluno a procurar a coordenação ou o e-mail \
ativ.complementar@iesb.br.
"""

root_agent = LlmAgent(
    name="assistente_iesb",
    model=_BedrockClaude(model=_MODEL),
    description="Responde dúvidas de alunos do IESB sobre extensão e atividades complementares.",
    instruction=_INSTRUCAO,
    tools=[buscar_nos_guias],
)
