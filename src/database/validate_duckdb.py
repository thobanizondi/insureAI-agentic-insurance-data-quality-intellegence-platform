
import duckdb
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DUCKDB_PATH = PROJECT_ROOT / "data" / "insureai.duckdb"

TABLES = [
    "raw_Claims",
    "raw_Policies",
    "raw_Customers",
    "stg_Claims",
    "stg_Customers",
    "stg_Policies",
    "dim_Date",
    "dim_RiskCategory",
    "claims_snapshot",
]


def validate_database():

    conn = duckdb.connect(str(DUCKDB_PATH), read_only=True)

    try:
        print("\nINSUREAI - DUCKDB DATABASE VALIDATION")
        print("=" * 65)

        tables = conn.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'main'
            ORDER BY table_name
        """).fetchall()

        available_tables = {row[0] for row in tables}

        print(f"\nTables found: {len(available_tables)}")

        missing = set(TABLES) - available_tables

        for table in TABLES:

            if table not in available_tables:
                print(f"{table:<22} MISSING")
                continue

            count = conn.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]

            columns = conn.execute(
                f'PRAGMA table_info("{table}")'
            ).fetchall()

            print(
                f"{table:<22} "
                f"{count:>8,} rows | "
                f"{len(columns):>3} columns | PASS"
            )

        print("\n" + "=" * 65)

        if missing:
            raise RuntimeError(
                f"Missing tables: {sorted(missing)}"
            )

        print("DUCKDB STRUCTURE VALIDATION PASSED")

    finally:
        conn.close()


if __name__ == "__main__":
    validate_database()
