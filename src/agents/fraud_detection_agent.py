
import os
import json

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from src.tools.fraud_detection_engine import detect_claim_risk

load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise EnvironmentError(
        "GROQ_API_KEY was not found. Check your project .env file."
    )


@tool
def investigate_insurance_claim(claim_id: int) -> str:
    """
    Retrieve fraud-risk and data-quality investigation evidence
    for an insurance claim using the read-only DuckDB engine.
    """
    try:
        result = detect_claim_risk(claim_id)
        return json.dumps(result, indent=2, default=str)

    except Exception as error:
        return json.dumps({
            "status": "ERROR",
            "claim_id": claim_id,
            "message": str(error)
        })


tools = [investigate_insurance_claim]

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

llm_with_tools = llm.bind_tools(tools)


SYSTEM_PROMPT = """
You are InsureAI, an AI-assisted insurance fraud investigation
and data quality intelligence agent.

Analyse only the evidence returned by the deterministic
insurance claim investigation tool.

INVESTIGATION RULES:

1. Always use the investigate_insurance_claim tool before
   analysing a claim.
2. Never invent claim, customer, policy or detection information.
3. Distinguish fraud-risk indicators from data-quality and
   coverage indicators.
4. An existing Fraud_Flag = Yes is a source-system flag,
   not independently verified fraud.
5. Frequent claims and unusually high claim amounts are
   screening indicators, not proof of fraud.
6. A claim exceeding recorded policy coverage is a potential
   coverage or data-quality discrepancy, not proof of fraud.
7. Never automatically approve or reject a claim.
8. Never declare a claim fraudulent or fraud-free.
9. Recommend human investigation when indicators are detected.
10. If the claim is not found or the tool returns an error,
    explain that the investigation could not be completed.

REPORT FORMAT:

INSUREAI - FRAUD INVESTIGATION REPORT

1. CLAIM INFORMATION
- Claim ID
- Customer
- Policy ID
- Claim date
- Claim amount
- Claim type
- Claim status

2. FRAUD-RISK ANALYSIS
- Number of fraud-risk indicators
- Triggered rules
- Evidence
- Severity
- Interpretation

3. DATA QUALITY AND COVERAGE ANALYSIS
- Number of data-quality indicators
- Triggered rules
- Evidence
- Interpretation

4. INVESTIGATION ASSESSMENT
- Overall investigation status
- Key findings
- Potential concerns

5. RECOMMENDED INVESTIGATION ACTIONS
- Evidence and documentation to verify
- Policy information to review
- Recommended human investigation steps

6. FINAL CONCLUSION
- Summarise the available evidence.
- State whether human review is required.
- Explicitly state that fraud has not been established.

Only report facts supported by the tool output.
If information is unavailable, state that it is unavailable.
"""


def fraud_detection_agent(state: MessagesState):
    response = llm_with_tools.invoke(
        [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    )
    return {"messages": [response]}


workflow = StateGraph(MessagesState)

workflow.add_node("fraud_detection_agent", fraud_detection_agent)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "fraud_detection_agent")

workflow.add_conditional_edges(
    "fraud_detection_agent",
    tools_condition
)

workflow.add_edge("tools", "fraud_detection_agent")
workflow.add_edge("fraud_detection_agent", END)

fraud_graph = workflow.compile()


def run_fraud_investigation(claim_id: int):

    if (
        not isinstance(claim_id, int)
        or isinstance(claim_id, bool)
        or claim_id <= 0
    ):
        raise ValueError("Claim ID must be a positive integer.")

    print("\nINSUREAI - AGENTIC FRAUD DETECTION")
    print("=" * 70)
    print(f"Investigating Claim ID: {claim_id}")

    result = fraud_graph.invoke({
        "messages": [
            HumanMessage(
                content=(
                    f"Conduct a fraud-risk investigation for insurance "
                    f"claim ID {claim_id}. Retrieve the evidence and "
                    "generate the complete structured investigation report."
                )
            )
        ]
    })

    print("\nSTRUCTURED INVESTIGATION REPORT")
    print("=" * 70)

    final_report = None

    for message in result["messages"]:
        if isinstance(message, AIMessage) and not message.tool_calls:
            final_report = message.content

    if final_report is None:
        print("No final investigation report was generated.")
    else:
        print(final_report)

    print("\n" + "=" * 70)
    print("Investigation completed.")
    print("Source database: Read-only")
    print("Automated fraud decision: Disabled")
    print("Automated claim approval: Disabled")
    print("Automated claim rejection: Disabled")

    return result


if __name__ == "__main__":
    TEST_CLAIM_ID = 21319
    run_fraud_investigation(TEST_CLAIM_ID)
