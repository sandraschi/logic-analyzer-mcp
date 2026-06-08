# Backends

## simulator

Always available. Generates synthetic digital patterns on D0–D7.

- Device ID: `sim-la-001`
- Decoders: stub UART/I2C/SPI rows for CI
- No external dependencies

## sigrok

Wraps `sigrok-cli` subprocess for scan, capture, and decode.

### Requirements

- `sigrok-cli` on PATH (PulseView installer)
- USB driver per device (fx2lafw, dslogic, …)
- Windows: Zadig WinUSB for many FX2 devices

### Scan

```powershell
sigrok-cli --scan
```

Device IDs in MCP are prefixed: `sigrok:<driver>:<usb-path>`

### Capture

Exports CSV via `-O csv`, parsed into `LogicCapture`.

### Decode

Builds `-P` decoder stack (e.g. `uart:rx=D0`, `i2c:sda=D0,scl=D1`).

### Env

```
LOGIC_ANALYZER_MCP_SIGROK_CLI=C:\Path\To\sigrok-cli.exe
```
