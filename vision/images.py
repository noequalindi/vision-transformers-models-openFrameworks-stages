"""Decodificación acotada compartida por consola y HTTP; no guarda las imágenes."""
import base64
import binascii
import io
import warnings
from PIL import Image, ImageOps
MAX_IMAGE_BYTES = 4 * 1024 * 1024
MAX_PIXELS = 12_000_000

def decode_image(encoded):
    if not isinstance(encoded,str) or len(encoded)>((MAX_IMAGE_BYTES+2)//3)*4:
        raise ValueError("Imagen ausente o demasiado grande (máximo 4 MiB)")
    try:
        raw=base64.b64decode(encoded,validate=True)
    except (ValueError,binascii.Error) as exc:
        raise ValueError("La imagen debe ser base64 de JPEG o PNG, sin prefijo data:") from exc
    if not raw or len(raw)>MAX_IMAGE_BYTES:
        raise ValueError("Imagen vacía o demasiado grande")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error",Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw)) as image:
                if image.format not in {"JPEG","PNG"}:
                    raise ValueError("Usar JPEG o PNG")
                if image.width*image.height>MAX_PIXELS:
                    raise ValueError("Imagen mayor a 12 megapíxeles: reducir antes de enviar")
                return ImageOps.exif_transpose(image).convert("RGB")
    except (OSError,Image.DecompressionBombError,Image.DecompressionBombWarning) as exc:
        raise ValueError("Archivo de imagen inválido o demasiado grande") from exc
