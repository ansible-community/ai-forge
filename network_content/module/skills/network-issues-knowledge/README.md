# Network Issues — Common Knowledge

Shared reference for `network-issues-scanner`, `network-issues-validator`, and
`network-issues-orchestrator`. Consume these files as needed — skills decide
when each topic applies; knowledge files do not prescribe pipeline steps.

## Topics

| File | Topics covered |
|------|----------------|
| [parser-anatomy.md](parser-anatomy.md) | Parser keys, comparison paths, `compval` rules, config registration |
| [patterns.md](patterns.md) | Gap patterns: symptom, cause, detection signals, validation, fix |
| [crosswalk.md](crosswalk.md) | Argspec ↔ template ↔ config registration crosswalk |
| [verification.md](verification.md) | Per-hit review, verdicts, drop reason codes |
| [checklists.md](checklists.md) | Module-level analysis checklists |
| [confidence-and-severity.md](confidence-and-severity.md) | Hit confidence levels, severity hints, discovery priority |

## Scope balance

Patterns 1–3 (boolean toggle / negate) are one family. Do not over-index on
`shutdown`/`enable`. Coverage gaps, type mismatches, compound CLI, idempotency,
stale parsers, and stale EXAMPLES (Pattern 11) are equally common. Pattern 11 is
a documentation gap — details in [patterns.md](patterns.md).

## Discovery vs validation posture

| Posture | Behavior |
|---------|----------|
| **Discovery** | Cast wide net; prefer inclusion; assign confidence; note mitigations in `Notes` |
| **Validation** | Verify every hit in source; drop false positives; confirm only with evidence |

Implementing fixes is out of scope for all skills unless the user explicitly asks.
To reproduce and fix a single confirmed gap, use `network-issues-resolver`.
