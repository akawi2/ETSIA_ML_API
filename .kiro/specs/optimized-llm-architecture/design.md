# Design Document

## Overview

This document describes the design for optimizing the ETSIA ML API architecture to use a hybrid approach with specialized models for different tasks. The current architecture uses Llama 3.2 8B via Ollama for both depression detection and content generation, which results in unacceptable latency (30-120s) for user-facing workflows.

The new architecture will use:
- **CamemBERT or XLM-RoBERTa** (110-125M params) for depression detection: 20-50ms latency, optimized for French
- **Llama 3.2 3B** via Ollama for content generation: 5-15s latency, acceptable for demos/tests

This hybrid approach provides:
- 500-2000x faster depression detection
- 100% free and open-source
- Excellent French language support
- Efficient resource usage on CPU-only servers

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Model Registry (Enhanced)              │    │
│  │  - Manages multiple model types                │    │
│  │  - Routes requests to appropriate models       │    │
│  │  - Handles fallback logic                      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────────┐   │
│  │  Depression      │      │  Content Generation  │   │
│  │  Detection       │      │  Service             │   │
│  │  Service         │      │                      │   │
│  └──────────────────┘      └──────────────────────┘   │
│           │                          │                  │
└───────────┼──────────────────────────┼──────────────────┘
            │                          │
            ▼                          ▼
   ┌──────────────────┐      ┌──────────────────────┐
   │  CamemBERT/      │      │  Llama 3.2 3B       │
   │  XLM-RoBERTa     │      │  (via Ollama)       │
   │  (Transformers)  │      │                     │
   │                  │      │                     │
   │  Latency: 20-50ms│      │  Latency: 5-15s     │
   │  RAM: 500-600MB  │      │  RAM: 4-6GB         │
   └──────────────────┘      └──────────────────────┘
```

### Provider Architecture

The system will support three provider modes:

1. **Hybrid Mode** (Recommended for production):
   - Depression detection → CamemBERT/XLM-RoBERTa
   - Content generation → Llama 3.2 3B

2. **Legacy Mode** (Backward compatibility):
   - All tasks → Llama 3.2 8B (current behavior)

3. **External Mode** (Optional, for comparison):
   - All tasks → GPT-4o-mini or Claude

### Request Flow

```
User Request
     │
     ▼
API Endpoint (/api/v1/depression/detect or /api/v1/content/generate-*)
     │
     ▼
Model Registry
     │
     ├─── Is depression detection? ──→ CamemBERT Model
     │                                      │
     │                                      ▼
     │                                 Inference (20-50ms)
     │                                      │
     │                                      ▼
     │                                 Return Result
     │
     └─── Is content generation? ──→ Llama 3.2 3B Model
                                          │
                                          ▼
                                     Inference (5-15s)
                                          │
                                          ▼
                                     Return Result
```

## Components and Interfaces

### 1. Enhanced Model Registry

**Purpose**: Manage multiple model types and route requests appropriately

**Interface**:
```python
class EnhancedModelRegistry:
    def register_detection_model(self, model: BaseMLModel, priority: int)
    def register_generation_model(self, model: BaseMLModel)
    def get_detection_model(self) -> BaseMLModel
    def get_generation_model(self) -> BaseMLModel
    def health_check_all(self) -> Dict[str, Any]
```

### 2. CamemBERT Detection Model

**Purpose**: Fast, accurate depression detection for French text

**Interface**:
```python
class CamemBERTDepressionModel(BaseMLModel):
    model_name: str = "camembert-depression"
    
    def __init__(self, model_path: str = "camembert-base")
    def predict(self, text: str, include_reasoning: bool = True) -> Dict[str, Any]
    def batch_predict(self, texts: List[str]) -> List[Dict[str, Any]]
```

**Key Features**:
- Uses HuggingFace Transformers
- Fine-tuned or zero-shot classification
- Confidence scoring via softmax
- Optional reasoning via attention weights

### 3. XLM-RoBERTa Detection Model (Alternative)

**Purpose**: Multilingual depression detection with broader language support

**Interface**: Same as CamemBERT model

**Key Features**:
- Supports 100 languages
- Slightly slower than CamemBERT (30-60ms vs 20-50ms)
- Better for mixed-language content

### 4. Llama Content Generator (Optimized)

**Purpose**: Generate realistic French content for demos/tests

**Changes from current**:
- Use Llama 3.2 **3B** instead of 8B (2-3x faster)
- Add request queuing to prevent blocking
- Implement caching for common requests

### 5. Fallback Handler

**Purpose**: Handle failures gracefully with fallback models

**Logic**:
```python
try:
    result = primary_model.predict(text)
