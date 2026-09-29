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
