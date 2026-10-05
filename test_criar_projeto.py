"""Testes do gerador de projetos a partir do template."""
import importlib.util
import os
import subprocess
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "criar_projeto", Path(__file__).resolve().parent / "criar_projeto.py"
)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)


def test_gera_projeto_sem_placeholders_residuais(tmp_path):
    destino = mod.gerar(nome="projeto-exemplo", destino=tmp_path,
                        descricao="Projeto de exemplo.", stack="Python 3.12 + FastAPI",
                        deps="requirements.txt")
    assert destino == tmp_path / "projeto-exemplo"
    assert (destino / "AGENTS.md").is_file()
    assert (destino / "docs" / "steering" / "sdd-processo.md").is_file()
    PLACEHOLDERS = ("{{NOME_PROJETO}}", "{{DESCRICAO}}", "{{STACK}}", "{{ARQUIVO_DEPENDENCIAS}}", "{{DATA}}")
    residuais = [
        p for p in destino.rglob("*")
        if p.is_file() and p.suffix in {".md", ".yml", ".yaml", ".py", ".tf"}
        and any(ph in p.read_text(encoding="utf-8") for ph in PLACEHOLDERS)
    ]
    assert residuais == [], f"placeholders residuais em: {residuais}"


def test_git_inicializado_com_commit(tmp_path):
    destino = mod.gerar(nome="proj-git", destino=tmp_path, descricao="d",
                        stack="s", deps="requirements.txt")
    log = subprocess.run(["git", "-C", str(destino), "log", "--oneline"],
                         capture_output=True, text=True, check=True)
    assert "estrutura inicial" in log.stdout


def test_recusa_destino_existente(tmp_path):
    (tmp_path / "ocupado").mkdir()
    try:
        mod.gerar(nome="ocupado", destino=tmp_path, descricao="d", stack="s",
                  deps="requirements.txt")
        raise AssertionError("deveria ter recusado destino existente")
    except FileExistsError:
        pass


def test_nao_copia_artefatos_de_so_nem_cache(tmp_path):
    """Regressão: .DS_Store tem suffix '' e '' está em EXTENSOES_TEXTO, então o
    gerador tentava decodificá-lo como UTF-8 e estourava. Nenhum artefato de SO
    ou cache deve chegar ao projeto gerado."""
    destino = mod.gerar(nome="proj-limpo", destino=tmp_path, descricao="d",
                        stack="s", deps="requirements.txt")
    lixo = [str(p.relative_to(destino)) for p in destino.rglob("*")
            if p.name == ".DS_Store" or p.name == "__pycache__" or p.suffix == ".pyc"]
    assert lixo == [], f"artefatos indevidos no projeto gerado: {lixo}"


def test_ponteiros_de_ferramenta_existem_e_apontam_para_agents(tmp_path):
    """AGENTS.md é a fonte única. Os ponteiros precisam existir e referenciá-lo.
    ANTIGRAVITY.md NÃO deve existir: o Antigravity lê apenas AGENTS.md e GEMINI.md."""
    destino = mod.gerar(nome="proj-ponteiros", destino=tmp_path, descricao="d",
                        stack="s", deps="requirements.txt")
    assert not (destino / "ANTIGRAVITY.md").exists(), \
        "ANTIGRAVITY.md é inerte — o Antigravity não lê esse nome"
    for ponteiro in ("CLAUDE.md", "GEMINI.md"):
        caminho = destino / ponteiro
        assert caminho.is_file(), f"ponteiro ausente: {ponteiro}"
        assert "AGENTS.md" in caminho.read_text(encoding="utf-8"), \
            f"{ponteiro} não aponta para AGENTS.md"


def test_diretorio_de_testes_prometido_pelo_mapa_existe(tmp_path):
    """O mapa do repositório em AGENTS.md promete tests/ — o template deve entregá-lo."""
    destino = mod.gerar(nome="proj-tests", destino=tmp_path, descricao="d",
                        stack="s", deps="requirements.txt")
    assert (destino / "tests").is_dir(), "tests/ prometido no mapa do repo e ausente no template"


def test_agents_md_cabe_no_limite_de_contexto_do_codex(tmp_path):
    """O Codex trunca documentos de projeto em project_doc_max_bytes = 32768."""
    destino = mod.gerar(nome="proj-limite", destino=tmp_path, descricao="d",
                        stack="s", deps="requirements.txt")
    tamanho = (destino / "AGENTS.md").stat().st_size
    assert tamanho < 30000, f"AGENTS.md com {tamanho} bytes — perto do limite de 32768 do Codex"


def test_suite_do_projeto_gerado_roda_sem_pythonpath_manual(tmp_path):
    """Regressão empírica: um agente construiu uma feature completa sobre este
    scaffold e a suíte só rodava com PYTHONPATH=. na frente. O job de CI do
    template chama `pytest tests/` direto, então quebraria. O template precisa
    declarar onde o código-fonte mora."""
    destino = mod.gerar(nome="proj-pythonpath", destino=tmp_path, descricao="d",
                        stack="s", deps="requirements.txt")
    pyproject = destino / "pyproject.toml"
    assert pyproject.is_file(), "template não emite pyproject.toml"
    conteudo = pyproject.read_text(encoding="utf-8")
    assert "[tool.pytest.ini_options]" in conteudo, "sem configuração de pytest"
    assert "pythonpath" in conteudo, "pytest não sabe onde o código-fonte mora"


def test_skills_montadas_para_as_tres_ferramentas(tmp_path):
    """Um corpo de skill, N pontos de montagem. Claude Code lê .claude/skills,
    Codex lê .codex/skills e Kiro lê .kiro/skills; os três apontam para o mesmo
    diretório para que não existam três cópias divergindo."""
    destino = mod.gerar(nome="proj-skills", destino=tmp_path, descricao="d",
                        stack="s", deps="requirements.txt")
    canonico = destino / "skills" / "arquitetura-viva" / "SKILL.md"
    assert canonico.is_file(), "skill canônica ausente"
    for ferramenta in (".claude", ".codex", ".kiro"):
        pasta = destino / ferramenta / "skills"
        assert pasta.is_symlink(), (
            f"{ferramenta}/skills virou cópia, não ponto de montagem. Copiar significa que "
            "editar a skill em um lugar deixa os outros dois desatualizados em silêncio, "
            "que é exatamente o problema que o corpo único existe para evitar."
        )
        montagem = pasta / "arquitetura-viva" / "SKILL.md"
        assert montagem.is_file(), f"{ferramenta}/skills não resolve para a skill"


