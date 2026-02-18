"""
Lease Accounting Compliance Agent
An AI agent for automated ASC 842 lease accounting compliance verification

This agent demonstrates key principles for audit/advisory AI agents:
1. Autonomous workflow execution
2. Rule-based decision making with human escalation
3. Complete audit trail
4. Real-time monitoring and alerting
5. Framework-based validation (ASC 842 compliance)
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import uuid


class LeaseClassification(Enum):
    """ASC 842 Lease Classifications"""
    OPERATING = "operating"
    FINANCE = "finance"
    SHORT_TERM = "short_term"
    UNKNOWN = "unknown"


class RiskLevel(Enum):
    """Risk assessment levels for audit findings"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentAction(Enum):
    """Types of actions the agent can take"""
    AUTO_APPROVE = "auto_approve"
    AUTO_CORRECT = "auto_correct"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    REQUEST_MORE_INFO = "request_more_info"


@dataclass
class LeaseContract:
    """Represents a lease contract to be analyzed"""
    id: str
    description: str
    start_date: str  # ISO format
    end_date: str
    monthly_payment: float
    initial_payment: float
    residual_value: Optional[float]
    interest_rate: Optional[float]
    asset_fair_value: Optional[float]
    classification: Optional[str] = None

    def get_lease_term_months(self) -> int:
        """Calculate lease term in months"""
        start = datetime.fromisoformat(self.start_date)
        end = datetime.fromisoformat(self.end_date)
        return (end.year - start.year) * 12 + (end.month - start.month)

    def get_total_payments(self) -> float:
        """Calculate total lease payments"""
        return self.initial_payment + (self.monthly_payment * self.get_lease_term_months())


