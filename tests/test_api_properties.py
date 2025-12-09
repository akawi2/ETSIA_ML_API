"""
Property-Based Tests for API Interface Consistency and Backward Compatibility

Feature: optimized-llm-architecture
Tests Properties 8 and 16 from the design document.
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from fastapi.testclient import TestClient
from app.main import app
from app.core.model_registry import registry
from app.core.base_model import BaseMLModel
from typing import Dict, Any, List
import time

# Create test client
client = TestClient(app)


# ============================================================================
# MOCK MODELS FOR TESTING
# ============================================================================

class MockDetectionModel(BaseMLModel):
    """Mock detection model for testing"""
    
    def __init__(self, name: str = "mock-detection"):
        self._name = name
        self._initialized = True
    
    @property
    def model_name(self) -> str:
        return self._name
    
    @property
    def model_version(self) -> str:
        return "1.0.0-test"
    
    @property
    def author(self) -> str:
        return "Test Suite"
    
    @property
    def description(self) -> str:
        return f"Mock detection model: {self._name}"
    
    @property
    def tags(self) -> List[str]:
        return ["mock", "test"]
    
    def predict(self, text: str, include_reasoning: bool = True, **kwargs) -> Dict[str, Any]:
        """Mock prediction"""
        confidence = 0.85 if "sad" in text.lower() or "depressed" in text.lower() else 0.15
        prediction = "DÉPRESSION" if confidence > 0.5 else "NORMAL"
        severity = "Élevée" if confidence > 0.8 else "Faible" if confidence > 0.5 else "Aucune"
        
        result = {
            "prediction": prediction,
            "confidence": confidence,
            "severity": severity,
            "processing_time": 25.0
        }
        
        if include_reasoning:
            result["reasoning"] = f"Mock reasoning for {prediction}"
        
        return result
    
    def batch_predict(self, texts: List[str], include_reasoning: bool = False, **kwargs) -> List[Dict[str, Any]]:
        """Mock batch prediction"""
        return [self.predict(text, include_reasoning) for text in texts]
    
    def health_check(self) -> Dict[str, Any]:
        """Mock health check"""
        return {
            "status": "healthy",
            "model": self.model_name,
            "version": self.model_version,
            "llm_provider": "mock",
            "llm_model": self.model_name
        }


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture(scope="module", autouse=True)
def setup_test_models():
    """Setup mock models for testing"""
    # Register mock detection models
    primary_model = MockDetectionModel("mock-camembert")
    fallback_model = MockDetectionModel("mock-llama-fallback")
    
    registry.register_detection_model(primary_model, priority=10)
    registry.register_detection_model(fallback_model, priority=0)
    
    yield
    
    # Cleanup is handled by registry singleton


# ============================================================================
# PROPERTY 8: API INTERFACE CONSISTENCY
# **Feature: optimized-llm-architecture, Property 8**
# **Validates: Requirements 3.3**
# ============================================================================

@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    text=st.text(min_size=10, max_size=500, alphabet=st.characters(blacklist_categories=('Cs',))),
    include_reasoning=st.booleans()
)
def test_property_8_api_interface_consistency_detect(text, include_reasoning):
    """
    Property 8: API interface consistency
    
    For any model switch (CamemBERT ↔ XLM-RoBERTa ↔ Llama), 
    the response schema should remain identical with same field names and types.
    
    This test verifies that the /detect endpoint always returns the same schema
    regardless of which model is used.
    """
    # Make request
    response = client.post(
        "/api/v1/depression/detect",
        json={"text": text, "include_reasoning": include_reasoning}
    )
    
    # Should succeed
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Verify required fields exist
    required_fields = ["prediction", "confidence", "severity", "model_used", "fallback_used"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Verify field types
    assert isinstance(data["prediction"], str), "prediction must be string"
    assert isinstance(data["confidence"], (int, float)), "confidence must be numeric"
    assert isinstance(data["severity"], str), "severity must be string"
    assert isinstance(data["model_used"], str), "model_used must be string"
    assert isinstance(data["fallback_used"], bool), "fallback_used must be boolean"
    
    # Verify optional fields
    if include_reasoning:
        assert "reasoning" in data, "reasoning should be present when requested"
        if data["reasoning"] is not None:
            assert isinstance(data["reasoning"], str), "reasoning must be string or null"
    
    if "processing_time" in data:
        assert isinstance(data["processing_time"], (int, float)), "processing_time must be numeric"
    
    # Verify value constraints
    assert data["prediction"] in ["DÉPRESSION", "NORMAL"], f"Invalid prediction: {data['prediction']}"
    assert 0.0 <= data["confidence"] <= 1.0, f"Confidence out of range: {data['confidence']}"
    assert data["severity"] in ["Aucune", "Faible", "Moyenne", "Élevée", "Critique"], \
        f"Invalid severity: {data['severity']}"


@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    texts=st.lists(
        st.text(min_size=10, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
        min_size=1,
        max_size=10
    ),
    include_reasoning=st.booleans()
)
def test_property_8_api_interface_consistency_batch(texts, include_reasoning):
    """
    Property 8: API interface consistency (batch endpoint)
    
    For any model switch, the batch response schema should remain identical.
    """
    # Make request
    response = client.post(
        "/api/v1/depression/batch-detect",
        json={"texts": texts, "include_reasoning": include_reasoning}
    )
    
    # Should succeed
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Verify top-level fields
    required_fields = ["results", "total_processed", "processing_time", "model_used", "fallback_used"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Verify field types
    assert isinstance(data["results"], list), "results must be list"
    assert isinstance(data["total_processed"], int), "total_processed must be int"
    assert isinstance(data["processing_time"], (int, float)), "processing_time must be numeric"
    assert isinstance(data["model_used"], str), "model_used must be string"
    assert isinstance(data["fallback_used"], bool), "fallback_used must be boolean"
    
    # Verify results count
    assert data["total_processed"] == len(texts), "total_processed should match input count"
    assert len(data["results"]) == len(texts), "results count should match input count"
    
    # Verify each result has consistent schema
    for i, result in enumerate(data["results"]):
        result_required = ["text", "prediction", "confidence", "severity"]
        for field in result_required:
            assert field in result, f"Result {i} missing field: {field}"
        
        # Verify types
        assert isinstance(result["text"], str), f"Result {i} text must be string"
        assert isinstance(result["prediction"], str), f"Result {i} prediction must be string"
        assert isinstance(result["confidence"], (int, float)), f"Result {i} confidence must be numeric"
        assert isinstance(result["severity"], str), f"Result {i} severity must be string"
        
        # Verify values
        assert result["prediction"] in ["DÉPRESSION", "NORMAL"], \
            f"Result {i} invalid prediction: {result['prediction']}"
        assert 0.0 <= result["confidence"] <= 1.0, \
            f"Result {i} confidence out of range: {result['confidence']}"
        assert result["severity"] in ["Aucune", "Faible", "Moyenne", "Élevée", "Critique"], \
            f"Result {i} invalid severity: {result['severity']}"


# ============================================================================
# PROPERTY 16: BACKWARD COMPATIBILITY
# **Feature: optimized-llm-architecture, Property 16**
# **Validates: Requirements 7.1**
# ============================================================================

@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    text=st.text(min_size=10, max_size=500, alphabet=st.characters(blacklist_categories=('Cs',))),
    include_reasoning=st.booleans()
)
def test_property_16_backward_compatibility_detect(text, include_reasoning):
    """
    Property 16: Backward compatibility
    
    For any existing API endpoint call with the old request format,
    the system should return a valid response in the expected format.
    
    This test verifies that the API maintains backward compatibility
    by accepting the same request format and returning all expected fields
    (including new fields like model_used and fallback_used).
    """
    # Old request format (still supported)
    request_data = {
        "text": text,
        "include_reasoning": include_reasoning
    }
    
    # Make request
    response = client.post("/api/v1/depression/detect", json=request_data)
    
    # Should succeed
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Verify all OLD fields are present (backward compatibility)
    old_required_fields = ["prediction", "confidence", "severity"]
    for field in old_required_fields:
        assert field in data, f"Missing backward-compatible field: {field}"
    
    # Verify NEW fields are also present (forward compatibility)
    new_fields = ["model_used", "fallback_used"]
    for field in new_fields:
        assert field in data, f"Missing new field: {field}"
    
    # Verify the response is still valid according to old expectations
    assert data["prediction"] in ["DÉPRESSION", "NORMAL"]
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["severity"] in ["Aucune", "Faible", "Moyenne", "Élevée", "Critique"]
    
    # Verify optional reasoning field behavior hasn't changed
    if include_reasoning:
        # Reasoning should be present (or null)
        assert "reasoning" in data


@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    texts=st.lists(
        st.text(min_size=10, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
        min_size=1,
        max_size=10
    ),
    include_reasoning=st.booleans()
)
def test_property_16_backward_compatibility_batch(texts, include_reasoning):
    """
    Property 16: Backward compatibility (batch endpoint)
    
    Verifies that the batch endpoint maintains backward compatibility.
    """
    # Old request format
    request_data = {
        "texts": texts,
        "include_reasoning": include_reasoning
    }
    
    # Make request
    response = client.post("/api/v1/depression/batch-detect", json=request_data)
    
    # Should succeed
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    
    # Verify all OLD fields are present
    old_required_fields = ["results", "total_processed", "processing_time"]
    for field in old_required_fields:
        assert field in data, f"Missing backward-compatible field: {field}"
    
    # Verify NEW fields are also present
    new_fields = ["model_used", "fallback_used"]
    for field in new_fields:
        assert field in data, f"Missing new field: {field}"
    
    # Verify results structure hasn't changed
    assert len(data["results"]) == len(texts)
    assert data["total_processed"] == len(texts)
    
    # Verify each result maintains old structure
    for result in data["results"]:
        old_result_fields = ["text", "prediction", "confidence", "severity"]
        for field in old_result_fields:
            assert field in result, f"Result missing backward-compatible field: {field}"


def test_property_16_health_endpoint_backward_compatibility():
    """
    Property 16: Backward compatibility (health endpoint)
    
    Verifies that the health endpoint still works and returns expected format.
    """
    response = client.get("/api/v1/depression/health")
    
    # Should succeed
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    
    # Verify expected fields
    expected_fields = ["status", "model", "version"]
    for field in expected_fields:
        assert field in data, f"Missing field in health response: {field}"


def test_property_16_info_endpoint_backward_compatibility():
    """
    Property 16: Backward compatibility (info endpoint)
    
    Verifies that the info endpoint still works.
    """
    response = client.get("/api/v1/depression/info")
    
    # Should succeed
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    
    # Should have basic info
    assert "model_name" in data or "current_model" in data
    assert "endpoints" in data


# ============================================================================
# ADDITIONAL CONSISTENCY TESTS
# ============================================================================

def test_new_health_all_endpoint():
    """
    Test the new /health/all endpoint that checks all models.
    """
    response = client.get("/api/v1/depression/health/all")
    
    # Should succeed
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    
    # Verify structure
    assert "overall_status" in data
    assert "models" in data
    assert isinstance(data["models"], dict)
    
    # Should have at least primary model info
    assert "primary" in data["models"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
