install:
	$(info [*] Preparing development environment...)
	@uv venv --allow-existing
	@uv sync

test:
	$(info [*] Running unit tests...)
	@uv run pytest

lint:
	@uv run black .