except Exception:
    logger.warning("Primary model failed, using fallback")
    result = fallback_model.predict(text, timeout=10s)
```

**Fallback Chain**:
1. Primary: CamemBERT (20-50ms)
2. Fallback: Llama 3.2 1B (2-5s)
3. Error: Return error with retry suggestion

## Data Models

### Configuration Model

```python
class ModelConfig(BaseSettings):
    # Provider selection
    DETECTION_PROVIDER: str = "camembert"  # camembert, xlm-roberta, llama
    GENERATION_PROVIDER: str = "ollama"    # ollama, gpt, claude
    
    # CamemBERT settings
    CAMEMBERT_MODEL: str = "camembert-base"
    CAMEMBERT_DEVICE: str = "cpu"
    CAMEMBERT_MAX_LENGTH: int = 512
    
    # XLM-RoBERTa settings
    XLM_ROBERTA_MODEL: str = "xlm-roberta-base"
    XLM_ROBERTA_DEVICE: str = "cpu"
    
    # Ollama settings (updated)
    OLLAMA_DETECTION_MODEL: str = "llama3.2:1b"  # Fallback only
    OLLAMA_GENERATION_MODEL: str = "llama3.2:3b"  # Primary for generation
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Performance settings
    MAX_DETECTION_LATENCY_MS: int = 500
    MAX_GENERATION_LATENCY_S: int = 30
    ENABLE_FALLBACK: bool = True
    
    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LATENCY: bool = True
```

### Response Models (Enhanced)

```python
class DepressionDetectResponse(BaseModel):
    prediction: str  # "DÉPRESSION" or "NORMAL"
    confidence: float  # 0.0 to 1.0
    severity: str  # "Aucune", "Faible", "Moyenne", "Élevée", "Critique"
    reasoning: Optional[str]
    processing_time: float  # milliseconds
    model_used: str  # "camembert", "xlm-roberta", "llama-1b"
    fallback_used: bool = False
```

### Metrics Model

```python
class ModelMetrics(BaseModel):
    model_name: str
    total_requests: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    error_rate: float
    accuracy: Optional[float]  # When ground truth available
    throughput_rps: float  # Requests per second
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Detection latency bound

*For any* text input to depression detection, the system response time should be less than 500 milliseconds when using CamemBERT or XLM-RoBERTa.

**Validates: Requirements 1.1**

### Property 2: French detection accuracy

*For any* French text in a labeled test dataset, the system should maintain accuracy above 80% for depression detection.

**Validates: Requirements 1.2**

### Property 3: Multilingual accuracy equivalence

*For any* pair of equivalent French and English texts in a labeled test dataset, the accuracy difference should be less than 5 percentage points.

**Validates: Requirements 1.3**

### Property 4: Memory consumption bound

*For any* model loading operation for depression detection, the RAM consumption should be less than 1 gigabyte.

**Validates: Requirements 1.5**

### Property 5: Zero external API costs

*For any* request processed by the system, no calls should be made to paid external APIs (OpenAI, Anthropic, etc.) when running in local mode.

**Validates: Requirements 2.4**

### Property 6: Detection model routing

*For any* depression detection request, the system should route to CamemBERT or XLM-RoBERTa, never to Llama for generation.

**Validates: Requirements 3.1**

### Property 7: Generation model routing

*For any* content generation request, the system should route to Llama 3.2 3B via Ollama.

**Validates: Requirements 3.2**

### Property 8: API interface consistency

*For any* model switch (CamemBERT ↔ XLM-RoBERTa ↔ Llama), the response schema should remain identical with same field names and types.

**Validates: Requirements 3.3**

### Property 9: Generation latency bound

*For any* content generation request, the system response time should be less than 30 seconds.

**Validates: Requirements 4.1**

