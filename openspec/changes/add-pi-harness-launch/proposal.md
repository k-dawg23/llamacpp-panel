## Why

The panel already helps users choose models, download from Hugging Face, and launch the upstream web UI, but it does not provide any way to start local project tooling from the same workflow. Users who keep `pi` projects beside their llama.cpp work still have to leave the panel and launch `pi` manually from the correct folder.

## What Changes

- Add a lightweight project-folder concept so the user can save one or more local project directories and choose one as the active project workspace.
- Add a panel action to launch `pi` from the currently selected project folder, using the locally installed `pi` command and treating that folder as the process working directory.
- Capture launch success and startup failures clearly in the UI so users can tell whether `pi` was started and which folder was used.
- Keep `pi` launch separate from the existing `llama-server` supervisor lifecycle so starting or stopping one does not implicitly control the other.
- Document how project folders and the `Start pi harness` action behave, including the expectation that `pi` and `pi-llama-cpp` are already installed on the host.

## Capabilities

### New Capabilities

- `project-tool-launchers`: Saved local project folders and host-side launching of supported tools from the selected folder, beginning with `pi`.

### Modified Capabilities

- `control-panel-ui`: Add project-folder selection and a clearly labeled action for launching `pi` from the chosen folder, with visible status or error feedback.

## Impact

- **Backend:** Config schema for saved project folders and current selection; new API endpoint or supervisor-adjacent service to launch `pi` with an explicit working directory; validation and error reporting around missing folders or missing `pi` on `PATH`.
- **Frontend:** New controls in the existing UI for managing project folders, selecting the active one, and triggering `pi` launch.
- **Docs:** README and [`docs/panel-user-guide.md`](/home/kdawg/AI/Cursor/llama_front_end/docs/panel-user-guide.md) updates for the new workflow.
- **Compatibility:** Non-breaking for existing llama.cpp usage; users who do not use `pi` can ignore the new project controls.
