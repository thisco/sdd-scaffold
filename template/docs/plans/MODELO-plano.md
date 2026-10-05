# Plano: <título da mudança>

> **Tier:** 1 | 2
> **Spec relacionada:** `docs/specs/AAAA-MM-DD-nome.md` (obrigatória em Tier 2)
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

<!-- Se qualquer resposta for "sim": aplicar o ciclo da skill `arquitetura-viva` e a tabela de
     equivalências local para nuvem, que está em docs/steering/arquitetura.md. -->

## Estratégia de rollback

<!-- OBRIGATÓRIA quando há mudança de schema ou de deploy. Procedimento na skill
     `migrations-reversiveis`; os caminhos concretos deste projeto (workflow de redeploy,
     onde ficam os backups, tempo de restauração) estão em docs/steering/infra-devops.md.
     Declarar a estratégia às vezes revela que ela não existe, e descobrir isso aqui é
     barato. Seção vazia não conta: o verificador de PR checa se há conteúdo. -->

## Tarefas

<!-- Cada tarefa termina com os requisitos da spec que ela entrega, no formato `(R1)` ou
     `(R1, R2)`. O verificador de PR avisa quando um R<n> da spec não aparece em nenhuma
     tarefa, e quando uma tarefa cita um R<n> que a spec não tem. -->

- [ ] <descrição da tarefa> (R1)
- [ ] Atualizar `CHANGELOG.md` (Keep a Changelog, versão incrementada) antes do merge.
- [ ] Colar evidências (testes/lint) antes de concluir.

## Evidências

<!-- Saída real dos comandos de validação, colada em bloco de código. Nenhuma tarefa fecha sem
     esta seção preenchida, e o verificador de PR confere que há conteúdo, não apenas o título.
     Correção de bug leva as DUAS execuções: a que falha antes e a que passa depois. -->

## Revisão adversarial: <data> — achados

<!-- Tier 2: preenchido pelo revisor independente que confere a implementação CONTRA a spec.
     Uma linha por requisito da spec, com o veredito (atendido, parcial ou não atendido) e a
     evidência que o sustenta (teste, trecho, saída de comando). O verificador de PR avisa
     quando a tabela tem linhas e falta algum R<n>. -->

| R | veredito | evidência |
|---|---|---|
