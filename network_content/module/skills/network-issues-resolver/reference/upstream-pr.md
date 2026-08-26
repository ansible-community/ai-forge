# Upstream pull request

**After step 11 (device cleanup)** — or after step 9 when `--skip-device`. Ask the user:

> “Do you want a **draft** pull request opened against upstream (`ansible-collections/<repo>`)?”

Do **not** commit, push, or open a PR unless the user explicitly says yes. **Always use draft PRs** — never open a ready-for-review PR unless the user explicitly requests it.

**`--dry-run`:** do **not** run this workflow. Local files may already be modified for preview.
Show would-run commands only; ask keep / discard / continue without `--dry-run`.

Fork remotes setup: see [resolution-details.md](resolution-details.md) Branch section.

---

## Prerequisites

- Fix complete; unit + sanity tox passed
- Changelog fragment and test updates committed-ready
- **Before/after snippets captured** during repro (step 4) and corrective verify (step 6) —
  or from [unit-only evidence](#unit-only-evidence-skip-device) when `--skip-device` — required for PR body

---

## Workflow

```bash
cd <collection-path>
cat .github/PULL_REQUEST_TEMPLATE.md
git add <fix-files> <changelog> <tests>
git commit -m "Fix <module> <short description>"
git push -u origin HEAD
gh pr create \
  --draft \
  --repo ansible-collections/<repo> \
  --base main \
  --head <github-user>:<branch-name> \
  --title "<Title>" \
  --body "$(cat <<'EOF'
<filled template>
EOF
)"
```

Push to **origin** (fork); PR base is **upstream**. Do not push to upstream directly. Return draft PR URL.

---

## Filling `.github/PULL_REQUEST_TEMPLATE.md`

Read the template from the **target collection** at
`.github/PULL_REQUEST_TEMPLATE.md` and preserve its headings and checkboxes.

Network collections (cisco.ios, cisco.nxos, cisco.iosxr, arista.eos) typically include:

| Section | What to write |
|---------|----------------|
| **Description** | What / why / how — tie to validated report issue and pattern |
| **Type of Change** | Check **Bug fix** (and **Test update** if tests changed) |
| **Component Name** | Module FQCN, e.g. `cisco.nxos.nxos_hsrp_interfaces` |
| **Self-Review Checklist** | Check applicable items |
| **Testing Instructions** | Prerequisites, steps (repro playbook), expected results |
| **Command Output / Logs** | **Mandatory before/after snippets** (see below) |
| **Required Actions** | Check changelog, unit/integration test updates as applicable |

Do not strip template sections — fill or mark N/A. Match tone of merged PRs in that repo.

---

## Before / after snippets (required)

Include **both** in PR body under **Command Output / Logs**. Verbatim — trim noise, not failing lines.

| When | Capture |
|------|---------|
| **Before** (step 4) | `changed`, `commands`, errors from broken task |
| **After** (step 6) | Corrected `commands` / `changed` + assert pass |

### Unit-only evidence (skip-device)

State in Testing Instructions: "Validated via unit + sanity only; no device run."

| When | Capture |
|------|---------|
| **Before** | Pre-fix broken expected `commands` or failing unit assertion |
| **After** | Updated expected `commands` + tox unit pass line |

---

## PR title

Format: `<module> | <short fix description>`. Match style of recent merged PRs.

Examples: `nxos_hsrp_interfaces | Fix preempt replaced state setval` · `iosxr_bgp_global | Add parser coverage for max_metric suboptions`

If user provides a GitHub issue: add `Fixes #NNN` to Related Issue. Do not include repro playbooks, scanner/validator report artifacts, or unrelated changes.
