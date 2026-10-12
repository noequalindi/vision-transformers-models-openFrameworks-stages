# Validación de visión

Registro histórico trasladado desde la clase original. Las rutas y comandos de
instalación vigentes están en el [README](../README.md).

## Vision Transformer y multimodal — 4 de octubre de 2026

- 29 pruebas Python aprobadas: contratos de imágenes/servicio ViT y pruebas
  existentes del instalador. Se comprobaron datos inválidos, tamaño máximo,
  recuperación tras fallo y servicio sin cargar pesos en los tests unitarios.
- Instalación real de ViT Base y `qwen3-vl:2b-instruct` en macOS Apple Silicon.
  ViT ejecutó inferencia con MPS. Se fija la variante Instruct de Qwen para
  evitar que la etiqueta genérica seleccione la variante Thinking.
- `visionViT` y `visionChat`: compilación y enlace nativos con OF 0.12.1;
  ambos ejecutables consultaron sus modelos reales y finalizaron con
  `VISION_CONTRACT_OK`. Se usó la imagen sintética incluida: comprueba la
  integración, no mide precisión de clasificación ni calidad general.
- Comprobación de sintaxis del addon y ejemplos anteriores/nuevos con
  `tools/check_of_headers.py RUTA_A_OF --stage --vision`: correcta.
- Capturas nativas de ambos ejemplos revisadas. Las capturas del PPTX usan
  respuestas grabadas, identificadas como SIN INFERENCIA.
- PPTX: 20 diapositivas y 20 notas de orador, tipografía Poppins, revisión
  visual completa. Control de disposición: cero errores; una advertencia
  aceptada por etiquetas independientes de las fases de una línea temporal.
- Sin verificar en hardware: cámara web, Windows, Linux y CUDA. Los scripts
  incluyen esas plataformas, pero la validación nativa fue en macOS/MPS.

El servicio Python nuevo pertenece exclusivamente al ejemplo ViT; los ejemplos
LLM y visionChat siguen consultando Ollama directamente. Ver `vision/README.md`
para instalar y ejecutar. Las pruebas nativas se hicieron en copias temporales;
los alumnos deben importar los fuentes de la clase con Project Generator.

## Ampliación didáctica de visión — 4 de octubre de 2026

La presentación ahora tiene **25 diapositivas y 25 notas**, con cinco inserciones:
CNN frente a ViT; LLM causal frente a encoder visual; Q/K/V; bloque del encoder;
comparación de los contratos ViT y Qwen3-VL. Se mantuvo el estilo y el contenido
de los ejemplos. Las notas de Canva siguen la nueva numeración.

Se revisaron las 25 diapositivas renderizadas y el paquete PPTX (notas, Poppins,
medios y orden). Control de disposición sin errores. Las advertencias corresponden
a tipografía heredada de la importación en pies de página, y a etiquetas
independientes de tabla/línea temporal; los renders conservan el tamaño y no
muestran recortes. No se modificó código ni modelos en esta ampliación.

## Reparación del paquete PPTX — 4 de octubre de 2026

Se detectó un identificador `cNvPr id=1` repetido entre el grupo raíz y la
primera forma en cada una de las 25 diapositivas. Se asignó un ID libre al
grupo raíz, conservando las formas y sus referencias. Verificación posterior:
IDs únicos, XML válido, destinos de relaciones existentes, ZIP íntegro y
25 diapositivas/25 notas. Comparación del XML confirma que solamente cambió
el ID del grupo raíz, sin cambios visuales ni de texto. La apertura/importación
en la aplicación del usuario queda pendiente de confirmar.

## Compatibilidad de importación — 4 de octubre de 2026

El usuario informó que la primera reparación no resolvió la importación.
El paquete original pasó XSD PresentationML/DrawingML y pudo leerse con
python-pptx, pero app.xml declaraba cero diapositivas y cero notas.
Se corrigieron esos conteos; se normalizaron relaciones a rutas relativas,
tipos de contenido y metadatos de layouts/grupos, retirando IDs de creación
opcionales. La versión `_importar.pptx` y la principal contienen lo mismo.

Validación independiente: 25 diapositivas con notas, XSD sin errores,
relaciones resueltas e IDs únicos. Se comprobó igualdad de todos los textos,
notas, posiciones, tamaños e imágenes con la versión anterior. Render de las
25 diapositivas y PDF visual de respaldo de 25 páginas. El PDF contiene
imágenes de las diapositivas: no reemplaza la edición de elementos en PPTX.

La conexión de carga de Canva respondió `Unsupported file format PPTX`;
esa ruta de herramientas no admite el formato y no sirve para comprobar
el importador interactivo. No se ha confirmado apertura en Google Slides
ni Canva. No atribuir el rechazo original a una causa única sin esa prueba.

## Reconstrucción del contenedor y prueba de importación real

Se reconstruyó el contenedor OPC desde una plantilla independiente: nuevas
relaciones, patrón, tema y layouts. Se conservaron los elementos de las
25 diapositivas y sus notas. Archivo de entrega: `Vision_Transformers_RECONSTRUIDO.pptx`;
las versiones principal y `_importar` también se sustituyeron por esta copia.

