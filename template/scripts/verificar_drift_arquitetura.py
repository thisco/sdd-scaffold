#!/usr/bin/env python3
"""Verificador de drift da Arquitetura Viva.

Compara o manifesto Arquitetura/mapa.yml com três fontes:
  1. labels dos nós do diagrama draw.io (XML);
  2. diretórios de módulos OpenTofu (infra/cloud/modules/);
  3. serviços do docker-compose local (infra/local/docker-compose.yml).

Uso: python3 scripts/verificar_drift_arquitetura.py [--raiz CAMINHO]
Saída: relatório de divergências. Exit code SEMPRE 0 (check informativo,
nunca bloqueante — decisão registrada na spec 2026-07-02).
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import unicodedata
from pathlib import Path

import yaml


def _normalizar(texto: str) -> str:
    """Minúsculas, sem acentos, espaços colapsados — para matching tolerante."""
    texto = html.unescape(texto)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto).strip().lower()


def extrair_labels_drawio(caminho: Path) -> list[str]:
    conteudo = caminho.read_text(encoding="utf-8")
    brutos = re.findall(r'value="([^"]+)"', conteudo)
    return [_normalizar(b) for b in brutos if _normalizar(b)]


def listar_modulos_tofu(diretorio: Path) -> set[str]:
    if not diretorio.is_dir():
        return set()
    return {p.name for p in diretorio.iterdir() if p.is_dir()}


def listar_servicos_compose(caminho: Path) -> set[str]:
    if not caminho.is_file():
        return set()
    dados = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    return set((dados.get("services") or {}).keys())


def verificar(raiz: Path) -> list[str]:
    """Retorna a lista de mensagens de drift (vazia = arquitetura em sincronia)."""
    mapa = yaml.safe_load((raiz / "Arquitetura" / "mapa.yml").read_text(encoding="utf-8"))
    componentes = mapa.get("componentes") or []

    labels = extrair_labels_drawio(raiz / mapa["diagrama"])
    modulos = listar_modulos_tofu(raiz / mapa["modulos_tofu"])
    servicos = listar_servicos_compose(raiz / mapa["compose"])

    mapeados_tofu = {c["tofu_modulo"] for c in componentes if c.get("tofu_modulo")}
    mapeados_compose = {s for c in componentes for s in (c.get("compose_servicos") or [])}

    drifts: list[str] = []

    for modulo in sorted(modulos - mapeados_tofu):
        drifts.append(
            f"módulo OpenTofu '{modulo}' existe em infra/cloud/modules/ mas não está no mapa.yml"
        )
    for servico in sorted(servicos - mapeados_compose):
        drifts.append(
            f"serviço compose '{servico}' existe no docker-compose mas não está no mapa.yml"
        )
    for modulo in sorted(mapeados_tofu - modulos):
        drifts.append(
            f"componente declara tofu_modulo '{modulo}' que não existe no diretório de módulos"
        )
    for servico in sorted(mapeados_compose - servicos):
        drifts.append(
            f"componente declara compose_servico '{servico}' que não existe no compose"
        )

    for comp in componentes:
        label = comp.get("drawio_label")
        if not label:
            continue  # null = decisão consciente de não desenhar
        alvo = _normalizar(label)
        if not any(alvo in rotulo for rotulo in labels):
            drifts.append(
                f"componente '{comp['nome']}': label '{label}' não encontrado"
                " em nenhum nó do diagrama"
            )
    return drifts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", default=".", help="raiz do repositório (default: .)")
    args = parser.parse_args()

    drifts = verificar(Path(args.raiz).resolve())
    if not drifts:
        print(
            "✔ Arquitetura em sincronia: mapa.yml × drawio × OpenTofu × compose"
            " sem divergências."
        )
    else:
        print(f"⚠ {len(drifts)} divergência(s) de arquitetura detectada(s):\n")
        for d in drifts:
            print(f"  - {d}")
        print(
            "\nAção esperada: atualizar Arquitetura/mapa.yml, o diagrama .drawio, o módulo"
            " OpenTofu ou o docker-compose na MESMA branch"
            " (steering: docs/steering/arquitetura.md)."
        )
    return 0  # informativo, nunca bloqueante


if __name__ == "__main__":
    sys.exit(main())