### Property 10: Non-blocking generation

*For any* concurrent depression detection and content generation requests, the detection request should complete within its latency bound regardless of generation status.

**Validates: Requirements 4.5**

### Property 11: Latency logging

*For any* request processed, the system should log the latency metric with model identifier.

**Validates: Requirements 5.1**

### Property 12: Error rate logging

*For any* error encountered during inference, the system should log the error with model identifier and error type.

**Validates: Requirements 5.3**

### Property 13: Throughput tracking

*For any* time window under load, the system should track and report requests per second for each model.

**Validates: Requirements 5.5**

### Property 14: Timeout enforcement

*For any* inference operation that exceeds the configured timeout, the system should return a timeout error within the timeout period plus 100ms maximum.

**Validates: Requirements 6.2**

### Property 15: Concurrent request capacity

*For any* set of 10 concurrent depression detection requests, all should complete successfully without errors.

**Validates: Requirements 6.5**

### Property 16: Backward compatibility

*For any* existing API endpoint call with the old request format, the system should return a valid response in the expected format.

**Validates: Requirements 7.1**

### Property 17: Response format preservation

*For any* request made before and after migration, the response schema should be identical (same fields, types, and structure).

**Validates: Requirements 7.3**

### Property 18: Batch throughput optimization

*For any* batch of N requests, the total processing time should be less than N times the single-request latency (demonstrating batching efficiency).

**Validates: Requirements 8.2**

### Property 19: Memory release on idle

*For any* idle period of 5 minutes, the system memory usage should decrease by at least 10% compared to peak usage.

**Validates: Requirements 8.3**

### Property 20: Confidence score validity

*For any* prediction returned by the system, the confidence score should be between 0.0 and 1.0 inclusive.

**Validates: Requirements 9.1**

### Property 21: Severity classification validity

*For any* depression detection result, the severity should be one of: "Aucune", "Faible", "Moyenne", "Élevée", or "Critique".

**Validates: Requirements 9.2**

## Error Handling

### Error Categories

1. **Model Loading Errors**
   - Missing model files
   - Insufficient memory
   - Corrupted model weights
   - **Action**: Log error, attempt fallback model, return 503 if all fail

2. **Inference Errors**
   - Timeout exceeded
   - Out of memory during inference
   - Invalid input format
   - **Action**: Log error, retry once, use fallback if available, return 500

3. **Input Validation Errors**
   - Text too long (>5000 chars)
   - Empty text
   - Invalid encoding
   - **Action**: Return 400 with clear error message

4. **Resource Exhaustion**
   - Too many concurrent requests
   - Memory limit reached
   - **Action**: Queue requests or return 429 (rate limit)

### Fallback Strategy

```python
def predict_with_fallback(text: str) -> Dict[str, Any]:
    """
    Attempt prediction with fallback chain
    """
    models = [
        (camembert_model, 500),   # 500ms timeout
        (llama_1b_model, 5000),   # 5s timeout
    ]
    
    for model, timeout in models:
        try:
            return model.predict(text, timeout=timeout)
        except TimeoutError:
            logger.warning(f"{model.name} timed out, trying fallback")
            continue
        except Exception as e:
            logger.error(f"{model.name} failed: {e}")
            continue
    
    raise RuntimeError("All models failed")
```

### Graceful Degradation

- If CamemBERT fails → Use Llama 3.2 1B (slower but works)
- If Llama 3.2 3B fails → Use Llama 3.2 1B (faster, lower quality)
- If all local models fail → Return error with suggestion to check logs

## Testing Strategy

### Unit Testing

**Framework**: pytest

**Coverage Areas**:
1. Model loading and initialization
2. Request routing logic
3. Response formatting
4. Error handling paths
5. Configuration management
6. Fallback logic

**Example Tests**:
```python
def test_camembert_loads_successfully():
    """Test CamemBERT model loads without errors"""
    model = CamemBERTDepressionModel()
    assert model._initialized == True
    assert model.model is not None

def test_detection_routes_to_camembert():
    """Test depression detection uses CamemBERT"""
    registry = EnhancedModelRegistry()
    model = registry.get_detection_model()
    assert model.model_name == "camembert-depression"

def test_fallback_on_primary_failure():
    """Test fallback activates when primary fails"""
    # Mock primary model to fail
    with patch.object(camembert_model, 'predict', side_effect=Exception):
        result = predict_with_fallback("test text")
        assert result['fallback_used'] == True
```

