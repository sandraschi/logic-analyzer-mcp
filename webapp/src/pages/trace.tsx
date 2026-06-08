import { callTool, runCapture } from '@/lib/api';
import { useCallback, useEffect, useRef, useState } from 'react';

type Preview = {
  channels: Record<string, number[]>;
};

const LANE_HEIGHT = 28;

export default function Trace() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const draw = useCallback((data: Preview) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const channelIds = Object.keys(data.channels);
    const height = Math.max(200, channelIds.length * LANE_HEIGHT + 40);
    canvas.height = height;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = '#09090b';
    ctx.fillRect(0, 0, width, height);

    const colors = [
      '#22d3ee',
      '#3b82f6',
      '#10b981',
      '#f59e0b',
      '#ef4444',
      '#a855f7',
      '#ec4899',
      '#84cc16',
    ];
    if (!channelIds.length) return;

    channelIds.forEach((id, index) => {
      const samples = data.channels[id];
      const yBase = 24 + index * LANE_HEIGHT;
      const laneMid = yBase + LANE_HEIGHT / 2;

      ctx.strokeStyle = '#27272a';
      ctx.beginPath();
      ctx.moveTo(80, laneMid);
      ctx.lineTo(width - 12, laneMid);
      ctx.stroke();

      ctx.fillStyle = colors[index % colors.length];
      ctx.font = '12px monospace';
      ctx.fillText(id, 8, laneMid + 4);

      ctx.strokeStyle = colors[index % colors.length];
      ctx.lineWidth = 2;
      let lastX = 80;
      let lastHigh = samples[0] === 1;
      samples.forEach((v, i) => {
        const x = 80 + (i / Math.max(samples.length - 1, 1)) * (width - 92);
        const high = v === 1;
        const yHigh = yBase + 6;
        const yLow = yBase + LANE_HEIGHT - 6;
        if (i === 0) {
          ctx.beginPath();
          ctx.moveTo(x, high ? yHigh : yLow);
        } else {
          ctx.lineTo(lastX, high ? yHigh : yLow);
          ctx.lineTo(x, high ? yHigh : yLow);
        }
        lastX = x;
        lastHigh = high;
        void lastHigh;
      });
      ctx.stroke();
    });
  }, []);

  useEffect(() => {
    if (preview) draw(preview);
  }, [preview, draw]);

  const connectSimulator = async () => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await callTool('la_device', { operation: 'connect', device_id: 'sim-la-001' });
      const payload = res.data?.data ?? res.data;
      setMessage(
        payload?.success !== false
          ? 'Connected to simulator'
          : (payload?.error ?? 'Connect failed'),
      );
    } catch (e) {
      setMessage(e instanceof Error ? e.message : 'Connect failed');
    }
    setBusy(false);
  };

  const capture = async () => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await runCapture({
        sample_rate_hz: 1_000_000,
        sample_count: 2048,
        channels: ['D0', 'D1', 'D2', 'D3'],
      });
      const previewData = res.data?.data?.preview as Preview | undefined;
      if (previewData) setPreview(previewData);
      setMessage('Capture complete');
    } catch (e) {
      setMessage(e instanceof Error ? e.message : 'Capture failed');
    }
    setBusy(false);
  };

  return (
    <div className="max-w-6xl">
      <h1 className="text-2xl font-bold mb-2">Trace Viewer</h1>
      <p className="text-zinc-400 mb-4">
        Digital lane preview from la_capture (simulator or sigrok hardware).
      </p>

      <div className="flex gap-3 mb-4">
        <button
          type="button"
          onClick={connectSimulator}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Connect simulator
        </button>
        <button
          type="button"
          onClick={capture}
          disabled={busy}
          className="rounded-lg bg-cyan-500/20 text-cyan-200 px-4 py-2 text-sm hover:bg-cyan-500/30 disabled:opacity-50"
        >
          Capture
        </button>
      </div>

      {message && <p className="text-sm text-zinc-400 mb-4">{message}</p>}

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
        <canvas ref={canvasRef} width={960} height={200} className="w-full rounded-lg" />
      </div>
    </div>
  );
}
