## 1. Config and backend launch support

- [x] 1.1 Extend the persisted app config with saved project folder paths and a selected project folder default that preserves compatibility with existing config files
- [x] 1.2 Add backend validation for project-folder launch requests so empty, missing, and non-directory paths return clear errors
- [x] 1.3 Implement a dedicated API route that launches `pi` with the selected project folder as `cwd` and returns immediate success or startup failure details

## 2. Frontend project-folder workflow

- [x] 2.1 Add UI controls to enter, persist, and select project folders within the existing panel layout
- [x] 2.2 Add a clearly labeled `Start pi harness` action near the selected project folder summary
- [x] 2.3 Show inline success and error feedback for `pi` launch attempts without conflating that status with the `llama-server` supervisor state

## 3. Documentation and verification

- [x] 3.1 Update `README.md` and `docs/panel-user-guide.md` to describe project-folder setup and the requirement that `pi` and `pi-llama-cpp` are already installed
- [x] 3.2 Add backend tests for config compatibility and `pi` launch validation/error handling
- [x] 3.3 Perform a manual smoke test covering project-folder save/select behavior and a successful `pi` launch from a real project directory
