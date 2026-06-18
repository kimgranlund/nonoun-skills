---
date: 2026-05-06
---

# Adversarial Probe — Find What Breaks

Systematically attack the system to discover failure modes, edge cases, and breaking points. Generate inputs designed to fail, then fix the failures found.

## Input

$ARGUMENTS — What to probe. Can be:
- A component or module to stress-test
- A generation or transformation pipeline
- A scoring or evaluation system (can we fool it?)
- An API or interface (error handling, edge cases)
- A configuration system (invalid states, conflicts)
- Default: the most recently changed component or system

## Configuration

- **MAX_ROUNDS**: 100 (override with "max N rounds" in arguments)
- **SEVERITY_THRESHOLD**: "medium" (report bugs at this level or higher)
- **FIX_MODE**: true (fix bugs as found) or false (just report)

## Phase -1: Research (MANDATORY)

Before probing, use web search to gather knowledge about known vulnerability classes for the system under test. Real attackers do reconnaissance first — so should you.

1. **Search for known bugs and CVEs** — What are documented vulnerabilities in this type of system? What common failure modes exist in this domain?
2. **Search for attack patterns** — What are established techniques for breaking this class of system? (e.g., OWASP for web, fuzzing for parsers, boundary analysis for numeric systems)
3. **Search for testing techniques** — What do QA professionals recommend for this domain? Property-based testing? Mutation testing? Chaos engineering?
4. **Build an attack playbook** — Compile known attack patterns from research-survey into a prioritized list. Test the highest-risk ones first.

This phase ensures you're testing known-dangerous patterns, not just random inputs. The best adversarial probes come from studying real-world failures.

## Phase 0: Threat Model

1. **Identify attack surface** — What can go wrong? Universal categories:
   - **Boundary values** — empty, null, undefined, max-length, negative, zero, off-by-one
   - **Type confusion** — wrong types, mixed types, implicit coercion, format mismatches
   - **Volume** — too many items, deeply nested structures, extremely large inputs
   - **Timing** — rapid sequential calls, concurrent operations, race conditions, timeouts
   - **Mutation** — state changes mid-operation, unexpected modifications, stale references
   - **Content** — malformed input, special characters, encoding issues, injection payloads
   - **Environment** — missing dependencies, permission changes, resource exhaustion, config drift
   - **State** — invalid transitions, repeated operations, interruption mid-process

2. **Prioritize probes** — Rank by likelihood × impact.

```
╔══════════════════════════════════════════════════╗
║  ADVERSARIAL PROBE — {target}                    ║
╠══════════════════════════════════════════════════╣
║  Attack categories: {count}                      ║
║  Planned probes: {count}                         ║
║  Fix mode: {on|off}                              ║
╚══════════════════════════════════════════════════╝
```

## Phase 1: Loop

For each probe (1 to MAX_ROUNDS):

### Step 1 — Design the attack
Create a specific input or scenario designed to break the system. Be creative and thorough.

### Step 2 — Execute
Apply the attack. Observe the result.

### Step 3 — Classify
- **CRASH** — unhandled exception, total failure, hung process
- **CORRUPT** — wrong output, garbled results, data loss, silent failure
- **DEGRADE** — works but poorly (slow, truncated, partial results)
- **SURVIVE** — handled gracefully (error message, fallback, boundary enforcement)

### Step 4 — Fix (if FIX_MODE)
If the probe found a bug at SEVERITY_THRESHOLD or above, fix it before continuing. Re-run the probe to verify the fix.

### Step 5 — Print result
```
Probe {n}: {attack_description}
  Category: {boundary|volume|timing|content|...}
  Result: {CRASH|CORRUPT|DEGRADE|SURVIVE}
  Severity: {critical|high|medium|low}
  {Fixed: {description} | Reported: {details}}
```

## Phase 2: Hardening (if FIX_MODE)

After all probes, re-run the ones that initially failed to verify all fixes hold.

## Phase 3: Report

```
╔══════════════════════════════════════════════════════╗
║  ADVERSARIAL PROBE COMPLETE                          ║
╠══════════════════════════════════════════════════════╣
║  Probes run: {total}                                 ║
║  Survived: {survive_count} ({survive_pct}%)          ║
║  Degraded: {degrade_count}                           ║
║  Corrupted: {corrupt_count}                          ║
║  Crashed: {crash_count}                              ║
║                                                      ║
║  Bugs found:                                         ║
║    1. {description} — {severity} — {fixed|reported}  ║
║    2. {description} — {severity} — {fixed|reported}  ║
║                                                      ║
║  Most fragile area: {category}                       ║
║  Robustness score: {survive_count}/{total}            ║
║                                                      ║
║  Recommended hardening:                              ║
║    - {action_1}                                      ║
║    - {action_2}                                      ║
╚══════════════════════════════════════════════════════╝
```

## Rules

- **Be creative** — think like a QA engineer, a malicious user, and a tired developer simultaneously
- **Test the edges** — empty strings, max int, rapid toggling, concurrent mutations
- **Fix as you go** (if FIX_MODE) — don't accumulate bugs; fix each before moving on
- **Verify fixes** — re-run the probe after fixing to confirm
- **Escalate** — if a probe reveals a class of bugs (e.g., "all inputs over 10k chars crash"), probe the entire class
- **Document** — write up critical bugs even if fixed, for future reference
- **Web search on unfamiliar failures** — When a probe triggers an error you don't recognize, a crash in an external dependency, or behavior that seems environment-specific, STOP and use web search to look up the error message or stack trace. Known bugs, spec edge cases, and platform quirks are often documented. Search before guessing at a fix.
