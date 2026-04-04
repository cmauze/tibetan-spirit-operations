# Claude Code Features & Community Best Practices: Comprehensive Research Report

**Date:** 2026-03-31
**Purpose:** Inform the design of a personal AI operating system built on Claude Code
**Confidence baseline:** High -- sourced primarily from official Anthropic documentation (code.claude.com/docs) and verified community repositories

---

## Executive Summary

- **Skills are the primary extension mechanism.** The `.claude/skills/` system with SKILL.md frontmatter provides semantic discovery, progressive disclosure, and subagent execution -- directly replacing the older `.claude/commands/` pattern while remaining backward-compatible.
- **Hooks provide deterministic guarantees.** Unlike CLAUDE.md instructions (advisory, ~80% adherence), hooks execute shell commands at lifecycle points with 100% reliability. Four hook types exist: command, HTTP, prompt-based (LLM evaluation), and agent-based (multi-turn verification).
- **Agent teams and subagents are distinct patterns.** Subagents run within a session for focused delegation; agent teams coordinate across independent sessions with shared task lists and inter-agent messaging. Teams are experimental but stable enough for research/review workflows.
- **CLAUDE.md best practices have crystallized.** Official guidance recommends under 200 lines per file, aggressive use of `.claude/rules/` for modular organization, and skills for domain-specific knowledge -- keeping CLAUDE.md lean.
- **The community ecosystem is maturing rapidly.** The shanraisshan/claude-code-best-practice repo (28.8k stars) documents 87 actionable tips; Anthropic's own anthropics/skills repo (108k stars) provides the canonical skill format and production reference implementations.

---

## Methodology

**Primary sources:** Official Anthropic documentation at code.claude.com/docs (skills, hooks-guide, hooks, sub-agents, agent-teams, memory, best-practices, headless). All pages fetched and analyzed in full on 2026-03-31.

**Secondary sources:** Community GitHub repositories (shanraisshan/claude-code-best-practice, ChrisWiles/claude-code-showcase, hesreallyhim/awesome-claude-code, anthropics/skills, travisvn/awesome-claude-skills, ComposioHQ/awesome-claude-skills), plus Anthropic platform documentation (platform.claude.com skill authoring best practices).

**Approach:** Each topic was researched via web search, then primary documentation was fetched and analyzed in full. Findings were cross-referenced between official docs and community patterns.

---

## 1. Claude Code Skills System

### Current State

Skills are Claude Code's primary extension mechanism, following the open [Agent Skills](https://agentskills.io) standard adopted by OpenAI Codex, GitHub Copilot, Cursor, and others. Custom commands (`.claude/commands/`) are fully merged into skills -- existing command files continue to work, but skills add frontmatter control, supporting files, and auto-discovery.

### SKILL.md Format

Every skill is a directory containing a required `SKILL.md` file with two parts:

```yaml
---
name: my-skill          # lowercase + hyphens, max 64 chars, becomes /slash-command
description: What this does and when to use it. Front-load key use case.
                        # Max 1024 chars (platform) / 250 chars displayed (Claude Code)
disable-model-invocation: false  # true = manual /invoke only
user-invocable: true             # false = hidden from / menu, Claude-only
allowed-tools: Read, Grep, Glob  # restrict tool access
model: sonnet                    # sonnet|opus|haiku|inherit|full-model-id
effort: high                     # low|medium|high|max
context: fork                    # runs in isolated subagent
agent: Explore                   # which subagent type when context: fork
hooks: {}                        # lifecycle hooks scoped to this skill
paths:                           # glob patterns limiting auto-activation
  - "src/api/**/*.ts"
shell: bash                      # bash (default) or powershell
argument-hint: "[issue-number]"  # autocomplete hint
skills: []                       # preloaded skills (for subagent execution)
---

Markdown instructions Claude follows when skill is invoked.
```

