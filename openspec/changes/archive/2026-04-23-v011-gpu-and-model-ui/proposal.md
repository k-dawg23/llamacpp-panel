## Why

Users on multi-GPU machines need to see what hardware is available and reliably target one device for `llama-server`, but the panel today only exposes layer count (`-ngl`) and gives no inventory or device choice. Separately, choosing a model on the **Models** tab via **Use** saves in the background with little on-screen confirmation, which feels broken or ambiguous. This release (tagged **v0.1.1**) addresses both usability gaps before broader feature work.

## What Changes

- Bump shipped version to **0.1.1** and document tagging **`v0.1.1`** for the release.
- **GPU awareness:** Detect and display accelerator devices (at minimum NVIDIA via `nvidia-smi` when present; extend or degrade gracefully for other stacks). Expose details (vendor, model name, stable id) via the supervisor API and Settings UI.
- **Multi-GPU selection:** When more than one compatible device is reported, the UI SHALL offer an explicit control to choose which device to use; the choice SHALL persist in the launch profile and SHALL be applied when spawning `llama-server` (for example via backend-appropriate environment variables such as `CUDA_VISIBLE_DEVICES` / Vulkan-visible-device patterns per upstream llama.cpp behavior).
- **Models tab feedback:** After **Use** (or equivalent “set active model”), the Models tab SHALL show an immediate, persistent “current model” summary and clear visual distinction for the selected row (or equivalent affordance) without requiring a trip to Settings.

## Capabilities

### New Capabilities

- `gpu-devices`: Discover GPUs/accelerators, report structured device metadata via API, persist user-selected device identifier in configuration, and document backend-specific application rules.

### Modified Capabilities

- `control-panel-ui`: Extend Settings to surface GPU inventory and multi-device selection; strengthen Model library requirements so active model selection is visibly confirmed on the Models tab.
- `server-supervisor`: Require that supervised launch applies the saved GPU/device selection to the child process environment or arguments in line with the active backend.

## Impact

- **Backend:** New endpoint(s) for hardware discovery; optional dependencies or subprocess calls (`nvidia-smi`, future ROCm/Vulkan probes); launch profile and config schema extended with device selection fields; argument/environment builder updated.
- **Frontend:** Settings section for GPUs; Models tab “current model” strip and row highlighting; version display **0.1.1** where appropriate.
- **Docs:** README note on multi-GPU and tagging; release checklist including `git tag v0.1.1`.
- **Compatibility:** Non-breaking for existing configs; missing detection SHALL degrade to today’s behavior with a clear “no GPUs enumerated” message.
