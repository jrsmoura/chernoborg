"""Avaliação de acurácia do agente assistente_iesb.

Envia cada pergunta do questions_pt.json ao ADK local (127.0.0.1:8001),
extrai a resposta e verifica se contém os keywords esperados.

Uso:
    python tests/run_accuracy.py
"""

from __future__ import annotations

import json
import sys
import time
import uuid
from pathlib import Path

import urllib.request
import urllib.error

ADK_BASE = "http://127.0.0.1:8001"
APP_NAME = "assistente_iesb"
USER_ID  = "test_accuracy"
PASS_THRESHOLD = 0.5  # fração mínima de keywords presentes para PASS


def _post(url: str, body: dict) -> dict | list:
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def create_session() -> str:
    url = f"{ADK_BASE}/apps/{APP_NAME}/users/{USER_ID}/sessions"
    result = _post(url, {})
    return result.get("id") or result.get("session_id") or str(uuid.uuid4())


def ask(session_id: str, question: str) -> str:
    url = f"{ADK_BASE}/run"
    body = {
        "app_name": APP_NAME,
        "user_id": USER_ID,
        "session_id": session_id,
        "new_message": {"role": "user", "parts": [{"text": question}]},
    }
    events = _post(url, body)
    if not isinstance(events, list):
        return ""
    for event in reversed(events):
        content = event.get("content") or {}
        if content.get("role") == "model":
            parts = content.get("parts") or []
            texts = [p.get("text", "") for p in parts if p.get("text")]
            if texts:
                return " ".join(texts)
    return ""


def evaluate(response: str, keywords: list[str]) -> tuple[bool, int, int]:
    resp_lower = response.lower()
    found = sum(1 for kw in keywords if kw.lower() in resp_lower)
    total = len(keywords)
    passed = (found / total) >= PASS_THRESHOLD if total else False
    return passed, found, total


def main() -> None:
    questions_file = Path(__file__).parent / "questions_pt.json"
    questions = json.loads(questions_file.read_text())

    results = []
    passed_total = 0

    print(f"\n{'='*72}")
    print(f"  Avaliação de Acurácia — assistente_iesb")
    print(f"  {len(questions)} perguntas  |  threshold: {PASS_THRESHOLD:.0%} dos keywords")
    print(f"  Sessão independente por pergunta | 3 tentativas com backoff")
    print(f"{'='*72}\n")

    for q in questions:
        qid      = q["id"]
        pergunta = q["pergunta"]
        keywords = q["keywords"]

        response = ""
        for attempt in range(3):
            try:
                session_id = create_session()
                response = ask(session_id, pergunta)
                break
            except Exception as e:
                wait = 5 * (attempt + 1)
                print(f"  [tentativa {attempt+1} falhou: {e}  aguardando {wait}s]")
                time.sleep(wait)
                response = f"[ERRO após 3 tentativas: {e}]"

        time.sleep(2)  # respeitar rate limit do Bedrock

        passed, found, total = evaluate(response, keywords)
        status = "PASS" if passed else "FAIL"
        if passed:
            passed_total += 1

        snippet = response[:120].replace("\n", " ") if response else "(sem resposta)"
        print(f"[{status}] {qid}: {pergunta}")
        print(f"       Keywords: {found}/{total} encontrados")
        print(f"       Resposta: {snippet}")
        print()

        results.append({
            "id": qid,
            "pergunta": pergunta,
            "status": status,
            "keywords_found": found,
            "keywords_total": total,
            "response_snippet": snippet,
            "full_response": response,
        })

    accuracy = passed_total / len(questions) * 100
    print(f"{'='*72}")
    print(f"  RESULTADO: {passed_total}/{len(questions)} PASS  ({accuracy:.1f}% acurácia)")
    print(f"{'='*72}\n")

    out_file = Path(__file__).parent / "accuracy_results.json"
    out_file.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"Resultados detalhados salvos em: {out_file}")

    # summary by category
    by_cat: dict[str, list[bool]] = {}
    for r in results:
        cat = r["id"].split("-")[0]
        by_cat.setdefault(cat, []).append(r["status"] == "PASS")

    print("\nPor categoria:")
    for cat, statuses in sorted(by_cat.items()):
        pct = sum(statuses) / len(statuses) * 100
        print(f"  {cat}: {sum(statuses)}/{len(statuses)}  ({pct:.0f}%)")


if __name__ == "__main__":
    main()
