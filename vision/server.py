"""Servicio ViT local. Ejecutar: .venv-vision/bin/python -m vision.server"""
import argparse
import json
import threading
from fastapi import FastAPI,HTTPException,Request
from starlette.concurrency import run_in_threadpool
from .images import decode_image,MAX_IMAGE_BYTES
from .config import VIT_ID

# El clasificador se inyecta: se puede probar HTTP sin descargar pesos.
def create_app(classifier):
    app=FastAPI(title="UNA / ViT local")
    lock=threading.Lock()
    @app.get("/health")
    def health():
        return {"service":"una-vit","model":VIT_ID,"ready":True,"device":classifier.device}

    @app.post("/classify")
    async def classify(request:Request):
        # Acotar también cuerpos HTTP fragmentados, antes de parsear el JSON.
        body=bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body)>MAX_IMAGE_BYTES*4//3+1024:
                raise HTTPException(413,"Solicitud demasiado grande")
        try:
            payload=json.loads(body)
            if not isinstance(payload,dict) or set(payload)!={"image"}:
                raise ValueError("Enviar exactamente un campo image con JPEG/PNG en base64")
            image=decode_image(payload["image"])
        except (ValueError,TypeError) as exc:
            raise HTTPException(422,str(exc)) from exc
        if not lock.acquire(blocking=False):
            raise HTTPException(429,"Ya hay una imagen en proceso; esperar su respuesta")
        try:
            return await run_in_threadpool(classifier.classify,image)
        except Exception as exc:
            raise HTTPException(500,"Falló la inferencia: "+str(exc)[:200]) from exc
        finally:
            lock.release()
    return app

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--device",choices=["auto","cpu","cuda","mps"],default="auto")
    p.add_argument("--port",type=int,default=8768)
    args=p.parse_args()
    from .vit_model import ViTClassifier
    import uvicorn
    print("Cargando ViT local. Si faltan pesos: ejecutar install_env de este repositorio.",flush=True)
    model=ViTClassifier(args.device)
    print("ViT listo en "+model.device,flush=True)
    uvicorn.run(create_app(model),host="127.0.0.1",port=args.port,access_log=False)
if __name__=="__main__":main()
