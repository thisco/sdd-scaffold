# Qualidade

> **Escopo:** testes, lint, formato de saída, evidências e contratos regulatórios.
> **Gatilho de leitura:** antes de qualquer PR.
> **Última destilação:** {{DATA}}

## Validação local rígida

Antes de solicitar o Code Review de um desenvolvedor sênior ou submeter um Pull Request, garanta que:

1. A suíte completa de testes automatizados está passando.
2. O linter não aponta nenhuma inconformidade de estilo.
3. O formatador não aponta nenhuma inconformidade.
4. A cobertura mínima de testes foi atingida ou superada.

<!-- preencher: comandos exatos de validação deste projeto (ex.: runner de testes, linter e
     formatador com suas flags e o interpretador/venv correto). -->

## TDD e prove-it

- **Implementação de lógica começa por um teste que falha.** Escreva o teste antes do código de produção; ele deve falhar pela ausência da implementação, não por erro de setup.
- **Correção de bug exige um teste que reproduz o defeito** — falha antes da correção, passa depois. A evidência das **duas execuções** (falha e sucesso) vai no plano.

## Testes de integração

- **Nunca** rodar testes de integração contra o banco de dev.
- Usar banco/recurso efêmero provisionado por fixture, que cria e derruba o ambiente ao final. Isolar por variável de ambiente dedicada de teste (não reaproveitar a conexão de dev).
- Worktrees paralelas **usam nomes de recurso distintos** para não colidir com a fixture de outra sessão.

<!-- preencher: convenção concreta de banco/recurso efêmero deste projeto (variável de ambiente
     de teste, marcador de teste de integração, padrão de nomes por worktree). -->

## Contrato de saída (se houver)

<!-- preencher: se o projeto produz um artefato com contrato externo/regulatório (formato de
     arquivo, colunas, encoding, delimitador, nomenclatura, valores válidos), documentar aqui e
     apontar onde validar contra exemplos oficiais. Remover esta seção se não se aplica. -->

## Evidência antes de conclusão

Nenhuma tarefa ou PR fecha sem a **saída real** dos comandos de validação colada no plano. Não afirmar que algo passa sem o output correspondente.
