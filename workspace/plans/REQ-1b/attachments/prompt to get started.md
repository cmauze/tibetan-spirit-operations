# Claude Code multi-agent patterns, Notion migration, and subagent mastery

Claude Code's agent ecosystem has matured rapidly through early 2026, offering three distinct tiers of multi-agent coordination: **subagents** (single-session delegation), **Agent Teams** (multi-session swarms via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`), and the new `/batch` command for codebase-wide migrations. This report covers the current state of all three topics in full technical depth, with configuration snippets, file structures, and hard-won community patterns.

---

## Part 1: Agent Teams — file-based swarms with independent context windows

Agent Teams, shipped in Claude Code v2.1.32 (February 5, 2026), represent a fundamentally different architecture from subagents. Where subagents run inside a single session and report back to a parent, **teammates are independent Claude Code sessions** with their own 1M-token context windows, communicating through JSON files on disk. This makes them suitable for parallelizing large workloads where each agent needs substantial working memory.

### Enabling and configuring the feature

Three activation methods exist, in order of recommendation:

```json
// settings.json (recommended — persists across sessions)
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

```bash
# Shell environment variable
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Per-session CLI flag
claude --teammate-mode tmux
```

Display modes control how agents render in your terminal. **In-process** mode (default) runs all agents in one terminal — cycle between them with `Shift+Up/Down`. **Split-pane** mode spawns each agent in its own tmux or iTerm2 pane, which is strongly recommended for 3+ agents. Configure via `"teammateMode": "tmux"` in settings.json.

### The seven coordination primitives

Agent Teams expose exactly seven tool calls that form a complete coordination protocol:

| Primitive | Purpose |
|-----------|---------|
| `TeamCreate({team_name, description})` | Creates team directory structure and config |
| `Task({team_name, name, prompt, model})` | Spawns a new teammate as an independent session |
| `TaskCreate({subject, description, blockedBy})` | Creates a JSON task file with dependency tracking |
| `TaskList()` | Returns all tasks with current status |
| `TaskUpdate({taskId, status, owner})` | Claims or completes tasks (file locking prevents races) |
| `SendMessage({type, recipient, content})` | Inter-agent messaging — supports `message`, `broadcast`, `shutdown_request` |
| `TeamDelete()` | Cleans up all team files |

The coordination layer is entirely file-based. Tasks live at `~/.claude/tasks/{team-name}/` as numbered JSON files with three states: `pending`, `in_progress`, `completed`. Mailboxes sit at `~/.claude/teams/{team-name}/inboxes/{agent-id}.json`. Teammates poll their inbox and the task list, self-claim unassigned work, and update status through file operations with locking to prevent double-claiming.

```
~/.claude/
├── teams/
│   └── auth-refactor/
│       ├── config.json
│       └── inboxes/
│           ├── team-lead.json
│           ├── backend-agent.json
│           └── frontend-agent.json
├── tasks/
│   └── auth-refactor/
│       ├── 1.json      # {subject, description, status, owner, blockedBy}
│       ├── 2.json
│       └── 3.json
```

A critical architectural distinction: **teammates can message each other directly** — the lead is not required as intermediary. However, teammates do not inherit the lead's conversation history. Only explicit messages, task descriptions, and shared project files (CLAUDE.md, MCP servers) bridge context between agents.

### Task dependencies and messaging patterns

Tasks support a `blockedBy` field referencing other task IDs. Blocked tasks auto-unblock when their dependencies complete:

```javascript
TaskCreate({
  subject: "Implement login endpoint",
  description: "Build /api/auth/login with JWT...",
  blockedBy: ["1", "2"]  // Waits for schema + middleware tasks
})
```

Messaging follows four patterns depending on the coordination need:

```javascript
// Peer-to-peer: backend tells frontend types are ready
SendMessage({
  type: "message",
  recipient: "frontend-agent",
  content: "API types published at /types — you can import now."
})

// Broadcast: lead announces phase change
SendMessage({
  type: "broadcast",
  content: "All research complete. Moving to implementation phase."
})

