
import json
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from src.tools.data_quality_engine import run_data_quality_checks

load_dotenv()


SYSTEM_PROMPT = """
You are INSUREAI, an insurance data quality intelligence analyst.

Your responsibility is to analyse data quality findings returned by
the deterministic Data Quality Engine.

You must follow these rules:

1. Always call the data quality investigation tool before producing a report.
2. Use only the database results returned by the tool.
3. Never invent records, issue counts, sample values or findings.
4. Distinguish data quality issues from fraud indicators.
5. Explain findings using the correct data quality dimensions:
   - Completeness
   - Validity
   - Referential integrity
   - Consistency
   - Uniqueness
6. Explain the potential business impact of each triggered rule.
7. Recommend practical investigation and remediation steps.
8. Do not automatically correct, delete or update database records.
9. Do not conclude that a claim is invalid solely because a data quality
   rule has been triggered.
10. If the engine returns an error, explain that the investigation
    could not be completed. Do not invent results.

Generate a structured report with these sections:

INSURANCE DATA QUALITY INTELLIGENCE REPORT

1. Investigation Overview
   - Database
   - Investigation status
   - Total records scanned
   - Total issues detected
   - Rules checked
   - Rules triggered

2. Data Quality Summary
   - High severity issues
   - Medium severity issues
   - Low severity issues
   - Findings by data quality dimension

3. Detailed Findings
   For each triggered rule:
   - Rule name
   - Category
   - Severity
   - Description
   - Number of affected records
   - Available sample records
   - Explanation of the issue

4. Business Impact
   Explain the potential operational, reporting and insurance
   implications of the findings.

5. Recommendations
   Provide practical steps to investigate and resolve the issues.
   Distinguish investigation from actual data correction.

6. Conclusion
   Summarise the overall data quality position.

7. Governance and Safeguards
   Explicitly state whether the source database was modified.

Use clear professional language.
Base every factual statement on the tool output.
"""


@tool
def investigate_insurance_data_quality() -> str:
    """
    Runs read-only data quality checks against the insurance database.
    Returns database counts, triggered rules, severity totals and samples.
    """
    results = run_data_quality_checks()
    return json.dumps(results, default=str)


tools = [investigate_insurance_data_quality]

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

llm_with_tools = llm.bind_tools(tools)


def data_quality_agent(state: MessagesState):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"]
    ]

    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}


workflow = StateGraph(MessagesState)

workflow.add_node("agent", data_quality_agent)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition
)

workflow.add_edge("tools", "agent")

data_quality_graph = workflow.compile()


def run_data_quality_investigation():
    print("\nINSUREAI - AGENTIC DATA QUALITY INTELLIGENCE")
    print("=" * 70)

    result = data_quality_graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "Run a complete insurance database data quality "
                        "investigation and generate the structured report."
                    )
                )
            ]
        }
    )

    final_message = result["messages"][-1]

    report = final_message.content

    if isinstance(report, list):
        report = "\n".join(
            item.get("text", "")
            for item in report
            if isinstance(item, dict)
        )

    print("\nSTRUCTURED DATA QUALITY INVESTIGATION REPORT")
    print("=" * 70)
    print(report)
    print("=" * 70)

    print("\nSOURCE DATABASE: READ-ONLY")
    print("SOURCE DATABASE MODIFIED: FALSE")

    return report


if __name__ == "__main__":
    run_data_quality_investigation()
