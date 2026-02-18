# Agent Architecture Documentation
## Technical Deep Dive: Lease Compliance Agent

---

## System Overview

```
┌────────────────────────────────────────────────────────────────┐
│                    LEASE COMPLIANCE AGENT                      │
│                         (ASC 842)                              │
└────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────▼────────┐  ┌──────▼─────────┐
            │   INPUT LAYER  │  │ CONFIG LAYER   │
            └───────┬────────┘  └──────┬─────────┘
                    │                   │
            ┌───────▼───────────────────▼──────┐
            │      AGENT CORE PIPELINE         │
            │  1. Classify                     │
            │  2. Test                         │
            │  3. Assess Risk                  │
            │  4. Decide                       │
            │  5. Log                          │
            └───────┬──────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
  ┌─────▼─────┐ ┌──▼───┐ ┌────▼─────┐
  │  OUTPUTS  │ │ LOGS │ │ METRICS  │
  └───────────┘ └──────┘ └──────────┘
```

---

## Component Architecture

### 1. Data Models Layer

```python
┌─────────────────────────────────────────────────────────┐
│                    DATA MODELS                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  LeaseContract                                          │
│  ├── Contract details (dates, payments, terms)         │
│  ├── Financial data (PV, FV, interest rate)            │
│  └── Methods: get_lease_term(), get_total_payments()   │
│                                                         │
│  AuditFinding                                           │
│  ├── Finding metadata (type, description)              │
│  ├── Risk assessment (level, severity)                 │
│  ├── Recommendations                                    │
│  └── Suggested adjustments (journal entries)           │
│                                                         │
│  AgentDecision                                          │
│  ├── Action (approve/escalate/correct)                 │
│  ├── Rationale (why this decision)                     │
│  ├── Confidence score (0.0 - 1.0)                      │
│  └── Associated findings                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2. Agent Core Pipeline

```
                    ┌──────────────────┐
                    │  Input: Lease    │
                    │   Contract       │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  STEP 1:         │
                    │  CLASSIFY        │
                    │  LEASE           │
                    │                  │
                    │  • Apply ASC     │
                    │    842 criteria  │
                    │  • Calculate PV  │
                    │  • Determine     │
                    │    type          │
                    │  • Assign        │
                    │    confidence    │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  STEP 2:         │
                    │  RUN             │
                    │  COMPLIANCE      │
                    │  TESTS           │
                    │                  │
                    │  • Materiality   │
                    │  • Data quality  │
                    │  • Recognition   │
                    │  • Disclosure    │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  STEP 3:         │
                    │  ASSESS          │
                    │  RISK            │
                    │                  │
                    │  • Aggregate     │
                    │    findings      │
                    │  • Calculate     │
                    │    severity      │
                    │  • Consider      │
                    │    materiality   │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  STEP 4:         │
                    │  MAKE            │
                    │  DECISION        │
                    │                  │
                    │  • Evaluate      │
                    │    confidence    │
                    │  • Check risk    │
                    │  • Apply logic   │
                    │  • Generate      │
                    │    rationale     │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  STEP 5:         │
                    │  LOG TO          │
                    │  AUDIT TRAIL     │
                    │                  │
                    │  • Timestamp     │
                    │  • Action taken  │
                    │  • Data used     │
                    │  • Version info  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Output:         │
                    │  AgentDecision   │
                    │  + Findings      │
                    └──────────────────┘
