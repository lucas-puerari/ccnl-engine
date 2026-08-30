.PHONY: setup lint format typecheck test

setup:
	uv pip install -e .
	git config core.hooksPath .githooks
	@echo "Git hooks activated (.githooks)"

lint:
	uv run ruff check src/
	uv run mypy src/

format:
	uv run ruff format src/
	uv run ruff check --fix src/

typecheck:
	uv run mypy src/

test:
	uv run pytest