**Key insight on `description`:** This is the most important field. Claude uses it for semantic matching to decide when to auto-load the skill. Write in third person. Front-load the key use case. Descriptions over 250 characters are truncated in the skill listing. The description budget scales at 1% of context window (fallback: 8,000 chars). Override with `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var.

### Discovery and Loading

1. **At session start:** Only skill names and descriptions are loaded into context (not full content).
2. **On invocation:** Full SKILL.md content loads when the user types `/skill-name` or Claude determines relevance.
3. **Nested discovery:** Skills in subdirectory `.claude/skills/` are discovered when Claude works with files in those subdirectories (monorepo support).
4. **Priority order:** enterprise > personal (`~/.claude/skills/`) > project (`.claude/skills/`) > plugin (namespaced as `plugin-name:skill-name`).
5. **Additional directories:** `.claude/skills/` in `--add-dir` paths are loaded and support live change detection.

### Directory Structure

```
my-skill/
  SKILL.md              # Required - overview and navigation
  reference.md          # Detailed API docs (loaded when needed)
  examples.md           # Usage examples (loaded when needed)
  template.md           # Template for Claude to fill in
  scripts/
    validate.sh         # Script Claude can execute (not loaded into context)
    helper.py           # Utility script
```

### Invocation Control Matrix

| Frontmatter                       | User can invoke | Claude can invoke | Context behavior                                      |
|:----------------------------------|:----------------|:------------------|:------------------------------------------------------|
| (default)                         | Yes             | Yes               | Description always in context, full skill on invoke   |
| `disable-model-invocation: true`  | Yes             | No                | Description NOT in context, loads on manual invoke    |
| `user-invocable: false`           | No              | Yes               | Description always in context, loads when relevant    |

### String Substitutions

| Variable               | Description                          |
|:-----------------------|:-------------------------------------|
| `$ARGUMENTS`           | All arguments passed to the skill    |
| `$ARGUMENTS[N]` / `$N`| Positional argument (0-based)        |
| `${CLAUDE_SESSION_ID}` | Current session ID                   |
| `${CLAUDE_SKILL_DIR}`  | Directory containing SKILL.md        |

### Dynamic Context Injection

The `` !`command` `` syntax runs shell commands as preprocessing before content reaches Claude:

```yaml
---
name: pr-summary
context: fork
agent: Explore
---
PR diff: !`gh pr diff`
Changed files: !`gh pr diff --name-only`
```

### Progressive Disclosure Pattern (Critical)

This is the single most important skill authoring technique:

1. **Keep SKILL.md under 500 lines.** It is the table of contents, not the encyclopedia.
2. **Reference supporting files** with relative links: `See [reference.md](reference.md)`.
3. **Keep references one level deep.** Claude partially reads nested references (may use `head -100`).
4. **Organize by domain** for multi-domain skills (e.g., `reference/finance.md`, `reference/sales.md`).
5. **Include a ToC** in reference files longer than 100 lines.

### Key Patterns to Adopt

1. **Lean CLAUDE.md + rich skills.** Move all domain-specific knowledge into skills. CLAUDE.md should contain only universal project rules.
2. **`disable-model-invocation: true` for side-effect workflows.** Deploy, commit, release skills should be manual-only.
3. **`context: fork` for research skills.** Keeps exploration out of main conversation context.
4. **Skills with preloaded skills in subagents.** The `skills:` frontmatter field injects full skill content into subagent context at startup.
5. **Evaluation-driven development.** Create test scenarios BEFORE writing extensive skill content.

### Anti-Patterns to Avoid

- Putting all knowledge in SKILL.md instead of using supporting files (context bloat).
- Deeply nested file references (Claude may only preview with `head -100`).
- Vague descriptions ("Helps with documents") -- Claude cannot match semantically.
- Windows-style paths (always use forward slashes).
- Offering multiple tool choices without a default ("use pypdf or pdfplumber or PyMuPDF...").
- Time-sensitive content (use "old patterns" collapsible sections instead).

---

## 2. Claude Code Hooks

### Current State

Hooks are deterministic shell commands (or HTTP/prompt/agent handlers) that execute at specific lifecycle points. Unlike CLAUDE.md instructions which are advisory, hooks guarantee execution -- they are the enforcement layer.

### Hook Events (Complete List)

| Event                | When it fires                                           | Matcher filters on      |
|:---------------------|:--------------------------------------------------------|:------------------------|
| `SessionStart`       | Session begins or resumes                               | startup/resume/clear/compact |
| `UserPromptSubmit`   | User submits a prompt                                   | (no matcher)            |
| `PreToolUse`         | Before tool call (can block)                            | tool name               |
| `PermissionRequest`  | Permission dialog appears                               | tool name               |
| `PostToolUse`        | After tool call succeeds                                | tool name               |
| `PostToolUseFailure` | After tool call fails                                   | tool name               |
| `Notification`       | Claude needs attention                                  | notification type       |
| `SubagentStart`      | Subagent spawned                                        | agent type              |
| `SubagentStop`       | Subagent finishes                                       | agent type              |
| `TaskCreated`        | Task created via TaskCreate                             | (no matcher)            |
| `TaskCompleted`      | Task marked complete                                    | (no matcher)            |
| `Stop`               | Claude finishes responding                              | (no matcher)            |
| `StopFailure`        | Turn ends due to API error                              | error type              |
| `TeammateIdle`       | Agent team teammate going idle                          | (no matcher)            |
| `InstructionsLoaded` | CLAUDE.md or rules file loaded                          | load reason             |
| `ConfigChange`       | Config file changes during session                      | config source           |
| `CwdChanged`         | Working directory changes                               | (no matcher)            |
| `FileChanged`        | Watched file changes on disk                            | filename (basename)     |
| `WorktreeCreate`     | Git worktree being created                              | (no matcher)            |
| `WorktreeRemove`     | Git worktree being removed                              | (no matcher)            |
| `PreCompact`         | Before compaction                                       | manual/auto             |
| `PostCompact`        | After compaction                                        | manual/auto             |
| `Elicitation`        | MCP server requests user input                          | MCP server name         |
| `ElicitationResult`  | User responds to MCP elicitation                        | MCP server name         |
| `SessionEnd`         | Session terminates                                      | exit reason             |

### Handler Types

1. **`command`** -- Runs a shell command. JSON input on stdin, exit codes for control.
2. **`http`** -- POSTs event data to a URL. Response body uses same JSON format.
3. **`prompt`** -- Single-turn LLM evaluation. Returns `{"ok": true/false, "reason": "..."}`.
4. **`agent`** -- Multi-turn subagent with tool access. Same ok/reason format, 60s default timeout.

### Exit Code Semantics

| Exit code | Effect                                                    |
|:----------|:----------------------------------------------------------|
| 0         | Action proceeds. Stdout added to context (SessionStart, UserPromptSubmit). |
| 2         | Action blocked. Stderr becomes Claude's feedback.         |
| Other     | Action proceeds. Stderr logged but not shown to Claude.   |

### JSON Output (Structured Control)

For finer control than exit codes, exit 0 and write JSON to stdout:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Use rg instead of grep"
  }
}
```

