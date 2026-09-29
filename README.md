# sdd-scaffold

**Governança de engenharia para projetos construídos com IA, sem lock-in de ferramenta.**

Um scaffold que instala, num projeto novo, a espinha dorsal de processo que mantém a arquitetura
íntegra enquanto agentes de IA escrevem código na velocidade deles: constituição agnóstica de
ferramenta, Spec-Driven Development com rigor proporcional, Arquitetura Viva com verificação de
drift, memória destilada e portões de qualidade e segurança.

[![Licença: MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-black.svg)](LICENSE)
[![PRs bem-vindos](https://img.shields.io/badge/PRs-bem--vindos-brightgreen.svg)](#contribuindo)
[![Feito com SDD](https://img.shields.io/badge/feito%20com-SDD-6f42c1.svg)](#o-modelo-em-5-pilares)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776ab.svg)](#quick-start)

---

## O problema

Agentes de IA escrevem código mais rápido do que qualquer time consegue revisar. Essa velocidade é
real e é ótima, mas ela colide de frente com a integridade arquitetural. Sem trilhos, o resultado
é o *vibe coding*: código que passa no teste da vez, mas ninguém sabe explicar por que existe, como
se encaixa no todo, nem qual decisão ele silenciosamente reverteu.

O sintoma mais caro é o **drift**: a documentação diz uma coisa, o diagrama diz outra, a
infraestrutura faz uma terceira. Cada artefato foi verdadeiro em algum momento e nenhum é verdadeiro
agora. Quando o drift se instala, a documentação vira ficção e a única fonte de verdade passa a ser
ler o código inteiro de novo, exatamente o que a documentação deveria evitar.

Some a isso o **lock-in de ferramenta**. Quando as regras do projeto moram no formato proprietário
de um assistente específico, trocar de ferramenta, ou parear um humano com um agente, significa
reescrever a governança. O conhecimento fica refém do fornecedor.

E há a **memória perdida**. Todo agente começa cada sessão do zero. Sem um lugar deliberado para
destilar o que foi aprendido, cada decisão precisa ser reconquistada, cada gotcha é redescoberto,
e o projeto anda em círculos. Este scaffold ataca os quatro problemas de uma vez.

## O modelo em 5 pilares

**1. Constituição + steering, agnósticos de ferramenta.** Um único `AGENTS.md` na raiz é a fonte de
verdade de governança, com uma tabela de roteamento que carrega o steering de domínio sob demanda
(`docs/steering/`). Codex, Kiro e Antigravity leem esse arquivo nativamente; `CLAUDE.md` e
`GEMINI.md` são stubs de quatro linhas que apontam para ele. *Por quê:* a regra vive uma vez, em
texto aberto, qualquer humano ou agente lê, e trocar de ferramenta não custa nada.

**2. SDD com tiers de rigor.** Toda mudança é classificada em Tier 0 (trivial, direto), Tier 1
(pequeno, plano leve) ou Tier 2 (feature/estrutural: spec → plano → checkpoints → ADR). *Por quê:* processo
pesado em tudo mata a velocidade; processo nenhum mata a arquitetura. O rigor acompanha o risco, com
critérios objetivos e a regra "na dúvida, tier mais alto".

**3. Arquitetura Viva com drift check.** Diagrama `.drawio`, IaC (OpenTofu) e `docker-compose`
descrevem o mesmo sistema e são amarrados por um manifesto (`Arquitetura/mapa.yml`). Um script
compara os três e reporta divergências. *Por quê:* documentação que não é verificada apodrece, aqui a
sincronia é uma checagem executável, rodada no CI a cada PR.

**4. Memória destilada.** Uma memória quente de ~1 página (`docs/PROJECT_MEMORY.md`) é lida no início
de cada sessão; aprendizados maduros são promovidos ao steering ou a uma ADR e removidos de lá.
*Por quê:* contexto que não é destilado se perde entre sessões, este é o lugar deliberado onde o projeto
lembra o que aprendeu.

**5. Qualidade e segurança com prove-it.** Nada fecha sem evidência colada no plano (testes, lint);
Tier 2 passa por revisão adversarial *contra a spec* (não contra o diff); specs que tocam entrada
externa respondem a um checklist de threat-model. *Por quê:* "confie em mim, funciona" não é evidência,
e um revisor que parte da spec pega o requisito que foi silenciosamente esquecido.

### O que impede e o que orienta

Os cinco pilares acima são texto: eles entram no contexto do agente e o orientam. Texto depende de
o agente seguir, e ele costuma seguir, mas não é garantia.

O scaffold também instala três controles que são código rodando fora do modelo, um por ferramenta,
com a mesma regra: o agente escreve código, testes, specs e planos, e não reescreve a constituição,
as ADRs nem o mapa de arquitetura por conta própria.

| Ferramenta | Controle | Arquivo |
|---|---|---|
| Claude Code | hook antes da escrita | `scripts/proteger_governanca.py` e `.claude/settings.json` |
| Kiro | regra declarativa, `deny` sobre `ask` sobre `allow` | `.kiro/permissions.yaml` |
| Codex | fixa `git_attribution` desligado, protegendo o princípio de não citar marca de IA | `.codex/requirements.toml` |
| CI | verifica as normas contra o diff do PR | `scripts/verificar_pr.py` |

O verificador de PR confere o que o processo pedia e ninguém checava: spec com threat-model
quando a mudança toca superfície sensível, plano com estratégia de rollback quando mexe em
schema, evidência de teste colada no plano, e migration já aplicada não sendo editada.

Só o último **bloqueia**. Editar uma migration que já rodou corrompe o histórico de schema de
quem aplicou a anterior, é inequívoco e difícil de desfazer. Os outros três **avisam**, porque
envolvem julgamento sobre o que é suficiente, e um portão que reprova por julgamento ensina o
time a contorná-lo.

Saber em qual das duas camadas cada regra está é o que separa governança de intenção.

## As quatro camadas de governança

Governança aqui é classificada por **quando o conteúdo entra no contexto do agente**, não por
assunto. É o que permite compartilhar procedimento entre projetos sem vazar detalhe de um projeto
para outro.

| Camada | Onde mora | Quando entra | Conteúdo |
|---|---|---|---|
| **0 · Constituição** | bloco inline no `AGENTS.md`, canônico em `docs/constituicao/` | **Sempre** | Princípios que valem para todos os projetos da organização |
| **1 · Premissa** | `AGENTS.md` + ponteiros `CLAUDE.md`, `GEMINI.md` | **Sempre** | Stack, idioma, princípios inegociáveis, mapa do repo, tabela de roteamento |
| **2 · Procedimento** | `SKILL.md` compartilhável | **Sob demanda**, por gatilho | Como classificar tier, conduzir TDD, preparar PR, depurar |
| **3 · Parâmetro** | `docs/steering/*.md` curtos | **Quando a skill instrui a ler** | Comandos reais, variáveis, convenções, contratos de saída |

O critério decisivo: **premissa não pode morar em skill**, porque skill é revelada
condicionalmente e premissa precisa valer em todo turno. Por isso a camada 1 é sempre carregada e
precisa ficar pequena, o Codex trunca documentos de projeto em 32.768 bytes, **sem avisar**.

Uma skill nunca contém conteúdo de projeto: ela termina mandando ler o steering local e traz
defaults para funcionar sem ele. Procedimento específico de um projeto vira **skill local**, não
promovida ao repositório compartilhado; se provar valor em dois projetos, sobe por PR.

Decisão completa, alternativas descartadas e riscos em
[`docs/adr/0001-separacao-entre-premissa-procedimento-e-parametro.md`](docs/adr/0001-separacao-entre-premissa-procedimento-e-parametro.md),
que inclui o teste empírico feito antes de implementar: um agente cumpriu a constituição sem
nenhuma skill instalada, o que rebaixou a justificativa da conversão.

### A camada 0, e por que ela é inline

Princípios que valem para todos os projetos não podem virar um arquivo lido sob demanda, porque
premissa precisa valer em todo turno. Também não podem depender de include remoto: só uma das
ferramentas implementa isso, e adotar esse caminho reintroduziria o lock-in que o scaffold
existe para evitar.

A solução é vendoring com verificação. A constituição fica **inline no `AGENTS.md`, entre
marcadores**, e a cópia canônica em `docs/constituicao/` existe para que o CI confira que as
duas batem:

```bash
python3 scripts/verificar_constituicao.py --raiz .
# Constituição padrao-v1.0: bloco inline confere com o arquivo canônico.
```

O verificador detecta dois problemas com severidades diferentes. Editar a constituição dentro de
um projeto **reprova** (exit 1), porque ela é compartilhada. Estar numa versão anterior à que a
organização publicou apenas **avisa** (exit 0), porque um projeto pode ter motivo legítimo para
esperar:

```bash
python3 scripts/verificar_constituicao.py --raiz . --origem ~/constituicao-publicada
# AVISO: a organização publicou 'padrao-v2.0' e este projeto usa 'padrao-v1.0'.
```

Para adotar uma versão nova, substitua o arquivo canônico e reinline o bloco. Uma organização
que queira sua própria constituição troca `docs/constituicao/padrao-v1.0.md` pelo seu texto e
mantém o mecanismo.

Análise completa em
[`docs/plans/2026-09-29-analise-skills-mecanismos-e-constituicao.md`](docs/plans/2026-09-29-analise-skills-mecanismos-e-constituicao.md).

### Um corpo de skill, três pontos de montagem

As skills ficam em `skills/`. Cada ferramenta lê de um caminho diferente, então
`.claude/skills`, `.codex/skills` e `.kiro/skills` são links para esse mesmo diretório. Editar
a skill num lugar vale para os três, e não existe cópia para divergir.

Quatro skills acompanham o scaffold, e cada uma tem um mecanismo que verifica o resultado:

| Skill | Procedimento | Verificada por |
|---|---|---|
| `arquitetura-viva` | ciclo, manifesto e drift entre diagrama, IaC e ambiente local | `verificar_drift_arquitetura.py` |
| `threat-model` | as cinco perguntas, menor privilégio, tratamento de segredo | `verificar_pr.py` e gitleaks |
| `migrations-reversiveis` | reversibilidade, rollback, expandir e contrair | `verificar_pr.py` |
| `estados-de-interface` | os quatro estados de tela, protótipo antes do código | revisão de PR |

Cada skill termina apontando o arquivo de steering que guarda os parâmetros daquele domínio, e
traz defaults para continuar funcionando quando ele não existe.

`sdd-processo.md` **não** virou skill: a [`sdd-lifecycle`](https://github.com/thisco/sdd-lifecycle)
já conduz o ciclo, e converter criaria duas skills competindo no mesmo terreno. `infra-devops` e
`troubleshooting` seguem como steering, porque o que resta neles é do projeto.

### Por que os ponteiros são de quatro linhas

`AGENTS.md` é a fonte única. `CLAUDE.md` e `GEMINI.md` só apontam para ele, porque duas cópias da
mesma regra divergem e a divergência é silenciosa.

Quais nomes cada ferramenta lê de fato, verificado em 2026-09-29:

| Arquivo | Lido por |
|---|---|
| `AGENTS.md` | Codex CLI, Kiro, Antigravity, nativamente |
| `CLAUDE.md` | Claude Code |
| `GEMINI.md` | Antigravity, Gemini CLI |

> ⚠️ **`ANTIGRAVITY.md` não existe como mecanismo** e foi removido do template. O Antigravity lê
> apenas `AGENTS.md` e `GEMINI.md`, confirmado na skill embutida do próprio produto, na
> documentação oficial e por observação de sessão real, onde um `ANTIGRAVITY.md` presente no
> projeto nunca foi aberto. Um arquivo que parece hook e não é custa depuração a alguém.

## Quick start

Requer **Python 3.11+**. O gerador é **stdlib pura, zero dependências**; a única biblioteca de
terceiros do scaffold é **PyYAML**, usada apenas pelo drift check.

```bash
python3 criar_projeto.py --nome meu-projeto --destino ~/workspace
```

O que acontece:

- copia o `template/` para `~/workspace/meu-projeto`;
- substitui os placeholders (nome do projeto, descrição, stack, arquivo de dependências, data) nos
  arquivos de texto;
- roda `git init -b main` e faz o primeiro commit (`feat: estrutura inicial de meu-projeto via sdd-scaffold`);
- imprime os próximos passos.

- instala a skill do ciclo SDD a partir do repositório dela.

Opções: `--descricao "..."`, `--stack "Python 3.12 + FastAPI"`, `--deps requirements.txt` (default:
`requirements.txt`). Descrição e stack não informadas ficam como `<!-- preencher -->` para completar depois.

### A skill do ciclo é instalada, não copiada

A [`sdd-lifecycle`](https://github.com/thisco/sdd-lifecycle) conduz o ciclo SDD e vive em
repositório próprio. O gerador a instala em `skills/sdd-lifecycle/` e registra a origem e a
revisão em `PROCEDENCIA.md`, de modo que exista uma fonte só e o projeto receba a versão vigente
no dia em que nasce.

```bash
--origem-ciclo <url ou caminho>   # outra origem, inclusive um diretório local
--sem-skill-do-ciclo              # não instalar
```

Se a origem estiver inacessível, **a geração continua**. O projeto nasce sem a skill e com um
arquivo `skills/SKILL-CICLO-AUSENTE.md` explicando como instalar depois. Um gerador que aborta
porque a rede caiu falha justamente quando alguém está começando um projeto.

## O que você recebe

```
meu-projeto/
├── AGENTS.md                       # constituição: princípios + tabela de roteamento
├── CLAUDE.md · GEMINI.md           # ponteiros de 4 linhas: apontam para AGENTS.md
├── CHANGELOG.md                    # Keep a Changelog, pronto para a primeira entrada
├── pyproject.toml                  # pytest (pythonpath, marcadores), ruff, mypy
├── .gitignore
├── Arquitetura/
│   ├── arquitetura.drawio          # diagrama C4 (esqueleto, para você desenhar)
│   └── mapa.yml                    # manifesto de correspondência drawio × IaC × compose
├── docs/
│   ├── constituicao/padrao-v1.0.md # camada 0: cópia canônica, inline no AGENTS.md
│   ├── PROJECT_MEMORY.md           # memória quente (~1 página), lida a cada sessão
│   ├── steering/                   # parâmetros deste projeto (7 arquivos):
│   │   ├── sdd-processo.md          #   tiers, planos, checkpoints, git
│   │   ├── arquitetura.md           #   estrutura, decisões-chave, equivalências local para nuvem
│   │   ├── seguranca.md             #   segredos, auth/RBAC, threat-model
│   │   ├── qualidade.md             #   testes, lint, prove-it, contratos de saída
│   │   ├── infra-devops.md          #   ambientes, deploy, migrations
│   │   ├── frontend-ux.md           #   padrões de painel/frontend
│   │   └── troubleshooting.md        #   gotchas estáveis
│   ├── prd/MODELO-prd.md           # modelo de PRD (o POR QUE)
│   ├── specs/MODELO-spec.md        # modelo de especificação (o QUE)
│   ├── plans/MODELO-plano.md       # modelo de plano de implementação (o COMO)
│   ├── adr/MODELO-adr.md           # modelo de Architecture Decision Record
│   └── release-notes/              # histórico de entregas por versão
├── infra/
│   ├── local/docker-compose.yml    # ambiente local (esqueleto)
│   └── cloud/                       # OpenTofu: main.tf, versions.tf, modules/exemplo-servico/
├── skills/                              # corpo único, montado nas três ferramentas
│   ├── arquitetura-viva/SKILL.md
│   ├── threat-model/SKILL.md
│   ├── migrations-reversiveis/SKILL.md
│   ├── estados-de-interface/SKILL.md
│   └── sdd-lifecycle/                   # instalada na geração, com PROCEDENCIA.md
├── .claude/skills · .codex/skills · .kiro/skills   # pontos de montagem para skills/
├── .claude/settings.json                # hook que protege a governança
├── .codex/requirements.toml             # fixa git_attribution desligado
├── .kiro/permissions.yaml               # deny/ask por caminho sensível
├── scripts/
│   ├── verificar_drift_arquitetura.py   # compara mapa.yml × drawio × tofu × compose
│   ├── verificar_constituicao.py        # bloco inline × cópia canônica
│   ├── verificar_pr.py                  # normas do PR contra o diff
│   └── proteger_governanca.py           # hook PreToolUse
├── tests/
│   ├── unidade/ · integracao/ · e2e/    # camadas da suíte
│   └── README.md                        # regras das três camadas + seed determinístico
└── .github/workflows/qualidade.yml # CI: testes, lint/tipos, governança, drift, gitleaks, pip-audit
```

## Pós-geração

Depois de gerar o projeto, siga este checklist:

- [ ] **Revisar `AGENTS.md`**, confira nome, stack e descrição substituídos; ajuste os princípios ao
      seu contexto. Ele é lido a cada turno, então mantenha-o curto.
- [ ] **Instalar a skill do ciclo.** O scaffold traz `skills/arquitetura-viva`, mas o ciclo SDD em si
      é conduzido pela skill [`sdd-lifecycle`](https://github.com/thisco/sdd-lifecycle), que é um
      repositório à parte. Copie-a para `skills/` se quiser o ciclo completo.
- [ ] **Preencher os `<!-- preencher -->`.** Eles estão em `docs/steering/` (comandos de teste e
      lint, mecanismo de auth, escopos de commit, ordem de rebuild) e também fora dele: `pyproject.toml`,
      `tests/README.md`, `.kiro/permissions.yaml` e `docs/prd/MODELO-prd.md`. São os pontos onde o
      modelo genérico vira o *seu* projeto.
- [ ] **Conferir os caminhos protegidos** em `.kiro/permissions.yaml` e em
      `scripts/proteger_governanca.py`, acrescentando o que for sensível aqui (migrações já
      aplicadas, contratos externos, chaves de configuração).
- [ ] **Escrever o PRD** antes da primeira spec de Tier 2, usando `docs/prd/MODELO-prd.md`.
- [ ] **Desenhar o diagrama** em `Arquitetura/arquitetura.drawio` (o esqueleto usa o modelo C4).
- [ ] **Ajustar `Arquitetura/mapa.yml`**, mapeie cada componente lógico para seu nó no diagrama, módulo
      de IaC e serviço no compose.
- [ ] **Rodar o drift check:**

  ```bash
  pip install pyyaml
  python3 scripts/verificar_drift_arquitetura.py
  ```

  No **primeiro run**, com `componentes: []` ainda vazio, o check reporta o módulo de exemplo
  `exemplo-servico` como "não mapeado". **Isso é esperado**, não é defeito, o aviso some assim que você
  mapear seus componentes reais (ou remover o módulo de exemplo). O check é informativo e nunca bloqueia
  o CI.

## Origem

Este scaffold foi extraído de um projeto real em produção: um pipeline multi-cloud de catálogo de
serviços (seis provedores de nuvem), com mais de 1000 testes automatizados e 35+ ADRs registradas. O
modelo de governança nasceu da necessidade concreta de manter a integridade arquitetural com boa parte
do código sendo escrita por agentes de IA, e foi generalizado aqui, sem nenhum acoplamento ao domínio
original.

## Referências

O modelo dialoga com o estado da arte em SDD, steering e arquitetura como documentação:

- [OpenSpec](https://github.com/Fission-AI/OpenSpec), specs como fonte de verdade para agentes.
- [GitHub Spec Kit](https://github.com/github/spec-kit), toolkit de Spec-Driven Development.
- [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD), método ágil orientado a agentes.
- [Padrão AGENTS.md](https://agents.md/), convenção aberta para arquivo de instruções de agentes.
- [Kiro, Steering (AWS)](https://kiro.dev/docs/steering/), documentos de steering persistentes.
- [Anthropic Engineering, Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices), práticas de engenharia com agentes (fonte de mercado).
- [Anthropic Engineering, Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), engenharia de contexto para agentes (fonte de mercado).
- [Comparativo de frameworks SDD, ranthebuilder.cloud](https://www.ranthebuilder.cloud/post/spec-driven-development-frameworks-compared), panorama comparativo.
- [Architecture Decision Records, Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), o formato ADR original.
- [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), formato de changelog adotado.
- [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/), convenção de mensagens de commit.
- [C4 model](https://c4model.com/), modelo de diagramação de arquitetura de software.

## Licença

Distribuído sob a licença [MIT](LICENSE). Copyright (c) 2026 Thiago Oliveira.

## Contribuindo

Contribuições são muito bem-vindas. Abra uma *issue* para propor melhorias ou discutir o modelo, e
mande *pull requests*, de correção de typo a novos pilares de governança. Se for uma mudança
estrutural, descreva a motivação e o impacto no processo.
