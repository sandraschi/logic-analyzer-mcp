import { callTool, getTools } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

const PORTMANTEAU_OPS: Record<string, string[]> = {
  la_device: ['list', 'connect', 'disconnect', 'status', 'capabilities', 'backends'],
  la_configure: ['channels', 'sample_rate', 'get', 'simulator_pattern'],
  la_trigger: ['set', 'get'],
  la_capture: ['single', 'preview', 'export_csv', 'export_vcd', 'export_summary', 'last'],
  la_decode: ['list', 'uart', 'i2c', 'spi', 'last'],
  la_help: ['discover', 'tool_help', 'status', 'quickstart', 'faq', 'hardware_guide'],
};

export default function ToolsPage() {
  const { data } = useQuery({ queryKey: ['tools'], queryFn: getTools });
  const [result, setResult] = useState<string>('');
  const [busy, setBusy] = useState(false);

  const run = async (name: string, operation: string) => {
    setBusy(true);
    try {
      const args: Record<string, unknown> = { operation };
      if (name === 'la_device' && operation === 'connect') args.device_id = 'sim-la-001';
      if (name === 'la_capture' && operation === 'single') {
        args.sample_rate_hz = 1_000_000;
        args.sample_count = 1024;
        args.channels = ['D0', 'D1'];
      }
      if (name === 'la_configure' && operation === 'channels') args.channels = ['D0', 'D1'];
      const res = await callTool(name, args);
      setResult(JSON.stringify(res, null, 2));
    } catch (e) {
      setResult(e instanceof Error ? e.message : 'Tool call failed');
    }
    setBusy(false);
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-2xl font-bold mb-2">Tools Hub</h1>
      <p className="text-zinc-400 mb-6">Portmanteau-aware MCP tool browser with dry-run calls.</p>

      <div className="space-y-4">
        {(data?.tools ?? []).map((tool) => (
          <div key={tool.name} className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
            <div>
              <p className="font-mono text-cyan-300">{tool.name}</p>
              <p className="text-sm text-zinc-400 mt-1 line-clamp-2">{tool.description}</p>
            </div>
            {PORTMANTEAU_OPS[tool.name] && (
              <div className="flex flex-wrap gap-2 mt-3">
                {PORTMANTEAU_OPS[tool.name].map((op) => (
                  <button
                    key={op}
                    type="button"
                    disabled={busy}
                    onClick={() => run(tool.name, op)}
                    className="rounded-md border border-zinc-700 px-2 py-1 text-xs font-mono hover:bg-zinc-800 disabled:opacity-50"
                  >
                    {op}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {result && (
        <pre className="mt-6 rounded-xl border border-zinc-800 bg-black/40 p-4 text-xs overflow-x-auto text-emerald-200">
          {result}
        </pre>
      )}
    </div>
  );
}
