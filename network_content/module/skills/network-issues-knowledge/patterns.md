# Gap Patterns

Catalog of parser and rm_template issue types. Each pattern includes symptom,
root cause, detection signals, validation confirm/drop bars, and potential fix.

**Read this entire catalog during discovery and validation.** Do not anchor on a
single gap family.

---

## Gap families at a glance

| Family | Patterns | Typical symptom |
|--------|----------|-----------------|
| **Coverage** | 4, 8, generate gaps | Documented option accepted but never parsed or generated |
| **Comparison granularity** | 1 | `set: false` or disable transitions not detected |
| **Negate / CLI symmetry** | 2, 3 | `no …` not parsed or not generated |
| **Type / schema alignment** | 5, 7, 10 | Wrong type, wrong keyword, hardcoded compound CLI |
| **Round-trip / idempotency** | 6, 10 | Second run reports `changed: true`; `replaced` leaves stale sub-keys |
| **Test hygiene** | 9 | Failure mode never exercised in CI |
| **Documentation** | 11 | EXAMPLES in module file use stale parameter names or structure |

---

## Pattern 1 — Boolean `.set` comparison-path mismatch

**Symptom:** Argspec documents `parameter.set: true|false` but the parser
compares at `parameter` (parent dict) instead of `parameter.set`.

**Cause:** RMEngineBase diff runs at the wrong granularity. It cannot detect a
`True → False` transition, so `set: false` does not emit the negate CLI (`no …`).

**Applies to:** Any `*.set` boolean suboption — `shutdown`, `enable`, `passive`,
`logging`, `bfd`, etc. Shutdown is a frequent instance, not the only one.

**Detection signals:**

- Argspec has a dict suboption with only `set:` (bool) under a parent key
- Parser comparison path (compval or name) resolves to the parent key, not `parent.set`
- `result` expression sets `"set": "{{ True if X is defined }}"` with no False branch

**Validation confirm:** argspec has `parent.set: bool` and no parser compares at
`parent.set` (via `compval` or dot-namespaced `name`), and config does not handle
disable transitions elsewhere.

**Validation drop:** comparison path is `parent.set` or child namespace parser covers it.

**Examples:**

