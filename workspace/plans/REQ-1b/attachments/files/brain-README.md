# The Brain — Personal Knowledge System

This is Chris Mauzé's personal knowledge vault, managed by [Obsidian](https://obsidian.md) and backed by Git. It is the single source of truth for everything Chris knows, decides, and learns. Claude Code agents read and write to this vault directly — it is the knowledge layer of the chris-os system.

---

## How It's Organized (PARA)

Everything in this vault follows the **PARA methodology** — four top-level folders, ordered by actionability:

```
brain/
├── 1-Projects/     Things you're actively working on (have a deadline or clear deliverable)
├── 2-Areas/        Ongoing responsibilities you maintain (no end date)
├── 3-Resources/    Reference material organized by topic (no action required)
├── 4-Archive/      Completed or inactive items (searchable, not browsed)
└── _inbox/         Unsorted captures — process into PARA during weekly review
```

### When to use each folder

**1-Projects/** — "I'm building this right now." Has a clear finish line. When complete, move to 4-Archive. Examples: `tibetan-spirit-ops-setup`, `portfolio-deck`, `email-automation-system`.

**2-Areas/** — "I'm responsible for this ongoing." No finish line, just a standard to maintain. Examples: `fitness` (training programming), `finance` (budgets, investments), `tibetan-buddhism` (practice, DKF board).

**3-Resources/** — "I might need this someday." Reference material organized by topic. No action required. Examples: `ai-engineering` (patterns, frameworks, research), `cpg-analytics` (industry knowledge), `dharma-teachings` (lineage materials).

**4-Archive/** — "This is done or no longer active." Searchable but not browsed. Projects move here when complete. Resources move here when obsolete.

**_inbox/** — "I captured this but haven't filed it yet." The staging area. Quick notes, Claude artifacts, downloaded PDFs that need classification. Process during weekly review. The vault-maintenance skill can help.

### The decision tree

```
Is this something I'm actively working toward completing?
  YES → 1-Projects/
  NO  →
    Is this an ongoing area of my life I need to maintain?
      YES → 2-Areas/
      NO  →
        Is this useful reference material I might need later?
          YES → 3-Resources/
          NO  → Delete it, or 4-Archive/ if uncertain
```

---

## Conventions

### Every note has frontmatter

```yaml
---
type: decision | principle | reference | note | project | meeting | how-to
status: active | draft | archived
tags: [topic-1, topic-2]
created: 2026-03-31
---
```

### File naming
- Lowercase with hyphens: `my-note-title.md`
- No spaces, no special characters
- Date-prefix for time-sensitive notes: `2026-03-31-meeting-notes.md`

### Linking
- Use `[[wikilinks]]` to connect related notes
- Prefer linking over duplicating content
- One idea per note (atomic notes)

### Length
- Under 500 lines per note
- If longer, split into linked sub-notes

---

## For Collaborators

This vault is personal but parts of it are designed to be shared:

- **`3-Resources/system-wiki/`** — Documentation of how the chris-os system works. Start here if you're learning the system.
- **`1-Projects/`** — Active project notes. If we're collaborating on a project, the relevant notes are here.

If you're Ashley or Garrett and need to understand the system, start with `3-Resources/system-wiki/index.md`.

---

## For AI Agents

Claude Code reads and writes to this vault via the `obsidian-vault-ops` skill and the `vault-maintenance` skill. The CLAUDE.md file at vault root provides navigation context. When adding or modifying notes:

- Always include frontmatter
- Follow the PARA classification (use the decision tree above)
- Link to related notes
- Keep notes atomic (one idea per file)
- Place uncertain items in `_inbox/` for human review rather than guessing the classification
