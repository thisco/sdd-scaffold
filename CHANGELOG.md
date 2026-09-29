# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) ·
Versionamento: [SemVer](https://semver.org/lang/pt-BR/).

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