// Shutdown coordination
SendMessage({ type: "shutdown_request" })
// Teammate finishes current work, then responds
SendMessage({ type: "shutdown_response" })
```

### Three hook events provide quality gates

Agent Teams add three lifecycle hooks beyond standard Claude Code hooks:

```json
{
  "hooks": {
    "TeammateIdle": [{
      "hooks": [{
        "type": "command",
        "command": "bash .claude/hooks/check-remaining-tasks.sh"
      }]
    }],
    "TaskCompleted": [{
      "hooks": [{
        "type": "command",
        "command": "bash .claude/hooks/run-tests.sh"
      }]
    }],
    "TaskCreated": [{
      "hooks": [{
        "type": "command",
        "command": "bash .claude/hooks/validate-task.sh"
      }]
    }]
  }
}
```

Exit code `0` allows the action to proceed. **Exit code `2`** sends stdout as feedback — for `TeammateIdle`, this keeps the teammate working; for `TaskCompleted`, it prevents completion and sends the test failure output back to the agent.

### Hard limitations as of March 2026

The feature carries ten confirmed constraints worth knowing before adoption:

- **No nested teams.** Teammates cannot spawn their own teams. Only the lead manages the team structure.
- **No session resumption.** `/resume` does not restore in-process teammates. After resuming, the lead may message agents that no longer exist.
- **One team per session.** Clean up before starting a new team.
- **No shared memory or context.** Agents only share information through explicit messages and task files. Teammates load project CLAUDE.md and MCP servers independently.
- **Shutdown can lag.** Teammates finish their current tool call before responding to shutdown.
- **Task status can drift.** Teammates sometimes fail to mark tasks completed, blocking dependents. Manual nudges may be needed.
- **Split panes require tmux or iTerm2.** Not supported in VS Code terminal, Windows Terminal, or Ghostty.
- **Permissions propagate from lead.** All teammates inherit the lead's permission settings.
- **No hard agent limit**, but practical diminishing returns appear beyond **5 teammates**. Token costs scale linearly, and coordination overhead grows.
- **Per-teammate model selection** is a community workaround (passing `model: "sonnet"` in the `Task()` call), not a first-class feature yet.

### The "plan first, parallelize second" pattern

Community consensus, documented across alexop.dev, Addy Osmani, and John Kim's 30 Tips, converges on a two-phase approach:

**Phase 1 — Plan mode.** Use `/plan` (Shift+Tab twice) for cheap, read-only codebase exploration. Claude generates a structured implementation plan. Review and refine it.

**Phase 2 — Hand plan to team.** The lead creates tasks from the plan and spawns teammates for parallel execution.

Key decomposition rules from production usage:

- **5-6 tasks per teammate** keeps agents productive without excessive coordination overhead
- **Never let agents touch the same files** — assign clear file or directory ownership per teammate
- **Embed full context in task descriptions** — teammates don't see the lead's conversation
- **Run lead on Opus for planning, teammates on Sonnet for execution** to optimize costs (~3-4x token cost vs single session for a 3-agent team)
- **Use delegate mode** (Shift+Tab to "delegate") to prevent the lead from implementing instead of delegating

### The research coordinator pattern

For spawning specialist researchers, the recommended pattern uses a skill definition:

```markdown
---
description: Research a problem using parallel specialist agents
allowed-tools: Task, WebSearch, WebFetch, Grep, Glob, Read, Write, Bash
---
# Research: $ARGUMENTS

## Instructions
Launch multiple subagents in parallel to gather information:

1. **Web Documentation Agent** — Search official docs, find best practices
2. **Stack Overflow Agent** — Find similar problems and highly-voted solutions  
3. **Codebase Explorer Agent** (type: Explore) — Search codebase for related patterns
4. **Standards Agent** — Research relevant RFCs, standards, and specifications

Synthesize all findings into a structured report with recommendations.
```

For Agent Teams specifically, the prompt pattern that works in production:

```
Create an agent team to research our migration from Express to Fastify.
One teammate on benchmarking performance differences,
one on analyzing our middleware compatibility,
one on reviewing our 47 route handlers for breaking changes.
Require plan approval before any agent begins work.
```

### Proven production examples

Real-world usage has been documented across several scales. Anthropic researchers used **16 agents over two weeks** (approximately $20,000 in tokens) to build a functional C compiler from scratch. A social media content production workflow generated a full week of platform-specific content in **15 minutes at $7.80** using strategist, researcher, copywriter, and reviewer agents. Heeki Park documented a product management cycle where agents handled spec writing, development, and testing in parallel — though with caveats about teammates occasionally getting stuck and requiring restarts.

Community tooling has emerged rapidly: `cs50victor/claude-code-teams-mcp` reimplements the protocol for any MCP client, `777genius/claude_agent_teams_ui` provides a Kanban board interface, and `panaversity/claude-code-agent-teams-exercises` offers eight structured exercises for learning the feature.

---

## Part 2: Notion to Obsidian migration via Claude Code and MCP

### The MCP server landscape for Notion access

Three tiers of Notion MCP servers exist, each suited to different migration scenarios:

**Official Notion Hosted MCP (recommended for interactive use):**
```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
# Then run /mcp in Claude Code to authenticate via OAuth
```
This server uses OAuth 2.0, requires a browser authentication flow, and provides the richest tool surface. It supports Streamable HTTP transport at `https://mcp.notion.com/mcp` or legacy SSE at `https://mcp.notion.com/sse`. The companion [Claude Code Notion Plugin](https://github.com/makenotion/claude-code-notion-plugin) bundles this server with pre-built skills and slash commands.

