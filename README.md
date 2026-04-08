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
> The **React/Nginx** container uses a multi-stage build to keep the final image as small as possible. The first stage installs dependencies and compiles the React app into static files via `npm run build`. The second stage copies only those static files into a fresh **Nginx** image, discarding the Node runtime entirely, and serves them using a custom `nginx.conf`.
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

> #### Linting, Testing & Branch Protection
>
> The Continuous Integration workflow uses GitHub Actions to run Python linting with **Ruff** and Python testing with **pytest** in parallel runners. This triggers on every push to the `dev` branch and on every pull request. The `main` branch also has branch protection enabled — nothing can be pushed directly to `main`, and pull requests can only be merged once linting and all tests pass.
>
> ---
>
> #### Docker Image Validation
>
> After linting and tests pass, the CI pipeline kicks off three additional parallel runners to verify that the custom Docker images for the **scraper**, **API**, and **frontend** build successfully.

### CD

> #### Overview
>
> The Continuous Deployment workflow treats the `main` branch and a home Linux server as **production**. This workflow only triggers once the CI pipeline has completed successfully on `main` following a merged pull request.
>
> ---
>
> #### Deployment Steps
>
> 1. **Build & Push Images** — Three parallel runners build and push the custom Docker images to **GHCR**, tagging each as `latest`.
> 2. **Connect to Production** — Once all images are built, the pipeline joins a **Tailscale** network and SSHes into the production server.
> 3. **Deploy** — A script runs on the server to:
>    - Create environment variables sourced from the production environment secrets on GitHub
>    - Pull the latest version of `main`
>    - Pull and run the latest Docker images from **GHCR**

### Current Port Usage

> The ports exposed by the project depend on which Docker Compose file is used:
>
> | Environment | Port Mapping | Notes                                                             |
> |-------------|--------------|-------------------------------------------------------------------|
> | Default     | `9001:80`    | Host port `9001` → container port `80` (frontend)                |
> | Production  | None         | All ports closed; accessible only via an external Docker network  |
>
> The production Compose file is specifically engineered to run on a home Linux server, which is why no ports are directly exposed.

*Last updated: 4/8/2026*

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
