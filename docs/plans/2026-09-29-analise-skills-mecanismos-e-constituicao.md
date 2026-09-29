# Análise: skills, mecanismos de enforcement e onde moram as premissas gerais

> **Estado em 2026-09-29, fim do dia:** implementada. A camada 0 saiu na v1.3.0, os mecanismos
> de PR na v1.4.0 e as três skills na v1.5.0. Duas recomendações não sobreviveram ao contato com
> a implementação, e o apêndice do ADR-0001 registra quais e por quê. O texto abaixo fica como
> foi escrito, para que a diferença entre o previsto e o feito continue legível.

Data: 2026-09-29 · Insumo: pesquisa de internos de cinco harnesses
(`serpro-cloud-ia-governance/docs/research/harness-internals/`) e leitura integral dos sete
arquivos de steering do template.

---

## 1. A pergunta do enforcement tem uma resposta incômoda

Skill não faz enforcement de skill. A pesquisa dos harnesses separou as duas camadas com
clareza, e a separação é arquitetural:

| Camada | O que é | Exemplos | Falha quando |
|---|---|---|---|
| **Impede** | código rodando fora do modelo | hook `PreToolUse`, sandbox de SO, regra em `permissions.yaml`, job de CI | a regra está escrita errada |
| **Orienta** | texto dentro do modelo | constituição, steering, skill | o agente escolhe não seguir |

Uma skill é texto. Ela entra no contexto e orienta. Pedir que uma skill garanta o cumprimento
de outra skill é pedir que texto obrigue texto.

Então a pergunta certa não é "quais skills faltam para fazer enforcement", e sim **"para cada
norma que hoje só orienta, qual é o mecanismo que a verifica"**. Skill e mecanismo andam em
par: a skill ensina o procedimento, o mecanismo recusa a entrega que não o seguiu.

O teste empírico de hoje reforça isso por outro lado: sem skill nenhuma, só com a constituição,
o agente cumpriu quase tudo. O que faltou não foi orientação, foi alguém verificando.

---

## 2. Pares norma → skill → mecanismo

Levantamento a partir do conteúdo genuinamente genérico dos seis steering restantes.

| Norma (hoje só texto) | Vira skill? | Mecanismo que a verifica | Custo |
|---|---|---|---|
| Ciclo da Arquitetura Viva | ✅ feita | `verificar_drift_arquitetura.py` no CI, informativo | pronto |
| As 5 perguntas de threat-model em spec Tier 2 | ✅ `threat-model` | Job de CI: se o diff toca auth, upload, entrada externa ou IaC, a spec correspondente precisa ter a seção respondida | baixo |
| Migration com `upgrade` e `downgrade` | ✅ `migrations-reversiveis` | Job de CI que roda `downgrade` seguido de `upgrade` contra banco efêmero | médio |
| Nunca editar migration já aplicada | (mesma skill) | Job de CI que recusa diff em arquivo de migration já presente na `main` | baixo |
| Os 4 estados obrigatórios de tela | ✅ `estados-de-interface` | Slot obrigatório no modelo de spec, mais job que recusa spec de UI sem as quatro seções | baixo |
| Protótipo aprovado antes do código de página | (mesma skill) | Difícil de automatizar. Fica como item de checklist do PR | baixo |
| Estratégia de rollback declarada no plano | ❌ | Slot obrigatório no modelo de plano, mais job que recusa plano sem a seção quando o diff toca schema ou deploy | baixo |
| Evidência de teste colada no plano | ❌ | Job que procura bloco de evidência no plano quando o diff toca código | baixo |
| Commits convencionais | ❌ | `commitlint` no CI | baixo |
| Segredo nunca commitado | ❌ | `gitleaks`, já bloqueante | pronto |
| Menor privilégio em IaC | ❌ | Job que sinaliza wildcard em policy e exige justificativa no PR | médio |
| Protocolo de depuração sistemática | ❌ ver §3 | Teste que falha antes e passa depois, verificável no diff do PR | médio |
| Governança não se autoedita | ❌ | Hook, `permissions.yaml` e sandbox. Já feito nas três ferramentas | pronto |

**Skills propostas: três.** `threat-model`, `migrations-reversiveis`, `estados-de-interface`.
Todas têm procedimento genérico real, reuso entre projetos e um mecanismo que as verifica.

**Mecanismos propostos: sete jobs de CI**, dos quais cinco são de custo baixo.

### O que deliberadamente não vira skill

- **`depuracao-sistematica`.** O procedimento de reproduzir, levantar hipótese, buscar
  evidência e só então corrigir já existe como skill madura em ecossistemas de terceiros. Criar
  a nossa significaria manter uma versão pior da mesma coisa. O steering mantém o protocolo em
  quatro linhas e aponta para a skill instalada.
- **`sdd-processo`.** Decidido na Onda 2: a `sdd-lifecycle` já cobre todos os tópicos, e em
  vários com mais profundidade.
- **`infra-devops`.** Depois de extrair migrations e rollback, o que sobra é inteiramente do
  projeto: serviços do compose, ordem de rebuild, normas de deploy e inventário de workflows.

---

## 3. Redução dos steering ao que é específico