### Property-Based Testing

**Framework**: Hypothesis (Python)

**Configuration**: Minimum 100 iterations per property

**Test Structure**:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=10, max_size=5000))
def test_property_detection_latency_bound(text):
    """
    Property 1: Detection latency bound
    Feature: optimized-llm-architecture, Property 1
    """
    start = time.time()
    result = detection_model.predict(text)
    latency_ms = (time.time() - start) * 1000
    
    assert latency_ms < 500, f"Latency {latency_ms}ms exceeds 500ms"

@given(st.lists(st.text(min_size=10, max_size=500), min_size=1, max_size=100))
def test_property_confidence_validity(texts):
    """
    Property 20: Confidence score validity
    Feature: optimized-llm-architecture, Property 20
    """
    results = detection_model.batch_predict(texts)
    
    for result in results:
        assert 0.0 <= result['confidence'] <= 1.0
```

### Integration Testing

**Scope**: End-to-end API testing

**Tests**:
1. Full request/response cycle for depression detection
2. Full request/response cycle for content generation
3. Concurrent request handling
4. Fallback activation under failure
5. Health check endpoints
6. Metrics collection

### Performance Testing

**Tools**: locust or pytest-benchmark

**Metrics to Measure**:
- Latency (p50, p95, p99)
- Throughput (requests/second)
- Memory usage over time
- CPU usage
- Error rates under load

**Load Scenarios**:
1. Sustained load: 10 req/s for 10 minutes
2. Burst load: 50 req/s for 1 minute
3. Mixed load: Detection + generation concurrent

### Acceptance Testing

**Validation Against Requirements**:
- Manual testing of French text detection
- Quality assessment of generated content
- Verification of latency requirements
- Resource usage validation on target hardware

## Migration Strategy

### Phase 1: Parallel Deployment (Week 1)

- Deploy new models alongside existing Llama 8B
- Route 10% of traffic to new models
- Compare metrics side-by-side
- Validate latency improvements

### Phase 2: Gradual Rollout (Week 2)

- Increase traffic to new models: 25% → 50% → 75%
- Monitor error rates and accuracy
- Collect user feedback
- Fine-tune confidence thresholds

### Phase 3: Full Migration (Week 3)

- Route 100% of detection to CamemBERT
- Route 100% of generation to Llama 3.2 3B
- Keep Llama 8B as fallback for 1 week
- Update documentation

### Phase 4: Cleanup (Week 4)

- Remove Llama 8B from primary path
- Keep as optional fallback
- Update monitoring dashboards
- Finalize documentation

### Rollback Plan

If issues arise:
1. Change `DETECTION_PROVIDER=llama` in config
2. Restart service (< 30 seconds downtime)
3. All traffic returns to Llama 8B
4. Investigate issues offline

## Performance Benchmarks

### Expected Performance (CPU-only, 32GB RAM)

| Model | Task | Latency (p50) | Latency (p95) | RAM | Throughput |
|-------|------|---------------|---------------|-----|------------|
| CamemBERT | Detection | 30ms | 50ms | 500MB | 30 req/s |
| XLM-RoBERTa | Detection | 40ms | 60ms | 600MB | 25 req/s |
| Llama 3.2 1B | Detection (fallback) | 2s | 5s | 2GB | 0.5 req/s |
| Llama 3.2 3B | Generation | 8s | 15s | 5GB | 0.1 req/s |
| Llama 3.2 8B | Generation (legacy) | 40s | 120s | 16GB | 0.02 req/s |

### Comparison with Current Architecture

| Metric | Current (Llama 8B) | New (Hybrid) | Improvement |
|--------|-------------------|--------------|-------------|
| Detection Latency | 30-120s | 30-50ms | **600-2400x faster** |
| Detection RAM | 16GB | 500MB | **32x less** |
| Generation Latency | 40-120s | 8-15s | **3-8x faster** |
| Generation RAM | 16GB | 5GB | **3x less** |
| Total Disk Space | 16GB | 6GB | **2.7x less** |
| Cost per Request | $0 | $0 | Same (free) |

## Monitoring and Observability

### Metrics to Track

1. **Latency Metrics**
   - Per-model latency (p50, p95, p99)
   - End-to-end API latency
   - Fallback activation latency

2. **Accuracy Metrics** (when ground truth available)
   - Precision, Recall, F1 per model
   - Confusion matrix
   - Severity classification accuracy

3. **Resource Metrics**
   - Memory usage per model
   - CPU usage
   - Disk I/O
   - Request queue depth

4. **Error Metrics**
   - Error rate per model
   - Timeout rate
   - Fallback activation rate
   - 4xx/5xx HTTP errors

### Logging Strategy

```python
# Structured logging format
{
    "timestamp": "2025-01-16T10:30:00Z",
    "level": "INFO",
    "model": "camembert-depression",
    "endpoint": "/api/v1/depression/detect",
    "latency_ms": 35,
    "prediction": "NORMAL",
    "confidence": 0.92,
    "fallback_used": false,
    "request_id": "abc123"
}
```

### Alerting Rules

1. **Critical Alerts** (immediate action)
   - Detection latency > 1s for 5 consecutive requests
   - Error rate > 10% over 5 minutes
   - Memory usage > 90%
   - All models failing

2. **Warning Alerts** (investigate soon)
   - Detection latency > 500ms for p95
   - Fallback activation rate > 5%
   - Accuracy drop > 5% from baseline
   - Memory usage > 75%

### Dashboard Metrics

- Real-time latency graph per model
- Request volume over time
- Error rate trends
- Model usage distribution
- Resource utilization (CPU, RAM)
- Fallback activation frequency

## Security Considerations

1. **Input Validation**
   - Sanitize all text inputs
   - Limit input length (5000 chars)
   - Validate encoding (UTF-8)
   - Rate limiting per IP

2. **Model Security**
   - Verify model checksums on load
   - Use trusted model sources only (HuggingFace, Ollama official)
   - Isolate model execution (no arbitrary code execution)

3. **API Security**
   - Optional API key authentication
   - CORS configuration
   - Request size limits
   - Timeout enforcement

4. **Data Privacy**
   - No logging of sensitive user text (configurable)
   - Local processing only (no external API calls)
   - Optional anonymization of logs

## Deployment Considerations

### Docker Configuration

```dockerfile
# Optimized for CPU-only deployment
FROM python:3.11-slim