PreToolUse decisions: `allow`, `deny`, `ask`.

**Critical nuance:** `allow` skips the interactive prompt but does NOT override deny rules from settings. Enterprise managed deny lists always take precedence.

### The `if` Field (v2.1.85+)

Filters hooks by tool name AND arguments using permission rule syntax:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "if": "Bash(git *)",
        "command": "./scripts/check-git-policy.sh"
      }]
    }]
  }
}
```

The hook process only spawns when the Bash command starts with `git`.

### Configuration Location

| Location                        | Scope              | Shareable            |
|:--------------------------------|:-------------------|:---------------------|
| `~/.claude/settings.json`       | All your projects  | No (local)           |
| `.claude/settings.json`         | Single project     | Yes (commit to repo) |
| `.claude/settings.local.json`   | Single project     | No (gitignored)      |
| Managed policy settings         | Organization-wide  | Admin-controlled     |
| Plugin `hooks/hooks.json`       | When plugin active | Bundled with plugin  |
| Skill/agent frontmatter         | While active       | Defined in component |

### Key Patterns to Adopt

1. **Auto-format on every edit:**
   ```json
   {"hooks": {"PostToolUse": [{"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"}]}]}}
   ```

2. **Block protected files** (`.env`, `package-lock.json`, `.git/`): PreToolUse with exit code 2.

3. **Re-inject context after compaction:**
   ```json
   {"hooks": {"SessionStart": [{"matcher": "compact", "hooks": [{"type": "command", "command": "echo 'Reminder: use Bun, not npm. Current sprint: auth refactor.'"}]}]}}
   ```

4. **Desktop notifications** when Claude needs input: `Notification` event with `osascript`.

5. **Stop hooks with completion verification:** Prompt-based hook checking if all tasks are done.

6. **Prompt-based hooks for judgment calls:** `type: "prompt"` for decisions requiring LLM evaluation.

7. **`PermissionRequest` auto-approval** for specific tools (e.g., `ExitPlanMode`).

### Anti-Patterns to Avoid

- Shell profiles with unconditional `echo` statements (prepend garbage to hook JSON output -- wrap in `[[ $- == *i* ]]`).
- Stop hooks without `stop_hook_active` guard (infinite loop).
- Multiple PreToolUse hooks writing `updatedInput` for the same tool (last one wins, non-deterministic).
- Using `PermissionRequest` hooks in headless mode (`-p`) -- they don't fire. Use `PreToolUse` instead.
- Matching on `.*` or empty matcher for PermissionRequest (auto-approves everything).

### Hooks vs Skills vs CLAUDE.md

| Mechanism  | Execution     | Adherence | Best for                              |
|:-----------|:--------------|:----------|:--------------------------------------|
| Hooks      | Deterministic | 100%      | Formatting, blocking, notifications   |
| CLAUDE.md  | Advisory      | ~80-90%   | Coding standards, architectural rules |
| Skills     | On-demand     | ~80-90%   | Domain knowledge, workflows           |

---

## 3. Subagents and Agent Teams

### Subagents (Stable, Production-Ready)

Subagents run in isolated context windows within a single session. They preserve main conversation context by keeping exploration/research output separate.

**Built-in subagents:**

| Agent            | Model   | Tools         | Purpose                              |
|:-----------------|:--------|:--------------|:-------------------------------------|
| Explore          | Haiku   | Read-only     | Fast codebase search/analysis        |
| Plan             | Inherit | Read-only     | Research for plan mode               |
| general-purpose  | Inherit | All           | Complex multi-step tasks             |
| Bash             | Inherit | Terminal      | Running commands in separate context |

**Custom subagent definition** (`.claude/agents/my-agent.md`):

```yaml
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
permissionMode: default
maxTurns: 50
memory: project
skills:
  - api-conventions
  - error-handling-patterns
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
isolation: worktree
background: false
effort: high
---

