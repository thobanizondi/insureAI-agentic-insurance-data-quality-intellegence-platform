
import os
import json
from typing import Any, TypedDict

import groq
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from src.tools.ask_insureai_tools import (
    get_database_schema,
    execute_read_only_query
)


load_dotenv()

MODEL_NAME = "openai/gpt-oss-120b"
MAX_SQL_ATTEMPTS = 2

# INSUREAI regional configuration
DEFAULT_CURRENCY = "ZAR"
DEFAULT_CURRENCY_SYMBOL = "R"
DEFAULT_LOCALE = "South Africa"

_llm = None


class AskInsureAIState(TypedDict, total=False):
    question: str
    schema: str
    sql: str
    dataframe: Any
    row_count: int
    truncated: bool
    answer: str
    error: str
    attempts: int


def get_llm():
    """Initialize the Groq model when the agent is first used."""

    global _llm

    if _llm is None:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY was not found in the .env file "
                "or the environment (Streamlit Cloud: App Settings > Secrets)."
            )

        _llm = ChatGroq(
            model=MODEL_NAME,
            temperature=0,
            api_key=api_key
        )

    return _llm


def generate_sql(state: AskInsureAIState):
    """Generate DuckDB SQL from the user's question."""

    try:
        schema = get_database_schema()
        attempts = state.get("attempts", 0) + 1

        system_prompt = f"""
You are Ask INSUREAI, an expert insurance data analyst
and DuckDB SQL developer.

Your task is to translate natural-language questions
into accurate SQL queries against the supplied database.

REGIONAL CONTEXT:

INSUREAI is a South African insurance analytics platform.

Default reporting currency: {DEFAULT_CURRENCY}
Currency symbol: {DEFAULT_CURRENCY_SYMBOL}
Region: {DEFAULT_LOCALE}

Important currency rules:

1. Do not assume monetary amounts are denominated in USD.
2. Do not introduce dollar signs into generated SQL aliases
   or calculated results.
3. Do not perform currency conversions unless explicitly
   requested by the user.
4. Preserve the original numerical values stored in the database.
5. Currency formatting belongs to the explanation and
   presentation layers, not SQL calculations.
6. If the database explicitly identifies a different currency,
   do not silently relabel it as ZAR.

DATABASE SCHEMA:
{schema}

DATABASE METADATA ACCESS:

The database catalog can be queried using:

information_schema.tables

This metadata table is an approved source for database
metadata questions.

For questions about the number of tables, generate a query
that counts actual tables from information_schema.tables.

For example:

SELECT COUNT(*) AS table_count
FROM information_schema.tables
WHERE table_schema = 'main'
AND table_type = 'BASE TABLE'

For questions asking which tables exist, retrieve their
actual names from information_schema.tables.

Do not use hardcoded VALUES lists to represent database
tables. Do not guess or invent table names or counts.

DATABASE RULES:

1. Generate DuckDB-compatible SQL only.
2. Only generate read-only SELECT queries.
3. Never generate INSERT, UPDATE, DELETE, DROP,
   ALTER, CREATE or other modification statements.
4. Only use business tables and columns present in the
   supplied schema.
5. Use information_schema.tables only for database
   metadata questions.
6. Prefer staging tables for normal business analytics:
   - stg_Claims
   - stg_Customers
   - stg_Policies
7. Join tables using their actual Customer_Id,
   Policy_Id and other appropriate relationship columns.
8. Do not invent columns, tables, relationships or values.
9. Use meaningful aliases for calculated columns.
10. Use aggregation where appropriate.
11. Do not return SELECT * unless the user specifically
    requests detailed records.
12. Do not access external files or external data sources.
13. Do not include explanations or Markdown formatting
    in the SQL output.
14. Do not use multiple SQL statements.
15. Do not include a trailing semicolon.

Return only the SQL query.

If a previous query failed, correct it using this error:
{state.get("error", "None")}

Previous SQL:
{state.get("sql", "None")}
"""

        response = get_llm().invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["question"])
        ])

        sql = response.content

        if isinstance(sql, list):
            sql = " ".join(
                item.get("text", "")
                if isinstance(item, dict)
                else str(item)
                for item in sql
            )

        return {
            "sql": str(sql).strip(),
            "schema": schema,
            "attempts": attempts,
            "error": ""
        }

    except groq.RateLimitError:
        # Let the dashboard show the friendly quota message.
        raise

    except Exception as exc:
        return {
            "error": f"SQL generation failed: {exc}",
            "attempts": state.get("attempts", 0) + 1
        }


def execute_sql(state: AskInsureAIState):
    """Validate and execute the generated SQL."""

    try:
        result = execute_read_only_query(state["sql"])

        return {
            "dataframe": result["data"],
            "row_count": result["row_count"],
            "truncated": result["truncated"],
            "error": ""
        }

    except Exception as exc:
        return {
            "error": str(exc),
            "dataframe": None,
            "row_count": 0
        }