def test_hook_protege_governanca_e_libera_codigo(tmp_path):
    """A mesma regra que o Kiro faz por permissions.yaml e o Codex por sandbox:
    o agente escreve código, não reescreve a constituição por conta própria."""
    import json as _json
    import subprocess as _sp
    destino = mod.gerar(nome="proj-hook", destino=tmp_path, descricao="d",
                        stack="s", deps="requirements.txt")
    script = destino / "scripts" / "proteger_governanca.py"
    assert script.is_file(), "hook ausente no projeto gerado"
    assert (destino / ".claude" / "settings.json").is_file(), "hook não registrado"

    def decidir(caminho):
        evento = _json.dumps({"tool_name": "Edit", "tool_input": {"file_path": caminho}})
        saida = _sp.run(["python3", str(script)], input=evento, capture_output=True,
                        text=True, check=True).stdout.strip()
        return _json.loads(saida)["hookSpecificOutput"]["permissionDecision"] if saida else None

    for protegido in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", "docs/adr/0001-x.md",
                      "Arquitetura/mapa.yml", ".github/workflows/qualidade.yml"):
        assert decidir(protegido) == "ask", f"{protegido} deveria exigir aprovação"

    for livre in ("src/app.py", "tests/unidade/test_app.py", "docs/specs/2026-01-01-x.md",
                  "docs/plans/2026-01-01-x.md", "README.md"):
        assert decidir(livre) is None, f"{livre} não deveria ser bloqueado"


def test_constituicao_organizacional_inline_e_verificavel(tmp_path):
    """Camada 0: a constituição vale para todos os projetos, então precisa estar
    SEMPRE no contexto, e não num arquivo lido sob demanda. Ela fica inline no
    AGENTS.md entre marcadores; o arquivo canônico existe para o CI conferir que
    o bloco não divergiu."""
    import subprocess as _sp
    destino = mod.gerar(nome="proj-const", destino=tmp_path, descricao="d",
                        stack="s", deps="requirements.txt")
    canonico = destino / "docs" / "constituicao" / "padrao-v1.0.md"
    assert canonico.is_file(), "constituição canônica ausente"

    agents = (destino / "AGENTS.md").read_text(encoding="utf-8")
    assert "<!-- constituicao:inicio" in agents and "<!-- constituicao:fim -->" in agents, \
        "AGENTS.md não delimita o bloco da constituição"
    bloco = agents.split("<!-- constituicao:inicio", 1)[1].split("-->", 1)[1]
    bloco = bloco.split("<!-- constituicao:fim -->", 1)[0].strip()
    assert bloco == canonico.read_text(encoding="utf-8").strip(), \
        "o bloco inline divergiu do arquivo canônico"

    verificador = destino / "scripts" / "verificar_constituicao.py"
    assert verificador.is_file(), "verificador ausente"
    ok = _sp.run(["python3", str(verificador), "--raiz", str(destino)],
                 capture_output=True, text=True)
    assert ok.returncode == 0, f"verificador reprovou projeto recém-gerado: {ok.stdout}{ok.stderr}"

    # adulterar o bloco inline deve ser detectado
    (destino / "AGENTS.md").write_text(
        agents.replace("Português do Brasil", "Klingon"), encoding="utf-8")
    ruim = _sp.run(["python3", str(verificador), "--raiz", str(destino)],
                   capture_output=True, text=True)
    assert ruim.returncode != 0, "adulteração da constituição passou despercebida"


def test_hook_e_permissoes_protegem_a_constituicao(tmp_path):
    """A constituição é compartilhada: um projeto não a edita por conta própria."""
    import json as _json, subprocess as _sp
    destino = mod.gerar(nome="proj-prot", destino=tmp_path, descricao="d",
                        stack="s", deps="requirements.txt")
    script = destino / "scripts" / "proteger_governanca.py"
    evento = _json.dumps({"tool_name": "Write",
                          "tool_input": {"file_path": "docs/constituicao/padrao-v1.0.md"}})
    saida = _sp.run(["python3", str(script)], input=evento, capture_output=True,
                    text=True, check=True).stdout.strip()
    assert saida, "o hook deixou a constituição ser reescrita sem aprovação"
    regras = (destino / ".kiro" / "permissions.yaml").read_text(encoding="utf-8")
    assert "docs/constituicao/**" in regras, "permissions.yaml não cobre a constituição"


def _verificador_pr(destino):
    """Carrega o verificador de PR do projeto gerado como módulo."""
    import importlib.util as _il
    import sys as _sys
    caminho = destino / "scripts" / "verificar_pr.py"
    assert caminho.is_file(), "verificar_pr.py ausente no projeto gerado"
    spec = _il.spec_from_file_location("verificar_pr", caminho)
    m = _il.module_from_spec(spec)
    # dataclasses resolve o módulo por sys.modules; sem registrar, o decorator falha.
    _sys.modules["verificar_pr"] = m
    spec.loader.exec_module(m)
    return m


def test_pr_que_altera_migration_ja_aplicada_reprova(tmp_path):
    """Editar migration que já rodou em produção corrompe o histórico de schema.
    É inequívoco e perigoso, então bloqueia."""
    v = _verificador_pr(mod.gerar(nome="p1", destino=tmp_path, descricao="d", stack="s",
                                  deps="requirements.txt"))
    achados = v.analisar(
        alterados=["migrations/0001_inicial.py"],
        conteudos={},
        migrations_na_base={"migrations/0001_inicial.py"},
    )
    bloqueios = [a for a in achados if a.bloqueia]
    assert bloqueios, "alterar migration já aplicada deveria bloquear"
    assert "0001_inicial" in bloqueios[0].mensagem

    # criar migration nova não bloqueia
    ok = v.analisar(alterados=["migrations/0002_nova.py"], conteudos={},
                    migrations_na_base={"migrations/0001_inicial.py"})
    assert not [a for a in ok if a.bloqueia]


