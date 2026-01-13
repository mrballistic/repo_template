SHELL := /bin/bash

.PHONY: install sync test lint format

install:
	uv sync --group dev

sync:
	uv sync --group dev

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .
