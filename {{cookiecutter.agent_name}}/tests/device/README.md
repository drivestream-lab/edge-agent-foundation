# Device tests

On-hardware verification for target devices. Not run in CI.

## Prerequisites

- Target device with Docker (if exercising engine runtime)
- Host supervisor / Runtime API endpoint reachable via local IPC

## Suggested checks

1. **Buffers** — metrics + capture WAL survive process restart
2. **Engine lifecycle** — start/stop inference container via `EngineRuntimeService`
3. **Host supervisor** — publish + desired fetch against a real supervisor stub
