# visionChat

**Modelo: 1,89 GB.** Para planificar la práctica, partir de **8 GB de RAM** con
poco margen; **16 GB recomendados**. GPU opcional, CPU con mayor espera. Estas
cifras de RAM son estimaciones, no mínimos medidos.
Ver [requisitos completos y espacio para instalar](../README.md#modelos-tamaño-y-requisitos-locales).

Ver [instalación, descarga, controles y recorrido del código](../vision/README.md).

Copiar esta carpeta completa a `OF/apps/myApps/visionChat` y actualizar
`OF/addons/ofxLocalAI`. Importar en Project Generator con addon `ofxLocalAI`.

Mantener Ollama abierto; no necesita el servidor ViT.

El modelo es Qwen3-VL 2B Instruct: imagen + pregunta → texto.
Cada consulta es independiente. Esc sale del editor para usar los atajos.

**Recargar ejemplo** (arriba a la derecha) vuelve a `sample.png`, detiene la
cámara y limpia la respuesta. Conserva la pregunta escrita. Se habilita cuando
termina el pedido pendiente; Enter vuelve a consultar al modelo.
