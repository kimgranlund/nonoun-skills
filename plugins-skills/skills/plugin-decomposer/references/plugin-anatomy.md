# Plugin anatomy — the manifest / marketplace / skills-discovery contract

The MANIFEST axis (B) grades whether a plugin **actually installs & loads**. This is the contract it
grades against: what a valid Claude Code plugin and its marketplace entry must satisfy, and the
discovery model that ties them together. `bin/plugin-check.py` mechanizes the deterministic parts
(B1–B4); this doc is the human-readable spec behind it.

## The chain

A plugin is discovered and installed through a three-link chain — break any link and the plugin
silently doesn't load:

```
marketplace.json   "plugins":[ { name, source, description, … } ]   ← the catalog
        │ source points at →
<plugin>/.claude-plugin/plugin.json   { name, version, … }          ← the manifest (version lives here)
        │ the loader discovers components by convention under →
<plugin>/skills/<skill>/   commands/   agents/   hooks/   .mcp.json  ← the components
```

The non-obvious rule: **there is no central component registry inside a plugin.** The loader
discovers components by directory convention — anything under `skills/<name>/` with a `skill.json` is
a skill; `commands/*.md` are slash commands; `agents/*.md` are subagents; `hooks/` and an MCP config
declare hooks and MCP servers. So "add a skill to a plugin" is just "create the folder" — but "add a
*plugin*" requires both its `plugin.json` **and** a `marketplace.json` `plugins[]` entry, or the
catalog can't resolve it (B3).

## B1 — `plugin.json` well-formed (the manifest)

Lives at `<plugin>/.claude-plugin/plugin.json`. The hard floor is two fields; the rest are
conventional metadata (present in this repo's plugins, but not load-blocking):

| Field | Required | Shape | Notes |
|---|---|---|---|
| `name` | **yes** | kebab-case string | must match the marketplace entry `name` (B3) |
| `version` | **yes** | semver string | the version lives **here**, not in `marketplace.json` |
| `description` | conventional | string | refreshed when the plugin gains a component |
| `author` | conventional | `{name, email}` | |
| `homepage` | conventional | URL string | |
| `license` | conventional | SPDX string | |
| `keywords` | conventional | string[] | |

A missing/empty/wrong-type `name` or `version`, or a non-object manifest, is **MANIFEST_INVALID** —
the manifest can't be parsed into a loadable plugin. (`bin/plugin-check.py` gates on `name` +
`version` only; it does not fail a plugin for omitting `homepage`.)

## B2 — name & version valid

- **name — kebab-case.** Lowercase letters/digits joined by single hyphens: `plugin-decomposer`,
  `code-skills`. **Not** `Foo Bar` (space/caps), `foo_bar` (underscore), `-x` / `x-` (edge hyphen),
  `x--y` (double hyphen). The name is an identifier (namespacing, install paths, the
  `marketplace.json` key) — a non-kebab name breaks resolution. → **BAD_NAME**.
- **version — semver.** `MAJOR.MINOR.PATCH`, optionally `-prerelease` and `+build`: `0.1.0`,
  `1.2.3`, `1.0.0-rc.1`. **Not** `1.0` (two-part), `v1.0.0` (`v` prefix), `latest`. → **BAD_VERSION**.

## B3 — the marketplace entry resolves

`marketplace.json` (at the repo root, under `.claude-plugin/`) is the catalog. Each plugin needs one
`plugins[]` entry:

```json
{
  "name": "plugin-decomposer-plugin",
  "source": "./plugins-skills",
  "description": "what the bundle is for",
  "category": "meta",
  "tags": ["skills", "decomposition", "rubric"]
}
```

The two load-bearing fields are **`name`** and **`source`**:

- **`name`** must match the manifest `name` it points at, or the catalog references a plugin that
  doesn't identify itself the same way — it won't resolve. → **MARKETPLACE_MISMATCH** (also raised
  when no `plugins[]` entry names the plugin at all).
