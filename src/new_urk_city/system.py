from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Iterable


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class AutomationPhase(str, Enum):
    ALERTS_ONLY = "phase_1"
    PREFILLED_ACTIONS = "phase_2"
    LIMITED_APPROVALS = "phase_3"


@dataclass(frozen=True)
class Source:
    name: str
    category: str
    region: str
    reputation: int
    access_method: str
    update_frequency: str
    trusted: bool
    requires_cross_verification: bool = False


@dataclass(frozen=True)
class Opportunity:
    id: str
    title: str
    source_name: str
    agent_role: str
    category: str
    summary: str
    capital_required_dollars: float
    expected_return_percent: float
    estimated_gain_dollars: float
    effort_hours: float
    lockup_days: int
    risk_level: RiskLevel
    fees_dollars: float
    recurring: bool
    deadline: datetime | None
    eligibility_regions: tuple[str, ...]
    required_skills: tuple[str, ...] = ()
    preferred_account_types: tuple[str, ...] = ()
    confidence: float = 1.0
    evidence_count: int = 1
    documentation_required: bool = False
    terms_last_checked: datetime = field(default_factory=lambda: datetime.now(UTC))
    allowed_actions: tuple[str, ...] = ("notify", "compare", "schedule", "prefill")


@dataclass(frozen=True)
class UserRules:
    available_cash: float
    geography: str
    risk_tolerance: RiskLevel
    preferred_account_types: tuple[str, ...]
    excluded_institutions: tuple[str, ...]
    skills: tuple[str, ...]
    min_yield_percent: float
    max_lockup_days: int


@dataclass(frozen=True)
class VerificationResult:
    approved: bool
    suppressed: bool
    requires_human_review: bool
    confidence_penalty: float
    flags: tuple[str, ...]


@dataclass(frozen=True)
class Recommendation:
    opportunity: Opportunity
    score: float
    reasons: tuple[str, ...]
    required_steps: tuple[str, ...]
    verification: VerificationResult


@dataclass(frozen=True)
class WorkflowResult:
    recommendations: tuple[Recommendation, ...]
    approval_queue: tuple[Recommendation, ...]
    audit_log: tuple[str, ...]
    daily_summary: str
    weekly_report: str
    action_queue: str


class SourceRegistry:
    def __init__(self, sources: Iterable[Source]) -> None:
        self._sources = {source.name: source for source in sources}

    def get(self, name: str) -> Source:
        return self._sources[name]

    def all(self) -> tuple[Source, ...]:
        return tuple(self._sources.values())


class OpportunityScorer:
    def score(
        self,
        opportunity: Opportunity,
        source: Source,
        rules: UserRules,
        verification: VerificationResult,
    ) -> float:
        score = opportunity.expected_return_percent * 12
        score += min(opportunity.estimated_gain_dollars / 10, 20)
        score -= opportunity.effort_hours * 3
        score -= opportunity.lockup_days / 30
        score -= opportunity.fees_dollars
        score -= {RiskLevel.LOW: 0, RiskLevel.MODERATE: 8, RiskLevel.HIGH: 25}[opportunity.risk_level]
        score += 6 if opportunity.recurring else 0
        score += source.reputation / 10
        score -= verification.confidence_penalty * 20

        if opportunity.capital_required_dollars > rules.available_cash:
            score -= 100
        if rules.geography not in opportunity.eligibility_regions and "global" not in opportunity.eligibility_regions:
            score -= 100
        if opportunity.lockup_days > rules.max_lockup_days:
            score -= 100
        if source.name in rules.excluded_institutions:
            score -= 100
        if opportunity.preferred_account_types and not set(opportunity.preferred_account_types).intersection(
            rules.preferred_account_types
        ):
            score -= 20
        if opportunity.expected_return_percent < rules.min_yield_percent and opportunity.category == "yield":
            score -= 25
        if opportunity.required_skills and not set(opportunity.required_skills).intersection(rules.skills):
            score -= 25
        if rules.risk_tolerance == RiskLevel.LOW and opportunity.risk_level != RiskLevel.LOW:
            score -= 25
        return round(score, 2)


