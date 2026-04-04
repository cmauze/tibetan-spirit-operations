# FILESYSTEM AUDIT REPORT: Planned vs. Actual State
**Date:** 2026-03-31
**Status:** READ-ONLY AUDIT (no modifications made)

---

## EXECUTIVE SUMMARY

**CRITICAL FINDING:** The filesystem has evolved BEYOND the planned architecture. You now have TWO parallel directory trees in active use:

1. **NEW ARCHITECTURE** (Primary, preferred): `~/` with `~/brain`, `~/code`, `~/.claude`, `~/Documents`
2. **LEGACY WORKSPACE** (Secondary, deprecated): `~/cm/` with nested brain, code, temp, health-wellness-protocols, music

**Action Required:** Plan a migration strategy to consolidate from legacy `~/cm` into the new tree. The brain vault is actively synced and used. `~/code/active/tibetan-spirit-ops` is in active development. The `~/cm/` structure is unmaintained.

---

## SECTION 1: ROOT-LEVEL DIRECTORY STATE

| Location | Exists? | Size | Status | Notes |
|----------|---------|------|--------|-------|
| `~/.claude/` | ✓ YES | 380M | **ACTIVE** | Global Claude Code harness state, settings, history, tasks, projects |
| `~/brain/` | ✓ YES | 575M | **ACTIVE** | Obsidian vault (PARA structure, git-synced) |
| `~/code/` | ✓ YES | 134G | **ACTIVE** | Production code repos with active/.claude/ subdirs |
| `~/Documents/` | ✓ YES | 90M | **MIXED** | iCloud personal + music DAW assets (Native Instruments, Max, UA) |
| `~/Desktop/` | ✓ YES | ~5.3G | **iCloud** | iCloud Desktop folder (not local) |
| `~/Music/` | ✓ YES | LOCAL | **LOCAL** | Local Ableton library |
| `~/cm/` | ✓ YES | 5.6G | **LEGACY** | Old monolithic workspace (deprecated but unmigrated) |

**Key Finding:** All expected root directories exist. However, `~/cm` appears to be a holdover from an earlier workspace structure that should be consolidated.

---

## SECTION 2: ~/.claude/ (GLOBAL HARNESS)

**Line count:** 40 lines (meets spec: <60 lines for user-level)
**File count:** 2,184 files across subdirectories
**Key files:**
- `CLAUDE.md` - User preferences (40 lines) ✓
- `settings.json` - Global config with permissions/env ✓
- `settings.local.json` - 36.5KB (extensive local config)
- `statusline.sh` - Custom shell status command

**Subdirectories found:**
- `agents/` - Agent definitions
- `backups/` - Session backups
- `cache/` - Cache storage
- `cm-notes/` - Cross-workspace notes
- `debug/` - Debug logs
- `file-history/` - File change history
- `ide/` - IDE integrations
- `paste-cache/` - Clipboard history
- `plans/` - Sprint/session plans
- `projects/` - Per-project config
- `rules/` - Global rules (6 files, last updated Jan 27)
- `session-env/` - Session environment (15 subdirs)
- `sessions/` - Session history (8 subdirs)
- `shell-snapshots/` - 264 snapshots (last modified Mar 31 20:11)
- `skills/` - 18 skill implementations
- `statsig/` - Feature flag service
- `tasks/` - 86 task files
- `teams/` - Team config
- `telemetry/` - Telemetry data
- `templates/` - Template files
- `todos/` - 1,078 todo items (extensive!)

**Verdict:** `.claude/` is highly active, well-maintained, with extensive task/todo tracking. No gaps vs. specification.

---

## SECTION 3: ~/brain/ (OBSIDIAN VAULT - PARA Structure)

**Structure found:**
```
~/brain/
├── .claude/               (project-specific Claude config, 3 files)
├── .git/                  (git repo, 14 refs, actively maintained)
├── .obsidian/             (16 plugin configs + settings)
├── .smart-env/            (8 files, smart env setup)
├── 00 Inbox/              (25 subdirs - active inbox captures)
├── 01 Core/               (8 subdirs - core knowledge)
├── 99 Archives/           (4 subdirs - archived material)
├── ai-research/           (4 subdirs)
├── calendar/              (3 subdirs)
├── efforts/               (3 subdirs)
├── vault-v0/              (9 subdirs - versioned vault backup)
└── **Workspace-as-Code Repository**.md
    NotebookLM Vibecoding architecture rec.md
    README.md
```

