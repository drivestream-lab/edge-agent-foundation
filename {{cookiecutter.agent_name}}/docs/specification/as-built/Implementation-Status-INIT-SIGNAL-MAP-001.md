# As-built — INIT-SIGNAL-MAP-001 (edge-agent)

**Initiative:** Edge Signal Map — EA join + Autrio dispatch  
**Branch:** `chore/INIT-SIGNAL-MAP`  
**Status:** W1 mock complete (unit + fixtures); live Setu/Pravah + human Docker deferred

## Wave table

| Wave | Status | Capability | Unit | Live / Docker |
|------|--------|------------|------|---------------|
| W0 | done | Product INIT + as-built | — | — |
| W1 | done | Bootstrap index + observe stub + Autrio HTTP dispatch (mocks) | `tests/unit/test_signal_map_dispatch.py`, `tests/unit/test_inventory_http_client.py` | — |
| W3 | pending | Live Setu bootstrap + Pravah MQTT downlink/uplink | pending | human |
| W4 | pending | Closed-loop multi-IS regression | — | human Docker |

## Verification matrix (W1)

| REQ | Capability | Evidence |
|-----|------------|----------|
| REQ-01 | Index by `(service_name, endpoint_name)` | `BootstrapInventoryService.load_configuration` + unit |
| REQ-02 | Observe schedule stub from inventory | `schedule_observe_endpoints` + unit |
| REQ-03 / D12 | Reject non-`autrio.command.v1` | `CommandDispatchService.parse_downlink` + unit |
| REQ-04 | Lookup + HTTP with catalog `http_method` | `CommandDispatchService.dispatch` + unit |
| REQ-05 / D8 | GET→query; POST→JSON body | `InventoryHttpClientService.request` + unit |
| REQ-06 / D11 | Uplink `acked` \| `executed` \| `failed` | dispatch returns ordered envelopes + unit |
| REQ-07 | No URL from Autrio pack | pack payload model forbids host/path/method; URL from inventory only |

## Live Docker handoff (W3/W4 — human)

Not run in this wave. When Setu/Pravah stacks are available:

1. Bootstrap device via Setu (`enriched_detailed` inventory in `configuration`).
2. Confirm EA indexes services and schedules observe endpoints.
3. Publish Autrio `autrio.command.v1` on `edge_command` with Edge pack `service_name` / `endpoint_name` / `parameters`.
4. Assert local IS HTTP and uplink `autrio.command_response.v1` statuses.
5. Assert non-Autrio identities are rejected (no stratum path).

See `tests/README.md` and `tests/verify/README.md`.
