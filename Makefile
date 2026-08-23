.PHONY: up down build test-backend test-web

ARCH := $(shell uname -m)
ifeq ($(ARCH),x86_64)
	OVERLAY := docker-compose.amd64.yml
else ifeq ($(ARCH),aarch64)
	OVERLAY := docker-compose.arm64.yml
else ifeq ($(ARCH),arm64)
	OVERLAY := docker-compose.arm64.yml
else
	OVERLAY :=
endif

COMPOSE := docker compose -f docker-compose.yml $(if $(OVERLAY),-f $(OVERLAY))

up: ## Demarre la stack pour l'architecture detectee ($(ARCH) -> $(OVERLAY))
	$(COMPOSE) up -d

down: ## Arrete la stack (sans supprimer les volumes)
	$(COMPOSE) down

build: ## (Re)construit les images pour l'architecture detectee
	$(COMPOSE) build

test-backend: ## pytest dans le conteneur backend
	$(COMPOSE) exec -T backend pytest -p no:cacheprovider -q

test-web: ## vitest local (pas de conteneur dedie — voir docs/ENVIRONNEMENT.md)
	cd web && npx vitest run
