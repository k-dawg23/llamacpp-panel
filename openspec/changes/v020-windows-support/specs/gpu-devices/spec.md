## ADDED Requirements

### Requirement: NVIDIA enumeration on Microsoft Windows

On hosts running Microsoft Windows, when `nvidia-smi` is available (for example as `nvidia-smi.exe` on the process `PATH`), the GPU discovery implementation SHALL invoke the same non-interactive CSV query used on POSIX and SHALL return devices with the same `gpu:{index}` identifier scheme when the command succeeds.

#### Scenario: Windows 10 or 11 with NVIDIA driver

- **WHEN** the panel runs on Windows 10 or 11 and `nvidia-smi` executes successfully with one or more GPUs
- **THEN** the discovery API SHALL return at least one device per GPU and SHALL indicate the discovery source in the response metadata