- Microsoft Open XML SDK 3.3.0: **cero errores**, 25 diapositivas.
- LibreOffice Impress 26.2.6: importación real y conversión de comprobación
  a ODP; 25 diapositivas y 25 notas reconocidas. Esa copia ODP es solo de QA.
- Comparación del contenido con un lector independiente: textos, posiciones,
  tamaños y notas iguales. Los 25 renders de artifact-tool son idénticos píxel
  por píxel antes y después de reconstruir el paquete.
- Canva y Google Slides: importación pendiente de confirmar. El validador
  oficial tampoco detectó errores en el paquete anterior; no se ha identificado
  todavía la causa específica del rechazo en esos importadores.

La versión anterior también pudo importarse en Impress. Por lo tanto, la
prueba local no reproduce el fallo informado en Canva/Google Slides y no
demuestra que su causa haya quedado resuelta. Se solicitó el mensaje exacto.


## Separación en repositorio independiente — 5 de octubre de 2026

- Raíz: `vision_transformers_openFrameworks/`. Contiene los dos sketches, su
  copia completa de `ofxLocalAI`, Python, instaladores y material de clase.
- `setup_vision.py` importa `vision/ollama_runtime.py`; no importa `setup_local.py`
  ni requiere archivos de la clase LLM. El instalador prepara solo ViT y Qwen3-VL.
- Traslado verificado por SHA-256 antes de adaptar documentación/scripts. Se
  conservaron el código C++, los recursos y los documentos binarios. La
  presentación conserva sus contenidos y se llama `Vision_Transformers_updated.pptx`.
- Instalación real desde la carpeta nueva en macOS Apple Silicon: Python 3.11,
  Torch 2.8.0, ViT comprobado en MPS y Qwen3-VL precargado en GPU mediante Ollama.
  El entorno nuevo utiliza su propio Python en `.tools`; no reutiliza el de LLM.
- `python -m pytest -q`: **25 passed**. Incluye contratos HTTP, arranque de Ollama,
  instaladores shell desde rutas con espacios y selección simulada de paquetes
  para macOS/Windows/Linux. Aviso de deprecación de Starlette sobre su integración
  con httpx; no impidió las pruebas.
- `tools/check_of_headers.py RUTA_A_OF`: sintaxis C++ correcta para addon,
  `visionViT` y `visionChat` contra OF 0.12.1 macOS. No se volvió a enlazar una app.
- Scripts shell: `bash -n` correcto. Enlaces locales de Markdown comprobados.
- Servidor ViT reiniciado desde esta carpeta: `/health` indica `ready: true`,
  dispositivo `mps`. POST `/classify` sobre la imagen incluida devuelve top 5.
- Consulta real imagen + texto a `qwen3-vl:2b-instruct`: respondió una descripción
  del círculo rojo y cuadrado azul de la imagen incluida.
- Windows y Linux: no se ejecutaron instalaciones nativas en esta comprobación;
  las pruebas simuladas no sustituyen una validación en esos sistemas.
- Git local inicializado en `main`, sin commit ni remoto. Pesos, entornos y logs
  excluidos. LLM conserva su versión publicada y su árbol Git quedó limpio.


## Lectura del código OF para clase — 5 de octubre de 2026

- Fuentes de los sketches ordenados con `.clang-format`: instrucciones separadas,
  sangría de cuatro espacios, declaraciones y funciones legibles. Comentarios en
  envío del prompt/imagen, llamada asíncrona, recepción y uso visual del resultado.
- Guía breve `docs/GUIA_CODIGO_OF.md`, incluida en ambos repositorios, con el
  recorrido de llmPoster, llmStage, visionViT y visionChat y ejercicios pequeños.
- Pedidos JSON de chat desglosados por campo, conservando mensajes y opciones.
  ViT ya no contiene el editor ni la animación de escritura inactivos heredados
  del ejemplo de chat; visionChat ya no conserva el atajo de parches sin dibujo.
- Comprobación de sintaxis C++ correcta contra OF 0.12.1 macOS para los cuatro
  ejemplos y sus addons; incluye ofxBox2d en llmStage.
- Pruebas C++ existentes de PosterSpec, ChatSession, SceneSpec y ofxTextReveal:
  compiladas y ejecutadas correctamente. No se recompilaron/enlazaron las apps
  completas ni se reemplazaron los fuentes de las copias externas en OF.


## Traslado a projects y preparación del primer commit — 5 de octubre de 2026

- Repositorio: `vision-transformers-models-openFrameworks-stages`, ubicado en
  `/Users/noeliaqualindi/projects/vision-transformers-models-openFrameworks-stages`.
- Guía de código separada por clase: aquí se explican visionViT y visionChat;
  la guía de llmPoster y llmStage permanece en el repositorio LLM.
- Entorno Python recreado en la ruta nueva; el instalador completó la inferencia
  de comprobación ViT y la precarga de Qwen3-VL. El entorno anterior se conservó
  como respaldo local ignorado por Git.
- Servidor ViT reiniciado desde la ubicación nueva; /health confirmó ready.
- Enlaces locales comprobados. Entornos, pesos, logs y respaldos quedan fuera de Git.
- Remoto SSH: `git@github.com:noequalindi/vision-transformers-models-openFrameworks-stages.git`.
  Archivos preparados en el índice para que el docente realice commit y push.
