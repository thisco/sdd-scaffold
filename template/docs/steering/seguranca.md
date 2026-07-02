# Segurança

> **Escopo:** segredos, autenticação/RBAC, código híbrido público/privado e menor privilégio em IaC.
> **Gatilho de leitura:** auth, upload, entrada externa ou mudança de IaC.
> **Última destilação:** {{DATA}}

## Segredos

Nunca comite credenciais, senhas, chaves de API, segredos JWT ou dados sensíveis em nenhum arquivo do repositório. Utilize arquivos `.env` carregados dinamicamente no runtime.

O scanner de segredos **gitleaks roda no CI** (workflow `qualidade.yml`) e é **bloqueante**: um segredo detectado reprova o pipeline e impede o merge.

## Código híbrido público/privado

Lógicas proprietárias ou integrações corporativas restritas devem ser acopladas via interfaces e injeção de dependências, permitindo que o core do sistema compile e funcione mesmo sem os módulos privados.

## Autenticação e RBAC

<!-- preencher: mecanismo de autenticação/autorização deste projeto (provedor de identidade,
     protocolo — ex.: OIDC —, modelo de papéis/permissões, emissor/issuer por ambiente e as
     ADRs que fixam essas decisões). A norma universal: um único mecanismo de auth aprovado,
     nenhum atalho paralelo; papéis com política clara (aditivos ou não). -->

## Checklist de threat-model (obrigatório em spec Tier 2 que toca auth/upload/entrada externa)

Toda spec Tier 2 que toque autenticação, upload ou entrada externa deve responder às 5 perguntas abaixo. **Cada "sim" exige, na spec, ao menos 1 parágrafo descrevendo a mitigação correspondente.**

1. Há **entrada não confiável** (dados externos, upload, payload de usuário)?
2. A **autenticação/autorização** foi alterada?
3. Há **dados sensíveis** trafegando ou persistindo?
4. Um **novo endpoint** foi exposto?
5. Houve **mudança de privilégio em IaC**?

## Menor privilégio em IaC

As policies IAM devem ser **restritas ao recurso e à ação estritamente necessários**. Todo wildcard `*` em `infra/cloud/modules/iam/` (ou equivalente) deve ser revisado como **critério explícito de code review** — só é aceito com justificativa documentada. O auditor de dependências roda no CI de forma **informativa** (não bloqueante), sinalizando dependências com vulnerabilidades conhecidas para triagem.
