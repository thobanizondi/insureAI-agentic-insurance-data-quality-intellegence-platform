
from src.database.duckdb_connection import get_duckdb_connection


def detect_claim_risk(claim_id: int):
    """
    Deterministic insurance claim risk screening.

    Fraud-risk indicators and data-quality indicators are
    reported separately.

    This function is read-only and does not make automated
    fraud, approval or rejection decisions.
    """

    if not isinstance(claim_id, int) or isinstance(claim_id, bool) or claim_id <= 0:
        raise ValueError("Claim ID must be a positive integer.")

    conn = get_duckdb_connection()

    try:
        cursor = conn.cursor()

        # 1. Retrieve claim, customer and linked policy details
        cursor.execute(
            """
            SELECT
                cl.Claim_Id,
                cl.Customer_Id,
                cl.Policy_Id,
                cl.Claim_Date,
                cl.Claim_Amount,
                cl.Claim_Type,
                cl.Claim_Status,
                cl.Fraud_Flag,
                cl.Processing_Days,
                p.Policy_Type,
                p.Coverage_Amount,
                c.Customer_Name
            FROM raw_Claims cl
            LEFT JOIN raw_Policies p
                ON cl.Policy_Id = p.Policy_Id
            LEFT JOIN raw_Customers c
                ON cl.Customer_Id = c.Customer_Id
            WHERE cl.Claim_Id = ?
            """,
            (claim_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return {
                "claim_id": claim_id,
                "status": "NOT_FOUND",
                "message": "Claim does not exist."
            }

        (
            claim_id,
            customer_id,
            policy_id,
            claim_date,
            claim_amount,
            claim_type,
            claim_status,
            fraud_flag,
            processing_days,
            policy_type,
            coverage_amount,
            customer_name
        ) = row

        # Separate indicator collections
        fraud_risk_indicators = []
        data_quality_indicators = []

        # Keep a combined collection for compatibility
        # with the existing test script.
        indicators = []

        # 2. Existing source-system fraud flag
        if str(fraud_flag).strip().lower() == "yes":
            indicator = {
                "rule": "EXISTING_FRAUD_FLAG",
                "category": "FRAUD_RISK",
                "severity": "HIGH",
                "result": "TRIGGERED",
                "evidence": (
                    "The source claim record already has "
                    "Fraud_Flag = Yes."
                ),
                "interpretation": (
                    "Existing source-system flag. "
                    "Not independently verified."
                )
            }

            fraud_risk_indicators.append(indicator)
            indicators.append(indicator)

        # 3. Frequent customer claims within 30 days
        customer_claim_count = None

        if customer_id is not None and claim_date is not None:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM raw_Claims
                WHERE Customer_Id = ?
                  AND Claim_Date BETWEEN
                      (CAST(? AS DATE) - INTERVAL 30 DAY)
                      AND ?
                """,
                (customer_id, claim_date, claim_date)
            )

            customer_claim_count = cursor.fetchone()[0]

            if customer_claim_count >= 3:
                indicator = {
                    "rule": "FREQUENT_CUSTOMER_CLAIMS",
                    "category": "FRAUD_RISK",
                    "severity": "HIGH",
                    "result": "TRIGGERED",
                    "evidence": (
                        f"Customer {customer_id} has "
                        f"{customer_claim_count} claims within "
                        "30 days of this claim."
                    ),
                    "interpretation": (
                        "Frequent claims require investigation. "
                        "This pattern alone does not establish fraud."
                    )
                }

                fraud_risk_indicators.append(indicator)
                indicators.append(indicator)

        # 4. Frequent claims against the same policy
        policy_claim_count = None

        if policy_id is not None and claim_date is not None:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM raw_Claims
                WHERE Policy_Id = ?
                  AND Claim_Date BETWEEN
                      (CAST(? AS DATE) - INTERVAL 30 DAY)
                      AND ?
                """,
                (policy_id, claim_date, claim_date)
            )

            policy_claim_count = cursor.fetchone()[0]

            if policy_claim_count >= 3:
                indicator = {
                    "rule": "FREQUENT_POLICY_CLAIMS",
                    "category": "FRAUD_RISK",
                    "severity": "HIGH",
                    "result": "TRIGGERED",
                    "evidence": (
                        f"Policy {policy_id} has "
                        f"{policy_claim_count} claims within "
                        "30 days of this claim."
                    ),
                    "interpretation": (
                        "Repeated policy claims require investigation. "
                        "This pattern alone does not establish fraud."
                    )
                }

                fraud_risk_indicators.append(indicator)
                indicators.append(indicator)

        # 5. Portfolio 95th percentile claim amount
        cursor.execute(
            """
            SELECT DISTINCT
                quantile_cont(Claim_Amount, 0.95) AS P95_Claim_Amount
            FROM raw_Claims
            WHERE Claim_Amount IS NOT NULL
            """
        )

        percentile_row = cursor.fetchone()
        p95_amount = percentile_row[0] if percentile_row else None

        if (
            claim_amount is not None
            and p95_amount is not None
            and claim_amount >= p95_amount
        ):
            indicator = {
                "rule": "UNUSUALLY_HIGH_CLAIM_AMOUNT",
                "category": "FRAUD_RISK",
                "severity": "MEDIUM",
                "result": "TRIGGERED",
                "evidence": (
                    f"Claim amount {claim_amount} is at or above "
                    f"the portfolio 95th percentile of {p95_amount}."
                ),
                "interpretation": (
                    "High claim value requires supporting evidence. "
                    "A high amount alone does not establish fraud."
                )
            }

            fraud_risk_indicators.append(indicator)
            indicators.append(indicator)

        # 6. Claim amount compared with recorded policy coverage
        if (
            claim_amount is not None
            and coverage_amount is not None
            and claim_amount > coverage_amount
        ):
            indicator = {
                "rule": "CLAIM_EXCEEDS_RECORDED_COVERAGE",
                "category": "DATA_QUALITY_COVERAGE",
                "severity": "MEDIUM",
                "result": "TRIGGERED",
                "evidence": (
                    f"Claim amount {claim_amount} exceeds "
                    f"recorded coverage {coverage_amount}."
                ),
                "interpretation": (
                    "Potential coverage discrepancy. "
                    "Policy terms, limits, exclusions and source "
                    "data require human verification. "
                    "This is not independently a fraud indicator."
                )
            }

            data_quality_indicators.append(indicator)
            indicators.append(indicator)

        # 7. Determine investigation status
        fraud_risk_count = len(fraud_risk_indicators)
        data_quality_count = len(data_quality_indicators)

        if fraud_risk_count > 0 or data_quality_count > 0:
            investigation_status = "REVIEW_REQUIRED"
        else:
            investigation_status = "NO_INDICATORS_DETECTED"

        # 8. Build conclusion
        if fraud_risk_count > 0 and data_quality_count > 0:
            conclusion = (
                "Fraud-risk screening indicators and data-quality/"
                "coverage discrepancies were detected. "
                "Human investigation is required. "
                "Fraud has not been established."
            )

        elif fraud_risk_count > 0:
            conclusion = (
                "Fraud-risk screening indicators were detected. "
                "Human investigation is required. "
                "Fraud has not been established."
            )

        elif data_quality_count > 0:
            conclusion = (
                "A data-quality/coverage discrepancy was detected. "
                "Policy terms and source data require human verification. "
                "No configured fraud-risk indicators were detected."
            )

        else:
            conclusion = (
                "No configured fraud-risk or data-quality indicators "
                "were detected. This does not establish that the "
                "claim is fraud-free."
            )

        # 9. Return structured investigation result
        return {
            "claim_id": claim_id,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "policy_id": policy_id,
            "claim_date": (
                str(claim_date) if claim_date else None
            ),
            "claim_amount": (
                str(claim_amount) if claim_amount is not None else None
            ),
            "claim_type": claim_type,
            "claim_status": claim_status,
            "fraud_flag": fraud_flag,
            "policy_type": policy_type,
            "coverage_amount": (
                str(coverage_amount)
                if coverage_amount is not None else None
            ),

            "customer_claims_within_30_days": customer_claim_count,
            "policy_claims_within_30_days": policy_claim_count,

            "portfolio_95th_percentile": (
                str(p95_amount) if p95_amount is not None else None
            ),

            "processing_days": processing_days,

            "investigation_status": investigation_status,

            "fraud_risk_indicator_count": fraud_risk_count,
            "data_quality_indicator_count": data_quality_count,
            "total_indicator_count": len(indicators),

            "fraud_risk_indicators": fraud_risk_indicators,
            "data_quality_indicators": data_quality_indicators,

            # Backward compatibility with existing tests
            "indicator_count": len(indicators),
            "indicators": indicators,

            "conclusion": conclusion,

            "decision_controls": {
                "automated_fraud_decision": False,
                "automated_claim_approval": False,
                "automated_claim_rejection": False,
                "source_database_modified": False,
                "human_review_required": (
                    investigation_status == "REVIEW_REQUIRED"
                )
            }
        }

    finally:
        conn.close()


if __name__ == "__main__":
    import json

    test_claim_id = 20001

    print("\nINSUREAI - DETERMINISTIC FRAUD DETECTION")
    print("=" * 70)

    result = detect_claim_risk(test_claim_id)

    print(json.dumps(result, indent=4, default=str))

    print("\n" + "=" * 70)
    print("Source database: Read-only")
    print("Automated fraud decision: Disabled")
    print("Automated claim approval: Disabled")
    print("Automated claim rejection: Disabled")
    print("Human investigation: Required when indicators are detected")
