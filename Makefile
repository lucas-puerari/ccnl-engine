.PHONY: setup demo docs lint format typecheck test cognitive-complexity coverage-matrix rehash contract-pages

# Dev setup

setup:
	uv pip install -e .
	git config core.hooksPath .githooks
	@echo "Git hooks activated (.githooks)"

docs:
	uv run python scripts/docs/gen_coverage_matrix.py
	uv run python scripts/docs/gen_contract_pages.py
	@echo "Serving docs at http://127.0.0.1:8000"
	uv run zensical serve

demo:
	uv build --wheel --out-dir demo/wheels --quiet
	@WHEEL_VERSION=$$(uv version --short) && \
	  rm -rf demo/_build && mkdir -p demo/_build/wheels demo/_build/i18n && \
	  sed "s/WHEEL_VERSION/$${WHEEL_VERSION}/g" demo/index.html \
	    > demo/_build/index.html && \
	  cp demo/app.py demo/_build/app.py && \
	  cp demo/style.css demo/_build/style.css && \
	  sed "s/WHEEL_VERSION/$${WHEEL_VERSION}/g" demo/ui.js \
	    > demo/_build/ui.js && \
	  cp demo/wheels/*.whl demo/_build/wheels/ && \
	  cp demo/i18n/*.json demo/_build/i18n/
	@echo "Wheel built. Serving demo at http://127.0.0.1:8080"
	python3 -m http.server 8080 --directory demo/_build --bind 127.0.0.1

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
