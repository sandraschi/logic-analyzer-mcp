import { useState } from "react";
import { callTool, runCapture, runDecode } from "@/lib/api";

export default function Decode() {
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [protocol, setProtocol] = useState("uart");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const captureAndDecode = async () => {
    setBusy(true);
    setMessage(null);
    try {
      await callTool("la_device", { operation: "connect", device_id: "sim-la-001" });
      await runCapture({ sample_rate_hz: 1_000_000, sample_count: 1024, channels: ["D0", "D1"] });
      const decodeArgs =
        protocol === "i2c"
          ? { protocol: "i2c", sda: "D0", scl: "D1" }
          : protocol === "spi"
            ? { protocol: "spi", clk: "D0", mosi: "D1", miso: "D2" }
            : { protocol: "uart", rx: "D0" };
      const res = await runDecode(decodeArgs);
      const data = res.data?.data ?? res.data;
      setRows((data?.rows as Record<string, unknown>[]) ?? []);
      setMessage(`Decoded ${protocol.toUpperCase()}`);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Decode failed");
    }
    setBusy(false);
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-2xl font-bold mb-2">Decode View</h1>
      <p className="text-zinc-400 mb-4">Protocol decode output from la_decode (UART, I2C, SPI).</p>

      <div className="flex gap-3 mb-4 items-center">
        <select
          value={protocol}
          onChange={(e) => setProtocol(e.target.value)}
          className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm"
        >
          <option value="uart">UART</option>
          <option value="i2c">I2C</option>
          <option value="spi">SPI</option>
        </select>
        <button
          type="button"
          onClick={captureAndDecode}
          disabled={busy}
          className="rounded-lg bg-emerald-500/20 text-emerald-200 px-4 py-2 text-sm hover:bg-emerald-500/30 disabled:opacity-50"
        >
          Capture + decode
        </button>
      </div>

      {message && <p className="text-sm text-zinc-400 mb-4">{message}</p>}

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-zinc-800/50 text-left text-zinc-400">
            <tr>
              <th className="px-4 py-2">#</th>
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2">Payload</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-4 py-8 text-zinc-500 text-center">
                  No decode rows yet. Run capture + decode.
                </td>
              </tr>
            ) : (
              rows.map((row, idx) => (
                <tr key={idx} className="border-t border-zinc-800">
                  <td className="px-4 py-2 font-mono text-zinc-500">{idx + 1}</td>
                  <td className="px-4 py-2 text-cyan-300">{String(row.type ?? row.line ?? "-")}</td>
                  <td className="px-4 py-2 font-mono text-xs text-emerald-200">
                    {JSON.stringify(row)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
