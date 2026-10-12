"""La instalación visual no necesita ni descarga la clase de texto."""
from pathlib import Path
from unittest.mock import Mock
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import setup_vision as setup


@pytest.fixture
def install_context(tmp_path, monkeypatch):
    monkeypatch.setattr(setup, "ROOT", tmp_path)
    monkeypatch.setattr(setup.sys, "version_info", (3, 11, 14))
    monkeypatch.setattr(setup, "find_ollama", lambda: "ollama")
    monkeypatch.setattr(setup, "ensure_ollama", Mock())
    monkeypatch.setattr(setup, "ollama_request", Mock(side_effect=[
        {"version": "0.12.7"}, {"done": True}]))
    monkeypatch.setattr(setup.shutil, "which", lambda name: None)
    run = Mock()
    monkeypatch.setattr(setup.subprocess, "run", run)
    return tmp_path, run


@pytest.mark.parametrize("system,nvidia,index", [
    ("darwin", False, None),
    ("linux", False, "https://download.pytorch.org/whl/cpu"),
    ("linux", True, "https://download.pytorch.org/whl/cu128"),
    ("win32", False, "https://download.pytorch.org/whl/cpu"),
    ("win32", True, "https://download.pytorch.org/whl/cu128"),
])
def test_only_visual_models_and_own_environment(install_context, monkeypatch, system, nvidia, index):
    root, run = install_context
    monkeypatch.setattr(setup.sys, "platform", system)
    monkeypatch.setattr(setup.platform, "machine", lambda: "arm64")
    monkeypatch.setattr(setup.shutil, "which", lambda name: "nvidia-smi" if nvidia else None)
    monkeypatch.setenv("OLLAMA_HOST", "https://example.invalid")
    setup.install()
    commands = [call.args[0] for call in run.call_args_list]
    assert [c for c in commands if c[1] == "pull"] == [["ollama", "pull", "qwen3-vl:2b-instruct"]]
    assert "setup_local" not in str(commands) and "qwen2.5" not in str(commands)
    torch = next(c for c in commands if "torch==2.8.0" in c)
    if index:
        assert torch[-2:] == ["--index-url", index]
    else:
        assert "--index-url" not in torch
    python = root / ".venv-vision" / ("Scripts/python.exe" if system == "win32" else "bin/python")
    assert torch[0] == str(python)
    download = next(c for c in run.call_args_list if "vision.download" in c.args[0])
    assert download.kwargs["cwd"] == root
    pull = next(c for c in run.call_args_list if c.args[0][1] == "pull")
    assert pull.kwargs["env"]["OLLAMA_HOST"] == setup.OLLAMA_URL


def test_unsupported_ollama_stops_before_installing(install_context, monkeypatch):
    _, run = install_context
    monkeypatch.setattr(setup, "ollama_request", Mock(return_value={"version": "0.12.6"}))
    with pytest.raises(RuntimeError, match="Actualizar"):
        setup.install()
    run.assert_not_called()


def test_model_load_failure_is_not_reported_as_success(install_context, monkeypatch, capsys):
    monkeypatch.setattr(setup, "ollama_request", Mock(side_effect=[
        {"version": "0.12.7"}, {"done": False}]))
    with pytest.raises(RuntimeError, match="no confirmó"):
        setup.install()
    assert "Visión preparada" not in capsys.readouterr().out
