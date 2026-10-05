# Spec: spec verificável e aprovada (sdd-scaffold 1.7.0)

> **Tier:** 2 (muda os modelos de spec e plano, o verificador de PR e os pontos de montagem).
> **Status:** aprovada
> **Aprovado por:** thiago
> **Aprovado em:** 2026-10-05
> **Data:** 2026-10-05
> **Origem:** análise da prática SDD (curadoria A.5 do portal de padrões de engenharia), §7
> "Release 1", e os achados da curadoria da A.5. Companheira: spec do sdd-lifecycle 3.0.0.

## Motivação

1. **A spec não é verificável.** A skill pede requisitos `R1, R2…`, mas o `MODELO-spec.md` tem
   "Objetivos" e uma lista de checkboxes livre. Nada liga um requisito a uma tarefa ou a um teste.
2. **A aprovação não deixa rastro.** O checkpoint humano acontece na conversa. O cabeçalho da
   spec tem `Status`, mas não diz quem aprovou nem quando.
3. **A ambiguidade some com a conversa.** Uma dúvida em aberto não deixa marca no arquivo.
4. **Inconsistências internas:**
   - `sdd-processo.md` chama a implementação de "Fase 3", e a skill a numera como Fase 6;
   - o verificador de PR sai com 0 quando a base do diff não existe, então a trava passa em
     silêncio.
5. **Achados da curadoria da A.5:**
   - Codex e Antigravity documentam `.agents/skills`, e o template monta só `.claude`, `.codex`
     e `.kiro`;
   - o `CLAUDE.md` do template não importa o `AGENTS.md`;
   - o gerador instala a skill do ciclo a partir da `main`, sem versão fixada;
   - o README não tem o prompt para o próprio agente instalar o scaffold.

## Requisitos

**R1** O `MODELO-spec.md` tem a seção `## Requisitos`, com linhas `**R<n>** …`. Cada linha tem ao
menos um critério de aceite em GWT (`Dado/Quando/Então`) ou EARS (`QUANDO … O SISTEMA DEVE …`).
A seção substitui "Objetivos" e "Critérios de aceite".
- Critério: **Dado** o modelo novo, **Quando** se procura `^\*\*R\d+\*\*` na seção Requisitos,
  **Então** há ao menos um exemplo, e cada exemplo é seguido de uma linha `Critério`.

**R2** O cabeçalho do `MODELO-spec.md` tem `**Aprovado por:**` e `**Aprovado em:**`, vazios no
modelo.
- Critério: **Dado** uma spec com `Status: aprovada` e `Aprovado por` vazio, **Quando** o
  verificador roda, **Então** emite um AVISO de aprovação sem registro.

**R3** O `MODELO-spec.md` documenta o marcador `[ESCLARECER: …]` e traz a seção
`## Esclarecimentos`.
- Critério: **Dado** uma spec com `Status: aprovada`, ou citada por um plano do PR, que tem um
  marcador aberto fora de comentário, **Quando** o verificador roda, **Então** emite um AVISO com a
  contagem de marcadores.

**R4** O verificador avisa quando um `R<n>` da spec não tem linha de critério.
- Critério: **Dado** uma spec com `**R2**` sem `Critério` nem `Dado/Quando/Então` até o próximo
  `R`, **Quando** o verificador roda, **Então** emite um AVISO que cita `R2`.

**R5** O `MODELO-plano.md` pede `(R<n>)` no fim de cada tarefa e traz a tabela
`| R | veredito | evidência |` na seção de revisão adversarial.
- Critério: **Dado** o modelo novo, **Quando** é lido, **Então** a tarefa de exemplo termina com
  `(R1)` e a tabela existe.

**R6** O verificador confere o rastreio. Ele avisa nestes casos:
- um R<n> da spec do PR sem tarefa no plano;
- um R<n> sem citação em nenhum teste alterado no PR;
- uma tarefa que cita R<n> inexistente;
- num plano Tier 2 com a revisão adversarial preenchida, um R<n> ausente da tabela de veredito.

A mensagem diz "citado em teste", nunca "coberto".
- Critério: **Dado** uma spec com R1 e R2, um plano que cita só `(R1)` e um teste com
  `# cobre: R1`, **Quando** o verificador roda, **Então** emite AVISOs para R2 (sem tarefa e sem
  teste), e nenhum para R1.

**R7** Os avisos de R2 a R6 só disparam quando o artefato novo está presente: spec com ao menos
um `R<n>`, ou cabeçalho com `Aprovado por`. Nenhum deles bloqueia.
- Critério: **Dado** uma spec no formato da 1.6.1 (Objetivos, sem R<n>), **Quando** o
  verificador roda, **Então** não sai nenhum achado novo e o código de saída não muda.

**R8** O `MODELO-spec.md` e o `MODELO-plano.md` intocados não passam por "aprovados" nem por
"rastreados" (regressão da 1.6.1). Pergunta, comentário e placeholder não contam como conteúdo.
- Critério: **Dado** os modelos intocados lidos do template real, **Quando** o verificador roda,
  **Então** nenhuma checagem trata o modelo como spec aprovada com requisitos atendidos.

**R9** `qualidade.md` documenta a convenção de citar o requisito no teste (`# cobre: R<n>` no
nome, na docstring ou em comentário).
- Critério: **Dado** o steering de qualidade, **Quando** se procura `cobre: R`, **Então** a
  convenção e o seu limite (citação não é cobertura) aparecem.

**R10** O verificador sai com 2 e uma mensagem clara quando a base informada em `--base` não
existe. Hoje ele imprime "Nenhum arquivo alterado" e sai com 0.
- Critério: **Dado** `--base origin/inexistente`, **Quando** o verificador roda, **Então** imprime
  `ERRO: base origin/inexistente não encontrada` e sai com 2.

**R11** O template monta `.agents/skills` apontando para `skills/`, junto de `.claude/skills`,
`.codex/skills` e `.kiro/skills`, e o gerador preserva o link.
- Critério: **Dado** um projeto gerado, **Quando** se lê o link `.agents/skills`, **Então**
  `readlink` devolve `../skills`.

**R12** O `CLAUDE.md` do template importa a constituição com `@AGENTS.md`.
- Critério: **Dado** o projeto gerado, **Quando** se lê o `CLAUDE.md`, **Então** ele tem uma linha
  `@AGENTS.md`, e o texto continua sem regra própria.

**R13** O gerador instala a skill do ciclo da tag `v3.0.0` do sdd-lifecycle, e não da `main`.
`--origem-ciclo` continua aceitando URL ou caminho local.
- Critério: **Dado** a origem padrão, **Quando** o gerador monta o comando de clone, **Então** o
  comando fixa a tag `v3.0.0`. O teste verifica isso sem rede.

**R14** O README traz a seção "Instalar pelo próprio agente", com o prompt hoje não commitado.
O prompt muda em três pontos:
- faz o clone da tag `v1.7.0`;
- confere `.agents/skills` junto dos outros pontos de montagem;
- cita harness por nome só onde o comportamento difere.
- Critério: **Dado** o README, **Quando** se procura o prompt, **Então** ele tem
  `--branch v1.7.0` e `.agents/skills`, e não tem `--depth 1` sem tag.

**R15** `sdd-processo.md` numera as fases como a skill: a implementação é a Fase 6, e a volta é à
Fase 1.
- Critério: **Dado** o steering, **Quando** se procura "Fase 3 do SDD", **Então** não há
  resultado.

**R16** O `CHANGELOG.md` tem a entrada `[1.7.0]` com Adicionado, Modificado e Corrigido.
- Critério: **Dado** a branch pronta, **Quando** se lê o CHANGELOG, **Então** a entrada 1.7.0
  lista R1 a R15 em linguagem de usuário.

## Não-objetivos

- **Fica para a Release 2 (1.8.0):**
  - M4, a conferência pré-implementação;
  - M5, os "Requisitos afetados" no Tier 1;
  - M6, o teto de tamanho;
  - M9, a verificação da constituição no plano;
  - C12, o aviso de destilação.
- **Constituição:** o bloco `padrao-v1.0` do `AGENTS.md` não muda, inclusive a linha "PRD e spec
  aprovados antes". A divergência sobre o PRD se resolve na skill: a Fase 1 lê o PRD.
- **Spec viva (OpenSpec):** fora. Decidido o delta arquivado, ADR 0003 do portal.
- **Projetos já gerados:** não há mecanismo de atualização. Eles recebem a mudança só por cópia
  manual.
- **Hospedagem dos scripts de mecanismo no portal:** trabalho do portal, depois desta release.

## Design proposto

- **Modelos:** `template/docs/specs/MODELO-spec.md` e `template/docs/plans/MODELO-plano.md`. As
  orientações ficam em comentário HTML. Nenhuma pergunta vira prosa que pareça resposta (a lição
  da 1.6.1).
- **Verificador:** `template/scripts/verificar_pr.py` ganha as funções puras `checar_aprovacao`,
  `checar_marcadores`, `checar_criterios` e `analisar_rastreio`, chamadas por `analisar`.
  - `analisar` ganha o parâmetro opcional `testes: dict[str, str] | None = None`, compatível com
    os chamadores atuais.
  - `main()` passa a ler os arquivos de teste alterados.
  - `main()` confere a base com `git rev-parse --verify` antes do diff.
  - Os achados reaproveitam `Achado(bloqueia=False, …)`.
- **Gerador:** `criar_projeto.py` passa a usar `ORIGEM_CICLO_PADRAO` e uma constante
  `VERSAO_CICLO = "v3.0.0"`. O clone usa `--branch`. O template ganha o symlink `.agents/skills`.
- **Testes:** `test_criar_projeto.py` (link, `CLAUDE.md`, comando de clone) e os testes do
  verificador, todos lendo os modelos reais do template.
- **Impacto Arquitetural:** N/A. O repositório não tem compose, IaC nem diagrama próprios.

## Riscos e mitigações

- **Aviso em excesso.** Mitigação: R7 (opt-in por presença) e o teste de R7 com spec no formato
  1.6.1.
- **Falso "aprovado" com o modelo em branco.** Mitigação: R8, com testes sobre os modelos reais.
- **O link `.agents/skills` em Windows sem symlink.** Mesmo comportamento dos três links atuais;
  nada novo.
- **Tag `v3.0.0` ainda inexistente.** A release do scaffold só é marcada depois da tag da skill. O
  teste de R13 não usa rede.

## Esclarecimentos

### Sessão 2026-10-05

- P: Versão da skill companheira? → R: 3.0.0. A constituição do sdd-lifecycle trata mudança de
  critério de fase como major.
- P: M5 e C12 entram? → R: não, ficam na Release 2.
- P: O prompt "Instalar pelo próprio Kiro", não commitado? → R: entra, fixado na v1.7.0.
- P: E o PRD no `AGENTS.md:47`? → R: a skill lê o PRD; a constituição fica intacta.

## Threat-model

Não se aplica: a mudança não toca autenticação, entrada externa em runtime, segredo nem
privilégio de infraestrutura. O clone da skill por tag reduz superfície, porque fixa a origem.