```

---

## Decision Logic Flow

```
                        ┌──────────────┐
                        │   Start:     │
                        │   Lease +    │
                        │   Findings   │
                        └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │ Critical     │
                   ┌────┤ Finding?     ├────┐
                   │    └──────────────┘    │
                 YES                        NO
                   │                         │
          ┌────────▼────────┐      ┌────────▼────────┐
          │  ESCALATE       │      │ Confidence      │
          │  (Safety        │      │ Score >= 95%?   │
          │   First!)       │      └────┬───────┬────┘
          └─────────────────┘         YES      NO
                   │                   │        │
                   │          ┌────────▼────┐  │
                   │          │ Risk Level  │  │
                   │          │ == LOW?     │  │
                   │          └────┬───┬────┘  │
                   │             YES  NO        │
                   │              │   │         │
                   │     ┌────────▼┐  │         │
                   │     │AUTO-    │  │         │
                   │     │APPROVE  │  │         │
                   │     └─────────┘  │         │
                   │                  │         │
                   │      ┌───────────▼─────────▼───────┐
                   │      │ Confidence Score < 75%?     │
                   │      └───────┬───────────┬─────────┘
                   │            YES           NO
                   │              │            │
                   │     ┌────────▼────┐ ┌────▼────────┐
                   │     │ ESCALATE    │ │ Risk HIGH & │
                   │     │ (Uncertain) │ │ Requires    │
                   │     └─────────────┘ │ Adjustment? │
                   │                     └────┬───┬────┘
                   │                        YES  NO
                   │                         │   │
                   │                ┌────────▼┐  │
                   │                │ESCALATE │  │
                   │                │(Material│  │
                   │                │Impact)  │  │
                   │                └─────────┘  │
                   │                             │
                   │                   ┌─────────▼────┐
                   │                   │ AUTO-APPROVE │
                   │                   │ (Moderate    │
                   │                   │  Confidence) │
                   │                   └──────────────┘
                   │                            │
                   └────────────────────────────┘
                                │
                        ┌───────▼────────┐
                        │  Return:       │
                        │  AgentDecision │
                        └────────────────┘
```

---

## Classification Algorithm

### ASC 842 Finance Lease Test

```
┌─────────────────────────────────────────────────────┐
│         ASC 842 FINANCE LEASE CRITERIA              │
│              (Any ONE = Finance)                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Test 1: Ownership Transfer                        │
│  ├── Does lease transfer ownership at end?         │
│  └── IF YES → Finance Lease (100% confidence)      │
│                                                     │
│  Test 2: Bargain Purchase Option                   │
│  ├── Does lease contain BPO?                       │
│  └── IF YES → Finance Lease (100% confidence)      │
│                                                     │
│  Test 3: Lease Term (Major Part)                   │
│  ├── Calculate: lease_term / economic_life         │
│  ├── IF >= 75% → Finance Lease                     │
│  └── Confidence: 90%                                │
│                                                     │
│  Test 4: Present Value (Substantially All)         │
│  ├── Calculate: PV(payments) / Fair_Value          │
│  ├── IF >= 90% → Finance Lease                     │
│  └── Confidence: 95%                                │
│                                                     │
│  Test 5: Specialized Asset                         │
│  ├── Does asset have alternative use to lessor?    │
│  └── IF NO → Finance Lease (85% confidence)        │
│                                                     │
│  Short-Term Exception:                             │
│  ├── IF lease_term <= 12 months                    │
│  └── → Short-Term Lease (exemption available)      │
│                                                     │
│  Default Classification:                           │
│  └── IF none of above → Operating Lease            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Present Value Calculation

```python
# PV of Lease Payments Formula

PV = Initial_Payment + (Monthly_Payment × PV_Factor)

where:
    PV_Factor = [1 - (1 + r)^(-n)] / r

    r = Monthly interest rate (annual_rate / 12)
    n = Number of payment periods (months)

Example:
    Monthly_Payment = $5,000
    Initial_Payment = $10,000
    Annual_Rate = 6% (0.06)
    Term = 36 months

    Monthly_Rate = 0.06 / 12 = 0.005
    PV_Factor = [1 - (1.005)^(-36)] / 0.005
              = [1 - 0.8356] / 0.005
              = 32.87

    PV = $10,000 + ($5,000 × 32.87)
       = $10,000 + $164,350
       = $174,350
```

---

## Risk Assessment Matrix

