# AGENTS.md, constituição do repositório {{NOME_PROJETO}}

Regras para desenvolvedores e assistentes de IA pareando neste repositório. Este arquivo é a
**única fonte de verdade de governança** e é lido em todo turno, então mantenha-o curto. O
detalhe operacional mora em `docs/steering/` e nas skills em `skills/`, carregados sob demanda.

Paradigma: **Spec-Driven Development (SDD)**.

## Este projeto

- **Stack:** {{STACK}}
- **Estado:** {{DESCRICAO}}

<!-- constituicao:inicio padrao-v1.0 -->
## Princípios inegociáveis

Estes princípios valem para todos os projetos que adotam este scaffold. Eles são a camada 0 da
governança: não variam de projeto para projeto, e por isso vivem inline no `AGENTS.md`, onde são
carregados em todo turno, com a cópia canônica versionada em `docs/constituicao/`.

1. **SDD com rigor proporcional.** Toda mudança é classificada em Tier 0 (trivial, direto),
   Tier 1 (pequeno, plano leve) ou Tier 2 (feature ou estrutural: spec, plano, checkpoints e ADR).
   Critérios objetivos em `docs/steering/sdd-processo.md`. Na dúvida, o tier mais alto.
2. **Agnosticismo de ferramenta de IA.** Nenhum artefato, log, comentário ou commit menciona
   marca de assistente de IA. Arquivos específicos de ferramenta são stubs que apontam para a
   constituição. Nenhum rastreamento de tarefa fora do próprio arquivo de plano em `docs/plans/`.
3. **Português do Brasil** em código, testes, commits, comentários e documentação, com exceção de
   jargões técnicos globais consolidados.
4. **Proibido improvisar.** Se a spec ou o plano se provarem inviáveis durante a implementação, o
   trabalho é abortado e volta à especificação, normalmente gerando uma ADR. Contornar um
   obstáculo reverte, em silêncio, uma decisão de arquitetura que ninguém decidiu reverter.
5. **Segurança primeiro.** Segredo nunca é commitado; ele vive em `.env` carregado em runtime.
   Lógica proprietária é acoplada por interface e injeção de dependências, de modo que o núcleo
   compile sem os módulos privados. Detalhes em `docs/steering/seguranca.md`.
6. **Arquitetura Viva.** Ambiente local, infraestrutura como código e diagrama descrevem o mesmo
   sistema e são sincronizados na mesma branch. Procedimento na skill `arquitetura-viva`.
7. **Memória contínua.** `docs/PROJECT_MEMORY.md` é lido no início de toda sessão, e o aprendizado
   novo é registrado ao encerrar sessão complexa.
8. **A governança não se autoedita.** O agente escreve código, testes, specs e planos. Ele não
   altera esta constituição, as ADRs já registradas nem o mapa de arquitetura sem que uma pessoa
   peça. Isso é verificado por mecanismo, e não apenas por esta frase.

## Fluxo mínimo de qualquer entrega

1. Classificar o tier e criar branch `feat|fix/AAAA-MM-DD-nome` a partir da `main`.
2. Tier 1 ou superior: plano em `docs/plans/` com a seção **Impacto Arquitetural**.
   Tier 2: PRD e spec aprovados antes.
3. Implementar com TDD, colando evidência de teste e lint no plano antes de concluir.
4. Atualizar `CHANGELOG.md` no formato Keep a Changelog antes do merge.
5. PR com a suíte passando. Tier 2 passa por revisão adversarial contra a spec.
<!-- constituicao:fim -->

> O bloco acima é a **camada 0**: vale para todos os projetos da organização e não se edita por
> projeto. A cópia canônica está em `docs/constituicao/padrao-v1.0.md` e
> `scripts/verificar_constituicao.py` confere que as duas batem. Para adotar uma versão nova,
> substitua o arquivo canônico e reinline o bloco.

## Tabela de roteamento

Governança tem quatro camadas, separadas por **quando o conteúdo entra no contexto**:
constituição da organização (o bloco acima, sempre), premissa deste projeto (esta seção, sempre),
procedimento (skills em `skills/`, por gatilho) e parâmetro (`docs/steering/`, quando a skill
mandar ler).

| Se a tarefa envolve… | Procedimento | Parâmetros deste projeto |
|---|---|---|
| Criar/alterar qualquer código | — | `docs/steering/sdd-processo.md` |
| Mudança estrutural, infra, novo componente | skill `arquitetura-viva` | `docs/steering/arquitetura.md` |
| Auth, upload, entrada externa, IaC, segredos | skill `threat-model` | `docs/steering/seguranca.md` |
| Subir/atualizar ambiente, deploy, migrations | skill `migrations-reversiveis` | `docs/steering/infra-devops.md` |
| Preparar PR (testes, lint, contrato de saída) | — | `docs/steering/qualidade.md` |
| Painel/frontend | skill `estados-de-interface` | `docs/steering/frontend-ux.md` |
| Debugging | — | `docs/steering/troubleshooting.md` |

As skills ficam em `skills/` e são montadas em `.claude/skills`, `.codex/skills` e
`.kiro/skills`. Os três apontam para o mesmo corpo, então editar num lugar vale para todos.

## Mapa do repositório

```
src/           código-fonte da aplicação (módulos/pacotes do domínio)
infra/         local/ (docker-compose) · cloud/ (IaC multi-ambiente)
docs/          constituicao/ · prd/ · specs/ · plans/ · adr/ · release-notes/ · steering/ · PROJECT_MEMORY.md
Arquitetura/   diagrama .drawio + mapa.yml (manifesto de correspondência)
skills/        procedimento compartilhável, montado em .claude/ .codex/ .kiro/
scripts/       utilitários (drift de arquitetura, proteção e verificação da governança)
tests/         suíte automatizada (unidade, integração, e2e)
```