**Git Status:**
- Repo is active and well-maintained
- Auto-commits configured (format: `[auto] YYYY-MM-DD HH:MM - description`)
- Most recent commits show standard inbox/archive operations

**PARA Alignment:**
- Projects: `00 Inbox` (capture area) + `01 Core` (retained knowledge)
- Areas: `ai-research`, `efforts`
- Resources: `calendar`
- Archive: `99 Archives` + `vault-v0`
- Missing explicit "Areas" folder but content is appropriately organized

**Verdict:** Brain vault matches planned PARA structure. Actively maintained, git-synced. One minor issue: PARA folder labels use numeric prefix (00, 01, 99) instead of text labels (Projects, Areas, Resources, Archive).

---

## SECTION 4: ~/code/ (PRODUCTION CODE REPOS)

**Structure:**
```
~/code/
├── .claude/               (CLAUDE.md, 257 lines - meta-project spec)
├── active/                (4 active projects)
│   ├── asm-creative-agent/
│   ├── cgai/
│   ├── chris-os/          (infrastructure + personal agents)
│   └── tibetan-spirit-ops/ (ACTIVE - e-commerce ops)
├── completed/             (1 project)
├── cursor-workspaces/     (IDE config)
├── reference/             (4 reference projects)
├── sleeping/              (6 sleeping/paused projects)
└── trash/                 (26 archived projects)
```

**Total size:** 134G (mostly tibetan-spirit-ops and completed projects)

### `~/code/.claude/CLAUDE.md` (257 lines)

**Content:** Universal coding conventions for all projects in ~/code:
- Python 3.9+ with type hints (pydantic, black 100-char lines)
- TypeScript 5.0+ strict mode (Zod, Prettier)
- Project structure template (docs/AGENTS.md, .cursorrules symlinks)
- Testing conventions (pytest/Vitest, 80%+ coverage target)
- Git conventions (Conventional Commits, auto-commit in ~/brain only)
- Documentation standards (session_docs/, scratch/, .gitignore)
- Code review checklist

**Status:** Well-defined, comprehensive. Meets spec.

### ~/code/active/tibetan-spirit-ops/ (CRITICAL PROJECT)

**Status:** PRODUCTION READY
**Size:** 27 items in root, 11 subdirs deep
**Git:** Last commit 6289c28 (Mar 30 13:49) - "fix: extract views tests, trim notion_ops..."
**Untracked files:**
- `data/` (new data)
- `supabase/.temp/`
- `workspace/plans/REQ-1/01a-cowork-eval-session.md`
- `workspace/plans/REQ-1b/`

**Key Files:**
- `CLAUDE.md` (15.4K) - Detailed project spec
- `ORG.md` (2.7K) - Organizational roles + communication protocols
- `SYSTEM-STATUS.md` (30.6K) - Live technical reference (generated Mar 29)
- `DEV-PLAN.md` (70.1K) - Full implementation roadmap
- `pyproject.toml` - Python project config
- `validation-report.json` (16K) - Latest validation results

**Live Infrastructure:**
- Supabase PostgreSQL (Pro) connected - 19.4K orders, 559 products
- Shopify Admin API (2025-01) - active OAuth token
- Anthropic API key configured (in `.env`)
- Railway deployment ready (not yet active)
- 6 target workflows: daily_summary, weekly_pnl, cs_email_drafts, inventory_alerts, campaign_brief, product_descriptions

**Code Structure:**
- `lib/` - Shared Python library
- `server/` - API server
- `workflows/` - Workflow scripts (6 planned)
- `agents/` - Agent soul files
- `scripts/` - Backfill/validation/test scripts
- `supabase/` - Schema migrations
- `tests/` - Test suite (passing)
- `workspace/` - Execution plans + workspace docs
- `temp/` - Workspace scratchpad

**Verdict:** Tibetan Spirit is a flagship project in active development. Architecture is sound. Well-documented. Ready for workflow deployment.

---