def test_mudanca_sensivel_exige_threat_model_na_spec(tmp_path):
    """Spec que toca auth, upload, entrada externa ou IaC responde às 5 perguntas."""
    v = _verificador_pr(mod.gerar(nome="p2", destino=tmp_path, descricao="d", stack="s",
                                  deps="requirements.txt"))
    sem = v.analisar(
        alterados=["src/auth/login.py", "docs/specs/2026-01-01-login.md"],
        conteudos={"docs/specs/2026-01-01-login.md": "# Login\n\nFaz login."},
        migrations_na_base=set(),
    )
    assert any("threat-model" in a.mensagem.lower() for a in sem), \
        "mudança em auth sem threat-model deveria ser sinalizada"

    com = v.analisar(
        alterados=["src/auth/login.py", "docs/specs/2026-01-01-login.md"],
        conteudos={"docs/specs/2026-01-01-login.md":
                   "# Login\n\n## Threat-model\n\n1. Entrada não confiável? Sim, mitigado por…"},
        migrations_na_base=set(),
    )
    assert not any("threat-model" in a.mensagem.lower() for a in com)


def test_plano_sem_rollback_e_sem_evidencia_e_sinalizado(tmp_path):
    v = _verificador_pr(mod.gerar(nome="p3", destino=tmp_path, descricao="d", stack="s",
                                  deps="requirements.txt"))
    achados = v.analisar(
        alterados=["migrations/0002_x.py", "src/app.py", "docs/plans/2026-01-01-x.md"],
        conteudos={"docs/plans/2026-01-01-x.md": "# Plano\n\nFazer a coisa."},
        migrations_na_base=set(),
    )
    texto = " ".join(a.mensagem.lower() for a in achados)
    assert "rollback" in texto, "mudança de schema sem rollback declarado deveria avisar"
    assert "evidência" in texto, "plano sem evidência colada deveria avisar"
    assert not [a for a in achados if a.bloqueia], "avisos não devem bloquear"


def test_superficie_sensivel_nao_dispara_dentro_de_palavra(tmp_path):
    """Regressão: 'iam' casava no meio de LEIAME.md e o PR de documentação recebia
    aviso de threat-model. Aviso que dispara em arquivo irrelevante ensina o time a
    ignorar todos os avisos."""
    v = _verificador_pr(mod.gerar(nome="p4", destino=tmp_path, descricao="d", stack="s",
                                  deps="requirements.txt"))
    for inocente in ["LEIAME.md", "docs/miami.md", "src/authorship_display.py",
                     "src/relatorio.py", "CHANGELOG.md"]:
        achados = v.analisar(alterados=[inocente], conteudos={}, migrations_na_base=set())
        assert not any("threat-model" in a.mensagem.lower() for a in achados), \
            f"{inocente} não deveria disparar threat-model"

    for real in ["src/auth/login.py", "infra/cloud/modules/iam/main.tf",
                 "src/authentication.py", "api/upload.py", "src/rbac.py"]:
        achados = v.analisar(alterados=[real], conteudos={}, migrations_na_base=set())
        assert any("threat-model" in a.mensagem.lower() for a in achados), \
            f"{real} deveria disparar threat-model"


