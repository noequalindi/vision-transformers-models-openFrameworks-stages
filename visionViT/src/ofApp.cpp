#include "ofApp.h"

namespace
{
const ofRectangle imageArea(28, 112, 530, 480);
const ofRectangle sendButton(930, 680, 310, 62);
const ofRectangle instructionsPanel(28, 680, 880, 62);
const ofRectangle reloadButton(980, 32, 260, 42);

// Helpers de interfaz. Cambiar esta capa no cambia el modelo ni su conexión.
std::string wrap(const std::string& text, int columns, int limit = 22)
{
    std::string out;
    int col = 0;
    int line = 1;

    for (auto cp : ofUTF8Iterator(text))
    {
        if (cp == '\r')
        {
            continue;
        }

        if (cp == '\n' || col >= columns)
        {
            if (++line > limit)
            {
                return out + "...";
            }

            out += '\n';
            col = 0;

            if (cp == '\n')
            {
                continue;
            }
        }

        ofUTF8Append(out, cp);
        ++col;
    }

    return out;
}

void drawFit(ofImage& image, const ofRectangle& area)
{
    if (!image.isAllocated())
    {
        return;
    }

    ofRectangle rect(0, 0, image.getWidth(), image.getHeight());
    rect.scaleTo(area);

    ofSetColor(255);
    image.draw(rect);
}

} // namespace

// 1. CONECTAR. No descargar pesos ni consultar al modelo dentro de draw().
void ofApp::setup()
{
    ofSetFrameRate(60);
    ofSetVerticalSync(true);
    ofSetEscapeQuitsApp(false);
    ofSetWindowTitle("UNA / VISION ViT / imagen -> categorias");

    try
    {
        auto config = ofLoadJson("connection.json");
        url = config.at("url").get<std::string>();
        model = config.at("model").get<std::string>();
        ofAddListener(client.response, this, &ofApp::response);
        ofAddListener(client.error, this, &ofApp::error);
        client.setup(url);
        loadImage(ofToDataPath("sample.png", true));

        if (check)
        {
            send();
        }
    }
    catch (const std::exception& e)
    {
        status = e.what();

        if (check)
        {
            ofExit(1);
        }
    }
}

// 2. ENTRADA. La imagen permanece local, se envía solo al presionar ANALIZAR.
void ofApp::loadImage(const std::string& path)
{
    if (pending)
    {
        return;
    }

    ofImage image;

    if (!image.load(path))
    {
        status = "No se pudo abrir la imagen (usar JPG o PNG)";
        return;
    }

    source.setFromPixels(ofxVisionResize(image.getPixels()));
    camera.close();
    usingCamera = false;
    snapshot.clear();
    result = nullptr;
    detail.clear();
    showPatches = false;
    status = "Imagen cargada / todavia sin inferencia";
    sample = true;
}

// Volver a la imagen incluida permite repetir la demo sin reiniciar la app.
// loadImage limpia la captura, la respuesta y la cámara.
// Mientras esperamos HTTP, no reemplazamos la imagen asociada a ese pedido.
void ofApp::reloadExample()
{
    if (pending)
    {
        return;
    }

    loadImage(ofToDataPath("sample.png", true));
}

// 2b. ENVIAR: ViT no recibe un prompt; clasifica los píxeles de esta captura.
void ofApp::send()
{
    if (pending || !source.isAllocated())
    {
        return;
    }

    try
    {
        auto pixels = ofxVisionResize(source.getPixels());
        pixels.resize(224, 224); // Misma resolución cuadrada que el preprocesador ViT.
        const auto encoded = ofxVisionJpeg(pixels);

        // LLAMADA AL MODELO: el addon envía {image: base64} a /classify.
        // El bool indica que aceptó el envío; las categorías llegan luego a response().
        pending = client.classifyImage(encoded);

        if (pending)
        {
            snapshot.setFromPixels(pixels);
            sentAt = ofGetElapsedTimef();
            status = "Analizando la imagen...";
            detail.clear();
            result = nullptr;
            sample = false;
        }
    }
    catch (const std::exception& e)
    {
        status = e.what();
    }
}

// 3. ACTUALIZAR. La cámara y el dibujo siguen vivos mientras espera HTTP.
void ofApp::update()
{
    // Entrega los eventos de red a response()/error() en el hilo principal de OF.
    client.update();

    if (usingCamera)
    {
        camera.update();

        if (camera.isFrameNew())
        {
            source.setFromPixels(camera.getPixels());
        }
    }

    if (check && ofGetElapsedTimef() > 190)
    {
        ofLogError() << "VISION_TIMEOUT";
        ofExit(1);
    }
}

