# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) ·
Versionamento: [SemVer](https://semver.org/lang/pt-BR/).

## [1.4.0] - 2026-09-29

Mecanismos de PR: o processo passa a ser verificado, e não apenas escrito.

### Adicionado

- **`scripts/verificar_pr.py`** e o job `normas-do-pr`. Confere contra o diff quatro normas que
  a constituição pedia sem ninguém verificar: threat-model na spec quando a mudança toca
  superfície sensível, estratégia de rollback no plano quando mexe em schema, evidência de teste
  colada no plano, e migration já aplicada não sendo editada.
- A análise fica numa função pura sobre o retrato do PR, então os casos de borda são testáveis
  sem repositório de mentira.

### Severidades, e por quê

Alterar migration já aplicada **bloqueia**: corrompe o histórico de schema de quem aplicou a
anterior, é inequívoco e difícil de desfazer. Threat-model, rollback e evidência **avisam**:
envolvem julgamento sobre o que é suficiente, e portão que reprova por julgamento ensina o time
a contorná-lo.

### Corrigido antes de publicar

A primeira versão da detecção de superfície sensível casava substring, então `iam` disparava no
meio de `LEIAME.md` e um PR só de documentação recebia aviso de threat-model. Aviso que dispara
em arquivo irrelevante ensina a ignorar todos os avisos. Trocado por lista explícita de palavras
inteiras, com teste de regressão cobrindo `LEIAME.md`, `miami.md` e `authorship_display.py`.

## [1.3.0] - 2026-09-29

Camada 0: constituição organizacional.

### Adicionado

- **`docs/constituicao/padrao-v1.0.md`** e o bloco correspondente inline no `AGENTS.md`, entre
  marcadores. Os princípios que valem para todos os projetos deixam de ser texto solto dentro de
  cada `AGENTS.md` e passam a ter versão declarada.
- **`scripts/verificar_constituicao.py`** e o job `governanca` do CI. Editar a constituição
  dentro de um projeto reprova, porque ela é compartilhada. Estar atrás da versão publicada pela
  organização apenas avisa, porque um projeto pode ter motivo para esperar.
- O hook e o `permissions.yaml` passam a cobrir `docs/constituicao/`.

### Por que inline em vez de include

Premissa precisa valer em todo turno, então não pode virar arquivo lido sob demanda. Include
remoto foi descartado porque só uma das três ferramentas implementa, e depender disso
reintroduziria o lock-in que o scaffold existe para evitar. A escolha foi vendoring com
verificação: o texto vive inline e o CI confere que não divergiu.

### Modificado

- `AGENTS.md` reorganizado em quatro camadas. A seção do projeto ficou com stack e estado; o
  resto é constituição compartilhada ou roteamento.

## [1.2.0] - 2026-09-29

Onda 2: primeira skill compartilhável, pontos de montagem por ferramenta e três mecanismos
que passam a impedir em vez de só orientar.

### Adicionado

- **`skills/arquitetura-viva/SKILL.md`**, primeira conversão de steering em procedimento
  compartilhável. Carrega o ciclo da Arquitetura Viva, o manifesto e a verificação de drift.
  Os parâmetros que variam por projeto ficaram em `docs/steering/arquitetura.md`, que encolheu
  de 83 para 42 linhas e manteve os três pontos de preenchimento.
- **Pontos de montagem de skills.** `.claude/skills`, `.codex/skills` e `.kiro/skills` são
  links para `skills/`. O gerador passa a preservar links simbólicos; antes ele resolvia cada
  um e o projeto nascia com quatro cópias da mesma skill, prontas para divergir.
- **`scripts/proteger_governanca.py`** e `.claude/settings.json`. Hook que roda antes da
  escrita e pede aprovação para alterar `AGENTS.md`, os ponteiros de ferramenta, `docs/adr/`,
  `Arquitetura/mapa.yml` e os workflows de CI. É a mesma regra que o Kiro aplica por
  `permissions.yaml` e o Codex por sandbox, agora nas três ferramentas.
- **`.kiro/permissions.yaml`** com precedência deny sobre ask sobre allow.
- **`.codex/requirements.toml`** fixando `git_attribution` desligado, para que uma política de
  organização não passe a exigir rodapé de atribuição contra o princípio 2 da constituição.
- **`docs/prd/MODELO-prd.md`**. O fluxo saltava da ideia para a spec, e sem o PRD a spec acaba
  inventando requisito para preencher lacuna.
- Tabela de roteamento do `AGENTS.md` reescrita com duas colunas, separando procedimento de
  parâmetro.

### Decidido e não feito

`sdd-processo.md` não virou skill. A `sdd-lifecycle` já cobre todos os tópicos dele, e em
vários casos com mais profundidade: isolamento de branch aparece 11 vezes na skill contra 3 no
steering, revisão adversarial 6 contra 2. Converter criaria uma segunda skill competindo com a
primeira no mesmo terreno.

As outras normas seguem como steering. A conversão acontece quando uma delas provar valor em
mais de um projeto.

## [1.1.0] - 2026-09-29

Onda 1 do plano de melhoria derivado da pesquisa dos internos de cinco harnesses de coding agent
(Claude Code 2.1.267, Codex CLI 0.157.1, Kiro, Antigravity, DeepSeek dsh).

### Corrigido

- **`criar_projeto.py` falhava ao gerar qualquer projeto em máquina com `.DS_Store` no template.**
  `Path(".DS_Store").suffix` é `""`, e `""` pertence a `EXTENSOES_TEXTO` de propósito (para
  arquivos de texto sem extensão), então o gerador tentava decodificar 6.148 bytes binários como
  UTF-8 e estourava com `UnicodeDecodeError`. A cópia agora ignora `.DS_Store`, `__pycache__`,
  `*.pyc` e `.pytest_cache`, e o passo de substituição ignora binário que escape do filtro.
  Cinco `.DS_Store` foram removidos do template e entraram no `.gitignore`.
- **`ANTIGRAVITY.md` removido do template**, não é lido por ferramenta alguma. O Antigravity lê
  `AGENTS.md` e `GEMINI.md`. Em seu lugar entra `template/GEMINI.md`, que funciona de verdade e
  também cobre o Gemini CLI.
- **`template/tests/` passa a existir.** O mapa do repositório em `AGENTS.md` prometia `tests/` e o
  template não entregava, deixando o agente livre para criar a suíte onde quisesse.

### Adicionado

- **CI no próprio repositório** (`.github/workflows/ci.yml`), não havia nenhum, e é por isso que
  a suíte quebrada não foi notada: matriz Python 3.11/3.12/3.13 mais um job que gera um projeto de
  ponta a ponta, roda o drift check do projeto gerado e falha se sobrar placeholder ou artefato de SO.
- **Quatro testes de regressão**: artefatos de SO no projeto gerado, integridade dos ponteiros de
  ferramenta (incluindo a ausência de `ANTIGRAVITY.md`), existência de `tests/` e tamanho do
  `AGENTS.md` sob o limite do Codex.
- **Três jobs no CI do template**: `testes` (instalação congelada + suíte completa), `lint-e-tipos`
  (ruff, formato e mypy) e `governanca`, que falha se o `AGENTS.md` passar de 30.000 bytes, o
  Codex trunca em 32.768 **silenciosamente**, ou se um ponteiro de ferramenta estiver quebrado
  ou inerte.
- **`template/tests/README.md`** com as regras das três camadas da suíte, incluindo seed
  determinístico e fixtures versionadas: dado aleatório sem seed não produz regressão reproduzível.
- **`docs/adr/0001-separacao-entre-premissa-procedimento-e-parametro.md`**, decide a arquitetura
  de governança em três camadas (premissa sempre carregada, procedimento por gatilho, parâmetro
  lido sob instrução) e registra o critério: premissa não pode morar em skill. Implementação na
  Onda 2.
- **Seção "As três camadas de governança"** no README, com a tabela de qual arquivo cada
  ferramenta lê de fato.

### Verificado empiricamente

Antes de implementar a Onda 2, testamos a premissa que a motivava. Um agente recebeu uma tarefa
de Tier 2 sobre um projeto gerado por este scaffold, sem nenhuma skill instalada e sob pressão
de prazo. Ele seguiu a constituição: classificou o tier, escreveu spec antes do código, abriu
branch na convenção, gerou ADR, escreveu testes e fez a revisão adversarial, na qual encontrou
uma corrida de concorrência que ninguém pediu para procurar.

A premissa de que o agente ignoraria o steering sem mecanismo não se confirmou. A justificativa
da Onda 2 foi rebaixada no ADR-0001: ela passa a valer por reuso entre projetos, não por
correção de um problema observado.

O mesmo teste revelou que o projeto gerado não declarava onde o código-fonte mora, então
`pytest tests/` falhava e só passava com `PYTHONPATH=.`. O CI do template teria quebrado.
Corrigido com `template/pyproject.toml`, que também traz configuração de ruff e mypy.

### Notas para quem mantém projetos já gerados

Nada aqui exige migração. Se o seu projeto tem `ANTIGRAVITY.md`, ele nunca foi lido, pode apagar
e criar `GEMINI.md` com o mesmo ponteiro de quatro linhas. A mudança que **vai** exigir migração é
a Onda 2 (ADR-0001), que sai como major.