def test_quatro_skills_montadas_e_com_frontmatter_valido(tmp_path):
    """Cada skill declara nome e descrição, e a descrição diz QUANDO usar, sem
    resumir o procedimento: descrição que resume o fluxo vira atalho que o agente
    segue no lugar de ler a skill."""
    destino = mod.gerar(nome="proj-4sk", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt")
    esperadas = {"arquitetura-viva", "threat-model", "migrations-reversiveis",
                 "estados-de-interface"}
    presentes = {p.name for p in (destino / "skills").iterdir() if p.is_dir()}
    assert esperadas <= presentes, f"faltam skills: {esperadas - presentes}"

    for nome in esperadas:
        texto = (destino / "skills" / nome / "SKILL.md").read_text(encoding="utf-8")
        assert texto.startswith("---\n"), f"{nome}: sem frontmatter"
        fm = texto.split("---")[1]
        assert f"name: {nome}" in fm, f"{nome}: name não bate com o diretório"
        assert "description:" in fm, f"{nome}: sem description"
        assert len(fm) < 1024, f"{nome}: frontmatter acima do limite"
        assert "Use quando" in fm, f"{nome}: a descrição não diz quando usar"
        # cada skill degrada graciosamente: aponta o steering local e traz default
        assert "docs/steering/" in texto, f"{nome}: não aponta os parâmetros do projeto"
        assert "não existir" in texto, f"{nome}: não declara o comportamento sem o steering"

        # montada nas três ferramentas
        for ferramenta in (".claude", ".codex", ".kiro"):
            assert (destino / ferramenta / "skills" / nome / "SKILL.md").is_file(), \
                f"{nome} não visível em {ferramenta}"


def test_steering_ficou_so_com_parametro_de_projeto(tmp_path):
    """Depois da extração, o steering dos domínios convertidos não repete o
    procedimento que agora vive na skill."""
    destino = mod.gerar(nome="proj-st", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt")
    st = destino / "docs" / "steering"
    seguranca = (st / "seguranca.md").read_text(encoding="utf-8")
    assert "threat-model" in seguranca, "steering deveria apontar a skill"
    assert "1. Há **entrada não confiável**" not in seguranca, \
        "as cinco perguntas ainda estão duplicadas no steering"
    frontend = (st / "frontend-ux.md").read_text(encoding="utf-8")
    assert "estados-de-interface" in frontend
    assert "loading" not in frontend.lower() or "preencher" in frontend
    infra = (st / "infra-devops.md").read_text(encoding="utf-8")
    assert "migrations-reversiveis" in infra
    assert "NUNCA edite migrations antigas" not in infra, \
        "a regra de migration ainda está duplicada no steering"


def test_secao_apenas_mencionada_nao_conta_como_preenchida(tmp_path):
    """Defeito encontrado ao revisar os modelos: o MODELO-spec cita 'threat-model'
    num comentário de orientação, e o MODELO-plano traz a seção de rollback vazia.
    Buscar a palavra fazia o verificador aprovar um documento intocado."""
    v = _verificador_pr(mod.gerar(nome="p5", destino=tmp_path, descricao="d", stack="s",
                                  deps="requirements.txt"))

    spec_do_modelo = (
        "# Spec\n\n## Riscos e mitigações\n\n"
        "<!-- Para specs que tocam auth, responder ao checklist de threat-model\n"
        "     (skills/threat-model) com um parágrafo por sim. -->\n\n- ...\n"
    )
    achados = v.analisar(alterados=["src/auth/x.py", "docs/specs/2026-01-01-x.md"],
                         conteudos={"docs/specs/2026-01-01-x.md": spec_do_modelo},
                         migrations_na_base=set())
    assert any("threat-model" in a.mensagem.lower() for a in achados), \
        "spec copiada do modelo e não preenchida deveria ser sinalizada"

    spec_respondida = (
        "# Spec\n\n## Threat-model\n\n"
        "1. Entrada não confiável? Sim. O payload é validado contra schema na borda.\n"
        "2. Auth alterada? Não.\n"
    )
    ok = v.analisar(alterados=["src/auth/x.py", "docs/specs/2026-01-01-x.md"],
                    conteudos={"docs/specs/2026-01-01-x.md": spec_respondida},
                    migrations_na_base=set())
    assert not any("threat-model" in a.mensagem.lower() for a in ok)

    plano_vazio = "# Plano\n\n## Estratégia de rollback\n\n<!-- Obrigatória se há schema. -->\n"
    achados2 = v.analisar(alterados=["migrations/0009_x.py", "docs/plans/2026-01-01-x.md"],
                          conteudos={"docs/plans/2026-01-01-x.md": plano_vazio},
                          migrations_na_base=set())
    assert any("rollback" in a.mensagem.lower() for a in achados2), \
        "seção de rollback vazia deveria ser sinalizada"


def test_instala_skill_externa_a_partir_de_origem_local(tmp_path):
    """A sdd-lifecycle vive em repositório próprio e é instalada na geração."""
    import subprocess as _sp
    origem = tmp_path / "origem-skill"
    (origem / "docs").mkdir(parents=True)
    (origem / "SKILL.md").write_text("---\nname: sdd-lifecycle\ndescription: x\n---\n# Ciclo\n",
                                     encoding="utf-8")
    (origem / "docs" / "exemplo.md").write_text("exemplo", encoding="utf-8")
    for cmd in (["git", "init", "-q", "-b", "main"], ["git", "add", "-A"],
                ["git", "-c", "user.name=t", "-c", "user.email=t@e.com",
                 "commit", "-q", "-m", "inicial"]):
        _sp.run(cmd, cwd=origem, check=True, capture_output=True)

    destino = mod.gerar(nome="proj-skill-ext", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=str(origem), versao_ciclo="")
    instalada = destino / "skills" / "sdd-lifecycle" / "SKILL.md"
    assert instalada.is_file(), "sdd-lifecycle não foi instalada"
    assert "name: sdd-lifecycle" in instalada.read_text(encoding="utf-8")
    proc = destino / "skills" / "sdd-lifecycle" / "PROCEDENCIA.md"
    assert proc.is_file(), "sem registro de procedência"
    assert str(origem) in proc.read_text(encoding="utf-8")
    # visível nas três ferramentas pelo mesmo ponto de montagem
    for f in (".claude", ".codex", ".kiro"):
        assert (destino / f / "skills" / "sdd-lifecycle" / "SKILL.md").is_file()


def test_geracao_nao_falha_quando_a_origem_esta_inacessivel(tmp_path):
    """Sem rede, o projeto continua nascendo: a skill externa é um acréscimo, e
    um gerador que quebra por rede indisponível falha no pior momento."""
    destino = mod.gerar(nome="proj-sem-rede", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt",
                        origem_ciclo="https://example.invalid/nao-existe.git")
    assert (destino / "AGENTS.md").is_file(), "a geração deveria ter concluído"
    assert not (destino / "skills" / "sdd-lifecycle").exists()
    aviso = destino / "skills" / "SKILL-CICLO-AUSENTE.md"
    assert aviso.is_file(), "sem instrução de como instalar depois"
    assert "sdd-lifecycle" in aviso.read_text(encoding="utf-8")


def test_pode_dispensar_a_skill_externa(tmp_path):
    destino = mod.gerar(nome="proj-sem-skill", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    assert not (destino / "skills" / "sdd-lifecycle").exists()
    assert not (destino / "skills" / "SKILL-CICLO-AUSENTE.md").exists()


def _texto_do_template(destino, caminho):
    """Lê o artefato real do projeto gerado.

    Fixture escrita à mão testa o que o autor acha que o arquivo é. Foi assim que
    a regressão de threat-model passou despercebida: o teste reconstruía a versão
    anterior do modelo, enquanto o modelo real já tinha mudado de forma.
    """
    return (destino / caminho).read_text(encoding="utf-8")


def test_modelos_em_branco_nao_passam_nos_verificadores(tmp_path):
    """Os modelos REAIS, copiados e não preenchidos, precisam ser sinalizados."""
    destino = mod.gerar(nome="p6", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    v = _verificador_pr(destino)

    spec = _texto_do_template(destino, "docs/specs/MODELO-spec.md")
    achados = v.analisar(alterados=["src/auth/login.py", "docs/specs/2026-01-01-x.md"],
                         conteudos={"docs/specs/2026-01-01-x.md": spec},
                         migrations_na_base=set())
    assert any("threat-model" in a.mensagem.lower() for a in achados), \
        "MODELO-spec.md intocado foi aprovado: as perguntas contaram como respostas"

    plano = _texto_do_template(destino, "docs/plans/MODELO-plano.md")
    achados2 = v.analisar(alterados=["migrations/0009_x.py", "src/app.py",
                                     "docs/plans/2026-01-01-x.md"],
                          conteudos={"docs/plans/2026-01-01-x.md": plano},
                          migrations_na_base=set())
    texto = " ".join(a.mensagem.lower() for a in achados2)
    assert "rollback" in texto, "MODELO-plano intocado passou no check de rollback"
    assert "evidência" in texto, "MODELO-plano intocado passou no check de evidência"


def test_hook_protege_caminho_absoluto_que_e_o_que_a_ferramenta_envia(tmp_path, monkeypatch):
    """A ferramenta envia file_path ABSOLUTO. Testar só com relativo certifica um
    comportamento que o harness nunca produz, e foi assim que este hook nasceu inerte."""
    import json as _json, subprocess as _sp
    destino = mod.gerar(nome="p7", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    script = destino / "scripts" / "proteger_governanca.py"
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(destino)}

    def decidir(caminho):
        evento = _json.dumps({"tool_name": "Edit", "tool_input": {"file_path": caminho}})
        return _sp.run(["python3", str(script)], input=evento, capture_output=True,
                       text=True, env=env).stdout.strip()

    for protegido in ("AGENTS.md", "docs/adr/0001-x.md", "docs/constituicao/padrao-v1.0.md",
                      "Arquitetura/mapa.yml", ".claude/settings.json"):
        assert decidir(str(destino / protegido)), f"absoluto {protegido} passou livre"
    assert decidir(str(destino / "docs" / ".." / "AGENTS.md")), "travessia com .. escapou"
    assert not decidir(str(destino / "src" / "app.py")), "código não deveria ser bloqueado"


def test_projeto_gerado_tem_o_que_o_proprio_ci_exige(tmp_path):
    """Dois jobs do CI rodam pip install -r requirements.txt, e o job de governança
    confere o tamanho do AGENTS.md. O projeto precisa nascer capaz de passar."""
    destino = mod.gerar(nome="p8", destino=tmp_path, descricao="d", stack="Python 3.12",
                        deps="requirements.txt", origem_ciclo=None)
    assert (destino / "requirements.txt").is_file(), "CI instala arquivo que não existe"
    # O padrão é {{IDENTIFICADOR}} em maiúsculas. Procurar "{{" cru dá falso positivo
    # em quantificador de regex ({1,6}) e em expressão do GitHub Actions (${{ ... }}).
    import re as _re
    marcador = _re.compile(r"\{\{[A-Z_]+\}\}")
    residuais = [str(p.relative_to(destino)) for p in destino.rglob("*")
                 if p.is_file() and not p.is_symlink()
                 and p.suffix in {".md", ".yml", ".yaml", ".py", ".tf", ".toml", ".json", ".txt"}
                 and marcador.search(p.read_text(encoding="utf-8", errors="replace"))]
    assert residuais == [], f"placeholders não substituídos: {residuais}"


# --- 1.7.0: spec verificável e aprovada -------------------------------------------------

import re as _re_spec  # noqa: E402

_COMENTARIO_HTML = _re_spec.compile(r"<!--.*?-->", _re_spec.S)


def _projeto(tmp_path, nome):
    """Gera um projeto sem a skill do ciclo (sem rede) e devolve (destino, verificador)."""
    destino = mod.gerar(nome=nome, destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    return destino, _verificador_pr(destino)


def _secao(texto, titulo):
    """Corpo da seção `## <titulo>` do modelo, sem comentários HTML."""
    m = _re_spec.search(rf"^##\s+{_re_spec.escape(titulo)}\s*$", texto, _re_spec.M)
    assert m, f"seção '{titulo}' ausente"
    resto = texto[m.end():]
    prox = _re_spec.search(r"^##\s", resto, _re_spec.M)
    return _COMENTARIO_HTML.sub("", resto[: prox.start()] if prox else resto)


def test_modelo_spec_tem_requisitos_com_criterio(tmp_path):
    """cobre: R1. O modelo REAL tem a seção Requisitos, ao menos um exemplo **R<n>** e,
    depois de cada exemplo, uma linha de critério. Objetivos e Critérios de aceite saem."""
    destino = mod.gerar(nome="m1", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    spec = _texto_do_template(destino, "docs/specs/MODELO-spec.md")
    requisitos = _secao(spec, "Requisitos")
    linhas = requisitos.splitlines()
    exemplos = [i for i, l in enumerate(linhas) if _re_spec.match(r"^\*\*R\d+\*\*", l)]
    assert exemplos, "a seção Requisitos não traz exemplo **R<n>**"
    for i in exemplos:
        fim = next((j for j in range(i + 1, len(linhas))
                    if _re_spec.match(r"^\*\*R\d+\*\*", linhas[j])), len(linhas))
        assert any("Critério" in l for l in linhas[i + 1: fim]), \
            f"o exemplo da linha {i} não é seguido de uma linha Critério"
    assert not _re_spec.search(r"^##\s+Objetivos\s*$", spec, _re_spec.M), \
        "Objetivos deveria ter sido substituído por Requisitos"
    assert not _re_spec.search(r"^##\s+Critérios de aceite\s*$", spec, _re_spec.M), \
        "Critérios de aceite deveria ter sido substituído por Requisitos"


def test_modelo_spec_tem_aprovacao_e_esclarecimentos(tmp_path):
    """cobre: R2, R3. O cabeçalho do modelo tem Aprovado por/em vazios; o marcador
    [ESCLARECER: …] é documentado em comentário; a seção Esclarecimentos existe."""
    destino = mod.gerar(nome="m2", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    spec = _texto_do_template(destino, "docs/specs/MODELO-spec.md")
    for campo in ("Aprovado por", "Aprovado em"):
        m = _re_spec.search(rf"^>\s*\*\*{campo}:\*\*(.*)$", spec, _re_spec.M)
        assert m, f"cabeçalho sem '{campo}'"
        assert m.group(1).strip() == "", f"'{campo}' deveria vir vazio no modelo"
    assert "[ESCLARECER" in spec, "o marcador não está documentado"
    assert not _re_spec.search(r"\[ESCLARECER:[^\]]*\]", _COMENTARIO_HTML.sub("", spec)), \
        "o marcador do modelo deve ficar em comentário, senão a spec nasce com pendência"
    assert _re_spec.search(r"^##\s+Esclarecimentos\s*$", spec, _re_spec.M), \
        "seção Esclarecimentos ausente"


_SPEC_PR = "docs/specs/2026-01-01-x.md"
_PLANO_PR = "docs/plans/2026-01-01-x.md"


def _aprovada(spec_modelo, por=""):
    """Deriva do modelo REAL uma spec marcada como aprovada."""
    spec = spec_modelo.replace("> **Status:** rascunho | em revisão | aprovada | arquivada",
                               "> **Status:** aprovada")
    assert "> **Status:** aprovada" in spec, "o modelo mudou a linha de Status"
    if por:
        spec = spec.replace("> **Aprovado por:**", f"> **Aprovado por:** {por}")
    return spec


def _avisos(v, spec, **extra):
    achados = v.analisar(alterados=[_SPEC_PR, *extra.get("outros", [])],
                         conteudos={_SPEC_PR: spec, **extra.get("conteudos", {})},
                         migrations_na_base=set())
    assert not [a for a in achados if a.bloqueia], "aviso de spec não pode bloquear"
    return [a.mensagem for a in achados]


def test_aprovada_sem_aprovador_avisa(tmp_path):
    """cobre: R2. Status aprovada com 'Aprovado por' vazio é aprovação sem registro."""
    destino, v = _projeto(tmp_path, "t2a")
    modelo = _texto_do_template(destino, "docs/specs/MODELO-spec.md")
    assert any("aprovação sem registro" in m for m in _avisos(v, _aprovada(modelo)))
    assert not any("aprovação" in m for m in _avisos(v, _aprovada(modelo, por="thiago")))


def test_marcador_aberto_em_spec_aprovada_avisa(tmp_path):
    """cobre: R3. Marcador aberto fora de comentário, em spec aprovada ou citada por plano."""
    destino, v = _projeto(tmp_path, "t2b")
    modelo = _texto_do_template(destino, "docs/specs/MODELO-spec.md")
    spec = _aprovada(modelo, por="thiago").replace(
        "## Motivação\n", "## Motivação\n\nA chave expira em [ESCLARECER: quanto tempo?] e em "
        "[ESCLARECER: quem renova?].\n")
    msgs = _avisos(v, spec)
    assert any("ESCLARECER" in m and "2" in m for m in msgs), msgs

    # rascunho citado por um plano do PR também conta
    rascunho = modelo.replace("## Motivação\n", "## Motivação\n\n[ESCLARECER: x?]\n")
    assert not any("ESCLARECER" in m for m in _avisos(v, rascunho)), \
        "rascunho sem plano não deveria avisar"
    plano = f"# Plano\n\n> **Spec relacionada:** `{_SPEC_PR}`\n"
    msgs = _avisos(v, rascunho, outros=[_PLANO_PR], conteudos={_PLANO_PR: plano})
    assert any("ESCLARECER" in m for m in msgs), msgs


def test_marcador_aberto_em_comentario_nao_conta(tmp_path):
    """cobre: R3. O marcador citado em comentário (como o modelo faz) não é pendência."""
    destino, v = _projeto(tmp_path, "t2c")
    modelo = _texto_do_template(destino, "docs/specs/MODELO-spec.md")
    spec = _aprovada(modelo, por="thiago").replace(
        "## Motivação\n", "## Motivação\n\n<!-- [ESCLARECER: x?] -->\n")
    assert not any("ESCLARECER" in m for m in _avisos(v, spec))
    assert not any("ESCLARECER" in m for m in _avisos(v, _aprovada(modelo, por="thiago")))


def test_requisito_sem_criterio_avisa(tmp_path):
    """cobre: R4. Requisito sem Critério nem Dado/Quando/Então até o próximo R."""
    destino, v = _projeto(tmp_path, "t2d")
    modelo = _texto_do_template(destino, "docs/specs/MODELO-spec.md")
    bloco = ("**R1** O sistema exporta o relatório.\n"
             "- Critério: **Dado** um relatório, **Quando** exporta, **Então** gera o arquivo.\n\n"
             "**R2** O sistema valida o formato.\n\n")
    spec = modelo.replace(modelo[modelo.index("**R1**"):modelo.index("## Não-objetivos")],
                          bloco)
    msgs = _avisos(v, spec)
    assert any("R2" in m and "critério" in m for m in msgs), msgs
    assert not any("R1" in m for m in msgs), msgs


def test_spec_formato_161_sem_achados_novos(tmp_path):
    """cobre: R7. Spec com Objetivos, sem R<n> nem Aprovado por: nenhum achado novo."""
    destino, v = _projeto(tmp_path, "t2e")
    modelo = _texto_do_template(destino, "docs/specs/MODELO-spec.md")
    antiga = _re_spec.sub(r"^> \*\*Aprovado (por|em):\*\*.*\n", "", modelo, flags=_re_spec.M)
    inicio, fim = antiga.index("## Requisitos"), antiga.index("## Não-objetivos")
    antiga = antiga[:inicio] + "## Objetivos\n\n- Entregar a coisa.\n\n" + antiga[fim:]
    inicio, fim = antiga.index("## Esclarecimentos"), antiga.index("## Threat-model")
    antiga = _aprovada(antiga[:inicio] + antiga[fim:])
    assert "**R" not in antiga and "Aprovado por" not in antiga
    assert _avisos(v, antiga) == []


def test_modelos_intocados_nao_aprovados_nem_rastreados(tmp_path):
    """cobre: R8. Os modelos REAIS, lado a lado e intocados, não geram nenhum achado de
    aprovação, marcador, critério ou rastreio (regressão da 1.6.1)."""
    destino, v = _projeto(tmp_path, "t2f")
    spec = _texto_do_template(destino, "docs/specs/MODELO-spec.md")
    plano = _texto_do_template(destino, "docs/plans/MODELO-plano.md")
    achados = v.analisar(alterados=[_SPEC_PR, _PLANO_PR],
                         conteudos={_SPEC_PR: spec, _PLANO_PR: plano},
                         migrations_na_base=set(), testes={})
    assert [str(a) for a in achados] == []


def test_modelo_plano_tem_rastreio_e_tabela(tmp_path):
    """cobre: R5. A tarefa de exemplo do modelo REAL termina com (R1), e a seção de revisão
    adversarial traz a tabela | R | veredito | evidência |."""
    destino = mod.gerar(nome="t3a", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    plano = _texto_do_template(destino, "docs/plans/MODELO-plano.md")
    tarefas = _secao(plano, "Tarefas")
    assert any(_re_spec.match(r"^- \[ \] .*\(R1\)\s*$", l) for l in tarefas.splitlines()), \
        "nenhuma tarefa de exemplo termina com (R1)"
    revisao = plano[plano.index("## Revisão adversarial"):]
    assert _re_spec.search(r"^\|\s*R\s*\|\s*veredito\s*\|\s*evidência\s*\|\s*$", revisao,
                           _re_spec.M), "tabela de veredito ausente"


def _spec_com_r1_r2(destino):
    """Deriva do modelo real uma spec com R1 e R2, ambos com critério."""
    modelo = _texto_do_template(destino, "docs/specs/MODELO-spec.md")
    bloco = ("**R1** O sistema exporta.\n- Critério: **Dado** x, **Quando** y, **Então** z.\n\n"
             "**R2** O sistema valida.\n- Critério: **Dado** x, **Quando** y, **Então** z.\n\n")
    return modelo.replace(modelo[modelo.index("**R1**"):modelo.index("## Não-objetivos")], bloco)


def _plano_citando(destino, citacao, tier2=False):
    """Deriva do modelo real um plano cuja tarefa de exemplo cita `citacao`."""
    plano = _texto_do_template(destino, "docs/plans/MODELO-plano.md")
    plano = plano.replace("(R1)", citacao)
    if tier2:
        plano = plano.replace("> **Tier:** 1 | 2", "> **Tier:** 2")
        assert "> **Tier:** 2" in plano, "o modelo mudou a linha de Tier"
    return plano


def test_rastreio_r2_sem_tarefa_e_sem_teste(tmp_path):
    """cobre: R6. Spec com R1 e R2, plano que cita só (R1), teste com `# cobre: R1`:
    avisos para R2 (sem tarefa e sem teste) e nenhum para R1. Diz 'citado', nunca 'coberto'."""
    destino, v = _projeto(tmp_path, "t3b")
    spec = _spec_com_r1_r2(destino)
    plano = _plano_citando(destino, "(R1)")
    testes = {"tests/test_x.py": "# cobre: R1\ndef test_a():\n    pass\n"}
    msgs = [a.mensagem for a in v.analisar_rastreio(spec, plano, testes, tier2=False)]
    assert any("R2" in m and "tarefa" in m for m in msgs), msgs
    assert any("R2" in m and "citado em teste" in m for m in msgs), msgs
    assert not any("R1" in m for m in msgs), msgs
    assert not any("coberto" in m.lower() for m in msgs), msgs

    # a citação pelo nome da função também vale, e o aviso some
    testes["tests/test_y.py"] = "def test_valida_r2_formato():\n    pass\n"
    plano2 = _plano_citando(destino, "(R1, R2)")
    assert v.analisar_rastreio(spec, plano2, testes, tier2=False) == []

    # pelo analisar, com os arquivos do PR
    achados = v.analisar(alterados=[_SPEC_PR, _PLANO_PR, "tests/test_x.py"],
                         conteudos={_SPEC_PR: spec, _PLANO_PR: plano},
                         migrations_na_base=set(), testes=testes)
    assert any("R2" in a.mensagem for a in achados)
    assert not [a for a in achados if a.bloqueia]


def test_tarefa_cita_r_inexistente(tmp_path):
    """cobre: R6. Tarefa que cita R<n> que a spec não tem."""
    destino, v = _projeto(tmp_path, "t3c")
    spec = _spec_com_r1_r2(destino)
    plano = _plano_citando(destino, "(R1, R3)")
    testes = {"tests/test_x.py": "# cobre: R1, R2\ndef test_a():\n    pass\n"}
    msgs = [a.mensagem for a in v.analisar_rastreio(spec, plano, testes, tier2=False)]
    assert any("R3" in m and "inexistente" in m for m in msgs), msgs


def test_tabela_veredito_incompleta(tmp_path):
    """cobre: R6. Plano Tier 2 com a tabela de veredito preenchida precisa listar todo R<n>.
    Sem linhas na tabela, ou fora do Tier 2, não confere."""
    destino, v = _projeto(tmp_path, "t3d")
    spec = _spec_com_r1_r2(destino)
    testes = {"tests/test_x.py": "# cobre: R1, R2\ndef test_a():\n    pass\n"}
    base = _plano_citando(destino, "(R1, R2)", tier2=True)
    parcial = base.rstrip("\n") + "\n| R1 | atendido | tests/test_x.py |\n"
    msgs = [a.mensagem for a in v.analisar_rastreio(spec, parcial, testes, tier2=True)]
    assert any("R2" in m and "veredito" in m for m in msgs), msgs
    assert not any("R1" in m for m in msgs), msgs

    assert v.analisar_rastreio(spec, base, testes, tier2=True) == [], \
        "tabela sem linhas não deveria ser conferida"
    assert v.analisar_rastreio(spec, parcial, testes, tier2=False) == [], \
        "fora do Tier 2 a tabela não é conferida"
    completo = parcial + "| R2 | atendido | tests/test_x.py |\n"
    assert v.analisar_rastreio(spec, completo, testes, tier2=True) == []


def _repo_git(tmp_path, arquivos_na_feature):
    """Repositório temporário: um commit na main e outro numa branch com `arquivos_na_feature`."""
    repo = tmp_path / "repo-pr"
    repo.mkdir()
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@e.com"]

    def rodar(*args):
        subprocess.run([*git, *args], cwd=repo, check=True, capture_output=True)

    rodar("init", "-q", "-b", "main")
    (repo / "LEIAME.md").write_text("x\n", encoding="utf-8")
    rodar("add", "LEIAME.md")
    rodar("commit", "-q", "-m", "base")
    rodar("checkout", "-q", "-b", "feat/x")
    for caminho, texto in arquivos_na_feature.items():
        (repo / caminho).parent.mkdir(parents=True, exist_ok=True)
        (repo / caminho).write_text(texto, encoding="utf-8")
        rodar("add", caminho)
    rodar("commit", "-q", "-m", "feature")
    return repo


def _rodar_verificador(destino, repo, base):
    import sys as _sys
    return subprocess.run(
        [_sys.executable, str(destino / "scripts" / "verificar_pr.py"),
         "--base", base, "--raiz", str(repo)],
        capture_output=True, text=True)


def test_base_inexistente_sai_com_2(tmp_path):
    """cobre: R10. Base que não existe não pode passar em silêncio com 'nenhum arquivo'."""
    destino = mod.gerar(nome="t4a", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    repo = _repo_git(tmp_path, {"docs/notas.md": "x\n"})
    r = _rodar_verificador(destino, repo, "origin/inexistente")
    assert r.returncode == 2, r.stdout + r.stderr
    assert "ERRO: base origin/inexistente não encontrada" in r.stdout + r.stderr

    ok = _rodar_verificador(destino, repo, "main")
    assert ok.returncode == 0, ok.stdout + ok.stderr


def test_main_le_os_testes_alterados_do_pr(tmp_path):
    """cobre: R6. O main() entrega ao analisar os testes alterados no PR: com `# cobre: R1`
    no teste, o R1 não é apontado; sem o teste no PR, é."""
    destino = mod.gerar(nome="t4b", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    spec = _spec_com_r1_r2(destino)
    plano = _plano_citando(destino, "(R1, R2)")
    teste = "# cobre: R1\ndef test_a():\n    pass\n"
    repo = _repo_git(tmp_path, {_SPEC_PR: spec, _PLANO_PR: plano, "tests/test_x.py": teste})
    r = _rodar_verificador(destino, repo, "main")
    saida = r.stdout
    assert "R2 não é citado em teste" in saida, saida
    assert "R1 não é citado em teste" not in saida, saida
    assert r.returncode == 0, "aviso não pode bloquear"


def test_qualidade_documenta_cobre_r(tmp_path):
    """cobre: R9. O steering de qualidade documenta `# cobre: R<n>` e o limite da convenção."""
    destino = mod.gerar(nome="t5a", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    texto = _texto_do_template(destino, "docs/steering/qualidade.md")
    assert "cobre: R" in texto, "a convenção de citar o requisito no teste não está documentada"
    assert "não é cobertura" in texto.lower() or "não prova cobertura" in texto.lower(), \
        "o limite da convenção (citação não é cobertura) não aparece"


def test_sdd_processo_sem_fase_3_do_sdd(tmp_path):
    """cobre: R15. A implementação é a Fase 6, como na skill do ciclo, e a volta é à Fase 1."""
    destino = mod.gerar(nome="t5b", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    texto = _texto_do_template(destino, "docs/steering/sdd-processo.md")
    assert "Fase 3 do SDD" not in texto
    assert "(Fase 6 do SDD)" in texto
    assert "retorna à Fase 1" in texto


def test_projeto_gerado_monta_agents_skills(tmp_path):
    """cobre: R11. .agents/skills (Codex e Antigravity) aponta para ../skills, como os outros
    três pontos de montagem, e o gerador preserva o link em vez de copiar."""
    destino = mod.gerar(nome="t6a", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    link = destino / ".agents" / "skills"
    assert link.is_symlink(), ".agents/skills virou cópia ou não existe"
    assert os.readlink(link) == "../skills"
    assert (link / "arquitetura-viva" / "SKILL.md").is_file(), "o link não resolve para as skills"


def test_claude_md_importa_agents(tmp_path):
    """cobre: R12. O CLAUDE.md importa a constituição com @AGENTS.md e segue sem regra própria."""
    destino = mod.gerar(nome="t6b", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=None)
    linhas = _texto_do_template(destino, "CLAUDE.md").splitlines()
    assert "@AGENTS.md" in linhas, "falta a linha @AGENTS.md"
    assert len([l for l in linhas if l.strip()]) <= 5, "o CLAUDE.md deve ser só um ponteiro"


def test_clone_do_ciclo_fixa_versao(tmp_path, monkeypatch):
    """cobre: R13. Com a origem padrão, o comando de clone fixa a tag v3.0.0. O teste troca o
    subprocess.run por um dublê só para o clone, então não usa rede."""
    clones = []
    real = subprocess.run

    def duble(cmd, *a, **kw):
        if cmd[:2] == ["git", "clone"]:
            clones.append(cmd)
            return subprocess.CompletedProcess(cmd, 1, "", "sem rede")
        return real(cmd, *a, **kw)

    monkeypatch.setattr(mod.subprocess, "run", duble)
    mod.gerar(nome="t7a", destino=tmp_path, descricao="d", stack="s", deps="requirements.txt")
    assert mod.VERSAO_CICLO == "v3.0.0"
    assert len(clones) == 1
    cmd = clones[0]
    assert cmd[cmd.index("--branch") + 1] == "v3.0.0", cmd
    assert mod.ORIGEM_CICLO_PADRAO in cmd

    # versão vazia usa a branch padrão da origem
    clones.clear()
    mod.gerar(nome="t7b", destino=tmp_path, descricao="d", stack="s", deps="requirements.txt",
              versao_ciclo="")
    assert "--branch" not in clones[0], clones[0]

    # fallback e pontos de montagem citam .agents/skills
    aviso = (tmp_path / "t7a" / "skills" / "SKILL-CICLO-AUSENTE.md").read_text(encoding="utf-8")
    assert ".agents/skills" in aviso
    assert "--branch v3.0.0" in aviso


def test_instala_a_tag_pedida_e_nao_o_head_da_origem(tmp_path):
    """cobre: R13. Origem local com a tag v3.0.0 e um commit posterior: o projeto recebe o
    conteúdo da tag, e a procedência registra a versão."""
    origem = tmp_path / "origem-tag"
    origem.mkdir()
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@e.com"]

    def rodar(*args):
        subprocess.run([*git, *args], cwd=origem, check=True, capture_output=True)

    rodar("init", "-q", "-b", "main")
    (origem / "SKILL.md").write_text("---\nname: sdd-lifecycle\n---\nversao da tag\n",
                                     encoding="utf-8")
    rodar("add", "SKILL.md")
    rodar("commit", "-q", "-m", "v3")
    rodar("tag", "v3.0.0")
    (origem / "SKILL.md").write_text("---\nname: sdd-lifecycle\n---\nposterior a tag\n",
                                     encoding="utf-8")
    rodar("commit", "-q", "-am", "depois")

    destino = mod.gerar(nome="t7c", destino=tmp_path, descricao="d", stack="s",
                        deps="requirements.txt", origem_ciclo=str(origem))
    skill = (destino / "skills" / "sdd-lifecycle" / "SKILL.md").read_text(encoding="utf-8")
    assert "versao da tag" in skill and "posterior a tag" not in skill
    assert "v3.0.0" in (destino / "skills" / "sdd-lifecycle" / "PROCEDENCIA.md").read_text(
        encoding="utf-8")
