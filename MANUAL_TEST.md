# Manual end-to-end check (Ubuntu)

Use a real llama.cpp bundle (for example a Vulkan tarball extracted so `llama-server` and `libggml-*.so` sit in the same directory).

1. Install dependencies and build the web UI per `README.md`.
2. Start the panel: `python -m llamacpp_panel`.
3. Open `http://127.0.0.1:8742`.
4. **Settings:** set bundle directory to your folder (e.g. `/home/you/Downloads/llama-b8882`), click **Validate binary**, confirm `ok: true` and version text.
5. **Models:** add a model root containing a `.gguf`, click **Scan GGUF**, click **Use** on a file (or set HF repo + **Save launch profile**).
6. **Server:** click **Start**, confirm logs show `llama-server` starting; **Stop** terminates the process.
7. **Monitor:** with the server running, confirm **Health** JSON updates; optional endpoints may show errors if disabled upstream (expected).
8. **GPUs (NVIDIA hosts):** on **Settings**, open the GPU section and **Refresh GPU list**; confirm devices match `nvidia-smi`. If multiple GPUs appear, pick one, save, start the server, and verify the process uses the intended card (e.g. watch GPU util). On machines without `nvidia-smi`, confirm a friendly “none” message and that **Default** still works.
9. **Models tab:** click **Use** on a GGUF row and confirm the **Current model** banner updates and the row is visually highlighted without switching tabs.

If `llama-server` fails to start, check logs in the **Server** tab and verify `LD_LIBRARY_PATH` would work when run manually from the bundle directory.
