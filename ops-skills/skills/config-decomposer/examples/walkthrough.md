# Worked example — valid but unsafe on INTENT × VALIDITY

A complete DECOMPOSE → fix → GRADE for a config that **parses and schema-validates** cleanly and is
still dangerous — the signature failure `config-decomposer` exists to catch. The two `.yaml` files
here are checked in and `bin/config-lint.py` actually flags / clears them.

## The artifact

A `payments-api` service config. YAML parses, the schema validates, the plan applies. Ship it?

```yaml
service:
  image: payments-api:latest
database:
  password: "hunter2supersecret"
network:
  ingress:
    - cidr: 0.0.0.0/0
```

## DECOMPOSE

**A · Intent** (whole → part)
- **A1 Desired-state** `[gate]` — "a payments service reachable from the internal VPC." ✓
- **A2 Contract** `[gate]` — image pin, a DB credential, one scoped ingress. ✓

**B · Validity** (part → whole)
- B1 Parses / B2 Schema `[gate]` — green: the YAML is well-formed and every field is the right type.
- **B4 Safety** `[gate, code]` — a green parse is silent about *dangerous* values. Run the safety
  smell floor on the artifact (`examples/service.red.yaml`):

```
$ python3 bin/config-lint.py examples/service.red.yaml
config-lint: FAIL — 3 safety smell(s) across 1 file(s)
  examples/service.red.yaml:6  UNPINNED_VERSION   uses :latest — not reproducible, pin a version/digest
  examples/service.red.yaml:10  PLAINTEXT_SECRET   password set to a literal value — use a secret ref/var
  examples/service.red.yaml:14  OPEN_NETWORK       0.0.0.0/0 or ::/0 — open to the entire internet
```

**B4 has actually failed, proven mechanically.** Each value is *valid* and *catastrophic*: a literal
secret leaks into source control, `:latest` makes the deploy unreproducible, and `0.0.0.0/0` opens
the service to the entire internet. A schema validator is blind to all three — they are gate-grade
FAILs, not style nits.

## Fix — references, pins, and scope

Make the secret a reference, pin the image, and scope the ingress (`examples/service.green.yaml`):

```yaml
service:
  image: payments-api:1.4.2          # pinned
database:
  password: ${DB_PASSWORD}           # a reference, not a literal
network:
  ingress:
    - cidr: 10.0.0.0/8               # scoped to the private range
```

```
$ python3 bin/config-lint.py examples/service.green.yaml
config-lint: OK — no safety smells in 1 file(s)
```

The `${DB_PASSWORD}` reference is **not** flagged — the false-positive guard distinguishes a secret
*reference* from a secret *literal*, so the fix lands clean. The red→green transition is the proof.

## GRADE — two scores, never averaged

- **Intent: 5/5** — right desired state, sound contract; the *values* were the defect, not the shape.
- **Validity: B4 gate-fail → (after fix) 5/5** — parses, schema-valid, and the safety floor is now
  green (no secret/pin/ingress smell).

**Quadrant:** the red config sat in **"valid config, unsafe"** (Validity's B1/B2 passed — it's a fine
config — but the B4 safety floor was red) — *parses right, applies dangerously*. The fix is values
(ref + pin + scope), not schema machinery. After it: **SHIPPABLE**.

The lesson: "does it validate?" is the wrong question; "would a checked-in secret, a `:latest`, or a
`0.0.0.0/0` survive the parse?" is the right one — and that floor is mechanizable.
