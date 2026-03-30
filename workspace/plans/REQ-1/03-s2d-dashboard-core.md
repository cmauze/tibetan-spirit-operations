# Sprint S2-D: Dashboard Core

**Tool:** Cursor Agent (Gemini)
**Parallel Group:** PG-2 (runs in parallel with S2-W and S2-K)
**Prerequisites:** Sprint S1 Prompt 1D complete (three-layer schema in Supabase)
**Complexity:** Complex
**Repo:** `ts-command-center/` (new, separate repo)

---

## Overview

Create the Next.js 15 dashboard PWA from scratch. Deploy to Vercel. Implement the Task Inbox (the most critical view — phone-first approval queue), System Health, Cost Tracker, and Dashboard Home. Chris must be able to approve/reject workflows from his phone by the end of this sprint.

---

## Dev Prompt

```
You are building a React PWA dashboard called "Command Center" for an AI operations
platform. It reads from/writes to a Supabase PostgreSQL database that already has
data populated by Python workflow scripts.

The dashboard NEVER talks to the AI agents directly. Supabase is the shared
coordination bus — agents write to it, the dashboard reads from it, humans
approve through it.

Tech stack: Next.js 15 (App Router), TypeScript strict, Tailwind CSS,
@supabase/ssr, @supabase/supabase-js, Recharts, @radix-ui/themes,
next-intl, zod, date-fns.

=== PROMPT D-1: Next.js Scaffold + Supabase Connection ===

Initialize project:
  npx create-next-app@latest ts-command-center --typescript --tailwind --eslint --app --src-dir

Install dependencies:
  @supabase/ssr @supabase/supabase-js recharts @radix-ui/themes next-intl zod date-fns

Set up:
1. Supabase client utilities:
   - src/lib/supabase/server.ts (server components — uses cookies)
   - src/lib/supabase/client.ts (client components — uses createBrowserClient)
   - src/lib/supabase/middleware.ts (auth session refresh)

2. Auth with Supabase Auth:
   - Email/password login for 3 users: chris, jothi, fiona
   - Login page at /login
   - Middleware protects all routes except /login

3. Layout:
   - App shell with header: logo, company selector (dropdown), user menu
   - Company selector reads from `companies` table
   - Chris sees all companies; team members see only their company (RLS)
   - Selection persists to localStorage, filters all views
   - Mobile: bottom nav bar (Inbox, Health, Costs, More)
   - Desktop: left sidebar nav

4. PWA:
   - manifest.json with app name "TS Command Center", theme color, icons
   - Service worker registration for offline support
   - Add to home screen prompt

5. Internationalization:
   - next-intl with English (default), Chinese (zh), Bahasa Indonesia (id)
   - Locale files in messages/ directory
   - Language selector in user menu

Deploy to Vercel. Connect to Supabase via env vars:
  NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY

Commit: "feat: Next.js scaffold with Supabase auth, i18n, PWA"

=== PROMPT D-2: Task Inbox (Priority 1 — HITL Approval Queue) ===

This is the most critical view. Phone-first approval queue that Chris checks
multiple times daily.

Pages:
  /inbox — List view
  /inbox/[id] — Detail view with approve/reject

List view (/inbox):
- Card view on mobile (<768px), table view on desktop
- Filters: status (Needs Review default), company, assignee, priority, workflow
- Sort: priority (P0 first) → created_at (newest)
- Realtime: subscribe to task_inbox inserts/updates via Supabase Realtime
  When new task arrives, it appears without page refresh
- Badge count in nav showing "Needs Review" count for current company
- Quick-action buttons on each card/row: Approve / Reject without opening detail
- Empty state: "All caught up!" message when no items match filters

Detail view (/inbox/[id]):
- Left/main area: rendered output (output_rendered field, or formatted JSONB)
- Right sidebar (desktop) / bottom sheet (mobile): properties
  - Status badge (color-coded)
  - Priority (P0=red, P1=orange, P2=blue, P3=gray)
  - Assignee
  - Workflow name (linked to /workflows/[id] when it exists)
  - Cost (formatted USD)
  - Created at (relative time + absolute)
  - Wake reason
- Action buttons:
  - Approve → sets status='approved', feedback_by=current_user, feedback_at=now()
  - Reject → opens modal with feedback textarea, required before submit
    Sets status='rejected', feedback=text, feedback_by=current_user
  - Edit → opens inline editor for output modifications before approval
    If modified, save edited version to feedback field, set status='approved'

Mobile optimization:
- Large tap targets (48px minimum for all interactive elements)
- Swipe gestures if feasible (right=approve, left=reject)
- Bottom nav bar: Inbox (with badge), Health, Costs, More

Supabase tables used:
- task_inbox: id, company_id, workflow_id, agent_id, title, status, priority,
  assignee, output (JSONB), output_rendered (TEXT), feedback, feedback_by,
  feedback_at, wake_reason, cost_usd, run_id, due_at, created_at, updated_at

Company selector in header filters inbox to selected company_id.

Commit: "feat: task inbox with approve/reject, realtime, mobile-first"

=== PROMPT D-3: System Health + Cost Tracker + Home ===

Three more views:

System Health (/health):
- Grid of workflow cards (responsive: 1 col mobile, 2 tablet, 3 desktop)
- Each card shows:
  - Workflow name
  - Status badge: green (healthy), yellow (degraded), red (down)
  - Last run time (relative)
  - 7d success rate (percentage + tiny sparkline if possible)
  - Override rate (if available)
- Click card → expanded view with:
  - Recent workflow_runs (last 10) with status, cost, duration
  - Error messages for failed runs
- Auto-refresh via Supabase Realtime on workflow_health changes

Cost Tracker (/costs):
- Recharts AreaChart: daily cost over past 30 days
  - Stacked by company (if multi-company selected)
  - Or stacked by workflow (if single company)
- Budget progress bars: one per workflow
  - spend_records.total_cost_usd / workflows.monthly_budget
  - Color: green <60%, yellow 60-80%, red >80%
- Time range toggle: this week / this month / last 30 days
- Table below chart: top workflows by cost, sortable columns

Dashboard Home (/):
- Four-quadrant responsive grid:
  1. Needs Attention: task_inbox count by priority (P0 red, P1 orange, P2 blue, P3 gray)
     Click → navigates to /inbox filtered by that priority
  2. System Status: traffic light dots for each workflow from workflow_health
     Green/yellow/red. Click → /health
  3. Weekly Spend: total cost this week, budget utilization %, trend vs last week
     Click → /costs
  4. Recent Activity: latest 5 workflow_runs with status icon, name, time
     Click individual → /workflows/[id] (placeholder until Sprint S3-D)
- Company selector filters all quadrants

Commit: "feat: health dashboard, cost tracker, home overview"
```

