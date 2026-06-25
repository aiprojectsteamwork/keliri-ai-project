-- ============================================================
-- AI-Powered Hyperlocal Advertising Platform - Database Schema
-- ============================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- BRANDS
-- ============================================================
CREATE TABLE brands (
    id          SERIAL PRIMARY KEY,
    uuid        UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    name        VARCHAR(255) NOT NULL,
    slug        VARCHAR(255) NOT NULL UNIQUE,
    logo_url    TEXT,
    website     TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ
);

CREATE INDEX idx_brands_slug       ON brands(slug);
CREATE INDEX idx_brands_is_active  ON brands(is_active);
CREATE INDEX idx_brands_deleted_at ON brands(deleted_at);

-- ============================================================
-- BRANCHES
-- ============================================================
CREATE TABLE branches (
    id            SERIAL PRIMARY KEY,
    uuid          UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    brand_id      INTEGER NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    branch_name   VARCHAR(255) NOT NULL,
    latitude      NUMERIC(10, 7) NOT NULL,
    longitude     NUMERIC(10, 7) NOT NULL,
    address       TEXT NOT NULL,
    city          VARCHAR(100) NOT NULL,
    state         VARCHAR(100) NOT NULL,
    country       VARCHAR(100) NOT NULL DEFAULT 'India',
    pincode       VARCHAR(20),
    phone         VARCHAR(30),
    email         VARCHAR(255),
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at    TIMESTAMPTZ,
    CONSTRAINT chk_latitude  CHECK (latitude  BETWEEN -90  AND 90),
    CONSTRAINT chk_longitude CHECK (longitude BETWEEN -180 AND 180)
);

CREATE INDEX idx_branches_brand_id   ON branches(brand_id);
CREATE INDEX idx_branches_city       ON branches(city);
CREATE INDEX idx_branches_is_active  ON branches(is_active);
CREATE INDEX idx_branches_deleted_at ON branches(deleted_at);
CREATE INDEX idx_branches_geo        ON branches(latitude, longitude);

-- ============================================================
-- CAMPAIGNS
-- ============================================================
CREATE TABLE campaigns (
    id           SERIAL PRIMARY KEY,
    uuid         UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    brand_id     INTEGER NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    name         VARCHAR(255) NOT NULL,
    description  TEXT,
    budget       NUMERIC(12, 2),
    start_date   DATE NOT NULL,
    end_date     DATE NOT NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'draft'
                     CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled')),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at   TIMESTAMPTZ,
    CONSTRAINT chk_campaign_dates CHECK (end_date >= start_date)
);

CREATE INDEX idx_campaigns_brand_id   ON campaigns(brand_id);
CREATE INDEX idx_campaigns_status     ON campaigns(status);
CREATE INDEX idx_campaigns_dates      ON campaigns(start_date, end_date);
CREATE INDEX idx_campaigns_deleted_at ON campaigns(deleted_at);

-- ============================================================
-- OFFERS
-- ============================================================
CREATE TABLE offers (
    id                  SERIAL PRIMARY KEY,
    uuid                UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    branch_id           INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    campaign_id         INTEGER REFERENCES campaigns(id) ON DELETE SET NULL,
    title               VARCHAR(255) NOT NULL,
    description         TEXT,
    discount_percentage NUMERIC(5, 2) CHECK (discount_percentage BETWEEN 0 AND 100),
    start_date          DATE NOT NULL,
    end_date            DATE NOT NULL,
    valid_days          INTEGER[] NOT NULL DEFAULT '{0,1,2,3,4,5,6}',  -- 0=Sun…6=Sat
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ,
    CONSTRAINT chk_offer_dates CHECK (end_date >= start_date)
);

CREATE INDEX idx_offers_branch_id   ON offers(branch_id);
CREATE INDEX idx_offers_campaign_id ON offers(campaign_id);
CREATE INDEX idx_offers_is_active   ON offers(is_active);
CREATE INDEX idx_offers_dates       ON offers(start_date, end_date);
CREATE INDEX idx_offers_deleted_at  ON offers(deleted_at);

-- ============================================================
-- ASSETS  (images, videos attached to ads or offers)
-- ============================================================
CREATE TABLE assets (
    id           SERIAL PRIMARY KEY,
    uuid         UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    brand_id     INTEGER NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    file_name    VARCHAR(255) NOT NULL,
    file_url     TEXT NOT NULL,
    file_type    VARCHAR(50) NOT NULL,   -- image/jpeg, video/mp4 …
    file_size_kb INTEGER,
    width_px     INTEGER,
    height_px    INTEGER,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at   TIMESTAMPTZ
);

