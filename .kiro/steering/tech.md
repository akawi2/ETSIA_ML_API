# Tech Stack

## Languages & Frameworks

- Python 3.11
- FastAPI (web framework)
- Pydantic (data validation)
- Uvicorn (ASGI server)

## Key Libraries

- `httpx` - Async HTTP client (GA4-Bridge → GA4)
- `requests` - Sync HTTP client (FastAPI App → GA4-Bridge)

## Infrastructure

- Docker & Docker Compose for containerization
- Two services: `fastapi-app` (8000), `ga4-bridge` (5000)

## External Services

- Google Analytics 4 Measurement Protocol API

## Package Management

- `uv` (lockfile: `uv.lock`)
- Per-service `requirements.txt` for Docker builds

## Common Commands

```bash
# Build and start all services
docker-compose --env-file .env up --build -d

# Restart bridge after catalog changes
docker-compose restart ga4-bridge

# Health checks
curl http://localhost:5000/health  # GA4-Bridge
curl http://localhost:8000/health  # FastAPI App

# Test endpoints
curl -X POST http://localhost:8000/predict_hatecomment
curl -X POST http://localhost:8000/predict_depression

# Run test script
python scripts/send_sample_events.py
```

## Environment Variables

Required in `.env`:
- `GA4_MEASUREMENT_ID` - Google Analytics 4 measurement ID
- `GA4_API_SECRET` - GA4 API secret key