**Official Open-Source MCP (better for scripted migration):**
```json
{
  "mcpServers": {
    "notionApi": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": { "NOTION_TOKEN": "ntn_****" }
    }
  }
}
```
The `@notionhq/notion-mcp-server` package on npm uses bearer token authentication (no human in the loop), making it suitable for automated batch workflows. It is no longer actively maintained but remains functional.

**Third-party servers for specific needs:**

| Package | Key advantage |
|---------|---------------|
| `@suekou/mcp-notion-server` | Markdown conversion mode (`NOTION_MARKDOWN_CONVERSION=true`) that **dramatically reduces token usage** — critical for large migrations |
| `@ramidecodes/mcp-server-notion` | Full SDK wrapper with tools for Search, Databases, Pages, Blocks, Users, Comments |
| `notion-mcp-server` (awkoy) | Production-ready with batch operations and archive/restore support |

### The four MCP tools that drive migration

The migration workflow uses four core tools in sequence:

```bash
# 1. Discover all content — returns pages, databases, titles
notion-search(query="", query_type="internal")

# 2. Fetch database schema — returns data sources with collection:// IDs  
notion-fetch(id="https://notion.so/workspace/Database-URL")

# 3. Query database contents with existing view filters
notion-query-database-view(view_url="https://notion.so/.../db-id?v=view-id")

# 4. Fetch individual pages — returns enhanced Markdown
notion-fetch(id="page-uuid-or-url")

# 5. Extract comments (NOT included in standard Notion export)
notion-get-comments(page_id="uuid", include_all_blocks=true)
```

The `notion-fetch` tool returns Notion's enhanced Markdown format, which is close to but not identical to standard Markdown. For databases, `notion-fetch` reveals the schema with property names, types, and data source IDs — essential information for property-to-frontmatter mapping.

### Converting properties to YAML frontmatter

The frontmatter structure should map Notion property types to their Obsidian equivalents:

```yaml
---
title: "Feature: User Authentication"
status: "In Progress"           # Notion select → string
priority: "High"                 # Notion select → string
assignee: "[[John Smith]]"       # Notion person → wikilink
due_date: 2024-04-01             # Notion date → ISO date
tags: [feature, q2, auth]        # Notion multi-select → list
related_projects:                # Notion relation → wikilink list
  - "[[Project Alpha]]"
  - "[[Security Audit]]"
sprint: "Sprint 23"
notion-id: "abc123def456"        # Preserve for link resolution
notion-url: "https://notion.so/..." 
---
```

The mapping rules: Notion **select/multi-select** → YAML strings or lists. **Date** → ISO 8601. **Person** → `[[wikilink]]` to enable graph connections. **Relation** → list of `[[wikilinks]]` (critical for preserving the link graph). **Checkbox** → boolean. **Formula/rollup** → computed value as string, or use Dataview to recalculate dynamically.

### Databases should become folders with Dataview indexes

Each Notion database maps to a folder. Each row becomes a markdown file. An index file recreates the table view using Dataview:

```
Vault/
├── Databases/
│   ├── Tasks/
│   │   ├── Task-001.md         # Properties as YAML frontmatter
│   │   ├── Task-002.md
│   │   └── _index.md           # Dataview table query
│   └── Projects/
│       ├── Project-Alpha.md
│       └── _index.md
```

The index file that replaces a Notion table view:

````markdown
# Tasks Database

```dataview
TABLE status, priority, assignee, due_date
FROM "Databases/Tasks"
WHERE file.name != "_index"
SORT priority ASC
```
````

For two-way relations, ensure both files link to each other. Dataview can then query across relations with `WHERE contains(project, [[Project-Alpha]])`.

