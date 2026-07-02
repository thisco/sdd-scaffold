# sdd-scaffold

**Governança de engenharia para projetos construídos com IA — sem lock-in de ferramenta.**

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
real e é ótima — mas ela colide de frente com a integridade arquitetural. Sem trilhos, o resultado
é o *vibe coding*: código que passa no teste da vez, mas ninguém sabe explicar por que existe, como
se encaixa no todo, nem qual decisão ele silenciosamente reverteu.

O sintoma mais caro é o **drift**: a documentação diz uma coisa, o diagrama diz outra, a
infraestrutura faz uma terceira. Cada artefato foi verdadeiro em algum momento e nenhum é verdadeiro
agora. Quando o drift se instala, a documentação vira ficção e a única fonte de verdade passa a ser
ler o código inteiro de novo — exatamente o que a documentação deveria evitar.

Some a isso o **lock-in de ferramenta**. Quando as regras do projeto moram no formato proprietário
de um assistente específico, trocar de ferramenta — ou parear um humano com um agente — significa
reescrever a governança. O conhecimento fica refém do fornecedor.

E há a **memória perdida**. Todo agente começa cada sessão do zero. Sem um lugar deliberado para
destilar o que foi aprendido, cada decisão precisa ser reconquistada, cada gotcha é redescoberto,
e o projeto anda em círculos. Este scaffold ataca os quatro problemas de uma vez.

## O modelo em 5 pilares

**1. Constituição + steering, agnósticos de ferramenta.** Um único `AGENTS.md` na raiz é a fonte de
verdade de governança, com uma tabela de roteamento que carrega o steering de domínio sob demanda
(`docs/steering/`). Adaptadores de ferramenta (`CLAUDE.md`, `ANTIGRAVITY.md`) são stubs de uma linha
que apontam para lá. *Por quê:* a regra vive uma vez, em texto aberto — qualquer humano ou agente lê,
e trocar de ferramenta não custa nada.

**2. SDD com tiers de rigor.** Toda mudança é classificada em Tier 0 (trivial, direto), Tier 1
(pequeno, plano leve) ou Tier 2 (feature/estrutural: spec → plano → checkpoints → ADR). *Por quê:* processo
pesado em tudo mata a velocidade; processo nenhum mata a arquitetura. O rigor acompanha o risco, com
critérios objetivos e a regra "na dúvida, tier mais alto".

**3. Arquitetura Viva com drift check.** Diagrama `.drawio`, IaC (OpenTofu) e `docker-compose`
descrevem o mesmo sistema e são amarrados por um manifesto (`Arquitetura/mapa.yml`). Um script
compara os três e reporta divergências. *Por quê:* documentação que não é verificada apodrece — aqui a
sincronia é uma checagem executável, rodada no CI a cada PR.

**4. Memória destilada.** Uma memória quente de ~1 página (`docs/PROJECT_MEMORY.md`) é lida no início
de cada sessão; aprendizados maduros são promovidos ao steering ou a uma ADR e removidos de lá.
*Por quê:* contexto que não é destilado se perde entre sessões — este é o lugar deliberado onde o projeto
lembra o que aprendeu.

**5. Qualidade e segurança com prove-it.** Nada fecha sem evidência colada no plano (testes, lint);
Tier 2 passa por revisão adversarial *contra a spec* (não contra o diff); specs que tocam entrada
externa respondem a um checklist de threat-model. *Por quê:* "confie em mim, funciona" não é evidência,
e um revisor que parte da spec pega o requisito que foi silenciosamente esquecido.

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

Opções: `--descricao "..."`, `--stack "Python 3.12 + FastAPI"`, `--deps requirements.txt`. Campos não
informados ficam como `<!-- preencher -->` para você completar depois.

## O que você recebe

