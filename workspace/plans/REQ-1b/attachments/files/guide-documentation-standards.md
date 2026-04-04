# Guide: Documentation Standards and Specification-First Development

## What This Is

The rules for how every project, routine, skill, and system change gets documented in chris-os. This isn't a style guide — it's a development methodology. Documentation comes first because documentation IS the specification that Claude Code agents implement from.

## Why It Matters

In a system where AI agents do the building, the quality of the output is determined by the quality of the input. The input is documentation. A vague README produces vague code. A precise README with clear success criteria, diagrams, and examples produces precise implementations with testable outcomes.

This also solves a human problem: Chris works across multiple ventures and systems. Without clear documentation, context evaporates between sessions. With it, any Claude Code session can pick up where the last one left off by reading the docs.

And it solves a collaboration problem: when Garrett needs to understand the consulting system, or Ashley needs to interact with design workflows, or a future hire needs to onboard — the docs are the onboarding.

## How It Works

### The Development Sequence

Every piece of work follows this sequence. No exceptions.

```
 ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
 │ SPECIFY  │───▶│   EVAL   │───▶│   PLAN   │───▶│  BUILD   │───▶│  TEST    │
 │          │    │          │    │          │    │          │    │          │
 │ Write    │    │ Define   │    │ Claude   │    │ Claude   │    │ Run eval │
 │ README + │    │ what     │    │ Code     │    │ Code     │    │ suite.   │
 │ docs     │    │ "good"   │    │ reads    │    │ builds.  │    │ Verify.  │
 │ first.   │    │ looks    │    │ docs,    │    │ Chris    │    │ Fix.     │
 │ No code  │    │ like.    │    │ proposes │    │ reviews  │    │ Update   │
 │ yet.     │    │ Promptfoo│    │ plan.    │    │ at check-│    │ docs.    │
 │          │    │ YAML.    │    │ Chris    │    │ points.  │    │          │
 │          │    │          │    │ approves.│    │          │    │          │
 └──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
       ▲                                                               │
       └──────────────── feedback loop ────────────────────────────────┘
```

### What "Specify" means in practice

For a **new routine** (e.g., email automation):
- Write a README that describes: what problem this solves, who it serves, what it does step by step, what the inputs and outputs are, what approval rules apply, what success looks like.
- Include diagrams showing data flow.
- Define the labels/categories/triggers (for email: which labels exist, what triggers each one, who manages the trigger list).
- Describe the iterative recommendation behavior (the system should observe patterns and recommend improvements — new labels, new triggers, new rules — for Board approval).

For a **new skill**:
- Write the SKILL.md with clear trigger descriptions, step-by-step instructions, and supporting files (examples of good/bad output, reference docs, templates).

For a **new agent**:
- Write the SOUL.md (values, judgment framework, decision authority) and AGENTS.md (role definition, skills list, reporting structure).

### The Iterative Recommendation Principle

This comes from the email automation design and applies to the entire system. Agents don't just execute — they **observe patterns and recommend system improvements**.

Examples:
- Email agent notices Chris always archives emails from a particular sender → recommends adding that sender to an auto-archive rule.
- Inventory agent notices a product consistently sells out within 3 days of restock → recommends adjusting the reorder threshold.
- CS agent notices a new type of customer question appearing frequently → recommends a new FAQ entry or skill.
- Vault maintenance skill notices a cluster of notes in _inbox/ that all relate to the same topic → recommends creating a new resource folder.

The pattern is always the same: **observe → recommend → Board approves → system updates.** Agents never make organizational changes autonomously. They surface recommendations with evidence and let the Board decide.

This principle should be encoded in every agent's soul file as a standing directive: "When you notice recurring patterns that suggest a system improvement, document the observation and recommendation. Present it to the Board during the next review cycle."

## In Our System

### README structure for projects

Every project README follows this template:

