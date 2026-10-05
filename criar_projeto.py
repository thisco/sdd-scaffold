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
import sys
import tempfile
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / "template"

# A skill que conduz o ciclo SDD vive em repositório próprio e é instalada na geração,
# em vez de ser copiada para dentro deste template. Assim existe uma fonte só, e o
# projeto recebe a versão vigente no dia em que nasce, com a origem registrada.
ORIGEM_CICLO_PADRAO = "https://github.com/thisco/sdd-lifecycle.git"
# Tag da skill do ciclo que este scaffold instala. Fixar a tag evita que a `main` da skill
# mude o projeto no dia em que ele nasce. Vazio usa a branch padrão da origem.
VERSAO_CICLO = "v3.0.0"
EXTENSOES_TEXTO = {".md", ".yml", ".yaml", ".py", ".tf", ".toml", ".json",
                   ".txt", ".gitignore", ".drawio", ""}
# Artefatos de SO/cache nunca devem chegar ao projeto gerado. Atenção: `.DS_Store` tem
# suffix "" (nome só com ponto inicial), e "" está em EXTENSOES_TEXTO de propósito, para
# pegar arquivos de texto sem extensão. Sem este filtro o gerador tenta decodificar o
# binário como UTF-8 e estoura — ver test_nao_copia_artefatos_de_so_nem_cache.
IGNORAR = shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc", ".pytest_cache")


def instalar_skill_do_ciclo(alvo: Path, origem: str, versao: str = VERSAO_CICLO) -> bool:
    """Instala a skill do ciclo SDD em skills/sdd-lifecycle/.

    Devolve True se instalou. Falha de rede ou origem inacessível **não** aborta a
    geração: o projeto nasce sem a skill e com um arquivo explicando como instalar
    depois. Um gerador que quebra porque a rede caiu falha justamente quando alguém
    está começando um projeto. `versao` é a tag (ou branch) a clonar; vazia, usa a
    branch padrão da origem.
    """
    destino_skill = alvo / "skills" / "sdd-lifecycle"
    ref = ["--branch", versao] if versao else []
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "ciclo"
        r = subprocess.run(
            ["git", "clone", "--depth", "1", "--quiet", *ref, origem, str(clone)],
            capture_output=True, text=True,
        )
        if r.returncode != 0 or not (clone / "SKILL.md").is_file():
            erro = (r.stderr or "").strip() or "o clone não trouxe um SKILL.md"
            print(
                f"AVISO: a skill do ciclo não foi instalada (origem {origem}, "
                f"versão {versao or 'branch padrão'}).\n{erro}\n"
                'Se a tag não existe nessa origem, use --versao-ciclo "" para a branch padrão '
                "ou --versao-ciclo <tag existente>.",
                file=sys.stderr)
            (alvo / "skills" / "SKILL-CICLO-AUSENTE.md").write_text(
                "# A skill do ciclo SDD não foi instalada\n\n"
                f"Origem tentada: `{origem}` (versão: `{versao or 'branch padrão'}`)\n\n"
                f"Erro do git:\n\n```text\n{erro}\n```\n\n"
                "A geração seguiu sem ela, porque a skill é um acréscimo e não um\n"
                "pré-requisito. Para instalar depois:\n\n"
                "```bash\n"
                f"git clone {' '.join(['--depth 1', *ref])} {origem} /tmp/sdd-lifecycle\n"
                "cp -R /tmp/sdd-lifecycle skills/sdd-lifecycle\n"
                "rm -rf skills/sdd-lifecycle/.git\n"
                "```\n\n"
                "Ela fica visível em todas as ferramentas pelo mesmo ponto de montagem,\n"
                "porque `.claude/skills`, `.codex/skills`, `.kiro/skills` e\n"
                "`.agents/skills` apontam para `skills/`. Apague este arquivo depois de\n"
                "instalar.\n",
                encoding="utf-8")
            return False

        revisao = subprocess.run(["git", "-C", str(clone), "rev-parse", "--short", "HEAD"],
                                 capture_output=True, text=True).stdout.strip()
        shutil.copytree(clone, destino_skill,
                        ignore=shutil.ignore_patterns(".git", ".github", ".DS_Store",
                                                      "__pycache__", "*.pyc"))
        (destino_skill / "PROCEDENCIA.md").write_text(
            "# Procedência desta skill\n\n"
            f"- **Origem:** `{origem}`\n"
            f"- **Versão pedida:** `{versao or 'branch padrão'}`\n"
            f"- **Revisão instalada:** `{revisao or 'desconhecida'}`\n"
            f"- **Instalada em:** {dt.date.today().isoformat()}\n\n"
            "Esta skill não nasceu aqui: ela foi instalada na geração do projeto a partir\n"
            "do repositório acima. Editar o conteúdo aqui cria uma bifurcação silenciosa.\n"
            "Se a mudança serve para outros projetos, mande PR para a origem. Se serve só\n"
            "para este, crie uma skill local com outro nome e registre o motivo.\n",
            encoding="utf-8")
    return True


def gerar(nome: str, destino: Path | str, descricao: str, stack: str, deps: str,
          origem_ciclo: str | None = ORIGEM_CICLO_PADRAO,
          versao_ciclo: str = VERSAO_CICLO) -> Path:
    destino = Path(destino).expanduser().resolve()
    alvo = destino / nome
    if alvo.exists():
        raise FileExistsError(f"destino já existe: {alvo}")

    # symlinks=True preserva os pontos de montagem de skills (.claude/skills, .codex/skills,
    # .kiro/skills e .agents/skills apontam para skills/). Sem isso o copytree resolve cada
    # link e o projeto nasce com quatro cópias da mesma skill, que divergem no primeiro ajuste.
    shutil.copytree(TEMPLATE, alvo, ignore=IGNORAR, symlinks=True)

    trocas = {
        "{{NOME_PROJETO}}": nome,
        "{{DESCRICAO}}": descricao,
        "{{STACK}}": stack,
        "{{ARQUIVO_DEPENDENCIAS}}": deps,
        "{{DATA}}": dt.date.today().isoformat(),
    }
    for arquivo in alvo.rglob("*"):
        if arquivo.is_symlink():
            continue  # ponto de montagem: o corpo real já é visitado pelo caminho canônico
        if not arquivo.is_file() or arquivo.suffix not in EXTENSOES_TEXTO:
            continue
        try:
            texto = arquivo.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binário com extensão de texto: nada a substituir
        for chave, valor in trocas.items():
            texto = texto.replace(chave, valor)
        arquivo.write_text(texto, encoding="utf-8")

    if origem_ciclo:
        instalar_skill_do_ciclo(alvo, origem_ciclo, versao_ciclo)

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
    parser.add_argument("--origem-ciclo", default=ORIGEM_CICLO_PADRAO,
                        help="repositório ou caminho da skill do ciclo SDD")
    parser.add_argument("--versao-ciclo", default=VERSAO_CICLO,
                        help=f"tag da skill do ciclo (padrão {VERSAO_CICLO}); "
                             "vazio usa a branch padrão da origem")
    parser.add_argument("--sem-skill-do-ciclo", action="store_true",
                        help="não instalar a skill do ciclo SDD")
    args = parser.parse_args()

    alvo = gerar(args.nome, args.destino, args.descricao, args.stack, args.deps,
                 origem_ciclo=None if args.sem_skill_do_ciclo else args.origem_ciclo,
                 versao_ciclo=args.versao_ciclo)
    print(f"✔ Projeto criado em {alvo}")
    print("Próximos passos: revisar AGENTS.md, preencher docs/steering/, desenhar Arquitetura/arquitetura.drawio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