def explain_results(state: AskInsureAIState):
    """Generate a natural-language explanation of query results."""

    try:
        dataframe = state["dataframe"]

        if dataframe.empty:
            sample_data = []
        else:
            sample_data = dataframe.head(25).to_dict(
                orient="records"
            )

        result_context = {
            "question": state["question"],
            "sql": state["sql"],
            "total_returned_rows": state["row_count"],
            "results_truncated": state.get("truncated", False),
            "sample_results": sample_data,
            "reporting_region": DEFAULT_LOCALE,
            "default_currency": DEFAULT_CURRENCY,
            "currency_symbol": DEFAULT_CURRENCY_SYMBOL
        }

        prompt = f"""
You are Ask INSUREAI, an insurance data analytics assistant.

You provide clear, professional and accurate insurance
analytics for a South African insurance environment.

USER QUESTION:
{state["question"]}

QUERY RESULTS:
{json.dumps(result_context, default=str, indent=2)}

INSTRUCTIONS:

1. Answer the user's actual question.
2. Use only the supplied query results.
3. Never invent statistics, findings or explanations.
4. Highlight important patterns where supported.
5. Mention when no matching records were found.
6. If results were truncated, disclose this.
7. Distinguish potential fraud indicators from confirmed fraud.
8. Do not make insurance approval, rejection or settlement
   decisions.
9. Keep the answer concise, structured and useful.
10. Do not repeat the SQL query in your explanation.
11. Do not claim that records are complete unless the
    supplied result metadata supports that statement.

CURRENCY AND REGIONAL FORMATTING:

12. INSUREAI uses South African Rand (ZAR) as its
    default reporting currency.
13. For monetary amounts confirmed or assumed by the
    platform's reporting convention to be ZAR, use
    the prefix R.

    Correct example: R254,719.20
    Incorrect example: $254,719.20

14. Never use the $ symbol for default INSUREAI monetary
    reporting.
15. Use two decimal places and comma-separated thousands
    when presenting monetary values.
16. Do not convert, recalculate or change the underlying
    numerical values merely to change their presentation.
17. Do not invent exchange rates or perform currency
    conversions unless explicitly requested.
18. If the supplied database results explicitly identify
    another currency, disclose that currency instead of
    silently labelling it ZAR.
19. If the currency is not identified in the database,
    use the platform's default reporting convention of ZAR
    and avoid claiming that the database independently
    verified the currency.

REPORTING STYLE:

- Use clear section headings where useful.
- Use tables for comparisons between categories.
- Use concise bullet points for key observations.
- Keep numerical values consistent with the query results.
- Use South African English spelling and terminology.

"""

        response = get_llm().invoke([
            SystemMessage(content=prompt),
            HumanMessage(content="Explain these query results.")
        ])

        return {
            "answer": str(response.content).strip()
        }

    except groq.RateLimitError:
        # Let the dashboard show the friendly quota message.
        raise

    except Exception as exc:
        return {
            "answer": (
                "The SQL query executed successfully, but "
                f"the explanation could not be generated: {exc}"
            )
        }


def handle_failure(state: AskInsureAIState):
    """Return a controlled error if processing fails."""

    return {
        "answer": (
            "I could not complete your request safely. "
            f"Details: {state.get('error', 'Unknown error')}"
        )
    }


def route_after_generation(state: AskInsureAIState):
    if state.get("error"):
        return "failed"

    return "execute"


def route_after_execution(state: AskInsureAIState):
    if state.get("error"):
        if state.get("attempts", 0) < MAX_SQL_ATTEMPTS:
            return "retry"

        return "failed"

    return "explain"


# ---------------------------------------------------------
# LANGGRAPH WORKFLOW
# ---------------------------------------------------------

workflow = StateGraph(AskInsureAIState)

workflow.add_node("generate_sql", generate_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("explain_results", explain_results)
workflow.add_node("handle_failure", handle_failure)

workflow.add_edge(START, "generate_sql")

workflow.add_conditional_edges(
    "generate_sql",
    route_after_generation,
    {
        "execute": "execute_sql",
        "failed": "handle_failure"
    }
)

workflow.add_conditional_edges(
    "execute_sql",
    route_after_execution,
    {
        "retry": "generate_sql",
        "explain": "explain_results",
        "failed": "handle_failure"
    }
)

workflow.add_edge("explain_results", END)
workflow.add_edge("handle_failure", END)

ask_insureai_workflow = workflow.compile()


# ---------------------------------------------------------
# PUBLIC AGENT ENTRY POINT
# ---------------------------------------------------------

def ask_insureai(question: str):
    """Public entry point for the Ask INSUREAI agent."""

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    result = ask_insureai_workflow.invoke({
        "question": question.strip(),
        "attempts": 0,
        "error": ""
    })

    return {
        "question": result["question"],
        "sql": result.get("sql", ""),
        "answer": result.get("answer", ""),
        "data": result.get("dataframe"),
        "row_count": result.get("row_count", 0),
        "truncated": result.get("truncated", False),
        "success": result.get("dataframe") is not None
    }