```
┌──────────────────────────────────────────────────────────┐
│              RISK LEVEL DETERMINATION                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  CRITICAL (🔴)                                           │
│  ├── Any finding with risk_level = CRITICAL             │
│  ├── Data integrity violations                          │
│  ├── Invalid calculations (negative terms, etc.)        │
│  └── Always escalates to human                          │
│                                                          │
│  HIGH (🟠)                                               │
│  ├── 2+ findings with risk_level = HIGH                 │
│  ├── OR 1 HIGH finding + material lease                 │
│  ├── OR Material lease with required adjustment         │
│  └── Typically escalates unless high confidence         │
│                                                          │
│  MEDIUM (🟡)                                             │
│  ├── 1 HIGH finding (not material)                      │
│  ├── OR multiple MEDIUM findings                        │
│  ├── OR any finding requiring adjustment                │
│  └── May auto-approve with high confidence              │
│                                                          │
│  LOW (🟢)                                                │
│  ├── No findings OR only LOW-level findings             │
│  ├── No material impact                                 │
│  ├── No adjustments required                            │
│  └── Auto-approve if confidence adequate                │
│                                                          │
└──────────────────────────────────────────────────────────┘

MATERIALITY THRESHOLD: $50,000 (configurable)
```

---

## Compliance Test Suite

