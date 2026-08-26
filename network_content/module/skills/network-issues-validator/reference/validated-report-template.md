# Validated Gap Report Template

Use this format for validator Step 5 output. Save as `network-issues-report.md`
in the working directory.

```markdown
# Network Issues Report (Validated)

**Validation date:** YYYY-MM-DD
**Scanner hits reviewed:** N
**Confirmed gaps:** X
**Dropped (false positive / fixed):** Y

## Validation Summary

| Metric | Count |
|--------|-------|
| Scanner hits in | N |
| Confirmed | X |
| Dropped | Y |
| Downgraded | Z |

## Confirmed gaps

| Repo | Module | Parameter | File:Line | Pattern | Issue | Potential Fix |
|------|--------|-----------|-----------|---------|-------|---------------|
| cisco.iosxr | iosxr_bgp_global | max_metric.router_lsa.on_startup.wait_for_bgp | plugins/.../argspec/bgp_global.py:412 | 4 | Argspec documents option but no parser comparison path covers it — silent no-op on configure | Add parser with name/compval covering leaf; register in config |
| cisco.ios | ios_interfaces | interfaces[].enable.set | plugins/.../rm_templates/interfaces.py:88 | 1 | Parser compares at `enable` not `enable.set`; `set: false` may not emit `no enable` | Set comparison path to `enable.set`; conditional setval; negate getval |

## Dropped hits

| Repo | Module | Parameter | Scanner confidence | Drop reason | Notes |
|------|--------|-----------|-------------------|-------------|-------|
| cisco.nxos | nxos_ospf_interfaces | ... | candidate | mechanical-false-positive | Parent parser intentionally covers struct |

## Downgraded hits

| Repo | Module | Parameter | Original pattern | New finding | Notes |
|------|--------|-----------|------------------|-------------|-------|
| ... | ... | ... | 1 | 9 | Code correct; missing integration test for `set: false` |
```

## Column rules (confirmed gaps)

- **Repo** — collection name (`cisco.iosxr`)
- **Module** — full module name (`iosxr_bgp_global`)
- **Parameter** — dotted argspec path
- **File:Line** — repo-relative path with line number (primary evidence)
- **Pattern** — [patterns.md](../network-issues-knowledge/patterns.md) pattern number
- **Issue** — verified description and user-visible symptom
- **Potential Fix** — brief direction (not a full implementation)

## Sort order

Sort confirmed gaps by severity (high first), then repo, then module.

## JSON shape

```json
{
  "validation_date": "YYYY-MM-DD",
  "summary": {
    "scanner_hits_in": 0,
    "confirmed": 0,
    "dropped": 0,
    "downgraded": 0
  },
  "confirmed": [],
  "dropped": [],
  "downgraded": []
}
```
