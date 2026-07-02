# Infraestrutura e DevOps

> **Escopo:** ambiente de dev local, CI/CD, deploy, migrations e rollback.
> **Gatilho de leitura:** ao subir/atualizar o ambiente, fazer deploy ou mudar o schema do banco.
> **Última destilação:** {{DATA}}

## Ambiente de dev local (ordem de rebuild)

O ambiente de desenvolvimento roda no docker compose (`infra/local/docker-compose.yml`). Se o código é *baked* nas imagens (sem live-reload), toda alteração exige rebuild antes de recriar os serviços.

<!-- preencher: serviços reais do docker-compose deste projeto e a ORDEM EXATA de rebuild
     ("subir/atualizar o ambiente de dev"): (1) migrations se o schema mudou; (2) rebuild das
     imagens cujo código mudou; (3) recriar os serviços (`docker compose up -d`); (4) verificar
     saúde (endpoints/portas de health). Documentar também atalhos comuns e comandos específicos. -->

Avaliar o **impacto cloud** de qualquer alteração de infra conforme a tabela de equivalências do guardrail de Arquitetura Viva (ver `docs/steering/arquitetura.md`).

## Migrations

- Use migrations versionadas em todas as alterações de esquema do banco de dados.
- Cada arquivo de migration deve conter funções explícitas e reversíveis de `upgrade` e `downgrade`.
- NUNCA edite migrations antigas já aplicadas em produção ou staging. Sempre crie uma nova migration corretiva incremental.

## Normas de deploy

<!-- preencher: normas de deploy específicas deste projeto (quais serviços são versionados/
     atualizados juntos para evitar descompasso de versão; proibição de operações manuais fora
     do CI/CD por perda de rastreabilidade; cuidados com auto-upgrades da nuvem que geram
     falso-diff no IaC; etc.). -->

## Rollback

Todo plano que inclua mudança de schema ou de deploy **declara explicitamente a estratégia de rollback** antes da execução. Formas aceitas conforme o tipo de mudança:

- Mudança de schema → `downgrade` da migration testado (executado ao menos uma vez em ambiente efêmero).
- Mudança de deploy/imagem → redeploy da imagem anterior via workflow.
- Perda ou corrupção de dados → restore a partir de backup.

## Workflows existentes

<!-- preencher: inventário de `.github/workflows/` deste projeto (deploy, reset de ambiente,
     qualidade etc.) com uma linha por workflow descrevendo seu papel. O workflow
     `qualidade.yml` já acompanha o scaffold (drift informativo, gitleaks bloqueante,
     auditoria de dependências informativa). -->
