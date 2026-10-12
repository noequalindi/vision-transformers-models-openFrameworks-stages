# Visión con transformers: dos ejemplos locales

Para explicar las llamadas al modelo y convertir la respuesta en una interacción,
ver la [guía breve del código OF](../docs/GUIA_CODIGO_OF.md).

| Ejemplo OF | Modelo | Entrada → salida | Servicio |
| --- | --- | --- | --- |
| `visionViT` | `google/vit-base-patch16-224` | Imagen → top 5 de 1000 categorías ImageNet | Python / PyTorch en 127.0.0.1:8768 |
| `visionChat` | `qwen3-vl:2b-instruct` | Imagen + pregunta → respuesta escrita | Ollama en 127.0.0.1:11434 |

Este repositorio contiene **dos proyectos OF independientes**.
Ambos usan el addon actualizado `ofxLocalAI`. No requieren Box2D, OSC ni Docker.
Los pesos se distribuyen con licencia Apache 2.0 y se ejecutan localmente sin
API key ni cobro por consulta. El equipo aporta la memoria y el procesamiento.

## Tamaño y equipo necesario

| Ejemplo | Modelo en disco | RAM total para planificar la práctica |
| --- | --- | --- |
| `visionViT` | **346 MB**, ViT Base FP32 | **8 GB** como punto de partida; 16 GB da margen para IDE y otras aplicaciones |
| `visionChat` | **1,89 GB**, Qwen3-VL 2B Instruct Q4_K_M | **8 GB** como punto de partida, con poco margen; **16 GB recomendados** |

Tamaños medidos localmente el **5 de octubre de 2026**. Los dos modelos visuales
suman **2,24 GB** aproximadamente, sin contar entornos ni aplicaciones.
El instalador de este repositorio prepara solamente estos dos modelos.

La RAM indicada es una **estimación para la clase**, usando un modelo a la vez,
no un mínimo oficial ni una prueba realizada en equipos de 8 GB. **GPU opcional**:
se puede ejecutar en CPU, con mayor demora. El tamaño del archivo no equivale al
consumo de memoria durante una consulta. Estos ejemplos procesan una captura por
pedido; no requieren que el modelo siga los FPS de la cámara.

