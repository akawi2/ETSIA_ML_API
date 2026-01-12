# 🚀 Guide de Déploiement

Guide complet pour déployer l'API de détection de dépression en production.

---

## 📋 Prérequis

- Python 3.8+
- Clé API LLM (OpenAI, Anthropic, ou Ollama installé)
- Serveur Linux (Ubuntu 20.04+ recommandé)
- Domaine avec SSL (recommandé pour production)

---

## 🏠 Déploiement Local

### 1. Installation

```bash
# Cloner le projet
git clone <votre-repo>
cd ETSIA_ML_API

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos clés
nano .env
```

Exemple `.env` :
```env
LLM_PROVIDER=gpt
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
```

### 3. Lancer l'API

```bash
# Mode développement
uvicorn app.main:app --reload --port 8000

# Mode production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Tester

```bash
# Health check
curl http://localhost:8000/health

# Prédiction
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel so sad"}'
```

---

## 🐳 Déploiement Docker

### 1. Créer le Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copier requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY app/ ./app/
COPY .env .env

# Exposer le port
EXPOSE 8000

# Lancer l'API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Build et Run

```bash
# Build
docker build -t depression-api .

# Run
docker run -p 8000:8000 --env-file .env depression-api

# Avec docker-compose
docker-compose up -d
```

### 3. docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - BRIDGE_URL=http://ga4-bridge:5000/log_metric
    restart: unless-stopped
    depends_on:
      ga4-bridge:
        condition: service_started
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ga4-bridge:
    build: ./ga4_bridge
    ports:
      - "5000:5000"
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./metrics_catalog.json:/app/metrics_catalog.json:ro
```

**Note :** L'API attend maintenant que le service `ga4-bridge` soit démarré avant de lancer, assurant que le monitoring est disponible dès le démarrage.

---

## ☁️ Déploiement Cloud

### Option 1: Render

**Avantages:** Gratuit, simple, SSL automatique

**Étapes:**

