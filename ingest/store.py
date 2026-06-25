"""Índice FAISS + docstore, encapsulados em uma única classe reutilizável.

Lembrete importante: FAISS é um índice de *vetores*, não um banco de documentos.
Ele guarda os embeddings; o texto e os metadados ficam num docstore paralelo
(``chunks.jsonl``) cuja ordem corresponde 1:1 às linhas do índice. Sem esse
mapeamento, uma busca devolve posições e nada para mostrar ao usuário.

Como os embeddings chegam normalizados (unitários), usamos ``IndexFlatIP``:
produto interno entre vetores unitários = similaridade de cosseno. Para ~dezenas
de milhares de chunks, busca exata (Flat) é instantânea e dispensa tuning de
índices aproximados.
"""

from __future__ import annotations

from pathlib import Path

import faiss
import numpy as np

from .models import Chunk, IndexedChunk, RetrievedChunk

_INDEX_FILE = "index.faiss"
_DOCSTORE_FILE = "chunks.jsonl"


class FaissStore:
    def __init__(self, index: faiss.Index, docstore: list[IndexedChunk]) -> None:
        self._index = index
        self._docstore = docstore

    # ------------------------------------------------------------------ build
    @classmethod
    def build(cls, embeddings: np.ndarray, chunks: list[Chunk]) -> "FaissStore":
        if embeddings.shape[0] != len(chunks):
            raise ValueError("nº de embeddings ≠ nº de chunks")
        vectors = np.ascontiguousarray(embeddings, dtype=np.float32)
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        docstore = [
            IndexedChunk(faiss_id=i, chunk=c) for i, c in enumerate(chunks)
        ]
        return cls(index, docstore)

    # ------------------------------------------------------------- persistence
    def save(self, directory: str | Path) -> None:
        out = Path(directory)
        out.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(out / _INDEX_FILE))
        with (out / _DOCSTORE_FILE).open("w", encoding="utf-8") as fh:
            for item in self._docstore:
                fh.write(item.model_dump_json() + "\n")

    @classmethod
    def load(cls, directory: str | Path) -> "FaissStore":
        src = Path(directory)
        index = faiss.read_index(str(src / _INDEX_FILE))
        with (src / _DOCSTORE_FILE).open(encoding="utf-8") as fh:
            docstore = [IndexedChunk.model_validate_json(line) for line in fh if line.strip()]
        return cls(index, docstore)

    # ------------------------------------------------------------------ search
    def search(self, query_vector: np.ndarray, k: int = 4) -> list[RetrievedChunk]:
        query = np.ascontiguousarray(query_vector, dtype=np.float32).reshape(1, -1)
        k = min(k, len(self._docstore))
        scores, ids = self._index.search(query, k)
        results: list[RetrievedChunk] = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0:
                continue
            results.append(
                RetrievedChunk(chunk=self._docstore[idx].chunk, score=float(score))
            )
        return results

    def __len__(self) -> int:
        return len(self._docstore)