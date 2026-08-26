# Device alternatives and `--skip-device`

Mocks and evidence for code-only fixes (no lab device). Full flags/pipeline: [../SKILL.md](../SKILL.md).

Steps 3–4, 6, 10–11 are N/A under `--skip-device`. Do not invent lab runs. Mark skipped steps `[-]`.

## Entry gates

| Gate | Required? |
|------|-----------|
| Validated report + one issue | Yes |
| Collection path | Yes |
| Python venv | Yes (tox) |
| Playbook directory | **No** |

---

## Mock / no-device alternatives (preference order)

### 1. Unit fixtures (primary mock)

Supported “mock device” for code-only fixes.

`tests/unit/modules/network/<platform>/test_<module>.py`:

- Mocked running-config fixtures
- `set_module_args` for the want config / state
- Assert expected `commands` (or `changed`)

Read an existing case for the same state/parameter family; update in place.
See [resolution-details.md — Unit cases](resolution-details.md#unit-cases).

### 2. `state: rendered` / `state: parsed`

When the module supports these states, they can validate CLI generation or parse
round-trip **without** `network_cli` to hardware (often localhost / no device
connection). Useful for setval / template checks.

Not a substitute for full `merged` / `replaced` lab proof. Optional supplement
to unit fixtures — not required under `--skip-device`.

### 3. Real lab / sim playbooks (default path)

Default (non-`--skip-device`) path. See [resolution-details.md](resolution-details.md).
