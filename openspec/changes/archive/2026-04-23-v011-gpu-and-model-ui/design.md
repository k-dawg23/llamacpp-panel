## Context

Release **v0.1.1** builds on the existing FastAPI supervisor and React UI. GPU selection must align with how [llama.cpp](https://github.com/ggml-org/llama.cpp) chooses devices: commonly `CUDA_VISIBLE_DEVICES` for NVIDIA CUDA builds, and Vulkan-visible device indices or documented env vars for Vulkan builds. The implementation should not guess undocumented flags; verify against the user’s installed `llama-server --help` where needed.

## Goals / Non-Goals

**Goals:**

- Enumerate devices with enough detail for users to tell GPUs apart (name, vendor, stable id).
- Persist `selected_device_id` (string) in `LaunchProfile` / config JSON.
- Apply selection on spawn for CUDA at minimum; stub or second-phase ROCm/Vulkan with explicit “experimental” messaging if detection is incomplete.
- Models tab: persistent **Current model** banner + highlight selected GGUF row.

**Non-Goals:**

- Remote GPU pools or multi-node.
- Automatic benchmark or VRAM sizing.
- Perfect support for every vendor on day one; ship NVIDIA-first with graceful fallback.

## Decisions

1. **Detection:** Prefer **`nvidia-smi --query-gpu=index,uuid,name --format=csv,noheader`** when `nvidia-smi` exists and returns rows. If absent, return empty list and a short explanation (no error spam).
2. **Persistence:** Store `gpu_device_id` (string) in launch profile; empty string means “default / all visible” behavior unchanged from today.
3. **Apply on spawn:** When `gpu_device_id` is set and looks like a CUDA index or UUID, set `CUDA_VISIBLE_DEVICES` for the child **only** (prepend/override for child env). Vulkan: map to `GGML_VK_VISIBLE_DEVICES` or documented variable after confirming against the user’s llama.cpp version README.
4. **API:** `GET /api/hardware/gpus` returns `{ devices: [{ id, name, vendor }], source: "nvidia-smi" | "none" }`.
5. **UI:** Settings shows read-only list + `<select>` when `devices.length > 1`; Models tab shows `Current model: …` bound to `launch_profile.local_model_path` or `hf_repo` + mode.

## Risks / Trade-offs

- **Wrong env for Vulkan build** → Document version matrix; integration test with user’s bundle when possible.
- **`nvidia-smi` missing in container** → Empty list; user can still run CPU or set manual extra args.

## Migration Plan

- Existing configs without `gpu_device_id`: treated as unset; no behavior change.
- After deploy, tag **`v0.1.1`** and push tags to GitHub.

## Open Questions

- Exact Vulkan env var name for the user’s llama.cpp revision (confirm at implement time).
- Whether to expose manual override text field for power users in the same release.
