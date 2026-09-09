.PHONY: setup demo lint format typecheck test cognitive-complexity coverage-matrix rehash contract-pages

# Dev setup

setup:
	uv pip install -e .
	git config core.hooksPath .githooks
	@echo "Git hooks activated (.githooks)"

demo:
	uv build --wheel --out-dir demo/wheels --quiet
	@echo "Wheel built. Serving demo at http://localhost:8080"
	python3 -m http.server 8080 --directory demo

# Quality gates

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

cognitive-complexity:
	uv run complexipy src/ && echo "Cognitive Complexity check passed"

# Docs / data scripts

coverage-matrix:
	uv run python scripts/docs/gen_coverage_matrix.py

rehash:
	uv run python scripts/docs/rehash_ccnl.py

contract-pages:
	uv run python scripts/docs/gen_contract_pages.py
