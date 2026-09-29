#!/usr/bin/env python3
"""Verifica que a constituição inline no AGENTS.md corresponde à versão declarada.

A camada 0 da governança vale para todos os projetos, então precisa estar sempre
no contexto do agente. Um arquivo em docs/ só entra quando alguém manda ler, o que
não serve para premissa. Por isso a constituição vive inline no AGENTS.md, entre
marcadores, e a cópia canônica em docs/constituicao/ existe para esta verificação.

Detecta dois problemas:
  1. o bloco inline foi editado localmente e divergiu da versão declarada;
  2. o projeto está numa versão anterior à publicada pela organização, quando o
     caminho de origem é informado por --origem.

Uso:
  python3 scripts/verificar_constituicao.py [--raiz CAMINHO] [--origem CAMINHO]

Saída: relatório. Exit code 1 apenas para divergência do bloco inline, que é
adulteração local. Defasagem de versão é informativa e sai 0, pela mesma razão do
drift check: um projeto pode ter motivo legítimo para ficar numa versão anterior.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

INICIO = re.compile(r"<!--\s*constituicao:inicio\s+(?P<versao>[\w.\-]+)\s*-->")
FIM = "<!-- constituicao:fim -->"


def extrair_bloco(agents: str) -> tuple[str, str] | None:
    m = INICIO.search(agents)
    if not m or FIM not in agents:
        return None
    corpo = agents[m.end():].split(FIM, 1)[0]
    return m.group("versao"), corpo.strip()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raiz", default=".")
    p.add_argument("--origem", default=None,
                   help="diretório da constituição publicada pela organização")
    args = p.parse_args()
    raiz = Path(args.raiz).resolve()

    caminho_agents = raiz / "AGENTS.md"
    if not caminho_agents.is_file():
        print("AGENTS.md não encontrado; nada a verificar.")
        return 0

    extraido = extrair_bloco(caminho_agents.read_text(encoding="utf-8"))
    if extraido is None:
        print("AGENTS.md não delimita a constituição. Esperado:")
        print("  <!-- constituicao:inicio <versao> -->  ...  <!-- constituicao:fim -->")
        return 1
    versao, inline = extraido

    canonico = raiz / "docs" / "constituicao" / f"{versao}.md"
    if not canonico.is_file():
        print(f"Versão declarada '{versao}', mas {canonico.relative_to(raiz)} não existe.")
        return 1

    if inline != canonico.read_text(encoding="utf-8").strip():
        print(f"DIVERGÊNCIA: o bloco inline no AGENTS.md não corresponde a {versao}.")
        print("A constituição é compartilhada e não se edita por projeto. Para adotar uma")
        print("versão nova, substitua o arquivo canônico e reinline o bloco.")
        return 1

    print(f"Constituição {versao}: bloco inline confere com o arquivo canônico.")

    if args.origem:
        pasta = Path(args.origem).expanduser().resolve()
        publicadas = sorted(pasta.glob("*.md")) if pasta.is_dir() else []
        if publicadas:
            mais_nova = publicadas[-1].stem
            if mais_nova != versao:
                print(f"AVISO: a organização publicou '{mais_nova}' e este projeto usa "
                      f"'{versao}'. Informativo, não bloqueia.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
