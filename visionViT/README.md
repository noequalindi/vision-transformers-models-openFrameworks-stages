# visionViT

**Modelo: 346 MB.** Para planificar la práctica, partir de **8 GB de RAM** y
CPU compatible con PyTorch; GPU opcional. Es una estimación, no un mínimo medido.
Ver [requisitos completos y espacio para instalar](../README.md#modelos-tamaño-y-requisitos-locales).

Ver [instalación, descarga, controles y recorrido del código](../vision/README.md).

Copiar esta carpeta completa a `OF/apps/myApps/visionViT` y actualizar
`OF/addons/ofxLocalAI`. Importar en Project Generator con addon `ofxLocalAI`.

Iniciar `start_vision` desde la raíz de la clase antes de ejecutar.

El modelo es ViT Base: imagen → cinco categorías. P muestra la cuadrícula de
parches de entrada; no muestra atención ni detecciones.

**Recargar ejemplo** (arriba a la derecha) vuelve a `sample.png`, detiene la
cámara y limpia la respuesta y la cuadrícula. Se habilita cuando termina el
pedido pendiente; Enter vuelve a consultar al modelo.
