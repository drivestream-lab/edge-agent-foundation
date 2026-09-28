# Tests

| Directory | Purpose |
|-----------|---------|
| `unit/` | Fast pytest suite with mocks — run via `make test` |
| `_helpers/` | Shared fixtures (not collected) — e.g. `signal_map_fixtures.py` |
| `verify/` | Live compose verification flows (Mosquitto + agent) |
| `device/` | On-hardware tests (target device) — documented stub |

Day-one CI runs `tests/unit/` only.

## Feature map

| Capability | Pytest | Live / Docker |
|------------|--------|---------------|
| INIT-SIGNAL-MAP-001 bootstrap inventory index + Autrio dispatch | `test_signal_map_dispatch.py`, `test_inventory_http_client.py` | **Deferred** — human Docker after Setu `enriched_detailed` + Pravah Edge pack (see as-built W3/W4) |
| Buffers / settings / OTA models | existing `test_*.py` | compose flows in `verify/` (TODO) |

### INIT-SIGNAL-MAP-001 live handoff

W1 is fixture/mock-only (no live host supervisor or IS required for `make test`).

For closed-loop (human):

```bash
# After Setu + Pravah + local IS containers are up
cp .env.example .env
make setup
docker compose -f docker/docker-compose.yml up -d
# Agent consumes Setu bootstrap configuration, indexes inventory,
# subscribes edge_command, publishes edge_command_response.
```

Assert: multi-IS route by `(service_name, endpoint_name)`; GET query / POST body; uplink `acked|executed|failed`; reject non-`autrio.command.v1`.
