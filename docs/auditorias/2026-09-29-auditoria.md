# Auditoria do sdd-scaffold

- **Data:** 2026-09-29
- **Versão auditada:** 1.6.0 (HEAD `7099894`, árvore de trabalho limpa)
- **Auditor:** agente `auditor-de-scaffold`
- **Método:** leitura integral de `README.md`, `CHANGELOG.md`, `docs/adr/0001`, `docs/plans/2026-09-29-…`,
  `criar_projeto.py`, `test_criar_projeto.py`, os dois workflows de CI e todo o `template/`;
  execução da suíte; geração de um projeto real em diretório temporário; construção manual do
  caso-que-deve-pegar e do caso-inocente para cada um dos quatro mecanismos; 19 consultas web.
- **Convenção de origem:** `[verificado: …]` foi executado ou lido nesta auditoria ·
  `[web: …]` fonte externa, com data de acesso 2026-09-29 · `[inferido]` raciocínio, não fato ·
  **não verificado** onde não houve como confirmar.
- **Interpretador da suíte:** venv do scratchpad (o `python3` do sistema não tem pytest nem PyYAML).

---

## Sumário executivo

A suíte passa (22 testes) e o gerador funciona de ponta a ponta. O problema não está no que é
testado, está na distância entre o que o repositório afirma sobre os **mecanismos** e o que eles
fazem quando executados fora dos testes.

Os três achados mais graves têm a mesma forma: **o teste valida uma versão imaginada do artefato,
não o artefato que o template entrega.**

1. O hook de governança (`proteger_governanca.py`) não dispara em uso real do Claude Code, porque
   compara caminho relativo contra o `file_path` **absoluto** que o harness envia.
2. O verificador de PR aprova a `MODELO-spec.md` **real** copiada e nunca preenchida — exatamente o
   defeito que o CHANGELOG [1.6.0] declara corrigido. O teste de regressão usa uma spec fabricada à
   mão que não corresponde ao modelo em `template/docs/specs/`.
3. Dois dos três controles "por ferramenta" (`.kiro/permissions.yaml`, `.codex/requirements.toml`)
   usam nome de capacidade / chave / caminho que a documentação dos produtos não confirma. É a
   repetição do erro do `ANTIGRAVITY.md`, na coluna do README que mais se orgulha de "impedir".

Somando: a tabela "O que impede e o que orienta" descreve quatro controles, e nenhum dos três de
ferramenta tem prova de que impede alguma coisa. Só o CI (`verificar_pr.py`) foi observado
funcionando — e com os furos da seção 1.4.

---

# Frente 1 · O repositório corresponde ao que afirma?

## 1.0 O que passou

- Suíte: **22 testes, 22 passam, 22,03 s** [verificado: `pytest -q` na raiz]. O README não afirma
  número de testes, então não há contagem errada aqui.
- Gerador: gera projeto, substitui placeholders, preserva os três symlinks de montagem, instala a
  `sdd-lifecycle` com `PROCEDENCIA.md`, faz `git init -b main` e o commit inicial
  [verificado: `python3 criar_projeto.py --nome alvo --destino …`].
- Contagens de documentação conferidas e **corretas**: 7 arquivos de steering totalizando 280 linhas;
  `seguranca.md` 28, `frontend-ux.md` 26, `infra-devops.md` 42 [verificado: `wc -l template/docs/steering/*.md`].
- `CLAUDE.md` e `GEMINI.md` têm de fato 4 linhas e citam `AGENTS.md` [verificado].
- `AGENTS.md` gerado tem 5.407 bytes, muito abaixo do limite de 32.768 [verificado: `ls -la`].
- O gerador é stdlib pura [verificado: imports de `criar_projeto.py`].
- Todos os caminhos citados na árvore "O que você recebe" do README existem no projeto gerado,
  com uma exceção (§1.2, `src/`) e uma ausência não listada (§1.1, `requirements.txt`).

## 1.1 CRÍTICO · O hook de governança não dispara em uso real

`proteger_governanca.caminho_protegido` normaliza apenas os prefixos `./` e `/` e depois compara
com `fnmatch` contra padrões relativos (`AGENTS.md`, `docs/adr/*`, …).

