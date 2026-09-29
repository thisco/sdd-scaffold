# Infraestrutura e DevOps

> **Escopo:** os parâmetros de ambiente e deploy deste projeto.
> **Procedimento:** migrations reversíveis e estratégia de rollback estão na skill
> `migrations-reversiveis`. O ciclo da Arquitetura Viva está na skill `arquitetura-viva`.
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

<!-- preencher: ferramenta de migration adotada, comando de execução, e como provisionar o banco
     efêmero em que o par upgrade/downgrade é testado. As regras estão na skill. -->

## Normas de deploy

<!-- preencher: normas de deploy específicas deste projeto (quais serviços são versionados/
     atualizados juntos para evitar descompasso de versão; proibição de operações manuais fora
     do CI/CD por perda de rastreabilidade; cuidados com auto-upgrades da nuvem que geram
     falso-diff no IaC; etc.). -->

## Rollback

<!-- preencher: qual workflow faz redeploy da imagem anterior, onde ficam os backups e qual o
     tempo de restauração conhecido. As formas aceitas estão na skill. -->

## Workflows existentes

<!-- preencher: inventário de `.github/workflows/` deste projeto (deploy, reset de ambiente,
     qualidade etc.) com uma linha por workflow descrevendo seu papel. O workflow
     `qualidade.yml` já acompanha o scaffold (drift informativo, gitleaks bloqueante,
     auditoria de dependências informativa). -->
