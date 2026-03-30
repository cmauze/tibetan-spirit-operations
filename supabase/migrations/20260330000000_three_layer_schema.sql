-- Three-Layer Schema: Registry + Runtime + Eval
-- Migration: 20260330000000_three_layer_schema
-- Depends on: 20260323064342_initial_schema (existing orders, products tables)

-- ============================================================================
-- TRIGGER FUNCTION
-- Ensure trigger function exists (originally from initial_schema migration)
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ENUMS
-- ============================================================================

CREATE TYPE task_status AS ENUM (
    'needs_review', 'in_progress', 'approved', 'rejected', 'auto_logged'
);

CREATE TYPE workflow_run_status AS ENUM (
    'pending', 'running', 'completed', 'failed', 'cancelled'
);

CREATE TYPE health_status AS ENUM (
    'healthy', 'degraded', 'failing', 'disabled'
);

CREATE TYPE workflow_trigger_type AS ENUM (
    'cron', 'webhook', 'manual', 'event'
);

CREATE TYPE step_type AS ENUM (
    'python', 'llm', 'api_call', 'human_review'
);

CREATE TYPE period_type AS ENUM (
    'daily', 'weekly', 'monthly'
);

CREATE TYPE entity_status AS ENUM (
    'active', 'inactive', 'archived'
);

CREATE TYPE eval_status AS ENUM (
    'pending', 'running', 'completed', 'failed'
);

CREATE TYPE priority_level AS ENUM (
    'P0', 'P1', 'P2', 'P3'
);

CREATE TYPE approval_tier AS ENUM (
    'tier_1', 'tier_2', 'tier_3'
);


-- ============================================================================
-- REGISTRY LAYER — what exists
-- ============================================================================

