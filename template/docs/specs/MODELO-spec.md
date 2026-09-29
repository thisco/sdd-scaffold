# Spec: <título da mudança>

> **Tier:** 2 (feature/estrutural). Specs descrevem a **mudança**, não o sistema inteiro.
> **PRD relacionado:** `docs/prd/nome.md`. O PRD diz por que e para quem; esta spec diz o quê.
> **Status:** rascunho | em revisão | aprovada | arquivada
> **Data:** YYYY-MM-DD
> **Autor(es):** <nome>

## Motivação

<!-- Por que esta mudança existe. O problema/dor concreto, com contexto suficiente para
     alguém sem histórico entender a necessidade. -->

## Objetivos

<!-- O que esta mudança DEVE entregar. Lista verificável. -->

- ...

## Não-objetivos

<!-- O que esta mudança explicitamente NÃO cobre, para conter o escopo. -->

- ...

## Design proposto

<!-- Como a mudança será estruturada: componentes afetados, fluxo de dados, interfaces/contratos
     novos ou alterados, impacto arquitetural (compose ↔ IaC ↔ diagrama ↔ mapa.yml). -->

## Critérios de aceite

<!-- Condições objetivas e testáveis para considerar a spec atendida. Base da revisão adversarial. -->

- [ ] ...

## Riscos e mitigações

<!-- Riscos técnicos e de regressão que não são de segurança. -->

- ...

## Threat-model

<!-- OBRIGATÓRIO quando a mudança toca autenticação, autorização, upload, webhook, endpoint
     novo, entrada externa, segredo ou privilégio em IaC. Procedimento na skill `threat-model`.
     Responda cada pergunta; cada "sim" leva ao menos um parágrafo descrevendo a mitigação,
     e mitigação descreve mecanismo, não intenção. Se a mudança não toca nenhuma dessas
     superfícies, escreva "não se aplica" e o motivo, em vez de apagar a seção. -->

1. Há entrada não confiável?
2. A autenticação ou autorização foi alterada?
3. Há dado sensível trafegando ou sendo persistido?
4. Um endpoint novo foi exposto?
5. Houve mudança de privilégio em infraestrutura como código?
