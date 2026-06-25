"""Geração de embeddings, atrás de uma interface trocável.

Default: ``GeminiEmbedder`` (``gemini-embedding-001``). Como o agente já usa a
API Gemini para o LLM, embeddar com a mesma API não adiciona dependência nem
peso à imagem Docker — diferente de ``sentence-transformers``, que arrasta o
torch (~2 GB).

``LocalFastEmbedEmbedder`` fica disponível para quem quiser zero dependência de
API: usa ONNX via ``fastembed`` (sem torch), ao custo de baixar os pesos do
modelo para a imagem.

Contrato: ambos devolvem vetores **unitários** (normalizados em L2), para que o
índice FAISS possa usar produto interno = similaridade de cosseno.
"""

from __future__ import annotations

import abc
import os

import numpy as np

_DOC = "RETRIEVAL_DOCUMENT"
_QUERY = "RETRIEVAL_QUERY"


def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (matrix / norms).astype(np.float32)


class Embedder(abc.ABC):
    """Embedda documentos (índice) e consultas (busca) separadamente."""

    @property
    @abc.abstractmethod
    def dim(self) -> int: ...

    @abc.abstractmethod
    def embed_documents(self, texts: list[str]) -> np.ndarray: ...

    @abc.abstractmethod
    def embed_query(self, text: str) -> np.ndarray: ...


class GeminiEmbedder(Embedder):
    """``gemini-embedding-001`` via google-genai.

    ``gemini-embedding-001`` aceita um texto por chamada e NÃO normaliza a
    saída quando ``output_dimensionality`` é diferente do padrão, então
    normalizamos aqui. O corpus é pequeno (~dezenas de chunks), então o laço
    sequencial é irrelevante em custo.
    """

    def __init__(self, model: str = "gemini-embedding-001", dim: int = 768) -> None:
        from google import genai

        self._client = genai.Client()
        self._model = model
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def _embed_one(self, text: str, task_type: str) -> np.ndarray:
        from google.genai import types

        resp = self._client.models.embed_content(
            model=self._model,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type, output_dimensionality=self._dim
            ),
        )
        return np.asarray(resp.embeddings[0].values, dtype=np.float32)

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        vectors = np.vstack([self._embed_one(t, _DOC) for t in texts])
        return _l2_normalize(vectors)

    def embed_query(self, text: str) -> np.ndarray:
        return _l2_normalize(self._embed_one(text, _QUERY)[None, :])[0]


class BedrockEmbedder(Embedder):
    """Amazon Titan Embeddings v2 via boto3 Bedrock Runtime.

    Multilingual (supports Portuguese). ``dim`` must be 256, 512, or 1024.
    Auth follows the standard boto3 chain: env vars
    (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY) or IAM role on the instance.
    """

    def __init__(
        self,
        model: str = "amazon.titan-embed-text-v2:0",
        dim: int = 1024,
        region: str | None = None,
    ) -> None:
        import boto3

        self._client = boto3.client(
            "bedrock-runtime",
            region_name=region or os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
        )
        self._model = model
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def _embed_one(self, text: str) -> np.ndarray:
        import json

        body = json.dumps({"inputText": text, "dimensions": self._dim, "normalize": True})
        resp = self._client.invoke_model(
            modelId=self._model,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(resp["body"].read())
        return np.asarray(result["embedding"], dtype=np.float32)

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        vectors = np.vstack([self._embed_one(t) for t in texts])
        return _l2_normalize(vectors)

    def embed_query(self, text: str) -> np.ndarray:
        return _l2_normalize(self._embed_one(text)[None, :])[0]


class LocalFastEmbedEmbedder(Embedder):
    """Embeddings locais via ONNX (fastembed) — sem torch, sem chamada de API.

    Default multilíngue para conteúdo em português. Use se quiser independência
    total de API; a imagem fica maior pelos pesos do modelo, mas bem menor que
    qualquer pilha baseada em torch.
    """

    def __init__(
        self, model: str = "intfloat/multilingual-e5-small", dim: int = 384
    ) -> None:
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model)
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    # e5 espera prefixos "passage:" / "query:".
    def embed_documents(self, texts: list[str]) -> np.ndarray:
        vecs = list(self._model.embed([f"passage: {t}" for t in texts]))
        return _l2_normalize(np.vstack(vecs))

    def embed_query(self, text: str) -> np.ndarray:
        vec = next(iter(self._model.embed([f"query: {text}"])))
        return _l2_normalize(np.asarray(vec, dtype=np.float32)[None, :])[0]
