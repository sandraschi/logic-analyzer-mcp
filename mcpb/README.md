# logic-analyzer-mcp (MCPB Bundle)

FastMCP 3.2+ server for USB logic analyzers via sigrok and simulator backends with protocol decoding and fleet webapp.

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "logic-analyzer-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "logic_analyzer_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **get_logs**: get_logs
- **clear_logs**: clear_logs
- **export_logs**: export_logs
- **health**: health
- **api_status**: api_status
- **api_capabilities**: api_capabilities
- **api_tools**: api_tools
- **api_tool_call**: api_tool_call
- **api_capture_last**: api_capture_last
- **api_capture_run**: api_capture_run
- **api_decode_last**: api_decode_last
- **llm_providers**: llm_providers
- **llm_chat**: llm_chat
- **api_decode_run**: api_decode_run
- **la_capture**: la_capture
- **la_capture_single**: la_capture(single)
- **la_capture_preview**: la_capture(preview)
- **la_capture_export_csv**: la_capture(export_csv)
- **la_capture_export_vcd**: la_capture(export_vcd)
- **la_capture_export_summary**: la_capture(export_summary)
- **la_capture_last**: la_capture(last)
- **la_configure**: la_configure
- **la_configure_channels**: la_configure(channels)
- **la_configure_sample_rate**: la_configure(sample_rate)
- **la_configure_get**: la_configure(get)
- **la_configure_simulator_pattern**: la_configure(simulator_pattern)
- **la_decode**: la_decode
- **la_decode_list**: la_decode(list)
- **la_decode_run**: la_decode(run)
- **la_decode_last**: la_decode(last)
- **la_decode_uart**: la_decode(uart)
- **la_decode_i2c**: la_decode(i2c)
- **la_decode_spi**: la_decode(spi)
- **la_device**: la_device
- **la_device_list**: la_device(list)
- **la_device_connect**: la_device(connect)
- **la_device_disconnect**: la_device(disconnect)
- **la_device_status**: la_device(status)
- **la_device_capabilities**: la_device(capabilities)
- **la_device_backends**: la_device(backends)
- **la_help**: la_help
- **la_help_discover**: la_help(discover)
- **la_help_tool_help**: la_help(tool_help)
- **la_help_status**: la_help(status)
- **la_help_quickstart**: la_help(quickstart)
- **la_help_faq**: la_help(faq)
- **la_help_hardware_guide**: la_help(hardware_guide)
- **la_trigger**: la_trigger
- **la_trigger_set**: la_trigger(set)
- **la_trigger_get**: la_trigger(get)

## Requirements

- Python 3.12+
- uv