- [cisco.iosxr PR #623](https://github.com/ansible-collections/cisco.iosxr/pull/623) —
  `neighbors.shutdown.set` vs parser comparing at `shutdown`
- Same class on `enable.set`, `passive.set`, or any toggle dict in interface/BGP/OSPF modules

**Potential fix:** Set comparison path to `parameter.set` (via `compval` or
dot-namespaced `name`), update `getval` to capture `no`, and branch
`result`/`setval` for True, False, None.

---

## Pattern 2 — Missing negate capture in getval regex

**Symptom:** Device CLI supports `no <command>` but the template `getval` regex
does not include a `(?P<negate>\sno)?` group before the command keyword.

**Cause:** Parsed running config always reports the feature as present (enabled)
even when the device shows `no …`. Idempotency and state reconciliation fail.

**Detection signals:**

- Argspec or docs mention enable/disable, `set: false`, or negate semantics
- `getval` regex matches the affirmative command only
- No `negate` or `no` capture group in the regex

**Validation confirm:** device CLI supports `no …`, argspec implies disable semantics,
and no parser getval for that command captures optional `no`.

**Validation drop:** negate group exists, or a sibling parser parses the `no` form.
Drop reason: `negate-capture-present` or `sibling-parser`.

**Examples:**

- PR #623 — `getval` matched `shutdown` but not `no shutdown`
- Incomplete `logging` / `snmp-server` / `feature` toggles where device uses `no feature …`

**Potential fix:** Add optional negate group to `getval`; branch `result` on it.

---

## Pattern 3 — Static setval for toggle parameters

**Symptom:** Template `setval` is a fixed CLI string with no Jinja conditional
for the disabled/negated state.

**Cause:** When desired state is off/false, the module still emits the affirmative command.

**Detection signals:**

- `setval` is a plain string, not a Jinja expression
- Argspec parameter is boolean or has `set:` suboption
- No companion template entry for the negate case

**Validation confirm:** `set: false` or disable cannot emit `no …` from setval/template
engine and config does not generate it.

**Validation drop:** conditional setval, template engine negate, or config method emits CLI.

**Examples:**

- Static `"shutdown"` or `"enable"` setvals (common but not exclusive)
- Fixed `"passive"` / `"bfd"` / feature keyword strings without `no` branch
- [cisco.nxos PR #1075](https://github.com/ansible-collections/cisco.nxos/pull/1075) —
  `preempt` setval unconditionally emitted `preempt delay minimum …` even when
  `minimum` was absent, producing malformed CLI like `preempt delay minimum None reload 50`
- Same PR — `priority` setval emitted `forwarding-threshold lower … upper …` without
  the `forwarding-threshold` keyword when only `upper` was set

**Potential fix:** Use conditional Jinja in `setval` or rely on compval + negate-aware result.

---

## Pattern 4 — Argspec/template coverage gap

**Symptom:** Parameter appears in argspec and module documentation but has no
parser that covers it (no matching parser `name` or `compval` path, and no parser
whose `getval`/`result` populates that argspec leaf).

**Cause:** Module accepts the parameter at validation time but never generates or
parses the CLI — silent no-op or wrong `changed` result.

**Detection signals:**

- Walk argspec nested keys; match each leaf to a parser comparison path
- Check config class `self.parsers` lists — parser must be registered to participate
- Recently added argspec options without template additions
- Parser has `getval` but no `setval` when generate path is required

**Validation confirm:** leaf has no parser comparison path **and** module is expected
to parse/generate it per argspec/docs **and** config does not handle it.

**Validation drop:** parent parser intentionally covers struct children, or option is
gather-only with no setval expectation documented. Drop reason: `intentional-design`.

**Examples:**

- [cisco.iosxr PR #615](https://github.com/ansible-collections/cisco.iosxr/pull/615) —
  `max-metric router-lsa` suboptions incomplete in templates
- New scalar options added to argspec without rm_template entries
- Parser defined in rm_templates but missing from config `self.parsers`

**Potential fix:** Add template entries with correct getval/setval/compval/result;
register parsers in config class.

---

## Pattern 5 — Argspec type vs CLI semantics mismatch

**Symptom:** Argspec declares a type that does not match device CLI behavior.

**Cause:** Users pass values the parser cannot round-trip; merged state generates wrong commands.

**Detection signals:**

- Compare argspec `type`/`choices` against template getval capture groups
- Renamed/deprecated parameters still in argspec
- Docs describe mutual exclusivity not enforced in templates
- Integer argspec for a keyword-only CLI (or vice versa)

**Validation confirm:** mismatch is demonstrable between argspec type/choices and
what getval captures or setval generates.

**Validation drop:** types align on inspection; drop reason: `comparison-path-ok` or
`mechanical-false-positive`.

**Examples:**

- PR #615 — `wait_for_bgp_asn` (int) corrected to `wait_for_bgp` (bool) for IOS-XR
- `max_metric_value` (int) vs `set` (bool) representing the same CLI knob
- PR #1075 — hardcoded `preempt delay` setval structure not aligned with NX-OS
  compound CLI semantics (see Pattern 10)

**Documentation reference:** Consult
[Cisco IOS/NX-OS documentation](https://www.cisco.com/c/en/us/support/ios-nx-os-software/index.html)
to verify CLI keyword order, optional sub-keys, and per-sub-key negate forms before
confirming or fixing.

**Potential fix:** Align argspec type/choices with CLI; update getval/setval accordingly.

---

## Pattern 6 — Idempotency gap for merged/replaced/overridden

**Symptom:** First application works but re-running with the same desired state
reports `changed: true` or emits spurious commands.

**Cause:** Parsed state from device does not match normalized desired state — often
Patterns 1–3 combined, or value normalization (string vs int, list ordering).

**Detection signals:**

- Unit tests only cover initial merge, not second-run idempotency
- Integration tests lack `changed: false` after converge step
- Template `result` maps device output to different structure than argspec expects

**Validation confirm:** code structure shows second-run `changed: true` risk; cite
specific result/setval asymmetry.

**Validation drop:** parse/generate symmetry is demonstrably correct.

**Examples:**

- PR #615 — max-metric idempotency fixed across merged, replaced, overridden
- List-of-dict parsers where key order or optional fields differ between parse and want
- PR #1075 — `state: replaced` with only `preempt.sync` in want left `preempt.reload`
  on device because the whole `preempt` dict compared as a monolithic value →
  `changed: false`, `commands: []` (see Pattern 10)

**Potential fix:** Fix parse/generate symmetry; add idempotent re-run tests.

---

## Pattern 7 — Missing mutual exclusivity in parser layer

**Symptom:** Argspec documents mutually exclusive suboptions but templates allow
both to be set independently.

**Cause:** Module sends conflicting CLI; device may reject or apply unpredictably.

**Detection signals:**

- Argspec has `mutually_exclusive` or description notes exclusivity
- Templates use independent compval paths with no conflict handling
- No validation in config class before template rendering

**Validation confirm:** mismatch is demonstrable; conflicting suboptions independently templated.

**Validation drop:** config class enforces exclusivity before rendering.

**Examples:**

- PR #615 — `max_metric_value` vs `set`, `wait_for_bgp` vs `wait_period`

**Potential fix:** Enforce in argspec + config validation; single template with branches.

---

## Pattern 8 — Stale or dead config/parser code

**Symptom:** Helper functions or template entries reference removed argspec paths;
copy-paste artifacts from other modules.

**Cause:** Misleading code paths; subtle wrong key building in list/dict conversion.

**Detection signals:**

- Config functions referencing argspec keys that no longer exist
- Parser comparison paths not found in current argspec tree
- Parser names from a different module copied into rm_templates

**Validation confirm:** parser path has no argspec counterpart **and** it causes
user-visible wrong behavior (not merely dead code).

**Validation drop:** stale entry is harmless unused template noise with no registration.

**Examples:**

- PR #623 — stale `_build_key` in `bgp_global.py` config removed

**Potential fix:** Remove dead code; align config normalization with current argspec.

---

## Pattern 9 — Test coverage blind spots

**Symptom:** Toggle, negate CLI, coverage, or idempotent re-run scenarios untested.

**Cause:** Gaps reach production because CI never exercises the failure mode.

**Detection signals:**

- Compare argspec leaf paths against unit test task vars and integration playbooks
- Search for `set: false`, negate CLI strings, second-run idempotency
- Integration tests assert commands but not `changed: false` on re-apply

**Validation confirm:** code path appears correct but no unit/integration test
exercises disable, negate, or the specific leaf. Verdict: `downgraded` if code is fine.

**Validation drop:** tests exist and code path is correct — not a code gap.

**Potential fix:** Add unit test with mocked running config + integration idempotency task
for each high-risk parameter class (toggles, new scalars, list merges).

---

## Pattern 10 — Hardcoded compound CLI parser

**Symptom:** A dict-valued argspec option maps to a **compound device CLI command**
(one line with multiple sub-keys), but the parser/setval treats it as a monolithic
scalar — like `group_name` or `mac_address` — with hardcoded keyword order and no
per-sub-key handling for negate or `replaced`/`overridden`.

**Cause:** Device CLI allows independent sub-key configuration and removal
(e.g. `no preempt delay reload 20` while keeping `preempt delay sync 55`), but the
module compares or generates the entire dict as one unit. Partial `want` matches
present sub-keys in `have`, so no commands emit and stale sub-keys remain. Hardcoded
setval may also emit leading keywords or `None` for absent optional sub-keys.

**Applies to:** HSRP `preempt delay`, `priority forwarding-threshold`, timer
compounds, multi-field feature commands, and similar NX-OS/IOS-XR knob structures
where Cisco docs show per-field negate semantics.

**Detection signals:**

- Argspec defines a dict with multiple sub-keys under one parent CLI knob
- setval uses fixed keyword order (e.g. always starts with `minimum`) regardless of which sub-keys are set
- setval references sub-keys without `is defined` guards — risk of `None` in CLI
- Config compares parent dict as scalar via standard `compare()` with no per-sub-key logic
- No integration test for `state: replaced`/`overridden` with partial sub-key set in `want`
- `complex_parsers` or similar lists treat dict and scalar parsers identically

**Validation confirm:** Cisco documentation shows sub-keys are independently
configurable/removable; code compares or renders the dict monolithically; `replaced`
with subset `want` demonstrably fails to remove extra `have` sub-keys or emits
malformed CLI. Cross-reference Patterns 3, 5, and 6 — this pattern often presents
as a combination.

**Validation drop:** Cisco docs confirm the CLI is truly atomic (all sub-keys must
be set/cleared together) and current parser matches that semantics. Drop reason:
`cli-semantics-verified`.

**Examples:**

- [cisco.nxos PR #1075](https://github.com/ansible-collections/cisco.nxos/pull/1075) —
  `nxos_hsrp_interfaces` `preempt` and `priority` handling:
  - NX-OS: `preempt delay minimum <N> reload <N> sync <N>` — each sub-key removable
    via `no preempt delay <sub-key> <value>`
  - Before fix: `state: replaced` with only `sync: 55` in want → `changed: false`,
    `reload: 20` left on device
  - Before fix: setval emitted `preempt delay minimum None reload 50` when `minimum` absent
  - Fix: split `complex_scalar_parsers` vs `complex_dict_parsers`, added
    `_complex_compare` for per-sub-key `no` commands, conditional setval per sub-key

**Documentation reference:** **Required** before confirming — consult
[Cisco IOS/NX-OS documentation](https://www.cisco.com/c/en/us/support/ios-nx-os-software/index.html)
(or platform-specific command reference) for compound command structure, optional
sub-key order, and whether `no <sub-key>` forms exist independently.

**Potential fix:** Split scalar vs dict compound parsers; build setval only from
defined sub-keys; guard parent CLI keywords; add config-class per-sub-key compare
for `replaced`/`overridden`; add integration tests for partial replace and negate
per sub-key.

---

## Pattern 11 — Stale or invalid module EXAMPLES

**Symptom:** The `EXAMPLES` block in `plugins/modules/<prefix><module>.py` shows task
vars (parameter names, nesting, types, `state` values, or structure) that no longer
match the current argspec.

**Cause:** Argspec evolved — options added, renamed, removed, or retyped — without
updating module documentation examples. Users copy broken YAML from docs and hit
argument validation errors before any parser logic runs.

**Applies to:** All resource modules. Examples live in the module-level `EXAMPLES`
string in `plugins/modules/<prefix><module>.py`. Some collections also embed examples
inside `DOCUMENTATION`; check both when present.

**Detection signals:**

Run `scripts/validate_examples.py /path/to/collection --json` (Step 3). It performs all checks below mechanically and emits per-task, per-parameter findings with integration testcase references:

- Parameters in EXAMPLES absent from argspec at that nesting depth (removed or renamed)
- Type mismatches: scalar where argspec expects `dict`, dict where argspec expects scalar, scalar where `list` expected
- Invalid `state` values not present in argspec `choices`
- Required parameters (`required: true` in argspec) absent from the task

For modules where `validate_examples.py` skips (YAML parse failure), fall back to manual walk: parse EXAMPLES task vars and compare each parameter path and type against `argspec/{module}/{module}.py`.

Cross-check format against `tests/integration/targets/<module>/tests/cli/*.yml` — integration tests are the preferred reference for valid structure.

**Validation confirm:** EXAMPLES reference removed/renamed argspec paths, wrong types,
invalid `state` values, or structures that would fail `ansible.module_utils` argument
validation. Cite the specific example line and the argspec leaf it contradicts.

**Validation drop:** Examples align with current argspec on inspection; differences are
cosmetic formatting only. Drop reason: `examples-aligned`.

**Examples:**

- Argspec adds `neighbors[].bfd` dict suboptions but EXAMPLES still show flat `bfd: true`
- Renamed `wait_for_bgp_asn` (int) → `wait_for_bgp` (bool) but EXAMPLES use old name/type
- Example uses `state: merged` when argspec `choices` no longer include `merged`
- New required `as_number` added to argspec but EXAMPLES omit it in configure tasks

**Documentation reference:** Use integration test playbooks as the working reference for
parameter paths and YAML structure.

**Potential fix:** Update `EXAMPLES` in `plugins/modules/<prefix><module>.py` to match
current argspec paths, types, and integration test formatting. Reproduce the faulty
example in a playbook to confirm failure, then verify the updated example passes.
Do not change argspec or parser code unless a separate code gap (Patterns 1–10) is also
confirmed. See `network-issues-resolver` for the fix pipeline.
