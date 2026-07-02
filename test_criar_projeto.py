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
    residuais = [
        p for p in destino.rglob("*")
        if p.is_file() and p.suffix in {".md", ".yml", ".yaml", ".py", ".tf"}
        and "{{" in p.read_text(encoding="utf-8")
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