```
┌──────────────────────────────────────────────────────────┐
│                  COMPLIANCE TESTS                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Test 1: Materiality Check                              │
│  ├── IF total_payments > threshold                      │
│  │   └── THEN verify completeness of data               │
│  └── Flags: Missing IBR, missing FV                     │
│      Risk: HIGH (material misstatement possible)        │
│                                                          │
│  Test 2: Classification Validation                      │
│  ├── IF Finance Lease                                   │
│  │   ├── Calculate ROU asset = PV(payments)            │
│  │   ├── Calculate Lease liability = PV(payments)      │
│  │   └── Generate suggested JE                          │
│  └── Risk: MEDIUM (requires verification)               │
│                                                          │
│  Test 3: Short-Term Election                            │
│  ├── IF term <= 12 months                               │
│  │   └── Flag: Exemption available                     │
│  └── Risk: LOW (policy election needed)                 │
│                                                          │
│  Test 4: Data Validation                                │
│  ├── Verify lease term > 0                              │
│  ├── Verify payments > 0                                │
│  ├── Verify dates are logical (end > start)            │
│  └── Risk: CRITICAL if validation fails                 │
│                                                          │
│  Test 5: Disclosure Requirements                        │
│  ├── IF material lease                                  │
│  │   └── Verify disclosure requirements met             │
│  └── Risk: MEDIUM (compliance requirement)              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Audit Trail Structure

```json
{
  "timestamp": "2024-01-15T14:32:10.123456",
  "action_type": "analysis_started",
  "details": {
    "lease_id": "LEASE-001",
    "input_data": {
      "description": "Office Space",
      "start_date": "2024-01-01",
      "end_date": "2026-12-31",
      "monthly_payment": 5000.0,
      "initial_payment": 10000.0,
      "interest_rate": 0.06,
      "asset_fair_value": 200000.0
    },
    "config_used": {
      "auto_approve_threshold": 0.95,
      "escalation_threshold": 0.75,
      "materiality_threshold": 50000
    }
  },
  "agent_version": "1.0.0",
  "user_id": "auditor-123",
  "session_id": "session-abc-xyz"
}
```

### Why This Matters

1. **Regulatory Compliance**: SOX, PCAOB standards require documentation
2. **Quality Review**: Partners can review AI decisions
3. **Debugging**: Trace why agent made specific decisions
4. **Learning**: Analyze patterns in escalations and errors
5. **Audit Defense**: Prove compliance if challenged

---

## Configuration System

```python
DEFAULT_CONFIG = {
    # Decision thresholds
    "auto_approve_threshold": 0.95,    # 95% confidence to auto-approve
    "escalation_threshold": 0.75,      # < 75% confidence escalates

    # Materiality
    "materiality_threshold": 50000,    # $50k threshold

    # Classification criteria
    "short_term_threshold_months": 12, # Short-term if <= 12 months
    "finance_lease_thresholds": {
        "ownership_transfer": True,    # Check ownership transfer
        "bargain_purchase": True,      # Check BPO
        "lease_term_percentage": 0.75, # 75% of economic life
        "present_value_percentage": 0.90 # 90% of fair value
    }
}
```

### Firm Customization Examples

**Conservative Firm** (more escalations):
```python
config = {
    "auto_approve_threshold": 0.98,    # Higher bar
    "escalation_threshold": 0.85,      # Escalate more often
    "materiality_threshold": 25000     # Lower materiality
}
```

**Aggressive Firm** (fewer escalations):
```python
config = {
    "auto_approve_threshold": 0.90,    # Lower bar
    "escalation_threshold": 0.70,      # Escalate less
    "materiality_threshold": 100000    # Higher materiality
}
```

---

## Performance Characteristics

### Time Complexity

- **Classification**: O(1) - Fixed number of tests
- **Compliance Tests**: O(n) where n = number of tests
- **Risk Assessment**: O(f) where f = number of findings
- **Decision Making**: O(1) - Rule-based logic
- **Overall**: O(n + f) ≈ O(1) for typical cases

### Space Complexity

- **Per Lease**: ~1-2 KB (in-memory representation)
- **Audit Trail**: ~0.5-1 KB per log entry
- **Report**: ~5-10 KB per lease analyzed
- **Overall**: O(l) where l = number of leases

### Throughput Estimates

**Single-threaded:**
- Classification: ~10,000 leases/second
- Full analysis: ~10-20 leases/second
- Report generation: ~1,000 reports/second

**Production (8 cores):**
- Full analysis: ~100-150 leases/second
- Throughput: ~360,000 leases/hour

**Bottlenecks:**
- Audit trail logging (I/O bound)
- Report generation (JSON serialization)
- Database writes (if implemented)

---

## Extension Points

### 1. Machine Learning Integration

```
┌─────────────────────────────────────────┐
│   PHASE 1: Rule-Based (Current)        │
│   • Deterministic logic                │
│   • High explainability                │
├─────────────────────────────────────────┤
│   PHASE 2: Hybrid (6 months)           │
│   • ML for confidence scoring          │
│   • Pattern recognition for anomalies  │
│   • Rules for final decisions          │
├─────────────────────────────────────────┤
│   PHASE 3: Agentic (12 months)         │
│   • Multi-step reasoning               │
│   • Tool use (APIs, calculations)      │
│   • Natural language interaction       │
│   • Still with human oversight         │
└─────────────────────────────────────────┘
```

### 2. Multi-Framework Support

```python
class FrameworkEngine:
    """Abstract base for accounting frameworks"""

    def classify(self, contract):
        """Framework-specific classification logic"""
        pass

    def test(self, contract):
        """Framework-specific compliance tests"""
        pass


class ASC842Engine(FrameworkEngine):
    """US GAAP lease accounting"""
    pass


class IFRS16Engine(FrameworkEngine):
    """International lease accounting"""
    pass


class SOC2Engine(FrameworkEngine):
    """Control testing framework"""
    pass
