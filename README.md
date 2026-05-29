# Retail Recommendation Engine

A production-style recommendation API for a home-improvement retailer. Combines collaborative filtering (TruncatedSVD) with content-based filtering (TF-IDF) in a weighted hybrid model, served over FastAPI with PostgreSQL persistence.

## Architecture

```
┌─────────────┐    ┌──────────────────────────────────────────┐    ┌──────────────┐
│   FastAPI   │───▶│  HybridRecommender (0.6 CF + 0.4 CB)    │───▶│  PostgreSQL  │
│  app.main   │    │  ├─ CollaborativeFilteringTrainer (SVD)  │    │  products    │
│             │    │  └─ ContentBasedRecommender (TF-IDF)     │    │  users       │
│  /api/v1/   │    └──────────────────────────────────────────┘    │  interactions│
│  /health    │                                                     │  model_regist│
└─────────────┘                                                     └──────────────┘
```

## Prerequisites

- Docker and Docker Compose, **or** Python 3.11+ and PostgreSQL 15

## Quickstart (Docker)

```bash
cp .env.example .env          # or edit .env directly
docker compose up --build
```

On first boot the app container seeds the database (50 products, 20 users, ~570 interactions), trains all three models, and starts the API on port 8080.

Models are stored in a named Docker volume (`models_data`) so they survive container restarts without retraining.

## Local development

```bash
# 1. Start only the database
docker compose up -d db

# 2. Create and activate a virtualenv
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Seed and train
python scripts/seed.py
python scripts/train.py

# 5. Start the API
uvicorn app.main:app --reload --port 8080
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | `localhost` | Postgres host |
| `DB_PORT` | `5432` | Postgres port |
| `DB_USER` | `postgres` | Postgres user |
| `DB_PASSWORD` | `postgres` | Postgres password |
| `DB_NAME` | `recommendations` | Database name |
| `COLLAB_WEIGHT` | `0.6` | Collaborative filter blend weight |
| `CONTENT_WEIGHT` | `0.4` | Content-based filter blend weight |

## API reference

All routes are under `/api/v1`.

### Recommendations

| Method | Path | Description |
|---|---|---|
| `GET` | `/recommendations/{user_id}` | Top-N hybrid recommendations for a user |
| `GET` | `/recommendations/similar/{product_id}` | Top-N TF-IDF similar products |

Query parameter `top_n` (default 10, max 100) controls list length.

**Example — user recommendations:**
```bash
curl http://localhost:8080/api/v1/recommendations/1
```
```json
{
  "user_id": 1,
  "recommendations": [
    {"rank": 1, "product_id": 18, "sku": "LBR-00008", "name": "1/2-in 4x8 Drywall",
     "category": "Lumber", "price": "13.48", "score": 0.3178}
  ],
  "model_name": "hybrid",
  "model_version": "1.0"
}
```

**Example — similar products:**
```bash
curl http://localhost:8080/api/v1/recommendations/similar/1
```

### Products

| Method | Path | Description |
|---|---|---|
| `GET` | `/products/` | Paginated product list (`limit`, `offset`) |
| `GET` | `/products/{product_id}` | Single product by ID |
| `GET` | `/products/category/{category}` | Products filtered by category |

### Model registry

| Method | Path | Description |
|---|---|---|
| `GET` | `/models/` | All registered model versions with metrics |

```bash
curl http://localhost:8080/api/v1/models/
```
```json
{
  "models": [
    {"model_name": "hybrid", "version": "1.0", "metrics": {},
     "is_active": true, "created_at": "2026-05-29T19:47:00"}
  ]
}
```

### System

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check; reports loaded model status |

## ML pipeline

```
scripts/train.py
  1. Load interaction matrix from DB (users × products)
  2. Fit CollaborativeFilteringTrainer (TruncatedSVD, n_components=20)
  3. Leave-one-out evaluation → precision/recall/nDCG @10
  4. Fit ContentBasedRecommender (TF-IDF max_features=500)
  5. Build HybridRecommender (collab + content)
  6. Register all three models in model_registry table (joblib on disk)
```

Re-running `train.py` upserts existing model versions and promotes them to active.

## Project layout

```
app/
  api/          # FastAPI routers (products, recommendations, models, users)
  ml/           # trainer, evaluator, content_based, hybrid, registry
  models/       # Pydantic schemas
  repository/   # psycopg2 data access (product, user, interaction, model_registry)
configs/        # pydantic-settings config
migrations/     # 001_init.sql — schema DDL
models/         # joblib model files (git-ignored except .gitkeep)
scripts/        # seed.py, train.py
```
