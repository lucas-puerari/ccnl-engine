.PHONY: setup format check lint typecheck complexity architecture test generate rehash docs demo

SITE := demo/release/site
PACKAGES := demo/release/packages

# Setup

setup:
	uv sync --locked --group dev
	uv pip install -e .
	git config core.hooksPath .githooks

# Quality gates

format:
	uv run ruff format src tests scripts
	uv run ruff check --fix src tests scripts

check: lint typecheck complexity architecture test

lint:
	uv run ruff check src tests scripts
	uv run ruff format --check src tests scripts

typecheck:
	uv run mypy src tests
	uv run mypy scripts --explicit-package-bases

complexity:
	uv run complexipy src tests scripts

architecture:
	uv run python scripts/architecture/check.py
	uv run python scripts/quality/test_tree/check.py

test:
	uv run pytest -n auto

# Generated artefacts: knowledge manifest and documentation pages

generate:
	uv run python scripts/knowledge/manifest/build.py
	uv run python scripts/documentation/contract_page/generate.py
	uv run python scripts/documentation/contract_example/generate.py
	uv run python scripts/documentation/trust_count/generate.py
	uv run python scripts/documentation/coverage_matrix/generate.py
	uv run python scripts/documentation/capability_matrix/generate.py
	uv run python scripts/documentation/review_plan/generate.py
	uv run python scripts/documentation/validation_matrix/generate.py

rehash:
	uv run python scripts/knowledge/update.py

# Local servers

docs: generate
	uv run zensical serve

demo:
	rm -rf $(SITE) $(PACKAGES)
	uv build --wheel --out-dir $(PACKAGES) --quiet
	mkdir -p $(SITE)/wheels/local $(SITE)/i18n
	sed "s/WHEEL_VERSION/$$(uv version --short)/g" demo/index.html > $(SITE)/index.html
	sed -e "s/WHEEL_VERSION/$$(uv version --short)/g" -e "s/WHEEL_BUILD/local/g" demo/ui.js > $(SITE)/ui.js
	cp demo/app.py demo/style.css $(SITE)/
	cp $(PACKAGES)/*.whl $(SITE)/wheels/local/
	cp demo/localization/*.json $(SITE)/i18n/
	python3 -m http.server 8080 --directory $(SITE) --bind 127.0.0.1
