#!/usr/bin/env python3
"""Gera um projeto novo a partir do template sdd-scaffold.

Uso:
  python3 criar_projeto.py --nome meu-projeto --destino ~/Workspace \
      [--descricao "..."] [--stack "..."] [--deps requirements.txt]
"""
from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / "template"
EXTENSOES_TEXTO = {".md", ".yml", ".yaml", ".py", ".tf", ".gitignore", ".drawio", ""}
# Artefatos de SO/cache nunca devem chegar ao projeto gerado. Atenção: `.DS_Store` tem
# suffix "" (nome só com ponto inicial), e "" está em EXTENSOES_TEXTO de propósito, para
# pegar arquivos de texto sem extensão. Sem este filtro o gerador tenta decodificar o
# binário como UTF-8 e estoura — ver test_nao_copia_artefatos_de_so_nem_cache.
IGNORAR = shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc", ".pytest_cache")


def gerar(nome: str, destino: Path | str, descricao: str, stack: str, deps: str) -> Path:
    destino = Path(destino).expanduser().resolve()
    alvo = destino / nome
    if alvo.exists():
        raise FileExistsError(f"destino já existe: {alvo}")

    shutil.copytree(TEMPLATE, alvo, ignore=IGNORAR)

    trocas = {
        "{{NOME_PROJETO}}": nome,
        "{{DESCRICAO}}": descricao,
        "{{STACK}}": stack,
        "{{ARQUIVO_DEPENDENCIAS}}": deps,
        "{{DATA}}": dt.date.today().isoformat(),
    }
    for arquivo in alvo.rglob("*"):
        if not arquivo.is_file() or arquivo.suffix not in EXTENSOES_TEXTO:
            continue
        try:
            texto = arquivo.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binário com extensão de texto: nada a substituir
        for chave, valor in trocas.items():
            texto = texto.replace(chave, valor)
        arquivo.write_text(texto, encoding="utf-8")

    subprocess.run(["git", "init", "-b", "main"], cwd=alvo, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=alvo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"feat: estrutura inicial de {nome} via sdd-scaffold"],
        cwd=alvo, check=True, capture_output=True,
    )
    return alvo


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nome", required=True)
    parser.add_argument("--destino", required=True)
    parser.add_argument("--descricao", default="<!-- preencher: descrição do projeto -->")
    parser.add_argument("--stack", default="<!-- preencher: linguagem e frameworks -->")
    parser.add_argument("--deps", default="requirements.txt")
    args = parser.parse_args()

    alvo = gerar(args.nome, args.destino, args.descricao, args.stack, args.deps)
    print(f"✔ Projeto criado em {alvo}")
    print("Próximos passos: revisar AGENTS.md, preencher docs/steering/, desenhar Arquitetura/arquitetura.drawio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
