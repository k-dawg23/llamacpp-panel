## 1. Release metadata

- [x] 1.1 Bump `pyproject.toml` and `llamacpp_panel/__init__.py` version to **0.1.1**
- [x] 1.2 Surface version **0.1.1** in the web UI (footer or about line)
- [x] 1.3 After merge, create and push git tag **`v0.1.1`** (and optional GitHub release notes)

## 2. GPU discovery backend

- [x] 2.1 Implement GPU enumeration (phase 1: `nvidia-smi` CSV parse) in a small module with typed models
- [x] 2.2 Add `GET /api/hardware/gpus` returning devices + source metadata
- [x] 2.3 Extend `LaunchProfile` / config with optional `gpu_device_id` (or equivalent) and wire through `PUT /api/config`

## 3. Apply selection at launch

- [x] 3.1 Update supervisor spawn to set child `CUDA_VISIBLE_DEVICES` (or documented Vulkan vars) when `gpu_device_id` is set
- [x] 3.2 Document mapping in `README.md` and note limitations for non-NVIDIA builds

## 4. Frontend: Settings and Models

- [x] 4.1 Fetch and display GPU list in Settings; show `<select>` when multiple devices; bind to saved profile field
- [x] 4.2 On Models tab, add persistent **Current model** summary and row highlight after **Use**; refresh summary when config reloads

## 5. Verification

- [x] 5.1 Manual check on a single-GPU and multi-GPU host if available
- [x] 5.2 Add unit tests for GPU parser (mock `nvidia-smi` output) and env application helper
