# Changelog

All notable changes to `edge-agent-foundation` are documented here.

---

## v0.1.0

### Summary

Initial cookiecutter forked from the Edge Agent craft shape, with:

- Host supervisor Runtime API client stub (no device-root MQTT / Mosquitto)
- Engine-agnostic container runtime stub
- Dual SQLite buffers, reconcile, inventory/command patterns
- Pin guidance for `edge-agent-rules` **v0.2.0**

### Migration guide

- Greenfield Pilot / Edge Agent: prefer this foundation over `edge-agent-triton-foundation`
- Existing Triton+MQTT consumers: remain on `edge-agent-triton-foundation` until peeled
