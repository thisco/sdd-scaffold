# AGENTS.md — Constituição do Repositório

Regras para desenvolvedores e assistentes de IA pareando no repositório **{{NOME_PROJETO}}**. Este arquivo é a
**única fonte de verdade de governança**; o detalhe operacional mora em `docs/steering/` e é
carregado sob demanda pela tabela de roteamento abaixo. Paradigma: **Spec-Driven Development (SDD)**.

## Princípios inegociáveis

1. **SDD com rigor proporcional:** toda mudança é classificada em Tier 0 (trivial — direto),
   Tier 1 (pequeno — plano leve) ou Tier 2 (feature/estrutural — spec → plano → checkpoints → ADR).
   Critérios objetivos em `docs/steering/sdd-processo.md`. Na dúvida, tier mais alto.
2. **Agnosticismo de ferramenta de IA:** nenhum artefato, log, comentário ou commit menciona marca
   de assistente de IA. Arquivos de steering específicos de ferramenta são stubs que apontam para cá.
   Nenhum rastreamento de tarefas fora do próprio arquivo de plano em `docs/plans/`.
3. **Português do Brasil** em todo código, testes, commits, comentários e documentação
   (exceção: jargões técnicos globais consolidados). Stack: {{STACK}}.
4. **Strict fallback:** se a spec/plano se provar inviável durante a implementação, é proibido
   improvisar — aborta e retorna à fase de especificação (geralmente gerando ADR).
5. **Segurança primeiro:** nunca commitar segredos (`.env` no runtime); lógica proprietária acoplada
   por interfaces + injeção de dependências. Detalhes em `docs/steering/seguranca.md`.
6. **Arquitetura Viva:** docker-compose (local) → infraestrutura cloud (IaC) → diagrama `.drawio` +
   `mapa.yml` sincronizados na mesma branch/PR. Procedimento na skill `arquitetura-viva`;
   parâmetros deste projeto em `docs/steering/arquitetura.md`.
7. **Memória contínua:** ler `docs/PROJECT_MEMORY.md` (memória quente, ~1 página) no início de toda
   sessão; registrar aprendizado novo ao encerrar sessão complexa.

## Tabela de roteamento do steering

Governança tem três camadas, separadas por **quando o conteúdo entra no contexto**:
premissa (este arquivo, sempre), procedimento (skills em `skills/`, por gatilho) e parâmetro
(`docs/steering/`, quando a skill mandar ler). Detalhe em `docs/adr/` do scaffold.

| Se a tarefa envolve… | Procedimento | Parâmetros deste projeto |
|---|---|---|
| Criar/alterar qualquer código | — | `docs/steering/sdd-processo.md` |
| Mudança estrutural, infra, novo componente | skill `arquitetura-viva` | `docs/steering/arquitetura.md` |
| Auth, upload, entrada externa, IaC, segredos | — | `docs/steering/seguranca.md` |
| Subir/atualizar ambiente, deploy, migrations | — | `docs/steering/infra-devops.md` |
| Preparar PR (testes, lint, contrato de saída) | — | `docs/steering/qualidade.md` |
| Painel/frontend | — | `docs/steering/frontend-ux.md` |
| Debugging | — | `docs/steering/troubleshooting.md` |

As skills ficam em `skills/` e são montadas em `.claude/skills`, `.codex/skills` e
`.kiro/skills`. Os três apontam para o mesmo corpo, então editar num lugar vale para todos.

## Mapa do repositório

```
src/           código-fonte da aplicação (módulos/pacotes do domínio)
infra/         local/ (docker-compose) · cloud/ (IaC multi-ambiente)
docs/          prd/ · specs/ · plans/ · adr/ · release-notes/ · steering/ · PROJECT_MEMORY.md
Arquitetura/   diagrama .drawio + mapa.yml (manifesto de correspondência)
scripts/       utilitários (inclui verificar_drift_arquitetura.py)
skills/        procedimento compartilhável, montado em .claude/ .codex/ .kiro/
tests/         suíte automatizada (unidade, integração, e2e)
```

**Estado:** {{DESCRICAO}}

## Fluxo mínimo de qualquer entrega

1. Classificar o tier (`sdd-processo.md`) e criar branch `feat|fix/YYYY-MM-DD-nome` a partir da `main`.
2. Tier 1+: plano em `docs/plans/` com seção **Impacto Arquitetural**; Tier 2: spec aprovada antes.
3. Implementar com TDD; evidências (testes/lint) coladas no plano antes de concluir.
4. Atualizar `CHANGELOG.md` (Keep a Changelog, versão incrementada) antes do merge.
5. PR com testes passando; Tier 2 passa por revisão adversarial contra a spec.
