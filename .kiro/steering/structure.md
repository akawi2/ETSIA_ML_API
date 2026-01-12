# Project Structure

```
/
├── fastapi_app/           # Business API service
│   ├── app/
│   │   └── main.py        # FastAPI app, endpoints, middleware
│   ├── Dockerfile
│   └── requirements.txt
│
├── ga4_bridge/            # Monitoring middleware service
│   ├── main.py            # FastAPI app, alert evaluation, GA4 forwarding
│   ├── schemas.py         # Pydantic models (MetricEvent)
│   ├── Dockerfile
│   └── requirements.txt
│
├── scripts/
│   └── send_sample_events.py  # Test script for sending events
│
├── metrics_catalog.json   # Alert rules configuration (mounted in ga4-bridge)
├── docker-compose.yml     # Service orchestration
├── pyproject.toml         # Python project config
├── uv.lock                # Dependency lockfile
└── .env                   # Environment variables (gitignored)
```

## Service Boundaries

- `fastapi_app`: Contains only business logic and metric emission
- `ga4_bridge`: Contains only monitoring logic, alert evaluation, and GA4 integration
- Configuration (`metrics_catalog.json`) is external and volume-mounted

## Conventions

- Each service has its own `Dockerfile` and `requirements.txt`
- Shared types/schemas are defined in `schemas.py` within each service
- Test utilities go in `/scripts`
