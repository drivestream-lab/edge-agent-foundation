# Verify (local integration stubs)

Manual / semi-automated checks after `make setup`.

1. **Host supervisor stub** — client records publishes with `HOST_SUPERVISOR_ENABLED=true`
2. **Dual buffers** — write/read metrics + capture lanes
3. **Reconcile** — bootstrap with empty desired state is a no-op milestone
