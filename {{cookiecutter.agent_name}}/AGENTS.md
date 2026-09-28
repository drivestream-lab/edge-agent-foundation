# Agent notes — {{ cookiecutter.agent_name }}

- Mount **edge-agent-rules** @ **v0.2.0** under `.cursor/rules`.
- Device-root MQTT lives on the **host supervisor** — use `HostSupervisorClientService`.
- Engine image family is a **product ADR**; keep `EngineRuntimeService` agnostic.
- Day-one gate: `make check && make test`.
