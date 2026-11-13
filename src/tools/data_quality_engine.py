
import json

from src.database.duckdb_connection import get_duckdb_connection


DATA_QUALITY_RULES = {
    "CLAIM_MISSING_CUSTOMER_ID": {
        "category": "COMPLETENESS",
        "severity": "HIGH",
        "description": "Claims with missing customer IDs.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Claims
            WHERE Customer_Id IS NULL
        """,
        "sample_sql": """SELECT Claim_Id, Customer_Id, Policy_Id
            FROM raw_Claims
            WHERE Customer_Id IS NULL
            LIMIT 10
        """
    },
    "CLAIM_MISSING_POLICY_ID": {
        "category": "COMPLETENESS",
        "severity": "HIGH",
        "description": "Claims with missing policy IDs.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Claims
            WHERE Policy_Id IS NULL
        """,
        "sample_sql": """SELECT Claim_Id, Customer_Id, Policy_Id
            FROM raw_Claims
            WHERE Policy_Id IS NULL
            LIMIT 10
        """
    },
    "CLAIM_INVALID_AMOUNT": {
        "category": "VALIDITY",
        "severity": "HIGH",
        "description": "Claims with zero or negative claim amounts.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Claims
            WHERE Claim_Amount <= 0
        """,
        "sample_sql": """SELECT Claim_Id, Claim_Amount
            FROM raw_Claims
            WHERE Claim_Amount <= 0
            LIMIT 10
        """
    },
    "CLAIM_MISSING_DATE": {
        "category": "COMPLETENESS",
        "severity": "MEDIUM",
        "description": "Claims with missing claim dates.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Claims
            WHERE Claim_Date IS NULL
        """,
        "sample_sql": """SELECT Claim_Id, Claim_Date
            FROM raw_Claims
            WHERE Claim_Date IS NULL
            LIMIT 10
        """
    },
    "CLAIM_ORPHAN_CUSTOMER": {
        "category": "REFERENTIAL_INTEGRITY",
        "severity": "HIGH",
        "description": "Claims referencing customers that do not exist.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Claims c
            LEFT JOIN raw_Customers cu
                ON c.Customer_Id = cu.Customer_Id
            WHERE c.Customer_Id IS NOT NULL
              AND cu.Customer_Id IS NULL
        """,
        "sample_sql": """SELECT
                c.Claim_Id,
                c.Customer_Id,
                c.Policy_Id
            FROM raw_Claims c
            LEFT JOIN raw_Customers cu
                ON c.Customer_Id = cu.Customer_Id
            WHERE c.Customer_Id IS NOT NULL
              AND cu.Customer_Id IS NULL
            LIMIT 10
        """
    },
    "CLAIM_ORPHAN_POLICY": {
        "category": "REFERENTIAL_INTEGRITY",
        "severity": "HIGH",
        "description": "Claims referencing policies that do not exist.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Claims c
            LEFT JOIN raw_Policies p
                ON c.Policy_Id = p.Policy_Id
            WHERE c.Policy_Id IS NOT NULL
              AND p.Policy_Id IS NULL
        """,
        "sample_sql": """SELECT
                c.Claim_Id,
                c.Customer_Id,
                c.Policy_Id
            FROM raw_Claims c
            LEFT JOIN raw_Policies p
                ON c.Policy_Id = p.Policy_Id
            WHERE c.Policy_Id IS NOT NULL
              AND p.Policy_Id IS NULL
            LIMIT 10
        """
    },
    "CLAIM_CUSTOMER_POLICY_MISMATCH": {
        "category": "REFERENTIAL_INTEGRITY",
        "severity": "HIGH",
        "description": "Claims where the customer does not match the customer recorded against the policy.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Claims c
            INNER JOIN raw_Policies p
                ON c.Policy_Id = p.Policy_Id
            WHERE c.Customer_Id IS NOT NULL
              AND p.Customer_Id IS NOT NULL
              AND c.Customer_Id <> p.Customer_Id
        """,
        "sample_sql": """SELECT
                c.Claim_Id,
                c.Customer_Id AS Claim_Customer_Id,
                c.Policy_Id,
                p.Customer_Id AS Policy_Customer_Id
            FROM raw_Claims c
            INNER JOIN raw_Policies p
                ON c.Policy_Id = p.Policy_Id
            WHERE c.Customer_Id IS NOT NULL
              AND p.Customer_Id IS NOT NULL
              AND c.Customer_Id <> p.Customer_Id
            LIMIT 10
        """
    },
    "POLICY_INVALID_COVERAGE": {
        "category": "VALIDITY",
        "severity": "HIGH",
        "description": "Policies with zero or negative coverage amounts.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Policies
            WHERE Coverage_Amount <= 0
        """,
        "sample_sql": """SELECT Policy_Id, Coverage_Amount
            FROM raw_Policies
            WHERE Coverage_Amount <= 0
            LIMIT 10
        """
    },
    "POLICY_INVALID_PREMIUM": {
        "category": "VALIDITY",
        "severity": "MEDIUM",
        "description": "Policies with negative premium amounts.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Policies
            WHERE Premium_Amount < 0
        """,
        "sample_sql": """SELECT Policy_Id, Premium_Amount
            FROM raw_Policies
            WHERE Premium_Amount < 0
            LIMIT 10
        """
    },
    "POLICY_INVALID_DATE_RANGE": {
        "category": "CONSISTENCY",
        "severity": "HIGH",
        "description": "Policies with an end date earlier than the start date.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Policies
            WHERE Start_Date IS NOT NULL
              AND End_Date IS NOT NULL
              AND End_Date < Start_Date
        """,
        "sample_sql": """SELECT
                Policy_Id,
                Start_Date,
                End_Date
            FROM raw_Policies
            WHERE Start_Date IS NOT NULL
              AND End_Date IS NOT NULL
              AND End_Date < Start_Date
            LIMIT 10
        """
    },
    "POLICY_MISSING_START_DATE": {
        "category": "COMPLETENESS",
        "severity": "MEDIUM",
        "description": "Policies with missing start dates.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Policies
            WHERE Start_Date IS NULL
        """,
        "sample_sql": """SELECT Policy_Id, Start_Date
            FROM raw_Policies
            WHERE Start_Date IS NULL
            LIMIT 10
        """
    },
    "POLICY_MISSING_END_DATE": {
        "category": "COMPLETENESS",
        "severity": "LOW",
        "description": "Policies with missing end dates.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Policies
            WHERE End_Date IS NULL
        """,
        "sample_sql": """SELECT Policy_Id, End_Date
            FROM raw_Policies
            WHERE End_Date IS NULL
            LIMIT 10
        """
    },
    "CLAIM_OUTSIDE_POLICY_PERIOD": {
        "category": "CONSISTENCY",
        "severity": "HIGH",
        "description": "Claims dated outside their recorded policy period.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Claims c
            INNER JOIN raw_Policies p
                ON c.Policy_Id = p.Policy_Id
            WHERE c.Claim_Date IS NOT NULL
              AND (
                    (p.Start_Date IS NOT NULL
                     AND c.Claim_Date < p.Start_Date)
                 OR (p.End_Date IS NOT NULL
                     AND c.Claim_Date > p.End_Date)
              )
        """,
        "sample_sql": """SELECT
                c.Claim_Id,
                c.Policy_Id,
                c.Claim_Date,
                p.Start_Date,
                p.End_Date
            FROM raw_Claims c
            INNER JOIN raw_Policies p
                ON c.Policy_Id = p.Policy_Id
            WHERE c.Claim_Date IS NOT NULL
              AND (
                    (p.Start_Date IS NOT NULL
                     AND c.Claim_Date < p.Start_Date)
                 OR (p.End_Date IS NOT NULL
                     AND c.Claim_Date > p.End_Date)
              )
            LIMIT 10
        """
    },
    "CUSTOMER_MISSING_NAME": {
        "category": "COMPLETENESS",
        "severity": "MEDIUM",
        "description": "Customers with missing or blank customer names.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Customers
            WHERE Customer_Name IS NULL
               OR LTRIM(RTRIM(Customer_Name)) = ''
        """,
        "sample_sql": """SELECT Customer_Id, Customer_Name
            FROM raw_Customers
            WHERE Customer_Name IS NULL
               OR LTRIM(RTRIM(Customer_Name)) = ''
            LIMIT 10
        """
    },
    "CUSTOMER_INVALID_AGE": {
        "category": "VALIDITY",
        "severity": "MEDIUM",
        "description": "Customers with ages outside the configured 0 to 120 range.",
        "count_sql": """
            SELECT COUNT(*)
            FROM raw_Customers
            WHERE Age < 0 OR Age > 120
        """,
        "sample_sql": """SELECT Customer_Id, Age
            FROM raw_Customers
            WHERE Age < 0 OR Age > 120
            LIMIT 10
        """
    },
    "DUPLICATE_CLAIM_RECORDS": {
        "category": "UNIQUENESS",
        "severity": "HIGH",
        "description": "Repeated combinations of customer, policy, date and claim amount.",
        "count_sql": """
            SELECT COUNT(*)
            FROM (
                SELECT
                    Customer_Id,
                    Policy_Id,
                    Claim_Date,
                    Claim_Amount
                FROM raw_Claims
                GROUP BY
                    Customer_Id,
                    Policy_Id,
                    Claim_Date,
                    Claim_Amount
                HAVING COUNT(*) > 1
            ) duplicates
        """,
        "sample_sql": """SELECT
                Customer_Id,
                Policy_Id,
                Claim_Date,
                Claim_Amount,
                COUNT(*) AS Duplicate_Count
            FROM raw_Claims
            GROUP BY
                Customer_Id,
                Policy_Id,
                Claim_Date,
                Claim_Amount
            HAVING COUNT(*) > 1
            ORDER BY Duplicate_Count DESC
            LIMIT 10
        """
    }
}


def get_table_counts(cursor):
    counts = {}

    tables = {
        "claims": "raw_Claims",
        "policies": "raw_Policies",
        "customers": "raw_Customers"
    }

    for name, table in tables.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts[name] = cursor.fetchone()[0]

    return counts


def run_data_quality_checks():

    connection = None
    cursor = None

    try:
        connection = get_duckdb_connection()
        cursor = connection.cursor()

        table_counts = get_table_counts(cursor)

        total_issues = 0
        high_severity_issues = 0
        medium_severity_issues = 0
        low_severity_issues = 0

        findings = []

        for rule_name, rule in DATA_QUALITY_RULES.items():

            cursor.execute(rule["count_sql"])
            issue_count = cursor.fetchone()[0]

            if issue_count == 0:
                continue

            cursor.execute(rule["sample_sql"])
            columns = [column[0] for column in cursor.description]

            samples = [
                dict(zip(columns, row))
                for row in cursor.fetchmany(10)
            ]

            total_issues += issue_count

            if rule["severity"] == "HIGH":
                high_severity_issues += issue_count
            elif rule["severity"] == "MEDIUM":
                medium_severity_issues += issue_count
            else:
                low_severity_issues += issue_count

            findings.append({
                "rule": rule_name,
                "category": rule["category"],
                "severity": rule["severity"],
                "description": rule["description"],
                "issue_count": issue_count,
                "sample_records": samples
            })

        status = "ISSUES_DETECTED" if total_issues else "NO_ISSUES_DETECTED"

        return {
            "status": "SUCCESS",
            "investigation_status": status,
            "database": "insureai.duckdb",
            "table_counts": table_counts,
            "total_records": sum(table_counts.values()),
            "total_issues": total_issues,
            "high_severity_issues": high_severity_issues,
            "medium_severity_issues": medium_severity_issues,
            "low_severity_issues": low_severity_issues,
            "rules_checked": len(DATA_QUALITY_RULES),
            "rules_triggered": len(findings),
            "findings": findings,
            "source_database_modified": False
        }

    except Exception as error:
        return {
            "status": "ERROR",
            "message": str(error),
            "source_database_modified": False
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":

    result = run_data_quality_checks()

    print("\nINSUREAI - DATA QUALITY INTELLIGENCE")
    print("=" * 70)
    print(json.dumps(result, indent=2, default=str))
    print("=" * 70)
    print("Source database: Read-only")
    print("Source database modified: False")
