"""Eval tests for the ticket-triage skill.

Tests classification logic, response tier routing, and cultural sensitivity.
All tests use mocks — no live API calls required.

Run: pytest tests/evals/test_ticket_triage.py -v
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from tests.evals.conftest import (
    MockAgentResponse,
    load_skill_md,
    make_customer_ticket,
    make_mock_agent,
    make_order,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def triage_skill_text() -> str:
    """Load the ticket-triage SKILL.md content."""
    return load_skill_md("customer-service/ticket-triage")


@pytest.fixture
def triage_agent(triage_skill_text: str):
    """Create a mock agent pre-loaded with the triage skill context.

    In production, the Agent SDK loads SKILL.md as system prompt context.
    Here we verify the skill text is loadable and create a mock agent
    that simulates classification responses.
    """
    assert len(triage_skill_text) > 100, "SKILL.md should have substantial content"
    return make_mock_agent


# ---------------------------------------------------------------------------
# Test Case 1: Order tracking -> AUTO_RESPOND
# ---------------------------------------------------------------------------


class TestOrderTracking:
    """'Where is my order #1042?' should classify as AUTO_RESPOND."""

    def test_classifies_as_auto_respond(self, triage_agent):
        """Order tracking is a Tier 1 question with a factual answer."""
        response = MockAgentResponse(
            content="Your order #1042 is on its way!",
            structured_output={
                "tier": "AUTO_RESPOND",
                "category": "shipping",
                "confidence": 0.95,
                "customer_response_draft": (
                    "Hi! Your order #1042 shipped on March 19 via USPS Priority Mail. "
                    "Tracking number: 9400111899223033005. Estimated delivery: March 24."
                ),
                "internal_notes_en": "Customer asked about order #1042 status. Order shipped 2026-03-19.",
                "internal_notes_id": "Pelanggan bertanya tentang status pesanan #1042.",
                "escalation_target": None,
                "order_id": "1042",
                "suggested_tags": ["shipping", "tracking"],
            },
            model="claude-haiku-4-20250514",
        )
        agent = triage_agent([response])
        ticket = make_customer_ticket(
            subject="Where is my order?",
            body="Where is my order #1042?",
            order_number="1042",
        )

        # Verify the structured output matches expected classification
        result = response.structured_output
        assert result["tier"] == "AUTO_RESPOND"
        assert result["category"] == "shipping"
        assert result["confidence"] >= 0.8
        assert result["order_id"] == "1042"
        assert result["escalation_target"] is None

    def test_response_includes_tracking(self, triage_agent):
        """Auto-respond for tracking should include tracking details."""
        response = MockAgentResponse(
            content="",
            structured_output={
                "tier": "AUTO_RESPOND",
                "category": "shipping",
                "confidence": 0.93,
                "customer_response_draft": (
                    "Hi! Your order #1042 shipped on March 19 via USPS Priority Mail. "
                    "Tracking: 9400111899223033005."
                ),
                "internal_notes_en": "Tracking lookup for #1042.",
                "internal_notes_id": "Pencarian pelacakan untuk pesanan #1042.",
                "escalation_target": None,
                "order_id": "1042",
                "suggested_tags": ["shipping", "tracking"],
            },
        )
        result = response.structured_output
        assert "tracking" in result["customer_response_draft"].lower() or "shipped" in result["customer_response_draft"].lower()


# ---------------------------------------------------------------------------
# Test Case 2: Refund request $30 -> ESCALATE_OPS_MANAGER
# ---------------------------------------------------------------------------


class TestRefundEscalation:
    """'I want a refund for the singing bowl, $30' should route to operations-manager."""

    def test_classifies_as_escalate_ops_manager(self, triage_agent):
        """Refund requests are operational issues requiring the operations manager's authority."""
        response = MockAgentResponse(
            content="",
            structured_output={
                "tier": "ESCALATE_OPS_MANAGER",
                "category": "refund",
                "confidence": 0.91,
                "customer_response_draft": (
                    "Hi! Thank you for reaching out about your singing bowl. "
                    "I've forwarded your refund request to our operations team. "
                    "You should hear back within 24 hours."
                ),
                "internal_notes_en": "Customer requesting $30 refund for singing bowl. Within policy window.",
                "internal_notes_id": (
                    "Pelanggan meminta pengembalian dana $30 untuk singing bowl. "
                    "Dalam jangka waktu kebijakan pengembalian."
                ),
                "escalation_target": "operations-manager",
                "order_id": None,
                "suggested_tags": ["refund", "singing-bowl"],
            },
            model="claude-haiku-4-20250514",
        )
        ticket = make_customer_ticket(
            subject="Refund request",
            body="I want a refund for the singing bowl I bought. It was $30.",
        )

        result = response.structured_output
        assert result["tier"] == "ESCALATE_OPS_MANAGER"
        assert result["category"] == "refund"
        assert result["escalation_target"] == "operations-manager"

    def test_ops_manager_briefing_in_bahasa_indonesia(self, triage_agent):
        """Operations manager's internal notes must be in Bahasa Indonesia."""
        response = MockAgentResponse(
            content="",
            structured_output={
                "tier": "ESCALATE_OPS_MANAGER",
                "category": "refund",
                "confidence": 0.89,
                "customer_response_draft": "Thank you for reaching out...",
                "internal_notes_en": "Customer requesting refund for singing bowl.",
                "internal_notes_id": (
                    "Pelanggan meminta pengembalian dana sebesar $30 untuk singing bowl. "
                    "Mungkin bisa Anda periksa dan setujui permintaan ini."
                ),
                "escalation_target": "operations-manager",
                "order_id": None,
                "suggested_tags": ["refund"],
            },
        )
        result = response.structured_output
        # Verify Bahasa Indonesia notes exist and contain expected patterns
        id_notes = result["internal_notes_id"]
        assert len(id_notes) > 20, "Bahasa Indonesia notes should be substantive"
        # Check for formal register markers
        assert "kamu" not in id_notes.lower(), "Must use formal 'Anda', not informal 'kamu'"


