"""ViT clasifica una imagen completa; no detecta cajas, poses ni personas."""
import time
from .config import VIT_DIR,VIT_ID

class ViTClassifier:
    def __init__(self,device="auto",model_dir=VIT_DIR):
        import torch
        from transformers import ViTImageProcessor,ViTForImageClassification
        self.torch=torch
        if device not in {"auto","cpu","cuda","mps"}:
            raise ValueError("Dispositivo: auto, cpu, cuda o mps")
        self.automatic=device=="auto"
        self.device=("cuda" if torch.cuda.is_available() else
                     "mps" if torch.backends.mps.is_available() else "cpu") if self.automatic else device
        # Solo archivos descargados. Abrir OF nunca dispara una descarga oculta.
        self.processor=ViTImageProcessor.from_pretrained(str(model_dir),local_files_only=True)
        self.model=ViTForImageClassification.from_pretrained(str(model_dir),local_files_only=True,use_safetensors=True).eval()
        self.warning=""
        try:
            self.model.to(self.device)
        except (RuntimeError,NotImplementedError) as exc:
            self._fallback(exc)

    def _fallback(self,error):
        if not self.automatic or self.device=="cpu":
            raise error
        self.warning="No se pudo usar la GPU; inferencia en CPU. " + str(error)[:160]
        self.device="cpu"
        self.model.to("cpu")

    def classify(self,image):
        start=time.perf_counter()
        inputs=self.processor(images=image,return_tensors="pt")
        # FP32, eval e inference_mode: no entrenamos ni modificamos los pesos.
        def infer():
            with self.torch.inference_mode():
                logits=self.model(**{k:v.to(self.device) for k,v in inputs.items()}).logits
                return logits.softmax(dim=-1)[0].cpu()
        try:
            scores=infer()
        except (RuntimeError,NotImplementedError) as exc:
            self._fallback(exc)
            scores=infer()
        values,indices=scores.topk(5)
        return {"model":VIT_ID,"device":self.device,"warning":self.warning,
                "elapsed_ms":round((time.perf_counter()-start)*1000,1),
                "predictions":[{"class_id":int(i),"label":self.model.config.id2label[int(i)],"score":float(v)}
                               for v,i in zip(values,indices)],
                "input_size":[224,224],"patch_size":16,
                "note":"Scores softmax entre 1000 clases; no son garantía de acierto."}
