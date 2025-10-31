CODE_COVERAGE = 72

install:
	$(info [*] Preparing development environment...)
	@uv venv
	@uv sync

test:
	$(info [*] Running unit tests...)
	@uv run pytest --cov-report=term-missing --cov-fail-under=$(CODE_COVERAGE) -vv
