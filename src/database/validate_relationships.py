
import csv
import duckdb

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DUCKDB_PATH = DATA_DIR / "insureai.duckdb"

CHECKS = {
    "Raw claims missing customers": """
        SELECT COUNT(*)
        FROM raw_Claims c
        LEFT JOIN raw_Customers cu
            ON c.Customer_Id = cu.Customer_Id
        WHERE c.Customer_Id IS NULL
           OR cu.Customer_Id IS NULL
    """,

    "Raw claims missing policies": """
        SELECT COUNT(*)
        FROM raw_Claims c
        LEFT JOIN raw_Policies p
            ON c.Policy_Id = p.Policy_Id
        WHERE c.Policy_Id IS NULL
           OR p.Policy_Id IS NULL
    """,

    "Raw policies missing customers": """
        SELECT COUNT(*)
        FROM raw_Policies p
        LEFT JOIN raw_Customers cu
            ON p.Customer_Id = cu.Customer_Id
        WHERE p.Customer_Id IS NULL
           OR cu.Customer_Id IS NULL
    """,

    "Staging claims missing customers": """
        SELECT COUNT(*)
        FROM stg_Claims c
        LEFT JOIN stg_Customers cu
            ON c.Customer_Id = cu.Customer_Id
        WHERE c.Customer_Id IS NULL
           OR cu.Customer_Id IS NULL
    """,

    "Staging claims missing policies": """
        SELECT COUNT(*)
        FROM stg_Claims c
        LEFT JOIN stg_Policies p
            ON c.Policy_Id = p.Policy_Id
        WHERE c.Policy_Id IS NULL
           OR p.Policy_Id IS NULL
    """,

    "Staging policies missing customers": """
        SELECT COUNT(*)
        FROM stg_Policies p
        LEFT JOIN stg_Customers cu
            ON p.Customer_Id = cu.Customer_Id
        WHERE p.Customer_Id IS NULL
           OR cu.Customer_Id IS NULL
    """,

    "Staging claims invalid date keys": """
        SELECT COUNT(*)
        FROM stg_Claims c
        LEFT JOIN dim_Date d
            ON c.Date_Key = d.Date_Key
        WHERE c.Date_Key IS NULL
           OR d.Date_Key IS NULL
    """,

    "Staging claims date mismatches": """
        SELECT COUNT(*)
        FROM stg_Claims c
        INNER JOIN dim_Date d
            ON c.Date_Key = d.Date_Key
        WHERE c.Claim_Date IS NULL
           OR d.Full_Date <> c.Claim_Date
    """,

    "Staging claims invalid risk categories": """
        SELECT COUNT(*)
        FROM stg_Claims c
        WHERE c.Risk_Level IS NULL
           OR c.Risk_Score IS NULL
           OR NOT EXISTS (
               SELECT 1
               FROM dim_RiskCategory r
               WHERE r.Risk_Level = c.Risk_Level
                 AND c.Risk_Score BETWEEN
                     r.Risk_Score_Min AND r.Risk_Score_Max
           )
    """,

    "Snapshot claims missing customers": """
        SELECT COUNT(*)
        FROM claims_snapshot c
        LEFT JOIN raw_Customers cu
            ON c.Customer_Id = cu.Customer_Id
        WHERE c.Customer_Id IS NULL
           OR cu.Customer_Id IS NULL
    """,

    "Snapshot claims missing policies": """
        SELECT COUNT(*)
        FROM claims_snapshot c
        LEFT JOIN raw_Policies p
            ON c.Policy_Id = p.Policy_Id
        WHERE c.Policy_Id IS NULL
           OR p.Policy_Id IS NULL
    """,

    "Duplicate raw claim IDs": """
        SELECT COUNT(*)
        FROM (
            SELECT Claim_Id
            FROM raw_Claims
            GROUP BY Claim_Id
            HAVING COUNT(*) > 1
        ) duplicates
    """,

    "Duplicate raw policy IDs": """
        SELECT COUNT(*)
        FROM (
            SELECT Policy_Id
            FROM raw_Policies
            GROUP BY Policy_Id
            HAVING COUNT(*) > 1
        ) duplicates
    """,

    "Duplicate raw customer IDs": """
        SELECT COUNT(*)
        FROM (
            SELECT Customer_Id
            FROM raw_Customers
            GROUP BY Customer_Id
            HAVING COUNT(*) > 1
        ) duplicates
    """,

    "Duplicate staging claim IDs": """
        SELECT COUNT(*)
        FROM (
            SELECT Claim_Id
            FROM stg_Claims
            GROUP BY Claim_Id
            HAVING COUNT(*) > 1
        ) duplicates
    """,

    "Duplicate staging policy IDs": """
        SELECT COUNT(*)
        FROM (
            SELECT Policy_Id
            FROM stg_Policies
            GROUP BY Policy_Id
            HAVING COUNT(*) > 1
        ) duplicates
    """,

    "Duplicate staging customer IDs": """
        SELECT COUNT(*)
        FROM (
            SELECT Customer_Id
            FROM stg_Customers
            GROUP BY Customer_Id
            HAVING COUNT(*) > 1
        ) duplicates
    """,

    "Duplicate date dimension keys": """
        SELECT COUNT(*)
        FROM (
            SELECT Date_Key
            FROM dim_Date
            GROUP BY Date_Key
            HAVING COUNT(*) > 1
        ) duplicates
    """,

    "Duplicate risk dimension keys": """
        SELECT COUNT(*)
        FROM (
            SELECT Risk_Key
            FROM dim_RiskCategory
            GROUP BY Risk_Key
            HAVING COUNT(*) > 1
        ) duplicates
    """,

    "Duplicate snapshot SCD IDs": """
        SELECT COUNT(*)
        FROM (
            SELECT dbt_scd_id
            FROM claims_snapshot
            GROUP BY dbt_scd_id
            HAVING COUNT(*) > 1
        ) duplicates
    """,

    "Multiple current snapshot versions": """
        SELECT COUNT(*)
        FROM (
            SELECT Claim_Id
            FROM claims_snapshot
            WHERE dbt_valid_to IS NULL
            GROUP BY Claim_Id
            HAVING COUNT(*) > 1
        ) duplicates
    """,
}


def validate_relationships():

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(
        str(DUCKDB_PATH),
        read_only=True
    )

    results = []

    try:
        print("\nINSUREAI - RELATIONSHIP AND DATA QUALITY VALIDATION")
        print("=" * 85)

        for check_name, query in CHECKS.items():

            issue_count = conn.execute(query).fetchone()[0]

            status = "PASS" if issue_count == 0 else "REVIEW"

            results.append({
                "check": check_name,
                "issue_count": issue_count,
                "status": status
            })

            print(
                f"{check_name:<48} "
                f"{issue_count:>8,} "
                f"{status}"
            )

        report_path = DATA_DIR / "relationship_validation.csv"

        with open(
            report_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "check",
                    "issue_count",
                    "status"
                ]
            )

            writer.writeheader()
            writer.writerows(results)

        passed = sum(
            result["status"] == "PASS"
            for result in results
        )

        review = len(results) - passed

        print("\n" + "=" * 85)
        print(f"TOTAL CHECKS: {len(results)}")
        print(f"PASSED:       {passed}")
        print(f"REVIEW:       {review}")
        print(f"\nReport saved: {report_path}")

        if review == 0:
            print("\nALL RELATIONSHIP CHECKS PASSED")
        else:
            print("\nDATA QUALITY ISSUES REQUIRE INVESTIGATION")

    finally:
        conn.close()


if __name__ == "__main__":
    validate_relationships()