```markdown
# Project Name

One paragraph: what this project does and why it exists.

## The Problem
What pain point or opportunity does this address?

## How It Works
Step-by-step description of what the system does.
Include a data flow diagram (Mermaid, preview-only).

## What's Automated
Table of all routines: name, schedule, model, approval tier.

## Inputs and Outputs
What data flows in (APIs, databases, files).
What the system produces (reports, drafts, alerts, recommendations).

## Approval Rules
What requires Board approval. What's auto-logged. What's auto-executed.

## Configuration
Labels, triggers, thresholds, schedules — the knobs that control behavior.
Where each is defined. How to change them.

## Success Criteria
How we know this system is working well. Metrics. Eval definitions.

## Known Limitations
What this system doesn't handle. Where human judgment is required.

## For Collaborators
What someone new needs to know to work with this system.
```

### README structure for routines

Each routine directory has a `config.yaml` AND a section in the project README. The config.yaml is machine-readable. The README section is human-readable. Both must agree.

### Documentation for skills

Skills use the SKILL.md + supporting files pattern:

```
skills/skill-name/
├── SKILL.md                    Instructions (under 500 lines)
├── examples/
│   ├── good-output.md          What correct output looks like
│   └── bad-output.md           What to avoid and why
├── references/
│   └── domain-knowledge.md     Detailed reference loaded on demand
├── templates/
│   └── output-template.md      Structural template for outputs
└── tests/
    └── eval.yaml               Promptfoo assertions
```

### Diagrams

Use Mermaid for all diagrams. Format as preview-only (no code blocks) when targeting Notion or Obsidian rendering. Every system should have at minimum:
- A data flow diagram (what goes in, what comes out, what happens in between)
- An approval flow diagram (who reviews what, when)

For complex systems (email automation, multi-step routines), add:
- A state diagram (what states exist, what triggers transitions)
- A trigger/label/category map (what rules exist, what triggers each)

### The trigger/rule documentation pattern

For systems with configurable rules (email labels, inventory thresholds, content tiers), maintain a single source-of-truth document listing every trigger:

```markdown
## Email Label Triggers

| Label | Trigger | Auto-applied? | Source |
|-------|---------|:---:|--------|
| legal | sender:@lawfirm.com, subject contains "contract" | Yes | AI-managed |
| ts-orders | sender:*@shopify.com, subject contains "order" | Yes | AI-managed |
| cgai | sender:garrett@..., body contains CGAI keywords | Yes | AI-managed |
| urgent | AI confidence: high-priority + time-sensitive | Proposed → Board approves | AI-recommended |

### How triggers are updated
1. Agent observes a pattern (e.g., new lawyer hired, emails from @newlawfirm.com)
2. Agent recommends: "Add @newlawfirm.com to legal label triggers"
3. Board approves or modifies
4. Trigger document updated
5. System applies new rule going forward
```

This pattern applies to any configurable system, not just email.

## Convention

1. **README comes first.** No code exists before the README is written and reviewed.
2. **Eval comes second.** No implementation before the success criteria are defined.
3. **Diagrams are required.** Every system has at least a data flow diagram.
4. **Trigger/rule docs are living documents.** Agents recommend changes, Board approves, docs update.
5. **If something is unclear, that's a documentation bug.** Fix the docs, not the person's understanding.
6. **Docs are written for three audiences.** Chris (reference), technical collaborators (operating), non-technical collaborators (interacting).
7. **Keep it real.** Document what IS, not what you wish existed. Mark planned features as "Planned: Phase X."

## Common Mistakes

- **Writing docs after the code.** By then, the docs describe the implementation, not the intention. Write docs first so the implementation matches the intention.
- **Documentation that's too abstract.** "The system processes emails" vs "The system checks for new emails every 30 minutes, classifies each into one of 10 core labels using Haiku, and posts Action Required items to Slack with one-line summaries." Be specific.
- **Treating docs as write-once.** Docs are living. Every phase completion includes a "update docs to reflect current state" step.
- **Over-engineering the documentation system itself.** The docs system should be simple enough that it actually gets maintained. If updating docs is harder than writing code, the docs will rot.

## Related Guides

- `guides/routine-developer/composable-patterns.md` — How routines are architectured
- `guides/skill-developer/writing-a-skill.md` — How skills are structured
- `guides/agent-developer/writing-a-soul-file.md` — How agent values are documented
- `specs/skills-spec.md` — The formal SKILL.md standard
