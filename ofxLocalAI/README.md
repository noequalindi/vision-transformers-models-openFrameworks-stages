# ofxLocalAI

Addon para **conectar openFrameworks con modelos locales de texto, visión y
multimodales mediante HTTP/JSON**. La inferencia se ejecuta en Ollama o en el
servicio Python de ViT. El addon usa libcurl, incluido en el SDK OF utilizado
para la prueba, y entrega las respuestas de forma asíncrona.

| Método | Servicio | Uso |
| --- | --- | --- |
| `chat(request)` | Ollama, `/api/chat` | Texto con Qwen2.5 o imagen + pregunta con Qwen3-VL |
| `classifyImage(base64)` | Python ViT, `/classify` | Clasificación de una imagen |
| `listModels()` | Ollama, `/api/tags` | Consultar el catálogo local de Ollama |

El addon conecta con esos contratos concretos; otros modelos o servidores
pueden requerir un adaptador. Los servicios se inician por separado.

## Actualizar desde el nombre anterior

El addon antes se llamaba `ofxLocalLLM`. Ahora la carpeta, la clase C++ y el
archivo principal se llaman **ofxLocalAI**:

1. Copiar `ofxLocalAI/` a `OF/addons/ofxLocalAI/`.
2. En el proyecto actualizado, usar `ofxLocalAI` en `addons.make` y seleccionar
   ese addon en Project Generator; quitar la selección del nombre anterior.
3. Incluir `ofxLocalAI.h` y declarar el cliente como `ofxLocalAI`.
4. Pulsar Update en Project Generator y recompilar.

Los dos ejemplos de esta carpeta ya usan el nuevo nombre. Los métodos y
contratos HTTP conservan su comportamiento. Un proyecto antiguo puede seguir
necesitando la carpeta anterior hasta que se migren sus fuentes.

## Uso

- Agregar `ofxLocalAI` con Project Generator e incluir `ofxLocalAI.h`.
- Crear un miembro `ofxLocalAI llm` en `ofApp`.
- En `setup()`: registrar listeners de `llm.response` y `llm.error`; llamar
  `llm.setup("http://127.0.0.1:11434")`.
- Enviar con `llm.chat(request)` desde un evento de interacción.
- Llamar `llm.update()` en cada `ofApp::update()`.
- En `exit()`: `llm.close()` y retirar los listeners.

```cpp
ofJson request = {
    {"model", "qwen3-vl:2b-instruct"},
    {"messages", ofJson::array({
        {{"role", "user"}, {"content", "Inventá una frase sobre la lluvia"}}
    })}
};
llm.chat(request);
```

El evento `response` contiene `request: "chat"` y `body`, la respuesta de Ollama.
El texto está en `event["body"]["message"]["content"]`. Se puede pedir texto
libre o solicitar un formato estructurado. Validar la salida antes
de usarla en la experiencia.

`listModels()` consulta `/api/tags` y emite `request: "models"`.
`chat()` envía `/api/chat` con `stream: false`. `chat()` y `listModels()` devuelven
`false` si no se configuró el cliente o ya hay una solicitud pendiente.
El consumidor debe llamar `update()` para recibir y liberar esa solicitud.

## Hilos, límites y cierre

La red corre en un worker; los eventos se entregan en `update()` desde el hilo
principal. Llamar a la API del addon desde ese hilo. Una solicitud a la vez,
sin reenvíos automáticos. Conexión: hasta 5 s; catálogo: 10 s; chat: 180 s;
respuesta: hasta 1 MiB. Los errores HTTP y las respuestas incompletas se notifican
por `error`. `close()` interrumpe la transferencia y espera al worker; no envía
una orden para detener Ollama ni garantiza cancelar su inferencia.

El [ejemplo visionChat](../visionChat/README.md) muestra cómo enviar también una imagen.
Referencia: [API de chat de Ollama](https://docs.ollama.com/api/chat).

## Escritura progresiva opcional

`ofxTextReveal.h` no depende de OF ni consulta la red. Permite animar la respuesta
completa después de validarla, sin cortar caracteres UTF-8:

```cpp
// Miembro de ofApp (incluir ofxTextReveal.h):
ofxTextReveal typing;

// Al recibir un texto válido:
typing.start(respuesta, ofGetElapsedTimef(), 40); // caracteres por segundo

// En update():
typing.update(ofGetElapsedTimef());

// En draw():
ofDrawBitmapString(typing.visible(), 30, 100);
// typing.active(): quedan caracteres. typing.finish(): mostrar todo.
```

Esto **simula escritura**; no es streaming de tokens. Conservar la respuesta
completa para el historial y los datos visuales. El ejemplo comentado
[visionChat](../visionChat/README.md) muestra la respuesta con escritura progresiva.


## Extensión de visión

`ofxVisionImage.h` convierte los píxeles a JPEG/base64. `visionChat` incluye ese
texto en `messages[].images[]` de una consulta Ollama. `visionViT` configura
`setup("http://127.0.0.1:8768")` y llama `classifyImage(base64)`; recibe un evento
`request: "classification"` con `body.predictions`. Es el servicio Python ViT,
no Ollama. Usar instancias independientes si se consultan ambos a la vez.
El contrato de chat anterior no cambia. [Ejemplos completos](../vision/README.md).
