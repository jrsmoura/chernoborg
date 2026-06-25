"""Chunking em nível de página.

Decisão de design para *este* corpus: as páginas são cartões curtos e
autocontidos (um tópico por página). Chunkar por página inteira:
- mantém o tópico íntegro (não fragmenta uma regra no meio);
- carrega todos os termos relevantes para a recuperação acertar a página;
- tolera a intercalação de colunas da extração de texto, porque o LLM de
  geração recebe a página inteira e desembaralha na resposta.

Páginas longas (> ``max_chars``) são divididas em janelas com sobreposição,
para não estourar nem diluir o embedding. Tudo aqui é função pura.
"""

from __future__ import annotations

import hashlib
import re

from .models import Chunk, RawPage

_HEADER_RE = re.compile(r"^[\wÀ-ÿ][\wÀ-ÿ %/?()|–-]{2,60}$")


def _infer_section(text: str) -> str | None:
    """Primeira linha curta sem pontuação final tratada como título da página."""
    for line in (ln.strip() for ln in text.splitlines()):
        if not line:
            continue
        if len(line) <= 60 and not line.endswith((".", ":", ";")) and _HEADER_RE.match(line):
            return line
        return None
    return None


def _chunk_id(source: str, page: int, ordinal: int) -> int:
    raw = f"{source}|{page}|{ordinal}"
    return int(hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16], 16)


def _normalize(text: str) -> str:
    """Colapsa espaços e linhas em branco repetidas, preservando parágrafos."""
    lines = [re.sub(r"[ \t]+", " ", ln).rstrip() for ln in text.splitlines()]
    out: list[str] = []
    blank = False
    for ln in lines:
        if ln:
            out.append(ln)
            blank = False
        elif not blank:
            out.append("")
            blank = True
    return "\n".join(out).strip()


def _split_long(text: str, max_chars: int, overlap: int) -> list[str]:
    """Divide um texto longo em janelas por parágrafo, com sobreposição."""
    if len(text) <= max_chars:
        return [text]
    paras = [p for p in text.split("\n\n") if p.strip()]
    windows: list[str] = []
    buf = ""
    for para in paras:
        if buf and len(buf) + len(para) + 2 > max_chars:
            windows.append(buf.strip())
            tail = buf[-overlap:] if overlap else ""
            buf = f"{tail}\n\n{para}" if tail else para
        else:
            buf = f"{buf}\n\n{para}" if buf else para
    if buf.strip():
        windows.append(buf.strip())
    return windows


def chunk_page(page: RawPage, *, max_chars: int = 1400, overlap: int = 150) -> list[Chunk]:
    text = _normalize(page.text)
    section = _infer_section(text)
    parts = _split_long(text, max_chars=max_chars, overlap=overlap)
    return [
        Chunk(
            chunk_id=_chunk_id(page.source, page.page, i),
            source=page.source,
            page=page.page,
            text=part,
            section=section,
        )
        for i, part in enumerate(parts)
    ]


def chunk_pages(pages: list[RawPage], **kwargs) -> list[Chunk]:
    return [c for page in pages for c in chunk_page(page, **kwargs)]
