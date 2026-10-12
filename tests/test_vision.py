"""Pruebas del contrato HTTP sin modelos, GPU ni descargas."""
import base64,io,sys
from pathlib import Path
import pytest
from PIL import Image
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from vision.images import decode_image
from vision.server import create_app
from setup_vision import version_tuple

def encoded():
    buffer=io.BytesIO();Image.new('RGB',(32,20),'red').save(buffer,format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()
class FakeClassifier:
    device='cpu'
    def classify(self,image):
        assert image.size==(32,20) and image.mode=='RGB'
        return {'predictions':[{'label':'red','score':.8}], 'device':'cpu'}

def test_decode():
    assert decode_image(encoded()).size==(32,20)
@pytest.mark.parametrize('value',['', 'data:image/png;base64,xxx', '!!!!', 'eHl6', None])
def test_bad_images(value):
    with pytest.raises(ValueError):decode_image(value)
def test_health_and_request():
    with TestClient(create_app(FakeClassifier())) as c:
        assert c.get('/health').json()['service']=='una-vit'
        result=c.post('/classify',json={'image':encoded()})
        assert result.status_code==200 and result.json()['device']=='cpu'
        assert c.post('/classify',json={'image':encoded(),'extra':1}).status_code==422
        assert c.post('/classify',json=['no']).status_code==422
        assert c.post('/classify',content='not json').status_code==422
        assert c.post('/classify',json={'image':'bad'}).status_code==422
        assert c.post('/classify',content=b'x'*6_000_000).status_code==413

def test_failure_releases_lock():
    class FailsOnce(FakeClassifier):
        failed=False
        def classify(self,image):
            if not self.failed:self.failed=True;raise RuntimeError('fake failure')
            return super().classify(image)
    with TestClient(create_app(FailsOnce())) as c:
        assert c.post('/classify',json={'image':encoded()}).status_code==500
        assert c.post('/classify',json={'image':encoded()}).status_code==200

def test_version():
    assert version_tuple('0.12.7')==(0,12,7)
    assert version_tuple('0.30.8-rc1')>(0,12,7)
    with pytest.raises(RuntimeError):version_tuple('invalid')
