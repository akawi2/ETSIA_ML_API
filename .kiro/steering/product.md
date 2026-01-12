# Product Overview

Yansnet is an ML monitoring system that tracks technical and business metrics for AI models (hate detection, depression detection, content generation, image captioning).

## Architecture

- **FastAPI App** (port 8000): Business API exposing ML model endpoints
- **GA4-Bridge** (port 5000): Middleware that evaluates alert thresholds in real-time before forwarding metrics to Google Analytics 4
- **Google Analytics 4**: Dashboard for visualization and historical data

## Core Functionality

1. ML endpoints emit metrics asynchronously to the GA4-Bridge
2. Bridge evaluates metrics against configurable thresholds (`metrics_catalog.json`)
3. Alerts are tagged on events when thresholds are breached
4. Events are forwarded to GA4 Measurement Protocol API

## Key Concepts

- **Metrics Catalog**: JSON file defining alert rules (service, metric, threshold, operator, priority)
- **Alert Tagging**: Events are enriched with `alert_triggered`, `alert_reason`, `alert_priority` when thresholds fail
- **Async Monitoring**: Metrics are sent with short timeouts to avoid impacting business API latency
