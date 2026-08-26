# Verification Procedure

Per-hit review applied before assigning a final verdict. Pattern-specific
confirm/drop bars are in [patterns.md](patterns.md).

---

## Per-hit review

For hit `{repo, module, parameter, file, line, pattern, issue}`:

### Argspec ground truth

Read the argspec leaf at the cited path (or parent struct). Record `type`,
`choices`, `default`, whether it is a boolean `.set` suboption, and whether
docs/comment say gather-only, config-only, or deprecated.

### Parser inventory

From `rm_templates/{module}.py`, list every parser entry with effective comparison
path, `getval`/`setval`/`result` presence, and negate capture where relevant.

Check whether **any** parser path covers the argspec leaf or a valid parent.
For `*.set` booleans, parent-level comparison is usually wrong.

For dict-valued compound CLI (Pattern 10), check whether setval builds commands
conditionally from each sub-key or treats the dict as a single scalar.

### Config registration

Read `config/{module}/{module}.py`:

- Parser lists passed to `compare()` / command generation
- Custom methods handling the parameter without a template parser
- `set: false` or negate handled in Python outside rm_templates
- Per-sub-key compare logic for `replaced`/`overridden` on compound CLI dicts

### Sibling and negate parsers

Search the same rm_template for mitigating parsers. See [parser-anatomy.md](parser-anatomy.md).

### Test cross-check

```bash
rg -n '<parameter_or_parent>' tests/unit/modules/network/<platform>/test_<module>.py
rg -n '<parameter_or_parent>' tests/integration/targets/<module>/
```

Absence of tests does not drop a code gap — it adds a test-coverage note.
Presence of `set: false` / negate tests may indicate fix or false positive; re-read
parser paths before dropping.

For Pattern 10, look for `state: replaced` / `overridden` tests with partial
sub-key sets in `want` while `have` retains extra sub-keys.

For Pattern 11, scanner Step 3 already ran `validate_examples.py` which performs
structural checks (type mismatches, removed parameters, invalid state, missing
required) and attaches an integration testcase reference per finding. Validator
task: confirm or drop each finding by reading the cited `file:line` in the
module's EXAMPLES and the `notes` integration ref. Manual EXAMPLES walk is only
needed for modules `validate_examples.py` skipped (YAML parse failure).
Integration tests are the preferred reference for valid structure — absence of a
test does not drop a documentation gap.

### Apply pattern confirm/drop bars

See [patterns.md](patterns.md) for the flagged pattern number. For Patterns 5, 6,
and 10, cross-check device CLI semantics against
[Cisco IOS/NX-OS documentation](https://www.cisco.com/c/en/us/support/ios-nx-os-software/index.html)
before confirming or dropping.

### Assign verdict

| Verdict | Action |
|---------|--------|
| `confirmed` | Keep in final report; cite verification evidence |
| `dropped` | Exclude from final report; record drop reason |
| `downgraded` | Keep only if reclassified issue remains (e.g. Pattern 9 test gap only) |

Process high-confidence hits first, then `likely`, then `candidate`. Do not skip
`candidate` hits — that is where most false positives are filtered.

**When uncertain after deep review:** drop with reason `insufficient-evidence` rather
than reporting a speculative gap.

---

## Drop reason codes

| Reason code | When to use |
|-------------|-------------|
| `comparison-path-ok` | Effective parser path matches argspec leaf |
| `sibling-parser` | Another parser covers the leaf or negate form |
| `config-class-handles` | Config Python handles generate/negate without template |
| `intentional-design` | Documented gather-only / config-only / deprecated |
| `negate-capture-present` | getval already captures `no` prefix |
| `mechanical-false-positive` | Heuristic disproven by full parser read |
| `already-fixed` | Code no longer matches hit description |
| `cli-semantics-verified` | Cisco docs confirm current parser matches device negate/generate behavior |
| `insufficient-evidence` | Cannot demonstrate gap after deep review |
| `examples-aligned` | EXAMPLES match current argspec; formatting-only differences |

---

## Global confirm / drop rules

**Drop when:**

- Parser comparison path (`compval` or `name`) correctly matches the argspec leaf
- Separate negate parser handles the `no …` form for the same logical option
- Config class generates or reconciles the path outside rm_templates (verify in code)
- Parameter is documented as gather-only or config-only with no setval expectation
- getval regex includes negate capture when Pattern 2 was flagged mechanically
- Issue was fixed in source since discovery (re-read shows correct path/setval)
- Cisco documentation confirms compound CLI is atomic (not per-sub-key negatable)

**Confirm when:**

- Argspec leaf has no parser comparison path and config does not handle it
- Boolean `.set` compares at parent; `set: false` cannot emit negate CLI
- Type/choices mismatch between argspec and getval/setval
- Parser defined in rm_templates but not registered in config class
- Idempotency or round-trip failure is demonstrable from code structure
- Hardcoded setval emits fixed keywords or `None` placeholders for optional sub-keys
- `replaced`/`overridden` leaves unwanted compound-CLI sub-keys on device (Pattern 10)
- EXAMPLES reference removed/renamed argspec paths or types that fail validation (Pattern 11)

---

## Dropped hits table format

```markdown
## Dropped hits

| Repo | Module | Parameter | Scanner confidence | Drop reason | Notes |
|------|--------|-----------|-------------------|-------------|-------|
| cisco.ios | ios_vlan | vlan.configuration | candidate | comparison-path-ok | Parser `vlan.configuration` matches leaf |
```