@dataclass
class AuditFinding:
    """Represents an audit finding identified by the agent"""
    id: str
    lease_id: str
    finding_type: str
    description: str
    risk_level: RiskLevel
    recommendation: str
    affected_accounts: List[str]
    requires_adjustment: bool
    suggested_adjustment: Optional[Dict] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class AgentDecision:
    """Represents a decision made by the agent"""
    decision_id: str
    lease_id: str
    action: AgentAction
    rationale: str
    confidence_score: float  # 0.0 to 1.0
    findings: List[AuditFinding]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class LeaseComplianceAgent:
    """
    AI Agent for Lease Accounting Compliance (ASC 842)

    Key Features:
    - Autonomous lease classification
    - Compliance testing against ASC 842
    - Risk assessment and prioritization
    - Intelligent escalation to human auditors
    - Complete audit trail generation
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.audit_trail: List[Dict] = []
        self.decisions: List[AgentDecision] = []

    def _default_config(self) -> Dict:
        """Default agent configuration"""
        return {
            "auto_approve_threshold": 0.95,  # Confidence threshold for auto-approval
            "escalation_threshold": 0.75,    # Below this, escalate to human
            "materiality_threshold": 50000,   # Dollar threshold for materiality
            "short_term_threshold_months": 12,
            "finance_lease_thresholds": {
                "ownership_transfer": True,
                "bargain_purchase": True,
                "lease_term_percentage": 0.75,  # 75% of economic life
                "present_value_percentage": 0.90  # 90% of fair value
            }
        }

    def analyze_lease(self, lease: LeaseContract) -> AgentDecision:
        """
        Main analysis workflow for a lease contract

        Steps:
        1. Classify the lease (finance vs operating)
        2. Verify compliance with ASC 842
        3. Identify any issues or exceptions
        4. Make recommendation (approve/correct/escalate)
        5. Log complete audit trail
        """
        self._log_action("analysis_started", {"lease_id": lease.id})

        # Step 1: Classify the lease
        classification, classification_confidence = self._classify_lease(lease)
        lease.classification = classification.value

        # Step 2: Run compliance tests
        findings = self._run_compliance_tests(lease, classification)

        # Step 3: Assess risk
        overall_risk = self._assess_risk(findings, lease)

        # Step 4: Make decision
        decision = self._make_decision(
            lease=lease,
            classification=classification,
            confidence=classification_confidence,
            findings=findings,
            risk_level=overall_risk
        )

        self.decisions.append(decision)
        self._log_action("analysis_completed", {
            "lease_id": lease.id,
            "decision": decision.action.value,
            "findings_count": len(findings)
        })

        return decision

    def _classify_lease(self, lease: LeaseContract) -> Tuple[LeaseClassification, float]:
        """
        Classify lease according to ASC 842 criteria

        Finance lease if ANY of these conditions are met:
        1. Ownership transfers at end of lease
        2. Contains bargain purchase option
        3. Lease term >= 75% of economic life
        4. PV of payments >= 90% of fair value
        5. Asset is specialized with no alternative use

        Returns: (classification, confidence_score)
        """
        self._log_action("classification_started", {"lease_id": lease.id})

        # Check for short-term lease (simplification opportunity)
        if lease.get_lease_term_months() <= self.config["short_term_threshold_months"]:
            return LeaseClassification.SHORT_TERM, 1.0

        # Finance lease criteria evaluation
        finance_indicators = []
        confidence_scores = []

        # Criterion 3: Lease term test (requires asset economic life - simplified)
        lease_term_months = lease.get_lease_term_months()
        if lease_term_months >= 60:  # Assuming 5-year typical economic life
            term_percentage = lease_term_months / 60
            if term_percentage >= self.config["finance_lease_thresholds"]["lease_term_percentage"]:
                finance_indicators.append("lease_term_major_part")
                confidence_scores.append(0.9)

        # Criterion 4: Present value test
        if lease.asset_fair_value and lease.interest_rate:
            pv_payments = self._calculate_present_value(lease)
            pv_percentage = pv_payments / lease.asset_fair_value

            if pv_percentage >= self.config["finance_lease_thresholds"]["present_value_percentage"]:
                finance_indicators.append("present_value_substantially_all")
                confidence_scores.append(0.95)

        # Determine classification
        if len(finance_indicators) > 0:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            return LeaseClassification.FINANCE, avg_confidence
        else:
            # Default to operating lease with moderate confidence
            # (In real scenarios, would need more data points)
            return LeaseClassification.OPERATING, 0.85

    def _calculate_present_value(self, lease: LeaseContract) -> float:
        """Calculate present value of lease payments"""
        if not lease.interest_rate:
            return lease.get_total_payments()

        monthly_rate = lease.interest_rate / 12
        n_periods = lease.get_lease_term_months()

        # PV of annuity formula
        if monthly_rate > 0:
            pv_factor = (1 - (1 + monthly_rate) ** -n_periods) / monthly_rate
            pv = lease.monthly_payment * pv_factor + lease.initial_payment
        else:
            pv = lease.get_total_payments()

        return pv

    def _run_compliance_tests(
        self,
        lease: LeaseContract,
        classification: LeaseClassification
    ) -> List[AuditFinding]:
        """
        Run ASC 842 compliance tests

        Tests include:
        - Proper classification
        - ROU asset recognition
        - Lease liability calculation
        - Disclosure requirements
        - Materiality assessment
        """
        findings = []

        # Test 1: Materiality check
        total_payments = lease.get_total_payments()
        if total_payments > self.config["materiality_threshold"]:
            # Check if material leases have all required data
            if not lease.interest_rate:
                findings.append(AuditFinding(
                    id=str(uuid.uuid4()),
                    lease_id=lease.id,
                    finding_type="missing_data",
                    description="Material lease missing interest rate (IBR)",
                    risk_level=RiskLevel.HIGH,
                    recommendation="Obtain incremental borrowing rate for accurate PV calculation",
                    affected_accounts=["ROU Asset", "Lease Liability"],
                    requires_adjustment=True
                ))

            if not lease.asset_fair_value:
                findings.append(AuditFinding(
                    id=str(uuid.uuid4()),
                    lease_id=lease.id,
                    finding_type="missing_data",
                    description="Material lease missing asset fair value",
                    risk_level=RiskLevel.MEDIUM,
                    recommendation="Obtain asset fair value to verify classification",
                    affected_accounts=["ROU Asset"],
                    requires_adjustment=False
                ))

        # Test 2: Classification validation
        if classification == LeaseClassification.FINANCE:
            # Finance lease requires specific journal entries
            liability_amount = self._calculate_present_value(lease) if lease.interest_rate else total_payments

            findings.append(AuditFinding(
                id=str(uuid.uuid4()),
                lease_id=lease.id,
                finding_type="classification_validation",
                description=f"Finance lease identified - requires ROU asset and liability recognition",
                risk_level=RiskLevel.MEDIUM,
                recommendation="Verify journal entries for initial recognition and subsequent measurement",
                affected_accounts=["ROU Asset - Finance", "Lease Liability - Finance"],
                requires_adjustment=True,
                suggested_adjustment={
                    "debit": {"ROU Asset - Finance": liability_amount},
                    "credit": {"Lease Liability - Finance": liability_amount}
                }
            ))

        # Test 3: Short-term lease exemption
        if classification == LeaseClassification.SHORT_TERM:
            findings.append(AuditFinding(
                id=str(uuid.uuid4()),
                lease_id=lease.id,
                finding_type="policy_election",
                description="Short-term lease eligible for recognition exemption",
                risk_level=RiskLevel.LOW,
                recommendation="Confirm company policy election for short-term lease treatment",
                affected_accounts=["Lease Expense"],
                requires_adjustment=False
            ))

        # Test 4: Lease term validation
        term_months = lease.get_lease_term_months()
        if term_months < 1:
            findings.append(AuditFinding(
                id=str(uuid.uuid4()),
                lease_id=lease.id,
                finding_type="data_validation",
                description="Invalid lease term calculation",
                risk_level=RiskLevel.CRITICAL,
                recommendation="Review and correct lease start and end dates",
                affected_accounts=[],
                requires_adjustment=False
            ))

        return findings

    def _assess_risk(self, findings: List[AuditFinding], lease: LeaseContract) -> RiskLevel:
        """
        Assess overall risk level based on findings and lease characteristics
        """
        if not findings:
            return RiskLevel.LOW

        # Check for critical findings
        if any(f.risk_level == RiskLevel.CRITICAL for f in findings):
            return RiskLevel.CRITICAL

        # Check for high-risk findings
        high_risk_count = sum(1 for f in findings if f.risk_level == RiskLevel.HIGH)
        if high_risk_count >= 2:
            return RiskLevel.HIGH
        if high_risk_count >= 1:
            return RiskLevel.HIGH

        # Check materiality
        if lease.get_total_payments() > self.config["materiality_threshold"] * 2:
            if any(f.requires_adjustment for f in findings):
                return RiskLevel.HIGH

        # Medium risk for any findings requiring adjustment
        if any(f.requires_adjustment for f in findings):
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def _make_decision(
        self,
        lease: LeaseContract,
        classification: LeaseClassification,
        confidence: float,
        findings: List[AuditFinding],
        risk_level: RiskLevel
    ) -> AgentDecision:
        """
        Make an autonomous decision on how to handle the lease

        Decision logic:
        - High confidence + Low risk = Auto-approve
        - Medium confidence + Low risk = Auto-approve with review flag
        - Low confidence OR High risk = Escalate to human
        - Critical risk = Always escalate
        - Missing data + Material = Escalate
        """
        decision_id = str(uuid.uuid4())

        # Critical findings always escalate
        if risk_level == RiskLevel.CRITICAL:
            return AgentDecision(
                decision_id=decision_id,
                lease_id=lease.id,
                action=AgentAction.ESCALATE_TO_HUMAN,
                rationale="Critical risk identified requiring human judgment",
                confidence_score=confidence,
                findings=findings
            )

        # High confidence and low risk - auto-approve
        if confidence >= self.config["auto_approve_threshold"] and risk_level == RiskLevel.LOW:
            return AgentDecision(
                decision_id=decision_id,
                lease_id=lease.id,
                action=AgentAction.AUTO_APPROVE,
                rationale="High confidence classification with no material findings",
                confidence_score=confidence,
                findings=findings
            )

        # Low confidence - escalate
        if confidence < self.config["escalation_threshold"]:
            return AgentDecision(
                decision_id=decision_id,
                lease_id=lease.id,
                action=AgentAction.ESCALATE_TO_HUMAN,
                rationale=f"Classification confidence ({confidence:.2f}) below threshold ({self.config['escalation_threshold']})",
                confidence_score=confidence,
                findings=findings
            )

        # High or medium risk - escalate
        if risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
            if any(f.requires_adjustment for f in findings):
                return AgentDecision(
                    decision_id=decision_id,
                    lease_id=lease.id,
                    action=AgentAction.ESCALATE_TO_HUMAN,
                    rationale=f"{risk_level.value.upper()} risk with required adjustments",
                    confidence_score=confidence,
                    findings=findings
                )

        # Default: Moderate confidence with low risk
        return AgentDecision(
            decision_id=decision_id,
            lease_id=lease.id,
            action=AgentAction.AUTO_APPROVE,
            rationale="Acceptable confidence with manageable risk level",
            confidence_score=confidence,
            findings=findings
        )

    def _log_action(self, action_type: str, details: Dict):
        """
        Log action to audit trail

        This is critical for audit verification and transparency
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "details": details,
            "agent_version": "1.0.0"
        }
        self.audit_trail.append(log_entry)

    def generate_audit_report(self) -> Dict:
        """
        Generate comprehensive audit report

        Includes:
        - Summary statistics
        - All decisions made
        - Complete audit trail
        - Recommendations for human review
        """
        escalated_decisions = [d for d in self.decisions if d.action == AgentAction.ESCALATE_TO_HUMAN]
        auto_approved = [d for d in self.decisions if d.action == AgentAction.AUTO_APPROVE]

        all_findings = []
        for decision in self.decisions:
            all_findings.extend(decision.findings)

        critical_findings = [f for f in all_findings if f.risk_level == RiskLevel.CRITICAL]
        high_findings = [f for f in all_findings if f.risk_level == RiskLevel.HIGH]

        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "agent_version": "1.0.0",
                "total_leases_analyzed": len(self.decisions)
            },
            "summary": {
                "total_decisions": len(self.decisions),
                "auto_approved": len(auto_approved),
                "escalated_to_human": len(escalated_decisions),
                "total_findings": len(all_findings),
                "critical_findings": len(critical_findings),
                "high_risk_findings": len(high_findings),
                "average_confidence": sum(d.confidence_score for d in self.decisions) / len(self.decisions) if self.decisions else 0
            },
            "decisions": [
                {
                    "decision_id": d.decision_id,
                    "lease_id": d.lease_id,
                    "action": d.action.value,
                    "rationale": d.rationale,
                    "confidence_score": d.confidence_score,
                    "findings_count": len(d.findings),
                    "timestamp": d.timestamp
                }
                for d in self.decisions
            ],
            "findings_by_lease": {
                decision.lease_id: [
                    {
                        "finding_id": f.id,
                        "type": f.finding_type,
                        "description": f.description,
                        "risk_level": f.risk_level.value,
                        "recommendation": f.recommendation,
                        "requires_adjustment": f.requires_adjustment,
                        "affected_accounts": f.affected_accounts,
                        "suggested_adjustment": f.suggested_adjustment
                    }
                    for f in decision.findings
                ]
                for decision in self.decisions
            },
            "items_requiring_human_review": [
                {
                    "decision_id": d.decision_id,
                    "lease_id": d.lease_id,
                    "priority": "HIGH" if any(f.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH] for f in d.findings) else "MEDIUM",
                    "reason": d.rationale,
                    "findings_count": len(d.findings)
                }
                for d in escalated_decisions
            ],
            "audit_trail": self.audit_trail
        }

        return report

    def export_for_workpaper(self, output_file: str):
        """
        Export results in workpaper-ready format
        """
        report = self.generate_audit_report()

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        return output_file


