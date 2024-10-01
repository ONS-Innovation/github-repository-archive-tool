.DEFAULT_GOAL := all


.PHONY: all
all: ## Show the available make targets.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: clean
clean: ## Clean the temporary files.
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf .ruff_cache
	rm -rf megalinter-reports

.PHONY: format
format:  ## Format the code.
	poetry run black .
	poetry run ruff check . --fix

.PHONY: black
black:
	poetry run black --check .

.PHONY: ruff
ruff:
	poetry run ruff check .

.PHONY: ruff-fix
ruff-fix:
	poetry run ruff check repoarchivetool --fix

.PHONY: pylint
pylint:
	poetry run pylint .

.PHONY: lint
lint:  ## Run Python linter
	make ruff || true
	make black
	make pylint || true

.PHONY: mypy
mypy:  ## Run mypy.
	poetry run mypy repoarchivetool

.PHONY: install
install:  ## Install the dependencies excluding dev.
	poetry install --only main --no-root

.PHONY: install-dev
install-dev:  ## Install the dependencies including dev.
	poetry install --no-root