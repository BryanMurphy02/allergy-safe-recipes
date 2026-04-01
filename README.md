# Recipe Allergen Tracker

A containerised pipeline that scrapes recipes from BBC Good Food and Serious Eats, detects allergens and dietary tags, stores everything in Postgres, and exposes a filtered query API via FastAPI.

---

## Architecture

```
[ Scraper Service ] → [ Postgres DB ] ← [ FastAPI Layer ] ← [ Frontend (later) ]
  runs on schedule      stores all         serves filtered
  parses allergens      recipe data        recipe data
```

Three containers, each with its own Dockerfile, wired together via Docker Compose.

---

## Features

- Scrapes recipe data from BBC Good Food and Serious Eats using schema.org/Recipe JSON-LD markup
- Detects 4 allergens: **peanuts**, **tree nuts**, **dairy**, **egg**
- Tags dietary preferences: **vegetarian**, **vegan**, **gluten-free**, **contains raw egg**
- Scheduled scraping via cron
- REST API with allergen and dietary filtering
- `/health` and `/metrics` endpoints for monitoring (Prometheus + Grafana)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Scraper | Python, BeautifulSoup, Requests |
| Database | PostgreSQL |
| API | FastAPI |
| Containers | Docker, Docker Compose |
| CI | GitHub Actions |
| Monitoring | Prometheus, Grafana |

---

## Project Structure

```
.
├── scraper/
│   ├── Dockerfile
│   ├── main.py
│   ├── sources/
│   │   ├── bbc_good_food.py
│   │   └── serious_eats.py
│   ├── allergen_matcher.py
│   └── dietary_tagger.py
│
├── api/
│   ├── Dockerfile
│   ├── main.py
│   ├── routers/
│   │   ├── recipes.py
│   │   ├── allergens.py
│   │   └── dietary_tags.py
│   └── models.py
│
├── db/
│   └── schema.sql
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Database Schema

```
sources              — scraped websites (BBC Good Food, Serious Eats)
recipes              — title, url, cuisine, prep_time, cook_time, servings
ingredients          — normalised ingredient names
recipe_ingredients   — recipes ↔ ingredients with quantity and unit
allergens            — peanuts, tree nuts, dairy, egg
ingredient_allergens — ingredient → allergen mappings
recipe_allergens     — rolled-up allergen flags per recipe
dietary_tags         — vegetarian, vegan, gluten_free, contains_raw_egg
recipe_dietary_tags  — recipes ↔ dietary tags
scrape_log           — url, source, scraped_at, status, error_message
```

---

## API Endpoints

```
GET /recipes                              List all recipes (paginated)
GET /recipes?exclude_allergens=dairy,egg  Filter by allergen exclusion
GET /recipes?dietary_tags=vegan           Filter by dietary tag
GET /recipes/{id}                         Full recipe detail
GET /recipes/{id}/allergens               Allergen summary for a recipe
GET /recipes/{id}/dietary-tags            Dietary tag summary for a recipe
GET /allergens                            List all 4 allergens
GET /dietary-tags                         List all dietary tags
GET /sources                              List scraped sites
GET /health                               Liveness probe
GET /metrics                              Prometheus metrics
```

---

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- (Optional) Prometheus + Grafana for monitoring

### Setup

```bash
git clone https://github.com/your-username/recipe-allergen-tracker.git
cd recipe-allergen-tracker

cp .env.example .env
# Edit .env with your settings

docker-compose up --build
```

The API will be available at `http://localhost:8000`.

### Environment Variables

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=recipes

SCRAPE_INTERVAL_HOURS=24
BBC_ENABLED=true
SERIOUS_EATS_ENABLED=true
```

---

## DevOps Notes

This project is intentionally structured to provide DevOps practice across:

- Writing and managing multi-stage Dockerfiles
- Docker Compose networking and volume management
- Scheduled jobs via cron inside containers
- CI pipeline with GitHub Actions (lint, test, build)
- Health and metrics endpoints for Prometheus scraping
- Grafana dashboards for scrape success rate, recipe count over time, allergen distribution

---

## Roadmap

- [x] Database schema
- [ ] Scraper — BBC Good Food
- [ ] Scraper — Serious Eats
- [ ] Allergen matching logic
- [ ] Dietary tag detection
- [ ] FastAPI layer
- [ ] Docker Compose setup
- [ ] GitHub Actions CI
- [ ] Prometheus + Grafana monitoring
- [ ] Frontend

