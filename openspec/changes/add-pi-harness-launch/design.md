## Context

The current panel persists llama.cpp-related configuration, scans model roots, and supervises a single `llama-server` child process. It does not track user project workspaces and it does not expose any backend API for starting host-side tooling other than the supervised server.

Launching `pi` has two important differences from launching `llama-server`:

- it depends on the selected project folder as the working directory rather than the llama.cpp bundle directory
- it should remain independent from the `llama-server` lifecycle because users may want to run one, both, or neither

That makes this a cross-cutting change across config, backend process launching, frontend state, and user documentation.

## Goals / Non-Goals

**Goals:**

- Let the user save one or more absolute project folders and mark one as the current project workspace.
- Provide a backend action that launches `pi` with the selected project folder as `cwd`.
- Return enough launch metadata to the UI to show what happened without requiring deep terminal access.
- Keep the existing `llama-server` supervisor behavior unchanged and isolated from `pi`.

**Non-Goals:**

- Supervising or terminating `pi` after launch.
- Streaming `pi` output into the panel in this change.
- Managing `pi` installation, virtual environments, or `pi-llama-cpp` setup.
- General plugin execution for arbitrary shell commands beyond the initial `pi` workflow.

## Decisions

1. **Persist project folders in app config.** Add a small config section for saved project folder paths plus the currently selected path. This keeps the workflow stable across restarts and avoids inventing a second local state store in the frontend.
Alternative considered: frontend-only selection. Rejected because the user explicitly wants to launch from a selected folder and that selection should survive refreshes and restarts.

2. **Add a dedicated `pi` launch endpoint instead of folding it into the llama supervisor.** The backend should expose a focused route such as `POST /api/tools/pi/start` that validates the selected folder and launches `pi` in that directory.
Alternative considered: reuse `LlamaSupervisor` for a second process type. Rejected because the supervisor semantics, logs, and stop behavior are specific to `llama-server`; reusing it would create accidental coupling and misleading UI expectations.

3. **Use detached, best-effort host launch semantics.** The backend should treat successful process creation as “launch started” and return the chosen folder and any immediate spawn errors. It should not promise that `pi` stayed alive after startup.
Alternative considered: full process tracking. Rejected for this change because the user asked for a launch option, not a second supervised runtime.

4. **Resolve the project folder explicitly at launch time.** The endpoint should reject empty, missing, or non-directory paths and should prefer the selected saved folder unless the UI sends an explicit override.
Alternative considered: implicitly derive the folder from model roots or llama bundle path. Rejected because those concepts are unrelated and would produce surprising behavior.

5. **Expose project selection in the existing UI rather than adding a new top-level tab.** The simplest fit is an additional section in Settings or Server where users can manage saved folders and click `Start pi harness`.
Alternative considered: a separate “Projects” tab. Rejected for now because the feature scope is narrow and does not justify another top-level area yet.

## Risks / Trade-offs

- **Detached launch gives limited visibility** → Mitigation: return immediate success/error details and show the folder used in the UI and docs.
- **Users may expect Stop to affect `pi`** → Mitigation: separate labels and help text stating that `pi` launch is independent from the `llama-server` supervisor.
- **PATH or environment differences could cause `pi` launch failures** → Mitigation: surface clear spawn errors and document that `pi` must already be installed and callable on the host.
- **Config growth may invite future tool-launch sprawl** → Mitigation: keep the data model narrow and name the new capability around project tool launchers so later expansion is deliberate.

## Migration Plan

- Add new config fields with empty defaults so existing config files remain valid.
- Ship the UI with no required migration steps; users who do not use `pi` can ignore the new controls.
- If rollout reveals platform-specific launch issues, the feature can be disabled by removing the UI action and backend route without affecting llama.cpp settings or existing supervised flows.

## Open Questions

- Should the UI allow ad hoc launch from a one-off folder path, or only from the saved folder list? Default recommendation: support saved folders first and defer ad hoc launch.
- Should the selected project folder be shown on the Models tab as well, or only near the `pi` action? Default recommendation: only show it near the `pi` workflow in this change.
