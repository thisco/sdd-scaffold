#!/usr/bin/env python3
"""Impede que o agente reescreva a governança do repositório sem alguém pedir.

Roda como hook PreToolUse: recebe a chamada de tool em JSON na entrada padrão e
decide antes de a tool executar. Como é código fora do modelo, o agente não
negocia com ele.

A mesma regra existe nas outras duas ferramentas por mecanismo próprio:
  - Kiro: .kiro/permissions.yaml, com precedência deny > ask > allow
  - Codex: no modo de escrita restrita, .git e diretórios de config ficam somente-leitura

O agente escreve código, testes, specs e planos. Ele não reescreve a constituição,
as decisões já registradas nem o mapa de arquitetura por conta própria.
"""
from __future__ import annotations

import fnmatch
import json
import sys

PROTEGIDOS = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "docs/adr/*",
    "Arquitetura/mapa.yml",
    ".github/workflows/*",
]

FERRAMENTAS_DE_ESCRITA = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def caminho_protegido(caminho: str) -> str | None:
    # Atenção: lstrip remove caracteres, não prefixo. `".github/x".lstrip("./")` devolve
    # "github/x" e quebra qualquer padrão que comece com ponto.
    normalizado = caminho
    for prefixo in ("./", "/"):
        if normalizado.startswith(prefixo):
            normalizado = normalizado[len(prefixo):]
    for padrao in PROTEGIDOS:
        if fnmatch.fnmatch(normalizado, padrao) or normalizado == padrao:
            return padrao
    return None


def main() -> int:
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # entrada inesperada nunca deve travar a sessão

    if evento.get("tool_name") not in FERRAMENTAS_DE_ESCRITA:
        return 0

    alvo = (evento.get("tool_input") or {}).get("file_path", "")
    if not alvo:
        return 0

    padrao = caminho_protegido(alvo)
    if padrao is None:
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"{alvo} casa com o padrão protegido '{padrao}'. Este arquivo carrega a "
                "governança do repositório e não deve ser reescrito pelo agente sem que "
                "uma pessoa peça. Se a mudança for intencional, aprove; se ela apareceu "
                "no meio de outra tarefa, é sinal de que a tarefa saiu do escopo."
            ),
        }
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
