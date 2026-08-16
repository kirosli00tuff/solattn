.PHONY: help install lint typecheck test verify watch collect checkpoint counts report clean

help: ## List available targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

install: ## Sync the Python environment (uv) and install pre-commit hooks
	uv sync --group dev
	uv run pre-commit install

lint: ## Ruff format check + lint
	uv run ruff format --check .
	uv run ruff check .

typecheck: ## Mypy --strict over solattn/ and tests/
	uv run mypy

test: ## Run the pytest suite (includes the honesty and registration tests)
	uv run pytest

verify: ## Measured access verification per source; writes docs/ACCESS.md
	uv run python -m solattn.cli verify

watch: ## Birth-ordered universe watcher; writes immutable daily manifests
	uv run python -m solattn.cli watch

collect: ## Attention collectors for every source that verified
	uv run python -m solattn.cli collect

checkpoint: ## Outcome candle fetch at the registered horizon checkpoints
	uv run python -m solattn.cli checkpoint

counts: ## Daily sanity counts: messages, match rates, enumerated pools
	uv run python -m solattn.cli counts

report: ## Write the committed daily digest for a UTC day
	uv run python -m solattn.cli report

clean: ## Remove caches (never touches data/)
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +
