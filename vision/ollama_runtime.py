"""Inicio y consultas de Ollama local, sin depender de otra clase."""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener

OLLAMA_URL = "http://127.0.0.1:11434"


def find_ollama():
    candidates = [shutil.which("ollama"),
                  "/Applications/Ollama.app/Contents/Resources/ollama",
                  Path.home() / "Applications/Ollama.app/Contents/Resources/ollama",
                  "/usr/local/bin/ollama", "/usr/bin/ollama"]
    if os.environ.get("LOCALAPPDATA"):
        candidates.append(Path(os.environ["LOCALAPPDATA"]) / "Programs/Ollama/ollama.exe")
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise RuntimeError("No se encontro Ollama. Ejecutar install_env_mac.command, install_env_linux.sh o install_env_windows.cmd de la raiz del repositorio.")


def ollama_request(route, payload=None, timeout=2):
    # The classroom config is local: do not inherit proxy or remote Ollama hosts.
    request = Request(OLLAMA_URL + route,
                      data=json.dumps(payload).encode() if payload is not None else None,
                      headers={"Content-Type": "application/json"})
    with build_opener(ProxyHandler({})).open(request, timeout=timeout) as response:
        return json.load(response)


def ollama_tags():
    data = ollama_request("/api/tags")
    if not isinstance(data, dict) or not isinstance(data.get("models"), list):
        raise ValueError("La respuesta en 11434 no corresponde a Ollama")
    return data


def ready():
    try:
        ollama_tags()
        return True
    except (URLError, OSError, ValueError):
        return False


def ensure_ollama(ollama, server, timeout=60):
    """Reuse an existing server; leave a successfully started own process running."""
    if ready():
        return
    log_path = server / ".local/ollama-setup.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, OLLAMA_HOST=OLLAMA_URL)
    options = {"start_new_session": True} if sys.platform != "win32" else {
        "creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP}
    print("Iniciando Ollama local en 127.0.0.1:11434...", flush=True)
    with log_path.open("ab") as log:
        process = subprocess.Popen([ollama, "serve"], stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=log, env=env, **options)
    deadline = time.monotonic() + timeout
    try:
        # An app/service may be starting concurrently. Recheck readiness even if
        # our process exits because that app already acquired the port.
        while time.monotonic() < deadline:
            if ready():
                return
            time.sleep(1)
        raise RuntimeError(f"Ollama no respondio en {OLLAMA_URL}. Revisar {log_path}")
    except BaseException:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        raise