Estado atual, já contando a Onda 2.

| Arquivo | Linhas hoje | Sai para skill | Fica no projeto | Linhas depois |
|---|---|---|---|---|
| `arquitetura.md` | 42 | feito | estrutura, decisões-chave, equivalências local para nuvem | 42 |
| `sdd-processo.md` | 85 | nada, ver §2 | escopos de commit. O resto é premissa geral, ver §4 | ~15 |
| `seguranca.md` | 36 | as 5 perguntas de threat-model | mecanismo de auth, provedor de identidade, modelo de papéis | ~14 |
| `infra-devops.md` | 44 | migrations e rollback | serviços, ordem de rebuild, deploy, workflows | ~26 |
| `frontend-ux.md` | 30 | 4 estados e protótipo antes | design system, diretório de protótipos, stack | ~14 |
| `troubleshooting.md` | 16 | nada | gotchas do projeto | ~10 |

Total: de 253 linhas para cerca de 121, com o procedimento saindo de dentro de cada projeto e
passando a viver em um lugar só.

O critério de corte continua o do ADR-0001: fica no projeto o que muda de projeto para projeto.
Sai o que seria idêntico em qualquer repositório.

---

## 4. Onde moram as premissas gerais de todos os projetos

Esta é a lacuna mais séria do desenho atual, e ela não aparece na separação de três camadas
porque as três tratam de **um** projeto.

### O problema

Parte do que está hoje no `AGENTS.md` de cada projeto não varia entre projetos:

- português do Brasil em código, testes, commits e documentação;
- nenhum artefato menciona marca de assistente de IA;
- SDD com rigor proporcional ao risco, em três tiers;
- proibido improvisar: spec inviável aborta e volta à especificação;
- segredo nunca é commitado;
- Arquitetura Viva sincronizada na mesma branch;
- memória contínua lida no início da sessão.

Isso é **constituição da organização**, não do projeto. Hoje ela é copiada para dentro de cada
`AGENTS.md` no momento da geração, e a consequência é conhecida: uma decisão nova da NUARQ não
alcança nenhum dos projetos que já nasceram. Cada um carrega um retrato congelado do dia em que
foi gerado, e a divergência é silenciosa.

### Por que não resolver com include remoto

O caminho tentador é um `AGENTS.md` que importe um arquivo central. Ele foi descartado por uma
razão que custou caro esta semana: o `ANTIGRAVITY.md` do scaffold nunca foi lido por ferramenta
nenhuma, e o erro só apareceu porque alguém foi verificar. O Claude Code tem sintaxe de import,
mas ela não foi confirmada na pesquisa e não é interoperável com as outras ferramentas.
Depender de um mecanismo que só uma ferramenta implementa reintroduz exatamente o lock-in que o
scaffold existe para evitar.

### Proposta: quarta camada, materializada com versão declarada

Uma **constituição organizacional** versionada em repositório próprio, copiada para dentro de
cada projeto e com a versão declarada no `AGENTS.md`:

```
AGENTS.md do projeto
├── cabeçalho: constituicao_organizacional: nuarq v1.3
├── premissas do PROJETO (stack, idioma se diferente, domínio, mapa do repo)
└── tabela de roteamento

docs/constituicao/nuarq-v1.3.md   ← cópia literal, não editável pelo projeto
```

O que torna isso diferente de copiar e esquecer:

1. **A versão é declarada**, então dá para saber quem está atrasado sem abrir os repositórios.
2. **Um job de CI compara** a cópia local com a versão publicada e avisa quando há defasagem.
   Informativo, pela mesma razão do drift check: um projeto pode ter motivo legítimo para ficar
   numa versão anterior por um tempo.
3. **O hook de governança já protege** o arquivo contra edição pelo agente.
4. **Funciona nas três ferramentas**, porque é arquivo em disco lido pelo `AGENTS.md`, e não
   um recurso de uma ferramenta específica.

### As quatro camadas, revisadas

| Camada | Escopo | Onde | Quando entra | Muda quando |
|---|---|---|---|---|
| 0 · Constituição da organização | todos os projetos | `docs/constituicao/`, cópia versionada | sempre | a NUARQ decide |
| 1 · Premissa do projeto | um projeto | `AGENTS.md` | sempre | o projeto decide |
| 2 · Procedimento | todos os projetos | `skills/`, corpo único montado | por gatilho | a prática evolui |
| 3 · Parâmetro | um projeto | `docs/steering/` | quando a skill manda | o projeto muda |

A simetria que faltava: a camada 0 está para a 1 assim como a 2 está para a 3. As pares são
compartilhado contra local, e não sempre contra condicional.

---

## 5. Ordem sugerida

1. Camada 0, com a constituição organizacional extraída do `AGENTS.md` atual e o job de
   verificação de versão. É o que destrava o resto, porque define o que sai de cada projeto.
2. Os cinco mecanismos de CI de custo baixo. Eles pagam rápido e não dependem de skill.
3. As três skills, uma por vez, cada uma com o mecanismo correspondente entrando junto.
4. Redução final dos steering, que só é segura depois que skill e mecanismo existirem.

Fazer na ordem inversa produziria steering vazio antes de existir onde colocar o conteúdo.
