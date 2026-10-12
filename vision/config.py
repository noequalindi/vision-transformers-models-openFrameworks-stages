from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
VIT_ID = "google/vit-base-patch16-224"
# La revisión se fija para que la clase use los mismos pesos y etiquetas.
VIT_REVISION = "3f49326eb077187dfe1c2a2bb15fbd74e6ab91e3"
VIT_DIR = ROOT / "models/vit-base-patch16-224"
VLM_ID = "qwen3-vl:2b-instruct"
VIT_URL = "http://127.0.0.1:8768"
