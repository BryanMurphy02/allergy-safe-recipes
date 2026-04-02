-- =============================================================
-- RECIPE ALLERGEN TRACKER — DATABASE SCHEMA
-- =============================================================


-- =============================================================
-- SECTION 1: SOURCES
-- The websites we scrape from.
-- =============================================================

CREATE TABLE sources (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    base_url    VARCHAR(255) NOT NULL UNIQUE,
    enabled     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO sources (name, base_url) VALUES
    ('BBC Good Food',  'https://www.bbcgoodfood.com');


-- =============================================================
-- SECTION 2: RECIPES
-- One row per recipe scraped from a source.
-- =============================================================

CREATE TABLE recipes (
    id            SERIAL PRIMARY KEY,
    source_id     INTEGER NOT NULL REFERENCES sources(id),
    title         VARCHAR(255) NOT NULL,
    url           VARCHAR(500) NOT NULL UNIQUE,
    description   TEXT,
    cuisine       VARCHAR(100),
    prep_time     INTEGER,   -- in minutes
    cook_time     INTEGER,   -- in minutes
    total_time    INTEGER,   -- in minutes (may differ from prep + cook)
    servings      INTEGER,
    image_url     VARCHAR(500),
    scraped_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_recipes_source ON recipes(source_id);
CREATE INDEX idx_recipes_cuisine ON recipes(cuisine);


-- =============================================================
-- SECTION 3: INGREDIENTS
-- A normalised list of unique ingredient names.
-- "Whole milk" and "full fat milk" would both normalise
-- to "milk" — this is handled by the scraper, not the DB.
-- =============================================================

CREATE TABLE ingredients (
    id               SERIAL PRIMARY KEY,
    raw_name         VARCHAR(255) NOT NULL,   -- exactly as scraped
    normalised_name  VARCHAR(255) NOT NULL,   -- cleaned up version
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(raw_name)
);

CREATE INDEX idx_ingredients_normalised ON ingredients(normalised_name);


-- =============================================================
-- SECTION 4: RECIPE_INGREDIENTS
-- Joins recipes to ingredients. One row per ingredient
-- per recipe, storing the quantity and unit as well.
-- =============================================================

CREATE TABLE recipe_ingredients (
    id             SERIAL PRIMARY KEY,
    recipe_id      INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_id  INTEGER NOT NULL REFERENCES ingredients(id),
    quantity       VARCHAR(50),    -- e.g. "2", "1/2", "a pinch"
    unit           VARCHAR(50),    -- e.g. "tbsp", "g", "cup"
    preparation    VARCHAR(100),   -- e.g. "finely chopped", "at room temperature"
    UNIQUE(recipe_id, ingredient_id)
);

CREATE INDEX idx_recipe_ingredients_recipe     ON recipe_ingredients(recipe_id);
CREATE INDEX idx_recipe_ingredients_ingredient ON recipe_ingredients(ingredient_id);


-- =============================================================
-- SECTION 5: ALLERGENS
-- The 4 true allergens we are tracking.
-- Pre-seeded — the scraper never adds to this table,
-- it only references it.
-- =============================================================

CREATE TABLE allergens (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,   -- e.g. "peanuts"
    display_name VARCHAR(100) NOT NULL,           -- e.g. "Peanuts"
    description  TEXT
);

INSERT INTO allergens (name, display_name, description) VALUES
    ('peanuts',    'Peanuts',    'Includes peanuts and peanut-derived ingredients such as peanut oil or peanut butter'),
    ('tree_nuts',  'Tree Nuts',  'Includes almonds, cashews, walnuts, pecans, pistachios, hazelnuts, and similar'),
    ('dairy',      'Dairy',      'Includes milk, cheese, butter, cream, yoghurt, and other milk-derived ingredients'),
    ('egg',        'Egg',        'Includes whole eggs, egg yolks, egg whites, and egg-derived ingredients');


-- =============================================================
-- SECTION 6: INGREDIENT_ALLERGENS
-- Maps which ingredients trigger which allergens.
-- This is the core of the allergen detection logic.
-- Populated by the scraper's allergen matcher.
-- =============================================================

CREATE TABLE ingredient_allergens (
    id             SERIAL PRIMARY KEY,
    ingredient_id  INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    allergen_id    INTEGER NOT NULL REFERENCES allergens(id),
    confidence     VARCHAR(20) NOT NULL DEFAULT 'high'
                   CHECK (confidence IN ('high', 'medium', 'low')),
    UNIQUE(ingredient_id, allergen_id)
);

CREATE INDEX idx_ingredient_allergens_ingredient ON ingredient_allergens(ingredient_id);
CREATE INDEX idx_ingredient_allergens_allergen   ON ingredient_allergens(allergen_id);


-- =============================================================
-- SECTION 7: RECIPE_ALLERGENS
-- A rolled-up summary of allergens per recipe.
-- Derived from recipe_ingredients + ingredient_allergens.
-- Updated by the scraper every time a recipe is processed.
-- This table exists purely for query performance — without it
-- the API would need a 4-table JOIN on every request.
-- =============================================================

CREATE TABLE recipe_allergens (
    id          SERIAL PRIMARY KEY,
    recipe_id   INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    allergen_id INTEGER NOT NULL REFERENCES allergens(id),
    UNIQUE(recipe_id, allergen_id)
);

CREATE INDEX idx_recipe_allergens_recipe   ON recipe_allergens(recipe_id);
CREATE INDEX idx_recipe_allergens_allergen ON recipe_allergens(allergen_id);


-- =============================================================
-- SECTION 8: DIETARY_TAGS
-- Lifestyle and preference tags. Not allergens, but used
-- for filtering. Pre-seeded — never written to by the scraper.
-- =============================================================

CREATE TABLE dietary_tags (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,   -- e.g. "vegan"
    display_name VARCHAR(100) NOT NULL,           -- e.g. "Vegan"
    description  TEXT
);

INSERT INTO dietary_tags (name, display_name, description) VALUES
    ('vegetarian',     'Vegetarian',     'Contains no meat or fish'),
    ('vegan',          'Vegan',          'Contains no animal products of any kind'),
    ('gluten_free',    'Gluten-Free',    'Contains no gluten-containing ingredients'),
    ('contains_raw_egg','Contains Raw Egg','Includes raw or lightly cooked egg, such as in mayonnaise or mousse');


-- =============================================================
-- SECTION 9: RECIPE_DIETARY_TAGS
-- Joins recipes to their dietary tags.
-- One row per tag per recipe.
-- =============================================================

CREATE TABLE recipe_dietary_tags (
    id            SERIAL PRIMARY KEY,
    recipe_id     INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    dietary_tag_id INTEGER NOT NULL REFERENCES dietary_tags(id),
    UNIQUE(recipe_id, dietary_tag_id)
);

CREATE INDEX idx_recipe_dietary_tags_recipe ON recipe_dietary_tags(recipe_id);
CREATE INDEX idx_recipe_dietary_tags_tag    ON recipe_dietary_tags(dietary_tag_id);


-- =============================================================
-- SECTION 10: SCRAPE_LOG
-- A record of every scrape attempt — success or failure.
-- Never updated, only inserted into. Your audit trail.
-- =============================================================

CREATE TABLE scrape_log (
    id            SERIAL PRIMARY KEY,
    source_id     INTEGER NOT NULL REFERENCES sources(id),
    url           VARCHAR(500) NOT NULL,
    status        VARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed', 'skipped')),
    error_message TEXT,
    scraped_at    TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scrape_log_source ON scrape_log(source_id);
CREATE INDEX idx_scrape_log_status ON scrape_log(status);
CREATE INDEX idx_scrape_log_scraped_at ON scrape_log(scraped_at);