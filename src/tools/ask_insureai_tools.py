import re

import sqlglot
from sqlglot import exp

from src.database.duckdb_connection import get_duckdb_connection


ALLOWED_TABLES = {
    "claims_snapshot",
    "dim_date",
    "dim_riskcategory",
    "raw_claims",
    "raw_customers",
    "raw_policies",
    "stg_claims",
    "stg_customers",
    "stg_policies",
}

ALLOWED_METADATA_TABLES = {
    "information_schema.tables",
}

MAX_RESULT_ROWS = 500

FORBIDDEN_FUNCTIONS = {
    "read_csv",
    "read_csv_auto",
    "read_parquet",
    "parquet_scan",
    "read_json",
    "read_json_auto",
    "read_ndjson",
    "read_text",
    "read_blob",
    "read_file",
    "glob",
    "sqlite_scan",
    "postgres_scan",
    "mysql_scan",
    "iceberg_scan",
    "delta_scan",
    "duckdb_scan",
    "query",
    "query_table",
    "http_get",
    "http_post",
    "load_extension",
}


def get_database_schema():
    """Retrieve the actual approved DuckDB schema for the AI prompt."""

    conn = get_duckdb_connection()

    try:
        tables = conn.execute("SHOW TABLES").fetchall()
        schema = []

        for (table_name,) in tables:
            if table_name.lower() not in ALLOWED_TABLES:
                continue

            columns = conn.execute(
                f'DESCRIBE "{table_name}"'
            ).fetchall()

            column_details = [
                f"{column[0]} ({column[1]})"
                for column in columns
            ]

            schema.append(
                f"TABLE: {table_name}\n"
                f"COLUMNS: {', '.join(column_details)}"
            )

        if not schema:
            return "No approved business tables were found."

        return "\n\n".join(schema)

    finally:
        conn.close()


def clean_generated_sql(sql):
    """Remove Markdown formatting from generated SQL."""

    if not isinstance(sql, str):
        raise ValueError("Generated SQL must be text.")

    sql = sql.strip()

    sql = re.sub(
        r"^```(?:sql)?\s*",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(r"\s*```$", "", sql)

    return sql.strip()


def validate_sql(sql):
    """Validate a read-only DuckDB SELECT query using SQLGlot."""

    sql = clean_generated_sql(sql)

    if not sql:
        raise ValueError("No SQL query was generated.")

    try:
        statements = [
            statement
            for statement in sqlglot.parse(
                sql,
                read="duckdb"
            )
            if statement is not None
        ]

    except sqlglot.errors.ParseError as exc:
        raise ValueError(
            f"Invalid SQL syntax: {exc}"
        ) from exc

    if len(statements) != 1:
        raise ValueError(
            "Multiple SQL statements are not permitted."
        )

    statement = statements[0]

    if not isinstance(statement, exp.Select):
        raise ValueError(
            "Only SELECT queries are permitted."
        )

    if any(
        node.comments
        for node in statement.walk()
    ):
        raise ValueError(
            "SQL comments are not permitted."
        )

    cte_names = {
        cte.alias_or_name.lower()
        for cte in statement.find_all(exp.CTE)
    }

    referenced_tables = set()

    for table in statement.find_all(exp.Table):

        if not isinstance(table.this, exp.Identifier):
            raise ValueError(
                "Table functions are not permitted."
            )

        table_name = table.name.lower()

        if not table_name:
            raise ValueError(
                "Invalid table reference."
            )

        if table.catalog:
            raise ValueError(
                "External database references are not permitted."
            )

        if table.db:
            schema_name = table.db.lower()

            if (
                schema_name == "information_schema"
                and table_name == "tables"
            ):
                referenced_tables.add(
                    "information_schema.tables"
                )
                continue

            raise ValueError(
                "Schema-qualified and external database "
                "references are not permitted."
            )

        referenced_tables.add(table_name)

    if not referenced_tables:
        raise ValueError(
            "The query must reference an approved database table."
        )

    invalid_tables = (
        referenced_tables
        - ALLOWED_TABLES
        - ALLOWED_METADATA_TABLES
        - cte_names
    )

    if invalid_tables:
        raise ValueError(
            "Unapproved table references: "
            + ", ".join(sorted(invalid_tables))
        )

    for function in statement.find_all(exp.Func):

        function_name = function.sql_name().lower()

        if isinstance(function, exp.Anonymous):
            function_name = function.name.lower()

        if (
            function_name in FORBIDDEN_FUNCTIONS
            or function_name.startswith("read_")
            or function_name.endswith("_scan")
        ):
            raise ValueError(
                f"External or prohibited function: {function_name}"
            )

    return sql


def execute_read_only_query(sql):
    """Validate and execute a read-only DuckDB query."""

    safe_sql = validate_sql(sql)

    conn = get_duckdb_connection()

    try:
        conn.execute(f"EXPLAIN {safe_sql}")

        limited_sql = (
            f"SELECT * FROM ({safe_sql}) "
            f"AS ask_insureai_result LIMIT {MAX_RESULT_ROWS + 1}"
        )

        dataframe = conn.execute(limited_sql).fetchdf()

        truncated = len(dataframe) > MAX_RESULT_ROWS

        if truncated:
            dataframe = dataframe.head(MAX_RESULT_ROWS)

        return {
            "data": dataframe,
            "columns": dataframe.columns.tolist(),
            "row_count": len(dataframe),
            "truncated": truncated,
            "success": True,
        }

    finally:
        conn.close()