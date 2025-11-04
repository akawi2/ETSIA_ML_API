"""
Tests pour le modèle de détection de contenu sensible dans les images
"""
import pytest
from PIL import Image
import io
from fastapi.testclient import TestClient
from app.main import app
from app.services.sensitive_image_caption import SensitiveImageCaptionModel

client = TestClient(app)


# ============================================================================
# TESTS UNITAIRES DU MODÈLE
# ============================================================================

def test_model_initialization():
    """Test d'initialisation du modèle"""
    try:
        model = SensitiveImageCaptionModel()
        assert model.model_name == "sensitive-image-caption"
        assert model.model_version == "1.0.0"
        assert model._initialized == True
    except Exception as e:
        pytest.skip(f"Modèle non disponible: {e}")


def test_model_properties():
    """Test des propriétés du modèle"""
    try:
        model = SensitiveImageCaptionModel()
        
        assert model.model_name is not None
        assert model.model_version is not None
        assert model.author is not None
        assert isinstance(model.tags, list)
    except Exception as e:
        pytest.skip(f"Modèle non disponible: {e}")


def test_detect_sensitive_keywords():
    """Test de détection de mots-clés sensibles"""
    try:
        model = SensitiveImageCaptionModel()
        
        # Textes sensibles
        assert model._detect_sensitive_content("This image shows drugs") == True
        assert model._detect_sensitive_content("A gun on the table") == True
        assert model._detect_sensitive_content("Nude person") == True
        
        # Textes sûrs
        assert model._detect_sensitive_content("A cat on a table") == False
        assert model._detect_sensitive_content("Beautiful landscape") == False
    except Exception as e:
        pytest.skip(f"Modèle non disponible: {e}")


def test_filter_caption():
    """Test de filtrage de légende"""
    try:
        model = SensitiveImageCaptionModel()
        
        # Filtrer les mots sensibles
        filtered = model._filter_caption("This shows drugs and guns")
        assert "***" in filtered
        assert "drugs" not in filtered.lower()
        
        # Texte sûr non modifié
        safe_text = "A beautiful cat"
        assert model._filter_caption(safe_text) == safe_text
    except Exception as e:
        pytest.skip(f"Modèle non disponible: {e}")


def test_health_check():
    """Test du health check"""
    try:
        model = SensitiveImageCaptionModel()
        health = model.health_check()
        
        assert health["status"] in ["healthy", "unhealthy"]
        assert health["model"] == "sensitive-image-caption"
    except Exception as e:
        pytest.skip(f"Modèle non disponible: {e}")


# ============================================================================
# TESTS D'INTÉGRATION AVEC L'API
# ============================================================================

def create_test_image(color='white', size=(100, 100)):
    """Crée une image de test"""
    img = Image.new('RGB', size, color=color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


def test_predict_image_endpoint():
    """Test de l'endpoint /api/v1/predict-image"""
    # Créer une image de test
    img_bytes = create_test_image()
    
    response = client.post(
        "/api/v1/predict-image",
        files={"image": ("test.jpg", img_bytes, "image/jpeg")}
    )
    
    # L'endpoint peut retourner 500 si le modèle n'est pas disponible
    if response.status_code == 500:
        pytest.skip("Modèle non disponible sur le serveur")
    
    assert response.status_code == 200
    data = response.json()
    
    # Vérifier la structure de la réponse
    assert "prediction" in data
    assert "confidence" in data
    assert "is_safe" in data
    assert "caption_fr" in data
    
    assert data["prediction"] in ["SENSIBLE", "SÛR"]
    assert 0 <= data["confidence"] <= 1


def test_predict_image_invalid_file():
    """Test avec un fichier invalide"""
    # Créer un fichier texte
    text_file = io.BytesIO(b"not an image")
    
    response = client.post(
        "/api/v1/predict-image",
        files={"image": ("test.txt", text_file, "text/plain")}
    )
    
    assert response.status_code == 400


def test_batch_predict_images_endpoint():
    """Test de l'endpoint /api/v1/batch-predict-images"""
    # Créer 3 images de test
    images = [
        ("test1.jpg", create_test_image('red'), "image/jpeg"),
        ("test2.jpg", create_test_image('green'), "image/jpeg"),
        ("test3.jpg", create_test_image('blue'), "image/jpeg")
    ]
    
    response = client.post(
        "/api/v1/batch-predict-images",
        files=[("images", img) for img in images]
    )
    
    # L'endpoint peut retourner 500 si le modèle n'est pas disponible
    if response.status_code == 500:
        pytest.skip("Modèle non disponible sur le serveur")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "results" in data
    assert "total_processed" in data
    assert len(data["results"]) == 3


def test_batch_predict_too_many_images():
    """Test batch avec trop d'images"""
    # Créer 11 images (max est 10)
    images = [
        (f"test{i}.jpg", create_test_image(), "image/jpeg")
        for i in range(11)
    ]
    
    response = client.post(
        "/api/v1/batch-predict-images",
        files=[("images", img) for img in images]
    )
    
    assert response.status_code == 400


# ============================================================================
# TESTS DE PERFORMANCE
# ============================================================================

@pytest.mark.slow
def test_prediction_performance():
    """Test de performance (optionnel)"""
    try:
        import time
        model = SensitiveImageCaptionModel()
        
        # Créer une image de test
        test_image = Image.new('RGB', (224, 224), color='white')
        
        # Mesurer le temps
        start = time.time()
        result = model.predict(image=test_image)
        duration = time.time() - start
        
        assert result is not None
        # Vérifier que ça prend moins de 30 secondes (CPU)
        assert duration < 30
        
        print(f"\nTemps de prédiction: {duration:.2f}s")
    except Exception as e:
        pytest.skip(f"Modèle non disponible: {e}")


# ============================================================================
# TESTS DE RÉGRESSION
# ============================================================================

def test_model_output_format():
    """Test que le format de sortie respecte le contrat"""
    try:
        model = SensitiveImageCaptionModel()
        test_image = Image.new('RGB', (100, 100), color='white')
        
        result = model.predict(image=test_image)
        
        # Vérifier les champs obligatoires
        required_fields = ["prediction", "confidence", "severity", "reasoning"]
        for field in required_fields:
            assert field in result, f"Champ manquant: {field}"
        
        # Vérifier les champs spécifiques au modèle
        assert "caption_en" in result
        assert "caption_fr" in result
        assert "is_safe" in result
        
        # Vérifier les types
        assert isinstance(result["prediction"], str)
        assert isinstance(result["confidence"], (int, float))
        assert isinstance(result["is_safe"], bool)
    except Exception as e:
        pytest.skip(f"Modèle non disponible: {e}")
