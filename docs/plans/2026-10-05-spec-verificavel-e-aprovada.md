# Plano: spec verificável e aprovada (sdd-scaffold 1.7.0)

> **Tier:** 2 — muda os modelos de spec e plano, o verificador de PR, os pontos de montagem e o gerador
> **Spec relacionada:** `docs/specs/2026-10-05-spec-verificavel-e-aprovada.md` (aprovada em 2026-10-05)
> **Branch:** `feat/2026-10-05-spec-verificavel`
> **Data:** 2026-10-05

## Contexto

A spec aprovada pede R1 a R16. Os testes ficam em `test_criar_projeto.py`, que gera um projeto
temporário e importa o `scripts/verificar_pr.py` dele. Os testes do verificador leem os modelos
**reais** do template, nunca uma cópia montada à mão (lição da 1.6.1).

**Restrição de execução:** neste ambiente, rodar código do scaffold pode ser barrado pelo
classificador de permissões. Se isso acontecer, quem executa não contorna. Ele acrescenta o
comando exato em `/Users/thiago/curadoria-a5/pendentes.sh` (bloco `s170-<tarefa>`, um comando
por linha, caminho absoluto) e segue escrevendo o resto. O dono roda o lote, e a saída vai para
Evidências.

## Arquivos afetados

- `template/docs/specs/MODELO-spec.md`: `Requisitos` com R<n> e critério, `Aprovado por/em`,
  `[ESCLARECER]` e `Esclarecimentos`.
- `template/docs/plans/MODELO-plano.md`: `(R1)` na tarefa de exemplo e a tabela de veredito.
- `template/scripts/verificar_pr.py`, com as funções novas:
  - `checar_aprovacao(spec: str) -> list[Achado]`;
  - `checar_marcadores(spec: str, citada_por_plano: bool) -> list[Achado]`;
  - `checar_criterios(spec: str) -> list[Achado]`;
  - `analisar_rastreio(spec: str, plano: str, testes: dict[str, str], tier2: bool) -> list[Achado]`.

  Mudanças no que já existe:
  - `analisar(alterados, conteudos, migrations_na_base, testes=None)`;
  - `main()` lê os testes alterados (`tests/` ou `test_*.py`) e confere a base com
    `git rev-parse --verify`, saindo com 2 se ela não existir.
- `template/docs/steering/qualidade.md`: a convenção `# cobre: R<n>` e o limite dela.
- `template/docs/steering/sdd-processo.md`: na linha 52, "Fase 3" passa a "Fase 6"; a linha 53
  continua na "Fase 1".
- `template/.agents/skills`: symlink novo, `ln -s ../skills skills` dentro de
  `template/.agents/`.
- `template/CLAUDE.md`: a linha `@AGENTS.md`.
- `criar_projeto.py`:
  - a constante `VERSAO_CICLO = "v3.0.0"`;
  - a opção `--versao-ciclo`, com padrão `VERSAO_CICLO` (string vazia usa a branch padrão da
    origem);
  - o clone passa `--branch <versao>`;
  - a mensagem de fallback e a de pontos de montagem citam `.agents/skills`.
- `README.md`: a seção "Instalar pelo próprio agente", feita a partir da mudança não commitada.
- `test_criar_projeto.py`: os testes novos, listados abaixo.
- `CHANGELOG.md`: a entrada `[1.7.0]`.

## Plano de testes

Cada teste cita `# cobre: R<n>`. Teste vermelho antes do código.

| Teste | Prova |
|---|---|
| `test_modelo_spec_tem_requisitos_com_criterio` | R1: o modelo real tem `**R1**` e uma linha `Critério` |
| `test_aprovada_sem_aprovador_avisa` | R2 |
| `test_marcador_aberto_em_spec_aprovada_avisa` / `..._em_comentario_nao_conta` | R3 |
| `test_requisito_sem_criterio_avisa` | R4 |
| `test_modelo_plano_tem_rastreio_e_tabela` | R5 |
| `test_rastreio_r2_sem_tarefa_e_sem_teste` / `test_tarefa_cita_r_inexistente` / `test_tabela_veredito_incompleta` | R6 |
| `test_spec_formato_161_sem_achados_novos` | R7 |
| `test_modelos_intocados_nao_aprovados_nem_rastreados` | R8 |
| `test_qualidade_documenta_cobre_r` | R9 |
| `test_base_inexistente_sai_com_2` (repositório git temporário) | R10 |
| `test_projeto_gerado_monta_agents_skills` | R11 |
| `test_claude_md_importa_agents` | R12 |
| `test_clone_do_ciclo_fixa_versao` (troca `subprocess.run` por um dublê, sem rede) | R13 |
| `test_readme_prompt_fixa_versao` | R14 |
| `test_sdd_processo_sem_fase_3_do_sdd` | R15 |

