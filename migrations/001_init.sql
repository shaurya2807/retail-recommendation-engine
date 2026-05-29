CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    sku         VARCHAR(64)    UNIQUE NOT NULL,
    name        VARCHAR(255)   NOT NULL,
    category    VARCHAR(100)   NOT NULL,
    subcategory VARCHAR(100),
    price       NUMERIC(10, 2) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id         SERIAL PRIMARY KEY,
    username   VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS interactions (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER     NOT NULL REFERENCES users(id)    ON DELETE CASCADE,
    product_id       INTEGER     NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    interaction_type VARCHAR(20) NOT NULL CHECK (interaction_type IN ('view', 'cart', 'purchase')),
    rating           SMALLINT    CHECK (rating BETWEEN 1 AND 5),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_registry (
    id         SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version    VARCHAR(50)  NOT NULL,
    metrics    JSONB,
    model_path VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    is_active  BOOLEAN      NOT NULL DEFAULT FALSE,
    UNIQUE (model_name, version)
);

CREATE INDEX IF NOT EXISTS idx_interactions_user_id    ON interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_product_id ON interactions(product_id);
CREATE INDEX IF NOT EXISTS idx_model_registry_active   ON model_registry(is_active) WHERE is_active = TRUE;
