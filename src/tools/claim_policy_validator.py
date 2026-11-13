
from src.database.duckdb_connection import get_duckdb_connection


# Approved combinations must be confirmed against business rules.
# Empty mappings mean REVIEW, not automatic rejection.
APPROVED_COMPATIBILITY = {
    # Example:
    # "Motor": ["Accident", "Theft"],
    # "Home": ["Fire", "Theft", "Natural Disaster"],
    # "Medical": ["Medical"],
    # "Life": ["Medical"]
}

# Only populate this mapping when an authoritative business rule
# explicitly prohibits a particular combination.
PROHIBITED_COMPATIBILITY = {
    # Example:
    # "Motor": ["Life"]
}


def validate_claim_policy(claim_id: int):
    """
    Validate whether a claim type is compatible with its policy type.

    PASS   - Combination exists in approved business rules.
    REVIEW - Combination has not been configured.
    FAIL   - Combination is explicitly prohibited by an
             authoritative business rule.
    """

    conn = get_duckdb_connection()

    try:
        cursor = conn.cursor()

        query = """
            SELECT
                cl.Claim_Id,
                cl.Customer_Id,
                cl.Policy_Id,
                cl.Claim_Type,
                p.Policy_Type
            FROM raw_Claims cl
            INNER JOIN raw_Policies p
                ON cl.Policy_Id = p.Policy_Id
            WHERE cl.Claim_Id = ?
              AND cl.Customer_Id = p.Customer_Id
        """

        cursor.execute(query, (claim_id,))
        row = cursor.fetchone()

        if row is None:
            return {
                "claim_id": claim_id,
                "rule": "CLAIM_POLICY_TYPE_COMPATIBILITY",
                "status": "REVIEW",
                "reason": (
                    "Claim or associated policy could not be "
                    "retrieved with a matching customer ID."
                )
            }

        claim_id, customer_id, policy_id, claim_type, policy_type = row

        claim_type = str(claim_type).strip()
        policy_type = str(policy_type).strip()

        approved_types = APPROVED_COMPATIBILITY.get(
            policy_type, []
        )

        prohibited_types = PROHIBITED_COMPATIBILITY.get(
            policy_type, []
        )

        if claim_type in approved_types:
            status = "PASS"
            reason = (
                f"{claim_type} claim is approved for "
                f"{policy_type} policy under configured business rules."
            )

        elif claim_type in prohibited_types:
            status = "FAIL"
            reason = (
                f"{claim_type} claim is explicitly prohibited "
                f"under {policy_type} policy by configured business rules."
            )

        else:
            status = "REVIEW"
            reason = (
                f"No approved or prohibited compatibility rule exists "
                f"for {claim_type} claim under {policy_type} policy. "
                f"Human verification is required."
            )

        return {
            "claim_id": claim_id,
            "customer_id": customer_id,
            "policy_id": policy_id,
            "claim_type": claim_type,
            "policy_type": policy_type,
            "rule": "CLAIM_POLICY_TYPE_COMPATIBILITY",
            "status": status,
            "reason": reason
        }

    finally:
        conn.close()


if __name__ == "__main__":

    test_claim_id = 20001

    print("\nINSUREAI - CLAIM POLICY COMPATIBILITY VALIDATION")
    print("=" * 65)

    result = validate_claim_policy(test_claim_id)

    for key, value in result.items():
        print(f"{key}: {value}")

    print("=" * 65)
