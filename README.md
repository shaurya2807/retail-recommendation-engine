# retail-recommendation-engine

A REST API that recommends home-improvement products to shoppers. It combines a collaborative filter (what similar shoppers bought) with a content-based filter (what is textually similar to products the shopper has already seen), blends the two scores, and returns a ranked list. Models are trained offline, serialised to disk, and loaded into memory at server start. All model versions and their evaluation metrics are recorded in Postgres so you can track accuracy over time and roll back to an earlier version.

## Architecture

```
PostgreSQL
    │
    ├─ products / users / interactions
    │       │
    │  Repository layer (psycopg2)
    │       │
    │  ML Pipeline
    │  ├─ CollaborativeFilteringTrainer  (TruncatedSVD)
    │  ├─ ContentBasedRecommender        (TF-IDF cosine)
    │  ├─ HybridRecommender              (weighted blend)
    │  └─ ModelRegistry                  (joblib + model_registry table)
    │       │
    └─ FastAPI
            │
          Client
```

## Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Language   | Python 3.11                       |
| Framework  | FastAPI + Uvicorn                 |
| ML         | scikit-learn (SVD, TF-IDF)        |
| Database   | PostgreSQL 15                     |
| Infra      | Docker Compose, joblib            |

## How to run locally

```bash
# 1. Start the database and application (seeds + trains on first boot)
docker compose up --build

# 2. If running outside Docker, seed the database
python scripts/seed.py

# 3. Train and register all three models
python scripts/train.py
```

The app is available at `http://localhost:8080`. Interactive docs at `/docs`.

## API endpoints

| Method | Path                                         | Description                                  |
|--------|----------------------------------------------|----------------------------------------------|
| GET    | `/api/v1/recommendations/{user_id}`          | Personalised top-N hybrid recommendations    |
| GET    | `/api/v1/recommendations/similar/{product_id}` | Top-N TF-IDF similar products              |
| GET    | `/api/v1/products/`                          | Paginated product list                       |
| GET    | `/api/v1/products/{product_id}`              | Single product by ID                         |
| GET    | `/api/v1/products/category/{category}`       | Products filtered by category                |
| GET    | `/api/v1/models/`                            | All registered model versions with metrics   |
| GET    | `/health`                                    | Liveness check; reports loaded model status  |

Query parameter `top_n` (default `10`, max `100`) applies to both recommendation routes.

## How the hybrid model works

Each request scores every product using both models independently: the collaborative filter predicts a user's affinity based on the SVD decomposition of the user–product interaction matrix, while the content-based filter scores products by the cosine similarity of their TF-IDF text vectors to the user's interaction history. Both score vectors are min-max normalised to `[0, 1]` so they are on the same scale, then combined as `0.6 × collab + 0.4 × content`. Products the user has already interacted with are excluded, and the top-N by combined score are returned.

## Model registry

Every time `scripts/train.py` runs it upserts a row into the `model_registry` table for each of the three models (`collaborative_filter`, `content_based`, `hybrid`) recording the version string, evaluation metrics (precision/recall/nDCG at k=10 for the collaborative filter), the path to the serialised file on disk, and a timestamp. Only one version per model name is marked `is_active=true` at a time; the lifespan hook in `app/main.py` loads the active versions into `app.state` on startup. To roll back, set `is_active=true` on an earlier row and restart the server.
