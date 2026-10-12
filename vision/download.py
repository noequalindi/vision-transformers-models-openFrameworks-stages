"""Descarga los archivos necesarios y comprueba inferencia local sin entrenamiento."""
import json
from pathlib import Path
from huggingface_hub import snapshot_download,HfApi
from .config import VIT_ID,VIT_REVISION,VIT_DIR

def main():
    # Reutilizar el commit de la primera instalación para no cambiar la clase silenciosamente.
    manifest=VIT_DIR/"installed.json"
    revision=json.loads(manifest.read_text())["revision"] if manifest.exists() else HfApi().model_info(VIT_ID,revision=VIT_REVISION).sha
    snapshot_download(VIT_ID,revision=revision,local_dir=VIT_DIR,
                      allow_patterns=["config.json","preprocessor_config.json","model.safetensors","README.md","LICENSE*"])
    from .vit_model import ViTClassifier
    from PIL import Image
    classifier=ViTClassifier()
    result=classifier.classify(Image.new("RGB",(224,224),(80,120,160)))
    # Imagen sintética de comprobación: NO es una medición de exactitud.
    manifest.write_text(json.dumps({"model":VIT_ID,"revision":revision,"device_checked":result["device"]},indent=2))
    print("ViT descargado y probado; dispositivo:",result["device"])
    if result["warning"]:print(result["warning"])
if __name__=="__main__":main()
