# Agent Ecosystem Research Report

**Date**: 2026-03-31
**Scope**: Paperclip AI, Agent Skills standard, OpenClaw, Skill Marketplaces, Promptfoo
**Methodology**: Web search, GitHub API queries, direct page fetches of documentation and repos

---

## Executive Summary

- **Paperclip** is a 4-week-old MIT-licensed orchestration framework (42.7k stars) that models AI agent teams as companies with org charts, budgets, and governance. Impressive concept, but early-stage (v0.3) with rough edges. The heartbeat protocol and atomic task checkout are its most adoptable patterns.
- **Agent Skills** (agentskills.io) is the emerging open standard for portable agent capabilities. Adopted by 30+ tools (Claude Code, Codex, Cursor, Gemini CLI, VS Code Copilot, etc.). The SKILL.md format is simple, well-specified, and worth building on immediately.
- **OpenClaw** is the fastest-growing open-source project in GitHub history (343k stars). It is an agent *runtime* (execution, messaging, skills), not an orchestration layer. Paperclip treats it as a managed adapter target. Now governed by an independent foundation after creator joined OpenAI.
- **Skill Marketplaces** (SkillsMP at 87k+ skills, SkillHub at 7k+, Antigravity at 1,340+) are active discovery platforms. Quality varies wildly. Antigravity has the best curation with installer CLI and role-based bundles.
- **Promptfoo** (18.9k stars, acquired by OpenAI March 2026, remains MIT) is the standard eval framework. YAML-first configuration, 40+ assertion types, native Claude/Anthropic support. The promptfoo-evals agent skill creates a tight write-eval-iterate loop.

---

## 1. Paperclip AI (paperclipai/paperclip)

### Status

| Metric | Value |
|--------|-------|
| GitHub | github.com/paperclipai/paperclip |
| Stars | 42,700 |
| Forks | 6,462 |
| Open Issues | 1,451 (604 issues + 847 PRs) |
| Created | 2026-03-02 |
| Last Push | 2026-03-31 |
| Latest Release | v2026.325.0 (2026-03-25) |
| License | MIT |
| Language | TypeScript (Node.js server + React UI) |
| Requires | Node.js 20+, pnpm 9.15+ |

Actively maintained. Daily commits. Switched from semver (v0.3.x) to calver (v2026.325.0) within three weeks. ~30 days old.

### The Companies Spec

Paperclip models autonomous operations around a corporate metaphor:

**Hierarchy**: Company > Goals > Projects > Issues/Tasks > Agents
- **Companies**: Top-level containers with goals, employees (all AI), org structure, budgets. One deployment supports many companies with complete data isolation.
- **Agents (Employees)**: Report to exactly one manager in a strict tree hierarchy. CEO has no manager. Any runtime that can receive a heartbeat can be "hired" (Claude Code, OpenClaw, Codex, Cursor, Gemini, HTTP agents, Bash processes).
- **Tasks (Issues)**: Assigned to single agents. Carry full goal ancestry -- every task traces back to the company mission. Ticket-based with persistent sessions across reboots.
- **Soul Files**: Each agent has three defining files in `$AGENT_HOME/`:
  - `SOUL.md` -- identity and behavioral guidelines ("who you are and how you should act")
  - `HEARTBEAT.md` -- execution and extraction checklist (run every heartbeat)
  - `TOOLS.md` -- available tools and capabilities
  - `AGENTS.md` -- composite instructions including embedded IC Protocol (~40 lines) or PM Protocol (~60 lines)

### The Heartbeat Protocol

Each heartbeat cycle follows this sequence:
1. **Check identity** (load SOUL.md)
2. **Review assignments** (query task queue)
3. **Pick work** (select highest-priority unfinished task)
4. **Check out task** (atomic -- only one agent can own a task at a time; concurrent claims get 409 Conflict)
5. **Do the work** (execute within budget constraints)
6. **Update status** (report progress, update issue)

Heartbeats trigger via: scheduled timers, task assignments, @-mentions in comments, manual UI invocation, or approval resolution events. Agents resume the same task context across heartbeats rather than restarting from scratch.

### Budget Enforcement

