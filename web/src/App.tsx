import type { CSSProperties, ReactElement, ReactNode } from "react";
import {
  cloneElement,
  isValidElement,
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";
import { HelpPanel } from "./HelpPanel";
import type { AppConfig, GpuDevice, LaunchProfile } from "./api";
import {
  getConfig,
  getMeta,
  hfDownload,
  hfJob,
  listGpus,
  listLocalModels,
  monitorStatus,
  putConfig,
  supervisorStart,
  supervisorStatus,
  supervisorStop,
  validateBinary,
} from "./api";

const presets: Record<string, Partial<LaunchProfile>> = {
  balanced: { ctx_size: 8192, n_gpu_layers: 99 },
  fast: { ctx_size: 4096, n_gpu_layers: 20 },
  quality: { ctx_size: 32768, n_gpu_layers: 99, enable_metrics: true },
};

type TabKey = "settings" | "models" | "server" | "monitor" | "help";

const TAB_ROWS: { key: TabKey; label: string; hint: string }[] = [
  {
    key: "settings",
    label: "Settings",
    hint: "llama-server binary path, model roots, launch profile (context, GPU, model path), and presets.",
  },
  {
    key: "models",
    label: "Models",
    hint: "Scan GGUF files under model roots, set the active model, and start Hugging Face downloads.",
  },
  {
    key: "server",
    label: "Server",
    hint: "Start or stop supervised llama-server and view live process logs.",
  },
  {
    key: "monitor",
    label: "Monitor",
    hint: "Poll the llama-server HTTP API for health, props, slots, and metrics.",
  },
  {
    key: "help",
    label: "Help",
    hint: "Full user guide: fields, tabs, and tips (same content as docs/panel-user-guide.md).",
  },
];

function launchProfileMatchesPreset(lp: LaunchProfile, presetName: string): boolean {
  const p = presets[presetName];
  if (!p) return false;
  return (Object.keys(p) as (keyof LaunchProfile)[]).every((k) => lp[k] === p[k]);
}

function tabButtonStyle(active: boolean): CSSProperties {
  return {
    padding: "8px 14px",
    borderRadius: 8,
    border: active ? "2px solid #5a8fd4" : "1px solid #2a3142",
    background: active ? "#2a3355" : "#151821",
    color: "#e8eaed",
    fontWeight: active ? 600 : 400,
    boxShadow: active ? "inset 0 0 0 1px rgba(90, 143, 212, 0.25)" : "none",
    cursor: "pointer",
  };
}

function presetToggleStyle(active: boolean): CSSProperties {
  return {
    padding: "8px 14px",
    borderRadius: 8,
    border: active ? "2px solid #5a8fd4" : "1px solid #2a3142",
    background: active ? "#252b48" : "#151821",
    color: "#e8eaed",
    fontWeight: active ? 600 : 400,
    cursor: "pointer",
  };
}

const srOnly: CSSProperties = {
  position: "absolute",
  width: 1,
  height: 1,
  padding: 0,
  margin: -1,
  overflow: "hidden",
  clip: "rect(0,0,0,0)",
  whiteSpace: "nowrap",
  border: 0,
};

function formatBytes(n: number) {
  if (n < 1024) return `${n} B`;
  const u = ["KB", "MB", "GB", "TB"];
  let v = n / 1024;
  let i = 0;
  while (v >= 1024 && i < u.length - 1) {
    v /= 1024;
    i++;
  }
  return `${v.toFixed(1)} ${u[i]}`;
}

export default function App() {
  const [cfg, setCfg] = useState<AppConfig | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState<TabKey>("settings");
  const [validation, setValidation] = useState<Record<string, unknown> | null>(null);
  const [models, setModels] = useState<{ path: string; size_bytes: number; mtime: number }[]>(
    [],
  );
  const [monitor, setMonitor] = useState<Record<string, unknown> | null>(null);
  const [sup, setSup] = useState<Record<string, unknown> | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const logRef = useRef<HTMLPreElement>(null);

  const [hfRepo, setHfRepo] = useState("");
  const [hfFile, setHfFile] = useState("");
  const [hfJobId, setHfJobId] = useState<string | null>(null);
  const [hfJobStatus, setHfJobStatus] = useState<Record<string, unknown> | null>(null);

  const [appVersion, setAppVersion] = useState<string>("");
  const [gpus, setGpus] = useState<GpuDevice[]>([]);
  const [gpuSource, setGpuSource] = useState<string>("none");
  const [gpuMessage, setGpuMessage] = useState<string>("");

  const refresh = useCallback(async () => {
    setErr(null);
    const c = await getConfig();
    setCfg(c);
  }, []);

  useEffect(() => {
    refresh().catch((e) => setErr(String(e)));
  }, [refresh]);

  useEffect(() => {
    getMeta()
      .then((m) => setAppVersion(m.version))
      .catch(() => setAppVersion(""));
  }, []);

  const refreshGpus = useCallback(async () => {
    try {
      const r = await listGpus();
      setGpus(r.devices);
      setGpuSource(r.source);
      setGpuMessage(r.message || "");
    } catch {
      setGpus([]);
      setGpuSource("none");
      setGpuMessage("Could not query GPUs");
    }
  }, []);

  useEffect(() => {
    if (tab === "settings") {
      void refreshGpus();
    }
  }, [tab, refreshGpus]);

  useEffect(() => {
    const t = window.setInterval(() => {
      supervisorStatus()
        .then(setSup)
        .catch(() => {});
    }, 2000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (tab !== "monitor") return;
    const t = window.setInterval(() => {
      monitorStatus()
        .then(setMonitor)
        .catch(() => setMonitor(null));
    }, 2000);
    monitorStatus()
      .then(setMonitor)
      .catch(() => setMonitor(null));
    return () => clearInterval(t);
  }, [tab]);

  useEffect(() => {
    const es = new EventSource("/api/logs/stream");
    es.onmessage = (ev) => {
      try {
        const j = JSON.parse(ev.data) as { line?: string };
        if (j.line) {
          setLogs((prev) => [...prev.slice(-4000), j.line!]);
        }
      } catch {
        /* ignore */
      }
    };
    es.onerror = () => es.close();
    return () => es.close();
  }, []);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    if (!hfJobId) return;
    const t = window.setInterval(() => {
      hfJob(hfJobId)
        .then(setHfJobStatus)
        .catch(() => {});
    }, 1000);
    hfJob(hfJobId)
      .then(setHfJobStatus)
      .catch(() => {});
    return () => clearInterval(t);
  }, [hfJobId]);

  const lp = cfg?.launch_profile;
  const gpuId = lp?.gpu_device_id ?? "";

  const savePartial = async (partial: Partial<AppConfig>) => {
    if (!cfg) return;
    setBusy(true);
    setErr(null);
    try {
      const next = await putConfig(partial);
      setCfg(next);
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  };

  const applyPreset = (name: string) => {
    if (!cfg) return;
    const p = presets[name];
    if (!p) return;
    void savePartial({
      launch_profile: { ...cfg.launch_profile, ...p },
    });
  };

  const refreshModels = async () => {
    setErr(null);
    try {
      const r = await listLocalModels();
      setModels(r.models);
    } catch (e) {
      setErr(String(e));
    }
  };

  const onValidate = async () => {
    if (!cfg) return;
    setErr(null);
    try {
      const v = await validateBinary(cfg.llama_bin_dir || undefined);
      setValidation(v);
    } catch (e) {
      setErr(String(e));
    }
  };

  const stylePanel = useMemo(
    () => ({
      background: "#1a1d26",
      border: "1px solid #2a3142",
      borderRadius: 10,
      padding: "1rem 1.25rem",
      marginBottom: "1rem",
    }),
    [],
  );

  if (!cfg || !lp) {
    return (
      <div style={{ padding: 24 }}>
        <p>Loading…</p>
        {err && <p style={{ color: "#f88" }}>{err}</p>}
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "1.25rem" }}>
      <header style={{ marginBottom: "1.25rem" }}>
        <h1 style={{ margin: "0 0 0.25rem", fontWeight: 600 }}>llama.cpp panel</h1>
        <p style={{ margin: 0, color: "#9aa3b5" }}>
          Configure <code>llama-server</code>, models, and monitoring (local only by default).
        </p>
      </header>

      <nav
        role="tablist"
        aria-label="Main sections"
        style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}
      >
        {TAB_ROWS.map(({ key: k, label, hint }) => (
          <button
            key={k}
            type="button"
            role="tab"
            id={`tab-${k}`}
            aria-selected={tab === k}
            aria-controls={`panel-${k}`}
            title={hint}
            onClick={() => setTab(k)}
            style={tabButtonStyle(tab === k)}
          >
            {label}
          </button>
        ))}
      </nav>

      {err && (
        <div style={{ ...stylePanel, borderColor: "#633" }}>
          <strong>Error</strong>
          <pre
            style={{
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              overflowWrap: "anywhere",
              margin: "0.5rem 0 0",
            }}
          >
            {err}
          </pre>
        </div>
      )}

      {tab === "settings" && (
        <div
          style={stylePanel}
          role="tabpanel"
          id="panel-settings"
          aria-labelledby="tab-settings"
        >
          <h2 style={{ marginTop: 0 }}>Paths and supervisor</h2>
          <label style={{ display: "block", marginBottom: 8 }}>
            <div style={{ color: "#9aa3b5", fontSize: 13 }} title="Folder containing llama-server and usually .so files for portable builds.">
              llama.cpp bundle directory
            </div>
            <input
              style={{ width: "100%", padding: 8, borderRadius: 6, border: "1px solid #2a3142", background: "#0e1016", color: "#e8eaed" }}
              value={cfg.llama_bin_dir}
              onChange={(e) =>
                setCfg({ ...cfg, llama_bin_dir: e.target.value })
              }
              placeholder="/path/to/llama-b8882"
              title="Absolute path to the directory with the llama-server executable."
              aria-describedby="hint-bundle-dir"
            />
            <span id="hint-bundle-dir" style={srOnly}>
              Absolute path to the directory with the llama-server executable (Vulkan/CUDA bundle).
            </span>
          </label>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
            <button
              type="button"
              disabled={busy}
              onClick={() => savePartial({ llama_bin_dir: cfg.llama_bin_dir })}
              style={btn}
              title="Write the bundle directory to saved configuration."
            >
              Save path
            </button>
            <button
              type="button"
              onClick={onValidate}
              style={btn}
              title="Check that llama-server exists at the resolved path and is executable."
            >
              Validate binary
            </button>
          </div>
          {validation && (
            <pre style={{ background: "#0e1016", padding: 12, borderRadius: 8, overflow: "auto" }}>
              {JSON.stringify(validation, null, 2)}
            </pre>
          )}

          <label style={{ display: "block", marginTop: 16 }}>
            <div style={{ color: "#9aa3b5", fontSize: 13 }} title="Directories scanned for .gguf when you click Scan GGUF on the Models tab.">
              Model roots (one per line)
            </div>
            <textarea
              style={{ width: "100%", minHeight: 80, padding: 8, borderRadius: 6, border: "1px solid #2a3142", background: "#0e1016", color: "#e8eaed" }}
              value={cfg.model_roots.join("\n")}
              onChange={(e) =>
                setCfg({
                  ...cfg,
                  model_roots: e.target.value.split("\n").map((s) => s.trim()).filter(Boolean),
                })
              }
              title="One absolute path per line; used by Models → Scan GGUF."
              aria-describedby="hint-model-roots"
            />
            <span id="hint-model-roots" style={srOnly}>
              One directory per line. The Models tab scans these paths for GGUF files.
            </span>
          </label>
          <button
            type="button"
            disabled={busy}
            onClick={() => savePartial({ model_roots: cfg.model_roots })}
            style={{ ...btn, marginTop: 8 }}
            title="Persist model root directories to configuration."
          >
            Save model roots
          </button>

          <h3>Launch profile</h3>
          <div style={{ display: "grid", gap: 10, gridTemplateColumns: "1fr 1fr" }}>
            <Field
              label="Model mode"
              hint="local: path to a .gguf file (-m). hf: Hugging Face repo id (-hf) if your build supports it."
            >
              <select
                value={lp.model_mode}
                onChange={(e) =>
                  setCfg({
                    ...cfg,
                    launch_profile: {
                      ...lp,
                      model_mode: e.target.value as LaunchProfile["model_mode"],
                    },
                  })
                }
                style={inputStyle}
              >
                <option value="local">local GGUF (-m)</option>
                <option value="hf">Hugging Face (-hf)</option>
              </select>
            </Field>
            <Field
              label="Server host"
              hint="HTTP bind address for llama-server (127.0.0.1 for local only; 0.0.0.0 exposes all interfaces)."
            >
              <input
                value={lp.server_host}
                onChange={(e) =>
                  setCfg({
                    ...cfg,
                    launch_profile: { ...lp, server_host: e.target.value },
                  })
                }
                style={inputStyle}
              />
            </Field>
            <Field
              label="Server port"
              hint="TCP port for the llama-server HTTP API (e.g. 8080). Must be free on the host."
            >
              <input
                type="number"
                value={lp.server_port}
                onChange={(e) =>
                  setCfg({
                    ...cfg,
                    launch_profile: { ...lp, server_port: Number(e.target.value) },
                  })
                }
                style={inputStyle}
              />
            </Field>
            <Field
              label="Context (-c)"
              hint="Context length in tokens. Lower if you hit OOM; upper bound depends on model and hardware."
            >
              <input
                type="number"
                value={lp.ctx_size}
                onChange={(e) =>
                  setCfg({
                    ...cfg,
                    launch_profile: { ...lp, ctx_size: Number(e.target.value) },
                  })
                }
                style={inputStyle}
              />
            </Field>
            <Field
              label="GPU layers (-ngl)"
              hint="Layers on GPU; 0 = CPU offload for GPU builds. 99 often means all layers—see llama-server --help."
            >
              <input
                type="number"
                value={lp.n_gpu_layers}
                onChange={(e) =>
                  setCfg({
                    ...cfg,
                    launch_profile: { ...lp, n_gpu_layers: Number(e.target.value) },
                  })
                }
                style={inputStyle}
              />
            </Field>
            <div style={{ gridColumn: "1 / -1", marginTop: 4 }}>
              <h3 style={{ margin: "0 0 8px", fontSize: 16 }}>GPU device</h3>
              <p style={{ margin: "0 0 8px", color: "#9aa3b5", fontSize: 13 }}>
                {gpuSource !== "none"
                  ? `Detected via ${gpuSource} (${gpus.length} device(s)).`
                  : gpuMessage || "No NVIDIA GPUs enumerated (nvidia-smi missing or none found). Vulkan builds may use a manual id such as vk:0."}
              </p>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 8 }}>
                <button
                  type="button"
                  style={btn}
                  title="Re-run GPU discovery (nvidia-smi when available)."
                  onClick={() => void refreshGpus()}
                >
                  Refresh GPU list
                </button>
              </div>
              {gpus.length > 0 && (
                <ul style={{ margin: "0 0 8px", paddingLeft: 20, color: "#c5cad6", fontSize: 13 }}>
                  {gpus.map((g) => (
                    <li key={g.id}>
                      <code>{g.id}</code> — {g.name}
                      {g.uuid ? (
                        <span style={{ display: "block", fontSize: 12, opacity: 0.85 }}>
                          UUID {g.uuid}
                        </span>
                      ) : null}
                    </li>
                  ))}
                </ul>
              )}
              {gpus.length > 1 ? (
                <Field
                  label="Use GPU for next launch"
                  hint="Restricts visible GPUs for the next start (CUDA and Vulkan indices when numeric, e.g. gpu:1). Empty = all visible."
                >
                  <select
                    value={gpuId}
                    style={inputStyle}
                    onChange={(e) => {
                      const v = e.target.value;
                      const nextLp = { ...lp, gpu_device_id: v };
                      setCfg({ ...cfg, launch_profile: nextLp });
                      void savePartial({ launch_profile: nextLp });
                    }}
                  >
                    <option value="">Default (all visible)</option>
                    {gpus.map((g) => (
                      <option key={g.id} value={g.id}>
                        {g.name}
                      </option>
                    ))}
                  </select>
                </Field>
              ) : (
                <Field
                  label="GPU device id (optional, e.g. gpu:1 or vk:0)"
                  hint="Manual id when auto-detection is missing: gpu:N for NVIDIA index, vk:N for Vulkan-only override. Leave empty for default."
                >
                  <input
                    value={gpuId}
                    style={inputStyle}
                    placeholder="Leave empty for default"
                    onChange={(e) =>
                      setCfg({
                        ...cfg,
                        launch_profile: { ...lp, gpu_device_id: e.target.value },
                      })
                    }
                  />
                </Field>
              )}
            </div>
            <Field
              label="API key (--api-key)"
              hint="Optional secret passed to llama-server. Recommended if you bind to non-loopback addresses."
            >
              <input
                type="password"
                value={lp.api_key}
                onChange={(e) =>
                  setCfg({
                    ...cfg,
                    launch_profile: { ...lp, api_key: e.target.value },
                  })
                }
                style={inputStyle}
                autoComplete="off"
              />
            </Field>
          </div>
          <label
            style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 8 }}
            title="Exposes server metrics endpoints when your llama-server build supports --metrics."
          >
            <input
              type="checkbox"
              checked={lp.enable_metrics}
              onChange={(e) =>
                setCfg({
                  ...cfg,
                  launch_profile: { ...lp, enable_metrics: e.target.checked },
                })
              }
            />
            Enable <code>--metrics</code>
          </label>
          <Field
            label={lp.model_mode === "local" ? "Local model path (-m)" : "HF repo (-hf)"}
            hint={
              lp.model_mode === "local"
                ? "Absolute path to the .gguf file used on server start."
                : "Hugging Face repository id (org/name) for -hf mode."
            }
          >
            <input
              value={lp.model_mode === "local" ? lp.local_model_path : lp.hf_repo}
              onChange={(e) =>
                setCfg({
                  ...cfg,
                  launch_profile:
                    lp.model_mode === "local"
                      ? { ...lp, local_model_path: e.target.value }
                      : { ...lp, hf_repo: e.target.value },
                })
              }
              style={{ ...inputStyle, width: "100%" }}
            />
          </Field>
          <Field
            label="Extra args (shell-quoted)"
            hint="Additional tokens appended to llama-server (e.g. --threads 8). Quoting rules match the supervisor implementation."
          >
            <input
              value={lp.extra_args}
              onChange={(e) =>
                setCfg({
                  ...cfg,
                  launch_profile: { ...lp, extra_args: e.target.value },
                })
              }
              style={{ ...inputStyle, width: "100%" }}
              placeholder='e.g. --threads 8'
            />
          </Field>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 8 }}>
            <span style={{ color: "#9aa3b5", alignSelf: "center" }} title="Apply starter values for context, GPU layers, and metrics. You still need Save launch profile.">
              Presets:
            </span>
            {Object.keys(presets).map((k) => {
              const active = launchProfileMatchesPreset(lp, k);
              return (
                <button
                  key={k}
                  type="button"
                  aria-pressed={active}
                  title={`Apply ${k} preset (context / GPU layers). Does not save until you click Save launch profile.`}
                  style={presetToggleStyle(active)}
                  onClick={() => applyPreset(k)}
                >
                  {k}
                </button>
              );
            })}
            <button
              type="button"
              disabled={busy}
              style={btnPrimary}
              title="Persist the launch profile fields to disk for the next server start."
              onClick={() => savePartial({ launch_profile: lp })}
            >
              Save launch profile
            </button>
          </div>
          {lp.server_host !== "127.0.0.1" && lp.server_host !== "localhost" && !lp.api_key && (
            <p style={{ color: "#fa0" }}>
              Non-loopback host without API key: consider setting <code>--api-key</code>.
            </p>
          )}
        </div>
      )}

      {tab === "models" && (
        <div style={stylePanel} role="tabpanel" id="panel-models" aria-labelledby="tab-models">
          <h2 style={{ marginTop: 0 }}>Model library</h2>
          <div
            style={{
              marginBottom: 16,
              padding: "12px 14px",
              borderRadius: 8,
              border: "1px solid #3d5a9c",
              background: "#1a2740",
            }}
          >
            <div style={{ fontSize: 12, color: "#9aa3b5", marginBottom: 4 }}>Current model</div>
            <div style={{ fontWeight: 600, wordBreak: "break-all" }}>
              {lp.model_mode === "local"
                ? lp.local_model_path || "— none selected —"
                : `Hugging Face: ${lp.hf_repo || "— none —"}`}
            </div>
            <div style={{ fontSize: 12, color: "#9aa3b5", marginTop: 6 }}>Mode: {lp.model_mode}</div>
          </div>
          <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
            <button
              type="button"
              style={btn}
              title="List .gguf files under configured model roots (Settings)."
              onClick={refreshModels}
            >
              Scan GGUF
            </button>
          </div>
          <div style={{ maxHeight: 240, overflow: "auto", border: "1px solid #2a3142", borderRadius: 8 }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
              <thead>
                <tr style={{ background: "#151821" }}>
                  <th style={th}>Path</th>
                  <th style={th}>Size</th>
                  <th style={th} />
                </tr>
              </thead>
              <tbody>
                {models.map((m) => {
                  const active =
                    lp.model_mode === "local" && m.path === lp.local_model_path;
                  return (
                  <tr
                    key={m.path}
                    style={
                      active
                        ? { background: "#1e3358", outline: "1px solid #4a7cbc" }
                        : undefined
                    }
                  >
                    <td style={td}><code style={{ wordBreak: "break-all" }}>{m.path}</code></td>
                    <td style={td}>{formatBytes(m.size_bytes)}</td>
                    <td style={td}>
                      <button
                        type="button"
                        style={btnSmall}
                        aria-pressed={active}
                        title={
                          active
                            ? "This row is the active local model for the next server start."
                            : "Set this GGUF as the local model and save the launch profile."
                        }
                        onClick={() => {
                          setCfg({
                            ...cfg,
                            launch_profile: {
                              ...lp,
                              model_mode: "local",
                              local_model_path: m.path,
                            },
                          });
                          void savePartial({
                            launch_profile: {
                              ...lp,
                              model_mode: "local",
                              local_model_path: m.path,
                            },
                          });
                        }}
                      >
                        {active ? "Selected" : "Use"}
                      </button>
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <h3>Hugging Face download</h3>
          <p style={{ color: "#9aa3b5", fontSize: 13, marginTop: 0, maxWidth: 720, lineHeight: 1.45 }}>
            Uses Hugging Face <strong>file paths</strong> from the repo&apos;s <strong>Files</strong> tab—not the{" "}
            <code style={{ fontSize: 12 }}>-hf org/repo:quant</code> shorthand that{" "}
            <code style={{ fontSize: 12 }}>llama-server</code> accepts. Example: if docs say{" "}
            <code style={{ fontSize: 12 }}>llama-server -hf unsloth/Qwen3.5-4B-GGUF:UD-Q4_K_XL</code>, enter repo{" "}
            <code style={{ fontSize: 12 }}>unsloth/Qwen3.5-4B-GGUF</code> and filename{" "}
            <code style={{ fontSize: 12 }}>Qwen3.5-4B-UD-Q4_K_XL.gguf</code> (the real object name on the Hub).
          </p>
          <div style={{ display: "grid", gap: 8, gridTemplateColumns: "1fr 1fr" }}>
            <Field
              label="Repo id"
              hint="Full id: organization/repository-name (e.g. unsloth/Qwen3.5-4B-GGUF). Must match the model page URL."
            >
              <input value={hfRepo} onChange={(e) => setHfRepo(e.target.value)} style={inputStyle} placeholder="org/model-repo" />
            </Field>
            <Field
              label="Filename in repo"
              hint="Exact path/filename in the repo (often ModelName-Quant.gguf). Open Files on huggingface.co and copy the name; colons belong in llama -hf syntax, not here."
            >
              <input
                value={hfFile}
                onChange={(e) => setHfFile(e.target.value)}
                style={inputStyle}
                placeholder="Qwen3.5-4B-UD-Q4_K_XL.gguf"
              />
            </Field>
          </div>
          <button
            type="button"
            style={btnPrimary}
            title="Queue a background download via huggingface_hub; status appears below."
            onClick={async () => {
              setErr(null);
              try {
                const r = await hfDownload(hfRepo.trim(), hfFile.trim());
                setHfJobId(r.job_id);
              } catch (e) {
                setErr(String(e));
              }
            }}
          >
            Start download
          </button>
          {hfJobStatus ? <HfDownloadJobPanel job={hfJobStatus} /> : null}
        </div>
      )}

      {tab === "server" && (
        <div style={stylePanel} role="tabpanel" id="panel-server" aria-labelledby="tab-server">
          <h2 style={{ marginTop: 0 }}>Operations</h2>
          <p>
            Status:{" "}
            <strong>{sup?.running ? `running (pid ${String(sup.pid)})` : "stopped"}</strong>
            {sup?.exit_code != null && ` · last exit ${String(sup.exit_code)}`}
          </p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button
              type="button"
              style={btnPrimary}
              disabled={busy || !!sup?.running}
              title="Spawn llama-server with the saved launch profile and bundle library path."
              onClick={async () => {
                setBusy(true);
                setErr(null);
                try {
                  await supervisorStart();
                  setSup(await supervisorStatus());
                } catch (e) {
                  setErr(String(e));
                } finally {
                  setBusy(false);
                }
              }}
            >
              Start
            </button>
            <button
              type="button"
              style={btn}
              disabled={busy || !sup?.running}
              title="Stop the supervised llama-server process (SIGTERM)."
              onClick={async () => {
                setBusy(true);
                setErr(null);
                try {
                  await supervisorStop();
                  setSup(await supervisorStatus());
                } catch (e) {
                  setErr(String(e));
                } finally {
                  setBusy(false);
                }
              }}
            >
              Stop
            </button>
          </div>
          <h3>Logs</h3>
          <pre
            ref={logRef}
            style={{
              background: "#0e1016",
              padding: 12,
              borderRadius: 8,
              maxHeight: 320,
              overflow: "auto",
              fontSize: 12,
              margin: 0,
            }}
          >
            {logs.join("\n")}
          </pre>
        </div>
      )}

      {tab === "monitor" && (
        <div style={stylePanel} role="tabpanel" id="panel-monitor" aria-labelledby="tab-monitor">
          <h2 style={{ marginTop: 0 }}>llama-server HTTP</h2>
          <p style={{ color: "#9aa3b5" }}>
            Polling <code>
              http://{lp.server_host}:{lp.server_port}
            </code>{" "}
            every 2s.
          </p>
          {monitor && (
            <>
              <h3>Health</h3>
              <pre style={preBox}>{JSON.stringify(monitor.health, null, 2)}</pre>
              <h3>Props (summary)</h3>
              <pre style={preBox}>{JSON.stringify(monitor.props, null, 2)}</pre>
              <h3>Slots</h3>
              <pre style={preBox}>{JSON.stringify(monitor.slots, null, 2)}</pre>
              <h3>Metrics</h3>
              <pre style={{ ...preBox, maxHeight: 200, overflow: "auto" }}>
                {typeof monitor.metrics === "string"
                  ? monitor.metrics
                  : JSON.stringify(monitor.metrics, null, 2)}
              </pre>
              <h3>Errors</h3>
              <pre style={preBox}>{JSON.stringify(monitor.errors, null, 2)}</pre>
            </>
          )}
        </div>
      )}

      {tab === "help" && (
        <div style={stylePanel} role="tabpanel" id="panel-help" aria-labelledby="tab-help">
          <h2 style={{ marginTop: 0 }}>User guide</h2>
          <p style={{ marginTop: 0, color: "#9aa3b5", fontSize: 14 }}>
            Same content as <code>docs/panel-user-guide.md</code> in the repository. For the latest after an upgrade, rebuild the web UI or open the file on disk.
          </p>
          <HelpPanel />
        </div>
      )}

      <footer style={{ marginTop: 24, paddingTop: 16, borderTop: "1px solid #2a3142", color: "#6b7280", fontSize: 13 }}>
        llamacpp-panel{appVersion ? ` v${appVersion}` : ""}
      </footer>
    </div>
  );
}

function HfDownloadJobPanel({ job }: { job: Record<string, unknown> }) {
  const err = job.error != null ? String(job.error) : "";
  const wrap: CSSProperties = {
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    overflowWrap: "anywhere",
  };
  return (
    <div
      style={{
        marginTop: 12,
        padding: 12,
        borderRadius: 8,
        border: "1px solid #2a3142",
        background: "#0e1016",
        maxWidth: "100%",
        overflow: "hidden",
        boxSizing: "border-box",
      }}
    >
      <div style={{ fontSize: 12, color: "#9aa3b5", marginBottom: 8 }}>Download job</div>
      <div style={{ fontSize: 14, marginBottom: 4 }}>
        <strong>Status:</strong> {String(job.status ?? "—")}
      </div>
      {"repo_id" in job ? (
        <div style={{ fontSize: 13, wordBreak: "break-all", marginBottom: 4 }}>
          <strong>Repo:</strong> {String(job.repo_id)}
        </div>
      ) : null}
      {"filename" in job ? (
        <div style={{ fontSize: 13, wordBreak: "break-all", marginBottom: 4 }}>
          <strong>Filename:</strong> {String(job.filename)}
        </div>
      ) : null}
      {"progress" in job && job.progress != null ? (
        <div style={{ fontSize: 13, marginBottom: 4 }}>
          <strong>Progress:</strong> {String(job.progress)}
        </div>
      ) : null}
      {"local_path" in job && job.local_path != null ? (
        <div style={{ fontSize: 13, wordBreak: "break-all", marginBottom: 4 }}>
          <strong>Local path:</strong> {String(job.local_path)}
        </div>
      ) : null}
      {err ? (
        <>
          <div style={{ marginTop: 10, color: "#f88", fontWeight: 600, fontSize: 13 }}>Error</div>
          <pre
            style={{
              ...wrap,
              margin: "8px 0 0",
              fontSize: 13,
              fontFamily: "ui-monospace, monospace",
              color: "#e8eaed",
            }}
          >
            {err}
          </pre>
        </>
      ) : null}
      <details style={{ marginTop: 12 }}>
        <summary style={{ cursor: "pointer", color: "#9aa3b5", fontSize: 13 }}>Raw JSON</summary>
        <pre style={{ ...wrap, marginTop: 8, fontSize: 12, color: "#c5cad6" }}>
          {JSON.stringify(job, null, 2)}
        </pre>
      </details>
    </div>
  );
}

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  const id = useId();
  const descId = hint ? `${id}-hint` : undefined;
  const control =
    hint && isValidElement(children)
      ? cloneElement(children as ReactElement<Record<string, unknown>>, {
          title: hint,
          "aria-describedby": descId,
        })
      : children;
  return (
    <label style={{ display: "block" }}>
      <div style={{ color: "#9aa3b5", fontSize: 13 }} title={hint}>
        {label}
      </div>
      {hint ? (
        <span id={descId} style={srOnly}>
          {hint}
        </span>
      ) : null}
      {control}
    </label>
  );
}

const inputStyle: CSSProperties = {
  width: "100%",
  padding: 8,
  borderRadius: 6,
  border: "1px solid #2a3142",
  background: "#0e1016",
  color: "#e8eaed",
};

const btn: CSSProperties = {
  padding: "8px 14px",
  borderRadius: 8,
  border: "1px solid #2a3142",
  background: "#151821",
  color: "#e8eaed",
};

const btnPrimary: CSSProperties = { ...btn, background: "#2d4a7c", borderColor: "#3d5a9c" };

const btnSmall: CSSProperties = { ...btn, padding: "4px 8px", fontSize: 13 };

const th: CSSProperties = { textAlign: "left", padding: 8, borderBottom: "1px solid #2a3142" };
const td: CSSProperties = { padding: 8, borderBottom: "1px solid #1e2230", verticalAlign: "top" };

const preBox: CSSProperties = {
  background: "#0e1016",
  padding: 12,
  borderRadius: 8,
  overflow: "auto",
  fontSize: 13,
};
