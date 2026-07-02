# Plano: <título da mudança>

> **Tier:** 1 | 2
> **Spec relacionada:** `docs/specs/YYYY-MM-DD-nome.md` (obrigatória em Tier 2)
> **Branch:** `feat|fix/YYYY-MM-DD-nome`
> **Data:** YYYY-MM-DD

## Contexto

<!-- Resumo do que será feito e por quê. Referência à spec quando aplicável. -->

## Arquivos afetados

<!-- Lista exata de arquivos a criar/editar e as assinaturas de novas funções/classes. -->

- `caminho/arquivo` — ...

## Plano de testes

<!-- Testes automatizados que provam a mudança (unidade/integração/e2e) e a cobertura mínima.
     TDD: o teste que falha vem antes do código de produção. -->

- ...

## Impacto Arquitetural

- [ ] O `docker-compose.yml` (`infra/local/`) foi alterado?
- [ ] Algum módulo de IaC (`infra/cloud/modules/`) foi criado ou alterado?
- [ ] O diagrama `.drawio` e o `Arquitetura/mapa.yml` foram atualizados?

<!-- Se qualquer resposta for "sim": aplicar o ciclo completo da Arquitetura Viva e a tabela de
     equivalências local→cloud (docs/steering/arquitetura.md). -->

## Estratégia de rollback

<!-- Obrigatória se há mudança de schema ou de deploy (docs/steering/infra-devops.md). -->

## Tarefas

- [ ] ...
- [ ] Atualizar `CHANGELOG.md` (Keep a Changelog, versão incrementada) antes do merge.
- [ ] Colar evidências (testes/lint) antes de concluir.

## Evidências

<!-- Saída real dos comandos de validação. Nenhuma tarefa fecha sem esta seção preenchida. -->

## Revisão adversarial: <data> — achados

<!-- Tier 2: preenchido pelo revisor independente que confere a implementação CONTRA a spec. -->