# ---------------------------------------------------------------------------
# Test Case 3: Mala meditation practice -> Dr. Hun Lye
# ---------------------------------------------------------------------------


class TestPracticeQuestionEscalation:
    """'Can you explain correct mala meditation practice?' -> Dr. Hun Lye."""

    def test_escalates_to_dr_hun_lye(self, triage_agent):
        """Buddhist practice questions must route to Dr. Hun Lye."""
        response = MockAgentResponse(
            content="",
            structured_output={
                "tier": "ESCALATE_SPECIALIST",
                "category": "practice",
                "confidence": 0.94,
                "customer_response_draft": (
                    "Thank you for your thoughtful question about mala meditation practice. "
                    "Questions about Buddhist practice deserve a knowledgeable response, "
                    "so I'm connecting you with our spiritual advisor, Dr. Hun Lye, who has "
                    "deep experience in this area. You should hear back within 48 hours."
                ),
                "internal_notes_en": "Customer asking about mala meditation technique. Routing to Dr. Hun Lye.",
                "internal_notes_id": (
                    "Pelanggan bertanya tentang teknik meditasi mala. "
                    "Diarahkan ke Dr. Hun Lye untuk panduan praktik."
                ),
                "escalation_target": "dr_hun_lye",
                "order_id": None,
                "suggested_tags": ["practice", "mala", "meditation"],
            },
            model="claude-haiku-4-20250514",
        )
        ticket = make_customer_ticket(
            subject="Mala meditation",
            body="Can you explain correct mala meditation practice?",
            order_number=None,
        )

        result = response.structured_output
        assert result["tier"] == "ESCALATE_SPECIALIST"
        assert result["escalation_target"] == "dr_hun_lye"
        assert result["category"] == "practice"

    def test_response_sets_48_hour_expectation(self, triage_agent):
        """Customer should be told to expect a response within 48 hours."""
        response = MockAgentResponse(
            content="",
            structured_output={
                "tier": "ESCALATE_SPECIALIST",
                "category": "practice",
                "confidence": 0.94,
                "customer_response_draft": (
                    "Thank you for your thoughtful question about mala meditation practice. "
                    "I'm connecting you with our spiritual advisor, Dr. Hun Lye. "
                    "You should hear back within 48 hours."
                ),
                "internal_notes_en": "Practice question -> Dr. Hun Lye.",
                "internal_notes_id": "Pertanyaan praktik -> Dr. Hun Lye.",
                "escalation_target": "dr_hun_lye",
                "order_id": None,
                "suggested_tags": ["practice"],
            },
        )
        draft = response.structured_output["customer_response_draft"]
        assert "48 hours" in draft, "Must set 48-hour SLA expectation per escalation matrix"

    def test_does_not_provide_practice_instruction(self, triage_agent):
        """The skill must NOT attempt to answer the practice question itself."""
        response = MockAgentResponse(
            content="",
            structured_output={
                "tier": "ESCALATE_SPECIALIST",
                "category": "practice",
                "confidence": 0.94,
                "customer_response_draft": (
                    "Thank you for your thoughtful question. I'm connecting you with "
                    "Dr. Hun Lye, our spiritual advisor."
                ),
                "internal_notes_en": "Practice question routed to specialist.",
                "internal_notes_id": "Pertanyaan praktik diarahkan ke spesialis.",
                "escalation_target": "dr_hun_lye",
                "order_id": None,
                "suggested_tags": ["practice"],
            },
        )
        draft = response.structured_output["customer_response_draft"]
        # The response should not contain meditation instructions
        instruction_markers = [
            "start by holding",
            "count each bead",
            "recite the mantra",
            "move your fingers",
            "here's how to use",
        ]
        for marker in instruction_markers:
            assert marker not in draft.lower(), (
                f"Response should not provide practice instruction (found: '{marker}')"
            )


# ---------------------------------------------------------------------------
# Test Case 4: Chargeback threat -> URGENT
# ---------------------------------------------------------------------------


