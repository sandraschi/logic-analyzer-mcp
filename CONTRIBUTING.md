# Contributing

1. Fork and clone to `D:\Dev\repos\logic-analyzer-mcp`
2. `uv sync --extra dev`
3. `just fix` before commit
4. `just test` — unit tests must pass
5. Mark hardware/sigrok tests with `@pytest.mark.integration`

Follow fleet standards in `mcp-central-docs/standards/`. PowerShell launchers only — no `&&`, no Linux syntax in scripts.
