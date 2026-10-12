#pragma once
#include "ofMain.h"
#include "ofxLocalAI.h"
#include "ofxVisionImage.h"

class ofApp : public ofBaseApp {
public:
    void setup() override;
    void update() override;
    void draw() override;
    void exit() override;
    void keyPressed(int key) override;
    void mousePressed(int x, int y, int button) override;
    void dragEvent(ofDragInfo info) override;

    // Conexión: enviar una vez por acción, recibir y actualizar el estado visual.
    void send();
    void response(ofJson& event);
    void error(std::string& message);
    void loadImage(const std::string& path);
    void recorded();
    void reloadExample();

    // Opciones de comprobación usadas por las herramientas de desarrollo.
    bool check = false;
    std::string preview;

private:
    ofxLocalAI client; // HTTP en otro hilo; update entrega eventos en el hilo de OF.
    ofVideoGrabber camera;
    // La respuesta siempre se muestra junto a la imagen enviada.
    ofImage source;
    ofImage snapshot;
    ofJson result; // Última clasificación validada: draw() la convierte en barras.
    std::string url;
    std::string model;
    std::string status = "Cargar una imagen o activar la camara";
    std::string detail;
    bool pending = false;
    bool usingCamera = false;
    bool showPatches = false;
    bool sample = true;
    double sentAt = 0;
};