-- companies
CREATE TABLE companies (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slug        text NOT NULL UNIQUE,
    name        text NOT NULL,
    status      entity_status NOT NULL DEFAULT 'active',
    config      jsonb DEFAULT '{}',
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- agents
CREATE TABLE agents (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    slug            text NOT NULL,
    name            text NOT NULL,
    status          entity_status NOT NULL DEFAULT 'active',
    soul_path       text,
    config_path     text,
    model           text,
    budget_usd      numeric,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (company_id, slug)
);

CREATE TRIGGER trg_agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- skills
CREATE TABLE skills (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    slug            text NOT NULL,
    name            text NOT NULL,
    skill_md_path   text,
    category        text,
    version         text DEFAULT '0.1.0',
    status          entity_status NOT NULL DEFAULT 'active',
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (company_id, slug)
);

CREATE TRIGGER trg_skills_updated_at
    BEFORE UPDATE ON skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- agent_skills (junction)
CREATE TABLE agent_skills (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id        uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    skill_id        uuid NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    config_overrides jsonb DEFAULT '{}',
    created_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (agent_id, skill_id)
);

-- workflows
CREATE TABLE workflows (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id          uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    agent_id            uuid REFERENCES agents(id) ON DELETE SET NULL,
    slug                text NOT NULL,
    name                text NOT NULL,
    trigger_type        workflow_trigger_type NOT NULL DEFAULT 'cron',
    trigger_config      jsonb DEFAULT '{}',
    approval_required   boolean NOT NULL DEFAULT true,
    approval_tier       approval_tier DEFAULT 'tier_3',
    default_assignee    text,
    default_priority    priority_level DEFAULT 'P2',
    max_cost_per_run    numeric,
    monthly_budget      numeric,
    status              entity_status NOT NULL DEFAULT 'active',
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now(),
    UNIQUE (company_id, slug)
);

CREATE TRIGGER trg_workflows_updated_at
    BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- workflow_steps
CREATE TABLE workflow_steps (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id     uuid NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    step_order      int NOT NULL,
    slug            text NOT NULL,
    step_type       step_type NOT NULL DEFAULT 'llm',
    model           text,
    temperature     numeric DEFAULT 0,
    max_tokens      int DEFAULT 2000,
    config          jsonb DEFAULT '{}',
    eval_criteria   jsonb DEFAULT '{}',
    created_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (workflow_id, step_order)
);


-- ============================================================================
-- RUNTIME LAYER — what happened
-- ============================================================================

-- task_inbox
CREATE TABLE task_inbox (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    workflow_id     uuid REFERENCES workflows(id) ON DELETE SET NULL,
    agent_id        uuid REFERENCES agents(id) ON DELETE SET NULL,
    title           text NOT NULL,
    status          task_status NOT NULL DEFAULT 'needs_review',
    priority        priority_level NOT NULL DEFAULT 'P2',
    assignee        text,
    output          jsonb DEFAULT '{}',
    output_rendered text,
    feedback        text,
    feedback_by     text,
    feedback_at     timestamptz,
    wake_reason     text DEFAULT 'scheduled',
    cost_usd        numeric DEFAULT 0,
    run_id          uuid,
    due_at          timestamptz,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_task_inbox_updated_at
    BEFORE UPDATE ON task_inbox
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- workflow_runs
CREATE TABLE workflow_runs (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id     uuid NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    agent_id        uuid REFERENCES agents(id) ON DELETE SET NULL,
    company_id      uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    status          workflow_run_status NOT NULL DEFAULT 'pending',
    wake_reason     text,
    steps_completed int DEFAULT 0,
    steps_total     int DEFAULT 0,
    current_step    text,
    step_results    jsonb DEFAULT '[]',
    input_tokens    int DEFAULT 0,
    output_tokens   int DEFAULT 0,
    total_cost_usd  numeric DEFAULT 0,
    model_used      text,
    error_message   text,
    error_step      text,
    started_at      timestamptz DEFAULT now(),
    completed_at    timestamptz,
    duration_ms     int,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_workflow_runs_updated_at
    BEFORE UPDATE ON workflow_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- workflow_health
CREATE TABLE workflow_health (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id         uuid NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    company_id          uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    status              health_status NOT NULL DEFAULT 'healthy',
    last_run_at         timestamptz,
    last_result         text,
    failures_7d         int DEFAULT 0,
    avg_cost_per_run    numeric DEFAULT 0,
    avg_duration_ms     int DEFAULT 0,
    success_rate_7d     numeric DEFAULT 1.0,
    override_rate_30d   numeric DEFAULT 0,
    notes               text,
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now(),
    UNIQUE (workflow_id)
);

CREATE TRIGGER trg_workflow_health_updated_at
    BEFORE UPDATE ON workflow_health
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- spend_records
CREATE TABLE spend_records (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    period              date NOT NULL,
    period_type         period_type NOT NULL,
    company_id          uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    workflow_id         uuid REFERENCES workflows(id) ON DELETE SET NULL,
    run_count           int DEFAULT 0,
    success_count       int DEFAULT 0,
    failure_count       int DEFAULT 0,
    total_input_tokens  bigint DEFAULT 0,
    total_output_tokens bigint DEFAULT 0,
    total_cost_usd      numeric DEFAULT 0,
    budget_usd          numeric,
    models_used         jsonb DEFAULT '[]',
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now(),
    UNIQUE (period, period_type, company_id, workflow_id)
);

CREATE TRIGGER trg_spend_records_updated_at
    BEFORE UPDATE ON spend_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- EVAL LAYER — how good is it
-- ============================================================================

-- eval_suites
CREATE TABLE eval_suites (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id         uuid REFERENCES workflows(id) ON DELETE SET NULL,
    skill_id            uuid REFERENCES skills(id) ON DELETE SET NULL,
    slug                text NOT NULL UNIQUE,
    name                text NOT NULL,
    test_cases          jsonb DEFAULT '[]',
    scoring_criteria    jsonb DEFAULT '{}',
    pass_thresholds     jsonb DEFAULT '{}',
    status              entity_status NOT NULL DEFAULT 'active',
    created_at          timestamptz NOT NULL DEFAULT now(),
    updated_at          timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_eval_suites_updated_at
    BEFORE UPDATE ON eval_suites
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- prompt_versions
CREATE TABLE prompt_versions (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id             uuid REFERENCES workflows(id) ON DELETE CASCADE,
    workflow_step_id        uuid REFERENCES workflow_steps(id) ON DELETE SET NULL,
    version                 text NOT NULL,
    system_prompt           text,
    user_prompt_template    text,
    model                   text,
    temperature             numeric DEFAULT 0,
    max_tokens              int DEFAULT 2000,
    few_shot_examples       jsonb DEFAULT '[]',
    hypothesis              text,
    parent_version_id       uuid REFERENCES prompt_versions(id) ON DELETE SET NULL,
    is_current              boolean DEFAULT false,
    created_at              timestamptz NOT NULL DEFAULT now(),
    updated_at              timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_prompt_versions_updated_at
    BEFORE UPDATE ON prompt_versions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- eval_runs
CREATE TABLE eval_runs (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    eval_suite_id           uuid NOT NULL REFERENCES eval_suites(id) ON DELETE CASCADE,
    prompt_version_id       uuid REFERENCES prompt_versions(id) ON DELETE SET NULL,
    status                  eval_status NOT NULL DEFAULT 'pending',
    aggregate_scores        jsonb DEFAULT '{}',
    pass                    boolean,
    total_cost_usd          numeric DEFAULT 0,
    total_tokens            int DEFAULT 0,
    compared_to_version_id  uuid REFERENCES prompt_versions(id) ON DELETE SET NULL,
    improvement_delta       jsonb DEFAULT '{}',
    started_at              timestamptz DEFAULT now(),
    completed_at            timestamptz,
    created_at              timestamptz NOT NULL DEFAULT now(),
    updated_at              timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER trg_eval_runs_updated_at
    BEFORE UPDATE ON eval_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- eval_results
CREATE TABLE eval_results (
    id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    eval_run_id             uuid NOT NULL REFERENCES eval_runs(id) ON DELETE CASCADE,
    test_case_index         int NOT NULL,
    input                   jsonb DEFAULT '{}',
    expected_output         jsonb DEFAULT '{}',
    actual_output           jsonb DEFAULT '{}',
    scores                  jsonb DEFAULT '{}',
    pass                    boolean,
    evaluator_model         text,
    evaluator_reasoning     text,
    human_score_override    jsonb,
    human_notes             text,
    created_at              timestamptz NOT NULL DEFAULT now()
);


-- ============================================================================
-- INDEXES — hot query paths
-- ============================================================================

-- task_inbox
CREATE INDEX idx_task_inbox_needs_review
    ON task_inbox (status) WHERE status = 'needs_review';
CREATE INDEX idx_task_inbox_assignee_status
    ON task_inbox (assignee, status);
CREATE INDEX idx_task_inbox_company_status
    ON task_inbox (company_id, status);

-- workflow_runs
CREATE INDEX idx_workflow_runs_running
    ON workflow_runs (status) WHERE status = 'running';
CREATE INDEX idx_workflow_runs_workflow_started
    ON workflow_runs (workflow_id, started_at DESC);
CREATE INDEX idx_workflow_runs_company
    ON workflow_runs (company_id, started_at DESC);

-- spend_records
CREATE INDEX idx_spend_records_period_company
    ON spend_records (period, company_id);
CREATE INDEX idx_spend_records_workflow
    ON spend_records (workflow_id, period DESC);

-- eval_runs
CREATE INDEX idx_eval_runs_suite_started
    ON eval_runs (eval_suite_id, started_at DESC);

-- eval_results
CREATE INDEX idx_eval_results_run
    ON eval_results (eval_run_id, test_case_index);

-- agents
CREATE INDEX idx_agents_company
    ON agents (company_id);

-- workflows
CREATE INDEX idx_workflows_company
    ON workflows (company_id);

-- workflow_health
CREATE INDEX idx_workflow_health_company
    ON workflow_health (company_id);


-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

-- Enable RLS on all new tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_inbox ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_health ENABLE ROW LEVEL SECURITY;
ALTER TABLE spend_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE eval_suites ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE eval_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE eval_results ENABLE ROW LEVEL SECURITY;

-- Admin policy: admin role sees all rows
CREATE POLICY admin_all ON companies FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON agents FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON skills FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON agent_skills FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON workflows FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON workflow_steps FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON task_inbox FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON workflow_runs FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON workflow_health FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON spend_records FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON eval_suites FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON prompt_versions FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON eval_runs FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');
CREATE POLICY admin_all ON eval_results FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');

-- Team policy: members see rows for their company
CREATE POLICY team_own_company ON companies FOR SELECT TO authenticated
    USING (id::text = auth.jwt() ->> 'company_id');

CREATE POLICY team_own_company ON agents FOR SELECT TO authenticated
    USING (company_id::text = auth.jwt() ->> 'company_id');

CREATE POLICY team_own_company ON skills FOR SELECT TO authenticated
    USING (company_id::text = auth.jwt() ->> 'company_id');

CREATE POLICY team_own_company ON agent_skills FOR SELECT TO authenticated
    USING (
        agent_id IN (
            SELECT id FROM agents WHERE company_id::text = auth.jwt() ->> 'company_id'
        )
    );

CREATE POLICY team_own_company ON workflows FOR SELECT TO authenticated
    USING (company_id::text = auth.jwt() ->> 'company_id');

CREATE POLICY team_own_company ON workflow_steps FOR SELECT TO authenticated
    USING (
        workflow_id IN (
            SELECT id FROM workflows WHERE company_id::text = auth.jwt() ->> 'company_id'
        )
    );

CREATE POLICY team_own_company ON task_inbox FOR ALL TO authenticated
    USING (company_id::text = auth.jwt() ->> 'company_id');

CREATE POLICY team_own_company ON workflow_runs FOR SELECT TO authenticated
    USING (company_id::text = auth.jwt() ->> 'company_id');

CREATE POLICY team_own_company ON workflow_health FOR SELECT TO authenticated
    USING (company_id::text = auth.jwt() ->> 'company_id');

CREATE POLICY team_own_company ON spend_records FOR SELECT TO authenticated
    USING (company_id::text = auth.jwt() ->> 'company_id');

CREATE POLICY team_own_company ON eval_suites FOR SELECT TO authenticated
    USING (
        workflow_id IN (
            SELECT id FROM workflows WHERE company_id::text = auth.jwt() ->> 'company_id'
        )
    );

CREATE POLICY team_own_company ON prompt_versions FOR SELECT TO authenticated
    USING (
        workflow_id IN (
            SELECT id FROM workflows WHERE company_id::text = auth.jwt() ->> 'company_id'
        )
    );

CREATE POLICY team_own_company ON eval_runs FOR SELECT TO authenticated
    USING (
        eval_suite_id IN (
            SELECT es.id FROM eval_suites es
            JOIN workflows w ON es.workflow_id = w.id
            WHERE w.company_id::text = auth.jwt() ->> 'company_id'
        )
    );

CREATE POLICY team_own_company ON eval_results FOR SELECT TO authenticated
    USING (
        eval_run_id IN (
            SELECT er.id FROM eval_runs er
            JOIN eval_suites es ON er.eval_suite_id = es.id
            JOIN workflows w ON es.workflow_id = w.id
            WHERE w.company_id::text = auth.jwt() ->> 'company_id'
        )
    );

-- Service role bypasses RLS (for workflow scripts using service key)
-- This is handled by Supabase automatically for the service_role key.


-- ============================================================================
-- REALTIME PUBLICATION
-- ============================================================================

ALTER PUBLICATION supabase_realtime ADD TABLE task_inbox;
ALTER PUBLICATION supabase_realtime ADD TABLE workflow_health;
ALTER PUBLICATION supabase_realtime ADD TABLE workflow_runs;


-- ============================================================================
-- REFRESH MATERIALIZED VIEW FUNCTION (for views.py)
-- ============================================================================

CREATE OR REPLACE FUNCTION refresh_materialized_view(view_name text)
RETURNS void AS $$
BEGIN
    EXECUTE format('REFRESH MATERIALIZED VIEW CONCURRENTLY %I', view_name);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Companies
INSERT INTO companies (slug, name, status, config) VALUES
    ('tibetan-spirit', 'Tibetan Spirit', 'active', '{"shopify_store": "tibetanspirits.myshopify.com"}'),
    ('personal', 'Personal', 'active', '{}');

-- Agents for tibetan-spirit
WITH ts AS (SELECT id FROM companies WHERE slug = 'tibetan-spirit')
INSERT INTO agents (company_id, slug, name, status, soul_path, config_path, model, budget_usd) VALUES
    ((SELECT id FROM ts), 'customer-service', 'Customer Service', 'active',
     'agents/customer-service/soul.md', 'agents/customer-service/config.yaml',
     'claude-haiku-4-5-20251001', 0.25),
    ((SELECT id FROM ts), 'operations', 'Operations', 'active',
     'agents/operations/soul.md', 'agents/operations/config.yaml',
     'claude-sonnet-4-6', 0.50),
    ((SELECT id FROM ts), 'finance', 'Finance', 'active',
     'agents/finance/soul.md', 'agents/finance/config.yaml',
     'claude-sonnet-4-6', 1.00),
    ((SELECT id FROM ts), 'marketing', 'Marketing', 'active',
     'agents/marketing/soul.md', 'agents/marketing/config.yaml',
     'claude-sonnet-4-6', 0.75),
    ((SELECT id FROM ts), 'ecommerce', 'Ecommerce', 'active',
     'agents/ecommerce/soul.md', 'agents/ecommerce/config.yaml',
     'claude-sonnet-4-6', 0.50),
    ((SELECT id FROM ts), 'category-management', 'Category Management', 'active',
     'agents/category-management/soul.md', 'agents/category-management/config.yaml',
     'claude-sonnet-4-6', 1.00);
