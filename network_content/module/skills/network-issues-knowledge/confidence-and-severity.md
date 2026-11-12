# Confidence and Severity

Hit confidence levels used during discovery. Final verdicts follow
[verification.md](verification.md).

---

## Scanner confidence levels

| Confidence | Meaning |
|------------|---------|
| `confirmed` | Code inspection shows a clear mismatch with no obvious mitigating path |
| `likely` | Strong signals; needs validator cross-check of config class or sibling parsers |
| `candidate` | Mechanical or heuristic signal only |

**Discovery rule:** prefer inclusion over exclusion. When uncertain, include the hit
with `candidate` confidence and a note — let validation decide.

**Known mitigations to note (not drop during scan):**

- Parser uses `name` only and comparison path may match argspec — mark `candidate`
- Template may use a separate parser for negate — note parser name in `Notes`
- Parameter may be intentionally parsed-only or config-only — cite docs if seen
- `set: false` may be handled by config class logic — note config file path
- Mechanical script flags a pattern that needs manual review — keep as `candidate`

## Severity hints

| Severity | Examples |
|----------|----------|
| **High** | Silent no-op, wrong commands, broken disable/toggle |
| **Medium** | Type mismatch, idempotency, exclusivity |
| **Low** | Stale code, test gaps, outdated EXAMPLES (Pattern 11) |

Sort output by confidence (`confirmed` first), then severity, then repo, then module.

## Discovery priority (avoid overfitting)

1. **Argspec/template crosswalk** — catches the broadest set of real gaps
2. **Mechanical script output** — all pattern families, not only boolean toggles
3. **Boolean `.set` / negate patterns (1–3)** — high impact but one family among many
4. **Type, compound CLI, exclusivity, idempotency (5–7, 10)** — require argspec + Cisco CLI semantics
5. **Tests and stale code (8–9)** — supporting evidence, often lower immediate user impact
6. **Module EXAMPLES vs argspec (11)** — documentation drift; compare `plugins/modules/<prefix><module>.py` EXAMPLES to argspec and integration tests

Do not stop after finding shutdown/enable issues. Continue the full module crosswalk.