### Eight pitfalls that break migrations

**Broken internal links** are the most common failure. Notion exports URLs like `https://notion.so/Page-Title-2d41ab7b61d14cec...` instead of wikilinks, and appends 32-character UUIDs to filenames. Tools like `notion2obsidian` (recommended: `bunx notion2obsidian ./Export.zip ~/Obsidian/Vault --enrich --dataview`) handle this by building an ID map across all files in a two-pass scan, then rewriting all links.

**Expired images** are the second-most damaging issue. Notion-hosted images use temporary signed URLs that expire after export. The `--enrich` flag on notion2obsidian downloads covers, and the `obsidian-local-images-plus` plugin can download remaining external images locally. Notion MCP does **not** yet support file downloads.

**Missing comments** catch many migrators off guard. Notion's standard export files **do not include comments at all**. Extract them via `notion-get-comments` through MCP before migration, and embed them as blockquotes in the markdown.

**Database views** (table, board, calendar, gallery) have no direct Obsidian equivalent. Use Dataview for tables and lists, the Projects plugin for kanban boards, and the Calendar plugin for date views. Accept some fidelity loss.

**Nested page depth** creates unwieldy folder structures. Flatten where possible — Obsidian's graph view and backlinks replace deep hierarchy more effectively than nested folders.

**Duplicate filenames** are legal in Notion but not on filesystems. The notion2obsidian tool disambiguates with sequential suffixes and stores originals as aliases.

**Over-databasing** — as Dave Rupert noted, many Notion users created databases just for the table UI. During migration, evaluate each database: some should become simple markdown files rather than being recreated as Dataview databases.

**Notion callouts** use different syntax from Obsidian callouts. Conversion tools transform them to Obsidian's `> [!note]` format automatically.

### Mapping Notion structure to PARA methodology

The target vault structure for PARA (Projects, Areas, Resources, Archive):

```
Vault/
├── 1 Projects/          # Active projects with deadlines
│   ├── Website Redesign/
│   └── Q2 Launch/
├── 2 Areas/             # Ongoing responsibilities (no deadline)
│   ├── Health/
│   ├── Finance/
│   └── Work/
├── 3 Resources/         # Reference material and topics of interest
│   ├── Programming/
│   └── Design/
├── 4 Archive/           # Completed or inactive items
├── _templates/
├── _attachments/
├── _daily/
└── Home.md              # Dashboard with Dataview queries
```

The mapping logic: Notion **active project databases** → `1 Projects/`. **Team spaces and recurring responsibilities** → `2 Areas/`. **Wiki and knowledge base pages** → `3 Resources/`. **Completed or archived databases** → `4 Archive/`. The Home.md dashboard uses Dataview queries to surface active projects, pending tasks, and recently modified files — replicating Notion's dashboard functionality.

### The recommended two-track migration workflow

**Track A (MCP-driven, for selective/intelligent migration):**
Use Claude Code with the Notion MCP to read content, make intelligent decisions about PARA categorization, convert properties to frontmatter, and write files locally. Best for workspaces under ~200 pages where Claude's judgment adds value in reorganization.

**Track B (Export-based, for large workspaces):**
Export from Notion UI (Settings → Export → Markdown & CSV), run `bunx notion2obsidian ./Export.zip ~/Obsidian/Vault --enrich --dataview`, then use Claude Code to reorganize the converted files into PARA structure. Better for large workspaces where batch processing matters more than per-page intelligence.

For either track, extract comments via MCP before starting, as they're lost in standard exports.

---

## Part 3: Subagent patterns for large-scale codebase work

### Complete subagent frontmatter reference

Custom subagents live in `.claude/agents/` as markdown files with YAML frontmatter. The full set of available fields as of March 2026:

```yaml
---
name: security-reviewer           # Unique ID, lowercase + hyphens
description: "PROACTIVELY review code for security vulnerabilities"
                                    # "PROACTIVELY" triggers auto-invocation
tools: Read, Grep, Glob, Bash      # Allowlist (inherits all if omitted)
disallowedTools: NotebookEdit       # Denylist, removed from inherited set
model: sonnet                       # haiku | sonnet | opus | inherit
permissionMode: plan                # default | acceptEdits | dontAsk | 
                                    # bypassPermissions | plan
maxTurns: 25                        # Max agentic turns before stopping
skills:                             # Skill names to preload (full content injected)
  - deploy-checklist
  - rollback-procedures
mcpServers:                         # MCP servers by name or inline config
  - slack
  - name: pagerduty
    command: npx
    args: ["-y", "@pagerduty/mcp-server"]
hooks:                              # Lifecycle hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh"
  Stop:
    - hooks:
        - type: command
          command: "./scripts/notify-complete.sh"
memory: project                     # user | project | local
background: true                    # Run as background task
isolation: worktree                 # Git worktree isolation
color: blue                         # CLI output color
---

You are a senior security engineer. Review all changed files for...
```