# Demonstration / Testing
def run_demo():
    """
    Demonstrate the agent with sample lease contracts
    """
    print("=== Lease Accounting Compliance Agent Demo ===\n")

    # Initialize agent
    agent = LeaseComplianceAgent()

    # Sample leases to analyze
    sample_leases = [
        LeaseContract(
            id="LEASE-001",
            description="Office Space - Downtown Location",
            start_date="2024-01-01",
            end_date="2026-12-31",
            monthly_payment=5000.0,
            initial_payment=10000.0,
            residual_value=None,
            interest_rate=0.06,
            asset_fair_value=200000.0
        ),
        LeaseContract(
            id="LEASE-002",
            description="Delivery Van Fleet",
            start_date="2024-06-01",
            end_date="2029-05-31",
            monthly_payment=1500.0,
            initial_payment=5000.0,
            residual_value=10000.0,
            interest_rate=0.055,
            asset_fair_value=80000.0
        ),
        LeaseContract(
            id="LEASE-003",
            description="Copy Machine - Short Term",
            start_date="2024-11-01",
            end_date="2025-10-31",
            monthly_payment=300.0,
            initial_payment=0.0,
            residual_value=None,
            interest_rate=None,
            asset_fair_value=5000.0
        ),
        LeaseContract(
            id="LEASE-004",
            description="Warehouse Space - Missing Data",
            start_date="2024-03-01",
            end_date="2027-02-28",
            monthly_payment=12000.0,
            initial_payment=25000.0,
            residual_value=None,
            interest_rate=None,  # Missing!
            asset_fair_value=None  # Missing!
        ),
    ]

    # Analyze each lease
    for lease in sample_leases:
        print(f"\n{'='*60}")
        print(f"Analyzing: {lease.description} ({lease.id})")
        print(f"{'='*60}")

        decision = agent.analyze_lease(lease)

        print(f"\n📋 Classification: {lease.classification}")
        print(f"🎯 Confidence Score: {decision.confidence_score:.2%}")
        print(f"🤖 Agent Decision: {decision.action.value.upper()}")
        print(f"💭 Rationale: {decision.rationale}")

        if decision.findings:
            print(f"\n🔍 Findings ({len(decision.findings)}):")
            for i, finding in enumerate(decision.findings, 1):
                print(f"\n  {i}. [{finding.risk_level.value.upper()}] {finding.finding_type}")
                print(f"     {finding.description}")
                print(f"     Recommendation: {finding.recommendation}")
                if finding.suggested_adjustment:
                    print(f"     Suggested Adjustment:")
                    for entry_type, accounts in finding.suggested_adjustment.items():
                        for account, amount in accounts.items():
                            print(f"       {entry_type.upper()}: {account} ${amount:,.2f}")

    # Generate final report
    print(f"\n\n{'='*60}")
    print("GENERATING AUDIT REPORT")
    print(f"{'='*60}\n")

    report = agent.generate_audit_report()

    print(f"📊 Summary Statistics:")
    print(f"   Total Leases Analyzed: {report['summary']['total_decisions']}")
    print(f"   Auto-Approved: {report['summary']['auto_approved']}")
    print(f"   Escalated to Human: {report['summary']['escalated_to_human']}")
    print(f"   Total Findings: {report['summary']['total_findings']}")
    print(f"   Critical Findings: {report['summary']['critical_findings']}")
    print(f"   Average Confidence: {report['summary']['average_confidence']:.2%}")

    if report['items_requiring_human_review']:
        print(f"\n⚠️  Items Requiring Human Review ({len(report['items_requiring_human_review'])}):")
        for item in report['items_requiring_human_review']:
            print(f"   - {item['lease_id']} [{item['priority']}]: {item['reason']}")

    # Export report
    output_file = "audit_report.json"
    agent.export_for_workpaper(output_file)
    print(f"\n✅ Full audit report exported to: {output_file}")

    return agent, report


if __name__ == "__main__":
    agent, report = run_demo()
