# Hardware Guide

## Recommended tiers

| Tier | Model | Channels | Backend | Notes |
|------|-------|----------|---------|-------|
| Budget | Hantek 6022BL (LA mode) | 8 @ 24 MHz | sigrok fx2lafw | Same dongle as scope; flip H/P |
| Dedicated | DSLogic / Plus | 8–16 @ 100–400 MHz | sigrok dslogic | Better probes, stable driver |
| Clone | FX2 “Saleae Logic” | 8 @ 24 MHz | sigrok fx2lafw | $10–30; quality varies |

## Hantek 6022BL

- **Scope mode**: PyHT6022 / oscilloscope-mcp `hantek` backend
- **LA mode**: Press H/P — enumerates as Saleae Logic VID; use sigrok `fx2lafw`
- **Not USBXI**: USBXI is Hantek’s modular chassis system; 6022BE/BL are standalone USB

## DSLogic

Purpose-built LA with open sigrok support. Good default if you want a dedicated LA without hacking a scope dongle.

## What to avoid

Closed Windows-only software with no sigrok driver. If PulseView cannot see it, this MCP cannot either.

## Fleet pair

Use **oscilloscope-mcp** for analog rails (power, clocks, reset) and **logic-analyzer-mcp** for digital buses (SPI, I2C, UART, JTAG).
