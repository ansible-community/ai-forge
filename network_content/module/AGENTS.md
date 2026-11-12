# Network Content

Module provides skills for network automation workflows specific to Ansible network collections.

## When to Use

### Skills

- **network-collection-triage skill**: Use the `network-collection-triage` skill to triage bug reports,
  CI failures, and GitHub issues across Ansible network collections (cisco.ios, cisco.iosxr, cisco.nxos,
  arista.eos, junipernetworks.junos, ansible.netcommon, ansible.utils). Supports two modes: scan mode
  for bulk weekly triage across all repos (outputs structured JSON and markdown), and direct mode for
  deep triage of a single issue. Includes cross-collection cascade detection for shared dependencies
  (netcommon, utils) and known network CI failure patterns. Invoke when asked to "triage network issues",
  "scan network issues", "weekly triage", "triage CI failure", or "triage collection issue".

- **network-issues-orchestrator skill**: Use the `network-issues-orchestrator` skill to run the full
  end-to-end parser and rm_template gap audit across Ansible network collections (cisco.ios, cisco.nxos,
  cisco.iosxr, arista.eos). Runs `network-issues-scanner` then `network-issues-validator` automatically
  and delivers only confirmed gaps. Invoke when asked to "scan parser gaps and validate", "audit resource
  modules with confirmed results", "run the full network gap pipeline", or "find confirmed template bugs".
  Prefer this over running scanner and validator separately.

- **network-issues-scanner skill**: Use the `network-issues-scanner` skill to cast a wide net across
  network collection resource modules and collect candidate gap hits. Covers argspec coverage gaps,
  boolean toggle mismatches, missing negate capture, type mismatches, compound CLI issues, stale parsers,
  outdated module EXAMPLES, and test blind spots. Emits candidate hits for validation — not a final
  report. Invoke when asked to "scan for parser gap candidates", "collect raw scanner hits", or when
  `network-issues-orchestrator` delegates the scan phase.

- **network-issues-validator skill**: Use the `network-issues-validator` skill to verify scanner hits
  by reading live source code and tests for each candidate, drop false positives, and emit a confirmed
  gap report. Input is `network-issues-scanner-hits.md` / `.json`. Invoke when a scanner run has already
  produced hits and the user wants them verified, or when `network-issues-orchestrator` delegates the
  validation phase.

- **network-issues-resolver skill**: Use the `network-issues-resolver` skill to reproduce and fix a
  single confirmed parser, rm_template, or documentation (EXAMPLES) gap from validator output. Acts as
  a senior Ansible network automation engineer: prepares a collection branch, writes reproduction
  playbooks, implements the fix with changelog and tests, validates via tox, and optionally opens an
  upstream draft PR. Supports `--skip-device` for code-only fixes (unit fixtures as primary mock) and
  `--dry-run` for a local on-disk preview without git branch/commit/push/PR (local file changes are
  still applied). Invoke when a validated report exists and the user wants to fix one confirmed gap.
  Resolves exactly one issue per invocation.

## Configuration

**Required Dependencies:**

- `gh` CLI — authenticated with `gh auth login` (used for GitHub queries and repo cloning)
- Python 3.8+ — required by `scan_mechanical_signals.py` and `validate_examples.py` (network-issues-scanner)
- PyYAML — required by scanner scripts for `config/repos.yaml` loading
- `ansible-test` — required by network-issues-resolver for unit and sanity validation
- `tox` with `tox-ansible` — required by network-issues-resolver for test execution

**Required Context:**

- Skills in this module are designed for Ansible network collection development and maintenance
- Network collection development follows standard Ansible collection conventions
- Network collections share common CI failure patterns (Galaxy version lag, cross-collection cascades)
- Parser gap skills require local clones of target collections or `gh api` access

## Notes

- All skills follow Ansible network collection conventions and best practices
- Skills are community-facing and should not contain internal business logic
- See SKILL_GUIDELINES.md for contribution criteria
- `network-issues-orchestrator` is the recommended entry point for end-to-end gap audits;
  use scanner/validator individually only when you need intermediate output or are resuming a partial run
- `network-issues-resolver` works on one confirmed gap at a time; run orchestrator first to get the
  validated report, then invoke resolver for each gap to fix
- Resolver flags: `--skip-device` (no lab; unit + sanity proof) and `--dry-run` (local edits OK;
  no branch/commit/push/PR — always communicate that local files were changed)
