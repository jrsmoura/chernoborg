"""Funções do Pipeline de ingestão.

NOTA: tudo aqui é IMUTÁVEL -> ``feozen=True``: uma página extraída - chunk - e o
registro que vai para o docstring do FAISS são valores, não objetos mutáveis.

Isso torna as etapas

[extrair] -> [chunkar] -> [embeddar] -> [indexar]

funções puras que recebem e devolvem listas desses valores.

author: jrsteiner
date: 24.06.2026
contact: jr.steiner@outlook.com
"""
from pydantic import BaseModel, ConfigDict, Field


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

class RawPage(_Frozen):
    """Texto de uma única página."""
    source: str = Field(..., description="Nome do PDF de origem.")
    page: int = Field(..., description="Número da página (1-based).")
    text: str = Field(..., description="Texto extraído da página.")

class Chunk(_Frozen):
    """Unicode de recuperação. Carrega metadados para citação pelo agente."""
    chunk_id: int = Field(..., description="ID estático e único do chunk.")
    source: str
    page: int
    text: str
    section: str | None =  Field(
        default=None, description="Título/seção inferido, quando disponível."
    )

    def citation(self) -> str:
        """Rótulo curto de proviniência.
        Exemplo: 'Guia de Extenss"ao, p. 29'
        """
        nome = self.source.removesuffix(".pdf").replace("_", " ")
        return f"{nome}, p. {self.page}"

class IndexedChunk(_Frozen):
    """Chunk + posição no índice FAISS. É o que persiste no docstore"""
    faiss_id: int = Field(..., ge=0)
    chunk: Chunk

class RetrievedChunk(_Frozen):
    """Resultado de uma busca: o chunk e seu score de similiaridade."""
    chunk: Chunk
    score: float
