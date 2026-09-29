---
name: threat-model
description: >-
  Use quando a mudança tocar autenticação, autorização, upload, webhook, endpoint novo,
  entrada vinda de fora do sistema, segredo, credencial ou privilégio em infraestrutura como
  código; e ao escrever spec de Tier 2 que envolva qualquer uma dessas superfícies.
---

# Threat-model em cinco perguntas

Spec que toca superfície sensível responde a cinco perguntas antes de virar código. O objetivo
não é produzir um documento de segurança, e sim forçar cinco olhadas específicas enquanto a
mudança ainda é barata de alterar.

## As perguntas

Responda cada uma com sim ou não. **Cada sim exige pelo menos um parágrafo descrevendo a
mitigação**, na própria spec, e não numa conversa que se perde.

1. Há **entrada não confiável**? Dado externo, upload, payload de usuário, resposta de API de
   terceiro, conteúdo de arquivo enviado.
2. A **autenticação ou autorização** foi alterada? Novo papel, nova permissão, mudança de quem
   pode o quê, mudança no emissor de token.
3. Há **dado sensível** trafegando ou sendo persistido? Pessoal, financeiro, credencial,
   segredo, qualquer coisa que a organização classifique como restrito.
4. Um **endpoint novo** foi exposto? Inclui fila consumida de fora, webhook recebido e job que
   aceita parâmetro externo.
5. Houve **mudança de privilégio** em infraestrutura como código? Policy nova, wildcard, papel
   com mais permissão do que tinha, recurso aberto para rede.

## Como responder bem

Uma mitigação descreve o mecanismo, não a intenção. "Validamos a entrada" não é mitigação;
"o payload é validado contra schema na borda, e campo desconhecido é rejeitado em vez de
ignorado" é.

Se a resposta honesta for "não sei", escreva isso. Uma pergunta em aberto declarada na spec vale
mais do que uma mitigação inventada, porque alguém pode respondê-la antes do merge.

Se a mitigação exigir uma decisão de difícil reversão, ela vira ADR. Escolha de provedor de
identidade, política de expiração de sessão e modelo de papéis são decisões, não detalhes.

## Menor privilégio

Policy restrita ao recurso e à ação estritamente necessários. Todo wildcard em policy é critério
explícito de revisão e só passa com justificativa escrita. Wildcard sem justificativa costuma
significar que ninguém sabia qual permissão bastava.

## Segredo

Segredo nunca é commitado. Ele vive em variável de ambiente carregada em runtime, e o scanner
roda bloqueante no CI. Se um segredo vazou para o histórico, rotacione antes de limpar o
histórico: remover o commit não invalida a credencial.

## Parâmetros deste projeto

Leia `docs/steering/seguranca.md` para o mecanismo de autenticação adotado, o provedor de
identidade, o modelo de papéis e as ADRs que fixam essas decisões.

Se esse arquivo não existir, trate como pergunta em aberto e escreva na spec: a mudança precisa
declarar qual mecanismo de auth está usando, e nunca introduzir um segundo em paralelo.

## Verificação

O job `normas-do-pr` avisa quando o diff toca superfície sensível e nenhuma spec do PR responde
ao checklist. O aviso não bloqueia, porque suficiência é julgamento; ele existe para que a
omissão seja visível na revisão.