Memory scopes determine where persistent agent memory is stored: `user` at `~/.claude/agent-memory/{name}/` (personal, not version-controlled), `project` at `.claude/agent-memory/{name}/` (shared, version-controlled), and `local` at `.claude/agent-memory-local/{name}/` (personal, not version-controlled).

Four built-in agent types ship with Claude Code: **`general-purpose`** (inherits model, all tools — the default), **`Explore`** (Haiku, read-only — fast codebase search), **`Plan`** (inherits model, read-only — pre-planning research), and **`claude-code-guide`** (inherits model, limited tools — answers Claude Code questions).

The invocation syntax was renamed from `Task()` to `Agent()` in v2.1.63, though `Task()` still works as an alias:

```
Agent(subagent_type="security-reviewer", prompt="Review the auth module for OWASP Top 10")
```

### Plan mode is powerful but not truly read-only

`claude --permission-mode plan` restricts Claude to read-only operations: `Read`, `LS`, `Glob`, `Grep`, `Agent`, `TodoRead/TodoWrite`, `WebFetch`, `WebSearch`, and `NotebookRead`. It blocks `Edit`, `MultiEdit`, `Write`, `Bash`, and state-modifying MCP tools.

The intended workflow — **Explore → Plan → Execute** — proceeds in three steps: start in plan mode, let Claude analyze the codebase and produce a structured plan, review the plan, then exit plan mode (Shift+Tab) for execution with confirmation prompts.

However, a critical caveat documented by multiple independent sources: **plan mode is prompt-based instruction, not a hard technical block.** As Sondera's analysis noted, "The plan mode prompt, like all prompts, is essentially a strong suggestion to the model." For true enforcement, add a `PreToolUse` hook that checks the permission mode and blocks write operations at the shell level.

Plan mode's key limitations: plans are **session-scoped** and disappear when the conversation ends, they are not collaborative (only the current user sees them), and there is no structured tracking of which plan steps have been completed during execution.

### Anthropic's own code review pattern sets the standard

The `plugins/code-review/commands/code-review.md` file in the Claude Code repository reveals Anthropic's production multi-agent code review approach:

**Step 1:** Launch a Haiku agent to return file paths for all relevant CLAUDE.md files.

**Step 2:** Launch four agents in parallel — two Sonnet agents audit CLAUDE.md compliance in parallel, one Opus agent scans for bugs (diff-only), and one Opus agent focuses on security issues and incorrect logic.

**Step 3:** For each issue found, launch parallel validation subagents (Opus for bugs, Sonnet for compliance violations).

**Step 4:** Filter out invalidated issues. **Step 5:** Output only HIGH SIGNAL issues — "Flag issues where the code will fail to compile or parse, will definitely produce wrong results."

This pattern — **fan-out for discovery, fan-out again for validation, then filter** — is the gold standard for large codebase review. It uses cheap models (Haiku) for file discovery, mid-tier (Sonnet) for compliance checks, and expensive models (Opus) only for bug detection where reasoning quality matters most.

### Three production-proven coordinator patterns

**Pattern A: PubNub's 3-stage pipeline** chains agents through a status queue. A PM agent reads an enhancement request and writes a spec, an architect agent validates the design and produces an ADR (Architecture Decision Record), and an implementer agent builds code and tests. A `_queue.json` file tracks status flow: `READY_FOR_ARCH → READY_FOR_BUILD → DONE`. Human-in-the-loop hooks print the next command for the human to paste, maintaining control over phase transitions.

```
.claude/
  agents/
    pm-spec.md
    architect-review.md
    implementer-tester.md
  hooks/
    on-subagent-stop.sh
enhancements/
  _queue.json
docs/claude/
  working-notes/
  decisions/
```

**Pattern B: Domain-parallel routing** spawns specialists by codebase domain. The lead analyzes the task and fans out to a frontend agent (React components, UI state), a backend agent (API routes, business logic), and a database agent (schema, migrations, queries). Each agent owns their domain completely with no file overlap.

