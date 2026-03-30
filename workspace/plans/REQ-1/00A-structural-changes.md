# REQ-1 Addendum: Structural Changes (Paperclip Concepts)

**Date:** 2026-03-30
**Applies to:** All sprint files (01-07)
**Status:** This addendum SUPERSEDES path references in the original sprint files.

---

## Path Migration

All sprint prompts that reference `skills/` must use the new `agents/` structure:

| Old Path | New Path |
|----------|----------|
| `skills/shared/brand-guidelines/SKILL.md` | `agents/shared/brand-guidelines/SKILL.md` |
| `skills/customer-service/ticket-triage/SKILL.md` | `agents/customer-service/skills/ticket-triage/SKILL.md` |
| `skills/finance/cogs-tracking/SKILL.md` | `agents/finance/skills/cogs-tracking/SKILL.md` |
| `skills/operations/inventory-management/SKILL.md` | `agents/operations/skills/inventory-management/SKILL.md` |
| `skills/marketing/meta-ads/SKILL.md` | `agents/marketing/skills/meta-ads/SKILL.md` |
| `skills/ecommerce/cross-channel-parity/SKILL.md` | `agents/ecommerce/skills/cross-channel-parity/SKILL.md` |
| `skills/category-management/pricing-strategy/SKILL.md` | `agents/category-management/skills/pricing-strategy/SKILL.md` |

**Pattern:** Shared skills: `agents/shared/{skill}/SKILL.md`
**Pattern:** Agent-specific skills: `agents/{agent}/skills/{skill}/SKILL.md`

## New Artifacts (Added to Sprint S1 Prompt 0A)

### Soul Files — one per agent (6 total)

Each agent gets `agents/{agent}/soul.md`:

```markdown
# {Agent Name} — Soul File

## Identity
I am the {role description} of Tibetan Spirit. {2-3 sentences about
character, judgment framework, and primary responsibility.}

## Values (non-negotiable)
I NEVER: {agent-specific prohibitions beyond shared values}
I ALWAYS: {agent-specific commitments}

## Judgment Principles
{How this agent makes decisions at the margins — when rules don't
clearly apply, what does this agent default to?}
```

Soul files for the 6 agents:

1. **customer-service/soul.md** — Voice of Tibetan Spirit to customers. Warmth over speed. Never guesses on dharma. Always escalates cultural uncertainty. Bilingual awareness.
2. **operations/soul.md** — Keeps the machinery running. Watches for problems before they become crises. Respects multilingual team (Bahasa Indonesia for Jothi, Chinese for Fiona).
3. **finance/soul.md** — Financial conscience. Accuracy over speed. Surfaces discrepancies immediately. Never makes financial decisions, only informs them.
4. **marketing/soul.md** — Values-constrained marketer. Practitioner trust > conversion rate. Enforces frequency caps. Restraint is competitive advantage.
5. **ecommerce/soul.md** — Channel-aware optimizer. SEO never compromises cultural accuracy. Product framing follows practice-first rules.
6. **category-management/soul.md** — Strategic thinker. Margin-aware. Ethical sourcing. Long-term category health over short-term revenue.

### Agent config.yaml — one per agent (6 total)

```yaml
name: {agent-slug}
description: "{one-line description}"
model: {claude-sonnet-4-6 | claude-haiku-4-5-20251001}
max_turns: {10-20}
budget_usd: {per-invocation cap}
skills:
  - shared/brand-guidelines    # Always first — constitutional values
  - shared/{other-shared-skill}
  - {agent}/{skill}
workflows:
  - {workflow_name}
```

### Values Guardrails

`agents/shared/brand-guidelines/SKILL.md` gets a constitutional values section at the top:
- Override priority: ABSOLUTE
- Frequency caps (email, ads, social)
- Content tier classification
- Product framing rules
- Dharma Giving integrity rules
- Sacred terminology preservation list

See `attachments/values-guardrails-framework.md` for full specification.

### CEO Decision Support

All workflow `run.py` outputs must end with structured decision support:
```
STATUS: GREEN/YELLOW/RED
DECISIONS NEEDED: {if any}
VALUES CHECK: Cultural sensitivity [PASS/FLAG] | Frequency [PASS/FLAG]
COST: $X.XX
```

## Sprint-Specific Changes

### S1 Prompt 0A (largest change)
- Add step 0.5: RESTRUCTURE `skills/` → `agents/`
  - Create `agents/` directory at repo root
  - Move `skills/shared/` → `agents/shared/`
  - For each agent (customer-service, operations, finance, marketing, ecommerce, category-management):
    - Create `agents/{agent}/` directory
    - Create `agents/{agent}/soul.md`
    - Create `agents/{agent}/config.yaml`
    - Move `skills/{domain}/` → `agents/{agent}/skills/`
  - Remove empty `skills/` directory
  - Update all `depends_on` paths in SKILL.md frontmatter
  - Update `server/server.py` AGENT_CONFIGS skill paths
  - Update all `scripts/validate_*.py` to scan `agents/` instead of `skills/`

### S1 Prompt 1A (claude_client.py)
- `load_skill()` looks in `agents/` tree instead of `skills/`
- `get_skill_index()` scans `agents/*/skills/` + `agents/shared/`
- Shared skills (`agents/shared/brand-guidelines`) must ALWAYS be loaded first (structural guarantee)

### S1 Prompt 2A-2B (workflows)
- Config.yaml skill references use new paths:
  `skills: [shared/brand-guidelines, shared/channel-config]`
  (the loader prepends `agents/` and appends `/SKILL.md` internally)

### S2-W Prompt 2C (CS workflow)
- Skill references: `agents/customer-service/skills/ticket-triage/SKILL.md`
- Values compliance check added to CS draft output format

### S2-K (Wiki Tier 1) and S3-D (Wiki Tier 2), S4 (Wiki Tier 3)
- All skill paths updated
- Soul files included in wiki deepening scope (review + polish)

### All workflow run.py files
- Add values-compliance section to output JSONB
- Add structured CEO decision support format

## Validation Script Updates

`scripts/validate_skill.py` must be updated to:
1. Scan `agents/*/skills/*/SKILL.md` and `agents/shared/*/SKILL.md`
2. Validate soul.md files exist for each agent
3. Validate config.yaml files exist and reference valid skill paths

`scripts/validate_cross_refs.py` must be updated to scan the new paths.
