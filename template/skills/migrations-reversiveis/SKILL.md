---
name: migrations-reversiveis
description: >-
  Use quando a mudança alterar o esquema do banco, criar ou editar arquivo de migration,
  quando um plano precisar declarar estratégia de rollback, ou antes de um deploy que inclua
  alteração de schema.
---

# Migrations reversíveis

Mudança de schema é a classe de alteração mais cara de desfazer, porque o estado já mudou
quando o problema aparece. Reversibilidade é planejada antes, e não improvisada no incidente.

## Regras

1. **Toda alteração de esquema é uma migration versionada.** Nada de alterar o banco por fora,
   nem em desenvolvimento: o ambiente que diverge do histórico deixa de servir como teste.
2. **`upgrade` e `downgrade` explícitos**, ambos funcionando. Migration sem `downgrade` é uma
   decisão de não poder voltar, e decisão dessas se declara.
3. **Migration já aplicada nunca é editada.** Quem já rodou a versão anterior ficaria com um
   estado que o código não descreve. Crie uma migration corretiva incremental.
4. **`downgrade` é testado, não apenas escrito.** Rode o par completo em banco efêmero pelo
   menos uma vez antes do merge.

## Estratégia de rollback no plano

Todo plano que inclua mudança de schema ou de deploy declara a estratégia **antes** da execução.
Três formas aceitas, conforme o tipo de mudança:

| Tipo de mudança | Rollback |
|---|---|
| Schema | `downgrade` da migration, testado em ambiente efêmero |
| Deploy ou imagem | redeploy da imagem anterior pelo mesmo pipeline |
| Perda ou corrupção de dado | restore a partir de backup, com o tempo de restauração conhecido |

Declarar a estratégia às vezes revela que ela não existe. Descobrir isso no plano é barato;
descobrir durante o incidente, não.

## Mudança destrutiva

Remover coluna, renomear tabela e alterar tipo de forma incompatível são destrutivos, e só
acontecem com ADR aprovada. O padrão seguro é expandir e contrair: adicione o novo, migre os
dados, passe a ler do novo, e só então remova o antigo, em uma entrega posterior.

## Parâmetros deste projeto

Leia `docs/steering/infra-devops.md` para a ferramenta de migration adotada, o comando de
execução, a ordem de rebuild do ambiente local e as normas de deploy.

Se esse arquivo não existir, use como default: migration em banco efêmero provisionado por
fixture, nunca contra o banco de desenvolvimento, e par `upgrade` e `downgrade` rodado antes do
merge.

## Verificação

O job `normas-do-pr` **bloqueia** quando um arquivo de migration que já existe na base é
alterado, e **avisa** quando o diff mexe em schema sem nenhum plano declarando rollback.