**Pattern C: The Master-Clone alternative,** advocated by Shrivu Shankar (blog.sshh.io), argues against custom subagents entirely: "Custom subagents are a brittle solution. Give your main agent the context in CLAUDE.md and let it use its own Task/Explore feature to manage delegation." This approach lets the main agent decide dynamically when and how to delegate, rather than pre-defining rigid workflows. The debate between pre-defined specialists and dynamic delegation remains active in the community.

### Context management determines success at scale

Context is the fundamental constraint for large codebase work. Subagents are the primary mitigation: since they run in separate context windows and report back summaries, the parent agent's context stays clean. Official Anthropic guidance states: "When Claude researches a codebase it reads lots of files, all of which consume your context. Subagents run in separate context windows and report back summaries."

Five context management techniques form the current best practice stack:

- **`/compact <instructions>`** — summarize conversation with focus guidance, e.g., `/compact Focus on the API changes`. The shanraisshan repo warns: "Do manual /compact at max 50% context usage — avoid the agent dumb zone."
- **`/clear`** — full context reset between unrelated tasks. Preferred over auto-compaction for task switches.
- **`/btw`** — quick question in a dismissible overlay that never enters conversation history.
- **Document & Clear pattern** — have Claude dump its plan and progress to a `.md` file, run `/clear`, then start a new session reading that file. This gives a fresh context window with full knowledge transfer.
- **Subagent model routing** via `CLAUDE_CODE_SUBAGENT_MODEL` environment variable: run the coordinator on Opus for reasoning quality and subagents on Sonnet or Haiku for cost efficiency.

```bash
export CLAUDE_CODE_SUBAGENT_MODEL="claude-sonnet-4-5-20250929"
```

### The /batch command handles codebase-wide transformations

Introduced in v2.1.63, `/batch` automates the Explore → Plan → Execute loop for migrations and large-scale refactoring:

```bash
/batch migrate from React class components to hooks
/batch replace all uses of lodash with native equivalents
/batch add type annotations to all untyped function parameters
```

It works in three phases. **Phase 1 (Research and Plan):** enters plan mode, launches Explore agents, decomposes work into 5-30 self-contained units. **Phase 2 (Parallel Execution):** spawns one background agent per unit with `isolation: "worktree"` — each agent's prompt is fully self-contained, workers run `/simplify` on changes, execute tests, commit, push, and create PRs. **Phase 3 (Track Progress):** a status table updates as agents complete, with a final summary like "22/24 units landed as PRs."

Boris Cherny (Claude Code creator, March 30, 2026) described the scale: "/batch interviews you, then fans out work to as many worktree agents as it takes — dozens, hundreds, even thousands."

### Tool categorization per agent role

The VoltAgent/awesome-claude-code-subagents repository provides a clean categorization:

- **Read-only agents** (reviewers, auditors): `Read, Grep, Glob`
- **Research agents** (analysts): `Read, Grep, Glob, WebFetch, WebSearch`
- **Code writers** (developers): `Read, Write, Edit, Bash, Glob, Grep`
- **Documentation agents**: `Read, Write, Edit, Glob, Grep, WebFetch, WebSearch`

This maps directly to the `tools` frontmatter field. The principle is minimal privilege: give each agent only the tools it needs. A security reviewer should never have `Write` or `Bash`. A documentation agent needs `WebFetch` for reference lookups but shouldn't need `Bash`.

## Conclusion

The three topics converge on a single architectural insight: **effective multi-agent work in Claude Code is fundamentally about context management and clear ownership boundaries.** Agent Teams solve the problem of parallel execution with independent context windows and file-based coordination. Notion-to-Obsidian migration succeeds when you match the MCP server to your automation needs (hosted for interactive, open-source for batch) and accept that some Notion fidelity will be lost in exchange for Obsidian's flexibility. Subagent patterns for large codebases work best when they follow Anthropic's own approach: fan-out for discovery with cheap models, validate findings with expensive models, and filter aggressively for signal.

The most actionable pattern across all three topics is **"plan first, parallelize second"** — whether you're decomposing a team's work, planning a migration, or reviewing a codebase. Start in plan mode with read-only exploration, produce a concrete plan, review it, then hand it to parallel agents for execution. This prevents the most common failure mode: agents doing redundant or conflicting work because they were launched without a shared understanding of the task.