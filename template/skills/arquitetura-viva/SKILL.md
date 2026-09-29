---
name: arquitetura-viva
description: >-
  Use quando a mudança tocar infraestrutura, criar ou remover um componente, alterar
  docker-compose, módulos de IaC ou o diagrama de arquitetura, quando um PR que mexe em
  infra estiver prestes a fechar, ou quando o relatório de drift apontar divergência entre
  diagrama, IaC e ambiente local.
---

# Arquitetura Viva

Diagrama, infraestrutura como código e ambiente local descrevem o mesmo sistema. Quando eles
divergem, cada um continua parecendo correto isoladamente e ninguém percebe até alguém
confiar no artefato errado. Esta skill mantém os três amarrados por um manifesto e verificados
por um script.

## Quando usar

- Vai criar, remover ou renomear um componente do sistema.
- Vai alterar `infra/local/docker-compose.yml` ou qualquer módulo em `infra/cloud/modules/`.
- Vai fechar um PR que toca infraestrutura.
- O relatório de drift apontou divergência.

Não é para mudança que não altera a topologia do sistema. Renomear uma função interna ou
corrigir um cálculo não exige este ciclo.

## O ciclo, sempre na mesma branch

A ordem é imperativa, e a razão é que o ambiente local é o único lugar onde uma hipótese de
infraestrutura custa segundos para ser testada.

1. **Local primeiro.** Altere `infra/local/docker-compose.yml` e comprove que funciona.
2. **Depois a nuvem.** Escreva o equivalente em `infra/cloud/modules/`, consultando a tabela
   de equivalências do projeto.
3. **Depois o diagrama.** Atualize `Arquitetura/arquitetura.drawio`.
4. **Depois o manifesto.** Ajuste `Arquitetura/mapa.yml`.
5. **ADR, se a decisão for de difícil reversão.** Formato Nygard: contexto, decisão,
   consequências.

Separar esses passos em PRs diferentes é a forma mais comum de o drift começar.

## O manifesto

`Arquitetura/mapa.yml` é a ponte estável entre os três mundos, e é robusto contra
reformatação visual do XML do diagrama. Cada componente lógico declara seus avatares:

| Campo | Aponta para | Ausente significa |
|---|---|---|
| `drawio_label` | fragmento do texto do nó no diagrama | `null` é decisão consciente de não desenhar |
| `tofu_modulo` | diretório em `infra/cloud/modules/` | componente sem equivalente em nuvem |
| `compose_servicos` | serviços no docker-compose local | componente sem equivalente local |

Atualize o manifesto na mesma branch em que o avatar nasce ou morre.

## A verificação

```bash
python3 scripts/verificar_drift_arquitetura.py --raiz .
```

O script compara o manifesto com os rótulos extraídos do XML do diagrama, os diretórios de
módulo e os serviços do compose, e lista as divergências.

**O exit code é sempre 0.** O relatório informa e não bloqueia o merge. Isso é deliberado:
quando um check bloqueia, a primeira reação do time é procurar como desligá-lo. Leia o
relatório e reconcilie o que ele apontar.

No primeiro run de um projeto novo, com `componentes: []` ainda vazio, o script reporta o
módulo de exemplo como não mapeado. Isso é esperado e some quando você mapear os componentes
reais.

## Regressão estrutural

- Funcionalidade nova e correção de bug vêm acompanhadas de teste.
- Mudança destrutiva em assinatura de API ou em modelo de banco só acontece com ADR aprovada.
  A ADR é o registro que autoriza o que os guardrails de outra forma proíbem.

## PR que toca infraestrutura

Anexe a saída resumida do `plan` da ferramenta de IaC, para que quem revisa veja quais
recursos seriam criados, alterados e destruídos antes do merge.

## Parâmetros deste projeto

Leia `docs/steering/arquitetura.md` do repositório para: a estrutura real de diretórios, as
decisões estruturais já tomadas e a **tabela de equivalências local para nuvem**, que é
específica de cada stack.

Se esse arquivo não existir, use como defaults: variável de ambiente nova vira entrada no
gerenciador de segredos; porta ou serviço novo vira regra de rede; alteração em código de
worker exige rebuild de imagem. Confirme com uma pessoa antes de aplicar qualquer um desses
defaults em nuvem.

## Erros comuns

| Erro | O que acontece |
|---|---|
| Atualizar o diagrama num PR separado | O drift nasce no intervalo entre os dois merges |
| Escrever o IaC antes de validar local | Ciclo de correção passa de segundos para minutos |
| Mapear só o que é desenhado | Módulo sem nó no diagrama fica invisível na revisão |
| Tratar o relatório de drift como ruído | O script vira decoração e o manifesto apodrece |