class OpportunityVerifier:
    def verify(self, opportunity: Opportunity, source: Source) -> VerificationResult:
        flags: list[str] = []
        penalty = max(0.0, 1.0 - opportunity.confidence)
        requires_review = True
        suppressed = False

        if not source.trusted or source.reputation < 60:
            flags.append("source is not on the allowlist or has low reputation")
            suppressed = True
        if source.requires_cross_verification and opportunity.evidence_count < 2:
            flags.append("cross-verification is incomplete")
            penalty += 0.35
        if opportunity.fees_dollars > 25:
            flags.append("fees are high enough to require closer review")
            penalty += 0.15
        if opportunity.documentation_required:
            flags.append("identity or documentation may be required")
        if opportunity.terms_last_checked < datetime.now(UTC) - timedelta(days=7):
            flags.append("terms are stale and must be re-checked")
            penalty += 0.2
        if penalty >= 0.75:
            flags.append("confidence is too low for recommendation")
            suppressed = True

        approved = not suppressed
        return VerificationResult(
            approved=approved,
            suppressed=suppressed,
            requires_human_review=requires_review,
            confidence_penalty=round(min(penalty, 1.0), 2),
            flags=tuple(flags),
        )


class OpportunityAgent:
    role = "opportunity"
    categories = {"grants", "scholarships", "bug_bounties", "research", "marketplaces"}

    def discover(self, opportunities: Iterable[Opportunity]) -> tuple[Opportunity, ...]:
        return tuple(item for item in opportunities if item.agent_role == self.role)


class YieldAgent:
    role = "yield"
    categories = {"yield", "bank_bonus"}

    def discover(self, opportunities: Iterable[Opportunity]) -> tuple[Opportunity, ...]:
        return tuple(item for item in opportunities if item.agent_role == self.role)


class SavingsAgent:
    role = "savings"
    categories = {"cashback", "rebates", "settlements", "refunds"}

    def discover(self, opportunities: Iterable[Opportunity]) -> tuple[Opportunity, ...]:
        return tuple(item for item in opportunities if item.agent_role == self.role)


