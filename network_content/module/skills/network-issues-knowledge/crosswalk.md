# Argspec vs Template Crosswalk

Procedure for matching argspec leaves to parser comparison paths and config
registration. Finds the **most** real gaps across all modules.

Run exhaustively for every resource module — do not skip modules after finding
toggle issues. See [parser-anatomy.md](parser-anatomy.md) for comparison path rules.

---

## Per-module crosswalk

For each resource module:

### 1. Parse argspec tree

Read `argspec/{module}/{module}.py` (or nested files). Extract every leaf
parameter path (e.g. `neighbors.shutdown.set`,
`max_metric.router_lsa.on_startup.wait_for_bgp`).

Record `type`, `choices`, `default`, and whether the leaf is a boolean `.set`
suboption.

### 2. Extract parser comparison paths

From `rm_templates/{module}.py`, for each parser entry collect:

- `"name": "..."` (always)
- `"compval": "..."` (when present — overrides name for diff)
- Effective comparison path = `compval` or `name`
- Presence of `getval`, `setval`, `result`

### 3. Cross-reference config registration

Read `config/{module}/{module}.py` and note which parser lists are passed to
`compare()`. A parser not registered here never participates in command generation
even if defined in rm_templates.

Also note custom methods that handle parameters outside rm_templates.

### 4. Diff

| Mismatch | Pattern / label |
|----------|-----------------|
| Argspec leaf with no parser comparison path covering it | Pattern 4 — coverage gap |
| Argspec has `parent.set` (bool) but comparison path is `parent` only | Pattern 1 — boolean-set mismatch |
| Comparison path exists but argspec leaf absent | Pattern 8 — stale parser |
| Parser has `getval`/`result` but no `setval` and state requires generate | generate gap |
| Dict-valued compound CLI compared/rendered as monolithic scalar | Pattern 10 — hardcoded compound CLI |
| EXAMPLES parameter path absent from argspec or wrong type/nesting | Pattern 11 — stale EXAMPLES (from Step 3 `validate_examples.py`; do not re-walk here) |

### 5. Check module EXAMPLES

Pattern 11 structural checks run in scanner Step 3 (`validate_examples.py`). **Do not**
repeat that walk here except for:

- Embedded examples inside `DOCUMENTATION` (not covered by the script)
- Modules the script skipped (YAML parse failure) — manual walk per [patterns.md](patterns.md) Pattern 11

For those cases, map parameter paths to argspec leaves and cross-check integration test
task vars when unsure.

### 6. Check types

For each shared path, compare argspec `type`/`choices` against what getval
captures and setval generates (Pattern 5).

**Do not** flag absent `compval` as a gap. Flag missing or misaligned parser
`name`/`compval` relative to argspec.

Document file paths and line numbers for every mismatch.

---

## Scalar and struct parsers (name-only, no compval)

When a module has zero or few `compval` entries, that is **normal**:

- Match argspec leaves to parser `name` (dot paths like `bgp.cluster_id`)
- Verify `getval`/`setval`/`result` round-trip the scalar or struct
- Flag leaves with no matching parser name — common coverage gap
- Do not require adding `compval` unless comparison granularity is wrong

---

## Cross-collection sweep

After scanning one collection, note **pattern families** that likely repeat elsewhere:

- Argspec leaves without template coverage (new options often land in argspec first)
- Boolean `.set` comparison at parent instead of `parent.set`
- `mutually_exclusive` groups with independent parsers
- getval without optional `no` on negate-capable CLI
- Dict sub-keys under compound CLI knobs (`preempt delay`, `forwarding-threshold`) modeled as monolithic parsers
- `EXAMPLES` in `plugins/modules/` not updated after argspec renames or type changes (Pattern 11)

Apply the same crosswalk to sibling collections — do not limit the sweep to
shutdown/enable keywords.
