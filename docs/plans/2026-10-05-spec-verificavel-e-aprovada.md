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
- [x] **T9 (R16).** Acrescente a entrada `[1.7.0] - 2026-10-05` no `CHANGELOG.md`.
- [x] **T10.** Rode `python3 -m pytest -q test_criar_projeto.py`, ou o bloco equivalente no
  `pendentes.sh`, e cole a saída em Evidências. Ruff, se estiver configurado.
- [x] **T11.** Revisão adversarial independente contra a spec, com a tabela por requisito.
- [x] **T12.** Merge e tag `v1.7.0`, só depois da tag `v3.0.0` da skill e com a ordem do dono.

## Evidências

O `pytest` não estava instalado no Python do sistema. A execução usou um venv fora do
repositório, com `pytest` e `pyyaml` (os mesmos pacotes do job de CI). Ruff não está configurado
no repositório. Cada tarefa viu o teste novo falhar pelo motivo esperado (ausência do modelo ou
da função) antes da implementação.

```text
$ python -m pytest -q -p no:cacheprovider test_criar_projeto.py -v
============================= test session starts ==============================
platform darwin -- Python 3.14.8, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/thiago/Documents/Workspace/repos/sdd-scaffold
collected 47 items

test_criar_projeto.py ...............................................    [100%]

============================= 47 passed in 19.10s ==============================
```

### Correções da revisão

| Achado | Teste que o cobre |
|---|---|
| 1. "quando" em prosa não é critério | `test_quando_em_prosa_nao_conta_como_criterio` (R4) |
| 2. marcador em código inline ou cercado | `test_marcador_em_codigo_nao_conta` (R3) |
| 3. spec aprovada sem R<n> válido; `**R1:**` e `- **R2**` passam a contar | `test_aprovada_sem_requisitos_validos_avisa` (R8) |
| 4. tarefas sob `###` | `test_tarefas_sob_subtitulo_contam` (R6) |
| 5. marcador só com artefato novo | `test_marcador_em_spec_formato_161_nao_avisa` (R7) |
| 6. `aprovada (data)` e `aprovada.` | `test_status_aprovada_com_texto_depois_e_reconhecido` (R2) |
| 7. R<n> em bloco de código | `test_requisito_em_bloco_de_codigo_nao_conta` (R4) |
| 8. falha no clone da tag avisa em stderr | `test_falha_no_clone_da_tag_avisa_em_stderr` (R13) |

Os oito testes falharam antes da correção (8 failed, 47 passed) e passam depois.

```text
$ python -m pytest -q -p no:cacheprovider test_criar_projeto.py
...............................................................          [100%]
55 passed in 21.08s

$ python3 template/scripts/verificar_pr.py --base main --raiz .
Verificação de PR: 13 arquivo(s), nenhum achado.
```

## Revisão adversarial: 2026-10-05 — achados

Revisor independente, sessão nova, modelo de raciocínio potente, contra a spec. Suíte rodada:
47 passed. Verificador rodado na própria branch (`--base main`).

| R | veredito | evidência |
|---|---|---|
| R1 | atendido | MODELO-spec.md:16,27-28 |
| R2 | atendido | MODELO-spec.md:6-7; verificar_pr.py:226-245 |
| R3 | parcial | verificar_pr.py:73,255; falso positivo com código inline (achado 2) |
| R4 | parcial | verificar_pr.py:80; "quando" em prosa mascara a falta de critério (achado 1) |
| R5 | atendido | MODELO-plano.md:48,65 |
| R6 | atendido | verificar_pr.py:310-341; mensagem "citado em teste" (L330) |
| R7 | atendido | verificar_pr.py:238,318; ressalva no achado 5 |
| R8 | atendido | test_criar_projeto.py:632; brecha no achado 3 |
| R9 | atendido | qualidade.md:24-33 |
| R10 | atendido | verificar_pr.py:355-361; saída 2 testada; qualidade.yml:116 com fetch-depth 0 |
| R11 | atendido | template/.agents/skills -> ../skills; test:811 |
| R12 | atendido | template/CLAUDE.md:6 |
| R13 | atendido | criar_projeto.py:25,45-49; test:863 com tag real em origem local |
| R14 | atendido | README.md:213,231 |
| R15 | atendido | sdd-processo.md:52 |
| R16 | atendido | CHANGELOG.md:6-45 |

Achados e tratamento:

1. **Médio**, `verificar_pr.py:80`. Com `re.I`, qualquer "quando" na prosa conta como critério.
   Tratamento: aceitar só a linha `Critério`, a sequência Dado…Quando…Então ou o EARS em caixa
   alta.
2. **Médio**, `verificar_pr.py:73/250`. Marcador em código inline conta como aberto, e a própria
   spec dispara o aviso. Tratamento: tirar code spans e blocos de código antes da busca.
3. **Médio**, `verificar_pr.py:70/220/238`. Spec aprovada só com `**R1** <...>`, ou com
   `**R1:**`, ou com `- **R2**`, desliga todas as checagens. Tratamento: avisar "spec aprovada sem
   requisitos R<n>" quando o cabeçalho novo existe e não sobra nenhum R válido.
4. **Baixo**, `verificar_pr.py:291`. Tarefas sob `###` ficam fora do corpo de "Tarefas".
   Tratamento: incluir os subtítulos na seção.
5. **Baixo**, `verificar_pr.py:248-256`. O aviso de marcador dispara em spec no formato 1.6.1,
   contra a letra do R7. Tratamento: exigir o artefato novo.
6. **Baixo**, `verificar_pr.py:235`. `Aprovada (data)` e `aprovada.` escapam do aviso. Tratamento:
   aceitar texto depois de `aprovada`.
7. **Baixo**, `verificar_pr.py:213`. Um R<n> dentro de bloco de código conta como requisito.
   Tratamento: remover os blocos antes da busca.
8. **Médio**, `criar_projeto.py:52/153`. Se o clone da tag falha, o gerador diz "✔ Projeto
   criado" sem avisar. Tratamento: aviso em stderr com o erro do git e a sugestão
   `--versao-ciclo ""`.

Veredito do revisor: vai a merge depois dos achados 1 a 3, e o 8 pode esperar. Todos os 8 serão
tratados.

Conferência das correções (mesmo revisor independente, 2026-10-05):

- Os 8 achados foram resolvidos nos commits f62ee9e e 40887da. Suíte: 55 passed.
  `verificar_pr.py --base main` na branch: nenhum achado, exit 0.
- R3 e R4 passam a atendidos.
- Sem regressão: a spec no formato 1.6.1 continua sem achado novo (R7), e os modelos intocados
  só geram o aviso de evidência que já existia (R8).
- Veredito: pode ir a merge.

Limites conhecidos, para a 1.8.0:

- um requisito escrito só como código inline (`**R1** \`cmd\``) some sem aviso;
- uma linha `critério` em minúscula não é aceita e gera aviso falso.