O Claude Code envia, no evento `PreToolUse`, `tool_input.file_path` **absoluto**:
> "`tool_input.file_path` is absolute, not relative. This applies to file-manipulation tools."
> [web: https://code.claude.com/docs/en/hooks]

E os próprios schemas de `Edit`/`Write` exigem caminho absoluto
[verificado: definição das tools nesta sessão — "The absolute path to the file to modify"].

Consequência medida:

```
{"tool_name":"Edit","tool_input":{"file_path":"AGENTS.md"}}                   -> ASK
{"tool_name":"Edit","tool_input":{"file_path":"/…/gen/c/AGENTS.md"}}          -> LIVRE
```
[verificado: execução do hook do projeto gerado com os dois payloads]

O hook está inerte na única ferramenta em que ele existe. O teste
`test_hook_protege_governanca_e_libera_codigo` alimenta somente caminhos relativos, então ele
certifica um comportamento que o harness nunca produz. **É o mesmo erro do `ANTIGRAVITY.md`:
um arquivo que parece hook e não é** — agravado por existir um teste verde em cima dele.

Outros furos do mesmo mecanismo, todos medidos:

| Entrada | Resultado | Por que importa |
|---|---|---|
| `docs/../AGENTS.md` | LIVRE | sem normalização de `..` |
| `tool_name: "Bash"` com `echo x > AGENTS.md` | LIVRE | `Bash` não está em `FERRAMENTAS_DE_ESCRITA`; `sed -i`, `cat >`, `tee` e um script Python passam direto |
| `Arquitetura/arquitetura.drawio` | LIVRE | `.kiro/permissions.yaml` protege `Arquitetura/*.drawio`; o hook não. A afirmação do README "é a mesma regra que o Kiro aplica" é falsa |
| `.claude/settings.json`, `scripts/proteger_governanca.py`, `.kiro/permissions.yaml`, `.codex/requirements.toml` | LIVRE nos dois mecanismos | o agente pode desarmar o próprio controle sem aprovação |
| `tool_name` `Update` / `apply_patch` | LIVRE | nomes de tool de outras versões/harnesses |

Ainda: o comando registrado é `python3 scripts/proteger_governanca.py`, caminho relativo. A
documentação recomenda `${CLAUDE_PROJECT_DIR}` [web: https://code.claude.com/docs/en/hooks]; com
caminho relativo, uma sessão aberta em subdiretório não encontra o script e o hook falha em
silêncio.

**Existe caminho declarativo, e ele é estritamente melhor.** O Claude Code tem sistema de
permissões com precedência `deny > ask > allow` — a mesma do `permissions.yaml` do Kiro — sintaxe
estilo gitignore, e ancoragem no diretório de trabalho para padrões `/path`
[web: https://code.claude.com/docs/en/permissions]. Duas propriedades decisivas para este caso:

- regras `deny`/`ask` **valem imediatamente**, sem depender de "trust" da pasta (ao contrário de
  `allow`);
- regras `Read`/`Edit` **também cobrem** comandos de arquivo dentro do Bash (`cat`, `sed`, `tee`) e
  os alvos de redirecionamento `> file`.

Ou seja: trocar o hook por `permissions.ask: ["Edit(/AGENTS.md)", "Edit(/docs/constituicao/**)",
"Edit(/docs/adr/**)", "Edit(/Arquitetura/mapa.yml)", "Edit(/Arquitetura/*.drawio)",
"Edit(/.github/workflows/**)", "Edit(/.claude/settings.json)"]` elimina o bug de caminho absoluto,
fecha o desvio por Bash, fica simétrico ao arquivo do Kiro e apaga 80 linhas de Python.
Atenção a uma pegadinha documentada: regra de caminho escrita para `Write(...)`, `NotebookEdit(...)`
ou `MultiEdit(...)` é aceita e **nunca consultada** — só `Edit(path)` e `Read(path)` entram na
checagem de arquivo [web: idem].

## 1.2 CRÍTICO · O verificador de PR aprova a MODELO-spec real não preenchida

O CHANGELOG [1.6.0] abre com: *"O verificador de PR aprovava documento intocado … Agora a
verificação exige seção com conteúdo."* A mesma release moveu as cinco perguntas de threat-model
**de dentro de um comentário HTML para prosa numerada** em `MODELO-spec.md` (linhas 51-55). As duas
mudanças se anulam: `secao_preenchida` remove comentários, mas as cinco perguntas agora são
conteúdo legítimo sob o título.

Medido contra o modelo que o template realmente entrega:

```
secao_preenchida(MODELO-spec.md real, "threat-model", …)          -> True
analisar(["src/auth/login.py","docs/specs/2026-09-29-x.md"], {spec = MODELO-spec.md real})
  -> nenhum achado de threat-model
```
[verificado: script em scratchpad carregando `scripts/verificar_pr.py` do projeto gerado]

O teste `test_secao_apenas_mencionada_nao_conta_como_preenchida` não pega isso porque constrói à
mão uma `spec_do_modelo` com a seção "Riscos e mitigações" e um comentário — a forma **anterior** do
modelo. O teste virou um fóssil: descreve o bug corrigido, não o artefato corrente.

Defeito irmão, mesma função: `RESIDUO` não reconhece caixa de marcação vazia. `- [ ]` e `- [ ] ...`
contam como conteúdo [verificado]. Como `MODELO-spec.md` usa `- [ ] ...` em "Critérios de aceite" e
`MODELO-plano.md` em "Tarefas", qualquer seção que o projeto converta em checklist passa intocada.

Correção mínima: o caso de teste deve **ler `template/docs/specs/MODELO-spec.md` do disco** em vez
de reconstruí-lo; e a detecção precisa exigir sinal de resposta (não só presença de linha), por
exemplo que cada pergunta numerada tenha texto depois do `?`, ou marcar as perguntas do modelo com
um token sentinela (`<!-- responda -->`) que conte como resíduo.

## 1.3 CRÍTICO · Os controles de Kiro e Codex não têm confirmação de que existem

O README apresenta três controles "um por ferramenta". Nenhum foi verificado contra o produto.

**`.kiro/permissions.yaml`.** O template usa `capability: fs.write` (ponto) e coloca o arquivo na
raiz do repositório. A documentação do Kiro descreve capacidades com **underscore** — `fs_read`,
`fs_write`, `filesystem`, `shell`, `web_fetch`, `mcp`, … — e escopos em
`~/.kiro/settings/permissions.yaml` (usuário) e `~/.kiro/workspace-roots/<hash>/permissions.yaml`
(workspace) [web: https://kiro.dev/docs/permissions/, via busca 2026-09-29]. A precedência
`deny > ask > allow` que o arquivo documenta está **correta**; o nome da capacidade e o local do
arquivo, provavelmente não. Há inclusive issues abertas no repositório do Kiro sobre a CLI ignorando
`.kiro/settings/permissions.yaml` [web: github.com/kirodotdev/Kiro issues #11037, #9567].

**`.codex/requirements.toml` com `git_attribution = false`.** A chave documentada para atribuição de
commit no Codex é `commit_attribution`, em `~/.codex/config.toml`; `requirements.toml` aparece como
arquivo de **restrição administrativa em máquina gerenciada**, não como config por repositório
[web: developers.openai.com/codex/config-advanced e codex.danielvaughan.com, via busca 2026-09-29].

**Não verificado:** não tenho o Kiro nem o Codex instalados aqui para conferir contra o binário. A
pesquisa de harnesses citada na ADR (Codex CLI 0.157.1, Kiro) pode ter achado nomes internos reais
que a documentação pública não usa. Mas o padrão de rigor que o próprio README estabelece
("verificado em 2026-09-29", e a nota do `ANTIGRAVITY.md`) exige que essa verificação esteja
registrada — e ela não está. **Enquanto não estiver, os dois arquivos são candidatos a inertes, e
um arquivo que parece controle e não é custa depuração a alguém.**

## 1.4 ALTO · `verificar_pr.py`: os irmãos do falso positivo do `iam`

A fronteira de palavra resolveu `LEIAME.md`. Ela não resolve `_`, `-`, `.` e `/`, que também são
fronteira. Medido:

| Caminho | Dispara? | Token |
|---|---|---|
| `src/token_bucket.py` (rate limiting) | **sim** | `token` |
| `src/rate_limit/token_ring.go` | **sim** | `token` |
| `data/tokens.csv` | **sim** | `tokens` |
| `docs/endpoint-catalog.md` | **sim** | `endpoint` |
| `web/static/login.css` | **sim** | `login` |
| `docs/adr/0007-uso-de-oauth.md` | **sim** | `oauth` |
| `docs/plans/2026-09-29-refatorar-iam-doc.md` | **sim** | `iam` |
| `src/miami_report.py`, `CHANGELOG.md`, `README.md` | não | — |
[verificado: `SENSIVEL.search` sobre cada caminho]

Dois padrões ruins saem daí:

1. **PR só de documentação recebe aviso de threat-model.** Um PR que muda apenas
   `docs/adr/0007-uso-de-oauth.md` e o `CHANGELOG.md` produz o aviso [verificado]. É o mesmo tipo de
   ruído do `LEIAME.md`, uma release depois.
2. **O PR se autoacusa pelo nome do próprio documento.** Uma spec chamada
   `docs/specs/2026-09-29-login-social.md` faz o PR "tocar superfície sensível" por causa do nome do
   arquivo de spec. O sinal deveria vir de caminhos de **código e IaC**, não de `docs/**`.

Correção de ordem de grandeza baixa: excluir `docs/**`, `CHANGELOG.md` e `README*` da varredura de
superfície sensível, e exigir que o token case em segmento de caminho ou em nome de arquivo sem
sufixo `_algo` de vocabulário genérico. Ou, mais barato e mais honesto: casar diretório
(`**/auth/**`, `**/authn/**`, `infra/cloud/**`) em vez de palavra dentro de nome de arquivo.

Outros dois furos da mesma função:

- **`EVIDENCIA` é buscado no documento inteiro**, não na seção de evidências. Um plano com a palavra
  "ok" em qualquer lugar e um título "Evidências" com uma linha qualquer passa: `"# Plano\n\nContexto
  ok.\n\n## Evidências\n\nrodei e passou\n"` produz **zero achados** [verificado].
- **Ponteiro morto na própria mensagem do verificador.** Ele diz *"Cinco perguntas em
  `docs/steering/seguranca.md`"* (`verificar_pr.py:122`). As cinco perguntas saíram de lá na v1.5.0 e
  hoje estão em `skills/threat-model/SKILL.md` e em `MODELO-spec.md` — há inclusive um teste
  (`test_steering_ficou_so_com_parametro_de_projeto`) que **exige** que não estejam mais lá
  [verificado: `grep -rn seguranca.md`]. A release 1.6.0 caçou ponteiros mortos nos modelos e deixou
  este, que aparece na saída do CI.

## 1.5 ALTO · O CI do projeto gerado não pode passar: falta `requirements.txt`

`template/.github/workflows/qualidade.yml` roda `pip install -r requirements.txt` no job `testes` e
`pip-audit -r requirements.txt` no job `dependencias`. O template **não emite `requirements.txt`**
[verificado: `ls requirements.txt` no projeto gerado → não existe]. O default de `--deps` é
justamente `requirements.txt`, então o caminho padrão produz um projeto cujo primeiro PR falha no
primeiro job.

Isso não é pego por nada: o `ci.yml` do scaffold gera o projeto, roda **só** o drift check e procura
placeholder residual; nunca tenta executar o workflow do projeto gerado.

Ordem de grandeza: emitir um `template/requirements.txt` com `pyyaml` (que o drift check exige) e um
comentário `<!-- preencher -->`. Uma linha de código, uma de teste.

## 1.6 ALTO · `pyproject.toml` nasce com placeholder não substituído

```
alvo/pyproject.toml:1:# Configuração de ferramentas de {{NOME_PROJETO}}.
alvo/pyproject.toml:2:# Stack: {{STACK}}
```
[verificado: `grep -rn '{{[A-Z_]*}}'` no projeto gerado]

Causa: `.toml` não está em `EXTENSOES_TEXTO` (`{".md",".yml",".yaml",".py",".tf",".gitignore",".drawio",""}`).

Por que sobreviveu a dois portões: `test_gera_projeto_sem_placeholders_residuais` filtra
`p.suffix in {".md",".yml",".yaml",".py",".tf"}`, e o passo de CI usa
`grep -rl '{{[A-Z_]*}}' --include='*.md' --include='*.yml' --include='*.py'`. **Os dois verificadores
herdaram a mesma lista incompleta do código que deveriam auditar.** Um verificador que compartilha a
premissa do verificado não é verificação.

Correção: varrer **todo** arquivo de texto no teste e no CI (sem allowlist de extensão), e acrescentar
`.toml` e `.json` a `EXTENSOES_TEXTO`.

## 1.7 MÉDIO · `verificar_constituicao.py`: o mecanismo não verifica o que o README promete

O README afirma: *"Editar a constituição dentro de um projeto **reprova** (exit 1), porque ela é
compartilhada."* O que o script faz é comparar **duas cópias locais** entre si. Medido:

| Caso | Resultado esperado | Resultado real |
|---|---|---|
| Projeto recém-gerado | passa | passa (exit 0) |
| Adulterar só o bloco inline | reprova | reprova (exit 1) |
| **Adulterar inline E o canônico juntos** ("Segredo nunca é commitado" → "Segredo pode ser commitado") | reprova | **passa, exit 0** |
| Remover o bloco inline inteiro | reprova | reprova (exit 1) |
| `AGENTS.md` ausente | ? | passa, "nada a verificar" |
| `--origem` com diretório inexistente | avisar | silêncio, exit 0 |
| `--origem` com `padrao-v1.0/v2.0/v10.0` publicadas | apontar v10.0 | aponta **v2.0** |
[verificado: sete execuções sobre um clone do projeto gerado]

Três problemas distintos:

1. **A adulteração coordenada é invisível.** Um agente (ou uma pessoa com pressa) que edite os dois
   arquivos no mesmo commit passa pelo portão. Editar dois arquivos é mais fácil do que editar um, e
   o hook que deveria pedir aprovação está inerte (§1.1). A verificação só teria dente se comparasse
   **conteúdo** contra uma origem externa — e `--origem` hoje compara apenas **nome de versão**.
   Nenhum job de CI passa `--origem`.
2. **Ordenação lexicográfica de versão.** `sorted(pasta.glob("*.md"))[-1]` diz que `padrao-v2.0` é
   mais nova que `padrao-v10.0`. O defeito acorda exatamente quando a organização chega à décima
   versão, e a mensagem também inverte de sentido quando o projeto está **à frente** da origem:
   qualquer nome diferente produz "a organização publicou X e este projeto usa Y".
3. **`--origem` errado é no-op silencioso.** Diretório inexistente ou vazio não gera diagnóstico.
   Um typo no caminho desliga a verificação sem que ninguém saiba.

## 1.8 MÉDIO · `verificar_drift_arquitetura.py`: "exit 0 sempre" é falso, e a checagem é meio cega

**Acerta o que promete pegar** [verificado]: módulo OpenTofu novo não mapeado, `tofu_modulo`
declarado inexistente, `compose_servico` inexistente e `drawio_label` ausente do diagrama — seis
divergências no caso construído, exit 0. O caso inocente fica limpo.

Mas:

1. **O exit code não é sempre 0.** `mapa.yml` sem a chave `diagrama` levanta `KeyError`; `diagrama`
   apontando para arquivo inexistente levanta `FileNotFoundError`. Nos dois casos o processo sai 1
   com traceback [verificado]. O step do CI do template é `SAIDA=$(python3 …)` sob `bash -e`, então
   ele **falha o job** — simulado: `exit do step=1` [verificado]. O README, o comentário do
   `mapa.yml` e a skill `arquitetura-viva` afirmam, os três, "nunca bloqueia o CI". Um `mapa.yml`
   malformado transforma o check informativo em portão bloqueante, e a mensagem que o time vê é um
   traceback de Python.
   Também: sem PyYAML instalado o script sai 1 com `ModuleNotFoundError` [verificado].
2. **A comparação com o diagrama é unidirecional.** `modulos` e `servicos` são comparados nos dois
   sentidos; os rótulos do `.drawio`, só de `mapa.yml` → diagrama. Um nó desenhado no diagrama que
   não existe em nenhum componente **nunca** é reportado. Isso contradiz "compara os três e reporta
   divergências" e é a metade do drift que mais acontece (alguém desenha a caixa e não implementa).
3. **Casamento por substring aceita rótulo degenerado.** `drawio_label: "a"` casa com qualquer
   rótulo que contenha a letra "a"; `"Dado"` casa com "Dados". Um mapa com rótulos de uma letra
   passa 100% verde [verificado: caso 5]. É um jeito acidental de silenciar o check.

## 1.9 MÉDIO · Contradições internas na documentação

Ordenadas por quanto custam a quem lê.

1. **Checklist de pós-geração contradiz a própria release.** README, "Pós-geração":
   *"**Instalar a skill do ciclo.** O scaffold traz `skills/arquitetura-viva`, mas o ciclo SDD em si
   é conduzido pela skill `sdd-lifecycle` … **Copie-a para `skills/` se quiser o ciclo completo.**"*
   A v1.6.0 fez o gerador instalar essa skill automaticamente, e o próprio README diz isso duas
   seções antes. O checklist também fala de "`skills/arquitetura-viva`" no singular quando o
   scaffold traz quatro skills. É a seção mais antiga do documento sobrevivendo à mudança
   [verificado: README linhas 208, 213-227 vs 287-289].
2. **ADR-0001, apêndice: "Três skills foram criadas" seguido de quatro nomes**
   (`arquitetura-viva`, `threat-model`, `migrations-reversiveis` e `estados-de-interface`). Três
   foram criadas na v1.5.0; `arquitetura-viva` veio na v1.2.0. A frase junta as duas coisas e a
   contagem fica errada [verificado: `docs/adr/0001…` linhas 190-191].
3. **`docs/steering/sdd-processo.md` descreve uma `docs/` que não é mais a do template.** A árvore
   lista `specs/ # PRDs, requisitos, diagramas e especificações` e omite `constituicao/` e `prd/` —
   quando `docs/prd/MODELO-prd.md` foi criado na v1.2.0 justamente porque *"o fluxo saltava da ideia
   para a spec"*. O mesmo arquivo manda *"Consulte `docs/steering/arquitetura.md` para o
   procedimento detalhado"*, e o procedimento saiu de lá para a skill `arquitetura-viva` na v1.2.0.
   São dois ponteiros mortos da mesma família que a 1.6.0 caçou nos modelos [verificado].
4. **Numeração de fase sem definição e inconsistente.** `sdd-processo.md` cita "Fase 3 do SDD"
   (implementação) e "Fase 1 (Especificação)"; `tests/README.md` cita "Fase 6 do SDD" para começar
   pelo teste que falha. Nenhum arquivo do projeto gerado define essas fases — elas vivem na
   `sdd-lifecycle`, que pode nem estar instalada. Dois números diferentes para o mesmo momento do
   ciclo [verificado].
5. **"três controles" com tabela de quatro linhas** (Claude Code, Kiro, Codex, CI), e o parágrafo
   seguinte volta a dizer "nas três ferramentas". Ambíguo o suficiente para o leitor contar errado
   [verificado: README linhas 69-79].
6. **A tabela "cada skill tem um mecanismo que verifica o resultado" desmente-se na própria
   linha:** `estados-de-interface` é "Verificada por · revisão de PR". Revisão de PR é exatamente a
   camada "orienta" que o README acabou de separar de "impede". `migrations-reversiveis` é dada como
   verificada por `verificar_pr.py`, que checa a existência da seção de rollback e a edição de
   migration antiga — não a reversibilidade, que é o assunto da skill [verificado].
7. **`docs/steering/qualidade.md` e `tests/README.md` repetem as mesmas duas regras de TDD** em
   redação diferente. A ADR-0001 descarta "duplicar o conteúdo nas duas formas" porque "duas cópias
   da mesma regra divergem"; aqui a duplicação já existe dentro do template. O checklist de Impacto
   Arquitetural está em três lugares (`AGENTS.md`, `sdd-processo.md`, `MODELO-plano.md`).
8. **Pós-geração: a lista de onde estão os `<!-- preencher -->` está incompleta.** São 23 marcadores
   no projeto gerado [verificado: `grep -ro`], e o README cita `pyproject.toml`, `tests/README.md`,
   `.kiro/permissions.yaml` e `docs/prd/MODELO-prd.md` — omitindo os **dois de
   `.github/workflows/qualidade.yml`**, que são os mais consequentes (trocar o runner Python pela
   stack real). O número 15 da ADR/plano é histórico e hoje está defasado.
9. **Bullet órfão no Quick start.** "- instala a skill do ciclo SDD a partir do repositório dela."
   aparece depois de uma linha em branco, fora da lista a que pertence [verificado: README linha 208].

## 1.10 MÉDIO · `src/` é prometido e não entregue

O mapa do repositório em `AGENTS.md` (e na constituição canônica) declara
`src/  código-fonte da aplicação`. O template não cria `src/`
[verificado: `ls -d src` no projeto gerado → não existe]. É literalmente o defeito que a v1.1.0
corrigiu para `tests/` — *"O mapa do repositório em `AGENTS.md` prometia `tests/` e o template não
entregava, deixando o agente livre para criar a suíte onde quisesse"* — com teste de regressão para
`tests/` e nenhum para `src/`. Agravante menor: o comentário de `pyproject.toml` fala de "layout
`src/`" enquanto configura `pythonpath = ["."]`.

## 1.11 O que o repositório defende e não verifica

Levantamento contra a lista de mecanismos propostos em `docs/plans/…§2` (sete jobs, cinco "baixo").

| Norma que o scaffold defende | Mecanismo | Situação |
|---|---|---|
| Migration não editada depois de aplicada | `verificar_pr.py` | **feito**, bloqueia |
| Threat-model em spec sensível | `verificar_pr.py` | feito, mas fura no modelo real (§1.2) e faz ruído (§1.4) |
| Rollback declarado no plano | `verificar_pr.py` | feito |
| Evidência colada no plano | `verificar_pr.py` | feito, mas fura (§1.4) |
| Segredo nunca commitado | gitleaks | feito, bloqueia |
| `downgrade` testado, não apenas escrito | job com banco efêmero | **não feito** (previsto, custo médio) |
| Menor privilégio / wildcard em policy IaC | job que sinaliza wildcard | **não feito** (previsto, custo médio) |
| Quatro estados por tela e por consulta | slot na spec + job | **não feito**; `MODELO-spec.md` não tem slot de estados de interface, e a skill afirma que "PR que não trate os quatro não passa em revisão" |
| Protótipo aprovado antes do código | — | declarado difícil de automatizar; não há item de checklist de PR, como o plano sugeria |
| Commits convencionais | `commitlint` | **não feito** (previsto, custo baixo) |
| Cobertura mínima atingida | — | `qualidade.md` exige, nada mede |
| Constituição não editada por projeto | `verificar_constituicao.py` | feito pela metade (§1.7) |
| Governança não se autoedita | hook / permissions / sandbox | **inerte ou não confirmado** (§1.1, §1.3) |
| Placeholder não sobra no projeto gerado | teste + CI | feito, mas cego a `.toml` (§1.6) |
| Workflow do projeto gerado executa | — | **nada verifica**; hoje ele não executa (§1.5) |

---

# Frente 2 · O que existe no mundo

Todos os itens abaixo foram abertos. Data de acesso: 2026-09-29.

## 2.1 GitHub Spec Kit — `[web: github.com/github/spec-kit, templates/commands/constitution.md]`

Instalação `uv tool install specify-cli` + `specify init … --integration <agente>`; o ciclo é um
conjunto de comandos de chat: `/speckit-constitution`, `/speckit-specify`, `/speckit-plan`,
`/speckit-tasks`, `/speckit-implement`, `/speckit-converge`, mais extensões de bug
(`/speckit-bug-assess|fix|test`) e de assessment. Artefatos em `.specify/`.

**Tem constituição, e a versiona melhor que este scaffold.** Fica em
`.specify/memory/constitution.md`, com **SemVer explícito e regra de bump declarada** (MAJOR =
remoção/redefinição incompatível de princípio; MINOR = princípio novo ou guia materialmente
expandido; PATCH = clarificação), um **Sync Impact Report** temporário no topo do arquivo durante a
emenda (versão antiga → nova, princípios modificados/renomeados, seções adicionadas e removidas,
TODOs pendentes), e validação pré-saída: nenhum token entre colchetes sem explicação, linha de
versão coerente com o relatório, datas em ISO, e **princípios "declarative, testable, and free of
vague language"**.

- **O que faz e este scaffold não faz:** versionamento semântico da constituição com critério de
  bump escrito; relatório de impacto por emenda; validação de que o princípio é testável;
  amplitude de agentes suportados por `--integration`.
- **O que este scaffold faz e ele não faz:** verificação **executável** de que a constituição não
  foi adulterada no projeto; arquitetura viva com drift entre diagrama, IaC e compose; camada 0
  organizacional (a constituição do spec-kit é do projeto, não da organização); controles de
  permissão por ferramenta; verificação de normas contra o diff do PR.
- **Diferença é lacuna ou escolha?** O SemVer com regra de bump e o relatório de impacto são
  **lacuna**: o scaffold usa `padrao-v1.0` como string opaca comparada por ordem lexicográfica
  (§1.7). Não há ADR discutindo esquema de versão da constituição.

## 2.2 OpenSpec — `[web: github.com/Fission-AI/OpenSpec]`

npm `@fission-ai/openspec` (Node ≥ 20.19). `openspec init`, `openspec update`,
`openspec config profile`. Diretório `openspec/` com `specs/` (requisitos com cenários, markdown
puro), `changes/` (uma pasta por mudança: `proposal.md`, `specs/`, `design.md`, `tasks.md`) e
`archive/` por data. Comandos de agente `/opsx:explore|propose|apply|archive`, e no perfil expandido
`/opsx:verify`, `/opsx:onboard`, `/opsx:bulk-archive`. Declara suporte a **30+ ferramentas**, com a
sintaxe do comando variando por ferramenta (`/opsx:propose`, `/opsx-propose`, `@opsx-propose`,
`$openspec-propose`).

- **O que faz e este scaffold não faz:** ciclo de vida de spec com **arquivamento explícito por
  data** e um `update` que re-emite as instruções de agente e os slash commands quando a ferramenta
  muda — isto é, trata a divergência de formato entre ferramentas como manutenção contínua, não
  como um arquivo escrito uma vez. O scaffold tem a ideia de "spec como delta arquivável" no
  steering, mas nenhum comando que arquive.
- **O que este scaffold faz e ele não faz:** tudo que é verificação executável (a busca não achou
  `openspec validate` nem checagem de CI); arquitetura viva; permissões.
- **Lacuna ou escolha?** O `update` que re-sincroniza a instalação é **lacuna não considerada**:
  hoje, um projeto gerado pelo sdd-scaffold em julho não tem caminho nenhum para receber a v1.6.0 —
  a ADR-0001 chega a prever um `docs/MIGRACAO-v2.md` que não existe.

## 2.3 Agent Skills (padrão aberto) — `[web: agentskills.io e agentskills.io/specification]`

Isto muda o enquadramento do scaffold. O `SKILL.md` deixou de ser "o maior denominador comum entre
três ferramentas" e virou padrão com **~40 implementações** listadas, entre elas Kiro, Gemini CLI,
Codex/ChatGPT, GitHub Copilot, VS Code, Cursor, opencode, OpenHands, Goose, Junie, Amp, Factory,
Roo Code, Laravel Boost, Pulumi Neo.

A especificação define: `name` (≤64, minúsculas/dígitos/hífen, sem hífen no início ou fim, **sem
hífen duplo**, **tem de casar o nome do diretório**), `description` (≤1024), e os opcionais
`license`, `compatibility` (≤500), `metadata` (mapa string→string, com exemplo usando `version`) e
`allowed-tools` (experimental, ex.: `Bash(git:*) Bash(jq:*) Read`). Convenções de diretório
`scripts/`, `references/`, `assets/`. Progressive disclosure em três estágios com orçamentos
recomendados: metadados ~100 tokens, corpo **< 5000 tokens e < 500 linhas**, recursos sob demanda.
Há **validador oficial**: `skills-ref validate ./my-skill`
[web: github.com/agentskills/agentskills/tree/main/skills-ref].

- **O que o padrão oferece e o scaffold não usa:** `metadata.version` (as quatro skills não
  declaram versão nenhuma, e a `sdd-lifecycle` instalada registra revisão só no `PROCEDENCIA.md`);
  `license`; `compatibility`; `allowed-tools`, que é justamente um mecanismo de permissão **dentro**
  da skill; e `skills-ref validate`, que o CI poderia rodar em vez das asserções de frontmatter
  escritas à mão em `test_quatro_skills_montadas_e_com_frontmatter_valido`.
- **O que o scaffold faz e o padrão não cobre:** a montagem de um corpo único em vários pontos
  (`.claude/skills`, `.codex/skills`, `.kiro/skills` como symlinks) e o pareamento skill ↔ mecanismo
  de verificação. Nada no padrão trata de onde a skill é descoberta, o que é exatamente o motivo dos
  symlinks.
- **Lacuna:** a lista de pontos de montagem está desatualizada em relação ao ecossistema. Cursor,
  Copilot/VS Code, Gemini CLI e opencode leem skills hoje, e o projeto gerado não os monta.
  Também: `test_…frontmatter_valido` afirma `len(fm) < 1024` sobre o frontmatter inteiro, quando o
  limite do padrão é 1024 para o campo `description` — a asserção mede a coisa errada, por sorte no
  lado conservador.

## 2.4 Padrão AGENTS.md — `[web: agents.md]`

Markdown comum, sem schema. **Sem mecanismo de include ou import, sem versionamento e sem limite de
tamanho** na convenção. O que existe é **hierarquia**: vários `AGENTS.md` em subdiretórios, e "o
mais próximo do arquivo editado ganha" (o monorepo da OpenAI usa 88). Mais de 60.000 projetos e 20+
ferramentas.

Isto **confirma a decisão da camada 0**: não há include no padrão, então vendoring era o caminho.
Mas revela uma capacidade do padrão que o scaffold não usa: **`AGENTS.md` aninhado por
subdiretório**. Hoje o scaffold tem só dois regimes, "sempre no contexto" e "por gatilho de skill".
O aninhamento dá um terceiro: premissa sempre carregada **quando se trabalha naquela pasta** — que
é exatamente o que `docs/steering/frontend-ux.md` e `infra-devops.md` querem ser.

## 2.5 tach — `[web: github.com/gauge-sh/tach]`

Verificador de arquitetura como código para Python, em Rust. Arquitetura declarada em `tach.toml`
(módulos, `depends_on`, interfaces públicas, source roots, camadas), `tach init` interativo.
`tach check` valida que os imports reais correspondem às dependências declaradas e **sai não-zero**
em violação; `tach report`, `tach show` (grafo DOT ou web), `tach map` (JSON). Detecta import de
dependência não declarada, chamada cruzada fora da interface pública e ciclo. Integra CI, pre-commit
e VS Code. Adoção incremental por módulos não verificados.

**Este é o achado mais acionável da frente 2.** A "Arquitetura Viva" do scaffold amarra
diagrama × IaC × compose e **nunca olha o código**. Nada impede o código de violar a topologia que o
`mapa.yml` declara: o componente "aplicação" pode importar direto do módulo de dados e os quatro
artefatos continuam verdes. O drift que o README chama de "sintoma mais caro" tem uma quinta
dimensão que o manifesto não cobre — e, ao contrário das outras quatro, esta é comparável
automaticamente com precisão, sem casamento por substring de rótulo.

- **O que tach faz e o scaffold não faz:** verifica a arquitetura contra o **código**, bloqueia, e
  tem grafo gerado a partir da realidade.
- **O que o scaffold faz e tach não faz:** amarra artefatos **não-código** (diagrama, IaC, compose)
  que tach ignora por completo.
- **Lacuna ou escolha?** Lacuna. Nenhuma ADR menciona verificação de dependência de módulo. Os dois
  são complementares, não concorrentes: `tach.toml` declara as arestas entre componentes que o
  `mapa.yml` já nomeia.

## 2.6 Sistema de permissões do Claude Code — `[web: code.claude.com/docs/en/permissions e /settings]`

Já detalhado em §1.1. Os pontos de frente 2 que o autor provavelmente não viu:

- Precedência `deny → ask → allow`, primeira regra que casa decide, **especificidade não muda a
  ordem**, e `allow` não abre exceção em `deny`. É a mesma semântica do `.kiro/permissions.yaml` —
  ou seja, existe um vocabulário comum de permissão emergindo entre ferramentas, e o scaffold
  implementou só o lado do Kiro.
- Regras `Read`/`Edit` usam **sintaxe gitignore** com quatro formas de ancoragem (`//abs`, `~/home`,
  `/relativo-à-origem-do-settings`, `path`/`./path` relativo ao cwd), e em regra `deny`/`ask` um
  padrão de segmento único casa em **qualquer profundidade**.
- Regras `Read`/`Edit` **alcançam o Bash**: `cat`, `head`, `tail`, `sed`, `tee` e os alvos de `>` e
  `<`. Para bloqueio de processo arbitrário existe o sandbox de SO.
- **Existe um tier organizacional de verdade:** `managed-settings.json`, política de MDM, ou
  server-managed settings vindo do console da claude.ai. Nada que o desenvolvedor escreva sobrepõe
  (com exceções de segurança em que o **mais restritivo** ganha). Isso é diretamente relevante à
  pergunta de desenho (§4 abaixo): um canal de política organizacional não sobreponível, que não
  depende de copiar texto para dentro de cada repositório.

## 2.7 Propagação de regra entre muitos repositórios

**`trick77/agents-md-sync`** [web: github.com/trick77/agents-md-sync]. Mantém `AGENTS.md` em muitos
repositórios a partir de um template central. Mecanismo oposto ao do scaffold: **substituição
integral do arquivo**, *"AGENTS.md is tool-owned. It is overwritten on every run."* Composição por
marcadores `<!-- include: NAME.md -->` num esqueleto, e por repositório um addendum local
`.agents/NAME.md` que é **empilhado antes** do fragmento central. Não há bookkeeping de drift:
*"There is no drift bookkeeping — the PR diff of AGENTS.md itself is the record of what changed."*
Abre PR por repositório (`prBranch`), config JSON com `targets`. Sem selo de versão dentro do
arquivo.

**GitHub Copilot** [web: docs.github.com/…/add-repository-custom-instructions]. Três mecanismos
coexistindo: `.github/copilot-instructions.md` (repositório inteiro), `AGENTS.md` em qualquer lugar
com o mais próximo ganhando, e `.github/instructions/NAME.instructions.md` com **frontmatter
`applyTo` por glob de caminho**. Quando os dois se aplicam, *"the instructions from both files are
used"*. Precedência declarada: **pessoal > repositório > organização**. Ou seja, **instruções de
nível de organização existem nativamente** na plataforma, e a recomendação de tamanho para as
instruções de repositório é "no more than 2 pages".

- **O que esses dois têm e o scaffold não tem:** um **caminho de atualização**. O scaffold instala a
  camada 0 no dia da geração e depois só sabe **avisar** que está atrasado (e nem isso, sem
  `--origem`, que nenhum CI passa). O `agents-md-sync` empurra por PR; o Copilot resolve por
  precedência em tempo de leitura, sem cópia alguma.
- **O que o scaffold tem e eles não têm:** detecção de adulteração local — pela metade (§1.7) — e
  independência de plataforma. O modelo do Copilot exige GitHub; o `agents-md-sync` exige que o
  arquivo seja tool-owned, o que mata a edição local legítima.
- Outros tocados só de leve, registrados sem examinar a fundo e portanto **sem entrar como
  referência**: `rulesync`, `agentsync`, `agent-skills-sync-tool`.

## 2.8 Fitness functions de arquitetura — `[web: busca 2026-09-29]`

O vocabulário estabelecido para o que o scaffold chama de "drift check" é **architectural fitness
function**: verificação automatizada, executável no CI, de que uma característica arquitetural ainda
vale. A família de ferramentas por linguagem: ArchUnit (JVM), ArchUnitNET (C#), ArchUnitTS/ts-arch
(TypeScript), konsist (Kotlin), tach (Python), dependency-cruiser e `eslint-plugin-boundaries` (JS).
Padrão dominante: **falhar o PR** quando a regra é violada.

Consequência para o scaffold: a escolha de "nunca bloquear" está fora da norma do campo, e a
justificativa registrada (*"quando um check bloqueia, a primeira reação do time é procurar como
desligá-lo"*) é uma hipótese sobre comportamento, não um resultado observado. Ela é defensável para
o drift **de diagrama** (rótulo, casamento frouxo, julgamento). É muito mais difícil de defender
para drift **de dependência de código**, que é binário. Só examinei este item por busca, não abri
ArchUnit nem dependency-cruiser: **não verificado** além do nível de panorama.

---

# Frente 3 · Análise de lacuna

Cada item traz: o que falta · custo de não ter · custo de resolver · lacuna ou escolha.

## Prioridade ALTA

### A1. Um mecanismo de permissão que funcione no Claude Code

- **Falta:** substituir (ou duplicar) o hook por regras declarativas `permissions.ask`/`deny` em
  `.claude/settings.json`, e um teste que alimente o hook com **caminho absoluto**, como o harness
  faz.
- **Custo de não ter:** o controle mais anunciado do README não existe na prática. Cenário: o agente
  reescreve um princípio do `AGENTS.md` no meio de uma tarefa Tier 1; ninguém é consultado; a
  auditoria seguinte encontra a constituição divergente e o CI reprova sem que ninguém entenda
  quando mudou. Pior que não ter mecanismo: o time acredita que tem.
- **Custo de resolver:** horas. Sete entradas de JSON, e o hook pode ser mantido com
  `os.path.relpath` contra `cwd` (que vem no payload) para quem quiser mensagem customizada.
- **Lacuna**, não escolha. A ADR-0001 e o plano tratam hook, `permissions.yaml` e sandbox como
  equivalentes; a assimetria (o Kiro protege o `.drawio`, o hook não; o hook não cobre Bash) nunca
  foi decidida, só aconteceu.

### A2. Verificar os mecanismos contra os artefatos reais do template

- **Falta:** os testes de `verificar_pr.py` devem **ler** `template/docs/specs/MODELO-spec.md` e
  `MODELO-plano.md` do disco, e afirmar que o modelo intocado é **reprovado** e o preenchido
  **aprovado**. Idem para `.kiro/permissions.yaml` e `.codex/requirements.toml` — pelo menos um
  teste de schema, e um registro de verificação contra a versão instalada da ferramenta.
- **Custo de não ter:** já cobrou (§1.2, §1.6). O padrão se repete três vezes na mesma release:
  teste e verificador compartilhando a premissa errada do código verificado. Cenário concreto: o
  time adota o scaffold, copia o modelo de spec, abre PR que toca `auth`, o CI fica verde, e a
  convicção de que "o portão funciona" se instala.
- **Custo de resolver:** horas por mecanismo. Uma fixture que carrega o modelo do template e o passa
  por `analisar()`.
- **Lacuna.** Nenhuma ADR discute a política de teste dos verificadores.

### A3. O projeto gerado precisa poder rodar o próprio CI

- **Falta:** `template/requirements.txt`; e um job no `ci.yml` do scaffold que **execute** os jobs do
  workflow gerado (ou ao menos `pip install -r requirements.txt && pytest tests/ -q` e
  `python3 scripts/verificar_constituicao.py` e `verificar_pr.py` contra um PR sintético).
- **Custo de não ter:** o primeiro PR de todo projeto gerado falha no primeiro job por um arquivo
  ausente. A primeira impressão do modelo é "o CI que vem no template está quebrado", e o custo real
  é o time desativar o workflow em vez de consertar — exatamente a reação que o README usa para
  justificar não bloquear no drift check.
- **Custo de resolver:** horas. Um arquivo de uma linha e um job de CI de dez.
- **Lacuna.** `ci.yml` exercita o drift check e nada mais dos quatro mecanismos.

## Prioridade MÉDIA

### M1. Verificação de arquitetura contra o código (a quinta dimensão do drift)

- **Falta:** ligar os componentes do `mapa.yml` a fronteiras de módulo verificáveis no código —
  `tach.toml` para stack Python, `dependency-cruiser` para JS/TS, ArchUnit para JVM — e um campo novo
  no manifesto (`modulo_codigo:`) para fechar o laço.
- **Custo de não ter:** o `mapa.yml` pode estar perfeitamente sincronizado enquanto o código viola a
  topologia que ele descreve. Cenário: o agente resolve um requisito importando direto da camada de
  dados; diagrama, IaC e compose seguem corretos; o drift fica invisível até a primeira tentativa de
  extrair um serviço.
- **Custo de resolver:** dias. É desenho novo (qual ferramenta por stack, como o manifesto
  referencia módulo de código, se bloqueia) mais uma skill e uma ADR.
- **Lacuna**, não escolha: o assunto não aparece em nenhuma ADR nem no plano.

### M2. Caminho de atualização para projetos já gerados

- **Falta:** o `docs/MIGRACAO-*.md` que a própria ADR-0001 prevê, e um comando de atualização
  (`criar_projeto.py --atualizar` ou script à parte) que traga camada 0, skills e scripts para um
  projeto existente.
- **Custo de não ter:** todo projeto gerado é um retrato congelado. A ADR-0001 nomeia o risco —
  *"uma decisão nova da NUARQ não alcança nenhum dos projetos que já nasceram"* — e a camada 0
  resolveu metade: sabe declarar a versão, não sabe adotar a nova. Seis releases saíram hoje;
  nenhum projeto gerado antes delas tem como recebê-las. Cenário: `sgd-catalogo-nuvem`, citado na
  ADR como rodando isso em produção.
- **Custo de resolver:** dias. O `openspec update` e o `agents-md-sync` mostram dois desenhos
  possíveis (re-emissão tool-owned vs PR por repositório).
- **Lacuna reconhecida e não endereçada**: a ADR a registra como consequência negativa e o item nunca
  entrou em release.

### M3. Versionar a constituição de verdade

- **Falta:** SemVer com regra de bump escrita (o spec-kit tem), comparação de **conteúdo** contra a
  origem publicada em vez de comparação de nome de arquivo, e ordenação de versão que não quebre em
  `v10.0`. E `--origem` no job `governanca` do template, senão o mecanismo de defasagem nunca roda.
- **Custo de não ter:** três falhas medidas em §1.7, e uma quarta: adulteração coordenada dos dois
  arquivos passa em silêncio. O portão que o README descreve como "reprova porque é compartilhada"
  hoje só detecta quem edita **um** dos dois lados.
- **Custo de resolver:** horas para ordenação e diagnóstico de `--origem`; dias para comparação de
  conteúdo contra origem remota (precisa decidir onde a constituição publicada mora e como o CI a
  alcança).
- **Lacuna.** A escolha registrada foi "inline em vez de include", que continua correta (§4); a
  fragilidade da *verificação* não foi decidida.

### M4. O drift check não deve poder bloquear por acidente, nem ficar verde por rótulo degenerado

- **Falta:** `try/except` em torno de `verificar()` reportando `mapa.yml` inválido como divergência
  (mantendo exit 0), validação das chaves obrigatórias, casamento de rótulo por igualdade normalizada
  ou por comprimento mínimo, e a direção que falta (nó do diagrama sem componente).
- **Custo de não ter:** um `mapa.yml` mal editado derruba o CI com traceback, contradizendo três
  documentos; e `drawio_label: "a"` silencia o check inteiro. Nas duas pontas o time aprende a
  desconfiar do relatório, que é o desfecho que a skill `arquitetura-viva` lista como erro comum
  ("o script vira decoração e o manifesto apodrece").
- **Custo de resolver:** horas.
- **Lacuna.**

### M5. Fechar os furos de `verificar_pr.py`

- **Falta:** excluir `docs/**`, `CHANGELOG.md` e `README*` da varredura de superfície sensível;
  casar diretório em vez de palavra dentro de nome de arquivo; buscar `EVIDENCIA` **dentro** da seção
  de evidências; tratar `- [ ]` como resíduo; corrigir o ponteiro morto da mensagem (`seguranca.md` →
  skill `threat-model`).
- **Custo de não ter:** o mecanismo está no caminho de se tornar ruído, que é o desfecho que a
  release 1.4.0 diz querer evitar. Um time que recebe aviso de threat-model num PR de documentação
  aprende a fechar todos os avisos.
- **Custo de resolver:** horas.
- **Lacuna**, com precedente explícito: o CHANGELOG [1.4.0] já descreve esta classe de defeito.

### M6. Reconciliar `sdd-processo.md` com as quatro camadas

- **Falta:** atualizar a árvore `docs/` (falta `constituicao/` e `prd/`; `specs/` ainda diz que
  guarda PRD), trocar "consulte `docs/steering/arquitetura.md` para o procedimento" por "skill
  `arquitetura-viva`", e resolver a numeração de fase (definir ou remover: hoje "Fase 1/3/6" não
  existem em nenhum arquivo do projeto gerado, e 3 e 6 nomeiam o mesmo momento).
- **Custo de não ter:** é o arquivo de steering **maior** (85 linhas) e o de gatilho mais largo
  ("sempre que for criar ou alterar código"), portanto o mais lido. Ele manda o agente para lugares
  que não têm mais o conteúdo.
- **Custo de resolver:** horas.
- **Lacuna.** A 1.6.0 caçou ponteiros mortos nos modelos e não no steering.

### M7. Cobrir mais pontos de montagem de skill, e usar o validador do padrão

- **Falta:** montar também `.cursor/`, `.github/skills` (ou o caminho que o Copilot usa),
  `.gemini/skills` e `.opencode/`, conforme cada ferramenta documenta; declarar `metadata.version` e
  `license` nas quatro skills; rodar `skills-ref validate` no CI em vez de asserções de frontmatter
  escritas à mão; corrigir a asserção `len(fm) < 1024`, que mede o frontmatter inteiro quando o
  limite do padrão é para `description`.
- **Custo de não ter:** o argumento central de venda é "sem lock-in", e a montagem cobre três
  ferramentas de um ecossistema de ~40 implementações do padrão. Um time que use Cursor ou Copilot
  recebe as skills e nenhuma delas é descoberta.
- **Custo de resolver:** horas por ferramenta, mais a pesquisa de qual caminho cada uma lê — que é
  exatamente o tipo de verificação que a nota do `ANTIGRAVITY.md` exige e que precisa ser feita
  contra o produto, não contra a documentação.
- **Lacuna**, criada pelo ecossistema ter andado: em 2026-09-29 a afirmação "maior denominador comum
  entre três ferramentas" está desatualizada para melhor.

## Prioridade BAIXA

### B1. `src/` prometido e não entregue, e `requirements.txt` ausente da árvore do README
Horas. Ver §1.10 e §1.5. Merece teste de regressão espelhando o de `tests/`.

### B2. `.toml`/`.json` fora da substituição de placeholder e fora dos dois verificadores
Horas. Ver §1.6. A correção mais durável é remover a allowlist de extensão dos verificadores.

### B3. Contradições de texto
Horas. Checklist de pós-geração (§1.9.1) primeiro, porque contradiz a release do dia; depois a
contagem da ADR, o bullet órfão, "três controles / quatro linhas", a coluna "verificada por · revisão
de PR", a duplicação TDD entre `qualidade.md` e `tests/README.md`, e a lista incompleta de
`<!-- preencher -->`.

### B4. Mecanismos previstos e não feitos
Dias cada. `commitlint` (baixo), wildcard em policy IaC (médio), par `upgrade`/`downgrade` em banco
efêmero (médio), slot de quatro estados de interface em `MODELO-spec.md` (baixo, e a skill hoje
afirma um portão que não existe). **Escolha parcialmente registrada:** o plano os lista como
propostos; nenhuma ADR os descarta.

### B5. Artefatos de SO na árvore de trabalho
Sete `.DS_Store` estão no disco, inclusive `template/.DS_Store` e `template/skills/.DS_Store`
[verificado: `find`]. Não estão versionados [verificado: `git ls-files | grep -i ds_store` → vazio] e
o gerador os ignora, então não vazam para o projeto gerado. Mencionado só para fechar o item: o
CHANGELOG [1.1.0] diz "cinco `.DS_Store` foram removidos do template", e eles voltaram no disco local
— o que é normal no macOS e está corretamente coberto pelo `.gitignore`. **Não é defeito.**

---

# Frente 4 · A pergunta de desenho: propagar regra compartilhada entre muitos repositórios

**A escolha de inline em vez de include está certa, e a pesquisa reforça.** O padrão AGENTS.md não
define include nem import [web: agents.md] e não tem versionamento nem limite de tamanho. Qualquer
mecanismo de include seria de uma ferramenta só, e reintroduziria o lock-in. A decisão registrada em
[1.3.0] e no apêndice da ADR-0001 sobrevive à auditoria.

**O que está fraco não é a escolha, é a verificação e o caminho de volta.** Três abordagens
observadas, com o que cada uma resolve melhor:

| Abordagem | Como propaga | O que resolve melhor que o scaffold | O que perde |
|---|---|---|---|
| **Vendoring com verificação** (este scaffold) | cópia no ato da geração + CI compara inline × canônico | independente de plataforma; detecta edição de **um** lado | não propaga atualização; adulteração coordenada passa; versão comparada por nome, lexicograficamente |
| **`agents-md-sync`** [web] | template central expandido por `<!-- include: -->`, arquivo **tool-owned** sobrescrito a cada run, PR por repositório | **empurra** a atualização; addendum local por repositório empilhado sobre o fragmento central; o diff do PR é o registro da mudança | o arquivo deixa de ser editável no repositório; sem selo de versão |
| **Tier organizacional da plataforma** (Copilot: pessoal > repositório > **organização**; Claude Code: `managed-settings.json`/MDM/server-managed, não sobreponível) [web] | **não copia nada**; resolve por precedência na leitura | mudança organizacional chega no mesmo dia, a todos os repositórios, sem PR nenhum; no Claude Code o desenvolvedor **não pode** sobrepor | amarra à plataforma; cobre uma ferramenta por vez |

**Existe abordagem melhor? Sim, e é composta, não substituta.** Recomendação:

1. **Manter o inline como fonte de contexto** — é o que garante que a premissa entra em todo turno em
   qualquer ferramenta. Não mexer.
2. **Trocar o que a verificação compara.** Hoje ela compara duas cópias locais, e por isso a
   adulteração coordenada passa (§1.7). O portão precisa comparar o bloco inline contra a **origem
   publicada** (URL bruta, submódulo, ou artefato de release com hash), não contra o vizinho de
   disco. Um hash SHA-256 da constituição canônica gravado no marcador
   (`<!-- constituicao:inicio padrao-v1.0 sha256:… -->`) já eleva o custo de adulteração de
   "editar dois arquivos" para "editar dois arquivos e recalcular um hash que o CI confere contra a
   origem".
3. **Adotar SemVer com regra de bump declarada**, como o spec-kit [web], e um relatório de impacto
   por emenda. Isso substitui a ordenação lexicográfica por comparação correta e dá ao projeto
   atrasado a informação de **quanto** ele está atrasado: PATCH pode esperar, MAJOR não.
4. **Empurrar, não só avisar.** Um comando que abra PR nos projetos-alvo com o bloco novo, no espírito
   do `agents-md-sync` — mas preservando a edição local por seção addendum, para não tornar o
   `AGENTS.md` tool-owned. Sem isso, a camada 0 é um detector de defasagem sem remédio.
5. **Usar o tier organizacional da plataforma para o que é `impede`, não para o que é `orienta`.** A
   constituição é texto e continua vendorizada; mas "a governança não se autoedita" é permissão, e
   permissão tem canal organizacional real: `managed-settings.json` / MDM / server-managed settings
   no Claude Code [web], onde nada que o desenvolvedor escreva sobrepõe. Publicar as regras
   `Edit(...)` de proteção de governança por esse canal resolve simultaneamente A1 e a propagação:
   uma regra da NUARQ passa a valer em todos os repositórios sem depender de arquivo dentro de
   nenhum deles.

Em uma frase: **o inline resolveu o carregamento e não resolveu a distribuição.** A camada 0 hoje é
um selo de versão com um comparador frágil; falta o canal que entrega a versão nova e o canal de
política que não pede licença ao repositório.

---

# O que não consegui verificar

- **`.kiro/permissions.yaml` e `.codex/requirements.toml` contra os produtos instalados.** Não tenho
  Kiro nem Codex CLI nesta máquina. As divergências de §1.3 vêm da documentação pública e podem
  estar erradas se a pesquisa de harnesses achou nomes internos não documentados. **A verificação
  precisa ser feita contra o binário**, e registrada, no mesmo padrão da nota do `ANTIGRAVITY.md`.
- **Se Kiro e Antigravity leem `AGENTS.md` nativamente** (README, tabela "verificado em 2026-09-29").
  Só pude confirmar o lado do Claude Code e, por documentação, Copilot/Codex.
- **Se o hook está inerte em sessão real.** A cadeia (o harness envia absoluto → `fnmatch` falha) está
  documentada e medida em cima do script, mas não executei o Claude Code com o hook instalado num
  projeto gerado. Confirmação de um minuto: gerar, abrir sessão, pedir para editar o `AGENTS.md`.
- **"Mais de 1000 testes automatizados e 35+ ADRs"** do projeto de origem (README, "Origem"). O
  repositório `sgd-catalogo-nuvem` não está aqui.
- **A `sdd-lifecycle` em si.** Clonou e instalou corretamente [verificado], mas não auditei o
  conteúdo dela; ela é o que conduz o ciclo e não está sob a governança deste repositório.
- **ArchUnit, dependency-cruiser e os demais itens de §2.8** só foram vistos por busca, não abertos.
  Entram como panorama, não como referência examinada.
- **`rulesync`, `agentsync`, `agent-skills-sync-tool`** apareceram na busca de §2.7 e não foram
  abertos; por isso não entram como referência.
- **Orçamento de pesquisa.** 19 consultas web, dentro do limite de ~20. Categorias que ficaram de
  fora por isso: sandbox de agente a nível de SO, formatos de policy-as-code (OPA/Conftest) aplicados
  a governança de agente, e governança de engenharia com IA em organizações grandes — as buscas
  nesta última voltaram material de marketing sem artefato examinável, e preferi não citar o que não
  pude abrir.