```

### 3. Document Intelligence

```
┌──────────────────────────────────────┐
│     DOCUMENT PROCESSING PIPELINE     │
├──────────────────────────────────────┤
│  1. Ingest PDF/Word lease contract  │
│  2. OCR text extraction              │
│  3. NLP to identify key terms        │
│  4. Extract structured data          │
│  5. Validate completeness            │
│  6. Feed to classification agent     │
└──────────────────────────────────────┘
```

### 4. Real-Time Monitoring

```
┌─────────────────────────────────────┐
│      EVENT-DRIVEN ARCHITECTURE      │
├─────────────────────────────────────┤
│  • Watch for new leases in ERP      │
│  • Trigger analysis automatically   │
│  • Alert on high-risk findings      │
│  • Dashboard with live metrics      │
│  • Slack/email notifications        │
└─────────────────────────────────────┘
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   CLIENT SYSTEMS                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐            │
│  │   ERP   │  │  Lease   │  │  Document  │            │
│  │ (SAP,   │  │  Mgmt    │  │  Storage   │            │
│  │NetSuite)│  │ Software │  │ (SharePt)  │            │
│  └────┬────┘  └─────┬────┘  └──────┬─────┘            │
│       │             │              │                   │
└───────┼─────────────┼──────────────┼───────────────────┘
        │             │              │
        │    ┌────────▼──────────────▼────┐
        │    │     API GATEWAY             │
        │    │   (Authentication,          │
        │    │    Rate Limiting,           │
        │    │    Load Balancing)          │
        │    └────────┬────────────────────┘
        │             │
┌───────▼─────────────▼──────────────────────────────────┐
│             LEASE COMPLIANCE AGENT                     │
│  ┌─────────────────────────────────────────────────┐  │
│  │  Agent Core Pipeline                            │  │
│  │  • Classify → Test → Assess → Decide → Log     │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │ Configuration│  │ Audit Trail  │  │   Cache    │  │
│  │   Storage    │  │   Database   │  │  (Redis)   │  │
│  └──────────────┘  └──────────────┘  └────────────┘  │
└────────────────────────┬───────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────┐
│                 OUTPUT SYSTEMS                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │
│  │ Fieldg.  │  │  Client  │  │   Notification   │    │
│  │ Platform │  │ Dashboard│  │   Service        │    │
│  │          │  │          │  │ (Email/Slack)    │    │
│  └──────────┘  └──────────┘  └──────────────────┘    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│              CLOUD DEPLOYMENT                   │
│               (AWS Example)                     │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │          CloudFront (CDN)                │  │
│  │       (Static assets, caching)           │  │
│  └────────────────┬─────────────────────────┘  │
│                   │                            │
│  ┌────────────────▼─────────────────────────┐  │
│  │     API Gateway + Lambda                 │  │
│  │    (Serverless agent execution)          │  │
│  │                                           │  │
│  │  ┌─────────────────────────────────────┐ │  │
│  │  │ Lambda Function: Agent Core         │ │  │
│  │  │ • Python 3.11                       │ │  │
│  │  │ • Memory: 512MB                     │ │  │
│  │  │ • Timeout: 30s                      │ │  │
│  │  │ • Concurrent executions: 1000       │ │  │
│  │  └─────────────────────────────────────┘ │  │
│  └────────────────┬─────────────────────────┘  │
│                   │                            │
│  ┌────────────────▼─────────────────────────┐  │
│  │        Data & Storage Layer              │  │
│  │                                           │  │
│  │  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │  RDS         │  │  S3              │  │  │
│  │  │  (PostgreSQL)│  │  (Audit trails,  │  │  │
│  │  │  - Config    │  │   Reports)       │  │  │
│  │  │  - Decisions │  │                  │  │  │
│  │  └──────────────┘  └──────────────────┘  │  │
│  │                                           │  │
│  │  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │ ElastiCache  │  │  SQS             │  │  │
│  │  │ (Redis)      │  │  (Job queue for  │  │  │
│  │  │ - PV calcs   │  │   batch process) │  │  │
│  │  └──────────────┘  └──────────────────┘  │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │     Monitoring & Observability           │  │
│  │  • CloudWatch (metrics, logs, alarms)    │  │
│  │  • X-Ray (distributed tracing)           │  │
│  │  • SNS (alerting)                        │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘

ESTIMATED COST (10,000 leases/month):
- Lambda: $20/month
- RDS: $50/month
- S3: $5/month
- ElastiCache: $30/month
Total: ~$100-150/month
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────┐
│              SECURITY LAYERS                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  LAYER 1: Network Security                     │
│  ├── VPC with private subnets                  │
│  ├── Security groups (least privilege)         │
│  └── WAF (web application firewall)            │
│                                                 │
│  LAYER 2: Authentication & Authorization       │
│  ├── OAuth 2.0 / SAML integration              │
│  ├── API key management                        │
│  ├── Role-based access control (RBAC)          │
│  └── Multi-factor authentication (MFA)         │
│                                                 │
│  LAYER 3: Data Protection                      │
│  ├── Encryption at rest (AES-256)              │
│  ├── Encryption in transit (TLS 1.3)           │
│  ├── Client data isolation (multi-tenant)      │
│  └── PII/PCI data handling                     │
│                                                 │
│  LAYER 4: Audit & Compliance                   │
│  ├── Complete audit trail (all actions logged) │
│  ├── Tamper-proof logging                      │
│  ├── Compliance certifications (SOC 2, GDPR)   │
│  └── Regular penetration testing               │
│                                                 │
│  LAYER 5: AI Governance                        │
│  ├── Model versioning and rollback             │
│  ├── Decision explainability                   │
│  ├── Bias monitoring and testing               │
│  └── Human review checkpoints                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Scalability Patterns

### Pattern 1: Vertical Scaling
```
┌────────────────────────────────┐
│   Single Instance Scaling      │
│                                │
│   Small:  512MB, 1 vCPU        │
│   → 100 leases/hour            │
│                                │
│   Medium: 2GB, 2 vCPU          │
│   → 500 leases/hour            │
│                                │
│   Large:  8GB, 4 vCPU          │
│   → 2,000 leases/hour          │
└────────────────────────────────┘
```

### Pattern 2: Horizontal Scaling
```
┌─────────────────────────────────┐
│    Load Balanced Cluster        │
│                                 │
│  ┌──────┐ ┌──────┐ ┌──────┐    │
│  │Agent │ │Agent │ │Agent │    │
│  │  1   │ │  2   │ │  3   │    │
│  └──────┘ └──────┘ └──────┘    │
│                                 │
│  3 instances × 500/hour         │
│  = 1,500 leases/hour            │
│                                 │
│  Auto-scaling: 1-100 instances  │
│  = Up to 50,000 leases/hour     │
└─────────────────────────────────┘
```

### Pattern 3: Batch Processing
```
┌─────────────────────────────────┐
│    Queue-Based Architecture     │
│                                 │
│  Leases → SQS Queue → Lambda    │
│             ↓                   │
│         Process in parallel     │
│         (1000 concurrent)       │
│             ↓                   │
│         Results → S3/DB         │
│                                 │
│  Throughput: ~100,000/hour      │
└─────────────────────────────────┘
```

---

## Continuous Learning Loop

```
┌────────────────────────────────────────────────────────┐
│            AGENT IMPROVEMENT CYCLE                     │
└────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  1. Agent Makes  │
    │     Decisions    │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │  2. Humans       │
    │     Review       │
    │     Escalations  │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │  3. Override +   │
    │     Feedback     │
    │     Logged       │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │  4. Analyze      │
    │     Patterns     │
    │     - Where did  │
    │       we under/  │
    │       over       │
    │       escalate?  │
    │     - What data  │
    │       improved   │
    │       decisions? │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │  5. Update       │
    │     Model/Rules  │
    │     - Adjust     │
    │       thresholds │
    │     - Add tests  │
    │     - Improve    │
    │       confidence │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │  6. A/B Test     │
    │     Changes      │
    │     - Shadow mode│
    │     - Compare    │
    │       metrics    │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │  7. Deploy       │
    │     Improvements │
    └────────┬─────────┘
             │
             └──────────► Back to step 1

KEY METRICS TO TRACK:
- Auto-approval rate (target: 70-80%)
- Override rate (when humans disagree)
- Precision (% escalations humans agree with)
- Recall (% issues agent catches)
- Time to resolution
- User satisfaction (NPS)
```

---

This architecture is production-ready, scalable, and designed for continuous improvement. It balances automation with human judgment while maintaining the auditability and transparency required in regulated industries.