- Monthly spend limits per company and per agent (in cents)
- When an agent hits its limit, it stops. No runaway costs.
- Task checkout and budget enforcement are atomic -- "no double-work and no runaway spend"
- Real-time cost monitoring in dashboard

### Board Governance

"You're the board." Three approval gates require human intervention:
1. Hiring requests from agents
2. CEO's initial strategic plan
3. Board overrides (pause, resume, terminate agents; reassign tasks)

Every mutation is logged in an immutable audit trail. Config versioning enables rollback.

### Dashboard Features

- Org chart visualization with hierarchies and reporting lines
- Real-time cost monitoring and budget tracking
- Task management interface
- Mobile-ready design
- Immutable audit logs with full tool-call tracing
- Multi-company management from single deployment

### Key Takeaways for Our System

1. **Heartbeat protocol pattern**: Wake-check-claim-work-report is a clean agent loop pattern worth adopting even without Paperclip itself
2. **Atomic task checkout**: 409 Conflict on concurrent claims prevents double-work -- simple and effective
3. **Goal ancestry**: Every task traces back to company mission -- good for alignment auditing
4. **Soul file separation**: SOUL.md (identity) vs HEARTBEAT.md (execution) vs TOOLS.md (capabilities) is a clean separation of concerns
5. **Budget enforcement at the orchestration layer**: Prevents runaway agent costs

### Patterns to Avoid

1. **Adopting the full framework at this stage**: v0.3 product, 4 weeks old, 1,451 open issues. Expect API changes.
2. **Self-hosted only**: No managed cloud option. Local-only scope limits distributed production deployments.
3. **Tight coupling to corporate metaphor**: The company/CEO/board model may over-constrain simpler agent setups
4. **Sparse ecosystem**: Fewer tutorials than AutoGen or CrewAI. Limited third-party documentation.

### Gaps/Concerns

- No YAML/JSON configuration schema documented publicly -- config is mostly through environment files
- Budget enforcement mechanics (overage handling, real-time tracking internals) are under-documented
- 16 pre-built company templates exist but quality/coverage is unclear
- Claude integration is strongest; other adapters are thinner
- 847 open PRs suggests contribution backlog or review bottleneck

---

## 2. Agent Skills Open Standard (agentskills.io)

### Status

| Metric | Value |
|--------|-------|
| Spec Repo | github.com/agentskills/agentskills (14,682 stars) |
| Example Skills | github.com/anthropics/skills (107,631 stars) |
| Spec Site | agentskills.io |
| License | Apache-2.0 (spec); varies (individual skills) |
| Origin | Anthropic (Dec 2025), now open governance |
| Adoption | 30+ tools |

### The SKILL.md Specification

#### Directory Structure
```
skill-name/
├── SKILL.md          # Required: YAML frontmatter + markdown instructions
├── scripts/          # Optional: executable code (Python, Bash, JS)
├── references/       # Optional: documentation files loaded on demand
├── assets/           # Optional: templates, images, data files, schemas
└── ...               # Any additional files
```

#### Frontmatter Fields

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | YES | Max 64 chars. Lowercase + hyphens only. Must match parent directory name. No leading/trailing/consecutive hyphens. |
| `description` | YES | Max 1024 chars. Describes what the skill does AND when to use it. Should include trigger keywords. |
| `license` | No | License name or reference to bundled LICENSE file |
| `compatibility` | No | Max 500 chars. Environment requirements (intended product, system packages, network) |
| `metadata` | No | Arbitrary key-value map (author, version, etc.) |
| `allowed-tools` | No | Space-delimited list of pre-approved tools. Experimental. |

#### Example SKILL.md
```markdown
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---

## Instructions
[Step-by-step instructions, examples, edge cases]

See [the reference guide](references/REFERENCE.md) for details.
Run: scripts/extract.py
```

#### Progressive Disclosure (Token Efficiency)
1. **Metadata** (~100 tokens): `name` and `description` loaded at startup for ALL skills
2. **Instructions** (<5000 tokens recommended): Full SKILL.md body loaded when skill activates
3. **Resources** (as needed): scripts/, references/, assets/ loaded only when required

Key guideline: Keep SKILL.md under 500 lines. Move detailed reference material to separate files.

### How Skills Are Discovered and Loaded