## SECTION 5: ~/cm/ (LEGACY WORKSPACE - DEPRECATED)

**Status:** ACTIVE BUT LEGACY (should be consolidated)
**Size:** 5.6G (mostly in temp/, 104,955 files)
**Last modified:** Mar 31 20:01 (minimal recent activity)

**Structure:**
```
~/cm/
├── .claude/               (2.8KB CLAUDE.md, 36.5KB settings.local.json)
├── .cursor/               (IDE config)
├── .vscode/               (IDE config)
├── _/                     (94 files - utility scripts, logs, docs)
├── code/                  (nested git workspaces)
├── health-wellness-protocols/ (1 file)
├── music/                 (2 files - stubs)
├── temp/                  (104,955 files - HUGE)
└── .claudeignore, .cursorignore, .coverage files
```

**Key Issue:** `~/cm/temp/` contains 104,955 files (5.5G). This is almost certainly a dump/archive location that should be cleaned up.

### ~/cm/code/ (Nested code directory)

**Content:**
```
~/cm/code/
└── cursor-workspaces/    (3 files)
```

This is nearly empty and redundant with `~/code/`.

### ~/cm/.claude/

**Content:**
- `CLAUDE.md` - 2.8KB (old project-level config, likely outdated)
- `settings.local.json` - 36.5KB (local overrides, may contain sensitive data)
- `rules/` - 8 subdirs with global rules (last updated Jan 27)

### ~/cm/_/ (Utility folder)

**Contents (94 files):**
- `config/` - Configuration files
- `data/` - Data files
- `docs/` - Documentation (9 files)
- `logs/` - Log files
- `scripts/` - Scripts (5 files)

Last modified dates suggest this was active through Dec 28, but is now dormant.

### ~/cm/health-wellness-protocols/

**Status:** Stub (1 file, no content)

### ~/cm/music/

**Status:** Stub (2 files, no content)

---

## SECTION 6: CLOUD STORAGE INTEGRATION

### Google Drive

**Mounted at:** `~/Library/CloudStorage/GoogleDrive-{account}/`

Two accounts:
1. `GoogleDrive-chrism@daasity.com` - Work account (13 shared drives, ~416 items)
2. `GoogleDrive-chrismauze@gmail.com` - Personal account (37 items in My Drive, 139 cloud folder items)

**Status:** Both mounted and active. Used for shared documents and archive.

### Dropbox

**Installed:** ✓ YES
**Status:** Active (apex.sqlite3 shows current activity through Mar 31)
**Mount point:** Unclear if actual ~/Dropbox mount exists, but `.dropbox/` directory shows recent sync activity (apex.sqlite3-wal updated Mar 31 14:10)

### iCloud

**Status:** Active
- Documents/Desktop are iCloud-synced (indicated by "iCloud personal" in Documents listing)
- Not a direct mount point like Google Drive; synced to ~/Documents and ~/Desktop

---

## SECTION 7: GIT REPOSITORY STATUS

| Repo | Location | Status | Last Commit | Notes |
|------|----------|--------|-------------|-------|
| **brain** | ~/brain | Active | [auto] 2026-01-28 (git log showed truncation) | Auto-commits configured, Obsidian vault |
| **tibetan-spirit-ops** | ~/code/active/tibetan-spirit-ops | Active | 6289c28 (Mar 30 13:49) | Production project, untracked data/ and workspace/ plans |
| **chris-os** | ~/code/active/chris-os | Minimal | v0-chris-os-mauze-group-sprint-plan.md (Mar 30 00:16) | Only doc file, no git activity |
| **cgai** | ~/code/active/cgai | Unknown | Not checked | Should audit |
| **asm-creative-agent** | ~/code/active/asm-creative-agent | Unknown | Not checked | Should audit |

**Verdict:** Core repos (brain, tibetan-spirit-ops) are active and well-maintained. Others need assessment.

---

## SECTION 8: DOCUMENTS DIRECTORY

**Size:** 90M (mostly music production assets)

