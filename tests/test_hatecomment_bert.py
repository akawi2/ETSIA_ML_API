"""
Tests pour le modèle HateComment BERT
"""
import pytest
from app.services.hatecomment_bert import HateCommentBertModel


def test_model_initialization():
    """Test d'initialisation du modèle"""
    model = HateCommentBertModel()
    assert model.model_name == "hatecomment-bert"
    assert model.model_version == "1.1.0"
    assert model.author == "Équipe ETSIA"
    assert "bert" in model.tags
    assert "multilingual" in model.tags


def test_model_predict_basic():
    """Test de prédiction basique"""
    model = HateCommentBertModel()
    
    # Test avec un texte neutre
    result = model.predict("Hello, how are you today?")
    
    assert "prediction" in result
    assert "confidence" in result
    assert "severity" in result
    assert "reasoning" in result
    assert result["prediction"] in ["HAINEUX", "NON-HAINEUX", "ERREUR"]
    assert 0 <= result["confidence"] <= 1


def test_model_predict_empty_text():
    """Test avec texte vide"""
    model = HateCommentBertModel()
    result = model.predict("")
    
    assert result["prediction"] == "NON-HAINEUX"
    assert result["confidence"] == 0.5
    assert "vide" in result["reasoning"].lower()


def test_model_predict_hate_speech():
    """Test avec du contenu potentiellement haineux"""
    model = HateCommentBertModel()
    
    # Test avec un texte potentiellement haineux
    result = model.predict("I hate everyone and everything")
    
    assert "prediction" in result
    assert "hate_classification" in result
    assert "original_label" in result


def test_model_batch_predict():
    """Test de prédiction batch"""
    model = HateCommentBertModel()
    
    texts = [
        "I'm feeling great today!",
        "I hate this world",
        "Normal conversation here"
    ]
    
    results = model.batch_predict(texts)
    
    assert len(results) == 3
    for result in results:
        assert "prediction" in result
        assert "confidence" in result
        assert result["prediction"] in ["HAINEUX", "NON-HAINEUX", "ERREUR"]


def test_model_health_check():
    """Test du health check"""
    model = HateCommentBertModel()
    health = model.health_check()
    
    assert "status" in health
    assert "model" in health
    assert health["model"] == "hatecomment-bert"
    assert health["status"] in ["healthy", "unhealthy"]


def test_model_info():
    """Test des informations du modèle"""
    model = HateCommentBertModel()
    info = model.get_info()
    
    assert info["name"] == "hatecomment-bert"
    assert info["version"] == "1.1.0"
    assert info["author"] == "Équipe ETSIA"
    assert isinstance(info["tags"], list)


if __name__ == "__main__":
    # Tests rapides pour développement
    print("Test d'initialisation...")
    model = HateCommentBertModel()
    print(f"✓ Modèle initialisé: {model.model_name}")
    
    print("\nTest de prédiction...")
    result = model.predict("I feel sad and hopeless")
    print(f"✓ Prédiction: {result}")
    
    print("\nTest health check...")
    health = model.health_check()
    print(f"✓ Health: {health}")
    
    print("\nTous les tests passés !")
