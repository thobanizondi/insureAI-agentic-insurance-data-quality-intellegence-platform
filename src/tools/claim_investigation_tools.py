
import csv
import json
from pathlib import Path

from langchain_core.tools import tool
from src.database.duckdb_connection import get_duckdb_connection


def execute_query(query, parameters):
    """Execute a read-only SQL query and return its first row."""

    conn = get_duckdb_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(query, parameters)

        row = cursor.fetchone()

        if row is None:
            return None

        columns = [column[0] for column in cursor.description]

        return dict(zip(columns, row))

    finally:
        conn.close()


@tool
def get_claim_details(claim_id: int) -> str:
    """Retrieve an insurance claim and its associated customer details using its claim ID."""

    query = """
        SELECT
            cl.Claim_Id,
            cl.Customer_Id,
            cu.Customer_Name,
            cu.Age,
            cu.Province,
            cl.Policy_Id,
            cl.Claim_Date,
            cl.Claim_Amount,
            cl.Claim_Type,
            cl.Claim_Status,
            cl.Fraud_Flag,
            cl.Processing_Days
        FROM raw_Claims cl
        LEFT JOIN raw_Customers cu
            ON cl.Customer_Id = cu.Customer_Id
        WHERE cl.Claim_Id = ?
    """

    result = execute_query(query, (claim_id,))

    if result is None:
        return f"No claim found with ID {claim_id}."

    return json.dumps(result, default=str, indent=2)


@tool
def get_policy_details(policy_id: int) -> str:
    """Retrieve policy type, coverage, premium, dates and status using its policy ID."""

    query = """
        SELECT
            Policy_Id,
            Customer_Id,
            Policy_Type,
            Coverage_Amount,
            Premium_Amount,
            Start_Date,
            End_Date,
            Policy_Status
        FROM raw_Policies
        WHERE Policy_Id = ?
    """

    result = execute_query(query, (policy_id,))

    if result is None:
        return f"No policy found with ID {policy_id}."

    return json.dumps(result, default=str, indent=2)


@tool
def get_claim_issues(claim_id: int) -> str:
    """Retrieve all detected data-quality issues for a claim from the issue register."""

    project_root = Path(__file__).resolve().parents[2]
    issue_file = project_root / "reports" / "claim_issue_register.csv"

    if not issue_file.exists():
        return "Issue register not found. Run the issue register builder first."

    matching_issues = []

    with open(issue_file, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if str(row.get("Claim_ID", "")).strip() == str(claim_id):
                matching_issues.append(row)

    if not matching_issues:
        return f"No recorded data-quality issues found for claim {claim_id}."

    return json.dumps(matching_issues, indent=2)