```
meu-projeto/
├── AGENTS.md                       # constituição: princípios + tabela de roteamento do steering
├── CLAUDE.md · ANTIGRAVITY.md      # stubs agnósticos: apontam para AGENTS.md
├── CHANGELOG.md                    # Keep a Changelog, pronto para a primeira entrada
├── Arquitetura/
│   ├── arquitetura.drawio          # diagrama C4 (esqueleto, para você desenhar)
│   └── mapa.yml                    # manifesto de correspondência drawio × IaC × compose
├── docs/
│   ├── PROJECT_MEMORY.md           # memória quente (~1 página), lida a cada sessão
│   ├── steering/                   # normas de domínio destiladas (7 arquivos):
│   │   ├── sdd-processo.md          #   tiers, planos, checkpoints, git
│   │   ├── arquitetura.md           #   ciclo da Arquitetura Viva, equivalências local→cloud
│   │   ├── seguranca.md             #   segredos, auth/RBAC, threat-model
│   │   ├── qualidade.md             #   testes, lint, prove-it, contratos de saída
│   │   ├── infra-devops.md          #   ambientes, deploy, migrations
│   │   ├── frontend-ux.md           #   padrões de painel/frontend
│   │   └── troubleshooting.md        #   gotchas estáveis
│   ├── specs/MODELO-spec.md        # modelo de especificação (o QUE)
│   ├── plans/MODELO-plano.md       # modelo de plano de implementação (o COMO)
│   ├── adr/MODELO-adr.md           # modelo de Architecture Decision Record
│   └── release-notes/              # histórico de entregas por versão
├── infra/
│   ├── local/docker-compose.yml    # ambiente local (esqueleto)
│   └── cloud/                       # OpenTofu: main.tf, versions.tf, modules/exemplo-servico/
├── scripts/
│   └── verificar_drift_arquitetura.py   # compara mapa.yml × drawio × tofu × compose
└── .github/workflows/qualidade.yml # CI: drift (informativo), gitleaks, pip-audit
```

## Pós-geração

Depois de gerar o projeto, siga este checklist:

- [ ] **Revisar `AGENTS.md`** — confira nome, stack e descrição substituídos; ajuste os princípios ao
      seu contexto.
- [ ] **Preencher os `<!-- preencher -->`** dos arquivos de `docs/steering/` — comandos de teste/lint,
      mecanismo de auth, escopos de commit etc. São os pontos onde o modelo genérico vira o *seu* projeto.
- [ ] **Desenhar o diagrama** em `Arquitetura/arquitetura.drawio` (o esqueleto usa o modelo C4).
- [ ] **Ajustar `Arquitetura/mapa.yml`** — mapeie cada componente lógico para seu nó no diagrama, módulo
      de IaC e serviço no compose.
- [ ] **Rodar o drift check:**

  ```bash
  pip install pyyaml
  python3 scripts/verificar_drift_arquitetura.py
  ```

  No **primeiro run**, com `componentes: []` ainda vazio, o check reporta o módulo de exemplo
  `exemplo-servico` como "não mapeado". **Isso é esperado**, não é defeito — o aviso some assim que você
  mapear seus componentes reais (ou remover o módulo de exemplo). O check é informativo e nunca bloqueia
  o CI.

## Origem

Este scaffold foi extraído de um projeto real em produção: um pipeline multi-cloud de catálogo de
serviços (seis provedores de nuvem), com mais de 1000 testes automatizados e 35+ ADRs registradas. O
modelo de governança nasceu da necessidade concreta de manter a integridade arquitetural com boa parte
do código sendo escrita por agentes de IA — e foi generalizado aqui, sem nenhum acoplamento ao domínio
original.

## Referências

O modelo dialoga com o estado da arte em SDD, steering e arquitetura como documentação:

- [OpenSpec](https://github.com/Fission-AI/OpenSpec) — specs como fonte de verdade para agentes.
- [GitHub Spec Kit](https://github.com/github/spec-kit) — toolkit de Spec-Driven Development.
- [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) — método ágil orientado a agentes.
- [Padrão AGENTS.md](https://agents.md/) — convenção aberta para arquivo de instruções de agentes.
- [Kiro — Steering (AWS)](https://kiro.dev/docs/steering/) — documentos de steering persistentes.
- [Anthropic Engineering — Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices) — práticas de engenharia com agentes (fonte de mercado).
- [Anthropic Engineering — Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — engenharia de contexto para agentes (fonte de mercado).
- [Comparativo de frameworks SDD — ranthebuilder.cloud](https://www.ranthebuilder.cloud/post/spec-driven-development-frameworks-compared) — panorama comparativo.
- [Architecture Decision Records — Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — o formato ADR original.
- [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) — formato de changelog adotado.
- [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/) — convenção de mensagens de commit.
- [C4 model](https://c4model.com/) — modelo de diagramação de arquitetura de software.

## Licença

Distribuído sob a licença [MIT](LICENSE). Copyright (c) 2026 Thiago Oliveira.

## Contribuindo

Contribuições são muito bem-vindas. Abra uma *issue* para propor melhorias ou discutir o modelo, e
mande *pull requests* — de correção de typo a novos pilares de governança. Se for uma mudança
estrutural, descreva a motivação e o impacto no processo.
