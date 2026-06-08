# Tools Reference

## la_device

| Operation | Description |
|-----------|-------------|
| list | All devices across backends |
| connect | Connect by device_id |
| disconnect | Drop session |
| status | Backend + connected device |
| capabilities | Channel count, max rate, decoders |
| backends | List backend names |

## la_configure

| Operation | Parameters |
|-----------|------------|
| channels | `channels: ["D0","D1"]` |
| sample_rate | `sample_rate_hz` |
| get | — |
| simulator_pattern | `pattern: uart\|i2c\|spi` |

## la_trigger

| Operation | Parameters |
|-----------|------------|
| set | `channel`, `pattern`, `mode`, `level` |
| get | — |

## la_capture

| Operation | Notes |
|-----------|-------|
| single | Acquire; stores last capture |
| preview | Downsampled JSON lanes |
| export_csv | CSV to capture_dir |
| export_vcd | VCD for PulseView |
| export_summary | JSON metadata |
| last | Return in-memory capture |

## la_decode

| Operation | Notes |
|-----------|-------|
| list | Available decoders |
| uart / i2c / spi | Shortcut decode ops |
| run | Generic with `protocol` |
| last | Last decode result |

## la_help

discover, tool_help, status, quickstart, faq, hardware_guide
