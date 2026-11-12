# Parser Anatomy

Foundation for argspec ↔ template crosswalk and per-hit verification.

---

## Parser keys

Each rm_template entry is a **parser** with these roles:

| Key | Role |
|-----|------|
| `name` | Parser identifier; **default comparison path** for want/have diff |
| `getval` | Regex to parse device config into facts |
| `setval` | Jinja/function to generate CLI from desired state |
| `result` | Facts tree populated from parsed data — **not** the comparison path |
| `compval` | **Optional** override when comparison granularity differs from `name` |

## Comparison path rule

**Effective comparison path** = `compval` if present, else parser `name`.

Supports dot notation (e.g. `use.neighbor_group`, `bgp.cluster_id`,
`max_metric.router_lsa.on_startup`).

When crosswalking argspec → templates, collect **both** parser names and
compvals. Do not treat absent `compval` as missing coverage.

## When `compval` is normal vs required

**Normal (not a gap):** Most parsers do **not** have `compval`. In `cisco.iosxr`,
modules like `logging_global`, `snmp_server`, `route_maps`, and `ntp_global` use
parser `name` alone (often zero `compval` entries). Direct-value options such as
`receive_buffer_size` compare by parser name.

Use `compval` only when parsers are split into namespace-style pieces and the
comparison key must differ from `name`. See the
[Resource Module dev guide](https://github.com/ansible-network/networking-docs/blob/main/rm_dev_guide.md).

## Config registration

A parser defined in `rm_templates/{module}.py` only participates in command
generation when registered in `config/{module}/{module}.py` — typically in
`self.parsers` or lists passed to `compare()`.

An unregistered parser is a gap **only if** the parameter requires template-driven
parse or generate.

## Sibling and negate parsers

Before flagging Patterns 1–3, check the same rm_template for:

- A second parser whose `name`/`compval` ends in `.set` while another handles the parent struct
- A dedicated negate parser (distinct entry matching `no …` CLI)
- Namespace-style split parsers where `compval` on a child covers the leaf

## Config-class handling outside templates

Some parameters are handled in Python config class logic rather than rm_templates:

- Custom methods generate or reconcile `set: false` / negate CLI
- Intentionally gather-only or config-only parameters per argspec/docs

Always read `config/{module}/{module}.py` before confirming or dropping a hit.