class AgentSystem:
    def __init__(
        self,
        registry: SourceRegistry,
        opportunities: Iterable[Opportunity],
        rules: UserRules,
        phase: AutomationPhase = AutomationPhase.ALERTS_ONLY,
    ) -> None:
        self.registry = registry
        self.opportunities = tuple(opportunities)
        self.rules = rules
        self.phase = phase
        self.agents = (YieldAgent(), SavingsAgent(), OpportunityAgent())
        self.verifier = OpportunityVerifier()
        self.scorer = OpportunityScorer()

    def run(self) -> WorkflowResult:
        discovered = self._deduplicate(
            opportunity
            for agent in self.agents
            for opportunity in agent.discover(self.opportunities)
        )
        recommendations: list[Recommendation] = []
        audit_log: list[str] = []

        for opportunity in discovered:
            source = self.registry.get(opportunity.source_name)
            verification = self.verifier.verify(opportunity, source)
            audit_log.append(self._build_audit_entry(opportunity, source, verification))
            if verification.suppressed:
                continue
            score = self.scorer.score(opportunity, source, self.rules, verification)
            if score < 0:
                continue
            recommendations.append(
                Recommendation(
                    opportunity=opportunity,
                    score=score,
                    reasons=self._build_reasons(opportunity, source, verification),
                    required_steps=self._allowed_steps(opportunity),
                    verification=verification,
                )
            )

        recommendations.sort(key=lambda item: item.score, reverse=True)
        recommendations, over_allocated_entries = self._apply_cash_limits(recommendations)
        audit_log.extend(over_allocated_entries)
        approval_queue = tuple(item for item in recommendations if item.verification.requires_human_review)
        return WorkflowResult(
            recommendations=tuple(recommendations),
            approval_queue=approval_queue,
            audit_log=tuple(audit_log),
            daily_summary=self._build_daily_summary(recommendations),
            weekly_report=self._build_weekly_report(recommendations),
            action_queue=self._build_action_queue(approval_queue),
        )

    def _deduplicate(self, opportunities: Iterable[Opportunity]) -> tuple[Opportunity, ...]:
        seen: set[tuple[str, str]] = set()
        unique: list[Opportunity] = []
        for opportunity in opportunities:
            key = (opportunity.title.casefold(), opportunity.source_name.casefold())
            if key in seen:
                continue
            seen.add(key)
            unique.append(opportunity)
        return tuple(unique)

    def _allowed_steps(self, opportunity: Opportunity) -> tuple[str, ...]:
        allowed_by_phase = {
            AutomationPhase.ALERTS_ONLY: {"notify"},
            AutomationPhase.PREFILLED_ACTIONS: {"notify", "compare", "schedule", "prefill"},
            AutomationPhase.LIMITED_APPROVALS: {"notify", "compare", "schedule", "prefill"},
        }[self.phase]
        return tuple(step for step in opportunity.allowed_actions if step in allowed_by_phase)

    def _apply_cash_limits(self, recommendations: list[Recommendation]) -> tuple[list[Recommendation], list[str]]:
        remaining_cash = self.rules.available_cash
        accepted: list[Recommendation] = []
        audit_entries: list[str] = []
        for item in recommendations:
            capital_required = item.opportunity.capital_required_dollars
            if capital_required and capital_required > remaining_cash:
                audit_entries.append(
                    f"{item.opportunity.id}: suppressed for over-allocation; "
                    f"required=${capital_required:.0f} remaining=${remaining_cash:.0f}"
                )
                continue
            accepted.append(item)
            remaining_cash -= capital_required
        return accepted, audit_entries

    def _build_reasons(
        self,
        opportunity: Opportunity,
        source: Source,
        verification: VerificationResult,
    ) -> tuple[str, ...]:
        reasons = [
            f"trusted source: {source.name}",
            f"estimated gain: ${opportunity.estimated_gain_dollars:.0f}",
            f"expected return: {opportunity.expected_return_percent:.2f}%",
        ]
        if opportunity.recurring:
            reasons.append("recurring opportunity")
        reasons.extend(verification.flags)
        return tuple(reasons)

    def _build_audit_entry(
        self,
        opportunity: Opportunity,
        source: Source,
        verification: VerificationResult,
    ) -> str:
        status = "suppressed" if verification.suppressed else "queued for review"
        flags = ", ".join(verification.flags) if verification.flags else "no flags"
        return f"{opportunity.id}: {status} via {source.name}; {flags}"

    def _build_daily_summary(self, recommendations: list[Recommendation]) -> str:
        lines = ["Daily summary"]
        for item in recommendations[:5]:
            lines.append(
                f"- {item.opportunity.title} [{item.opportunity.agent_role}] "
                f"score={item.score} gain=${item.opportunity.estimated_gain_dollars:.0f}"
            )
        if len(lines) == 1:
            lines.append("- No eligible opportunities today")
        return "\n".join(lines)

    def _build_weekly_report(self, recommendations: list[Recommendation]) -> str:
        now = datetime.now(UTC)
        new_items = sum(1 for item in recommendations if item.opportunity.terms_last_checked >= now - timedelta(days=7))
        expiring = [
            item.opportunity.title
            for item in recommendations
            if item.opportunity.deadline and item.opportunity.deadline <= now + timedelta(days=7)
        ]
        lines = [
            "Weekly report",
            f"- New or refreshed opportunities: {new_items}",
            f"- Expiring soon: {len(expiring)}",
        ]
        lines.extend(f"  - {title}" for title in expiring[:5])
        return "\n".join(lines)

    def _build_action_queue(self, approval_queue: tuple[Recommendation, ...]) -> str:
        lines = ["Action queue"]
        for item in approval_queue[:5]:
            deadline = item.opportunity.deadline.date().isoformat() if item.opportunity.deadline else "none"
            lines.append(
                f"- {item.opportunity.title}: steps={','.join(item.required_steps) or 'notify'} "
                f"gain=${item.opportunity.estimated_gain_dollars:.0f} deadline={deadline} "
                f"risk={item.opportunity.risk_level.value}"
            )
        if len(lines) == 1:
            lines.append("- No actions pending")
        return "\n".join(lines)


