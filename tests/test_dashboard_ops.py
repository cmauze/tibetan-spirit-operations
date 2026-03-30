"""Tests for ts_shared.dashboard_ops — mock Supabase, no live DB."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest


def _make_table_mock():
    """Create a single chainable table mock."""
    m = MagicMock()
    m.select.return_value = m
    m.insert.return_value = m
    m.update.return_value = m
    m.upsert.return_value = m
    m.eq.return_value = m
    m.limit.return_value = m
    m.execute.return_value = MagicMock(data=[], count=0)
    return m


def _make_mock_client():
    """Create a mock Supabase client with chainable table methods."""
    client = MagicMock()
    tables = [
        "companies", "agents", "skills", "agent_skills",
        "workflows", "workflow_steps",
        "task_inbox", "workflow_runs", "workflow_health", "spend_records",
    ]
    _table_mocks = {name: _make_table_mock() for name in tables}

    def table_factory(name):
        if name not in _table_mocks:
            _table_mocks[name] = _make_table_mock()
        return _table_mocks[name]

    client.table.side_effect = table_factory
    client._table_mocks = _table_mocks
    return client


@pytest.fixture
def mock_client():
    mock = _make_mock_client()
    with patch("ts_shared.dashboard_ops._get_client", return_value=mock):
        yield mock


# ---------------------------------------------------------------------------
# create_task
# ---------------------------------------------------------------------------


class TestCreateTask:
    def test_creates_task_and_returns_id(self, mock_client):
        from ts_shared.dashboard_ops import create_task

        # Set up company lookup
        companies = mock_client._table_mocks["companies"]
        companies.execute.return_value = MagicMock(
            data=[{"id": "comp-111"}]
        )

        # Set up workflow lookup
        workflows = mock_client._table_mocks["workflows"]
        workflows.execute.return_value = MagicMock(
            data=[{"id": "wf-222"}]
        )

        # Set up task_inbox insert
        inbox = mock_client._table_mocks["task_inbox"]
        inbox.execute.return_value = MagicMock(
            data=[{"id": "task-333"}]
        )

        task_id = create_task(
            company_slug="tibetan-spirit",
            workflow_slug="daily_summary",
            title="Daily Summary — 2026-03-30",
            output={"revenue": 1234.56},
            output_rendered="Revenue: $1,234.56",
            assignee="ceo",
        )

        assert task_id == "task-333"
        inbox.insert.assert_called_once()
        row = inbox.insert.call_args[0][0]
        assert row["company_id"] == "comp-111"
        assert row["title"] == "Daily Summary — 2026-03-30"
        assert row["status"] == "needs_review"
        assert row["priority"] == "P2"
        assert row["assignee"] == "ceo"
        assert row["output"] == {"revenue": 1234.56}

    def test_auto_logged_status(self, mock_client):
        from ts_shared.dashboard_ops import create_task

        mock_client._table_mocks["companies"].execute.return_value = MagicMock(
            data=[{"id": "comp-111"}]
        )
        mock_client._table_mocks["workflows"].execute.return_value = MagicMock(
            data=[]
        )
        mock_client._table_mocks["task_inbox"].execute.return_value = MagicMock(
            data=[{"id": "task-444"}]
        )

        task_id = create_task(
            company_slug="tibetan-spirit",
            workflow_slug="daily_summary",
            title="Test",
            output={},
            output_rendered="",
            assignee="ceo",
            status="auto_logged",
        )

        row = mock_client._table_mocks["task_inbox"].insert.call_args[0][0]
        assert row["status"] == "auto_logged"

    def test_raises_on_missing_company(self, mock_client):
        from ts_shared.dashboard_ops import create_task

        mock_client._table_mocks["companies"].execute.return_value = MagicMock(data=[])

        with pytest.raises(ValueError, match="Company not found"):
            create_task(
                company_slug="nonexistent",
                workflow_slug="x",
                title="T",
                output={},
                output_rendered="",
                assignee="ceo",
            )


# ---------------------------------------------------------------------------
# update_task_status
# ---------------------------------------------------------------------------


class TestUpdateTaskStatus:
    def test_updates_status(self, mock_client):
        from ts_shared.dashboard_ops import update_task_status

        update_task_status("task-123", "approved")

        inbox = mock_client._table_mocks["task_inbox"]
        inbox.update.assert_called_once()
        update_args = inbox.update.call_args[0][0]
        assert update_args["status"] == "approved"

    def test_includes_feedback(self, mock_client):
        from ts_shared.dashboard_ops import update_task_status

        update_task_status(
            "task-123", "rejected",
            feedback="Numbers look off",
            feedback_by="ceo",
        )

        inbox = mock_client._table_mocks["task_inbox"]
        update_args = inbox.update.call_args[0][0]
        assert update_args["feedback"] == "Numbers look off"
        assert update_args["feedback_by"] == "ceo"
        assert "feedback_at" in update_args


# ---------------------------------------------------------------------------
# log_workflow_run
# ---------------------------------------------------------------------------


class TestLogWorkflowRun:
    def test_logs_run_and_returns_id(self, mock_client):
        from ts_shared.dashboard_ops import log_workflow_run

        mock_client._table_mocks["companies"].execute.return_value = MagicMock(
            data=[{"id": "comp-111"}]
        )
        mock_client._table_mocks["workflows"].execute.return_value = MagicMock(
            data=[{"id": "wf-222", "agent_id": "agent-333"}]
        )
        mock_client._table_mocks["workflow_runs"].execute.return_value = MagicMock(
            data=[{"id": "run-444"}]
        )

        run_id = log_workflow_run(
            company_slug="tibetan-spirit",
            workflow_slug="daily_summary",
            status="completed",
            wake_reason="cron",
            steps_completed=1,
            steps_total=1,
            step_results=[{"step": "summarize", "status": "ok"}],
            input_tokens=500,
            output_tokens=200,
            total_cost_usd=0.005,
            model_used="claude-haiku-4-5-20251001",
            duration_ms=1200,
        )

        assert run_id == "run-444"
        runs = mock_client._table_mocks["workflow_runs"]
        runs.insert.assert_called_once()
        row = runs.insert.call_args[0][0]
        assert row["status"] == "completed"
        assert row["total_cost_usd"] == 0.005
        assert row["duration_ms"] == 1200
        assert row["completed_at"] is not None

    def test_raises_on_missing_company(self, mock_client):
        from ts_shared.dashboard_ops import log_workflow_run

        mock_client._table_mocks["companies"].execute.return_value = MagicMock(data=[])

        with pytest.raises(ValueError, match="Company not found"):
            log_workflow_run(
                company_slug="nonexistent",
                workflow_slug="x",
                status="completed",
                wake_reason="cron",
                steps_completed=0,
                steps_total=0,
                step_results=[],
                input_tokens=0,
                output_tokens=0,
                total_cost_usd=0,
                model_used="haiku",
            )


# ---------------------------------------------------------------------------
# update_workflow_health
# ---------------------------------------------------------------------------


class TestUpdateWorkflowHealth:
    def test_inserts_when_no_existing_record(self, mock_client):
        from ts_shared.dashboard_ops import update_workflow_health

        # workflow lookup
        mock_client._table_mocks["workflows"].execute.return_value = MagicMock(
            data=[{"id": "wf-222", "company_id": "comp-111"}]
        )
        # no existing health record
        mock_client._table_mocks["workflow_health"].execute.return_value = MagicMock(
            data=[]
        )

        update_workflow_health(
            workflow_slug="daily_summary",
            status="healthy",
            last_result="completed",
            cost=0.005,
            duration_ms=1200,
        )

        health = mock_client._table_mocks["workflow_health"]
        health.insert.assert_called_once()

    def test_updates_when_existing_record(self, mock_client):
        from ts_shared.dashboard_ops import update_workflow_health

        mock_client._table_mocks["workflows"].execute.return_value = MagicMock(
            data=[{"id": "wf-222", "company_id": "comp-111"}]
        )
        mock_client._table_mocks["workflow_health"].execute.return_value = MagicMock(
            data=[{"id": "health-555"}]
        )

        update_workflow_health(
            workflow_slug="daily_summary",
            status="degraded",
            last_result="failed: timeout",
        )

        health = mock_client._table_mocks["workflow_health"]
        health.update.assert_called()

    def test_warns_on_missing_workflow(self, mock_client):
        from ts_shared.dashboard_ops import update_workflow_health

        mock_client._table_mocks["workflows"].execute.return_value = MagicMock(data=[])

        # Should not raise — just log warning
        update_workflow_health(
            workflow_slug="nonexistent",
            status="healthy",
            last_result="ok",
        )


# ---------------------------------------------------------------------------
# log_spend
# ---------------------------------------------------------------------------


class TestLogSpend:
    def test_upserts_spend_record(self, mock_client):
        from ts_shared.dashboard_ops import log_spend

        mock_client._table_mocks["companies"].execute.return_value = MagicMock(
            data=[{"id": "comp-111"}]
        )
        mock_client._table_mocks["workflows"].execute.return_value = MagicMock(
            data=[{"id": "wf-222"}]
        )
        mock_client._table_mocks["spend_records"].execute.return_value = MagicMock(
            data=[{"id": "spend-666"}]
        )

        log_spend(
            period="2026-03-30",
            period_type="daily",
            company_slug="tibetan-spirit",
            workflow_slug="daily_summary",
            run_count=1,
            success_count=1,
            failure_count=0,
            total_input_tokens=500,
            total_output_tokens=200,
            total_cost_usd=0.005,
            models_used=["claude-haiku-4-5-20251001"],
        )

        spend = mock_client._table_mocks["spend_records"]
        spend.upsert.assert_called_once()
        row = spend.upsert.call_args[0][0]
        assert row["run_count"] == 1
        assert row["total_cost_usd"] == 0.005
        assert row["models_used"] == ["claude-haiku-4-5-20251001"]

    def test_raises_on_missing_company(self, mock_client):
        from ts_shared.dashboard_ops import log_spend

        mock_client._table_mocks["companies"].execute.return_value = MagicMock(data=[])

        with pytest.raises(ValueError, match="Company not found"):
            log_spend(
                period="2026-03-30",
                period_type="daily",
                company_slug="nonexistent",
                workflow_slug="x",
                run_count=0,
                success_count=0,
                failure_count=0,
            )
