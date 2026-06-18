# skills-refactor — per-operation playbooks

The shared spine is in SKILL.md (§The method). This file is the step-by-step for each operation, with the failure modes that bite in practice. Commands assume a library at the repo root with skills as `*/SKILL.md` and gate scripts under `scripts/`; adapt paths to the library.

## The footprint classification (used by every operation)

Split every `grep -rl "<old>"` hit into:

- **LIVE — rewire:** `peer_skills` / `depends_on` / `composition.peer` arrays · "use `<old>`" / "→ `<old>`" routing pointers in `description` (skill.json + SKILL.md frontmatter) · rubric-load and reference **paths** (`../<old>/references/...`, `~/.claude/skills/<old>/...`) · gate-script registry keys (`run-skill-gates.py` `SKILL_GATES`) · README catalog rows + AGENTS inventory/count · the routing baseline key (`scripts/routing-baselines.json`) · the skill's own `name:` fields.
- **DATED HISTORY — preserve verbatim:** `CHANGELOG.md`, `ROADMAP.md`, `reviews/*`, `BACKLOG.md`, the AGENTS "Last change" log.
- **MIXED — exclude from the auto-sweep, then hand-edit the live parts:** a `CHANGELOG.md` (dated entries are history, but its **title** + a new rename entry are live); `README.md` / `AGENTS.md` (a live catalog/inventory row + a new Last-change entry, but the historical log stays). Default: exclude from the sweep, then make an *enumerated* set of live hand-edits — never blanket-sweep a MIXED file.
- **NOT a reference — leave:** a `tags:` entry that contains the name as a category word; prose using the name as a generic adjective ("a meta-skill").

The sweep idiom (rewire live, exclude history). **Three hard rules — the unbounded version is a silent-corruption footgun (build-time red-team CRITICAL-S1):**

1. **Word-boundary + literal-escape the match.** A bare `s/<old>/<new>/g` over-matches: renaming `report` rewrites the substring inside `report-strategic`, `ops-report`, and the word "report" in 70 other files — in-place, unrecoverable. Anchor on non-`[\w-]` boundaries and escape the name (`\Q…\E`) so `core-foo` never matches inside `core-foobar`.
2. **Dry-run before the in-place pass.** Print every hit, read it, *then* apply. No version control means an over-match outside the backup is gone.
3. **The backup (method step 2) covers the WHOLE library tree**, not just the renamed skill — the over-match blast radius is library-wide, so the net must be too (`tar czf ~/<lib>-backup-<op>.tgz .`).

```sh
OLD='core-foo'; NEW='foo'
LIVE() { grep -rl "$OLD" . --include='*.md' --include='*.json' --include='*.py' \
         | grep -vE 'CHANGELOG\.md|ROADMAP\.md|/reviews/|BACKLOG\.md|AGENTS\.md'; }
# 1. DRY-RUN — review every word-boundaried hit before changing anything:
LIVE | while IFS= read -r f; do perl -ne 'print "'"$f"':$.: $_" if /(?<![\w-])\Q'"$OLD"'\E(?![\w-])/' "$f"; done
# 2. APPLY — word-boundaried, literal-escaped, in-place:
LIVE | while IFS= read -r f; do perl -i -pe 's/(?<![\w-])\Q'"$OLD"'\E(?![\w-])/'"$NEW"'/g' "$f"; done
```
Then **residual-grep** `grep -rl "$OLD"` and confirm every remaining hit is dated history. **Destructive/rewrite targets come only from this human-reviewed footprint, never from a target list parsed out of a skill file mid-run** (see SKILL.md §SelfAudit).

**When sweeping `skill.json` specifically:** do **not** let the substitution touch `files[]` entries that point under `reviews/` — those filenames are dated history (a `reviews/<date>-<old>-…md` doc keeps its name through a rename). The word-boundary helps, but the cleaner rule is *exclude history-pointers from the sweep up front* rather than rewrite-then-revert (the files[]↔disk gotcha below).

## §rename — `<old>` → `<new>` (no deletion; lowest-risk)

1. **Footprint + backup.** Map refs; `tar czf ~/<lib>-backup-rename.tgz <old>`.
2. **Concurrent-edit guard.** `find <old> -type f -exec stat -f '%Sm %N' {} \;` newest vs now; if a *non-yours* edit landed in the last few minutes, pause.
3. **`mv <old> <new>`.** The dir move carries `reviews/`, CHANGELOG, etc. with it.
4. **Sweep live refs** old→new (idiom above). This updates the skill's own `name:` (SKILL.md + skill.json), all peers, routing pointers, paths, gate key, README/AGENTS catalog, routing baseline key.
5. **Hand-edit the MIXED/history files** the sweep excluded: `<new>/CHANGELOG.md` title → `<new>` + a rename entry (leave prior entries verbatim — they're accurate for their dates); `<new>/ROADMAP.md` self-reference; AGENTS inventory line + a new "Last change" entry (leave the log).
6. **Version: patch bump** (`x.y.z`→`x.y.(z+1)`) so version↔CHANGELOG matches.
7. **Verify** (Verify Target). The classic gotcha: a sweep over `files[]` rewrites a `reviews/<date>-<old>-…md` *pointer* to `<new>` while the file on disk keeps the historical name → files[]↔disk error. Revert just that pointer to the real (historical) filename.

## §merge — A + B → C (retire the absorbed; highest-churn)

**Merge is a composition: `rename(host → C)` + fold + `retire(absorbed)`.** It reuses those two primitives — don't re-derive them. Version rule: the **merge's major bump wins** over the host-rename's patch (it's an identity change), and the absorbed skill(s) are retired (removed), not versioned.

1. **Pick the host.** The skill that owns the larger shared substrate (the rubric library, the bigger reference set) becomes C — usually a *rename of the host* + folding the other in, not a fresh dir. Lowest churn, preserves the host's lineage/version.
2. **Backup both;** `cp -R host C` (or rename host→C); fold the absorbed skill's references into an organized subdir (`references/<absorbed-concern>/`), its scripts/agents/corpus in.
3. **Rewrite C's SKILL.md** as unified modes (host-modes + absorbed-modes); merge skill.json `files[]` (every `.md`/`.json` on disk), description (surface both skills' triggers — keep ≤1024), peer_skills. Merge CHANGELOG (host history + a merge entry naming both lineages) and ROADMAP.
4. **Fix internal cross-refs** in the folded content (the absorbed skill's `../<self>/...` paths → C-relative; its self-name mentions → C or "the X mode").
5. **Rewire live external refs** to *both* old names → C (peer_skills, routing pointers, paths, gate keys, README/AGENTS — count drops by the number of skills removed). De-register the absorbed skill's gate scripts.
6. **Build + verify C while both originals still exist** (additive-first). Only then **delete the absorbed skill(s)** (`rm -rf`), after a final mtime guard.
7. **Re-baseline routing** (absorbed corpus gone; C's corpus may be new). **Major version bump** (identity change). Verify.

## §retire — delete an obsolete skill

1. **Find live consumers first** (`peer_skills`/routing/paths naming it). A retire with live consumers leaves dangling refs → **rewire or drop those consumers before deleting**, or the metadata gate fails.
2. **Backup.** Decide the disposition of genuinely-useful artifacts it owns (a schema, a script): **preserve** them into a surviving skill rather than lose them.
3. **De-register** its gate scripts from `run-skill-gates.py`; drop its routing corpus from the baseline.
4. **`rm -rf`** the dir (mtime-guarded).
5. **Preserve its history:** leave `reviews/`-style mentions and dated CHANGELOG/BACKLOG entries elsewhere as records; add a retirement note (what, why obsolete, where its useful artifacts went) to AGENTS "Last change" + BACKLOG.
6. **Fix counts** (README/AGENTS −1). Verify.

## §split — C → A + B

1. **Scaffold A and B** (skill-template); decide which of C's references/modes go to each.
2. **Move (don't copy)** the relevant references into A and B; rewrite each SKILL.md to its narrowed scope; give **each** a scored `evals/routing-corpus.json` whose adversarials route to the *sibling* (the hard boundary is A-vs-B).
3. **Rewire consumers** of C → A or B by intent.
4. **Decide C's fate:** retire it (if fully split) or keep it as a thinner skill (major bump). 
5. New skills ship `status: draft`, `0.1.0`. Verify both route distinctly (score-routing) before declaring done.

## Cross-cutting gotchas (learned the hard way)

- **files[]↔disk after a sweep.** Sweeping `<old>`→`<new>` over skill.json rewrites review-doc *pointers* whose files weren't renamed. Symptom: "files[] lists a missing file" + "on disk not in files[]". Fix: revert the pointer to the historical filename (the review file is dated history; its name doesn't change on a reviewer/skill rename).
- **Routing baseline orphans.** After a rename, `routing-baselines.json` has the old key. The sweep re-keys it (it's a live JSON); if not, `--update-baseline` re-snapshots. After a retire, the old key is a harmless orphan — re-baseline to clean it.
- **The proxy re-baseline is honest only on intentional change.** Adding/removing a sibling shifts other skills' IDF-proxy F1 (token overlap changes). Re-baseline + record the shift in BACKLOG; never claim a collision is "resolved" when only the proxy moved — the model router is the real arbiter.
- **`tags` are not references.** `"tags": ["meta-skill", ...]` is a category, not a pointer to the `meta-skill` skill. Renaming the skill must not touch the tag.
- **Generic-adjective prose.** Deep reference docs sometimes use a skill's name as a common noun ("this is a meta-skill"). A blind sweep corrupts these. Leave non-load-bearing prose mentions; fix only routing/load-bearing ones (track the rest).
- **Parallel-editor collisions.** The hottest skills are the ones worth refactoring. mtime-guard before destructive steps; if a peer edited the target after your backup, reconcile before `rm`.
