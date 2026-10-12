"""Instala ViT y Qwen3-VL para esta clase independiente de visión."""
import argparse,json,os,platform,re,shutil,subprocess,sys
from pathlib import Path
from vision.ollama_runtime import find_ollama,ensure_ollama,ollama_request,OLLAMA_URL
from vision.config import ROOT,VLM_ID

def version_tuple(value):
    match=re.search(r"(\d+)\.(\d+)\.(\d+)",value)
    if not match:raise RuntimeError("No se pudo leer la versión de Ollama")
    return tuple(map(int,match.groups()))

def install(torch_index=None):
    if sys.version_info[:2] != (3, 11):
        raise RuntimeError("Usar Python 3.11; los scripts install_env lo preparan automáticamente")
    ollama=find_ollama();ensure_ollama(ollama,ROOT)
    if version_tuple(ollama_request("/api/version")["version"])<(0,12,7):
        raise RuntimeError("Qwen3-VL necesita Ollama >=0.12.7. Actualizar la app y repetir.")
    env=ROOT/".venv-vision"
    python=env/("Scripts/python.exe" if sys.platform=="win32" else "bin/python")
    if not python.exists():
        if env.exists():raise RuntimeError(".venv-vision está incompleto o fue movido; renombrar y repetir")
        subprocess.run([sys.executable,"-m","venv",str(env)],check=True)
    # Entorno propio de esta clase; no se instala Gradio ni el modelo de texto.
    print("3/4 Instalando bibliotecas de visión...", flush=True)
    torch_version="2.2.2" if sys.platform=="darwin" and platform.machine()=="x86_64" else "2.8.0"
    args=[str(python),"-m","pip","install","torch=="+torch_version]
    if sys.platform!="darwin":
        index=torch_index or ("https://download.pytorch.org/whl/cu128" if shutil.which("nvidia-smi") else "https://download.pytorch.org/whl/cpu")
        args += ["--index-url",index]
    subprocess.run(args,check=True)
    subprocess.run([str(python),"-m","pip","install","-r",str(ROOT/"vision/requirements.txt")],check=True)
    print("4/4 Descargando/verificando los dos modelos...", flush=True)
    subprocess.run([str(python),"-m","vision.download"],cwd=ROOT,check=True)
    print("Descargando/verificando "+VLM_ID+" (~1.9 GB de pesos en Ollama)...",flush=True)
    subprocess.run([ollama,"pull",VLM_ID],check=True,env=dict(os.environ,OLLAMA_HOST=OLLAMA_URL))
    # Precarga corta. Ollama decide GPU/CPU según soporte y memoria.
    result=ollama_request("/api/generate",{"model":VLM_ID,"stream":False,"keep_alive":"5m","options":{"num_ctx":4096}},timeout=300)
    if result.get("done") is not True:raise RuntimeError("Ollama no confirmó la carga del modelo visual")
    subprocess.run([ollama,"ps"],check=True,env=dict(os.environ,OLLAMA_HOST=OLLAMA_URL))
    print("Visión preparada. Para ViT: iniciar start_vision del sistema y abrir visionViT.")
    print("Para visionChat: basta con Ollama activo. No necesita el servidor ViT.")

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--torch-index-url",help="Índice alternativo oficial de ruedas PyTorch")
    args=p.parse_args()
    try:install(args.torch_index_url)
    except (RuntimeError,OSError,ValueError,subprocess.SubprocessError) as exc:raise SystemExit("Visión NO preparada: "+str(exc))