System prompt as markdown body here.
```

**Key frontmatter fields:** `name`, `description` (required), `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory` (user/project/local), `background`, `effort`, `isolation` (worktree), `initialPrompt`.

**Scope priority:** CLI flag (`--agents`) > project (`.claude/agents/`) > user (`~/.claude/agents/`) > plugin.

**Persistent memory:** Subagents can maintain cross-session knowledge via the `memory` field. Claude manages a `MEMORY.md` file (first 200 lines loaded at startup) plus topic files read on demand.

**Invocation methods:**
- Natural language: "Use the security-reviewer subagent"
- @-mention: `@"security-reviewer (agent)"` (guarantees the specific subagent)
- Session-wide: `claude --agent security-reviewer` (replaces system prompt entirely)
- Settings default: `{"agent": "security-reviewer"}` in `.claude/settings.json`

**Foreground vs background:** Foreground blocks main conversation. Background runs concurrently (pre-approves permissions, auto-denies unapproved). Press Ctrl+B to background a running task.

### Agent Teams (Experimental)

Enable via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings or environment. Requires Claude Code v2.1.32+.

**Architecture:**
- **Team lead:** Main session that creates team, assigns tasks, synthesizes results.
- **Teammates:** Independent Claude Code instances with own context windows.
- **Task list:** Shared list with pending/in-progress/completed states and dependencies.
- **Mailbox:** Direct messaging between agents.

**How teams differ from subagents:**

| Aspect          | Subagents                          | Agent Teams                              |
|:----------------|:-----------------------------------|:-----------------------------------------|
| Context         | Own window, results return to main | Fully independent                        |
| Communication   | Report back to main only           | Direct inter-agent messaging             |
| Coordination    | Main agent manages all             | Shared task list, self-coordination      |
| Token cost      | Lower (summarized results)         | Higher (each is a full Claude instance)  |
| Best for        | Focused tasks, result-only         | Complex work requiring discussion        |

**Display modes:**
- **In-process** (default): All in main terminal. Shift+Down cycles. Works everywhere.
- **Split panes** (`tmux` or iTerm2): Each teammate gets own pane.

**Best practices for teams:**
- Start with 3-5 teammates.
- 5-6 tasks per teammate is optimal.
- Scope tasks to avoid file conflicts (two agents editing the same file = overwrites).
- Start with research/review (no-code) before trying parallel implementation.
- Use `SubagentStart`/`SubagentStop`, `TaskCreated`/`TaskCompleted`, `TeammateIdle` hooks for quality gates.

**Current limitations:**
- No session resumption with in-process teammates.
- Task status can lag (teammates sometimes forget to mark tasks complete).
- One team per session; no nested teams.
- Lead is fixed for lifetime of team.

### Key Patterns to Adopt

1. **Subagents for all research/exploration.** Isolates verbose file reads from main context.
2. **Writer/Reviewer pattern.** Separate sessions: one writes code, another reviews with fresh context.
3. **Chain subagents for multi-step workflows.** Research -> implement -> verify.
4. **`isolation: worktree` for parallel implementation.** Each subagent gets its own git worktree.
5. **`memory: project` for reviewers.** Accumulate codebase patterns across sessions.

---

## 4. CLAUDE.md Best Practices

### The Hierarchy

| Scope           | Location                                      | Loaded     | Shared with          |
|:----------------|:----------------------------------------------|:-----------|:---------------------|
| Managed policy  | `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS) | Always | Org (cannot exclude) |
| Project         | `./CLAUDE.md` or `./.claude/CLAUDE.md`        | At launch  | Team via VCS         |
| User            | `~/.claude/CLAUDE.md`                         | At launch  | Just you             |
| Subdirectory    | `subdir/CLAUDE.md`                            | On demand  | Team via VCS         |

