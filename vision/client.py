"""Una misma imagen: clasificación ViT o pregunta multimodal Qwen3-VL."""
import argparse,base64,json
from pathlib import Path
from urllib.request import Request,build_opener,ProxyHandler
from .images import decode_image,MAX_IMAGE_BYTES
from .config import VLM_ID,VIT_URL

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=["vit","chat"])
    parser.add_argument("image",type=Path)
    parser.add_argument("--question",default="Describe en español lo que ves. No inventes detalles.")
    args=parser.parse_args()
    if args.image.stat().st_size>MAX_IMAGE_BYTES:raise ValueError("Reducir la imagen a menos de 4 MiB")
    encoded=base64.b64encode(args.image.read_bytes()).decode()
    decode_image(encoded)
    if args.mode=="vit":url=VIT_URL+"/classify";body={"image":encoded}
    else:
        url="http://127.0.0.1:11434/api/chat"
        body={"model":VLM_ID,"stream":False,"options":{"num_ctx":4096,"num_predict":256},
              "messages":[{"role":"user","content":args.question,"images":[encoded]}]}
    request=Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
    with build_opener(ProxyHandler({})).open(request,timeout=180) as response:
        print(json.dumps(json.load(response),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
