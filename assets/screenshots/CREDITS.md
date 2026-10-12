# Capturas de los ejemplos de visión

Las capturas se obtuvieron el 12 de octubre de 2026 ejecutando los sketches de
openFrameworks con sus modelos locales. Se cargó la foto con la misma ruta de
procesamiento que usa la tecla **O**. La cámara no intervino.

- `vision-vit-cat.png`: `google/vit-base-patch16-224` sobre MPS. Primera categoría:
  `tabby, tabby cat`, score 0,475664. Muestra las cinco categorías devueltas por el modelo.
- `vision-chat-cat.png`: `qwen3-vl:2b-instruct` en Ollama. Pregunta:
  «Describe el animal, su pelaje y el entorno en una frase corta.»
  La respuesta visible fue generada por el modelo, sin reemplazarla por texto escrito a mano.
- `cat.jpg`: foto original para repetir la prueba. Las interfaces la redimensionan;
  ViT muestra la entrada de 224 × 224 y Chat conserva su proporción.

## Foto y licencia

**Felis catus-cat on snow.jpg**, de **Von.grzanka**.
[Fuente en Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Felis_catus-cat_on_snow.jpg).
Licencia elegida: [Creative Commons Attribution-ShareAlike 3.0](https://creativecommons.org/licenses/by-sa/3.0/).

La fotografía original se incluye sin cambios. En las capturas aparece
redimensionada e integrada en la interfaz. Las dos capturas se distribuyen
bajo CC BY-SA 3.0; conservar esta atribución al reutilizarlas. Esto no modifica
la licencia del código ni la de los modelos.