- **`source`** must be a legal path to the plugin dir (a relative `./<plugin>` in this repo). An
  absolute or `../`-escaping source is **ILLEGAL_PATH** (B4).

`description`/`category`/`tags` are the routing surface for *humans* browsing the marketplace; keep
the marketplace `description` and the `plugin.json` `description` in sync, and refresh both when the
plugin gains a component.

## B4 — paths legal

Every path a manifest or marketplace entry declares — `source`, and any explicit `commands` /
`agents` / `hooks` / `mcpServers` / `skills` paths — must be **portable**: relative, and contained
inside the plugin dir. A path is **ILLEGAL_PATH** if it is:

- **absolute** (`/etc/passwd`, `C:\x`, `~/x`) — won't exist on another machine / install root;
- **escaping** (`../shared/hook.json`, `a/../../b`) — reaches outside the bundle, so a copy-alone
  install breaks.

A legal-path run is **necessary, not sufficient**: the checker confirms the path *shape* is portable;
it does not confirm the file *exists* with the right content (that is on-disk validation, and in this
repo it's the job of the repo-wide `bin/check-skills.py` gate, which asserts every `skill.json`
`files[]` path exists). So B4 is scored as a `[review]`, not a pure gate.

## B5 — self-contained (review, not gateable)

A plugin should install and work from a **copy alone** — no undeclared dependency on another plugin's
files, on a tool the user is assumed to have, or on a path outside the bundle. The checker can flag an
*illegal path* but **cannot** prove self-containment: an undeclared runtime dependency (an MCP server
expecting an external binary, a hook shelling out to a tool, a skill `references/` link pointing into
a sibling plugin) reads as clean JSON. So B5 is a **review**, confirmed by reading the components, not
by `plugin-check.py`.

In this repo's idiom, self-containment also means: deterministic checks live in a skill's `bin/` as
selftested **stdlib** Python (no third-party imports), and a skill's `SKILL.md` is a table-of-contents
over its own `references/` — a link escaping the skill dir is a cross-skill reference (a warning), not
a contained dependency.

## The skill-bundle special case

This repo ships **skill-bundle plugins**: a plugin that bundles *only* skills — no commands, agents,
hooks, or MCP. The motive is the BUNDLE axis's A5 (standing-context cost): general-purpose skills are
kept out of product plugins so they don't bloat a plugin's always-on context. For a skill-bundle:

- the plugin declares no `commands`/`agents`/`hooks`/`mcpServers`, so it can never trip **KITCHEN_SINK**
  on component-kind count — its kitchen-sink risk is *too many unrelated skills* under one bundle,
  which is a **review** judgment (A3 cohesion), not a checker finding;
- each skill is its own self-contained folder under `skills/<name>/` with a `skill.json` whose `name`
  matches the dir — and the repo gate (`bin/check-skills.py`) validates the skills independently of
  the plugin manifest, so a skill passes its own contract before the plugin's `plugin.json` and
  marketplace entry even exist.

## How `plugin-check.py` maps onto this contract

| Finding | Severity | Level | Means |
|---|---|---|---|
| `MANIFEST_INVALID` | gate | B1 | non-object, or `name`/`version` missing/empty/wrong-type |
| `BAD_NAME` | gate | B2 | `name` not kebab-case |
| `BAD_VERSION` | gate | B2 | `version` not semver |
| `MARKETPLACE_MISMATCH` | gate | B3 | supplied marketplace entry `name` ≠ manifest `name` (or no entry found) |
| `ILLEGAL_PATH` | gate | B4 | a declared component/`source` path is absolute or escapes the dir |
| `KITCHEN_SINK` | advisory | A3/A4 | ≥4 distinct declared component kinds — an unfocused-bundle smell |

`KITCHEN_SINK` is the one *bundle*-axis signal the checker emits, and it is deliberately **advisory**:
the count of component kinds is a lossy proxy for "doing more than one job." Confirm the real BUNDLE
verdict (A1–A5) by review and an adversarial one-job probe — never read a clean `plugin-check.py` run
as proof the bundle is focused.
