import { useState } from 'react';
import { callTool } from '@/lib/api';

const CHANNELS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7'];

export default function TriggerPage() {
  const [channel, setChannel] = useState('D0');
  const [pattern, setPattern] = useState('rising');
  const [mode, setMode] = useState('auto');
  const [level, setLevel] = useState(1);
  const [state, setState] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const run = async (operation: string, args: Record<string, unknown> = {}) => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await callTool('la_trigger', { operation, ...args });
      const inner = res.data;
      if (!res.success || inner?.success === false) {
        setMessage(inner?.error ?? inner?.message ?? `${operation} failed`);
        return;
      }
      setMessage(inner?.message ?? `${operation} ok`);
      if (inner?.data) setState(inner.data);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : `${operation} failed`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-6xl">
      <h1 className="text-2xl font-bold mb-2">Trigger Configuration</h1>
      <p className="text-zinc-400 mb-4">Configure the digital acquisition trigger (channel, edge/pattern, mode).</p>

      {message && <p className="text-sm text-zinc-400 mb-4">{message}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Settings</h2>
          <div className="grid grid-cols-2 gap-3">
            <label className="text-xs text-zinc-500">
              Channel
              <select
                value={channel}
                onChange={(e) => setChannel(e.target.value)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              >
                {CHANNELS.map((ch) => (
                  <option key={ch} value={ch}>
                    {ch}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-xs text-zinc-500">
              Edge / pattern
              <select
                value={pattern}
                onChange={(e) => setPattern(e.target.value)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              >
                <option value="rising">Rising</option>
                <option value="falling">Falling</option>
                <option value="high">High</option>
                <option value="low">Low</option>
              </select>
            </label>
            <label className="text-xs text-zinc-500">
              Mode
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              >
                <option value="auto">Auto</option>
                <option value="normal">Normal</option>
                <option value="single">Single</option>
                <option value="off">Off</option>
              </select>
            </label>
            <label className="text-xs text-zinc-500">
              Logic level
              <select
                value={level}
                onChange={(e) => setLevel(Number(e.target.value))}
                className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
              >
                <option value={1}>1 (high)</option>
                <option value={0}>0 (low)</option>
              </select>
            </label>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              type="button"
              onClick={() => run('set', { channel, pattern, mode, level })}
              disabled={busy}
              className="rounded-lg bg-cyan-500/20 text-cyan-200 px-4 py-2 text-sm hover:bg-cyan-500/30 disabled:opacity-50"
            >
              Set trigger
            </button>
            <button
              type="button"
              onClick={() => run('get')}
              disabled={busy}
              className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
            >
              Read
            </button>
          </div>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <h2 className="text-sm font-semibold mb-3 text-zinc-300">Current trigger</h2>
          {state ? (
            <pre className="text-xs text-zinc-400 font-mono whitespace-pre-wrap">
              {JSON.stringify(state, null, 2)}
            </pre>
          ) : (
            <p className="text-sm text-zinc-500">No trigger state loaded yet. Set or read a trigger.</p>
          )}
        </div>
      </div>
    </div>
  );
}
