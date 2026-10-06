# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) ·
Versionamento: [SemVer](https://semver.org/lang/pt-BR/).

## [1.7.1] - 2026-10-06

Correções de governança. A revisão de segurança automática da 1.7.0 apontou os itens abaixo.

### Corrigido

- **Migration renomeada e editada passava pela trava.** O `verificar_pr.py` lista os nomes com
  `git diff --name-only --no-renames`, e a migration antiga deixa de sumir da lista.
- **O hook falhava inerte quando a sessão fazia `cd`.** O comando em `.claude/settings.json`
  passa a usar `python3 "$CLAUDE_PROJECT_DIR/scripts/proteger_governanca.py"`.
- **Protegidos a mais no hook:** `scripts/verificar_*.py`, `.claude/settings.local.json` e
  `.github/**` (workflows, CODEOWNERS, dependabot). `docs/steering` continua livre: o fluxo
  pós-geração manda o agente preenchê-lo.
- **`Write` sem regra.** Toda regra `ask` ou `deny` de `Edit(...)` ganha o `Write(...)` equivalente.
- **Caixa do nome.** O hook compara sem distinguir maiúsculas (`agents.md` é o `AGENTS.md` em
  macOS e Windows).

### Modificado

- O README declara o limite da trava de PR (o job roda o script do próprio PR, então ela vale
  contra descuido e não contra má-fé) e as mitigações: CODEOWNERS e proteção de branch em
  `scripts/` e `.github/`, ou rodar o script da base.

## [1.7.0] - 2026-10-05

Spec verificável e aprovada. A spec passa a ter requisitos com id, e o verificador de PR
confere o rastro entre requisito, tarefa, teste e veredito, sempre com aviso e nunca com
bloqueio.

### Adicionado

- **Requisitos com id e critério na spec.** O `MODELO-spec.md` traz a seção `Requisitos`, com
  linhas `**R<n>**` e um critério de aceite em Dado/Quando/Então (ou EARS) logo abaixo.
  Ela substitui "Objetivos" e "Critérios de aceite". Requisito sem critério gera aviso no PR.
- **Registro da aprovação.** O cabeçalho da spec ganha `Aprovado por` e `Aprovado em`. Spec com
  Status `aprovada` e sem aprovador gera aviso no PR.
- **Marcador de dúvida `[ESCLARECER: …]` e a seção `Esclarecimentos`.** Spec aprovada, ou citada
  por plano do PR, com marcador aberto gera aviso com a contagem.
- **Rastreio no plano e no teste.** A tarefa do plano termina com `(R<n>)`, e o teste cita o
  requisito com `# cobre: R<n>`. O verificador avisa quando um requisito não tem tarefa, quando
  uma tarefa cita requisito que não existe e quando nenhum teste do PR o cita. Em plano Tier 2
  com a tabela de veredito preenchida, avisa se falta algum requisito. A mensagem diz "citado em
  teste", porque citação não é cobertura.
- **Tabela `| R | veredito | evidência |`** na revisão adversarial do `MODELO-plano.md`.
- **Ponto de montagem `.agents/skills`**, lido pelo Codex e pelo Antigravity, ao lado de
  `.claude/skills`, `.codex/skills` e `.kiro/skills`.
- **Opção `--versao-ciclo`** no gerador, para escolher a tag da skill do ciclo.
- **Seção "Instalar pelo próprio agente" no README**, com o prompt que faz o agente clonar o
  scaffold na tag `v1.7.0` e configurar o projeto.

### Modificado

- O gerador instala a skill do ciclo pela tag `v3.0.0`, e não mais pela `main`.
- O `CLAUDE.md` do template importa a constituição com `@AGENTS.md`.
- `qualidade.md` documenta a convenção `# cobre: R<n>` e o limite dela.
- Os avisos novos só disparam quando a spec tem `R<n>` ou `Aprovado por`: a spec no formato
  1.6.1 segue sem nenhum achado novo.

### Corrigido

- **O verificador de PR saía com 0 quando a base do diff não existia**, e a trava passava em
  silêncio. Agora imprime `ERRO: base <base> não encontrada` e sai com 2.
- `sdd-processo.md` chamava a implementação de "Fase 3". Ela é a Fase 6, como na skill do ciclo.

## [1.6.1] - 2026-09-29

Correções de achados da primeira auditoria. Os três defeitos tinham a mesma causa: os testes
exercitavam o modelo mental do autor, e não o artefato real.

### Corrigido

- **O hook de governança estava inerte.** A ferramenta envia `file_path` absoluto, e o hook
  comparava contra padrões relativos, então nada casava. Os testes alimentavam caminho relativo,
  que é o que o autor supôs, e por isso certificavam um comportamento que o harness nunca
  produz. O caminho passa a ser resolvido contra `CLAUDE_PROJECT_DIR`, o que também fecha a
  travessia por `..`.
- **O verificador de PR voltou a aprovar o `MODELO-spec.md` em branco.** A própria v1.6.0
  introduziu a regressão: mover as cinco perguntas de comentário HTML para prosa numerada fez a
  verificação enxergar conteúdo onde há apenas perguntas. O teste de regressão não pegou porque
  construía à mão a versão anterior do modelo. Pergunta sem resposta e item de checklist vazio
  deixam de contar, e os testes passam a ler os modelos reais do template.
- **O projeto gerado não conseguia passar no próprio CI.** Faltava o `requirements.txt` que dois
  jobs instalam, e o `pyproject.toml` nascia com `{{NOME_PROJETO}}` porque `.toml` estava fora
  de `EXTENSOES_TEXTO`. A mesma omissão existia na allowlist do teste de placeholder residual,
  então nada acusava.

### Adicionado

- Permissões declarativas em `.claude/settings.json`, com `ask` e `deny` por caminho. Elas
  alcançam o `Bash`, que o hook não alcança: sem isso, `sed -i AGENTS.md` contornava a proteção.
- O hook passa a proteger também o diagrama, os arquivos de configuração das três ferramentas e
  ele próprio.

## [1.6.0] - 2026-09-29

Instalação da skill do ciclo na geração, e revisão de toda a documentação.

### Corrigido

- **O verificador de PR aprovava documento intocado.** Ele procurava as palavras
  "threat-model" e "rollback" no texto, e os modelos em `docs/` citam essas palavras dentro de
  comentários de orientação. Uma spec copiada do modelo e nunca preenchida passava no check.
  Agora a verificação exige **seção com conteúdo**: encontra o título, remove comentários e
  marcadores vazios, e confere que sobrou algo.
- Ponteiros mortos nos modelos. `MODELO-spec.md` mandava ler o checklist de threat-model em
  `docs/steering/seguranca.md`, de onde ele saiu na v1.5.0; `MODELO-plano.md` apontava para o
  ciclo da Arquitetura Viva e para as regras de rollback nos mesmos lugares antigos.

### Adicionado

- **O gerador instala a `sdd-lifecycle`** em `skills/sdd-lifecycle/`, com a origem e a revisão
  registradas em `PROCEDENCIA.md`. Opções `--origem-ciclo` e `--sem-skill-do-ciclo`.
  Origem inacessível não aborta a geração: o projeto nasce sem a skill e com um arquivo
  explicando como instalar depois.
- `MODELO-spec.md` ganha seção própria de threat-model com as cinco perguntas, em vez de a
  exigência viver num comentário dentro de "Riscos". Elemento obrigatório vira slot na estrutura,
  e não lembrete em prosa.
- `MODELO-spec.md` e `MODELO-plano.md` referenciam o PRD.

### Modificado

- ADR-0001 ganha apêndice registrando que a arquitetura virou quatro camadas e que dois destinos
  da classificação original foram revertidos. O texto original fica como estava: ADR é registro
  histórico, não documento vivo.
- A análise em `docs/plans/` ganha nota de estado dizendo o que foi implementado e o que não
  sobreviveu ao contato com a implementação.

## [1.5.0] - 2026-09-29

Três skills novas, e a redução do steering ao que é de projeto.

### Adicionado

- **`skills/threat-model`**: as cinco perguntas obrigatórias, o que conta como mitigação de
  verdade, menor privilégio em IaC e tratamento de segredo, incluindo a ordem correta quando um
  segredo vaza (rotacionar antes de limpar o histórico, porque remover o commit não invalida a
  credencial).
- **`skills/migrations-reversiveis`**: reversibilidade, rollback declarado antes da execução, e
  o padrão expandir e contrair para mudança destrutiva.
- **`skills/estados-de-interface`**: os quatro estados por tela e por consulta, por que o estado
  vazio não é estado de erro, e protótipo aprovado antes do código.

### Modificado

- `docs/steering/seguranca.md` de 36 para 28 linhas, `frontend-ux.md` de 30 para 26 e
  `infra-devops.md` mantém 42 com o procedimento substituído por parâmetros. O steering completo
  saiu de 335 para 280 linhas, e o que permanece é o que muda de projeto para projeto.
- Tabela de roteamento do `AGENTS.md` com as quatro skills.

### Nota sobre a redução projetada

A análise estimava cerca de 121 linhas de steering ao final. O número real ficou em 280 porque
`sdd-processo.md` não foi convertido: ele duplica a `sdd-lifecycle`, que vive em repositório
separado e não acompanha o projeto gerado. Enquanto essa skill não for empacotada aqui ou
instalada por quem gera o projeto, as 85 linhas precisam continuar no steering.

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
