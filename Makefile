.DEFAULT_GOAL := help
.PHONY: help install lint format test build clean example docker tf-fmt tf-validate

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install package with dev dependencies
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

lint: ## Run ruff and black in check mode
	ruff check src tests examples
	black --check src tests examples

format: ## Auto-format the codebase
	ruff check --fix src tests examples
	black src tests examples

test: ## Run the test suite
	pytest

example: ## Run the two-agent orchestration example (offline)
	python examples/two_agent_pipeline.py

build: ## Build distribution artifacts
	python -m pip install --upgrade build
	python -m build

docker: ## Build the container image
	docker build -t multi-agent-ai-framework:local .

tf-fmt: ## Format Terraform code
	terraform -chdir=terraform fmt -recursive

tf-validate: ## Validate the root Terraform module
	terraform -chdir=terraform init -backend=false
	terraform -chdir=terraform validate

clean: ## Remove build and cache artifacts
	rm -rf build dist *.egg-info src/*.egg-info .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
