# Arquitetura de {{NOME_PROJETO}}

> **Escopo:** os parâmetros de arquitetura deste projeto.
> **Procedimento:** o ciclo da Arquitetura Viva, o manifesto e a verificação de drift estão na
> skill `arquitetura-viva` (em `skills/`). Este arquivo guarda o que é específico daqui.
> **Gatilho de leitura:** mudança estrutural ou de infraestrutura.
> **Última destilação:** {{DATA}}

## Estado e estrutura

<!-- preencher: estado atual do sistema (ambientes ativos, URLs/portas, banco de dados,
     armazenamento) e a árvore real do código-fonte (`src/…`), infra (`infra/local`,
     `infra/cloud`) e migrations. Substituir o esqueleto abaixo pela estrutura concreta. -->

```
src/
├── ...            # pacotes/módulos do domínio
infra/
├── local/         # docker-compose.yml (serviços de dependência do dev local)
└── cloud/         # IaC (multi-ambiente: dev, homol, prod)
```

## Decisões-chave

<!-- preencher: decisões estruturais estáveis do projeto (escolha de banco, estratégia de
     persistência/versionamento de dados, pontos de extensão/plugins, padrões de integração).
     Cada decisão de difícil reversão deve ter uma ADR correspondente em docs/adr/. -->

## Tabela de equivalências local para nuvem

Sempre que `infra/local/` ou uma configuração de aplicação mudar, avalie o impacto na nuvem
antes de fechar a tarefa. Esta tabela é o que a skill `arquitetura-viva` manda consultar no
passo 2 do ciclo, e ela é específica da stack deste projeto.

<!-- preencher: tabela de equivalências local→cloud específica deste projeto. Exemplo de formato:

| Alteração local | Equivalente cloud | Arquivo IaC |
|---|---|---|
| Nova variável de ambiente | Gerenciador de segredos + task/deployment | `infra/cloud/modules/secrets/` |
| Nova porta ou serviço | Security group + regra de balanceador | `infra/cloud/modules/networking/` |
| Alteração no código de worker | Rebuild obrigatório das imagens worker | (código baked, não live-reload) |
-->
