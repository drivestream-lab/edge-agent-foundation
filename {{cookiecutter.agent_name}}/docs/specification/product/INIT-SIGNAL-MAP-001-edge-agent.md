# INIT-SIGNAL-MAP-001 — spec slice for edge-agent

| Field | Value |
|-------|-------|
| Initiative | `INIT-SIGNAL-MAP-001` |
| PRD | `drivestream-meta/prd/INIT-SIGNAL-MAP-001.md` |
| Impact map | `drivestream-meta/prd/reports/Impact-Map-INIT-SIGNAL-MAP-001.md` |
| Repo | `drivestream-lab/edge-agent-foundation` (generated agent) |
| Branch | `chore/INIT-SIGNAL-MAP` |
| Date | 2026-09-21 |
| Status | W1 mock — unit fixtures; live Docker deferred |

## Overview

Edge Agent consumes Setu bootstrap inventory as a local HTTP **signal map** and executes Autrio
`autrio.command.v1` by looking up `(service_name, endpoint_name)`, then calling
`base_url + path` with the catalog `http_method` and D8 parameter binding. Uplink uses
`autrio.command_response.v1` only. Non-Autrio identities are rejected (D12).

## Functional requirements

| ID | Requirement | PRD |
|----|-------------|-----|
| REQ-01 | Index bootstrap `configuration.services` by `(service_name, endpoint_name)` | D2 |
| REQ-02 | Schedule observe endpoints from inventory (`interval_seconds`); never from RO offers | D5 |
| REQ-03 | On Autrio downlink: validate `identity=autrio.command.v1`; else reject | D12 |
| REQ-04 | Resolve pack `service_name` + `endpoint_name` against inventory; HTTP with `http_method` | D1, D6, D9 |
| REQ-05 | GET → query params; POST/PUT/PATCH → JSON body from `parameters` | D8 |
| REQ-06 | Uplink `acked` \| `executed` \| `failed` only; same `correlation_id` | D11 |
| REQ-07 | Do not invent host/URL from Autrio pack | D9 |

## Non-goals

- Catalog authorship (ops/abhilekh)
- Accepting stratum / non-Autrio command identities
- Automotive packs

## Delivery

| Wave | Scope |
|------|-------|
| W1 | Mock fixtures implementing REQ-01–07 |
| W3 | Live Setu + Pravah |
| W4 | Human Docker closed-loop |
