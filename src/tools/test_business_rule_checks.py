
from src.tools.business_rule_checks import (
    validate_claim_business_rules
)


if __name__ == "__main__":

    claim_id = 20001

    print("\nINSUREAI - BUSINESS RULE VALIDATION")
    print("=" * 60)

    result = validate_claim_business_rules.invoke(
        {"claim_id": claim_id}
    )

    print(result)
