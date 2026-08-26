# Resolution Details

Operational reference for `network-issues-resolver`. The skill defines the pipeline;
this file holds commands, paths, and conventions.

**Modes:** `--skip-device` and `--dry-run` are defined in
[../SKILL.md](../SKILL.md). Device-optional procedure and mocks:
[device-alternatives.md](device-alternatives.md).

---

## Input report

Parse `network-issues-report.json` → `confirmed[]`, or the **Confirmed gaps** table.

| Field | Use |
|-------|-----|
| Repo | Collection (`cisco.nxos`) |
| Module | e.g. `nxos_hsrp_interfaces` |
| Parameter | Argspec path for playbook vars |
| File:Line | Primary fix location |
| Pattern | → [patterns.md](../../network-issues-knowledge/patterns.md) |
| Issue | Expected broken behavior |
| Potential Fix | Implementation direction |

`--issue N` → 1-based index into confirmed gaps.

---

## Collection paths

Look up the confirmed gap's **Repo** field in
[repos.yaml](../../network-issues-scanner/config/repos.yaml) `collections[]` for
`platform` and `module_prefix`, then apply the path templates below:

| Artifact | Path |
|----------|------|
| Argspec | `plugins/module_utils/network/{platform}/argspec/{module}/` |
| Templates | `plugins/module_utils/network/{platform}/rm_templates/{module}.py` |
| Config | `plugins/module_utils/network/{platform}/config/{module}/{module}.py` |
| Unit tests | `tests/unit/modules/network/{platform}/test_{module}.py` |
| Integration | `tests/integration/targets/{module}/tests/cli/*.yml` |
| Changelog | `changelogs/fragments/` |
| Module docs | `plugins/modules/<prefix><module>.py` (`EXAMPLES`) |

**Pattern 11:** fix location is `plugins/modules/<prefix><module>.py` — update the
`EXAMPLES` string (and embedded examples in `DOCUMENTATION` if present). Reproduce
using the faulty example YAML from that block; verify with the corrected example.

---

## Branch

Collection clones are **forks**. Sync `main` from **upstream** (ansible-collections), branch locally, push to **origin** (your fork) later in step 12.

**`--dry-run`:** do **not** create a branch. Stay on the current branch; apply local
edits in place so the user can preview with `git status` / `git diff`. Still do not
commit or push.

```bash
cd <collection-path>
git remote -v   # confirm origin (fork) + upstream (ansible-collections)

git fetch upstream main
git checkout main
git pull upstream main
git checkout -b fix-<module-without-prefix>-<short-slug>
```

If the clone is not a fork (direct ansible-collections clone), `origin` may point at upstream — use `origin` for fetch/pull in that case. Prefer fork workflow when `upstream` remote exists.

Examples: `fix-hsrp-preempt-replaced`, `fix-bgp-shutdown-set`, `fix-bgp-global-max-metric`.

Clean working tree before branching. Slug: 2–4 hyphenated words from parameter/symptom.

---

## Reproduction playbook

**`--skip-device`:** skip this section and steps 3–4 / 6 device runs. See
[device-alternatives.md](device-alternatives.md).

### Before writing

1. List playbook directory; read 1–2 **same-platform** sibling playbooks
2. Copy: `hosts`, connection, `ansible_network_os`, collections, credentials, group_vars
3. Use `<module>_config` or a setup task only if baseline device state is required

### Skeleton

```yaml
---
- name: Reproduce <module> — <parameter>
  hosts: <from_sibling_playbooks>
  gather_facts: false
  tasks:
    - name: Expose the bug
      cisco.<platform>.<module>:
        config: { }  # minimal; target reported parameter path only
        state: <merged|replaced|overridden as needed>
      register: result

    - name: Debug
      ansible.builtin.debug:
        var: result
```

- One play; one module task (+ optional debug); no unrelated tasks
- Idempotency bugs: second identical task + `assert:` on `changed: false`

### Iterate in place

One file per issue: `repro_<module>_<slug>.yml`. On any failure or failed repro → **edit same file**, re-run. Never create `repro_v2`, `_fixed`, or copies.

### Corrective playbook (step 6 — before unit tests)

Evolve the **same** repro playbook: wrap tasks in `block`/`always` so device changes auto-undo. Re-run; confirm fix; save **after** snippet.

```yaml
---
- name: Reproduce and verify <module> — <parameter>
  hosts: <from_sibling_playbooks>
  gather_facts: false
  tasks:
    - block:
        - name: Apply / verify fix
          cisco.<platform>.<module>: { config: { }, state: <as needed> }
          register: result
        - ansible.builtin.assert:
            that: [ result.changed ]  # adjust for idempotency
      always:
        - cisco.<platform>.<module>: { config: { }, state: deleted }
          ignore_errors: true
```

Rules: teardown reverses all setup; read `_remove_config.yaml` for reference; iterate same file.

### Run

```bash
source <venv>/bin/activate
cd <playbook-dir>
ansible-playbook repro_<module>_<slug>.yml -v
```

Install collection editable if siblings do (`ansible-galaxy collection install -e .`).

### Pattern repro hints

| Pattern | Vars / state to use |
|---------|---------------------|
| 1–3 | Pre-enabled device state; `set: false` or negate |
| 4 | Uncovered leaf; expect no-op or wrong `changed` |
| 5–7 | Type/exclusivity edge values |
| 6 | Second identical run; expect `changed: false` |
| 10 | `state: replaced`; partial sub-keys in want; extra sub-keys on device |
| 11 | Copy task vars verbatim from `EXAMPLES`; expect argument validation failure or wrong module behavior |

