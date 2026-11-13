
import duckdb
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DUCKDB_PATH = PROJECT_ROOT / "data" / "insureai.duckdb"


def inspect_invalid_date_keys():

    conn = duckdb.connect(
        str(DUCKDB_PATH),
        read_only=True
    )

    try:
        print("\nINSUREAI - INVALID DATE KEY INVESTIGATION")
        print("=" * 75)

        total = conn.execute("""
            SELECT COUNT(*)
            FROM stg_Claims
        """).fetchone()[0]

        null_keys = conn.execute("""
            SELECT COUNT(*)
            FROM stg_Claims
            WHERE Date_Key IS NULL
        """).fetchone()[0]

        unmatched_keys = conn.execute("""
            SELECT COUNT(*)
            FROM stg_Claims c
            WHERE c.Date_Key IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM dim_Date d
                  WHERE d.Date_Key = c.Date_Key
              )
        """).fetchone()[0]

        print(f"Total staging claims:       {total:,}")
        print(f"NULL Date_Key values:       {null_keys:,}")
        print(f"Unmatched Date_Key values:  {unmatched_keys:,}")

        print("\nDATE DIMENSION RANGE")
        print("-" * 75)

        date_range = conn.execute("""
            SELECT
                MIN(Full_Date),
                MAX(Full_Date),
                MIN(Date_Key),
                MAX(Date_Key),
                COUNT(*)
            FROM dim_Date
        """).fetchone()

        print(f"Earliest date: {date_range[0]}")
        print(f"Latest date:   {date_range[1]}")
        print(f"Minimum key:   {date_range[2]}")
        print(f"Maximum key:   {date_range[3]}")
        print(f"Date rows:     {date_range[4]:,}")

        print("\nCLAIM DATE RANGE")
        print("-" * 75)

        claim_range = conn.execute("""
            SELECT
                MIN(Claim_Date),
                MAX(Claim_Date),
                COUNT(DISTINCT Claim_Date)
            FROM stg_Claims
        """).fetchone()

        print(f"Earliest claim date: {claim_range[0]}")
        print(f"Latest claim date:   {claim_range[1]}")
        print(f"Distinct dates:      {claim_range[2]:,}")

        print("\nSAMPLE INVALID RECORDS")
        print("-" * 75)

        rows = conn.execute("""
            SELECT
                c.Claim_Id,
                c.Claim_Date,
                c.Date_Key
            FROM stg_Claims c
            LEFT JOIN dim_Date d
                ON c.Date_Key = d.Date_Key
            WHERE c.Date_Key IS NULL
               OR d.Date_Key IS NULL
            ORDER BY c.Claim_Id
            LIMIT 15
        """).fetchall()

        for row in rows:
            print(row)

    finally:
        conn.close()


if __name__ == "__main__":
    inspect_invalid_date_keys()
