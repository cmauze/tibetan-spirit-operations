# CS Pipeline Workflow

Orchestrates the full customer service email handling pipeline.

## Chain

```
cs-triage → enrichment (database + Gmail) → cs-drafter → approval queue
```

## Skills/Agents Used

| Stage | Component | Type |
|-------|-----------|------|
| Triage | `cs-triage` | Skill |
| Enrichment | database MCP + Gmail MCP | Direct tool calls |
| Draft | `cs-drafter` | Agent |
| Queue | CS drafts log file | Output file |

## Escalation Paths

- **Spiritual guidance** → `brand-specialist` (email, 48-72h response)
- **Wholesale >$500** → `general-manager` (Slack)
- **Data deletion request** → `general-manager` (Slack, immediate)
- **Complaint** → Priority queue, `general-manager` review first

## Compliance

- compliance: all drafts require human approval before sending
- `"ai_generated": true` logged for every draft
- Compliance gate hook blocks direct email sending at the tool layer