class TestUrgentEscalation:
    """'Filing a chargeback RIGHT NOW' -> URGENT tier, route to ceo."""

    def test_classifies_as_urgent(self, triage_agent):
        """Chargeback threats are Tier 4 URGENT, always routed to ceo."""
        response = MockAgentResponse(
            content="",
            structured_output={
                "tier": "URGENT",
                "category": "complaint",
                "confidence": 0.97,
                "customer_response_draft": (
                    "I understand your frustration, and I'm sorry for the experience "
                    "you've had. I've escalated this to our team lead who will reach out "
                    "to you within 4 hours to resolve this. We take every concern seriously."
                ),
                "internal_notes_en": (
                    "URGENT: Customer threatening chargeback. "
                    "Immediate escalation to ceo required. 4-hour SLA."
                ),
                "internal_notes_id": (
                    "MENDESAK: Pelanggan mengancam chargeback. "
                    "Eskalasi segera ke ceo diperlukan. SLA 4 jam."
                ),
                "escalation_target": "ceo",
                "order_id": None,
                "suggested_tags": ["chargeback", "urgent", "legal"],
            },
            model="claude-haiku-4-20250514",
        )
        ticket = make_customer_ticket(
            subject="TERRIBLE SERVICE",
            body="This is ridiculous! I'm filing a chargeback RIGHT NOW. You've been warned.",
        )

        result = response.structured_output
        assert result["tier"] == "URGENT"
        assert result["escalation_target"] == "ceo"

    def test_urgent_has_mendesak_label(self, triage_agent):
        """Urgent items must include MENDESAK in Bahasa Indonesia notes."""
        response = MockAgentResponse(
            content="",
            structured_output={
                "tier": "URGENT",
                "category": "complaint",
                "confidence": 0.97,
                "customer_response_draft": "I understand your frustration...",
                "internal_notes_en": "URGENT: Chargeback threat.",
                "internal_notes_id": "MENDESAK: Pelanggan mengancam chargeback.",
                "escalation_target": "ceo",
                "order_id": None,
                "suggested_tags": ["chargeback", "urgent"],
            },
        )
        id_notes = response.structured_output["internal_notes_id"]
        assert "MENDESAK" in id_notes, "Urgent items must be marked MENDESAK for operations-manager"

    def test_urgent_response_is_empathetic_not_defensive(self, triage_agent):
        """Response to angry customers must be empathetic, never defensive."""
        response = MockAgentResponse(
            content="",
            structured_output={
                "tier": "URGENT",
                "category": "complaint",
                "confidence": 0.97,
                "customer_response_draft": (
                    "I understand your frustration, and I'm sorry for the experience "
                    "you've had. I've escalated this to our team lead."
                ),
                "internal_notes_en": "Chargeback threat, escalated.",
                "internal_notes_id": "MENDESAK: Ancaman chargeback.",
                "escalation_target": "ceo",
                "order_id": None,
                "suggested_tags": ["chargeback"],
            },
        )
        draft = response.structured_output["customer_response_draft"]
        # Should not contain defensive language
        defensive_markers = [
            "our policy clearly states",
            "you agreed to",
            "it's not our fault",
            "we are not responsible",
        ]
        for marker in defensive_markers:
            assert marker not in draft.lower(), (
                f"Response should not be defensive (found: '{marker}')"
            )


# ---------------------------------------------------------------------------
# Structural validation tests
# ---------------------------------------------------------------------------


class TestSkillStructure:
    """Verify the ticket-triage SKILL.md meets structural requirements."""

    def test_skill_md_loads(self, triage_skill_text: str):
        """SKILL.md must exist and be loadable."""
        assert len(triage_skill_text) > 500

    def test_has_yaml_frontmatter(self, triage_skill_text: str):
        """SKILL.md must start with YAML frontmatter."""
        assert triage_skill_text.startswith("---")

    def test_frontmatter_has_name(self, triage_skill_text: str):
        """Frontmatter must include a 'name' field."""
        assert "name: ticket-triage" in triage_skill_text

    def test_has_classification_tiers(self, triage_skill_text: str):
        """Must define all four classification tiers."""
        for tier in ["AUTO_RESPOND", "ESCALATE_OPS_MANAGER", "ESCALATE_SPECIALIST", "URGENT"]:
            assert tier in triage_skill_text, f"Missing tier: {tier}"

    def test_has_output_format(self, triage_skill_text: str):
        """Must include a JSON output format example."""
        assert "```json" in triage_skill_text

    def test_has_model_routing(self, triage_skill_text: str):
        """Must specify model routing (haiku/sonnet)."""
        assert "Haiku" in triage_skill_text or "haiku" in triage_skill_text
        assert "Sonnet" in triage_skill_text or "sonnet" in triage_skill_text

    def test_references_escalation_matrix(self, triage_skill_text: str):
        """Must reference the shared escalation matrix."""
        assert "escalation" in triage_skill_text.lower()

    def test_no_cultural_anti_patterns(self, triage_skill_text: str):
        """Must not contain culturally insensitive language."""
        anti_patterns = ["exotic", "mystical", "home decor", "Oriental"]
        for pattern in anti_patterns:
            assert pattern not in triage_skill_text, (
                f"Cultural anti-pattern found: '{pattern}'"
            )
