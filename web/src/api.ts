const api = (path: string) => path;

export type LaunchProfile = {
  model_mode: "local" | "hf";
  local_model_path: string;
  hf_repo: string;
  server_host: string;
  server_port: number;
  ctx_size: number;
  n_gpu_layers: number;
  enable_metrics: boolean;
  api_key: string;
  extra_args: string;
  gpu_device_id: string;
};

export type AppConfig = {
  llama_bin_dir: string;
  supervisor_host: string;
  supervisor_port: number;
  model_roots: string[];
  log_buffer_lines: number;
  launch_profile: LaunchProfile;
};

export type GpuDevice = { id: string; name: string; vendor: string };

export async function getMeta(): Promise<{ version: string }> {
  const r = await fetch(api("/api/meta"));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function listGpus(): Promise<{
  devices: GpuDevice[];
  source: string;
  message: string;
}> {
  const r = await fetch(api("/api/hardware/gpus"));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function getConfig(): Promise<AppConfig> {
  const r = await fetch(api("/api/config"));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function putConfig(partial: Partial<AppConfig>): Promise<AppConfig> {
  const r = await fetch(api("/api/config"), {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(partial),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function validateBinary(llama_bin_dir?: string) {
  const r = await fetch(api("/api/validate-binary"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ llama_bin_dir: llama_bin_dir ?? null }),
  });
  return r.json();
}

export async function supervisorStatus() {
  const r = await fetch(api("/api/supervisor/status"));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function supervisorStart(launch_profile?: Partial<LaunchProfile>) {
  const r = await fetch(api("/api/supervisor/start"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ launch_profile: launch_profile ?? null }),
  });
  if (!r.ok) {
    const d = await r.json().catch(() => ({}));
    throw new Error((d as { detail?: string }).detail ?? r.statusText);
  }
  return r.json();
}

export async function supervisorStop() {
  const r = await fetch(api("/api/supervisor/stop"), { method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function listLocalModels() {
  const r = await fetch(api("/api/models/local"));
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{
    models: { path: string; size_bytes: number; mtime: number }[];
  }>;
}

export async function hfDownload(repo_id: string, filename: string) {
  const r = await fetch(api("/api/hf/download"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_id, filename }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{ job_id: string }>;
}

export async function hfJob(job_id: string) {
  const r = await fetch(api(`/api/hf/jobs/${job_id}`));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function monitorStatus() {
  const r = await fetch(api("/api/monitor"));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
