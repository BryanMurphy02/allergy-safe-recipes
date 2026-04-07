# SafePlate — Recipe Allergen Tracker
 
> A containerised pipeline that scrapes recipes from BBC Good Food and Budget Bytes, detects allergens and dietary tags, stores everything in Postgres, and exposes a filtered query API via FastAPI with a React frontend.
 
---
 
## Purpose

The purpose of this project was to gain hands-on experience with DevOps best practices. With Claude AI acting as the software engineer, I could focus entirely on the DevOps role. The initial goal was to containerise a multi-service application with Docker and implement a CI/CD pipeline — both of which were accomplished — but many other valuable skills were picked up along the way.

A high-level summary of what was learned and implemented is below. A link to more in-depth documentation can be found [here](./documentation/main-takeaways.md).

### Docker

- Managing multiple `requirements.txt` files scoped per container
- Building and running multi-container stacks
- Writing multiple custom Dockerfiles within a single repository
- Containerising non-Python services (Node.js, nginx)
- Multi-stage Docker image builds

### CI Pipeline (GitHub Actions)

- Setting up branch protection rules
- Creating a CI pipeline that runs linting and tests on push and pull request events
- Running jobs in parallel and configuring job dependencies

### CD Pipeline (GitHub Actions)

- Building and pushing Docker images to GitHub Container Registry (GHCR)
- SSHing into a home server to pull and redeploy updated images
- Ensuring the full CI pipeline passes before CD begins

### GitHub

- Managing GitHub Secrets for sensitive credentials
- Generating tokens for CI/CD authentication
- Using a Tailscale auth key to allow the CD pipeline to SSH into a private home server
- Creating a GitHub Environment to scope variables and secrets per deployment target

## DevOps Overview

### Docker
 
> #### Containers
>
> There are 4 separate containers working together in a stack: a **Postgres** database, a **Python scraper**, a **Python API**, and a **React/Nginx** frontend. With the exception of the Postgres database, each container has a custom-built image with the root of the project as its context. The database image is pulled first and undergoes a health check before the remaining containers are built.
>
> Each container is placed on a specific network, enabling communication only with the necessary services:
>
> | Container | Network(s)        |
> |-----------|-------------------|
> | Database  | Backend           |
> | Scraper   | Backend           |
> | API       | Frontend, Backend |
> | Frontend  | Frontend          |
>
> ---
>
> #### Compose Files
>
> There are two Docker Compose files:
>
> - **`docker-compose.yml`** — The base configuration covering everything described above.
> - **`docker-compose.prod.yml`** — A production overlay that overwrites select portions of the base config, specifically tailored for a home Linux server. This file overrides image names to integrate with the CD pipeline, and closes off exposed ports so the stack is only reachable via an external Docker network.

### CI

### CD

*Last updated: 4/7/2026*

## Software Overview
 
SafePlate is a full-stack recipe allergen tracking application built on a three-service containerised architecture. A Python scraper service crawls BBC Good Food and Budget Bytes on a configurable schedule, extracting structured recipe data from each site's schema.org JSON-LD markup. Each recipe's ingredients are normalised and run through a keyword-based allergen matcher that detects four tracked allergens — peanuts, tree nuts, dairy, and egg — as well as a dietary tagger that classifies recipes as vegetarian, vegan, gluten-free, or containing raw egg. All scraped data is persisted to a PostgreSQL database using a normalised schema that separates recipes, ingredients, allergens, and dietary tags into dedicated tables with a pre-computed recipe-level allergen rollup for fast querying. The scraper is built with Python, Requests, and BeautifulSoup, with psycopg2 handling all database writes.
 
The API layer is built with FastAPI and SQLAlchemy, exposing a REST interface that allows recipes to be filtered by allergen exclusion, dietary tag, cuisine, and cook time. Responses are paginated and shaped using Pydantic schemas, with a clear separation between summary responses for list views and full detail responses for individual recipes. The frontend is a React single-page application built with Vite and styled with Tailwind CSS, served in production by nginx which also acts as a reverse proxy for API requests. The entire stack runs in Docker Compose with four services — PostgreSQL, scraper, API, and frontend — connected via a shared internal network. A GitHub Actions CI pipeline runs linting with ruff and two separate pytest suites on every push, covering 209 tests across the scraper and API layers.

*Last updated: 4/7/2026*
 
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

