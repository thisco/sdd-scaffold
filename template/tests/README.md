# tests/

Suíte automatizada de **{{NOME_PROJETO}}**. A estrutura reflete as camadas de garantia de
regressão descritas em `docs/steering/qualidade.md`.

```
unidade/     rápido, sem I/O — a maior parte da suíte
integracao/  toca banco/recurso efêmero provisionado por fixture (NUNCA o banco de dev)
e2e/         fluxo completo pela borda externa do sistema
```

## Regras que valem para as três camadas

- **Implementação de lógica começa por um teste que falha** (Fase 6 do SDD).
- **Correção de bug exige um teste que reproduz o defeito** — falha antes, passa depois; a
  evidência das duas execuções vai no plano em `docs/plans/`.
- **Dados de teste são determinísticos**: seed fixa e fixtures versionadas. Dado aleatório
  sem seed não produz regressão reproduzível.
- **Worktrees paralelas usam nomes de recurso distintos** para não colidir entre sessões.

<!-- preencher: comando de execução da suíte, marcadores por camada, variável de ambiente
     do banco de teste e piso de cobertura por módulo deste projeto. -->
