export default function Help() {
  return (
    <div className="max-w-3xl prose prose-invert">
      <h1 className="text-2xl font-bold mb-2">Help</h1>
      <p className="text-zinc-400 mb-6">Quick reference for logic-analyzer-mcp fleet workflows.</p>

      <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 mb-4 text-sm space-y-3">
        <h2 className="text-lg font-semibold text-zinc-100">Quickstart</h2>
        <ol className="list-decimal list-inside text-zinc-300 space-y-1 font-mono text-xs">
          <li>la_device(operation=&quot;connect&quot;, device_id=&quot;sim-la-001&quot;)</li>
          <li>
            la_capture(operation=&quot;single&quot;, sample_rate_hz=1000000, sample_count=4096)
          </li>
          <li>la_decode(operation=&quot;uart&quot;, rx=&quot;D0&quot;)</li>
          <li>la_capture(operation=&quot;export_vcd&quot;)</li>
        </ol>
      </section>

      <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 text-sm">
        <h2 className="text-lg font-semibold text-zinc-100 mb-2">Hardware</h2>
        <ul className="text-zinc-300 space-y-2">
          <li>
            <strong className="text-cyan-300">Hantek 6022BL</strong> — flip H/P for LA mode; sigrok
            fx2lafw (8ch @ 24 MHz)
          </li>
          <li>
            <strong className="text-cyan-300">DSLogic</strong> — dedicated LA; sigrok dslogic driver
          </li>
          <li>
            <strong className="text-cyan-300">Pair with oscilloscope-mcp</strong> — analog rails +
            digital buses
          </li>
        </ul>
      </section>
    </div>
  );
}