Skills are filesystem-based. Agents scan known directories (e.g., `.claude/skills/`, `.agents/skills/`, project-level skill directories) at startup. The `name` and `description` fields from all discovered skills are loaded into context. When the agent determines a skill is relevant to the current task (based on description keywords and context), it loads the full SKILL.md body. Referenced files (scripts, references, assets) are loaded on-demand during execution.

### Tools Supporting Agent Skills (30+)

Claude Code, Claude (platform), OpenAI Codex, Cursor, VS Code Copilot, GitHub Copilot, Gemini CLI, OpenCode, OpenHands, Amp, Roo Code, Junie (JetBrains), Goose (Block), Letta, Firebender, Piebald, Factory, Databricks, Kiro, Laravel Boost, Spring AI, TRAE (ByteDance), Mux (Coder), Snowflake Cortex Code, Qodo, Emdash, Mistral Vibe, Command Code, Ona, VT Code, Agentman, Autohand

### Key Takeaways for Our System

1. **The standard has won**: 30+ tools, 100k+ stars on anthropics/skills. Build on it, not around it.
2. **Progressive disclosure is critical**: ~100 tokens for discovery, <5000 for activation, on-demand for deep reference. Design skills for token efficiency.
3. **Description field is the trigger mechanism**: Write descriptions that include specific keywords agents use to match tasks to skills.
4. **Validation tooling exists**: `skills-ref validate ./my-skill` checks frontmatter conformance.
5. **Cross-tool portability**: Same skill works in Claude Code, Codex, Cursor, etc. Write once, use everywhere.

### Patterns to Avoid

1. **Bloated SKILL.md files**: Keep under 500 lines. Token waste kills performance.
2. **Deep reference chains**: Keep file references one level deep from SKILL.md.
3. **Vague descriptions**: "Helps with PDFs" won't trigger. Be specific about what AND when.
4. **Ignoring `allowed-tools`**: Experimental but important for security -- pre-approve only needed tools.

### Gaps/Concerns

- `allowed-tools` field is experimental; support varies between implementations
- No standard for skill versioning (metadata.version is optional and unstructured)
- No dependency management between skills (no "this skill requires skill X")
- No standard for skill testing/validation beyond frontmatter checks
- Discovery relies entirely on `description` text matching -- no structured trigger syntax

---

## 3. OpenClaw

### Status

| Metric | Value |
|--------|-------|
| GitHub | github.com/openclaw/openclaw |
| Stars | 343,294 (fastest-growing OSS project in GitHub history) |
| Forks | 67,920 |
| Open Issues | 16,866 |
| Created | 2025-11-24 (as "Clawdbot") |
| Last Push | 2026-04-01 |
| License | MIT |
| Language | TypeScript |
| Creator | Peter Steinberger (PSPDFKit founder) |
| Governance | Independent foundation (since Feb 2026) |

### What It Is

OpenClaw is an **agent runtime**, not an orchestration framework. It is a personal AI assistant that runs locally and connects LLMs to real software. Key capabilities:

- Runs on any OS, any platform
- 100+ built-in skills
- Connects AI models to apps, browsers, system tools
- Messaging platform UI (Discord, Slack, Telegram)
- Task execution: automate workflows, manage files, send emails, control APIs
- Session and memory management
- Model provider failover

### Naming History

- Nov 2025: "Clawdbot" (original name)
- Jan 27, 2026: Renamed to "Moltbot"
- Jan 30, 2026: Renamed to "OpenClaw"
- Feb 14, 2026: Creator (Steinberger) joined OpenAI; project transferred to independent foundation

### Relationship to Paperclip

**Complementary, not competitive.** They solve different problems:

| Concern | OpenClaw | Paperclip |
|---------|----------|-----------|
| Role | Agent runtime (execution) | Orchestration control plane |
| Handles | Individual agent execution, messaging, sessions, memory, model failover | Multi-agent coordination, org charts, budgets, governance |
| Analogy | The employee | The company |

**Integration**: Paperclip's OpenClaw adapter connects via webhooks to OpenClaw's gateway (port 18789). Paperclip handles scheduling, cost tracking, heartbeats. OpenClaw handles how the agent executes. The integration was completed and verified on 2026-03-20/21 with 6 tools working.

### Relationship to Agent Skills

OpenClaw has its own built-in skills system (100+). The relationship to the agentskills.io SKILL.md standard is not explicitly documented in my research. OpenClaw's skill format may predate or differ from the open standard.

### Key Takeaways for Our System

1. **OpenClaw as adapter target**: If using Paperclip, OpenClaw is a first-class runtime to manage
2. **Independent foundation governance**: Good long-term signal for an open-source dependency
3. **Messaging-first interface**: Discord/Slack/Telegram as agent UIs is a pattern worth noting
4. **The runtime/orchestration split**: OpenClaw (runtime) + Paperclip (orchestration) is a clean architecture to emulate

### Patterns to Avoid

1. **16,866 open issues**: The project's growth has outpaced maintainer capacity
2. **OpenAI affiliation**: Creator at OpenAI; foundation governance is new and untested
3. **Direct dependency**: Too fast-moving and large to tightly couple to

### Gaps/Concerns

- OpenClaw's own skill format vs agentskills.io standard -- unclear compatibility
- Foundation governance is weeks old; long-term direction uncertain
- The rename history (3 names in 2 months) suggests early identity instability
- 16k open issues is a red flag for contributor/maintainer ratio

---

## 4. Skill Marketplaces

### SkillsMP (skillsmp.com)

| Metric | Value |
|--------|-------|
| Skills Count | 87,427+ |
| Format | Agent Skills (SKILL.md) standard |
| Compatible With | Claude Code, Codex CLI |
| Affiliation | Independent community project (not Anthropic) |
| Quality Control | AI-evaluated |

Aggregates agent skills from GitHub. Largest directory by volume. Quality varies -- AI evaluation is automated, not human-curated.

### SkillHub (skillhub.club)

| Metric | Value |
|--------|-------|
| Skills Count | 7,000+ |
| Format | Agent Skills standard |
| Compatible With | Claude Code, Codex CLI, Gemini CLI, OpenCode |
| Quality Control | AI-evaluated |

Smaller, more curated than SkillsMP.

### Antigravity Awesome Skills (github.com/sickn33/antigravity-awesome-skills)

| Metric | Value |
|--------|-------|
| Skills Count | 1,340+ |
| Format | Agent Skills standard |
| Installer | `npx antigravity-awesome-skills` |
| Tool Support | --claude, --cursor, --gemini, --codex, --antigravity, --kiro |
| Quality Control | Automated validation + manual review for risky changes |

**Best-curated collection.** Features:
- **Role-based bundles**: Essentials, Full-Stack Developer, Security Developer, DevOps & Cloud, QA & Testing, OSS Maintainer
- **Recommended starters**: Essentials + Full-Stack + QA for MVP; Security + DevOps + Observability for hardening
- **Installer CLI**: Shallow clone, tool-specific flags, custom paths
- **Quality gates**: Automated `npm run validate`, skill-review GitHub checks on PRs, manual review for risky guidance

### Other Notable Collections

- **VoltAgent/awesome-agent-skills**: Official skills from Anthropic, Google Labs, Vercel, Stripe, Cloudflare, Netlify, Sentry, Expo, Hugging Face, Figma + community skills
- **anthropics/skills** (107k stars): Anthropic's official example skills repo
- **LobeHub skills**: Marketplace integrated with LobeHub ecosystem
- **MCP Market skills directory**: Cross-listed with MCP servers

### Notable Infrastructure/Utility Skills Worth Forking

1. **promptfoo-evals**: Teaches agents proper eval conventions. Activates automatically for eval creation.
2. **agent-sandbox-skill**: E2B cloud sandbox for isolated full-stack development/testing
3. **Superpowers** (40.9k stars): Composable multi-agent development methodology. Structures full SDLC through chained skills.
4. **test-driven-development**: TDD workflow skill
5. **debugging-strategies**: Systematic troubleshooting
6. **security-auditor**: Security-focused code review
7. **create-pr**: PR packaging workflow
8. **lint-and-validate**: Quality checks

### Key Takeaways for Our System

1. **Antigravity is the best starting point**: Curated, installable, role-based bundles
2. **Volume does not equal quality**: SkillsMP's 87k skills are mostly auto-scraped from GitHub. Cherry-pick, don't bulk install.
3. **Fork infrastructure skills, don't depend on them**: Skills are just markdown folders -- fork and customize rather than pointing at external repos
4. **The promptfoo-evals skill is high-value**: Creates a tight eval loop for skill development itself

### Patterns to Avoid

1. **Bulk installing marketplace skills**: Most are low-quality or too generic
2. **Trusting AI-evaluated quality scores**: Automated evaluation misses context-specific issues
3. **External skill dependencies**: Skills should be vendored/forked into your project, not fetched at runtime

### Gaps/Concerns

- No standardized quality rating across marketplaces
- SkillsMP's 87k count likely includes many trivial/broken skills
- No deduplication across marketplaces -- same skills appear on multiple platforms
- Marketplace search/filtering is rudimentary

---

## 5. Promptfoo

### Status

| Metric | Value |
|--------|-------|
| GitHub | github.com/promptfoo/promptfoo |
| Stars | 18,942 |
| Forks | 1,623 |
| Open Issues | 316 |
| Created | 2023-04-28 |
| Last Push | 2026-04-01 |
| License | MIT |
| Language | TypeScript |
| Acquisition | OpenAI (announced 2026-03-09, pending close) |
| Status | Remains MIT open-source; team continues maintenance |

Most mature tool in this research. Three years old, actively maintained, used by both OpenAI and Anthropic.

### How It Works with Claude/Anthropic

Provider configuration:
```yaml
providers:
  - id: anthropic:messages:claude-opus-4-6
    config:
      temperature: 0
  - id: anthropic:messages:claude-sonnet-4-5-20250929
    config:
      thinking:
        type: enabled
        budget_tokens: 10000
```

Also supports Claude Agent SDK for evaluating CLI-based coding agents.

### YAML Assertion Format

Complete configuration lives in `promptfooconfig.yaml`:

```yaml
description: 'Customer support chatbot eval'
prompts:
  - file://prompts/chat.json
providers:
  - id: anthropic:messages:claude-sonnet-4-5-20250929
    config:
      temperature: 0
defaultTest:
  assert:
    - type: is-json
tests:
  - file://tests/*.yaml
```

Test files (tests/happy-path.yaml):
```yaml
- description: 'Returns order status for valid customer'
  vars:
    order_id: 'ORD-1001'
  assert:
    - type: is-json
    - type: javascript
      value: "JSON.parse(output).status === 'shipped'"
    - type: not-contains
      value: 'error'
    - type: latency
      threshold: 2000
    - type: cost
      threshold: 0.01
```

#### Key Assertion Types

**Deterministic (free, instant, reproducible)**:
`equals`, `contains`, `icontains`, `regex`, `starts-with`, `contains-any`, `contains-all`, `is-json`, `contains-json`, `is-html`, `is-sql`, `is-xml`, `is-refusal`, `latency`, `cost`, `levenshtein`, `rouge-n`, `bleu`, `javascript`, `python`, `webhook`

**Model-Graded (uses LLM, costs tokens)**:
`llm-rubric`, `similar` (embeddings), `factuality`, `answer-relevance`, `context-faithfulness`, `context-recall`, `g-eval`, `classifier`, `trajectory:goal-success`

**Agent-Specific**:
`trajectory:tool-used`, `skill-used`, `trace-span-count`

**Negation**: Every type supports `not-` prefix (e.g., `not-contains`, `not-regex`)

**Weighting**: `weight: 2.0` (default 1.0). Final score = weighted average of all assertions.

**Threshold**: Test-level threshold for combined weighted score. Assertion-level thresholds for similarity, cost, latency, etc.

### Best Practices for Eval-Driven Development

1. **Deterministic first**: Use `contains`, `is-json`, `javascript` before `llm-rubric`. Deterministic checks are fast, free, and reproducible.
2. **Two eval types for skills**:
   - **Quality eval** (promptfooconfig.yaml): Does the skill produce correct output?
   - **Trigger eval** (run_eval.py or eval-set.json): Does the skill activate at the right time?
   - A skill can pass quality evals and fail trigger evals (great output, never invoked), or vice versa.
