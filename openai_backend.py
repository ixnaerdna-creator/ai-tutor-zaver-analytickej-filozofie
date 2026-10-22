"""Jediná integračná vrstva pre OpenAI Responses API (bez externých nástrojov).

Kľúč sa načítava výhradne zo Streamlit Secrets/prostredia; do logov sa nezapisuje.
Zdroje zostávajú lokálne. Do API sa odosiela len práve vytvorený prompt s relevantnými
úryvkami (a priebehom dialógu) podľa logiky príslušného AI tútora.
"""
from __future__ import annotations
from dataclasses import dataclass
from openai import OpenAI


@dataclass(frozen=True)
class TextResult:
    text: str


def make_client(api_key: str, timeout_ms: int = 120000) -> OpenAI:
    """Vytvor klienta s obmedzeným počtom opakovaní a vhodným timeoutom."""
    timeout_s = max(30.0, min(240.0, float(timeout_ms) / 1000.0))
    return OpenAI(api_key=api_key, timeout=timeout_s, max_retries=1)


def generate_content(client: OpenAI, *, model: str, contents: str,
                     system: str, max_output_tokens: int = 3000,
                     reasoning_effort: str = "low") -> TextResult:
    """Generuj odpoveď s explicitnými inštrukciami a bez nástrojov.

    Nepripúšťa web/file search: zdrojom zostáva iba priložená časť korpusu.
    store=False, aby sa odpoveď neukladala ako stavový objekt Responses API.
    """
    effort = (reasoning_effort or "low").strip().lower()
    if effort == "minimal":
        effort = "low"
    if effort not in {"none", "low", "medium", "high", "xhigh", "max"}:
        effort = "low"
    if effort == "none" and model != "gpt-6-luna":
        effort = "low"
    response = client.responses.create(
        model=model,
        instructions=system,
        input=contents,
        max_output_tokens=max(1500, int(max_output_tokens)),
        reasoning={"effort": effort},
        store=False,
    )
    answer = (getattr(response, "output_text", "") or "").strip()
    if not answer:
        raise RuntimeError(
            "OpenAI API vrátilo prázdnu odpoveď. Overte názov modelu, "
            "výstupný limit a stav účtu."
        )
    return TextResult(text=answer)
