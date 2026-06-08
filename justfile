set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# logic-analyzer-mcp project management

default:
    @just --list

version:
    @uv run python -c "import pathlib, tomllib; p = pathlib.Path('pyproject.toml'); print(tomllib.loads(p.read_text(encoding='utf-8'))['project']['version'])"

install:
    uv sync --extra dev
    pre-commit install

serve:
    uv run python -m logic_analyzer_mcp --stdio

serve-http:
    uv run python -m logic_analyzer_mcp --http --port 10985

webapp:
    @powershell -ExecutionPolicy Bypass -File webapp/start.ps1

lint:
    ruff check .
    ruff format --check .

fix:
    ruff check . --fix
    ruff format .

test:
    uv run pytest tests/ -v -m "not integration"

test-all:
    uv run pytest tests/ -v

test-integration:
    uv run pytest tests/integration -v -m integration

ci: lint test