## Impacto Arquitetural

- [x] O compose não muda: N/A, o repositório não tem infraestrutura própria.
- [x] Nenhum módulo de IaC é criado ou alterado: N/A.
- [x] O diagrama não muda: N/A.

## Estratégia de rollback

Release de template: reverter o merge na `main` e não publicar a tag `v1.7.0`. Projetos já
gerados não são afetados, porque não há mecanismo de atualização.

## Tarefas

- [x] **T1 (R1, R2, R3).** Escreva os testes de R1 a R3 (vermelho) e depois altere o
  `MODELO-spec.md`:
  - o cabeçalho ganha `Aprovado por/em`;
  - `## Requisitos` substitui "Objetivos" e "Critérios de aceite", com o exemplo `**R1**` e o
    critério GWT, com o EARS como alternativa;
  - o marcador e `## Esclarecimentos` são explicados em comentário HTML.

  Pergunta e orientação ficam sempre em comentário.
- [x] **T2 (R2, R3, R4, R7, R8).** Implemente `checar_aprovacao`, `checar_marcadores` e
  `checar_criterios` e chame as três em `analisar`. Ative por presença: só dispara com R<n> ou
  com `Aprovado por`. Remova os comentários antes de analisar (`COMENTARIO` já existe).
- [x] **T3 (R5, R6).** Altere o `MODELO-plano.md` e implemente `analisar_rastreio`:
  - o regex de requisito é `^\*\*R(\d+)\*\*`;
  - a tarefa cita `\(R\d+(?:, ?R\d+)*\)`;
  - o teste cita `\bR(\d+)\b`, contando só depois de `cobre:` ou no nome da função `test_`.

  O plano Tier 2 é a linha `> **Tier:** 2`; só ele confere a tabela, e só se a seção de revisão
  tiver linhas.
- [x] **T4 (R10).** `main()` faz `git rev-parse --verify --quiet <base>`. Em falha, imprime
  `ERRO: base <base> não encontrada` e retorna 2. Em `main()`, leia os testes alterados e passe-os
  a `analisar`.
- [x] **T5 (R9, R15).** Altere `qualidade.md` e `sdd-processo.md`.
- [x] **T6 (R11, R12).** Crie o symlink `template/.agents/skills` e acrescente `@AGENTS.md` ao
  `template/CLAUDE.md`. O teste gera o projeto e confere `readlink`.
- [x] **T7 (R13).** Em `criar_projeto.py`, crie `VERSAO_CICLO`, a opção `--versao-ciclo` e o
  `--branch` no clone. Atualize as mensagens.
- [x] **T8 (R14).** Transforme o diff não commitado do README na seção "Instalar pelo próprio
  agente":
  - clone `git clone --depth 1 --branch v1.7.0 …`;
  - o passo 3 confere `.agents/skills` junto dos demais pontos;
  - o título e o texto ficam neutros. O Kiro aparece como exemplo, e o `.kiro/permissions.yaml` é
    citado só como "se o harness for o Kiro".
- [ ] **T9 (R16).** Acrescente a entrada `[1.7.0] - 2026-10-05` no `CHANGELOG.md`.
- [ ] **T10.** Rode `python3 -m pytest -q test_criar_projeto.py`, ou o bloco equivalente no
  `pendentes.sh`, e cole a saída em Evidências. Ruff, se estiver configurado.
- [ ] **T11.** Revisão adversarial independente contra a spec, com a tabela por requisito.
- [ ] **T12.** Merge e tag `v1.7.0`, só depois da tag `v3.0.0` da skill e com a ordem do dono.

## Evidências

## Revisão adversarial: <data> — achados

| R | veredito | evidência |
|---|---|---|