**Loading behavior:** Files above the working directory load in full at launch. Files in subdirectories load on demand when Claude reads files in those directories. The walk-up resolution means `foo/bar/CLAUDE.md` and `foo/CLAUDE.md` both load if you run from `foo/bar/`.

### The System-Reminder Wrapper

**Critical caveat:** CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself. Claude treats it as context, not enforced configuration. The system-reminder message wrapper may cause Claude to deprioritize content it considers irrelevant to the current task. This means:

- There is no guarantee of strict compliance, especially for vague or conflicting instructions.
- The more specific and concise your instructions, the more consistently Claude follows them.
- Emphasis markers ("IMPORTANT", "CRITICAL", "YOU MUST") improve adherence but are not absolute.

### Line Limits and Sizing

| File type          | Recommended limit | Rationale                                              |
|:-------------------|:------------------|:-------------------------------------------------------|
| `~/.claude/CLAUDE.md` | ~60 lines      | Loaded into every session across all projects          |
| Project CLAUDE.md  | ~200 lines        | Loaded every session for this project                  |
| `.claude/rules/*.md` | Varies          | Can be path-scoped for conditional loading             |
| Skills SKILL.md    | ~500 lines        | Loaded only when relevant                              |

**Auto memory limit:** First 200 lines or 25KB of `MEMORY.md` loaded at startup (whichever comes first).

### What Belongs Where

| Content                                    | CLAUDE.md | Skills      | Hooks       | Rules              |
|:-------------------------------------------|:----------|:------------|:------------|:-------------------|
| Build/test commands                        | YES       | -           | -           | -                  |
| Code style rules                           | YES       | -           | -           | YES (path-scoped)  |
| Architectural decisions                    | YES       | -           | -           | -                  |
| Domain-specific knowledge                  | -         | YES         | -           | -                  |
| Reusable workflows                         | -         | YES         | -           | -                  |
| Auto-formatting                            | -         | -           | YES         | -                  |
| File protection                            | -         | -           | YES         | -                  |
| Notifications                              | -         | -           | YES         | -                  |
| Path-specific conventions                  | -         | -           | -           | YES (with `paths:`)|

### `.claude/rules/` Organization

Rules files support YAML frontmatter with a `paths` field for conditional loading:

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API Development Rules
- All API endpoints must include input validation
```

Rules without `paths` load unconditionally. Path-scoped rules trigger when Claude reads matching files.

### Imports with `@path` Syntax

```markdown
See @README.md for project overview and @package.json for npm commands.
- git workflow: @docs/git-instructions.md
- personal overrides: @~/.claude/my-project-instructions.md
```

Relative paths resolve from the file containing the import. Max recursion depth: 5 hops. First encounter triggers an approval dialog.

### AGENTS.md Compatibility

Claude Code reads CLAUDE.md, not AGENTS.md. For cross-tool compatibility:

```markdown
# CLAUDE.md
@AGENTS.md

