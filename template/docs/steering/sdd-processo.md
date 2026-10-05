# Processo Spec-Driven Development (SDD)

> **Escopo:** processo Spec-Driven Development (specs, planos, tiers, checkpoints, git).
> **Gatilho de leitura:** sempre que for criar ou alterar código.
> **Última destilação:** {{DATA}}

## Tiers de rigor

O rigor do processo é proporcional ao risco da mudança. Três níveis, com critérios objetivos:

- **Tier 0 — Trivial:** docs, typo, ajuste de configuração sem impacto de comportamento. Commit convencional direto, sem spec/plano. Critério: nenhuma linha de código executável alterada OU mudança sem efeito observável em runtime.
- **Tier 1 — Pequeno:** bug fix localizado ou ajuste em até ~3 arquivos de código. Plano leve em `docs/plans/` (contexto, arquivos e teste que prova o fix). Sem spec separada.
- **Tier 2 — Feature/estrutural:** fluxo completo spec → plano → checkpoints humanos entre fases → ADR quando houver decisão de difícil reversão.

Em caso de dúvida entre tiers, assumir o **tier mais alto**. Escalação obrigatória: se um Tier 0/1 revelar **impacto estrutural** durante a execução, aborta e reclassifica.

## Estrutura docs/

As alterações e o design do sistema são geridos de forma rigorosa através do diretório `docs/`. Antes de codar, leia e compreenda:

```
docs/
├── specs/            # PRDs, requisitos, diagramas e especificações (O QUE o sistema faz)
├── plans/            # Planos detalhados de implementação passo a passo (COMO implementar)
├── adr/              # Architecture Decision Records (Histórico de decisões técnicas de design)
├── steering/         # Normas de processo e domínio destiladas (constituição operacional viva)
└── release-notes/    # Histórico de entregas detalhadas por recurso e versão
```

## Regras do plano de implementação

Regras para os planos em `docs/plans/`:

- Cada plano de implementação deve ser mapeado em um arquivo markdown com nomenclatura: `docs/plans/YYYY-MM-DD-nome-curto.md`.
- **`CHANGELOG.md` na raiz:** Atualizar **antes do merge**, seguindo estritamente o formato *Keep a Changelog*. A entrada deve conter: número de versão semântica incrementado em relação ao último registro, data, título descritivo e bullet points categorizados em `### Adicionado`, `### Modificado` e/ou `### Corrigido`. A IA é responsável por incluir essa atualização na branch da feature, não o humano.
- O plano deve conter a lista exata de arquivos que serão criados ou editados, as assinaturas de novas funções/classes, e um plano detalhado de testes automatizados com cobertura mínima.
- **Rastreamento de Progresso (Dentro do Plano):** O acompanhamento das tarefas durante a implementação é feito exclusivamente por uma lista de marcadores no formato Markdown (`- [ ]` / `- [x]`) dentro do próprio arquivo `docs/plans/`. Nenhum arquivo ou diretório adicional de rastreamento deve ser criado fora desta estrutura.
- **Checkpoints de Revisão Humana:** Planos multi-fase devem definir checkpoints explícitos entre as fases. A IA deve pausar, apresentar os resultados parciais e aguardar aprovação explícita do humano antes de prosseguir para a próxima fase.

### Seção "Impacto Arquitetural" (obrigatória em planos Tier 1+)

Todo plano Tier 1 ou superior deve conter uma seção **"Impacto Arquitetural"** com as três verificações abaixo respondidas explicitamente:

- [ ] O `docker-compose.yml` (`infra/local/`) foi alterado?
- [ ] Algum módulo de IaC (`infra/cloud/modules/`) foi criado ou alterado?
- [ ] O diagrama `.drawio` e o `Arquitetura/mapa.yml` foram atualizados?

Se qualquer resposta for "sim", aplique o ciclo completo da Arquitetura Viva e a tabela de equivalências local→cloud. Consulte `docs/steering/arquitetura.md` para o procedimento detalhado.

## Strict fallback (proibição de gambiarra)

- Especificações são a fonte da verdade. Se durante a implementação (Fase 6 do SDD) um bloqueio técnico provar que o plano original ou a spec são inviáveis ou inseguros, o subagente desenvolvedor está **proibido** de inventar "gambiarras" ou seguir atalhos não documentados.
- A implementação deve ser abortada imediatamente e o fluxo retorna à Fase 1 (Especificação). A spec deve ser atualizada e re-aprovada pelo usuário (geralmente gerando uma ADR).

## Revisão adversarial (Tier 2)

Antes do PR de Tier 2, uma sessão/agente **independente** revisa a implementação **contra a spec** (não contra o diff), caçando requisitos não atendidos e desvios silenciosos. O revisor parte da spec e verifica que cada requisito foi de fato entregue, em vez de apenas ler o que mudou.

O resultado é registrado no próprio plano, em uma seção **"Revisão adversarial: <data> — achados"**.

## Specs como deltas arquiváveis

Specs descrevem a **mudança**, não o sistema. Conhecimento que virou permanente é promovido a `docs/steering/` ou a uma ADR; a spec antiga é **histórico**, não fonte de verdade viva. Ao concluir uma feature, avalie o que da spec deve ser destilado para steering/ADR — a spec permanece arquivada como registro do delta aplicado.

## Verificação antes de conclusão

Nenhuma tarefa fecha sem **evidência colada no plano**: saída de testes, saída de lint e/ou health check, conforme aplicável à mudança. Afirmações de sucesso sem evidência não encerram a tarefa.

## Git e commits

1. **Isolamento de Branches**:
   - Todo plano de implementação deve ser executado em uma branch isolada e limpa criada a partir da `main`.
   - Nomenclatura sugerida: `feat/YYYY-MM-DD-nome-recurso` ou `fix/YYYY-MM-DD-nome-bug`.
   - O merge deve ser feito via Pull Request (PR) após a aprovação do plano de implementação correspondente e com a suíte de testes passando.
2. **Mensagens de Commit Profissionais**:
   - Utilize a especificação de **Commits Convencionais** (Conventional Commits): `tipo(escopo): descrição no imperativo`.
   - Exemplos de formato válido:
     - `feat(<escopo>): adicionar <capacidade>`
     - `fix(<escopo>): corrigir <defeito>`
     - `test(<escopo>): cobrir <cenário>`
     - `docs(specs): criar especificacao de <feature>`
   - NUNCA use expressões informais ou que sugiram autoria automatizada de IA (ex: "IA corrigiu o bug").

<!-- preencher: escopos convencionais de commit padronizados deste projeto (ex.: nomes de
     módulos/subsistemas usados no `escopo` dos Conventional Commits). -->
