#!/usr/bin/env python3
"""Verifica, no PR, as normas que o processo exige mas ninguém conferia.

A constituição pede spec com threat-model quando a mudança toca superfície
sensível, plano com estratégia de rollback quando mexe em schema ou deploy, e
evidência de teste colada no plano antes de concluir. Até aqui isso era texto
orientando. Este script é o mecanismo que verifica.

Severidades, e a razão de cada uma:

  BLOQUEIA  alterar migration que já existe na base de comparação. Editar uma
            migration já aplicada corrompe o histórico de schema de quem já
            rodou a anterior. É inequívoco e o estrago é difícil de desfazer.

  AVISA     threat-model, rollback e evidência. Envolvem julgamento sobre o que
            é suficiente, e um portão que reprova por julgamento ensina o time a
            contornar o portão. O aviso aparece no PR e é endereçável por gente.

Uso:
  python3 scripts/verificar_pr.py [--base origin/main]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# Superfícies em que a constituição exige threat-model na spec.
#
# As fronteiras à esquerda e à direita são obrigatórias. Sem elas, tokens curtos casam
# dentro de palavras comuns e o aviso vira ruído: "iam" casa no meio de LEIAME.md, e um
# aviso que dispara em arquivo irrelevante ensina o time a ignorar todos os avisos.
# Palavras inteiras, não prefixos: "auth*" casaria em "authorship", que não tem
# nada a ver com autenticação. A lista é curta e conhecida, então enumerar sai
# mais barato do que caçar falso positivo depois.
SENSIVEL = re.compile(
    r"(?<![0-9A-Za-zÀ-ÿ])"
    r"(?:authentication|authorization|authorize|autentica\w*|autoriza\w*|"
    r"credenciais|credencial|webhook|endpoint|upload|login|logout|"
    r"sess(?:ao|ão)|authn|authz|auth|iam|rbac|jwt|oauth|oidc|"
    r"secrets?|segredos?|tokens?)"
    r"(?![0-9A-Za-zÀ-ÿ])"
    r"|infra/cloud",
    re.I,
)
MIGRATION = re.compile(r"(^|/)(migrations?|alembic)/", re.I)
CODIGO = re.compile(r"\.(py|ts|tsx|js|jsx|go|java|rb|rs|kt|cs)$", re.I)
PLANO = re.compile(r"^docs/plans/\d{4}-\d{2}-\d{2}-.+\.md$")
SPEC = re.compile(r"^docs/specs/\d{4}-\d{2}-\d{2}-.+\.md$")

# Sinais de que a evidência foi de fato colada, e não prometida.
EVIDENCIA = re.compile(r"(passed|passou|ok\b|failed|\d+\s+test|coverage|cobertura|```)", re.I)

COMENTARIO = re.compile(r"<!--.*?-->", re.S)
RESIDUO = re.compile(r"^[\s\-*>#]*(\.\.\.|…|TODO|TBD|N/?A)?[\s\-*>#]*$", re.I)
# Item de checklist vazio e pergunta sem resposta não contam como preenchimento.
# O modelo lista as cinco perguntas em prosa numerada: se "há linha não vazia"
# bastasse, o modelo intocado passaria por estar preenchido.
CHECKBOX_VAZIO = re.compile(r"^\s*[-*]\s*\[\s*\]")
PERGUNTA = re.compile(r"\?\s*$")

# Spec verificável: requisito `**R<n>** texto`, status, aprovação e marcador de dúvida.
# Texto só de placeholder (`<...>`, `...`) não é requisito: é o modelo intocado.
REQUISITO = re.compile(r"^\*\*R(\d+)\*\*[ \t]*(.*)$", re.M)
PLACEHOLDER = re.compile(r"^(<[^>]*>|\.\.\.|…)?$")
STATUS = re.compile(r"^>?\s*\*\*Status:\*\*[ \t]*(.*)$", re.M | re.I)
APROVADO_POR = re.compile(r"^>?\s*\*\*Aprovado por:\*\*[ \t]*(.*)$", re.M | re.I)
MARCADOR = re.compile(r"\[ESCLARECER:[^\]]*\]")
CRITERIO = re.compile(r"crit[ée]rio|\bDado\b.*\bQuando\b|\bQUANDO\b", re.I)


def secao_preenchida(texto: str, *titulos: str) -> bool:
    """A seção existe E tem conteúdo de verdade sob o título.

    Procurar a palavra no documento inteiro não serve: os modelos em docs/ citam
    "threat-model" e "rollback" dentro de comentários de orientação, então uma spec
    copiada do modelo e nunca preenchida passaria no teste. O que conta é haver
    conteúdo sob o título, depois de remover comentários e marcadores vazios.
    """
    if not texto:
        return False
    alvo = "|".join(re.escape(x) for x in titulos)
    m = re.search(rf"^#{{1,6}}\s*.*?({alvo}).*?$", texto, re.I | re.M)
    if not m:
        return False
    resto = texto[m.end():]
    proximo = re.search(r"^#{1,6}\s", resto, re.M)
    corpo = resto[: proximo.start()] if proximo else resto
    corpo = COMENTARIO.sub("", corpo)
    for linha in corpo.splitlines():
        texto = linha.strip()
        if not texto or RESIDUO.match(linha) or CHECKBOX_VAZIO.match(linha):
            continue
        if PERGUNTA.search(texto):
            continue  # pergunta do modelo, ainda sem resposta
        return True
    return False


@dataclass
class Achado:
    bloqueia: bool
    mensagem: str

    def __str__(self) -> str:
        return ("BLOQUEIA: " if self.bloqueia else "AVISO: ") + self.mensagem


def analisar(alterados: list[str], conteudos: dict[str, str],
             migrations_na_base: set[str],
             testes: dict[str, str] | None = None) -> list[Achado]:
    """Função pura: recebe o retrato do PR e devolve os achados.

    `alterados` são os caminhos tocados; `conteudos` mapeia caminho para texto
    dos arquivos de plano e spec; `migrations_na_base` são as migrations que já
    existem no alvo do merge; `testes` mapeia caminho para texto dos testes
    alterados (opcional, para o rastreio de requisitos).
    """
    achados: list[Achado] = []

    for caminho in alterados:
        if MIGRATION.search(caminho) and caminho in migrations_na_base:
            achados.append(Achado(True, (
                f"{caminho} já existe na base e foi alterado. Migration aplicada não se edita: "
                "crie uma migration corretiva incremental."
            )))

    planos = [c for c in alterados if PLANO.match(c)]
    specs = [c for c in alterados if SPEC.match(c)]

    for s in specs:
        spec = conteudos.get(s, "")
        citada = any(s in conteudos.get(p, "") for p in planos)
        for a in (checar_aprovacao(spec) + checar_marcadores(spec, citada)
                  + checar_criterios(spec)):
            achados.append(Achado(a.bloqueia, f"{s}: {a.mensagem}"))

    toca_sensivel = [c for c in alterados if SENSIVEL.search(c)]
    if toca_sensivel:
        respondeu = any(
            secao_preenchida(conteudos.get(s, ""), "threat-model", "threat model",
                             "modelo de ameaça", "ameaças")
            for s in specs
        )
        if not respondeu:
            achados.append(Achado(False, (
                "a mudança toca superfície sensível (" + ", ".join(toca_sensivel[:3]) +
                ") e nenhuma spec do PR responde ao checklist de threat-model. "
                "Cinco perguntas em docs/steering/seguranca.md; cada sim pede um parágrafo "
                "de mitigação."
            )))

    toca_schema = [c for c in alterados if MIGRATION.search(c)]
    if toca_schema:
        declarou = any(
            secao_preenchida(conteudos.get(p, ""), "rollback", "reversão", "downgrade")
            for p in planos
        )
        if not declarou:
            achados.append(Achado(False, (
                "a mudança altera schema e nenhum plano do PR declara a estratégia de rollback. "
                "Declare antes de executar: downgrade testado, redeploy da imagem anterior ou "
                "restore de backup."
            )))

    toca_codigo = any(CODIGO.search(c) for c in alterados)
    if toca_codigo:
        if not planos:
            achados.append(Achado(False, (
                "o PR altera código e não traz plano em docs/plans/. Tier 0 dispensa plano; "
                "se este não for Tier 0, o plano está faltando."
            )))
        else:
            colou = any(
                secao_preenchida(conteudos.get(p, ""), "evidência", "evidencias", "evidências")
                and EVIDENCIA.search(COMENTARIO.sub("", conteudos.get(p, "")))
                for p in planos
            )
            if not colou:
                achados.append(Achado(False, (
                    "o plano não traz evidência colada de teste ou lint. Afirmação de sucesso "
                    "sem saída de execução não encerra a tarefa."
                )))

    return achados


def requisitos(spec: str) -> dict[int, str]:
    """Requisitos `**R<n>**` da spec, com o bloco de texto de cada um.

    O bloco vai da linha do requisito até o próximo requisito ou título. Comentário
    HTML sai antes, e requisito só de placeholder não conta: é o modelo intocado.
    """
    texto = COMENTARIO.sub("", spec)
    marcas = list(REQUISITO.finditer(texto))
    blocos: dict[int, str] = {}
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        titulo = re.search(r"^#{1,6}\s", texto[m.end():fim], re.M)
        if titulo:
            fim = m.end() + titulo.start()
        if PLACEHOLDER.match(m.group(2).strip()):
            continue
        blocos[int(m.group(1))] = texto[m.start():fim]
    return blocos


def checar_aprovacao(spec: str) -> list[Achado]:
    """Spec com Status `aprovada` precisa dizer quem aprovou.

    Só dispara com o artefato novo presente (R7): a linha `Aprovado por` no cabeçalho
    ou ao menos um requisito R<n>. O status é comparado por igualdade, porque o modelo
    lista as quatro opções na mesma linha e não pode passar por aprovado.
    """
    texto = COMENTARIO.sub("", spec)
    status = STATUS.search(texto)
    if not status or status.group(1).strip().lower() != "aprovada":
        return []
    por = APROVADO_POR.search(texto)
    if not por and not requisitos(spec):
        return []
    if por and por.group(1).strip():
        return []
    return [Achado(False, (
        "spec com Status aprovada e aprovação sem registro: preencha `Aprovado por` e "
        "`Aprovado em` no cabeçalho."
    ))]


def checar_marcadores(spec: str, citada_por_plano: bool) -> list[Achado]:
    """Marcador `[ESCLARECER: …]` aberto, fora de comentário, não passa para a implementação."""
    texto = COMENTARIO.sub("", spec)
    status = STATUS.search(texto)
    aprovada = bool(status) and status.group(1).strip().lower() == "aprovada"
    if not (aprovada or citada_por_plano):
        return []
    abertos = MARCADOR.findall(texto)
    if not abertos:
        return []
    return [Achado(False, (
        f"{len(abertos)} marcador(es) [ESCLARECER] aberto(s) numa spec aprovada ou citada "
        "por plano. Resolva, apague o marcador e registre a resposta em Esclarecimentos."
    ))]


def checar_criterios(spec: str) -> list[Achado]:
    """Todo requisito R<n> traz ao menos um critério de aceite (GWT ou EARS)."""
    sem = [n for n, bloco in requisitos(spec).items() if not CRITERIO.search(bloco)]
    return [Achado(False, (
        f"R{n} sem critério de aceite: acrescente uma linha `Critério` com "
        "Dado/Quando/Então (ou QUANDO … O SISTEMA DEVE …)."
    )) for n in sorted(sem)]


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", default="origin/main")
    p.add_argument("--raiz", default=".")
    args = p.parse_args()
    raiz = Path(args.raiz).resolve()

    alterados = [c for c in _git("-C", str(raiz), "diff", "--name-only",
                                 f"{args.base}...HEAD").splitlines() if c]
    if not alterados:
        print("Nenhum arquivo alterado em relação a", args.base)
        return 0

    conteudos = {}
    for caminho in alterados:
        if PLANO.match(caminho) or SPEC.match(caminho):
            arquivo = raiz / caminho
            if arquivo.is_file():
                conteudos[caminho] = arquivo.read_text(encoding="utf-8", errors="replace")

    na_base = {c for c in _git("-C", str(raiz), "ls-tree", "-r", "--name-only",
                               args.base).splitlines() if MIGRATION.search(c)}

    achados = analisar(alterados, conteudos, na_base)
    if not achados:
        print(f"Verificação de PR: {len(alterados)} arquivo(s), nenhum achado.")
        return 0

    for a in achados:
        print(a)
        nivel = "error" if a.bloqueia else "warning"
        print(f"::{nivel} title=Verificação de PR::{a.mensagem}")

    return 1 if any(a.bloqueia for a in achados) else 0


if __name__ == "__main__":
    raise SystemExit(main())
