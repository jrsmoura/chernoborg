"""Seleção de páginas: o que entra no índice e o que é descartado.

Os PDFs do IESB são infográficos com muito ruído para um RAG:
- O "Guia de Extensão" tem 72 páginas, mas 37-72 são um *planner* em branco
  (calendários, "Top 5 Songs", páginas de diário) e 1-10 são capa, sumário,
  listas de coordenadores (que saem embaralhadas na extração) e créditos.
- O "Guia de Atividades Complementares" tem capa (p1) e anexos em branco
  (p23-24, formulários só com linhas).

Indexar isso degrada a recuperação. A seleção abaixo é curada à mão porque o
corpus é pequeno e fixo; ``looks_like_filler`` é uma rede de segurança
heurística para qualquer reprocessamento futuro.
"""

from __future__ import annotations

import re
import unicodedata

# Faixas de páginas (inclusivas, 1-based) consideradas conteúdo útil.
KEEP_RANGES: dict[str, list[tuple[int, int]]] = {
    "Guia_da_Extensao_Curricular.pdf": [(11, 36)],
    "Guia_de_Atividades_Complementares_Atualizado_10_02_2026.pdf": [(2, 22)],
    "Guia de Curricularização da Extensão_vf.pdf": [(10, 45)],
}

# Padrões típicos das páginas de planner/diário e formulários em branco.
_FILLER_PATTERNS = (
    re.compile(r"tarefas da semana", re.IGNORECASE),
    re.compile(r"top 5", re.IGNORECASE),
    re.compile(r"boas mem[óo]rias", re.IGNORECASE),
    re.compile(r"espa[çc]o livre", re.IGNORECASE),
    re.compile(r"voc[êe] sabia\?", re.IGNORECASE),
    re.compile(r"planner do estudante", re.IGNORECASE),
)


def is_kept(source: str, page: int) -> bool:
    """True se a página estiver em uma faixa curada para indexação."""
    # Normalize to NFC so filenames from NFD filesystems (macOS, some Linux)
    # match the NFC keys written in this file.
    key = unicodedata.normalize("NFC", source)
    return any(lo <= page <= hi for lo, hi in KEEP_RANGES.get(key, []))


def looks_like_filler(text: str, *, min_chars: int = 60) -> bool:
    """Heurística: página de planner, formulário em branco ou quase vazia."""
    stripped = text.strip()
    if len(stripped) < min_chars:
        return True
    # Formulário em branco: dominado por underscores/linhas de preenchimento.
    if stripped.count("_") > max(20, len(stripped) // 8):
        return True
    return any(p.search(stripped) for p in _FILLER_PATTERNS)