## Claude Code specific
Use plan mode for changes under `src/billing/`.
```

This is exactly what your current symlink setup achieves (`CLAUDE.md -> docs/AGENTS.md`).

### Key Patterns to Adopt

1. **Prune ruthlessly.** For each line ask: "Would removing this cause Claude to make mistakes?" If not, cut it.
2. **Use `/init` for initial generation**, then refine. Set `CLAUDE_CODE_NEW_INIT=1` for the interactive multi-phase flow.
3. **Path-scoped rules** for language/framework-specific conventions (e.g., `src/api/**/*.ts` gets API rules).
4. **Symlink shared rules** across projects: `ln -s ~/shared-claude-rules .claude/rules/shared`.
5. **HTML comments for maintainer notes** (`<!-- notes -->` stripped before injection, zero token cost).
6. **`claudeMdExcludes`** in monorepos to skip other teams' CLAUDE.md files.

### Anti-Patterns to Avoid

- Over 200 lines (Claude ignores rules lost in the noise).
- Duplicating what Claude already knows (standard language conventions, obvious practices).
- Information that changes frequently (breaks stale when not updated).
- Contradicting rules across files (Claude picks one arbitrarily).
- File-by-file descriptions of the codebase (Claude can read the code).

---

## 5. Headless Mode / CI Integration

### Current State

The `-p` (or `--print`) flag runs Claude Code non-interactively. The Agent SDK (Python and TypeScript packages) provides full programmatic control.

### CLI Flags

| Flag                       | Purpose                                                   |
|:---------------------------|:----------------------------------------------------------|
| `-p "prompt"`              | Non-interactive mode                                      |
| `--bare`                   | Skip all auto-discovery (hooks, skills, plugins, MCP, CLAUDE.md). Recommended for CI. |
| `--output-format text`     | Plain text (default)                                      |
| `--output-format json`     | JSON with `result`, `cost_usd`, `duration_ms`, `num_turns`, `session_id` |
| `--output-format stream-json` | Newline-delimited JSON for real-time streaming         |
| `--json-schema '{...}'`    | Structured output conforming to schema (in `structured_output` field) |
| `--allowedTools "Read,Edit,Bash"` | Auto-approve specific tools                        |
| `--continue`               | Continue most recent conversation                         |
| `--resume SESSION_ID`      | Resume specific session                                   |
| `--append-system-prompt`   | Add instructions while keeping defaults                   |
| `--system-prompt`          | Fully replace system prompt                               |
| `--settings <file-or-json>`| Override settings                                         |
| `--mcp-config <file>`      | Override MCP config                                       |
| `--agents <json>`          | Define session-scoped agents                              |
| `--verbose`                | Debug output                                              |

### Session Management

```bash
# One-off
claude -p "Explain what this project does"

# Chain conversations
session_id=$(claude -p "Start review" --output-format json | jq -r '.session_id')
claude -p "Continue review" --resume "$session_id"

# Structured output
claude -p "Extract function names" --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}}}'
```

### Context Window Management

- **Auto-compaction:** Triggers at ~95% capacity (override with `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`).
- **`/compact <instructions>`:** Manual compaction with focus guidance.
- **`/compact Focus on the API changes`:** Directs what to preserve.
- **CLAUDE.md survives compaction:** Re-read from disk and re-injected fresh.
- **Subagent compaction:** Independent of main conversation.

### CI Integration Patterns

```bash
# GitHub Actions: auto-review PRs
gh pr diff "$1" | claude --bare -p \
  --append-system-prompt "You are a security engineer. Review for vulnerabilities." \
  --allowedTools "Read" \
  --output-format json

# Auto-commit with scoped permissions
claude --bare -p "Look at staged changes and create a commit" \
  --allowedTools "Bash(git diff *),Bash(git log *),Bash(git status *),Bash(git commit *)"