3. **File-based test organization**: Use `tests/*.yaml` glob patterns for scalable test suites.
4. **Nunjucks for env vars**: Use `'{{env.API_KEY}}'` not shell `$ENV_VAR`.
5. **Inline source material in rubrics**: Use `{{variable}}` to pass context into `llm-rubric` for hallucination detection.
6. **Explicit grader provider**: Specify which model grades `llm-rubric` assertions for reproducibility.
7. **Version control everything**: `promptfooconfig.yaml` lives alongside your code.

### The Promptfoo Agent Skill

A dedicated agent skill (`promptfoo-evals`) teaches coding agents proper eval conventions:

**Install**: Place in `.claude/skills/` or invoke from marketplace
**Activation**: Automatic when agent is asked to create/update eval coverage
**Slash command**: `/promptfoo-evals Create an eval suite for my summarization prompt`

The skill enforces patterns so the agent gets them right the first time: file organization, assertion priority (deterministic before model-graded), Nunjucks syntax, and validation via `promptfoo validate`.

### Key Takeaways for Our System

1. **Standard eval framework**: The most battle-tested option. Used by OpenAI and Anthropic themselves.
2. **Dual eval pattern**: Quality evals + trigger evals. Both are needed for skills.
3. **Deterministic assertions first**: The single most important best practice. Free, fast, reproducible.
4. **The promptfoo-evals skill**: Install it. It creates a tight write-eval-iterate loop.
5. **YAML-first is right**: Declarative configs that version-control well.

### Patterns to Avoid

1. **Over-relying on llm-rubric**: Expensive, non-deterministic, hard to debug. Use only for subjective qualities.
2. **Skipping trigger evals**: A skill that never fires is useless even if its output is perfect.
3. **Large, monolithic eval configs**: Split tests into focused files using glob patterns.

### Gaps/Concerns

- **OpenAI acquisition**: Pending close. Long-term neutrality uncertain despite MIT license commitment.
- **Anthropic provider support**: Works now, but post-acquisition priorities could shift.
- **No native Claude Code integration**: Requires the agent skill or manual setup; no built-in `/eval` command.

---

## Cross-Cutting Analysis

### How These Pieces Fit Together

```
Promptfoo (eval)
    |
    v
Agent Skills (SKILL.md standard) <-- Marketplaces (discovery)
    |
    v
Claude Code / OpenClaw (runtime)
    |
    v
Paperclip (orchestration, optional)
```

**The practical stack today**:
1. Write skills using the Agent Skills SKILL.md standard
2. Test skills with Promptfoo (quality evals + trigger evals)
3. Run skills in Claude Code (or other compatible runtime)
4. Optionally orchestrate multi-agent workflows with Paperclip

### Maturity Assessment

| Tool | Maturity | Adopt Now? |
|------|----------|------------|
| Agent Skills spec | Production-ready | YES -- it's the standard |
| Promptfoo | Production-ready (3 years) | YES -- essential for quality |
| Claude Code skills | Production-ready | YES -- primary runtime |
| Antigravity skills | Good starting point | YES -- fork selectively |
| OpenClaw | Fast-moving, massive | WATCH -- too volatile to depend on |
| Paperclip | Very early (v0.3, 4 weeks) | WATCH -- patterns are good, framework is premature |
| SkillsMP/SkillHub | Discovery only | USE FOR BROWSING -- don't bulk install |

### Recommended Immediate Actions

1. **Adopt SKILL.md format** for all custom skills. Already compatible with our `.claude/skills/` structure.
2. **Install promptfoo-evals skill** to establish eval-driven skill development.
3. **Fork 5-8 infrastructure skills** from Antigravity (TDD, debugging, security-auditor, create-pr, lint-and-validate).
4. **Adopt Paperclip's heartbeat pattern** conceptually without taking the framework dependency.
5. **Adopt the dual eval pattern** (quality + trigger) for every skill we build.

### What NOT to Do

1. Do not adopt Paperclip as a framework yet -- extract its patterns instead
2. Do not bulk-install marketplace skills -- quality is inconsistent
3. Do not depend on external skill repos at runtime -- fork and vendor
4. Do not use `llm-rubric` assertions where deterministic assertions suffice
5. Do not ignore trigger evals -- they catch the "skill never fires" failure mode

