"""Pipeline de build: PDFs -> índice FAISS pronto para o agente.

Uso:
    python -m ingest.build --pdfs ./pdfs --out ./index
    python -m ingest.build --pdfs ./pdfs --out ./index --extractor vision
    python -m ingest.build --pdfs ./pdfs --out ./index --embedder local

Cada etapa é uma função pura; este módulo só faz a orquestração e a I/O.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .chunk import chunk_pages
from .embed import BedrockEmbedder, Embedder, GeminiEmbedder, LocalFastEmbedEmbedder
from .extract import GeminiVisionExtractor, PdfExtractor, PdftotextLayoutExtractor
from .models import Chunk
from .store import FaissStore


def _resolve_pdfs(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(path.glob("*.pdf"))
    if path.is_file() and path.suffix.lower() == ".pdf":
        return [path]
    raise SystemExit(f"Nenhum PDF encontrado em {path}")


def _build_extractor(kind: str) -> PdfExtractor:
    return {"pdftotext": PdftotextLayoutExtractor, "vision": GeminiVisionExtractor}[kind]()


def _build_embedder(kind: str, dim: int) -> Embedder:
    if kind == "gemini":
        return GeminiEmbedder(dim=dim)
    if kind == "bedrock":
        return BedrockEmbedder(dim=dim)
    return LocalFastEmbedEmbedder()


def run(pdfs_path: Path, out_dir: Path, extractor: str, embedder: str, dim: int) -> None:
    ext = _build_extractor(extractor)
    pages = [p for pdf in _resolve_pdfs(pdfs_path) for p in ext.extract(pdf)]
    chunks: list[Chunk] = chunk_pages(pages)
    print(f"[build] {len(pages)} páginas úteis -> {len(chunks)} chunks", file=sys.stderr)

    emb = _build_embedder(embedder, dim)
    vectors = emb.embed_documents([c.text for c in chunks])
    print(f"[build] embeddings: {vectors.shape} (dim={emb.dim})", file=sys.stderr)

    FaissStore.build(vectors, chunks).save(out_dir)
    print(f"[build] índice salvo em {out_dir}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Constrói o índice FAISS dos guias do IESB.")
    parser.add_argument("--pdfs", type=Path, default=Path("pdfs"))
    parser.add_argument("--out", type=Path, default=Path("index"))
    parser.add_argument("--extractor", choices=["pdftotext", "vision"], default="pdftotext")
    parser.add_argument("--embedder", choices=["gemini", "local", "bedrock"], default="bedrock")
    parser.add_argument("--dim", type=int, default=1024, help="Dimensão do embedding (Gemini: 768; Bedrock Titan v2: 256/512/1024).")
    args = parser.parse_args()
    run(args.pdfs, args.out, args.extractor, args.embedder, args.dim)


if __name__ == "__main__":
    main()
