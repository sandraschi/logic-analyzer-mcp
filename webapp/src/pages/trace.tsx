import { callTool, getLastCapture, getStatus, runCapture } from '@/lib/api';
import { useCallback, useEffect, useRef, useState } from 'react';

type Preview = {
  sample_rate_hz?: number;
  sample_count?: number;
  channels: Record<string, number[]>;
};

const LANE_HEIGHT = 28;
const ALL_CHANNELS = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7'];

export default function Trace() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [backend, setBackend] = useState<string | null>(null);

  const [sampleRateHz, setSampleRateHz] = useState(1_000_000);
  const [sampleCount, setSampleCount] = useState(2048);
  const [captureChannels, setCaptureChannels] = useState<string[]>(['D0', 'D1', 'D2', 'D3']);
  const [visibleChannels, setVisibleChannels] = useState<string[]>(['D0', 'D1', 'D2', 'D3']);
  const [filename, setFilename] = useState('');

  const draw = useCallback((data: Preview, visible: string[]) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const channelIds = Object.keys(data.channels).filter((id) => visible.includes(id));
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
      });
      ctx.stroke();
    });

    if (data.sample_rate_hz) {
      ctx.fillStyle = '#71717a';
      ctx.font = '10px monospace';
      ctx.fillText(`${(data.sample_rate_hz / 1_000_000).toFixed(1)} MS/s`, width - 120, height - 8);
    }
  }, []);

  useEffect(() => {
    if (preview) draw(preview, visibleChannels);
  }, [preview, draw, visibleChannels]);

  useEffect(() => {
    (async () => {
      const st = await getStatus();
      setBackend(st.active_backend ?? null);
      const last = await getLastCapture();
      if (last.success && last.data?.preview) {
        const p = last.data.preview as Preview;
        if (last.data?.capture) {
          p.sample_rate_hz = last.data.capture.sample_rate_hz ?? p.sample_rate_hz;
          p.sample_count = last.data.capture.sample_count ?? p.sample_count;
        }
        setPreview(p);
        const ids = Object.keys(p.channels);
        setVisibleChannels(ids);
        setMessage('Loaded last capture');
      }
    })();
  }, []);

  const capture = async () => {
    setBusy(true);
    setMessage(null);
    try {
      const res = await runCapture({
        sample_rate_hz: sampleRateHz,
        sample_count: sampleCount,
        channels: captureChannels,
      });
      const previewData = res.data?.data?.preview as Preview | undefined;
      if (previewData) {
        setPreview(previewData);
        setVisibleChannels(Object.keys(previewData.channels));
        setSampleRateHz(previewData.sample_rate_hz ?? sampleRateHz);
        setSampleCount(previewData.sample_count ?? sampleCount);
      }
      setMessage('Capture complete');
    } catch (e) {
      setMessage(e instanceof Error ? e.message : 'Capture failed');
    }
    setBusy(false);
  };

  const toggleCaptureChannel = (ch: string) => {
    setCaptureChannels((prev) =>
      prev.includes(ch) ? prev.filter((c) => c !== ch) : [...prev, ch],
    );
  };

  const toggleVisibleChannel = (ch: string) => {
    setVisibleChannels((prev) =>
      prev.includes(ch) ? prev.filter((c) => c !== ch) : [...prev, ch],
    );
  };

  const exportFile = async (operation: string) => {
    setBusy(true);
    setMessage(null);
    const stem = filename.trim() || undefined;
    const res = await callTool('la_capture', { operation, filename: stem });
    const inner = res.data;
    if (res.success && inner?.success !== false && inner?.data?.path) {
      setMessage(`Exported to ${inner.data.path}`);
    } else {
      setMessage(inner?.error ?? inner?.message ?? 'Export failed — run a capture first');
    }
    setBusy(false);
  };

  return (
    <div className="max-w-6xl">
      <div className="flex items-center gap-3 mb-2">
        <h1 className="text-2xl font-bold">Trace Viewer</h1>
        {backend && (
          <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-[10px] text-zinc-400">
            backend: {backend}
          </span>
        )}
      </div>
      <p className="text-zinc-400 mb-4">
        Digital lane preview from la_capture (simulator or sigrok hardware).
      </p>

      {message && <p className="text-sm text-zinc-400 mb-4">{message}</p>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4 items-end">
        <label className="text-xs text-zinc-500">
          Sample rate
          <select
            value={sampleRateHz}
            onChange={(e) => setSampleRateHz(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
          >
            <option value={1_000_000}>1 MS/s</option>
            <option value={6_000_000}>6 MS/s</option>
            <option value={24_000_000}>24 MS/s</option>
            <option value={100_000_000}>100 MS/s</option>
          </select>
        </label>
        <label className="text-xs text-zinc-500">
          Sample count
          <select
            value={sampleCount}
            onChange={(e) => setSampleCount(Number(e.target.value))}
            className="mt-1 w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
          >
            <option value={512}>512</option>
            <option value={1024}>1 024</option>
            <option value={2048}>2 048</option>
            <option value={4096}>4 096</option>
          </select>
        </label>
        <div className="col-span-2">
          <p className="text-xs text-zinc-500 mb-1">Capture channels</p>
          <div className="flex flex-wrap gap-1.5">
            {ALL_CHANNELS.map((ch) => (
              <button
                key={ch}
                type="button"
                onClick={() => toggleCaptureChannel(ch)}
                className={`rounded-md px-2 py-1 text-[10px] font-mono transition ${
                  captureChannels.includes(ch)
                    ? 'bg-cyan-500/20 text-cyan-200'
                    : 'bg-zinc-800 text-zinc-500 hover:bg-zinc-700'
                }`}
              >
                {ch}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="flex gap-3 mb-4 items-center">
        <button
          type="button"
          onClick={capture}
          disabled={busy}
          className="rounded-lg bg-cyan-500/20 text-cyan-200 px-4 py-2 text-sm hover:bg-cyan-500/30 disabled:opacity-50"
        >
          Capture
        </button>
        <input
          type="text"
          value={filename}
          onChange={(e) => setFilename(e.target.value)}
          placeholder="export filename stem"
          className="flex-1 rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100"
        />
        <button
          type="button"
          onClick={() => exportFile('export_csv')}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Export CSV
        </button>
        <button
          type="button"
          onClick={() => exportFile('export_vcd')}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Export VCD
        </button>
        <button
          type="button"
          onClick={() => exportFile('export_summary')}
          disabled={busy}
          className="rounded-lg border border-zinc-700 px-4 py-2 text-sm hover:bg-zinc-800 disabled:opacity-50"
        >
          Export summary
        </button>
      </div>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
        <canvas ref={canvasRef} width={960} height={200} className="w-full rounded-lg" />
        {!preview && (
          <p className="text-sm text-zinc-500 text-center py-8">No trace yet. Run a capture.</p>
        )}
      </div>

      {preview && (
        <div className="flex flex-wrap gap-4 mt-4 items-center">
          <span className="text-xs text-zinc-500">
            {(preview.sample_rate_hz ?? 0).toLocaleString()} S/s ·{' '}
            {(preview.sample_count ?? 0).toLocaleString()} samples
          </span>
          <div className="flex flex-wrap gap-1.5">
            {Object.keys(preview.channels).map((id) => (
              <button
                key={id}
                type="button"
                onClick={() => toggleVisibleChannel(id)}
                className={`rounded-md px-2 py-1 text-[10px] font-mono transition ${
                  visibleChannels.includes(id)
                    ? 'bg-emerald-500/20 text-emerald-200'
                    : 'bg-zinc-800 text-zinc-500 hover:bg-zinc-700'
                }`}
              >
                {id}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
