# Arquitetura de Referência e Arquitetura Viva

> **Escopo:** arquitetura de referência e guardrail de sincronia (compose ↔ IaC ↔ diagrama ↔ ADR).
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

## Arquitetura Viva (guardrail obrigatório)

Toda mudança estrutural segue um ciclo formal, **sempre na mesma branch/PR**:

```
docker-compose (local) → IaC (cloud) → .drawio (visão) → ADR (se decisão)
```

A regra de precedência é imperativa: **qualquer alteração de infraestrutura deve ser validada primeiro no `docker-compose.yml` (`infra/local/`) antes de ser refletida no IaC de nuvem (`infra/cloud/`)**. Só depois de funcionar localmente o equivalente cloud é escrito, o diagrama `.drawio` é atualizado e — se houve decisão de difícil reversão — uma ADR é registrada.

### Tabela de equivalências local → cloud (OBRIGATÓRIO)

Sempre que `infra/local/` ou qualquer configuração de aplicação for alterada, avalie o impacto na infra em nuvem **antes de fechar a tarefa**. Mantenha o mapeamento de equivalências deste projeto atualizado.

<!-- preencher: tabela de equivalências local→cloud específica deste projeto. Exemplo de formato:

| Alteração local | Equivalente cloud | Arquivo IaC |
|---|---|---|
| Nova variável de ambiente | Gerenciador de segredos + task/deployment | `infra/cloud/modules/secrets/` |
| Nova porta ou serviço | Security group + regra de balanceador | `infra/cloud/modules/networking/` |
| Alteração no código de worker | Rebuild obrigatório das imagens worker | (código baked, não live-reload) |
-->

### Manifesto `Arquitetura/mapa.yml`

O manifesto `Arquitetura/mapa.yml` é a ponte estável entre os três mundos (diagrama, IaC, compose), robusta contra reformatação visual do XML. Cada componente lógico lista seus três avatares:

- `drawio_label` → fragmento do texto do nó no diagrama (`null` = decisão consciente de não desenhar);
- `tofu_modulo` → diretório em `infra/cloud/modules/`;
- `compose_servicos` → serviços em `infra/local/docker-compose.yml` (ausente = sem equivalente local).

**Quando atualizar:** a cada componente novo ou removido. Todo avatar criado (novo módulo de IaC, novo serviço no compose, novo nó no diagrama) ou retirado deve ter a entrada correspondente no `mapa.yml` ajustada na mesma branch/PR.

### Verificação de drift

Rode o verificador antes de fechar qualquer PR de infra:

```
python3 scripts/verificar_drift_arquitetura.py --raiz .
```

O script compara `mapa.yml` × labels extraídos do XML drawio × diretórios de `infra/cloud/modules/` × serviços do `docker-compose.yml` e emite um relatório de divergências (componente no IaC sem nó no diagrama, serviço no compose fora do mapa etc.). **Leia o relatório** e reconcilie as divergências apontadas. A severidade é informativa: o script sai **sempre com código 0** (nunca bloqueia); no CI o job `drift-arquitetura` publica o relatório como warning em PRs que tocam `infra/**`, `Arquitetura/**` ou `docker-compose*`.

### DevOps: plano de IaC no PR de infra

Todo PR que altera `infra/cloud/` deve anexar a **saída resumida do `plan`** da ferramenta de IaC, para que revisores validem o impacto real do apply (recursos criados, alterados, destruídos) antes do merge.

## Prevenção de regressões

- Cada funcionalidade nova ou correção de bug (`fix`) deve vir obrigatoriamente acompanhada de testes unitários e/ou de integração robustos.
- Modificações destrutivas na assinatura de APIs ou no modelo de banco de dados são estritamente proibidas, a menos que explicitamente previstas em uma **ADR** aprovada.

## ADRs

- **Quando criar:** sempre que uma decisão for de difícil reversão (escolha de banco, mudança destrutiva de API/schema, escolha de plataforma de auth, política de default etc.). A ADR é o registro que autoriza mudanças que os guardrails de outra forma proíbem.
- **Onde:** em `docs/adr/`, um arquivo por decisão.
- **Formato Nygard:** **contexto** (forças em jogo e o problema) → **decisão** (o que foi decidido) → **consequências** (o que fica mais fácil e mais difícil como resultado).
