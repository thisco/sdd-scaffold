"""Testes do gerador de projetos a partir do template."""
import importlib.util
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
