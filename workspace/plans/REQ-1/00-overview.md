# REQ-1: Tibetan Spirit AI Operations Platform — Build Epic

**Date:** 2026-03-29
**Owner:** Chris Mauzé
**Status:** In Progress
**Sprints:** 7 (across 4 parallel groups)

---

## Scope

Build an autonomous operations platform where Claude-powered workflows handle daily business operations for Tibetan Spirit. Two codebases:
- **tibetan-spirit-ops/** — Python workflows, skills, shared lib (Railway)
- **ts-command-center/** — Next.js 15 dashboard PWA (Vercel, separate repo)

Supabase Pro is the shared coordination bus.

## Sprint Map

```
PG-1:  ████████ S1 Foundation
       ── REVIEW ──
PG-2:               ████████ S2-W Workflows + Intercom    (Claude Code)
                    ████████ S2-D Dashboard Core           (Cursor/Gemini)
                    ████████ S2-K Wiki Tier 1              (Claude Code)
                    ── REVIEW ──
PG-3:                            ████████ S3-W Advanced WF (Claude Code)
                                 ████████ S3-D Dash Mgmt   (Cursor/Gemini + Claude Code)
                                 ── REVIEW ──
PG-4:                                         ████████ S4 Polish + Docs
                                              ── FINAL REVIEW ──
```

| Sprint | File | Tool | Parallel With | Prerequisites |
|--------|------|------|---------------|---------------|
| S1 | `01-s1-foundation.md` | Claude Code | — | None |
| S2-W | `02-s2w-workflows-intercom.md` | Claude Code | S2-D, S2-K | S1 complete |
| S2-D | `03-s2d-dashboard-core.md` | Cursor/Gemini | S2-W, S2-K | S1 Prompt 1D complete |
| S2-K | `04-s2k-wiki-tier1.md` | Claude Code | S2-W, S2-D | S1 Prompt 0A complete |
| S3-W | `05-s3w-advanced-workflows.md` | Claude Code | S3-D | S2-W, S2-K complete |
| S3-D | `06-s3d-dashboard-mgmt-wiki-t2.md` | Cursor/Gemini + Claude Code | S3-W | S2-D, S2-K complete |
| S4 | `07-s4-polish-docs.md` | Both | — | S3-W, S3-D complete |

## Acceptance Criteria

- [ ] 6 workflows running against real Supabase data
- [ ] Dashboard deployed on Vercel with task inbox, health, costs, workflow/agent registry
- [ ] Intercom Essentials integrated for CS email drafts
- [ ] All 57 SKILL.md files at production quality (version 1.0.0)
- [ ] Eval dashboard operational
- [ ] Academy M01-M04 generated in Notion
- [ ] CLAUDE.md regenerated (<300 lines), .env.example created, SYSTEM-STATUS.md updated
- [ ] `scripts/run_all_workflows.py --dry-run` passes for all workflows

## Structural Changes (Paperclip Concepts)

See `00A-structural-changes.md` for the full migration spec:
- `skills/` → `agents/` (agent-centric structure with embedded skills)
- Soul files added per agent (identity + judgment + values)
- Values guardrails framework (constitutional values, frequency caps, content tiers)
- CEO structured decision support format in all workflow outputs

## Key References

- `DEV-PLAN.md` — master plan with full prompt specifications
- `CLAUDE.md` — project context, architecture, skill schema (** marks incomplete items)
- `SYSTEM-STATUS.md` — live database schemas and system state
- `00A-structural-changes.md` — path migration and new artifact spec
- `attachments/intercom-research.md` — Intercom Essentials API research
- `attachments/paperclip-integration-plan.md` — Paperclip concepts adopted vs deferred
- `attachments/values-guardrails-framework.md` — Values constraints for all agents
