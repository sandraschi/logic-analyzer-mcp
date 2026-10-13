import { useState } from 'react';
import { callTool } from '@/lib/api';

const CHANNELS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7'];

export default function ConfigurePage() {
  const [channels, setChannels] = useState<string[]>(['D0', 'D1', 'D2', 'D3']);
  const [sampleRateHz, setSampleRateHz] = useState(1_000_000);
  const [pattern, setPattern] = useState('uart');
  const [current, setCurrent] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const toggleChannel = (ch: string) => {
    setChannels((prev) =>
      prev.includes(ch) ? prev.filter((c) => c !== ch) : [...prev, ch],
    );
  };

  const run = async (operation: string, args: Record<string, unknown> = {}) => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await callTool('la_configure', { operation, ...args });
      const inner = res.data;
      if (!res.success || inner?.success === false) {
        setMessage(inner?.error ?? inner?.message ?? `${operation} failed`);
        return;
      }
      setMessage(`${operation} ok`);
      if (operation === 'get') setCurrent(inner?.data ?? null);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : `${operation} failed`);
    } finally {
      setBusy(false);
    }
  };

  const applyChannels = async () => {
    if (!channels.length) {
      setMessage('Select at least one channel');
      return;
    }
    await run('channels', { channels });
  };

  const applySampleRate = async () => {
    await run('sample_rate', { sample_rate_hz: sampleRateHz });
  };

  const applyPattern = async () => {
    await run('simulator_pattern', { pattern });
  };

  return (
    <div className="max-w-6xl">
      <h1 className="text-2xl font-bold mb-2">Channel Configuration</h1>
      <p className="text-zinc-400 mb-4">Configure active digital channels, sample rate, and simulator pattern.</p>

      <div className="flex gap-3 mb-6">
        <button
          type="button"
          onClick={() => run('get')}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Read current config
        </button>
      </div>

      {message && <p className="text-sm text-zinc-400 mb-4">{message}</p>}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Active channels</h2>
          <div className="flex flex-wrap gap-2 mb-4">
            {CHANNELS.map((ch) => (
              <button
                key={ch}
                type="button"
                onClick={() => toggleChannel(ch)}
                className={`rounded-lg px-3 py-1.5 text-xs font-mono transition ${
                  channels.includes(ch)
                    ? 'bg-cyan-500/20 text-cyan-200'
                    : 'bg-zinc-800 text-zinc-500 hover:bg-zinc-700'
                }`}
              >
                {ch}
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={applyChannels}
            disabled={busy}
            className="rounded-lg bg-cyan-500/20 text-cyan-200 px-4 py-2 text-sm hover:bg-cyan-500/30 disabled:opacity-50"
          >
            Apply channels
          </button>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Sample rate</h2>
          <select
            value={sampleRateHz}
            onChange={(e) => setSampleRateHz(Number(e.target.value))}
            className="mb-4 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
          >
            <option value={1_000_000}>1 MS/s</option>
            <option value={6_000_000}>6 MS/s</option>
            <option value={24_000_000}>24 MS/s</option>
            <option value={100_000_000}>100 MS/s</option>
          </select>
          <button
            type="button"
            onClick={applySampleRate}
            disabled={busy}
            className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
          >
            Apply sample rate
          </button>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Simulator pattern</h2>
          <select
            value={pattern}
            onChange={(e) => setPattern(e.target.value)}
            className="mb-4 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
          >
            <option value="uart">UART</option>
            <option value="i2c">I2C</option>
            <option value="spi">SPI</option>
          </select>
          <button
            type="button"
            onClick={applyPattern}
            disabled={busy}
            className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
          >
            Apply pattern
          </button>
        </div>
      </div>

      {current && (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Current config</h2>
          <pre className="text-xs text-zinc-400 font-mono max-h-64 overflow-auto whitespace-pre-wrap">
            {JSON.stringify(current, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
