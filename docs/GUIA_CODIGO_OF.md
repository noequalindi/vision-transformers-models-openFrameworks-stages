# De la visión a una interacción en OF

**Guía breve para explicar el código de esta clase:** `visionViT` y `visionChat`.
Abrir los ejemplos y seguir las funciones indicadas. No hace falta recorrer el servidor.

> “El modelo devuelve datos. Nuestro código decide qué hacer con ellos: mostrar
> palabras, cambiar colores, mover formas o construir una escena física.”

## 1. El recorrido común — mostrarlo una vez

Abrir `src/ofApp.cpp` de un ejemplo y buscar estas funciones:

| Función | Qué explicar |
| --- | --- |
| `setup()` | Configuramos el cliente y registramos `response()` y `error()`: qué función llamar cuando llegue el resultado. |
| `send()` | Armamos el pedido y lo enviamos al presionar Enter o un botón. |
| `update()` | `client.update()` entrega los eventos recibidos. La animación sigue mientras esperamos. |
| `response()` | Leemos y validamos los datos; después modificamos el estado de nuestra obra. |
| `draw()` | Dibujamos ese estado en cada frame, sin consultar otra vez al modelo. |

**Clave:** `pending = client.chat(request)` (Chat) o
`pending = client.classifyImage(encoded)` (ViT) devuelve un booleano que indica si el
addon aceptó el envío. **La respuesta no está en ese booleano**: llega después a
`response()`. Es como hacer un pedido y recibirlo cuando llaman al timbre.

En los ejemplos, los comentarios **PROMPT**, **LLAMADA AL MODELO** y
**USAR LA RESPUESTA** señalan esos puntos. `ofApp.h` guarda las variables que
deben sobrevivir entre un evento y el siguiente frame.

## 2. visionViT — una clasificación controla un gráfico

**Abrir:** `visionViT/src/ofApp.cpp`.

1. **`send()`** obtiene una captura, la ajusta a 224 × 224 y la codifica como
   JPEG/base64. **Este ejemplo no lleva prompt de texto.**
2. La llamada es **`pending = client.classifyImage(encoded)`**.
3. **`response()`** lee `event["body"]["predictions"]`: cinco elementos con
   `label` y `score`. Valida los datos y los guarda con **`result = candidate`**.
4. En **`draw()`**, buscar el bucle `for (const auto& row : result["predictions"])`.
   **`530 * score`** transforma el puntaje en ancho de barra.

**Qué decir:** “Ahora tenemos números que podemos mapear a tamaño, color o
velocidad. El score corresponde a una hipótesis sobre la imagen completa;
no indica la posición de un objeto ni qué porcentaje de la foto ocupa.”

**Mostrar y modificar:** capturar el mismo objeto con dos encuadres. En el bucle
de barras, después de leer `score`, reemplazar el color de la barra de resultado por:

```cpp
const float hue = ofMap(score, 0.0f, 1.0f, 150.0f, 210.0f, true);
ofSetColor(ofColor::fromHsb(hue, 170, 240));
// Conservar el ofDrawRectangle(...) que usa 530 * score.
```

Así una misma respuesta controla ancho y color. La regla visual es nuestra.

## 3. visionChat — imagen + pregunta, respuesta escrita

**Abrir:** `visionChat/src/ofApp.cpp`.

1. En **`send()`**, `question` es el prompt de la persona. El mensaje `user`
   contiene **`content: question`** y **`images: [encoded]`**: enviamos píxeles,
   no el nombre del archivo. El mensaje `system` fija instrucciones generales.
2. La llamada es **`pending = client.chat(request)`**. Cada consulta lleva una
   imagen y una pregunta; este ejemplo no reenvía historial.
3. **`response()`** obtiene **`answer`** desde `body.message.content` y valida su
   tamaño. Ahí está el texto completo que podemos reutilizar.
4. **`typing.start(answer, ..., 45)`** inicia la presentación. `update()` la
   avanza y **`draw()` muestra `typing.visible()`**. Es escritura animada local;
   el HTTP usa `stream: false`.

**Qué decir:** “Podemos usar la respuesta como título, subtítulo o material de
una composición. El lugar para guardar esa decisión es `response()`; el lugar
para dibujarla es `draw()`.”

**Ejercicio para agregar una interacción** — estos fragmentos son una propuesta,
no están incorporados al sketch:

```cpp
// 1. En ofApp.h, dentro de private: guardar el estado entre frames.
float responseRadius = 12.0f;

// 2. En response(), después de validar answer:
const auto words = ofSplitString(answer, " ", true, true);
responseRadius = ofMap(words.size(), 0, 120, 12, 60, true);

// 3. Al final de draw(), antes del bloque de captura --preview:
ofPushStyle();
ofFill();
ofSetColor(134, 207, 244, 140);
ofDrawCircle(ofGetMouseX(), ofGetMouseY(), responseRadius);
ofPopStyle();
```

La longitud aproximada de la respuesta cambia el tamaño de una forma que sigue
al mouse. Es una decisión artística explícita, no una detección de emociones.
Para reiniciarla con **RECARGAR EJEMPLO**, agregar `responseRadius = 12.0f` en
`loadImage()` después de cargar correctamente la imagen.

## Cierre — qué deben llevarse para construir su obra

> “Elegimos una entrada, consultamos una vez por acción, validamos la respuesta
> y la convertimos en variables de nuestra experiencia. OF anima esas variables
> continuamente. Cambiar la obra no exige reescribir la conexión.”

- Conservar `setup()` con sus listeners, el cliente en `ofApp.h`, su `update()`
  y el cierre en `exit()`. Modificar principalmente `send()`, `response()` y el dibujo.
- No enviar desde `draw()`: actualizar el estado una vez por respuesta y dibujarlo en cada frame.
- No usar el texto generado como código ejecutable. Para acciones concretas,
  pedir datos definidos y validarlos antes de modificar la obra.
- Editar **la copia que se compila** en `OF/apps/myApps/`, o copiar allí los fuentes
  actualizados antes de recompilar. Un cambio en la carpeta de clase no actualiza esa copia.
