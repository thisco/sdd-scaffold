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

Limite: o hook só enxerga Edit, Write, NotebookEdit e MultiEdit. Escrita por comando de
shell passa por regras `ask` de Bash em .claude/settings.json, que cobrem só o padrão direto
(redirecionamento, cp, mv, interpretador em linha). A proteção é contra descuido, não má-fé.
"""
from __future__ import annotations

import fnmatch
import json
import os
import sys
from pathlib import Path

PROTEGIDOS = [
    "AGENTS.md",
    "docs/constituicao/*",
    "Arquitetura/*.drawio",
    ".claude/settings.json",
    ".kiro/permissions.yaml",
    ".codex/config.toml",
    "scripts/proteger_governanca.py",
    "CLAUDE.md",
    "GEMINI.md",
    "docs/adr/*",
    "Arquitetura/mapa.yml",
    ".github/workflows/*",
    ".github/*",
    "scripts/verificar_*.py",
    ".claude/settings.local.json",
]

FERRAMENTAS_DE_ESCRITA = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def relativo_ao_projeto(caminho: str) -> str:
    """Devolve o caminho relativo à raiz do projeto.

    A ferramenta envia `file_path` ABSOLUTO. Comparar a string crua contra padrões
    relativos deixa tudo passar, e foi assim que este hook nasceu inerte: os testes
    alimentavam caminho relativo, que é o que o autor supôs, e não o que o harness
    manda. Também resolve `..`, para que `docs/../AGENTS.md` não escape.
    """
    raiz = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
    try:
        p = Path(caminho)
        p = (p if p.is_absolute() else raiz / p).resolve()
        return p.relative_to(raiz).as_posix()
    except (ValueError, OSError):
        # fora da raiz do projeto: devolve o nome para ainda casar padrões simples
        return Path(caminho).name


def caminho_protegido(caminho: str) -> str | None:
    normalizado = relativo_ao_projeto(caminho)
    for padrao in PROTEGIDOS:
        # Caixa ignorada: em sistema de arquivos insensível a caixa (macOS, Windows),
        # `agents.md` é o `AGENTS.md`, e o fnmatch do POSIX distinguiria os dois.
        if fnmatch.fnmatchcase(normalizado.lower(), padrao.lower()):
            return padrao
    return None


def perguntar(motivo: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": motivo,
        }
    }))


def main() -> int:
    # Falha fechada: entrada que o hook não entende vira pedido de aprovação, e não
    # permissão tácita. Quem decide é uma pessoa, não um erro de parsing.
    try:
        evento = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        perguntar("O hook de governança não conseguiu ler a chamada da ferramenta; "
                  "confirme antes de seguir.")
        return 0

    if not isinstance(evento, dict) or evento.get("tool_name") not in FERRAMENTAS_DE_ESCRITA:
        return 0

    entrada = evento.get("tool_input") or {}
    alvo = entrada.get("file_path") or entrada.get("notebook_path") or ""
    if not alvo:
        perguntar("Ferramenta de escrita sem caminho reconhecível; o hook de governança "
                  "não consegue conferir o alvo. Confirme antes de seguir.")
        return 0

    padrao = caminho_protegido(alvo)
    if padrao is None:
        return 0

    perguntar(
        f"{alvo} casa com o padrão protegido '{padrao}'. Este arquivo carrega a "
        "governança do repositório e não deve ser reescrito pelo agente sem que "
        "uma pessoa peça. Se a mudança for intencional, aprove; se ela apareceu "
        "no meio de outra tarefa, é sinal de que a tarefa saiu do escopo."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
