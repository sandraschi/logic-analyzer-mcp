const BASE = '/api';

export interface StatusResponse {
  status: string;
  version: string;
  tool_count?: number;
  tools?: string[];
  active_backend?: string | null;
  connected_device?: Record<string, unknown> | null;
  capture_dir?: string;
}

export interface ToolInfo {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
}

export interface Capabilities {
  status: string;
  server?: { name: string; version: string };
  tool_surface?: { total: number; portmanteau_count: number; portmanteau_tools: string[] };
  features?: Record<string, boolean>;
  runtime?: { backend_port: number; frontend_port: number };
}

export async function getStatus(): Promise<StatusResponse> {
  const res = await fetch(`${BASE}/status`);
  return res.json();
}

export async function getCapabilities(): Promise<Capabilities> {
  const res = await fetch(`${BASE}/capabilities`);
  return res.json();
}

export async function getTools(): Promise<{ tools: ToolInfo[] }> {
  const res = await fetch(`${BASE}/tools`);
  return res.json();
}

export async function callTool(name: string, args: Record<string, unknown>) {
  const res = await fetch(`${BASE}/tools/${name}/call`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ arguments: args }),
  });
  return res.json();
}

export async function runCapture(args: {
  sample_rate_hz?: number;
  sample_count?: number;
  channels?: string[];
}) {
  const res = await fetch(`${BASE}/capture/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  return res.json();
}

export async function getLastCapture() {
  const res = await fetch(`${BASE}/capture/last`);
  return res.json();
}

export async function runDecode(args: {
  protocol?: string;
  rx?: string;
  sda?: string;
  scl?: string;
}) {
  const res = await fetch(`${BASE}/decode/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(args),
  });
  return res.json();
}

export async function getLastDecode() {
  const res = await fetch(`${BASE}/decode/last`);
  return res.json();
}