# Install dependencies
RUN pip install transformers torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install fastapi uvicorn

# Copy application
COPY app/ /app/

# Download models at build time
RUN python -c "from transformers import AutoModel; AutoModel.from_pretrained('camembert-base')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Resource Allocation

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 8G  # Reduced from 16G
          cpus: '4'
        reservations:
          memory: 2G
```

### Environment Variables

```bash
# Production configuration
DETECTION_PROVIDER=camembert
GENERATION_PROVIDER=ollama
OLLAMA_GENERATION_MODEL=llama3.2:3b
MAX_DETECTION_LATENCY_MS=500
MAX_GENERATION_LATENCY_S=30
ENABLE_FALLBACK=true
ENABLE_METRICS=true
LOG_LEVEL=INFO
```

## Future Enhancements

1. **Model Fine-tuning**
   - Fine-tune CamemBERT on French depression dataset
   - Improve accuracy from 80% → 90%+

2. **Quantization**
   - Apply INT8 quantization to CamemBERT
   - Further reduce latency and memory

3. **Caching Layer**
   - Cache common detection results
   - Cache generated content for demos

4. **GPU Support** (optional)
   - Add GPU acceleration for Llama models
   - Reduce generation latency to <1s

5. **Multi-model Ensemble**
   - Combine CamemBERT + XLM-RoBERTa predictions
   - Improve accuracy via voting

6. **Streaming Responses**
   - Stream content generation token-by-token
   - Improve perceived latency

## References

- CamemBERT: https://huggingface.co/camembert-base
- XLM-RoBERTa: https://huggingface.co/xlm-roberta-base
- Llama 3.2: https://ollama.com/library/llama3.2
- Transformers Library: https://huggingface.co/docs/transformers
- Ollama Documentation: https://github.com/ollama/ollama