# Fan-out migration
for file in $(cat files.txt); do
  claude --bare -p "Migrate $file from React to Vue. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done
```

### Key Patterns to Adopt

1. **Always use `--bare` for CI/scripts.** Prevents local config from affecting reproducibility.
2. **`--allowedTools` with permission rule syntax.** Trailing `*` enables prefix matching (`Bash(git diff *)` allows any git diff command).
3. **Capture `session_id` for multi-step workflows.** Continue conversations across pipeline stages.
4. **`stream-json` for real-time monitoring.** Process tokens as they arrive.
5. **`--json-schema` for machine-readable output.** Parse with jq in downstream pipeline steps.

---

## 6. Community Best Practice Repos

### [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) -- 28.8k stars

**Assessment:** The most comprehensive community reference. Covers all 10 primary Claude Code features with live `.claude/` configuration examples, 87 actionable tips across 12 categories, and comparative analysis of 9 major community workflows.

**Notable content:**
- **Orchestration pattern:** Command -> Agent -> Skill architecture (weather demo showing command asks for preference, agent fetches data, skill generates SVG).
- **87 tips** organized by category (prompting, planning, CLAUDE.md, agents, commands, skills, hooks, workflows, git, debugging, utilities, daily usage).
- **Workflow comparison matrix:** Ranks popular approaches (Superpowers/127k stars, Everything Claude Code/124k, Spec Kit/84k, etc.) by methodology.
- **Core philosophy:** "Do not babysit" -- trust Claude's autonomous decision-making.

**Key takeaways for our system:**
- Phase-wise gated plans with multiple test layers (unit, automation, integration).
- Fresh contexts strategically for complex multi-step tasks.
- Constitution-like rules for consistent agent behavior.

### [ChrisWiles/claude-code-showcase](https://github.com/ChrisWiles/claude-code-showcase) -- 5.6k stars

**Assessment:** A practical reference implementation showing a complete `.claude/` directory for a real project. Strong on hooks and automation.

**Notable content:**
- Auto-format hooks, test-on-change hooks, TypeScript type-check hooks, branch-protection hooks.
- Code review agent with detailed checklist (TypeScript strict mode, error handling, loading states, mutation patterns).
- GitHub workflow agents for scheduled tasks: monthly docs sync, weekly code quality reviews, biweekly dependency audits.
- MCP server integration with ticket systems (read tickets, implement features, update status).

**Key takeaways for our system:**
- Hooks for auto-formatting and branch protection are production-proven.
- Scheduled GitHub workflow agents are a mature pattern.
- MCP ticket integration closes the loop between project management and code.

### [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) -- 21.6k stars

**Assessment:** The canonical "awesome list" for Claude Code. Curated collection of skills, hooks, slash-commands, agent orchestrators, and plugins.

**Notable tools referenced:**
- **claude-devtools:** Desktop app for observability into Claude Code sessions (turn-based context data, subagent execution trees).
- **Agnix:** Linter for Claude Code agent files (validates CLAUDE.md, AGENTS.md, SKILL.md).
- **Codebase to Course:** Skill that turns a codebase into an interactive HTML course.

### [anthropics/skills](https://github.com/anthropics/skills) -- 108k stars

**Assessment:** Official Anthropic repository. The canonical reference for the Agent Skills open standard. Contains production-quality skill implementations.

**Content:**
- Skill format specification and template.
- Production skills: docx, pdf, pptx, xlsx (source-available reference implementations).
- Example skills across creative, technical, enterprise, and document categories.
- Plugin configuration for Claude Code marketplace integration.

**Key takeaway:** Use Anthropic's template as the starting point for all new skills. The document skills are the gold standard for progressive disclosure and script bundling.

### Other Notable Resources

- **[travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills):** Community-curated skills collection.
- **[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills):** Another skills curation.
- **[disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery):** Deep dive on hooks patterns.
- **[leehanchung.github.io (Agent Skills Deep Dive)](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/):** First-principles analysis of skill architecture.
- **[SkillsMP.com](https://skillsmp.com/):** Agent Skills Marketplace for cross-tool skill distribution.

---

## Concrete Recommendations for Your System

### Immediate Actions

1. **Create `~/.claude/skills/` directory.** Start migrating domain knowledge from CLAUDE.md rules into skills with proper SKILL.md frontmatter.

2. **Implement core hooks in `~/.claude/settings.json`:**
   - Notification hook (macOS `osascript` for desktop alerts).
   - SessionStart compact hook (re-inject critical reminders after compaction).
   - PostToolUse format hook (auto-format on edit/write).

3. **Create foundational subagents in `~/.claude/agents/`:**
   - `researcher.md` (Explore-based, read-only, Haiku model).
   - `code-reviewer.md` (read-only, Opus model, with `memory: user`).

4. **Slim down your CLAUDE.md files.** Your `~/.claude/CLAUDE.md` content currently gets injected via the project CLAUDE.md `@import` chain. Audit for anything Claude already knows or that should be a skill instead.

5. **Add path-scoped rules** for Python and TypeScript conventions in `.claude/rules/`.

### Architecture Decisions

| Decision                        | Recommendation                                           |
|:--------------------------------|:---------------------------------------------------------|
| Skill vs CLAUDE.md rule         | If it applies to ALL sessions: CLAUDE.md. If domain-specific: skill. |
| Hook vs CLAUDE.md instruction   | If it MUST happen: hook. If it SHOULD happen: CLAUDE.md. |
| Subagent vs agent team          | Subagent for focused tasks. Teams only for parallel research/review requiring inter-agent discussion. |
| `context: fork` vs inline skill | Fork for tasks producing verbose output or requiring isolation. Inline for conventions/guidelines. |
| User-level vs project-level     | Skills you use across projects: `~/.claude/skills/`. Project-specific: `.claude/skills/`. |

### Things to Monitor

- **Agent teams stability.** Currently experimental with known limitations (no session resumption, task status lag). Re-evaluate quarterly.
- **Skill marketplace evolution.** SkillsMP.com and Claude's `/plugin marketplace` are rapidly growing. Check for ready-made skills before building custom ones.
- **`--bare` as default for `-p`.** Anthropic plans to make `--bare` the default for headless mode in a future release. Current scripts using `-p` without `--bare` should be audited.

---

## Evidence Quality Assessment

| Topic                    | Confidence | Source quality                                                  |
|:-------------------------|:-----------|:----------------------------------------------------------------|
| Skills system            | High       | Official docs (code.claude.com) + platform docs + Anthropic repo |
| Hooks system             | High       | Official docs + multiple community implementations              |
| Subagents                | High       | Official docs, stable API, extensive examples                   |
| Agent teams              | Medium     | Official docs, but labeled experimental with known limitations  |
| CLAUDE.md best practices | High       | Official docs + 28k-star community reference                   |
| Headless / CI            | High       | Official docs, multiple CI integration guides                   |
| Community repos          | High       | Directly verified star counts and content via web fetch          |

---

## Limitations

1. **Time-sensitivity.** Claude Code is actively developed. Features marked "experimental" (agent teams, auto mode) may change significantly. This report reflects documentation as of 2026-03-31.

2. **Community repo recency.** Star counts and content were verified via web fetch on this date but change rapidly.

3. **Adherence percentages.** The "~80% adherence" figure for CLAUDE.md is a community consensus estimate, not an empirically measured value from Anthropic.

4. **Platform-specific behavior.** Some hook commands and paths are macOS-specific. Linux and Windows equivalents exist but were not exhaustively tested.

5. **Missing: Plugin system deep dive.** The plugin system (`/plugin`, marketplace, packaging) is maturing rapidly but was not a primary research topic. It warrants its own investigation.

---

## Sources

### Official Anthropic Documentation
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Automate workflows with hooks](https://code.claude.com/docs/en/hooks-guide)
- [Hooks reference](https://code.claude.com/docs/en/hooks)
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams)
- [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- [Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices)
- [Run Claude Code programmatically](https://code.claude.com/docs/en/headless)
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

### Community Repositories
- [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) -- 28.8k stars
- [ChrisWiles/claude-code-showcase](https://github.com/ChrisWiles/claude-code-showcase) -- 5.6k stars
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) -- 21.6k stars
- [anthropics/skills](https://github.com/anthropics/skills) -- 108k stars
- [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery)

### Articles and Guides
- [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Agent Skills Marketplace](https://skillsmp.com/)
- [Agent Skills open standard](https://agentskills.io)
