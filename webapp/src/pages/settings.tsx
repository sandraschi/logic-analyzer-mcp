import { useQuery } from "@tanstack/react-query";
import { getStatus } from "@/lib/api";

export default function Settings() {
  const { data: status } = useQuery({ queryKey: ["status"], queryFn: getStatus });

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold mb-2">Settings</h1>
      <p className="text-zinc-400 mb-6">Runtime configuration (env vars override defaults).</p>

      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 space-y-4 text-sm">
        <Row label="Backend port" value="10985" />
        <Row label="Frontend port" value="10987" />
        <Row label="Active backend" value={status?.active_backend ?? "auto"} />
        <Row label="Capture dir" value={status?.capture_dir ?? "./captures"} />
        <Row label="Env: LOGIC_ANALYZER_MCP_BACKEND" value="auto | simulator | sigrok" />
        <Row label="Env: LOGIC_ANALYZER_MCP_SIGROK_CLI" value="sigrok-cli (PATH)" />
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 border-b border-zinc-800 pb-3 last:border-0 last:pb-0">
      <span className="text-zinc-400">{label}</span>
      <span className="font-mono text-cyan-200 text-right">{value}</span>
    </div>
  );
}
