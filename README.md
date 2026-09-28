# edge-agent-foundation

**Cookiecutter chassis for Edge Agent workload services** — day-one-green Python
agent shape with `business_services` / `infra_services`, dual SQLite buffers,
desired-state reconcile, engine-runtime stub, and a **host supervisor client**
(Runtime API seam). Device-root MQTT stays with the host supervisor.

| | |
|---|---|
| **Template engine** | Cookiecutter |
| **Version** | see [`VERSION`](VERSION) (currently **0.1.0**) · [CHANGELOG](CHANGELOG.md) |
| **License** | [MIT](LICENSE) |
| **Constitution** | Pin **`edge-agent-rules`** @ **v0.2.0** at `.cursor/rules` |
| **Stack** | Python 3.11+ · Pydantic v2 · Injector DI · Loguru · SQLite buffers · Docker (optional) |

## What the chassis guarantees

1. **Shape** — layered `src/` with `business_services/` above `infra_services/`
2. **Constitution alignment** — consumers mount `edge-agent-rules`
3. **Job boundary** — agent delivers, observes, and reports; it never switches models inside the engine
4. **Real dual buffers** — SQLite WAL metrics lane plus durable capture queue
5. **Host supervisor seam** — `HostSupervisorClientService` stub (no device-root MQTT)
6. **Engine-agnostic** — `EngineRuntimeService` controls a configured container; image family is a product ADR
7. **Day-one-green CI** — `make check` / `make test` pass with `FakeHardwareProfile`

## Options

| Option | Meaning |
|--------|---------|
| `agent_name` | Package identity, container name |
| `agent_description` | Human-readable description |

## Usage

```bash
pip install cookiecutter
cookiecutter gh:drivestream-lab/edge-agent-foundation
# or local:
cookiecutter /path/to/edge-agent-foundation

cd <agent-name>
cp .env.example .env
make setup
make check && make test
python -m src.main
```

## Mounting edge-agent-rules

```bash
rm -rf .cursor/rules
git submodule add https://github.com/drivestream-lab/edge-agent-rules.git .cursor/rules
cd .cursor/rules && git checkout v0.2.0 && cd ../..
```

## Related

| Repo | Role |
|------|------|
| [`edge-agent-rules`](https://github.com/drivestream-lab/edge-agent-rules) | Constitution |
| [`edge-agent-triton-foundation`](https://github.com/drivestream-lab/edge-agent-triton-foundation) | Legacy Triton+MQTT defaults (kept for existing consumers) |
| [`rust-device-foundation`](https://github.com/drivestream-lab/rust-device-foundation) | Host supervisor / device daemon chassis |

## License

MIT — see [LICENSE](LICENSE).
