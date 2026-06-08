# Setup

See [INSTALL.md](../INSTALL.md) for full paths.

## Minimal

```powershell
Set-Location D:\Dev\repos\logic-analyzer-mcp
uv sync --extra dev
just serve
```

## Webapp

```powershell
just webapp
```

## sigrok

1. Install PulseView from https://sigrok.org/wiki/Downloads
2. `sigrok-cli --scan` with LA connected
3. `la_device(operation="list")`

## Cursor

Add `logic-analyzer-mcp` to `mcp.json` (see README), restart Cursor.
