import { getLastDecode, runCapture, runDecode } from '@/lib/api';
import { useEffect, useState } from 'react';

type DecodeResult = {
  protocol: string;
  rows: Record<string, unknown>[];
  annotations?: string[];
  source_capture?: string | null;
};

const PROTOCOL_CHANNELS: Record<string, { key: string; label: string; def: string }[]> = {
  uart: [
    { key: 'rx', label: 'RX', def: 'D0' },
    { key: 'tx', label: 'TX', def: 'D1' },
  ],
  i2c: [
    { key: 'sda', label: 'SDA', def: 'D0' },
    { key: 'scl', label: 'SCL', def: 'D1' },
  ],
  spi: [
    { key: 'clk', label: 'CLK', def: 'D0' },
    { key: 'mosi', label: 'MOSI', def: 'D1' },
    { key: 'miso', label: 'MISO', def: 'D2' },
  ],
};

export default function Decode() {
  const [result, setResult] = useState<DecodeResult | null>(null);
  const [protocol, setProtocol] = useState('uart');
  const [channels, setChannels] = useState<Record<string, string>>({ rx: 'D0', tx: 'D1' });
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const last = await getLastDecode();
      if (last.success && last.data) {
        setResult(last.data);
        setProtocol(last.data.protocol);
        setMessage(`Loaded last decode (${last.data.protocol})`);
      }
    })();
  }, []);

  const switchProtocol = (p: string) => {
    setProtocol(p);
    setChannels(Object.fromEntries(PROTOCOL_CHANNELS[p].map((c) => [c.key, c.def])));
  };

  const captureAndDecode = async () => {
    setBusy(true);
    setMessage(null);
    try {
      await runCapture({ sample_rate_hz: 1_000_000, sample_count: 1024, channels: ['D0', 'D1', 'D2'] });
      await decodeNow();
    } catch (e) {
      setMessage(e instanceof Error ? e.message : 'Decode failed');
    } finally {
      setBusy(false);
    }
  };

  const decodeNow = async () => {
    setBusy(true);
    setMessage(null);
    try {
      const args: Record<string, string> = { protocol };
      for (const c of PROTOCOL_CHANNELS[protocol]) {
        const v = channels[c.key]?.trim();
        if (v) args[c.key] = v;
      }
      const res = await runDecode(args);
      const data = res.data?.data ?? res.data;
      setResult(data ?? null);
      setMessage(`Decoded ${protocol.toUpperCase()}`);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : 'Decode failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-2xl font-bold mb-2">Decode View</h1>
      <p className="text-zinc-400 mb-4">Protocol decode output from la_decode (UART, I2C, SPI).</p>

      {message && <p className="text-sm text-zinc-400 mb-4">{message}</p>}

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4 mb-6">
        <div className="flex flex-wrap gap-3 items-end">
          <label className="text-xs text-zinc-500">
            Protocol
            <select
              value={protocol}
              onChange={(e) => switchProtocol(e.target.value)}
              className="mt-1 rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
            >
              <option value="uart">UART</option>
              <option value="i2c">I2C</option>
              <option value="spi">SPI</option>
            </select>
          </label>
          {PROTOCOL_CHANNELS[protocol].map((c) => (
            <label key={c.key} className="text-xs text-zinc-500">
              {c.label}
              <input
                type="text"
                value={channels[c.key] ?? ''}
                onChange={(e) => setChannels((prev) => ({ ...prev, [c.key]: e.target.value }))}
                className="mt-1 w-20 rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm font-mono text-zinc-100"
              />
            </label>
          ))}
          <button
            type="button"
            onClick={captureAndDecode}
            disabled={busy}
            className="rounded-lg bg-emerald-500/20 text-emerald-200 px-4 py-2 text-sm hover:bg-emerald-500/30 disabled:opacity-50"
          >
            Capture + decode
          </button>
          <button
            type="button"
            onClick={decodeNow}
            disabled={busy}
            className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
          >
            Decode last capture
          </button>
        </div>
      </div>

      {result && (
        <div className="flex flex-wrap gap-4 text-xs text-zinc-500 mb-4">
          <span>protocol: {result.protocol}</span>
          <span>{result.rows.length} rows</span>
          {result.source_capture && <span>source: {result.source_capture}</span>}
        </div>
      )}

      {result && result.annotations && result.annotations.length > 0 && (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-3 mb-4">
          {result.annotations.map((a, i) => (
            <p key={i} className="text-xs text-amber-200 font-mono">
              {a}
            </p>
          ))}
        </div>
      )}

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
            {(result?.rows.length ?? 0) === 0 ? (
              <tr>
                <td colSpan={3} className="px-4 py-8 text-zinc-500 text-center">
                  No decode rows yet. Run capture + decode.
                </td>
              </tr>
            ) : (
              result!.rows.map((row, idx) => (
                <tr key={idx} className="border-t border-zinc-800">
                  <td className="px-4 py-2 font-mono text-zinc-500">{idx + 1}</td>
                  <td className="px-4 py-2 text-cyan-300">{String(row.type ?? row.line ?? '-')}</td>
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
