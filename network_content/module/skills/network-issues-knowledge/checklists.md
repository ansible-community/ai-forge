# Analysis Checklists

Module-level checklists for crosswalk, pattern review, and test coverage.

---

## Argspec leaf coverage (every module)

For each argspec leaf path (scalar, struct field, or `*.set` bool):

- [ ] A parser comparison path (`compval` or `name`) matches the leaf or valid parent
- [ ] Parser has `getval` if gather/parse is required; `setval` if configure is required
- [ ] Parser is registered in config class `self.parsers` (or equivalent list)
- [ ] Unit or integration test references the parameter path
- [ ] `EXAMPLES` in `plugins/modules/<prefix><module>.py` uses the same dotted path as the parser

---

## Module EXAMPLES vs argspec checklist (Pattern 11)

`scripts/validate_examples.py` (Step 3) automates items marked **[auto]** below.
Validator confirms or drops its findings; manual walk only for modules it skipped.

- **[auto]** Every parameter path in examples exists in the current argspec at that nesting depth
- **[auto]** Parameter types match argspec (`dict` vs scalar, `list` vs scalar)
- **[auto]** `state` values are valid per argspec `choices`
- **[auto]** Required parameters (`required: true`) present in configure examples
- [ ] Embedded examples in `DOCUMENTATION` block reviewed (not checked by script)
- [ ] Example formatting aligns with `tests/integration/targets/<module>/tests/cli/*.yml` (use `notes` integration ref from findings)

---

## Boolean toggle checklist (Patterns 1–3)

When argspec defines `option.set: bool` (any parent key — not only shutdown/enable):

- [ ] Parser comparison path (`compval` or `name`) is `option.set`, not `option`
- [ ] `getval` captures optional `no` prefix
- [ ] `result` distinguishes True, False, and None/absent
- [ ] `setval` or template engine emits correct negate CLI
- [ ] Parser is registered in config class `self.parsers`
- [ ] Unit test with pre-existing enabled state + `set: false`
- [ ] Integration test asserts negate CLI (`no …`) and idempotent re-run

---

## Type and exclusivity checklist (Patterns 5, 7)

When argspec defines `type`, `choices`, or `mutually_exclusive`:

- [ ] getval capture group types match argspec (`int`, `str`, bool keywords)
- [ ] setval generates the same CLI form the device returns
- [ ] Conflicting suboptions are not independently templated without validation

---

## New argspec option checklist

When argspec adds options recently (check git log if available):

- [ ] Matching rm_template entry exists
- [ ] getval regex matches actual device output format
- [ ] rendered/gathered/parsed integration tests cover the option
- [ ] Module EXAMPLES block matches working parser paths

---

## Compound CLI checklist (Patterns 5, 6, 10)

When argspec models a dict under a knob that maps to a **compound device CLI**
(e.g. `preempt delay minimum … reload … sync …`, `forwarding-threshold lower … upper …`):

- [ ] Cisco documentation consulted for whether sub-keys are independently negatable
- [ ] setval builds CLI only from sub-keys actually present (no hardcoded leading keywords)
- [ ] Optional sub-keys do not emit `None` or placeholder tokens in generated CLI
- [ ] Parent CLI keywords guarded when only a subset of sub-keys is set
- [ ] `replaced`/`overridden` removes sub-keys present in `have` but absent in `want`
- [ ] Config class has per-sub-key compare or custom `_complex_compare` if needed
- [ ] Integration test covers partial sub-key replace with `changed: true` and expected `no …` commands

---

## Test coverage checklist (Pattern 9)

For modules with confirmed or suspected gaps:

- [ ] Unit tests exercise `set: false` / negate paths for high-risk leaves
- [ ] Integration tests assert `changed: false` on idempotent re-run
- [ ] Integration tests assert negate CLI (`no …`) where applicable
- [ ] Each boolean `.set`, new scalar, or list merge key has test references

Grep commands for test discovery live in
[network-issues-scanner/reference/workflow-details.md](../network-issues-scanner/reference/workflow-details.md).