CREATE INDEX idx_assets_brand_id   ON assets(brand_id);
CREATE INDEX idx_assets_deleted_at ON assets(deleted_at);

-- ============================================================
-- ADVERTISEMENTS
-- ============================================================
CREATE TABLE advertisements (
    id           SERIAL PRIMARY KEY,
    uuid         UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    campaign_id  INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    branch_id    INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    offer_id     INTEGER REFERENCES offers(id) ON DELETE SET NULL,
    asset_id     INTEGER REFERENCES assets(id) ON DELETE SET NULL,
    title        VARCHAR(255) NOT NULL,
    body_text    TEXT,
    cta_label    VARCHAR(100) DEFAULT 'Learn More',
    cta_url      TEXT,
    format       VARCHAR(30) NOT NULL DEFAULT 'banner'
                     CHECK (format IN ('banner', 'interstitial', 'native', 'video')),
    radius_km    NUMERIC(6, 2) NOT NULL DEFAULT 5.0,
    is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at   TIMESTAMPTZ
);

CREATE INDEX idx_ads_campaign_id  ON advertisements(campaign_id);
CREATE INDEX idx_ads_branch_id    ON advertisements(branch_id);
CREATE INDEX idx_ads_offer_id     ON advertisements(offer_id);
CREATE INDEX idx_ads_is_active    ON advertisements(is_active);
CREATE INDEX idx_ads_deleted_at   ON advertisements(deleted_at);

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE users (
    id           SERIAL PRIMARY KEY,
    uuid         UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE,
    device_id    VARCHAR(255) UNIQUE,
    email        VARCHAR(255) UNIQUE,
    phone        VARCHAR(30),
    name         VARCHAR(255),
    city         VARCHAR(100),
    state        VARCHAR(100),
    country      VARCHAR(100) DEFAULT 'India',
    is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_device_id ON users(device_id);
CREATE INDEX idx_users_email     ON users(email);
CREATE INDEX idx_users_city      ON users(city);

-- ============================================================
-- IMPRESSIONS  (ad was shown to user)
-- ============================================================
CREATE TABLE impressions (
    id               BIGSERIAL PRIMARY KEY,
    advertisement_id INTEGER NOT NULL REFERENCES advertisements(id) ON DELETE CASCADE,
    user_id          INTEGER REFERENCES users(id) ON DELETE SET NULL,
    branch_id        INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    user_latitude    NUMERIC(10, 7),
    user_longitude   NUMERIC(10, 7),
    distance_km      NUMERIC(8, 3),
    device_type      VARCHAR(50),
    ip_address       INET,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_impressions_ad_id     ON impressions(advertisement_id);
CREATE INDEX idx_impressions_user_id   ON impressions(user_id);
CREATE INDEX idx_impressions_branch_id ON impressions(branch_id);
CREATE INDEX idx_impressions_created   ON impressions(created_at DESC);

-- ============================================================
-- CLICKS
-- ============================================================
CREATE TABLE clicks (
    id               BIGSERIAL PRIMARY KEY,
    impression_id    BIGINT NOT NULL REFERENCES impressions(id) ON DELETE CASCADE,
    advertisement_id INTEGER NOT NULL REFERENCES advertisements(id) ON DELETE CASCADE,
    user_id          INTEGER REFERENCES users(id) ON DELETE SET NULL,
    cta_url          TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_clicks_impression_id ON clicks(impression_id);
CREATE INDEX idx_clicks_ad_id         ON clicks(advertisement_id);
CREATE INDEX idx_clicks_created       ON clicks(created_at DESC);

-- ============================================================
-- CONVERSIONS
-- ============================================================
CREATE TABLE conversions (
    id               BIGSERIAL PRIMARY KEY,
    click_id         BIGINT REFERENCES clicks(id) ON DELETE SET NULL,
    advertisement_id INTEGER NOT NULL REFERENCES advertisements(id) ON DELETE CASCADE,
    user_id          INTEGER REFERENCES users(id) ON DELETE SET NULL,
    branch_id        INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    conversion_type  VARCHAR(50) NOT NULL DEFAULT 'visit'
                         CHECK (conversion_type IN ('visit', 'purchase', 'signup', 'call')),
    revenue          NUMERIC(12, 2),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversions_ad_id     ON conversions(advertisement_id);
CREATE INDEX idx_conversions_branch_id ON conversions(branch_id);
CREATE INDEX idx_conversions_created   ON conversions(created_at DESC);

-- ============================================================
-- ANALYTICS  (daily roll-up per ad per branch)
-- ============================================================
CREATE TABLE analytics (
    id               SERIAL PRIMARY KEY,
    advertisement_id INTEGER NOT NULL REFERENCES advertisements(id) ON DELETE CASCADE,
    branch_id        INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
    date             DATE NOT NULL,
    impressions      INTEGER NOT NULL DEFAULT 0,
    clicks           INTEGER NOT NULL DEFAULT 0,
    conversions      INTEGER NOT NULL DEFAULT 0,
    revenue          NUMERIC(12, 2) NOT NULL DEFAULT 0,
    ctr              NUMERIC(6, 4) GENERATED ALWAYS AS (
                         CASE WHEN impressions > 0
                              THEN ROUND(clicks::NUMERIC / impressions, 4)
                              ELSE 0 END
                     ) STORED,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_analytics_ad_branch_date UNIQUE (advertisement_id, branch_id, date)
);

CREATE INDEX idx_analytics_ad_id     ON analytics(advertisement_id);
CREATE INDEX idx_analytics_branch_id ON analytics(branch_id);
CREATE INDEX idx_analytics_date      ON analytics(date DESC);

-- ============================================================
-- UPDATED_AT TRIGGER (shared)
-- ============================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_brands_updated_at     BEFORE UPDATE ON brands     FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_branches_updated_at   BEFORE UPDATE ON branches   FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_campaigns_updated_at  BEFORE UPDATE ON campaigns  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_offers_updated_at     BEFORE UPDATE ON offers     FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_ads_updated_at        BEFORE UPDATE ON advertisements FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_users_updated_at      BEFORE UPDATE ON users      FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- SAMPLE DATA
-- ============================================================
INSERT INTO brands (name, slug, logo_url, website) VALUES
    ('Haldiram''s', 'haldirams', 'https://cdn.example.com/haldirams-logo.png', 'https://haldirams.com'),
    ('Amul',        'amul',      'https://cdn.example.com/amul-logo.png',      'https://amul.com');

INSERT INTO branches (brand_id, branch_name, latitude, longitude, address, city, state, pincode) VALUES
    (1, 'Electronic City', 12.8399, 77.6770, 'Hosur Rd, Electronic City Phase 1', 'Bengaluru', 'Karnataka', '560100'),
    (1, 'Koramangala',     12.9352, 77.6245, '5th Block, Koramangala',             'Bengaluru', 'Karnataka', '560095'),
    (1, 'Indiranagar',     12.9784, 77.6408, '100 Feet Rd, Indiranagar',           'Bengaluru', 'Karnataka', '560038'),
    (2, 'MG Road',         12.9754, 77.6057, 'MG Road, Bengaluru',                 'Bengaluru', 'Karnataka', '560001');

INSERT INTO campaigns (brand_id, name, description, budget, start_date, end_date, status) VALUES
    (1, 'Monsoon Madness',  'Monsoon season promotions',   50000.00, '2024-06-01', '2024-08-31', 'active'),
    (1, 'Diwali Dhamaka',   'Festive season mega deals',  100000.00, '2024-10-01', '2024-11-15', 'draft'),
    (2, 'Summer Specials',  'Beat the heat with Amul',     30000.00, '2024-04-01', '2024-06-30', 'active');

INSERT INTO offers (branch_id, campaign_id, title, description, discount_percentage, start_date, end_date, valid_days) VALUES
    (1, 1, '50% OFF on Sweets',   'Half price on all sweets',      50.00, '2024-06-01', '2024-08-31', '{0,6}'),
    (2, 1, '30% OFF on Namkeen',  'Monsoon snack offer',           30.00, '2024-06-01', '2024-08-31', '{1,2,3,4,5}'),
    (3, 1, 'Buy 1 Get 1 Rasgulla','BOGO on Rasgullas',             NULL,  '2024-06-15', '2024-08-15', '{0,1,2,3,4,5,6}'),
    (4, 3, '20% OFF Ice Cream',   'Summer cooldown special',       20.00, '2024-04-01', '2024-06-30', '{0,1,2,3,4,5,6}');
