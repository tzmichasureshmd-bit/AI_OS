# ===== TZMICHA AI OS - Makefile =====
# Common commands for development and deployment

.PHONY: help dev start stop build deploy test clean

help: ## Show this help
	@echo ""
	@echo "  TZMICHA AI OS - Commands"
	@echo "  ========================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ===== Development =====

dev: ## Start all services for development
	docker compose up -d postgres redis qdrant
	cd apps/api && uvicorn src.app:app --reload --port 8000

infra: ## Start only infrastructure (DB, cache, vector)
	docker compose up -d postgres redis qdrant

api: ## Start only the API server
	cd apps/api && uvicorn src.app:app --reload --port 8000

web: ## Start only the frontend
	cd apps/web && npm run dev

# ===== Docker =====

start: ## Start everything in Docker
	docker compose up -d

stop: ## Stop all containers
	docker compose down

build: ## Build all Docker images
	docker compose build

logs: ## View logs
	docker compose logs -f

# ===== Production =====

deploy: ## Deploy to production
	docker compose -f docker-compose.prod.yml up -d --build

# ===== Database =====

db-migrate: ## Run database migrations
	cd apps/api && alembic upgrade head

db-reset: ## Reset database (WARNING: destroys data)
	docker compose down -v
	docker compose up -d postgres
	sleep 3
	cd apps/api && alembic upgrade head

# ===== Testing =====

test: ## Run tests
	cd apps/api && pytest

test-voice: ## Test voice pipeline
	cd apps/api && python -m scripts.test_voice

# ===== Cleanup =====

clean: ## Remove all containers, volumes, and build artifacts
	docker compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