1. Créer compte sur [render.com](https://render.com)

2. Créer un nouveau Web Service

3. Connecter votre repo GitHub

4. Configuration :
   ```
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

5. Ajouter variables d'environnement :
   ```
   LLM_PROVIDER=gpt
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   ```

6. Déployer !

**URL:** `https://votre-app.onrender.com`

---

### Option 2: Railway

**Avantages:** Simple, $5/mois, bon pour production

**Étapes:**

1. Créer compte sur [railway.app](https://railway.app)

2. Nouveau projet → Deploy from GitHub

3. Sélectionner votre repo

4. Railway détecte automatiquement Python

5. Ajouter variables d'environnement

6. Déployer !

**URL:** `https://votre-app.railway.app`

---

### Option 3: Heroku

**Avantages:** Mature, scalable

**Étapes:**

1. Installer Heroku CLI

2. Créer Procfile :
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. Déployer :
   ```bash
   heroku login
   heroku create votre-app
   git push heroku main
   heroku config:set OPENAI_API_KEY=sk-...
   ```

**URL:** `https://votre-app.herokuapp.com`

---

### Option 4: AWS (EC2)

**Avantages:** Contrôle total, scalable

**Étapes:**

1. **Lancer une instance EC2**
   ```bash
   # Ubuntu 22.04 LTS
   # t2.micro (gratuit) ou t2.small
   ```

2. **Connecter via SSH**
   ```bash
   ssh -i votre-cle.pem ubuntu@votre-ip
   ```

3. **Installer dépendances**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx -y
   ```

4. **Cloner et configurer**
   ```bash
   git clone <votre-repo>
   cd ETSIA_ML_API
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Créer service systemd**
   ```bash
   sudo nano /etc/systemd/system/depression-api.service
   ```

   ```ini
   [Unit]
   Description=Depression Detection API
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/ETSIA_ML_API
   Environment="PATH=/home/ubuntu/ETSIA_ML_API/venv/bin"
   EnvironmentFile=/home/ubuntu/ETSIA_ML_API/.env
   ExecStart=/home/ubuntu/ETSIA_ML_API/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

6. **Démarrer le service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start depression-api
   sudo systemctl enable depression-api
   sudo systemctl status depression-api
   ```

7. **Configurer Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/depression-api
   ```

   ```nginx
   server {
       listen 80;
       server_name votre-domaine.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/depression-api /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

8. **SSL avec Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d votre-domaine.com
   ```

**URL:** `https://votre-domaine.com`

---

### Option 5: Google Cloud Run

**Avantages:** Serverless, pay-per-use, scalable

**Étapes:**

1. **Installer gcloud CLI**

2. **Créer Dockerfile** (voir section Docker)

3. **Déployer**
   ```bash
   gcloud auth login
   gcloud config set project votre-projet
   
   gcloud run deploy depression-api \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=sk-...
   ```

**URL:** `https://depression-api-xxx.run.app`

---

## 🔒 Configuration SSL/HTTPS

### Avec Nginx + Let's Encrypt

```bash
# Installer certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir certificat
sudo certbot --nginx -d votre-domaine.com

# Renouvellement automatique
sudo certbot renew --dry-run
```

### Avec Cloudflare

1. Ajouter votre domaine à Cloudflare
2. Activer SSL/TLS (Full)
3. Activer "Always Use HTTPS"
4. Configurer DNS vers votre serveur

---

## 📊 Monitoring et Logs

### Logs avec systemd

```bash
# Voir les logs
sudo journalctl -u depression-api -f

# Logs des dernières 24h
sudo journalctl -u depression-api --since "24 hours ago"
```

### Monitoring avec Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'depression-api'
    static_configs:
      - targets: ['localhost:8000']
```

### Alertes avec Sentry

```python
# app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="votre-dsn-sentry",
    traces_sample_rate=1.0
)
```

---

## 🔧 Optimisations Production

### 1. Workers Uvicorn

```bash
# Nombre de workers = (2 x CPU cores) + 1
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### 2. Gunicorn + Uvicorn

```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 3. Cache Redis

```python
# app/services/cache.py
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_prediction(text):
    key = f"pred:{hash(text)}"
    cached = cache.get(key)
    if cached:
        return json.loads(cached)
    return None

def cache_prediction(text, result):
    key = f"pred:{hash(text)}"
    cache.setex(key, 3600, json.dumps(result))  # 1h TTL
```

### 4. Rate Limiting

```python
# app/main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/predict")
@limiter.limit("10/minute")
async def predict(request: Request, data: PredictRequest):
    ...
```

---

## 🧪 Tests en Production

### Health Check

```bash
# Simple
curl https://votre-api.com/health

# Avec monitoring
while true; do
  curl -s https://votre-api.com/health | jq .status
  sleep 60
done
```

### Load Testing

```bash
# Installer Apache Bench
sudo apt install apache2-utils

# Test de charge
ab -n 1000 -c 10 -p data.json -T application/json \
  https://votre-api.com/api/v1/predict
```

### Smoke Tests

```python
import requests

def test_production():
    base_url = "https://votre-api.com"
    
    # Health check
    r = requests.get(f"{base_url}/health")
    assert r.status_code == 200
    
    # Prédiction
    r = requests.post(
        f"{base_url}/api/v1/predict",
        json={"text": "I feel sad"}
    )
    assert r.status_code == 200
    assert "prediction" in r.json()
```

---

## 🔄 CI/CD

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          curl -X POST https://api.render.com/deploy/...
```

---

## 📈 Scaling

### Horizontal Scaling

```bash
# Avec Docker Swarm
docker swarm init
docker service create \
  --name depression-api \
  --replicas 3 \
  --publish 8000:8000 \
  depression-api:latest

# Avec Kubernetes
kubectl apply -f deployment.yaml
kubectl scale deployment depression-api --replicas=5
```

### Load Balancer

```nginx
# nginx.conf
upstream api_backend {
    server 10.0.1.1:8000;
    server 10.0.1.2:8000;
    server 10.0.1.3:8000;
}

server {
    location / {
        proxy_pass http://api_backend;
    }
}
```

---

## 💰 Coûts Estimés

### Cloud Providers

| Provider | Configuration | Coût/mois |
|----------|--------------|-----------|
| Render | Free tier | $0 |
| Railway | Hobby | $5 |
| Heroku | Hobby | $7 |
| AWS EC2 | t2.micro | $8 |
| Google Cloud Run | Pay-per-use | $5-20 |

### LLM API

| Provider | Coût/1M tokens | Coût/1000 requêtes |
|----------|----------------|---------------------|
| GPT-4o-mini | $0.15 input, $0.60 output | ~$0.60 |
| Claude Sonnet | $3 input, $15 output | ~$15 |
| Llama local | $0 | $0 |

**Recommandation:** Render (gratuit) + GPT-4o-mini (~$0.60/1000 requêtes)

---

## 🆘 Troubleshooting

### Problème : API ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u depression-api -n 50

# Vérifier le port
sudo netstat -tulpn | grep 8000

# Tester manuellement
source venv/bin/activate
uvicorn app.main:app --reload
```

### Problème : Erreur LLM

```bash
# Vérifier la clé API
echo $OPENAI_API_KEY

# Tester directement
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Problème : Timeout

```python
# Augmenter le timeout
# app/services/llm_service.py
response = requests.post(..., timeout=60)
```

---

## 📞 Support

Pour toute question sur le déploiement :
- **Documentation:** Voir README.md
- **Issues:** GitHub Issues
- **Email:** Équipe YANSNET

---

**Version:** 1.0.0  
**Dernière mise à jour:** Janvier 2025