---

## Limitations of This Research

- **Paperclip is 4 weeks old**: Documentation, community, and API are all in flux. Findings may be outdated within weeks.
- **OpenClaw's skill format compatibility**: I could not confirm whether OpenClaw's 100+ built-in skills use the agentskills.io SKILL.md standard or a proprietary format.
- **Promptfoo post-acquisition direction**: The OpenAI acquisition has not closed. Future changes to licensing, provider support, or governance are speculative.
- **Marketplace quality**: I did not install or test individual skills from any marketplace. Quality assessments are based on reported metrics and curation processes, not hands-on evaluation.
- **Paperclip budget enforcement internals**: The exact mechanics (real-time token counting, overage handling, throttle vs hard-stop) are not publicly documented in detail.

---

## Sources

### Paperclip AI
- [GitHub - paperclipai/paperclip](https://github.com/paperclipai/paperclip)
- [Paperclip Official Site](https://paperclip.ing/)
- [Paperclip Core Concepts](https://github.com/paperclipai/paperclip/blob/master/docs/start/core-concepts.md)
- [CEO AGENTS.md](https://github.com/paperclipai/companies/blob/main/default/ceo/AGENTS.md)
- [Paperclip Review 2026](https://vibecoding.app/blog/paperclip-review)
- [Paperclip Explained - Towards AI](https://pub.towardsai.net/paperclip-the-open-source-operating-system-for-zero-human-companies-2c16f3f22182)
- [Heartbeat Protocol Explained](https://paperclipai.info/blogs/explain_heartbeat/)
- [RFC: Proactive heartbeat pattern](https://github.com/paperclipai/paperclip/issues/206)

### Agent Skills
- [Agent Skills Specification](https://agentskills.io/specification)
- [Agent Skills Overview](https://agentskills.io/home)
- [GitHub - agentskills/agentskills](https://github.com/agentskills/agentskills)
- [GitHub - anthropics/skills](https://github.com/anthropics/skills)
- [Agent Skills - The New Stack](https://thenewstack.io/agent-skills-anthropics-next-bid-to-define-ai-standards/)
- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills)

### OpenClaw
- [GitHub - openclaw/openclaw](https://github.com/openclaw/openclaw)
- [OpenClaw Explained - KDnuggets](https://www.kdnuggets.com/openclaw-explained-the-free-ai-agent-tool-going-viral-already-in-2026)
- [OpenClaw - Wikipedia](https://en.wikipedia.org/wiki/OpenClaw)
- [OpenClaw vs Paperclip - Flowtivity](https://flowtivity.ai/blog/openclaw-vs-paperclip-ai-agent-framework-comparison/)
- [OpenClaw Gateway Adapter - DeepWiki](https://deepwiki.com/paperclipai/paperclip/5.3-openclaw-gateway-adapter)

### Skill Marketplaces
- [SkillsMP](https://skillsmp.com/)
- [SkillHub](https://www.skillhub.club)
- [Antigravity Awesome Skills](https://github.com/sickn33/antigravity-awesome-skills)
- [VoltAgent Awesome Agent Skills](https://github.com/VoltAgent/awesome-agent-skills)
- [10 Must-Have Skills - Medium](https://medium.com/@unicodeveloper/10-must-have-skills-for-claude-and-any-coding-agent-in-2026-b5451b013051)

### Promptfoo
- [GitHub - promptfoo/promptfoo](https://github.com/promptfoo/promptfoo)
- [Promptfoo Assertions Docs](https://www.promptfoo.dev/docs/configuration/expected-outputs/)
- [Promptfoo Agent Skill](https://www.promptfoo.dev/docs/integrations/agent-skill/)
- [Claude Code Eval Loop Guide](https://www.mager.co/blog/2026-03-08-claude-code-eval-loop/)
- [Promptfoo Joining OpenAI](https://www.promptfoo.dev/blog/promptfoo-joining-openai/)
- [OpenAI Acquires Promptfoo - TechCrunch](https://techcrunch.com/2026/03/09/openai-acquires-promptfoo-to-secure-its-ai-agents/)
- [Promptfoo Configuration Guide](https://www.promptfoo.dev/docs/configuration/guide/)
