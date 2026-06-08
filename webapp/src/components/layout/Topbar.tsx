export default function Topbar() {
  return (
    <header className="h-12 border-b border-zinc-800 bg-zinc-900/90 px-4 flex items-center justify-between">
      <p className="text-sm text-zinc-400">Fleet logic analyzer console</p>
      <p className="text-xs font-mono text-zinc-500">backend :10985 · frontend :10987</p>
    </header>
  );
}
