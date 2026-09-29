# ADR-0001 — Separação entre premissa, procedimento e parâmetro

- **Status:** aceita — decisão registrada em 2026-09-29; implementação programada (ver Consequências)
- **Contexto de origem:** pesquisa dos internos de 5 harnesses de coding agent
  (Claude Code 2.1.267, Codex CLI 0.157.1, Kiro, Antigravity, DeepSeek dsh), documentada em
  `serpro-cloud-ia-governance/docs/research/harness-internals/`

## Contexto

A governança deste scaffold mora hoje em duas formas: a constituição `AGENTS.md` (com
`{{NOME_PROJETO}}`, `{{STACK}}`, `{{DESCRICAO}}`) e sete arquivos em `docs/steering/`
totalizando 335 linhas. Esses sete arquivos contêm **dois tipos de conteúdo misturados**, e a
fronteira entre eles já está marcada no próprio texto: **15 comentários `<!-- preencher: … -->`**
separam a prosa de procedimento invariante ("correção de bug exige um teste que reproduz o
defeito") dos pontos onde o projeto concreto entra ("comandos exatos de validação deste
projeto").

A pesquisa dos harnesses trouxe dois fatos que forçam a decisão:

1. **O formato `SKILL.md` é hoje o maior denominador comum real entre ferramentas
   concorrentes.** É consumido nativamente por Claude Code, por Codex CLI (que ainda *exige* o
   uso da skill quando o gatilho casa) e por Kiro (via padrão aberto Agent Skills,
   `agentskills.io`). Evidência mais forte observada: as skills instaladas no Kiro da máquina de
   origem são o plugin `superpowers` do Claude Code **rodando sem alteração**.
2. **A tabela de roteamento do steering funciona por prompt, não por mecanismo.** No Codex, o
   `AGENTS.md` é concatenado *verbatim* dentro de `<INSTRUCTIONS>` como mensagem `user`; o
   harness não interpreta a tabela. O agente lê `docs/steering/*.md` porque a constituição
   manda — o que é obediência, não garantia. Apenas skills têm *progressive disclosure* nativo.

Se o procedimento virar skill compartilhada entre projetos, surge a pergunta que motiva esta
ADR: **onde ficam as instruções e premissas específicas de cada projeto?**

## Decisão

Classificar todo conteúdo de governança por **semântica de carregamento** — quando ele entra no
contexto do agente — e não por assunto. Três camadas:

| Camada | Onde mora | Quando entra no contexto | Conteúdo |
|---|---|---|---|
| **1 · Premissa** | `AGENTS.md`, com ponteiros `CLAUDE.md` e `GEMINI.md` | **Sempre.** Lido nativamente por Codex, Kiro e Antigravity | Stack, idioma, princípios inegociáveis, mapa do repositório, tabela de roteamento |
| **2 · Procedimento** | `SKILL.md`, compartilhável e versionado fora do projeto | **Sob demanda**, quando o `description` casa o gatilho | Como classificar tier, como conduzir TDD, como preparar PR, como depurar |
| **3 · Parâmetro** | `docs/steering/*.md`, arquivos curtos no repositório do projeto | **Quando a skill instrui a ler** | Comandos reais, variáveis de ambiente, convenções, contratos de saída |

### O critério decisivo

**Premissa não pode morar em skill.** Skills são reveladas *condicionalmente*, por casamento de
gatilho. Uma premissa como "este projeto é escrito em pt-BR e usa Postgres 16" precisa valer em
todo turno, inclusive naqueles em que nenhum gatilho casou. Por isso a camada 1 é sempre
carregada e precisa permanecer pequena — o Codex trunca documentos de projeto em
`project_doc_max_bytes = 32768` bytes, **silenciosamente**.

### Regra de dependência

Uma skill **nunca** contém conteúdo de projeto. Ela termina instruindo: *"leia
`docs/steering/<dominio>.md` deste repositório para os parâmetros locais; se o arquivo não
existir, use estes defaults"*. É a mesma propriedade de **degradar graciosamente** que a skill
`sdd-lifecycle` já declara no frontmatter: a skill funciona sem o projeto, o projeto especializa
a skill.

### Escotilha de escape

Procedimento genuinamente específico de um projeto vira **skill local** em `.claude/skills/` (ou
o diretório equivalente da ferramenta), marcada como local e **não promovida** ao repositório
compartilhado. Uma skill local que se provar útil em dois ou mais projetos é promovida por PR ao
repositório central — é o laço de composição que faz o conhecimento acumular em vez de ser
reinventado por projeto.

### Classificação dos sete arquivos atuais

Converter todos seria indireção sem retorno: dois deles são irredutivelmente do projeto.

| Arquivo | Linhas / marcadores | Destino |
|---|---|---|
| `sdd-processo.md` | 85 / 1 | Vira skill — procedimento quase puro |
| `troubleshooting.md` | 16 / 1 | Vira skill |
| `qualidade.md` | 41 / 3 | Skill + parâmetros |
| `seguranca.md` | 36 / 1 | Skill + parâmetros |
| `arquitetura.md` | 83 / 3 | Skill + parâmetros — a regra da Arquitetura Viva é genérica; a arquitetura em si é do projeto |
| `frontend-ux.md` | 30 / 3 | Skill + parâmetros |
| `infra-devops.md` | 44 / 3 | **Permanece só no repositório** — ambiente, deploy e migrations são do projeto |

## Alternativas consideradas e descartadas

- **Tudo em skill.** Descartada: premissa carregada condicionalmente deixa de ser premissa. Além
  disso, `infra-devops.md` não tem conteúdo compartilhável que justifique a indireção.
- **Tudo em steering, como hoje.** Descartada: abre mão do único mecanismo de *progressive
  disclosure* que os três harnesses implementam nativamente, e impede compartilhar procedimento
  entre projetos sem copiar arquivo — que é a causa clássica de divergência.
- **Duplicar o conteúdo nas duas formas.** Descartada pelo mesmo motivo pelo qual `CLAUDE.md` e
  `GEMINI.md` são ponteiros de quatro linhas em vez de cópias do `AGENTS.md`: duas cópias da
  mesma regra divergem, e a divergência é silenciosa.

## Consequências

**Positivas**
- O procedimento passa a ser exigido por mecanismo em Claude Code, Codex e Kiro, não por
  obediência a uma tabela.
- Procedimento vira ativo compartilhado e versionado; melhoria feita em um projeto beneficia os
  outros por PR.
- A camada 1 encolhe, o que reduz o risco de truncamento silencioso no Codex.

**Negativas e riscos**
- **É mudança major e quebra compatibilidade:** projetos existentes têm steering monolítico.
  Exige `docs/MIGRACAO-v2.md` com passo a passo.
- ⚠️ **`sgd-catalogo-nuvem` roda esta governança em produção.** A migração precisa ser validada
  lá antes de o scaffold anunciar a v2.
- Indireção a mais: quem lê um steering curto precisa saber qual skill traz o procedimento. A
  tabela de roteamento do `AGENTS.md` passa a ter duas colunas — "skill que ativa" e "parâmetros
  locais" — para que a indireção seja explícita.
- ⚠️ **Na CLI do Kiro os modos de inclusão de steering não funcionam**: tudo em
  `.kiro/steering/` carrega sempre. Steering precisa continuar pequeno, ou custa contexto em
  toda chamada.

**Implementação** — esta ADR registra a decisão; a execução é a Onda 2 do plano de melhoria
(converter os arquivos, emitir os diretórios de skill por ferramenta apontando para um único
corpo, reescrever a tabela de roteamento, escrever o guia de migração e validar no
`sgd-catalogo-nuvem`).
