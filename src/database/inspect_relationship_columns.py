
import duckdb
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DUCKDB_PATH = PROJECT_ROOT / "data" / "insureai.duckdb"

TABLES = [
    "raw_Claims",
    "raw_Policies",
    "raw_Customers",
    "stg_Claims",
    "stg_Policies",
    "stg_Customers",
    "claims_snapshot",
]


def inspect_columns():

    conn = duckdb.connect(str(DUCKDB_PATH), read_only=True)

    try:
        print("\nINSUREAI - RELATIONSHIP COLUMN INSPECTION")
        print("=" * 75)

        for table in TABLES:

            print(f"\n{table}")
            print("-" * 75)

            columns = conn.execute(
                f'PRAGMA table_info("{table}")'
            ).fetchall()

            for column in columns:
                print(
                    f"{column[1]:<30} {column[2]}"
                )

    finally:
        conn.close()


if __name__ == "__main__":
    inspect_columns()
