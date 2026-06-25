"""Extração de texto por página, atrás de uma interface trocável.

Dois extratores implementam o mesmo contrato ``PdfExtractor``:

- ``PdftotextLayoutExtractor``  — determinístico, offline, custo zero. Bom para
  páginas de coluna única; em páginas de 2 colunas pode intercalar as colunas
  (mitigado por chunkar a página inteira).
- ``GeminiVisionExtractor``     — rasteriza cada página e pede ao Gemini uma
  transcrição limpa em Markdown, na ordem de leitura correta. Custa 1 chamada
  de visão por página (uma vez, no build), mas resolve colunas e tabelas.

O resto do pipeline não sabe qual está em uso.
"""

from __future__ import annotations

import abc
import subprocess
import tempfile
from pathlib import Path

from .manifest import is_kept, looks_like_filler
from .models import RawPage


class PdfExtractor(abc.ABC):
    """Converte um PDF em uma lista de ``RawPage`` (só páginas úteis)."""

    @abc.abstractmethod
    def _page_count(self, pdf: Path) -> int: ...

    @abc.abstractmethod
    def _extract_page(self, pdf: Path, page: int) -> str: ...

    def extract(self, pdf: Path) -> list[RawPage]:
        source = pdf.name
        pages: list[RawPage] = []
        for page in range(1, self._page_count(pdf) + 1):
            if not is_kept(source, page):
                continue
            text = self._extract_page(pdf, page).strip()
            if not text or looks_like_filler(text):
                continue
            pages.append(RawPage(source=source, page=page, text=text))
        return pages


class PdftotextLayoutExtractor(PdfExtractor):
    """Extração via poppler ``pdftotext -layout`` (determinística)."""

    def _page_count(self, pdf: Path) -> int:
        out = subprocess.run(
            ["pdfinfo", str(pdf)], capture_output=True, text=True, check=True
        ).stdout
        for line in out.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":")[1].strip())
        raise RuntimeError(f"Não consegui contar páginas de {pdf}")

    def _extract_page(self, pdf: Path, page: int) -> str:
        return subprocess.run(
            ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout


class GeminiVisionExtractor(PdfExtractor):
    """Transcrição por visão: rasteriza a página e pede Markdown limpo ao Gemini.

    Use quando precisar de fidelidade em páginas de 2 colunas e tabelas (ex.:
    quadros de carga horária do Guia de Atividades Complementares). Requer
    ``GEMINI_API_KEY`` e a dependência opcional de renderização (poppler já
    fornece ``pdftoppm``).
    """

    _PROMPT = (
        "Transcreva o conteúdo desta página de um guia acadêmico para Markdown "
        "limpo, em português, na ordem natural de leitura. Preserve títulos, "
        "listas e tabelas. Se houver duas colunas ou cartões lado a lado, "
        "transcreva-os em blocos SEPARADOS, nunca intercalando linhas. Não "
        "invente conteúdo e não comente; devolva apenas a transcrição."
    )

    def __init__(self, model: str = "gemini-2.5-flash", dpi: int = 150) -> None:
        from google import genai  # import tardio: dependência só do caminho de visão

        self._client = genai.Client()
        self._model = model
        self._dpi = dpi

    def _page_count(self, pdf: Path) -> int:
        return PdftotextLayoutExtractor()._page_count(pdf)

    def _rasterize(self, pdf: Path, page: int) -> bytes:
        with tempfile.TemporaryDirectory() as tmp:
            prefix = Path(tmp) / "page"
            subprocess.run(
                ["pdftoppm", "-jpeg", "-r", str(self._dpi),
                 "-f", str(page), "-l", str(page), str(pdf), str(prefix)],
                check=True, capture_output=True,
            )
            return next(Path(tmp).glob("page*.jpg")).read_bytes()

    def _extract_page(self, pdf: Path, page: int) -> str:
        from google.genai import types

        image = self._rasterize(pdf, page)
        resp = self._client.models.generate_content(
            model=self._model,
            contents=[
                types.Part.from_bytes(data=image, mime_type="image/jpeg"),
                self._PROMPT,
            ],
        )
        return resp.text or ""
