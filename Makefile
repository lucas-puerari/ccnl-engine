.PHONY: setup lint format typecheck test cognitive-complexity coverage-matrix rehash

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

cognitive-complexity:
	uv run complexipy src/ && echo "Cognitive Complexity check passed"

coverage-matrix:
	uv run python docs/scripts/gen_coverage_matrix.py

rehash:
	uv run python docs/scripts/rehash_ccnl.py

contract-pages:
	uv run python docs/scripts/gen_contract_pages.py
