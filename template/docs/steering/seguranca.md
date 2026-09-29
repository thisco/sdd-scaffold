# Segurança de {{NOME_PROJETO}}

> **Escopo:** os parâmetros de segurança deste projeto.
> **Procedimento:** o checklist de threat-model, as regras de menor privilégio e o tratamento de
> segredo estão na skill `threat-model`. Este arquivo guarda o que é específico daqui.
> **Gatilho de leitura:** auth, upload, entrada externa ou mudança de IaC.
> **Última destilação:** {{DATA}}

## Autenticação e autorização

<!-- preencher: mecanismo de autenticação/autorização deste projeto (provedor de identidade,
     protocolo — ex.: OIDC —, modelo de papéis/permissões, emissor/issuer por ambiente e as
     ADRs que fixam essas decisões). A norma universal: um único mecanismo de auth aprovado,
     nenhum atalho paralelo; papéis com política clara (aditivos ou não). -->

## Classificação de dado

<!-- preencher: quais dados este projeto trata e como são classificados (público, interno,
     restrito, pessoal). A classificação é o que determina a resposta à pergunta 3 do
     threat-model. -->

## Código híbrido público e privado

Lógica proprietária ou integração corporativa restrita é acoplada por interface e injeção de
dependências, de modo que o núcleo compile e funcione sem os módulos privados.

<!-- preencher: quais módulos deste projeto são privados e onde ficam as interfaces. Remover
     esta seção se o projeto é inteiramente aberto. -->
