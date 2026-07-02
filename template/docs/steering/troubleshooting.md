# Troubleshooting — gotchas estáveis por subsistema

> **Escopo:** gotchas estáveis por subsistema e o protocolo de debugging sistemático.
> **Gatilho de leitura:** qualquer sessão de debugging ou investigação de comportamento inesperado.
> **Última destilação:** {{DATA}}

## Protocolo de debugging sistemático

Siga sempre a ordem: **reproduzir → hipótese → evidência (log/teste) → correção**. A correção deve vir acompanhada de um **teste que falha antes e passa depois** — sem esse teste, o bug não está fechado. Todo gotcha novo descoberto na investigação entra na **memória quente** (`docs/PROJECT_MEMORY.md`) na **mesma sessão**, antes de encerrar.

## Gotchas por subsistema

<!-- preencher: gotchas estáveis descobertos ao longo do projeto, agrupados por subsistema
     (ex.: Infra & Deploy, Domínio, Pipeline & Testes). Cada entrada descreve o sintoma
     observável, a causa-raiz e a correção/precaução. Entradas nascem na memória quente
     (`docs/PROJECT_MEMORY.md`) e são promovidas para cá quando se provam estáveis. -->
