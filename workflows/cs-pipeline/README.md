# CS Pipeline Workflow

Orchestrates the full customer service email handling pipeline for Tibetan Spirit.

## Chain

```
cs-triage → enrichment (Supabase + Gmail) → cs-drafter → approval queue
```

## Skills/Agents Used

| Stage | Component | Type |
|-------|-----------|------|
| Triage | `cs-triage` | Skill |
| Enrichment | Supabase MCP + Gmail MCP | Direct tool calls |
| Draft | `cs-drafter` | Agent |
| Queue | `data/cs-drafts-log.json` | Output file |

## Escalation Paths

- **Spiritual guidance** → Dr. Hun Lye (email, 48-72h response)
- **Wholesale >$500** → Chris (Slack)
- **Data deletion request** → Chris (Slack, immediate)
- **Complaint** → Priority queue, Chris review first

## Compliance

- CCPA ADMT: all drafts require human approval before sending
- `"ai_generated": true` logged for every draft
- CCPA gate hook (`ccpa-gate.sh`) blocks direct email sending at the tool layer
