
import json

from langchain_core.tools import tool

from src.database.duckdb_connection import get_duckdb_connection


@tool
def validate_claim_business_rules(claim_id: int) -> str:
    """
    Validate an insurance claim against its linked policy
    using deterministic database business-rule checks.
    """

    conn = get_duckdb_connection()

    try:
        cursor = conn.cursor()

        query = """
            SELECT
                cl.Claim_Id,
                cl.Customer_Id AS Claim_Customer_Id,
                cl.Policy_Id,
                cl.Claim_Date,
                cl.Claim_Amount,
                cl.Claim_Type,
                cl.Claim_Status,
                p.Customer_Id AS Policy_Customer_Id,
                p.Policy_Type,
                p.Coverage_Amount,
                p.Start_Date,
                p.End_Date,
                p.Policy_Status
            FROM raw_Claims cl
            LEFT JOIN raw_Policies p
                ON cl.Policy_Id = p.Policy_Id
            WHERE cl.Claim_Id = ?
        """

        cursor.execute(query, (claim_id,))
        row = cursor.fetchone()

        if row is None:
            return json.dumps({
                "claim_id": claim_id,
                "status": "NOT_FOUND",
                "findings": [
                    {
                        "rule": "CLAIM_EXISTS",
                        "status": "FAIL",
                        "message": "Claim was not found."
                    }
                ]
            }, indent=2)

        columns = [column[0] for column in cursor.description]
        record = dict(zip(columns, row))

    finally:
        conn.close()

    findings = []

    policy_exists = record["Policy_Customer_Id"] is not None

    findings.append({
        "rule": "POLICY_EXISTS",
        "status": "PASS" if policy_exists else "FAIL",
        "message": (
            "Linked policy exists."
            if policy_exists
            else "Linked policy was not found."
        )
    })

    if policy_exists:

        customer_match = (
            record["Claim_Customer_Id"]
            == record["Policy_Customer_Id"]
        )

        findings.append({
            "rule": "CUSTOMER_POLICY_MATCH",
            "status": "PASS" if customer_match else "FAIL",
            "message": (
                "Claim and policy reference the same customer."
                if customer_match
                else "Claim and policy reference different customers."
            )
        })

        claim_date = record["Claim_Date"]
        start_date = record["Start_Date"]
        end_date = record["End_Date"]

        date_valid = (
            start_date <= claim_date <= end_date
        )

        findings.append({
            "rule": "CLAIM_WITHIN_POLICY_DATES",
            "status": "PASS" if date_valid else "REVIEW",
            "message": (
                "Claim date falls within the recorded policy dates."
                if date_valid
                else "Claim date falls outside the recorded policy dates."
            )
        })

        amount_valid = (
            record["Claim_Amount"]
            <= record["Coverage_Amount"]
        )

        findings.append({
            "rule": "CLAIM_WITHIN_RECORDED_COVERAGE",
            "status": "PASS" if amount_valid else "REVIEW",
            "message": (
                "Claim amount does not exceed recorded policy coverage."
                if amount_valid
                else "Claim amount exceeds recorded policy coverage."
            ),
            "claim_amount": str(record["Claim_Amount"]),
            "recorded_coverage": str(record["Coverage_Amount"])
        })

    return json.dumps({
        "claim_id": claim_id,
        "claim_type": record["Claim_Type"],
        "policy_type": record["Policy_Type"],
        "claim_status": record["Claim_Status"],
        "policy_status": record["Policy_Status"],
        "findings": findings,
        "limitations": [
            "Coverage checks use recorded database values.",
            "Policy contracts and endorsements were not checked.",
            "Claim and policy type compatibility has not been validated "
            "because no approved compatibility rules are configured."
        ]
    }, indent=2, default=str)