Como margen de disco para el kit completo, prever **15 GB libres en CPU/macOS**
o **25 GB con PyTorch CUDA**, además de OF y su compilador. La guía general
detalla sistemas operativos, versiones, fuentes y comprobaciones:
[requisitos locales y tamaño de los modelos](../README.md#modelos-tamaño-y-requisitos-locales).

## 1. Instalar y descargar

Desde la raíz de la clase, elegir el comando del sistema:

```sh
# macOS
bash install_env_mac.command

# Linux
bash install_env_linux.sh
```

En una terminal de Windows:

```bat
install_env_windows.cmd
```

El repositorio incluye su propio instalador; no necesita la clase de LLM.

El script:

1. Comprueba Ollama **>= 0.12.7**; si es anterior, pide actualizarlo.
2. Prepara Python 3.11 en `.venv-vision` e instala PyTorch + Transformers.
3. Descarga ViT (~346 MB de pesos) a `models/vit-base-patch16-224`, fija la revisión
   y ejecuta una inferencia de comprobación. No es un benchmark de exactitud.
4. Descarga **Qwen3-VL 2B Instruct** (~1.9 GB) al almacenamiento de Ollama y lo precarga
   durante cinco minutos sin uso. No usar simplemente `:2b`, que puede seleccionar Thinking.

Reservar varios GB adicionales para librerías y cachés. La instalación inicial
requiere internet; con los archivos preparados, las consultas son locales.
La descarga no instala openFrameworks ni su compilador.

### GPU y CPU

ViT prueba **CUDA → MPS → CPU** según disponibilidad de PyTorch. En modo `auto`,
si falla la operación en GPU, reintenta en CPU y devuelve `warning`. `--device cpu`
permite elegir CPU al iniciar el servidor. La respuesta informa el dispositivo.

El instalador elige ruedas CUDA 12.8 si encuentra `nvidia-smi` en Windows/Linux;
en otros equipos de esos sistemas usa ruedas CPU. En macOS usa el paquete nativo
(Metal/MPS en equipos compatibles). Detectar `nvidia-smi` no garantiza que el driver
sea compatible: PyTorch comprueba la disponibilidad al ejecutar.
Para instalar otra variante oficial de PyTorch, usar `setup_vision.py --torch-index-url URL`.
Ollama decide su propia distribución GPU/CPU; no depende del PyTorch del ejemplo ViT.

## 2. Iniciar los servicios

**Para ViT**, abrir una terminal en la raíz de la clase y dejarla abierta:

```sh
# macOS
bash start_vision_mac.command
# Linux
bash start_vision_linux.sh
# Windows
start_vision_windows.cmd
```

Esperar `ViT listo en ...` y `Uvicorn running on http://127.0.0.1:8768`.
Ctrl+C detiene ese servicio. No descarga pesos al arrancar.
Si el puerto está ocupado, comprobar `http://127.0.0.1:8768/health` antes de abrir otra instancia.

**Para el multimodal**, mantener Ollama abierto. No iniciar el servicio ViT.
Después de reiniciar el equipo hay que abrir nuevamente el servicio correspondiente.

## 3. Copiar e importar en OF

1. Actualizar `OF/addons/ofxLocalAI/` **completo**, con `ofxVisionImage.h` y el método
   `classifyImage()` de la nueva versión.
2. Copiar `visionViT/` y/o `visionChat/` a `OF/apps/myApps/`.
3. Importar cada carpeta en Project Generator: **Project path = OF/apps/myApps**,
   **Project name = visionViT** o **visionChat**, addon **ofxLocalAI**.
   Additional source paths vacío. Pulsar Update; no crear una plantilla anidada.
4. Compilar el proyecto del sistema. En macOS/Linux:

```sh
cd RUTA_A_OF/apps/myApps/visionViT
make Release -j4
make RunRelease
# Para el otro ejemplo: cambiar visionViT por visionChat.
```

## 4. Probar

- **O** abre un JPG/PNG; también se puede arrastrar el archivo a la ventana.
- **RECARGAR EJEMPLO** vuelve a `sample.png`, cierra la cámara y limpia la
  respuesta. En Chat conserva la pregunta. Se habilita al terminar el pedido
  pendiente; presionar Enter para analizar de nuevo.
- **C** activa o detiene la webcam. Dar permiso a la app si el sistema lo solicita.
  `camera` en `bin/data/connection.json` permite elegir otro índice.
- **Enter / ANALIZAR** captura y envía una imagen. No se manda video continuo.
- La imagen mostrada al recibir la respuesta es la **captura enviada**, no otro frame.
- **visionViT / P** superpone los 14 × 14 parches sobre la captura. Esta cuadrícula
  es didáctica, **no es un mapa de atención**, segmentación ni tracking.
- **visionChat**: click en el editor para escribir; Ctrl/Cmd+A y V seleccionan/pegan.
  Esc sale del editor y habilita O/C/R/E. Cada pregunta es independiente, sin historial.
- **R** muestra datos escritos a mano, claramente marcados SIN INFERENCIA.
- **Esc, E** copia el diagnóstico si falla la conexión o respuesta.

Se incluye `sample.png`: composición sintética propia con dos figuras y texto.
Sirve para contrastar tareas: Qwen puede describirla; ViT debe elegir entre sus
clases conocidas, aunque ninguna represente bien ese dibujo. Para clasificar
objetos cotidianos, traer fotografías propias o usar la cámara.

## 5. Leer y modificar

| Archivo | Responsabilidad |
| --- | --- |
| `vision/vit_model.py` | Preprocesar, ejecutar ViT y convertir logits en scores |
| `vision/images.py` | Validar JPEG/PNG y límites de tamaño |
| `vision/server.py` | HTTP: `/health` y `/classify`, una inferencia simultánea |
| `vision/client.py` | Consultar desde Python para estudiar el intercambio |
| `vision/download.py` | Descargar pesos de una revisión fija y comprobar inferencia |
| `visionViT/src/ofApp.cpp` | Entrada, barras del top 5 y cuadrícula didáctica |
| `visionChat/src/ofApp.cpp` | Imagen + pregunta, respuesta y escritura progresiva |
| `ofxLocalAI/src/ofxVisionImage.h` | JPEG y base64 para transportar píxeles en JSON |

Recorrido comentado en C++: **setup → send → update → response → draw → exit**.
Modificar `response()` para mapear datos a una experiencia propia; modificar
`draw()` para cambiar su aspecto. No enviar peticiones en cada frame.

### Probar el mismo intercambio en Python

```sh
.venv-vision/bin/python -m vision.client vit visionViT/bin/data/sample.png
.venv-vision/bin/python -m vision.client chat visionChat/bin/data/sample.png --question "¿Qué colores y formas ves?"
```

En Windows usar `.venv-vision\Scripts\python.exe`. El modo ViT requiere el servidor
8768; el modo chat requiere Ollama. No hay que ejecutar el cliente Python para usar OF.

### Límites que conviene enseñar

ViT clasifica la imagen completa: no ubica objetos ni sigue manos. Sus scores son
relativos a las 1000 clases conocidas, no una garantía de acierto. Qwen genera
texto condicionado por imagen y pregunta: puede inventar detalles. Ninguno de
estos ejemplos genera imágenes nuevas ni video. Las respuestas no se ejecutan
como código. La cámara actualiza la vista; la inferencia se hace por captura.

ViT recibe 224 × 224; el multimodal recibe una imagen con lado mayor de hasta
768 píxeles. El servicio ViT rechaza entradas de más de 4 MiB o 12 megapíxeles.
El addon recibe la respuesta completa: la escritura progresiva es una animación local.

## Fuentes y licencias

- [ViT y pesos de Google](https://huggingface.co/google/vit-base-patch16-224).
- [Artículo original ViT](https://arxiv.org/abs/2010.11929).
- [Qwen3-VL Instruct](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct).
- [Etiqueta exacta en Ollama](https://ollama.com/library/qwen3-vl:2b-instruct).
- [Imágenes en la API REST de Ollama](https://docs.ollama.com/capabilities/vision).

La clase de LLM se distribuye en otro repositorio. Esta carpeta incluye todos
los fuentes necesarios para los ejemplos de visión y su addon.
