# MarketPulse AI — Enterprise Production & Operations Guide

This guide details enterprise operational standards, production container deployments, SLA guarantees, rate limiting, and observability telemetry for **MarketPulse AI Agents**.

---

## 🏗️ Production Infrastructure & Deployment

### 1. Docker Container Deployment
Deploy the pre-built multi-stage container:
```bash
docker-compose up -d --build
```

### 2. Container Health Checks
Automated container healthchecks poll the internal graph runtime every 30 seconds via `healthcheck.py`:
```bash
docker inspect --format='{{json .State.Health}}' marketpulse_app
```

---

## 🔒 Security & Compliance

- **Secret Redaction (`config/security.py`)**: All API keys, bearer tokens, and credentials are auto-redacted from logs using regular expression filters.
- **Input Sanitization**: Tickers and user queries undergo HTML/script tag stripping before passing to LLM nodes.

---

## ⚡ Performance & SLA Target Metrics

| Metric | Target SLA | Strategy |
| :--- | :--- | :--- |
| **Quick Analysis Latency** | < 3.0s | TTL in-memory caching (`tools/cache.py`) |
| **Standard Analysis Latency** | < 12.0s | Parallel batch tool execution (`tools/async_executor.py`) |
| **API Availability** | 99.9% | Circuit Breaker pattern with retry backoff (`tools/circuit_breaker.py`) |
| **Test Suite Reliability** | 100% Pass | 535+ automated unit and integration tests |