// 4. RESPUESTA. Este es el lugar para conectar los datos con la obra del alumno.
void ofApp::response(ofJson& event)
{
    pending = false;

    try
    {
        const auto candidate = event.at("body");
        const auto& predictions = candidate.at("predictions");

        if (!predictions.is_array() || predictions.size() != 5)
        {
            throw std::runtime_error("Se esperan cinco categorias");
        }

        for (const auto& row : predictions)
        {
            const auto label = row.at("label").get<std::string>();
            const double score = row.at("score").get<double>();

            if (label.empty() || label.size() > 300 || !std::isfinite(score) || score < 0 ||
                score > 1)
            {
                throw std::runtime_error("Categoria o score invalido");
            }
        }

        // USAR LA RESPUESTA: guardar solo después de validar todas las categorías.
        // Para otra obra, convertir aquí label/score en un estado: color, tamaño, sonido.
        // draw() reutiliza este estado en cada frame, sin volver a consultar al modelo.
        result = candidate;
        status = "Respuesta recibida / " + model;

        if (check)
        {
            ofLogNotice() << "VISION_CONTRACT_OK";
            ofExit(0);
        }
    }
    catch (const std::exception& e)
    {
        detail = e.what();
        status = "Respuesta rechazada. Esc y E: diagnostico";

        if (check)
        {
            ofExit(1);
        }
    }
}

void ofApp::error(std::string& message)
{
    pending = false;
    detail = message;
    status = "No se pudo analizar. Esc y E: diagnostico";

    if (check)
    {
        ofLogError() << message;
        ofExit(1);
    }
}

void ofApp::recorded()
{
    if (pending)
    {
        return;
    }

    try
    {
        result = ofLoadJson("recorded.json");
        snapshot.setFromPixels(source.getPixels());

        sample = true;
        status = "DATOS DIDACTICOS / SIN INFERENCIA / no describen necesariamente esta imagen";
    }
    catch (const std::exception& e)
    {
        status = e.what();
    }
}

// 5. REPRESENTAR. El modelo devuelve datos; estos gráficos están programados en C++.
void ofApp::draw()
{
    ofBackground(17, 24, 43);

    ofSetColor(230, 237, 252);
    ofDrawBitmapString("UNA / INFORMATICA APLICADA 2", 28, 31);
    ofDrawBitmapString("VISION ViT / imagen -> categorias", 28, 67);
    const bool reloadHovered = reloadButton.inside(ofGetMouseX(), ofGetMouseY());

    ofSetColor(pending         ? ofColor(40, 48, 64)
               : reloadHovered ? ofColor(54, 99, 158)
                               : ofColor(38, 70, 118));
    ofDrawRectRounded(reloadButton, 8);

    ofSetColor(pending ? ofColor(130, 145, 167) : ofColor(238, 244, 255));
    ofDrawBitmapString("RECARGAR EJEMPLO", reloadButton.x + 24, reloadButton.y + 26);

    ofSetColor(167, 195, 221);
    ofDrawBitmapString(
        pending ? "Disponible al terminar" : "Volver a la imagen inicial", reloadButton.x, 94);

    ofSetColor(32, 47, 72);
    ofDrawRectRounded(imageArea, 12);
    drawFit(snapshot.isAllocated() ? snapshot : source, imageArea);

    if (showPatches && snapshot.isAllocated())
    {
        // 14 x 14 patches de entrada. NO es atención ni segmentación del modelo.
        ofRectangle grid(0, 0, snapshot.getWidth(), snapshot.getHeight());
        grid.scaleTo(imageArea);

        ofSetColor(120, 255, 216, 150);

        for (int i = 0; i <= 14; ++i)
        {
            ofDrawLine(grid.x + i * grid.width / 14,
                       grid.y,
                       grid.x + i * grid.width / 14,
                       grid.getBottom());
            ofDrawLine(grid.x,
                       grid.y + i * grid.height / 14,
                       grid.getRight(),
                       grid.y + i * grid.height / 14);
        }
    }

    ofSetColor(220, 232, 248);
    ofDrawBitmapString(snapshot.isAllocated() ? "IMAGEN ENVIADA / respuesta asociada a esta captura"
                                              : "VISTA PREVIA / sin enviar",
                       28,
                       615);
    ofDrawBitmapString("O: abrir imagen | C: camara | R: ejemplo grabado | P: patches", 28, 642);
    ofDrawBitmapString(sample ? "SIN INFERENCIA / DATOS DIDACTICOS" : "MODELO: " + model, 590, 115);
    ofDrawBitmapString("TOP 5 / entre 1000 clases ImageNet", 590, 155);

    if (result.is_object() && result.contains("predictions"))
    {
        int i = 0;

        for (const auto& row : result["predictions"])
        {
            const float y = 202 + i++ * 65;

            ofSetColor(218, 229, 249);
            ofDrawBitmapString(wrap(row["label"].get<std::string>(), 62, 1), 590, y);

            // DATO -> GRÁFICO: el score [0, 1] controla el ancho de esta barra.
            // Cambiar este mapeo para que controle otra propiedad de la obra.
            const float score = row["score"].get<float>();

            ofSetColor(43, 59, 82);
            ofDrawRectangle(590, y + 12, 530, 13);

            ofSetColor(134, 207, 244);
            ofDrawRectangle(590, y + 12, 530 * score, 13);
            ofDrawBitmapString(ofToString(score * 100, 1) + "%", 1136, y + 23);
        }

        ofSetColor(167, 195, 221);
        ofDrawBitmapString(
            "Dispositivo: " + result.value("device", std::string("grabado")), 590, 554);
    }

    ofSetColor(167, 195, 221);
    ofDrawBitmapString("El score no garantiza acierto. No hay cajas ni tracking.", 590, 579);

    if (pending)
    {
        ofSetColor(143, 206, 246);
        ofDrawBitmapString(
            "Analizando... " + ofToString(int(ofGetElapsedTimef() - sentAt)) + " s", 590, 600);

        for (int i = 0; i < 3; ++i)
        {
            ofDrawCircle(596 + i * 16, 626, 3 + 1.4f * std::sin(ofGetElapsedTimef() * 5 - i));
        }
    }

    ofSetColor(31, 44, 68);
    ofDrawRectRounded(instructionsPanel, 8);

    ofSetColor(230, 238, 255);
    ofDrawBitmapString(
        wrap(std::string(
                 "Comparar encuadres, fondos y luz. La imagen completa recibe una categoria."),
             102,
             3),
        42,
        702);

    ofSetColor(pending ? ofColor(55, 66, 86) : ofColor(45, 87, 149));
    ofDrawRectRounded(sendButton, 8);

    ofSetColor(255);
    ofDrawBitmapString(pending ? "ANALIZANDO..." : "ANALIZAR / ENTER", 953, 716);

    ofSetColor(184, 205, 229);
    ofDrawBitmapString(wrap(status, 148, 2), 28, 771);

    if (!preview.empty() && ofGetFrameNum() == 60)
    {
        ofSaveScreen(preview);
        ofExit();
    }
}

void ofApp::mousePressed(int x, int y, int button)
{
    if (reloadButton.inside(x, y))
    {
        reloadExample();
        return;
    }

    if (sendButton.inside(x, y))
    {
        send();
    }
}

void ofApp::dragEvent(ofDragInfo info)
{
    if (!info.files.empty())
    {
        loadImage(info.files.front());
    }
}

void ofApp::keyPressed(int key)
{
    if (key == OF_KEY_RETURN)
    {
        send();
        return;
    }

    if (key == 'e' || key == 'E')
    {
        ofSetClipboardString(status + "\n" + detail);
    }

    if (key == 'p' || key == 'P')
    {
        showPatches = !showPatches;
    }

    if (pending)
    {
        return;
    }

    if (key == 'o' || key == 'O')
    {
        auto file = ofSystemLoadDialog("Seleccionar JPEG o PNG");

        if (file.bSuccess)
        {
            loadImage(file.getPath());
        }
    }

    if (key == 'r' || key == 'R')
    {
        recorded();
    }

    if (key == 'c' || key == 'C')
    {
        if (usingCamera)
        {
            camera.close();
            usingCamera = false;
            status = "Camara detenida";
            return;
        }

        auto config = ofLoadJson("connection.json");
        camera.setDeviceID(config.value("camera", 0));
        usingCamera = camera.setup(640, 480);
        snapshot.clear();
        result = nullptr;
        sample = true;
        status = usingCamera
                     ? "Camara activa / Enter captura y envia"
                     : "No se pudo abrir camara: revisar permisos y camera en connection.json";
    }
}

void ofApp::exit()
{
    client.close();
    camera.close();
    ofRemoveListener(client.response, this, &ofApp::response);
    ofRemoveListener(client.error, this, &ofApp::error);
}
