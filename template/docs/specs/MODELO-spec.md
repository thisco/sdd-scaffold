# Spec: <título da mudança>

> **Tier:** 2 (feature/estrutural). Specs descrevem a **mudança**, não o sistema inteiro.
> **PRD relacionado:** `docs/prd/nome.md`. O PRD diz por que e para quem; esta spec diz o quê.
> **Status:** rascunho | em revisão | aprovada | arquivada
> **Aprovado por:**
> **Aprovado em:**
> **Data:** YYYY-MM-DD
> **Autor(es):** <nome>

## Motivação

<!-- Por que esta mudança existe. O problema/dor concreto, com contexto suficiente para
     alguém sem histórico entender a necessidade. -->

## Requisitos

<!-- Cada requisito é uma linha `**R<n>** …` com id estável, e leva ao menos um critério de
     aceite logo abaixo. O id liga o requisito à tarefa do plano (`(R<n>)` no fim da tarefa) e
     ao teste (`# cobre: R<n>`). O verificador de PR confere esse rastro e avisa quando falta
     um elo; ele confere citação, não cobertura.
     Critério em GWT: **Dado** o contexto, **Quando** a ação, **Então** o resultado observável.
     Alternativa em EARS: QUANDO <evento>, O SISTEMA DEVE <resposta>.
     Aprovação: ao aprovar, troque o Status para `aprovada` e preencha `Aprovado por` e
     `Aprovado em` no cabeçalho. -->

**R1** <comportamento observável que a mudança entrega>
- Critério: **Dado** <contexto>, **Quando** <ação>, **Então** <resultado observável>.

## Não-objetivos

<!-- O que esta mudança explicitamente NÃO cobre, para conter o escopo. -->

- ...

## Design proposto

<!-- Como a mudança será estruturada: componentes afetados, fluxo de dados, interfaces/contratos
     novos ou alterados, impacto arquitetural (compose ↔ IaC ↔ diagrama ↔ mapa.yml). -->

## Riscos e mitigações

<!-- Riscos técnicos e de regressão que não são de segurança. -->

- ...

## Esclarecimentos

<!-- Dúvida que não dá para resolver agora: deixe no texto o marcador `[ESCLARECER: pergunta]`
     no ponto exato da ambiguidade. Spec aprovada, ou citada por plano, não pode ter marcador
     aberto: o verificador de PR avisa. Ao resolver, apague o marcador e registre aqui a
     pergunta e a resposta, uma sessão por data:

     ### Sessão AAAA-MM-DD
     - P: <pergunta> → R: <resposta> -->

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