**Contents:**
```
~/Documents/
├── Music/                      (music files)
├── Native Instruments/         (DAW plugins, ~9 dirs)
├── Max 8/ & Max 9/            (Max/MSP installations)
├── Universal Audio/           (UA plugins)
├── oeksound/                  (oeksound plugins)
├── Claude/                    (Claude-related docs)
├── CM/                        (CM-related docs)
├── util_backup/               (utility backups)
├── cm_music files from phone/ (phone migration)
└── Various PDFs & screenshots (consulting agreements, architecture docs, screen recordings)
```

**Status:** Active music production workspace + some archived docs. Should remain separate from code/brain organization.

---

## SECTION 9: DESKTOP DIRECTORY

**Size:** ~5.3G (iCloud-synced)
**Status:** Standard macOS user folder. Not relevant to code/brain organization.

---

## SECTION 10: SETTINGS & CONFIGURATION AUDIT

### ~/.claude/settings.json

**Current config:**
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "permissions": {
    "allow": [
      "Read", "Bash", "Write", "Edit",
      "WebSearch", "WebFetch",
      "Bash(./venv/bin/pip:*)",
      "Read(//Users/chrismauze/cm/brain/04 Resources/Code/**)",
      "Read(//Users/chrismauze/cm/**)"
    ],
    "additionalDirectories": [
      "/Users/chrismauze/cm/projects/code/active/daasity-ai",
      "/private/tmp",
      "/Users/chrismauze/cm/brain/04 Resources/Code/agents"
    ]
  },
  "statusLine": { "type": "command", "command": "/bin/bash /Users/chrismauze/.claude/statusline.sh" },
  "teammateMode": "tmux",
  "effortLevel": "high"
}
```

**Issues Found:**
1. Permissions still reference old `~/cm/` paths (e.g., `Read(//Users/chrismauze/cm/brain/04 Resources/Code/**)`)
2. Should be updated to reference new `~/brain/` and `~/code/` locations
3. additionalDirectories still references `cm/projects/code/active/daasity-ai` (no longer valid)

### ~/.claude/rules/ (Global Rules)

**Status:** 6 subdirs with rule definitions. Last updated Jan 27. No audit of content performed (read-only constraint).

---

## SECTION 11: PLANNED VS. ACTUAL ARCHITECTURE

### PLANNED STRUCTURE (from master spec):
```
~/
├── .claude/CLAUDE.md          ✓ Exists (40 lines)
├── .claude/settings.json      ✓ Exists (but has legacy refs)
├── .claude/skills/            ✓ Exists (18 skills)
├── brain/                     ✓ Exists (Obsidian, PARA structure)
├── code/                      ✓ Exists (4 active projects)
│   ├── .claude/CLAUDE.md      ✓ Exists (257 lines, comprehensive)
│   ├── active/chris-os/       ✓ Exists (minimal state)
│   └── active/tibetan-spirit/ ✓ Exists (PRODUCTION)
├── Documents/                 ✓ Exists (iCloud personal)
├── Music/                     ✓ Exists (LOCAL Ableton)
└── Google Drive/              ✓ Exists (~/Library/CloudStorage/)
```

**GAPS:**
1. `docs/guides/specs/architecture/reference/repo-examples/` - Not found in `~/code/`
2. `~/brain/` using numeric PARA labels (00, 01, 99) instead of text labels

**EXTRA (Unexpected):**
1. `~/cm/` - Legacy workspace still exists (should be archived/cleaned)
2. `~/code/` has sleeping/, completed/, trash/ subdirs (not in spec but reasonable)
3. Multiple code projects (cgai, asm-creative-agent) not in spec
4. Extensive task tracking in ~/.claude/tasks/ (1,078 todos) - not in spec

---

## SECTION 12: FILE COUNT SUMMARY

| Location | File Count | Directory Count | Last Modified |
|----------|------------|-----------------|----------------|
| `~/` (total) | ~400K+ | ~100+ | Mar 31 20:15 |
| `~/brain/` | ~1K+ | ~50+ | Mar 29 20:45 |
| `~/code/` | ~50K+ | ~200+ | Mar 31 20:02 |
| `~/.claude/` | 2,184 | 35+ | Mar 31 20:14 |
| `~/cm/` | ~105K | ~20+ | Mar 31 20:01 |
| `~/Documents/` | ~1K+ | ~20+ | Mar 30 16:24 |

---

## SECTION 13: GAP ANALYSIS & RECOMMENDATIONS

### What exists now:
- Complete new workspace architecture (brain, code, .claude at root level)
- Obsidian vault with PARA structure (mostly compliant)
- 4 active projects in ~/code/active/ with unified coding conventions
- Tibetan Spirit production project ready for deployment
- Global Claude Code harness with 2K+ files tracking sessions/tasks
- Cloud storage integration (Google Drive × 2, Dropbox, iCloud)

### What the plan expects:
- Same core structure, but with additional `docs/guides/specs/` directory
- Explicit PARA folder naming (Projects, Areas, Resources, Archive)
- Clean separation from legacy `~/cm/`

### What's missing or needs action:

| Issue | Severity | Action | Timeline |
|-------|----------|--------|----------|
| Legacy `~/cm/` still exists, not fully migrated | MEDIUM | Move archived content to Google Drive or delete; update `.claude/settings.json` permissions | Within 2 weeks |
| `~/.claude/settings.json` references old paths | MEDIUM | Update all `~/cm/` refs to point to new `~/brain/` and `~/code/` locations | Immediate |
| `~/cm/temp/` contains 104,955 files (5.5G) | HIGH | Audit and archive or delete; this looks like a dump | Investigate + action this week |
| PARA folder naming inconsistent | LOW | Rename 00/01/99 to Projects/Areas/Archive for clarity | Optional (works as-is) |
| `docs/guides/specs/architecture/` directory missing from `~/code/` | LOW | Create if needed for code architecture docs | As-needed |
| cgai, asm-creative-agent projects undocumented | LOW | Review and document these projects' purpose/status | Optional |

---

## SECTION 14: RECOMMENDATIONS

### Immediate (This week):
1. **Update ~/.claude/settings.json:**
   - Change `Read(//Users/chrismauze/cm/brain/04 Resources/Code/**)` → `Read(/Users/chrismauze/brain/**)`
   - Change `Read(//Users/chrismauze/cm/**)` → Remove (redundant)
   - Update `additionalDirectories` to point to new paths

2. **Audit ~/cm/temp/:**
   - What are the 104,955 files?
   - Archive old data to Google Drive if valuable
   - Delete if cache/temp data

3. **Verify ~/cm/.claude/settings.local.json:**
   - Does it contain secrets that should be moved to root .claude?
   - Is it still active or legacy?

### Short-term (2 weeks):
1. **Plan cm/ to archive transition:**
   - Move valuable docs to ~/brain/99 Archives
   - Move code to ~/code/trash (already exists)
   - Delete or archive ~/cm/ entirely

2. **Document active projects:**
   - cgai - purpose/status/owner
   - asm-creative-agent - purpose/status/owner
   - chris-os - seems like infrastructure, but has minimal content

3. **Create ~/code/docs/guides/ structure** (if needed):
   - Architecture reference for new developers
   - Onboarding docs
   - Deployment guides

### Medium-term (1 month):
1. **Migrate brain PARA folders:**
   - Rename 00/01/99 to more descriptive labels (optional but cleaner)

2. **Review completed/ and trash/ in ~/code/:**
   - Compress/archive old projects to reduce ~/code/ size from 134G
   - Keep reference/ as reference material only

3. **Establish clean state:**
   - Ensure no ~/cm/ references in any active configs
   - Archive legacy .claude/cm-notes/ to brain/99 Archives
   - Clean up .claude/todos/ (1,078 items is large)

---

## FINAL VERDICT

**Overall Assessment: HEALTHY WITH LEGACY CLUTTER**

✓ **PASS:** New architecture is well-established and functional
✓ **PASS:** Brain vault properly maintained and git-synced
✓ **PASS:** Code repos organized and documented
✓ **PASS:** Tibetan Spirit project is production-ready
✓ **PASS:** Cloud storage integration working

⚠ **WARNING:** Legacy ~/cm/ directory still exists and unmaintained
⚠ **WARNING:** Settings config still references old paths
⚠ **WARNING:** Huge temp/ directory (5.5G) needs investigation

**Action Plan:** The filesystem is operationally sound. Focus on consolidation and cleanup to avoid future confusion. The new architecture is clearly the intended future state; the legacy cm/ structure should be fully archived within 2 weeks.