**Pattern 11 (stale EXAMPLES):** use `EXAMPLES` task vars as repro input (step 3);
fix the `EXAMPLES` block in `plugins/modules/` (step 5); sanity tox validates
docs. See [patterns.md](../../network-issues-knowledge/patterns.md) for
confirm/drop bars.

---

## Fix

Minimal change aligned with **Potential Fix** and pattern catalog:

- `rm_templates/{module}.py` — getval / setval / compval / result
- `config/{module}/{module}.py` — registration, compare, state handling
- `argspec/` — only when schema/type requires it
- `plugins/modules/<prefix><module>.py` — `EXAMPLES` (Pattern 11 only)

Do **not** re-run the corrective playbook here — that is step 6 (after evolving teardown).
For Pattern 11, step 6 re-runs the repro playbook with corrected example vars instead of
device teardown (unless the example is a configure task that changes device state).

---

## Changelog

`changelogs/fragments/<short-description>.yml`. Match wording of existing fragments.

```yaml
---
bugfixes:
  - >-
    <module> - <user-visible fix> (fixes <parameter>).
# Pattern 11: use minor_changes; text: "update EXAMPLES to match current argspec for <parameter>."
```

---

## Tests

### Universal rules

| Rule | Detail |
|------|--------|
| **Read first** | Read existing cases; pick closest as template before any edit |
| **Update, don't add** | Extend existing case; new method/file only if nothing covers the scenario |
| **One scenario per case** | One bug path per `def test_*` or per integration `.yml` |

### Order

1. **Corrective repro playbook** re-run passes (step 6) — or under `--skip-device`:
   fix applied + rationale recorded ([device-alternatives.md](device-alternatives.md))
2. Update **unit** case → run **unit + sanity** tox (gate)
3. Update **integration** case (source only)
4. **Integration sim playbook** in playbook dir + run on device (step 10) —
   **N/A** under `--skip-device`

Integration tests **cannot be run** via tox in this environment — use the sim
playbook instead (default path), or rely on unit fixtures under `--skip-device`.

### Unit cases

`tests/unit/modules/network/<platform>/test_<module>.py`

1. Find `def test_*` for same `state` / parameter family
2. Mirror its `set_module_args`, fixtures, assertion style
3. Update vars and expected `commands` / result in **that one method**

### Unit + sanity tox

```bash
source <venv>/bin/activate
cd <collection-path>
tox --ansible -c tox-ansible.ini -e unit-py3.11-2.19
tox --ansible -c tox-ansible.ini -e sanity-py3.11-2.18
```

Read `tox.ini` / `tox-ansible.ini` for `<unit-env>` and Python/Ansible versions.

### Integration cases (update only)

`tests/integration/targets/<module>/tests/cli/*.yml`

1. Find case matching state operation (`replaced`, `merged`, etc.)
2. Mirror task/assert layout from that file
3. Update tasks/asserts for fixed behavior in **that one file**
4. Pattern 10: update existing replace/overridden case, not a new target

Do **not** run `tox -e <integration-env>` or any integration playbook locally.

---

## Integration simulation playbook

**`--skip-device`:** skip step 10 entirely (N/A).

**Step 10 — after integration case updates (step 9).** CI integration cannot run here;
simulate on the lab device with a playbook in the **playbook directory**.

### Before writing

1. Read the **updated** integration case `.yml` you edited in step 9
2. Read includes it uses: `_populate_config.yaml`, `_remove_config.yaml`, and any setup blocks
3. Read sibling playbooks in playbook dir for hosts, credentials, interface vars (`nxos_int1`, etc.)

### Create `sim_<module>_<slug>.yml`

One playbook that mirrors the **full** integration scenario:

| Phase | Source | Playbook equivalent |
|-------|--------|---------------------|
| Cleanup start | `_remove_config.yaml` / `include_tasks: _remove_config` | Inline `nxos_config` / module `deleted` tasks at top |
| Populate | `_populate_config.yaml` | Inline setup tasks (features, interfaces, baseline HSRP, etc.) |
| Test body | Main case tasks (merged / replaced / assert) | Same module tasks and `register: result` + asserts |
| Cleanup end | Trailing `_remove_config.yaml` | `always` block or final teardown tasks |

Flatten `include_tasks` into inline tasks — the sim playbook must be **self-contained** (no paths into the collection test tree).

```yaml
---
- name: Simulate integration — <module> <state>
  hosts: <from_sibling_playbooks>
  gather_facts: false
  tasks:
  - block:
      # inline: _remove_config tasks, then _populate_config tasks
      - cisco.<platform>.<module>: { config: { }, state: replaced }
        register: result
      - ansible.builtin.assert: { that: [ ... ] }
    always:
      # inline: _remove_config tasks
```

### Run simulation

```bash
source <venv>/bin/activate
cd <playbook-dir>
ansible-playbook sim_<module>_<slug>.yml -v
```

Iterate **same sim file** in place on failure. Device should be clean after `always` teardown.

Record pass/fail summary for deliverables. If sim fails but unit passed, reconcile integration case vs playbook before PR.

---

## Device cleanup

**`--skip-device`:** N/A.

Step 11: ask user before reverting residual device state. Revert only with explicit approval.

| What was configured | Typical revert |
|---------------------|----------------|
| New interface / VLAN SVI | `no interface Vlan218` |
| Feature enabled | `no feature <name>` |
| HSRP / standby block | `no hsrp <group>` under interface |
| Scalar knob set | `no <command>` |
| List merge item added | `no …` or `state: deleted` / `purged` |

Write a minimal `cleanup_<module>_<slug>.yml` in playbook dir if user approves. Then proceed to [upstream-pr.md](upstream-pr.md).

Evidence format: see [upstream-pr.md](upstream-pr.md).
