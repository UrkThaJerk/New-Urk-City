import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from new_urk_city.system import (  # noqa: E402
    AgentSystem,
    AutomationPhase,
    Opportunity,
    RiskLevel,
    Source,
    SourceRegistry,
    UserRules,
    build_default_system,
)


class AgentSystemTests(unittest.TestCase):
    def test_untrusted_sources_are_suppressed(self) -> None:
        result = build_default_system().run()
        titles = {item.opportunity.title for item in result.recommendations}
        self.assertNotIn("Mystery yield aggregator", titles)
        self.assertTrue(any("blocked-scam: suppressed" in entry for entry in result.audit_log))

    def test_alerts_only_phase_never_prefills_actions(self) -> None:
        result = build_default_system().run()
        for item in result.approval_queue:
            self.assertEqual(item.required_steps, ("notify",))

    def test_excluded_or_ineligible_items_drop_out(self) -> None:
        registry = SourceRegistry(
            (
                Source("Trusted Bank", "bank", "US", 90, "web", "daily", True),
            )
        )
        system = AgentSystem(
            registry=registry,
            opportunities=(
                Opportunity(
                    id="too-long",
                    title="Long lockup CD",
                    source_name="Trusted Bank",
                    agent_role="yield",
                    category="yield",
                    summary="Should fail rules due to lockup length.",
                    capital_required_dollars=1000,
                    expected_return_percent=5.0,
                    estimated_gain_dollars=300,
                    effort_hours=1.0,
                    lockup_days=365,
                    risk_level=RiskLevel.LOW,
                    fees_dollars=0,
                    recurring=False,
                    deadline=None,
                    eligibility_regions=("US",),
                ),
            ),
            rules=UserRules(
                available_cash=5000,
                geography="US",
                risk_tolerance=RiskLevel.LOW,
                preferred_account_types=("cash",),
                excluded_institutions=(),
                skills=(),
                min_yield_percent=3.0,
                max_lockup_days=90,
            ),
            phase=AutomationPhase.PREFILLED_ACTIONS,
        )
        result = system.run()
        self.assertEqual(result.recommendations, ())

    def test_reports_include_expected_sections(self) -> None:
        result = build_default_system().run()
        self.assertIn("Daily summary", result.daily_summary)
        self.assertIn("Weekly report", result.weekly_report)
        self.assertIn("Action queue", result.action_queue)


if __name__ == "__main__":
    unittest.main()
