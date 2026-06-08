from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path

from logic_analyzer_mcp.models.capture import LogicCapture


def ensure_capture_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def export_capture_csv(capture: LogicCapture, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    channel_ids = [ch.channel_id for ch in capture.channels]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sample_index", *channel_ids])
        for idx in range(capture.sample_count):
            row = [idx]
            for ch in capture.channels:
                row.append(ch.samples[idx])
            writer.writerow(row)
    return output_path


def export_capture_vcd(capture: LogicCapture, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    timescale_ns = int(1_000_000_000 / capture.sample_rate_hz) if capture.sample_rate_hz else 1
    lines = [
        "$date",
        datetime.now(UTC).isoformat(),
        "$end",
        "$timescale 1ns $end",
        "$scope module logic_analyzer_mcp $end",
    ]
    for ch in capture.channels:
        lines.append(f"$var wire 1 {ch.channel_id} {ch.channel_id} $end")
    lines.append("$enddefinitions $end")
    lines.append("$dumpvars")
    for ch in capture.channels:
        lines.append(f"0{ch.channel_id}")
    lines.append("$end")
    last_values = {ch.channel_id: ch.samples[0] if ch.samples else 0 for ch in capture.channels}
    for idx in range(capture.sample_count):
        time_ps = idx * timescale_ns
        changed = False
        for ch in capture.channels:
            value = ch.samples[idx]
            if value != last_values[ch.channel_id]:
                changed = True
                last_values[ch.channel_id] = value
                lines.append(f"{value}{ch.channel_id}")
        if changed:
            lines.append(f"#{time_ps}")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def export_capture_summary(capture: LogicCapture, output_path: Path) -> Path:
    payload = {"exported_at": datetime.now(UTC).isoformat(), "capture": capture.model_dump(mode="json")}
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def default_capture_filename(prefix: str = "logic_capture") -> str:
    return f"{prefix}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