---

## Test Prompt

```
Verify Sprint S2-D dashboard deployment and functionality.

=== SCAFFOLD (D-1) ===
1. App deploys to Vercel without build errors — check deployment URL
2. Login works for chris (email/password via Supabase Auth)
3. Company selector renders: shows "Tibetan Spirit" and "Personal"
4. Chris can switch companies; selection persists across page navigation
5. Jothi login: sees only "Tibetan Spirit" (RLS enforcement)
6. PWA: manifest.json accessible at /manifest.json
7. Service worker registered (check browser DevTools → Application)
8. i18n: language selector visible, switching to "id" changes labels

=== TASK INBOX (D-2) ===
9. Insert test task via SQL:
   INSERT INTO task_inbox (company_id, title, status, priority, assignee, output, output_rendered)
   VALUES ((SELECT id FROM companies WHERE slug='tibetan-spirit'),
           'Test P&L Review', 'needs_review', 'P1', 'chris',
           '{"revenue": 1500, "margin": 0.45}'::jsonb,
           '<h2>Weekly P&L</h2><p>Revenue: $1,500</p>');
   → Task appears in dashboard within 2 seconds (Realtime subscription)
10. Badge count in nav shows "1" (or correct count)
11. Click task → detail view loads with rendered output
12. Approve flow: click Approve → status='approved' in Supabase, page updates
13. Reject flow: click Reject → feedback modal → enter text → submit
    → status='rejected', feedback contains text
14. Mobile viewport (375px): cards stack vertically, buttons are 48px+ tap targets
15. Company filter: switch to "Personal" → inbox shows only personal tasks (or empty)
16. Filters work: change status to "Approved" → shows approved tasks

=== HEALTH + COSTS + HOME (D-3) ===
17. /health renders: workflow cards appear for seeded workflows
18. /costs renders: chart area visible (empty data OK initially)
19. Budget bars render with correct ceiling values from workflow configs
20. / (home): all four quadrants render without errors
21. Company selector filters all quadrants when switched
22. Realtime: update workflow_health status via SQL → card color changes without refresh
23. Click quadrant link → navigates to correct page
24. Mobile: bottom nav bar visible with Inbox/Health/Costs/More
25. Desktop: sidebar nav visible with all links

=== CROSS-CUTTING ===
26. No console errors on any page
27. All pages handle empty data gracefully (no crashes)
28. Loading states visible during data fetches
```
