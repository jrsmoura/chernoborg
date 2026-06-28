"""Seleção de páginas: o que entra no índice e o que é descartado.

Indexa os arquivos inteiros e delega a filtragem à heurística ``looks_like_filler``:
- Páginas com menos de 100 caracteres úteis (só cabeçalho + número de página)
- Formulários em branco dominados por underscores (RELATÓRIO INDIVIDUAL)
- Páginas de planner/diário identificadas por padrões textuais

O ``min_chars`` foi ajustado para 100 para capturar páginas que contêm apenas
o cabeçalho do guia + número de página (74 chars), que não acrescentam conteúdo.
"""

from __future__ import annotations

import re
import unicodedata

# Faixas de páginas (inclusivas, 1-based) — abrange o arquivo inteiro.
# A filtragem fina é feita por looks_like_filler.
KEEP_RANGES: dict[str, list[tuple[int, int]]] = {
    "Guia_de_Atividades_Complementares_Atualizado_10_02_2026.pdf": [(1, 24)],
    "Guia_de_Curricularização_da_Extensao_vf.pdf": [(1, 49)],
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


def looks_like_filler(text: str, *, min_chars: int = 100) -> bool:
    """Heurística: página de planner, formulário em branco ou quase vazia."""
    stripped = text.strip()
    if len(stripped) < min_chars:
        return True
    # Formulário em branco: dominado por underscores/linhas de preenchimento.
    if stripped.count("_") > max(20, len(stripped) // 8):
        return True
    return any(p.search(stripped) for p in _FILLER_PATTERNS)