def build_default_system() -> AgentSystem:
    now = datetime.now(UTC)
    sources = (
        Source("TreasuryDirect", "government", "US", 95, "api", "daily", True, True),
        Source("Vanguard", "brokerage", "US", 92, "web", "daily", True, True),
        Source("Ally Bank", "bank", "US", 90, "web", "daily", True),
        Source("Rakuten", "cashback", "US", 85, "api", "hourly", True),
        Source("ClassAction.org", "settlements", "US", 78, "web", "daily", True),
        Source("HackerOne", "bug_bounties", "global", 88, "api", "daily", True),
        Source("User Interviews", "research", "US", 82, "api", "daily", True),
        Source("Unverified Promo Hub", "unknown", "global", 20, "scrape", "hourly", False),
    )
    opportunities = (
        Opportunity(
            id="yield-tbill",
            title="13-week Treasury bill ladder",
            source_name="TreasuryDirect",
            agent_role="yield",
            category="yield",
            summary="Track short-duration Treasury bill yields for idle cash.",
            capital_required_dollars=5_000,
            expected_return_percent=5.1,
            estimated_gain_dollars=255,
            effort_hours=1.0,
            lockup_days=91,
            risk_level=RiskLevel.LOW,
            fees_dollars=0,
            recurring=True,
            deadline=now + timedelta(days=4),
            eligibility_regions=("US",),
            preferred_account_types=("taxable", "retirement"),
            confidence=0.96,
            evidence_count=2,
        ),
        Opportunity(
            id="yield-bank-bonus",
            title="High-yield savings account with new-customer bonus",
            source_name="Ally Bank",
            agent_role="yield",
            category="bank_bonus",
            summary="Compare promo APY and signup bonus against user cash needs.",
            capital_required_dollars=2_500,
            expected_return_percent=4.25,
            estimated_gain_dollars=320,
            effort_hours=1.5,
            lockup_days=60,
            risk_level=RiskLevel.LOW,
            fees_dollars=0,
            recurring=False,
            deadline=now + timedelta(days=10),
            eligibility_regions=("US",),
            preferred_account_types=("cash",),
            confidence=0.93,
            evidence_count=1,
            documentation_required=True,
        ),
        Opportunity(
            id="savings-cashback",
            title="Category cashback stacking",
            source_name="Rakuten",
            agent_role="savings",
            category="cashback",
            summary="Highlight high-confidence cashback matches for planned spending.",
            capital_required_dollars=0,
            expected_return_percent=8.0,
            estimated_gain_dollars=60,
            effort_hours=0.5,
            lockup_days=0,
            risk_level=RiskLevel.LOW,
            fees_dollars=0,
            recurring=True,
            deadline=None,
            eligibility_regions=("US",),
            confidence=0.9,
            evidence_count=1,
        ),
        Opportunity(
            id="savings-settlement",
            title="Open consumer settlement claim",
            source_name="ClassAction.org",
            agent_role="savings",
            category="settlements",
            summary="Prepare a claim checklist when a user appears eligible.",
            capital_required_dollars=0,
            expected_return_percent=0.0,
            estimated_gain_dollars=45,
            effort_hours=0.4,
            lockup_days=0,
            risk_level=RiskLevel.LOW,
            fees_dollars=0,
            recurring=False,
            deadline=now + timedelta(days=6),
            eligibility_regions=("US",),
            confidence=0.87,
            evidence_count=1,
            documentation_required=True,
        ),
        Opportunity(
            id="opportunity-bug-bounty",
            title="Matching bug bounty program alert",
            source_name="HackerOne",
            agent_role="opportunity",
            category="bug_bounties",
            summary="Surface programs aligned with the user's web security skills.",
            capital_required_dollars=0,
            expected_return_percent=0.0,
            estimated_gain_dollars=500,
            effort_hours=4.0,
            lockup_days=0,
            risk_level=RiskLevel.MODERATE,
            fees_dollars=0,
            recurring=False,
            deadline=None,
            eligibility_regions=("global",),
            required_skills=("security", "web"),
            confidence=0.88,
            evidence_count=1,
        ),
        Opportunity(
            id="opportunity-research",
            title="Remote paid research study",
            source_name="User Interviews",
            agent_role="opportunity",
            category="research",
            summary="Queue interviews aligned with the user's background and schedule.",
            capital_required_dollars=0,
            expected_return_percent=0.0,
            estimated_gain_dollars=125,
            effort_hours=1.0,
            lockup_days=0,
            risk_level=RiskLevel.LOW,
            fees_dollars=0,
            recurring=False,
            deadline=now + timedelta(days=3),
            eligibility_regions=("US",),
            confidence=0.84,
            evidence_count=1,
        ),
        Opportunity(
            id="blocked-scam",
            title="Mystery yield aggregator",
            source_name="Unverified Promo Hub",
            agent_role="yield",
            category="yield",
            summary="Intentionally suppressed example of an untrusted source.",
            capital_required_dollars=4_000,
            expected_return_percent=12.0,
            estimated_gain_dollars=700,
            effort_hours=0.2,
            lockup_days=30,
            risk_level=RiskLevel.HIGH,
            fees_dollars=49,
            recurring=True,
            deadline=now + timedelta(days=1),
            eligibility_regions=("global",),
            confidence=0.3,
            evidence_count=0,
        ),
    )
    rules = UserRules(
        available_cash=10_000,
        geography="US",
        risk_tolerance=RiskLevel.LOW,
        preferred_account_types=("cash", "taxable"),
        excluded_institutions=("Unverified Promo Hub",),
        skills=("security", "web"),
        min_yield_percent=3.5,
        max_lockup_days=120,
    )
    return AgentSystem(SourceRegistry(sources), opportunities, rules)
