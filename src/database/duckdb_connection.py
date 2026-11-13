
from pathlib import Path
import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DUCKDB_PATH = PROJECT_ROOT / "data" / "insureai.duckdb"


def get_duckdb_connection():
    if not DUCKDB_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: {DUCKDB_PATH}"
        )

    return duckdb.connect(
        database=str(DUCKDB_PATH),
        read_only=True,
        config={
            "enable_external_access": "false",
            "allow_unsigned_extensions": "false"
        }
    )
