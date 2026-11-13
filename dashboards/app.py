
import contextlib
import importlib
import io
import inspect
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import plotly.express as px


st.set_page_config(
    page_title="Thobani-INSUREAI | Insurance Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #0B1220;
    --navy-light: #111D30;
    --card: #15243A;
    --card-light: #1B304A;
    --border: #2B405C;
    --text: #F1F5F9;
    --muted: #A7B7CB;
    --teal: #35C6B0;
    --blue: #60A5FA;
    --purple: #A78BFA;
    --orange: #F5AD55;
    --red: #F87171;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 85% 5%, #17304A 0%, transparent 28%),
        linear-gradient(135deg, #0B1220, #101B2C);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: #FFFFFF !important;
    color: #000000 !important;
}

[data-testid="stHeader"] *,
[data-testid="stHeader"] button,
[data-testid="stHeader"] svg,
[data-testid="stToolbar"] * {
    color: #000000 !important;
    fill: #000000 !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101D30, #0C1728);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

h1, h2, h3 {
    color: var(--text);
    font-weight: 750;
    letter-spacing: -0.5px;
}

p, label {
    color: var(--muted);
}

.hero {
    background:
        radial-gradient(circle at 90% 10%, #236B71 0%, transparent 35%),
        linear-gradient(120deg, #172B47, #102B3A);
    border: 1px solid #31566A;
    border-radius: 20px;
    padding: 34px;
    margin-bottom: 28px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.18);
}

.hero-label {
    color: var(--teal);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
}

.hero-title {
    color: #FFFFFF;
    font-size: 36px;
    font-weight: 800;
    margin-top: 12px;
    line-height: 1.2;
}

.hero-text {
    color: #C4D2E2;
    font-size: 15px;
    line-height: 1.8;
    max-width: 780px;
    margin-top: 12px;
}

.metric-card {
    background: linear-gradient(145deg, #1B304A, #122137);
    border: 1px solid #304762;
    border-radius: 15px;
    padding: 21px;
    min-height: 135px;
    box-shadow: 0 7px 20px rgba(0,0,0,0.12);
}

.metric-label {
    color: #A9BBD0;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}

.metric-value {
    color: #FFFFFF;
    font-size: 32px;
    font-weight: 800;
    margin-top: 12px;
}

.metric-caption {
    color: var(--teal);
    font-size: 12px;
    margin-top: 5px;
}

.agent-card {
    background: linear-gradient(145deg, #1A2D46, #132238);
    border: 1px solid #304762;
    border-radius: 16px;
    padding: 21px;
    min-height: 205px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.13);
}

.agent-icon {
    font-size: 30px;
    margin-bottom: 13px;
}

.agent-title {
    color: #F8FAFC;
    font-size: 17px;
    font-weight: 750;
}

.agent-description {
    color: #AFC0D3;
    font-size: 13px;
    line-height: 1.7;
    margin-top: 10px;
}

.status-good {
    color: #48D6B9;
    font-size: 12px;
    font-weight: 700;
}

.status-warning {
    color: #F6BD67;
    font-size: 12px;
    font-weight: 700;
}

.section-card {
    background: linear-gradient(145deg, #172940, #122035);
    border: 1px solid #2C425D;
    border-radius: 15px;
    padding: 22px;
    margin-bottom: 12px;
}

.brand {
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.7px;
    color: #FFFFFF;
}

.brand-accent {
    color: var(--teal);
}

.brand-caption {
    font-size: 10px;
    color: #91A8C0;
    letter-spacing: 2px;
    font-weight: 700;
}

div.stButton > button {
    background: linear-gradient(100deg, #138D83, #20A99A);
    color: #FFFFFF;
    border: 1px solid #36BBAA;
    border-radius: 9px;
    min-height: 44px;
    font-weight: 700;
    transition: 0.2s ease;
}

div.stButton > button:hover {
    background: linear-gradient(100deg, #1BA99A, #35C6B0);
    border-color: #71E0CF;
    color: white;
    transform: translateY(-1px);
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #192D46, #132238);
    border: 1px solid #304762;
    border-radius: 13px;
    padding: 16px;
}

[data-testid="stMetricValue"] {
    color: #FFFFFF;
}

[data-testid="stMetricLabel"] {
    color: #AABBD0;
}

[data-testid="stMetricDelta"] {
    color: var(--teal);
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #138D83, #52D6BF);
}

.stTabs [data-baseweb="tab"] {
    color: #B4C3D5;
}

.stTabs [aria-selected="true"] {
    color: #55D4BE;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background-color: #15243A;
    border-color: #344B67;
}

input {
    color: #FFFFFF !important;
}

pre {
    white-space: pre-wrap !important;
    word-break: break-word;
}

code {
    color: #65D9C6;
}

hr {
    border-color: #30445E;
}

[data-testid="stAlert"] {
    border-radius: 10px;
}

footer {
    visibility: hidden;
}

[data-testid="stNumberInput"],
[data-testid="stTextInput"],
[data-testid="stSelectbox"],
[data-testid="stMultiSelect"],
[data-testid="stDateInput"],
[data-testid="stTimeInput"],
[data-testid="stTextArea"] {
    color: #FFFFFF !important;
}

[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stDateInput"] label,
[data-testid="stTimeInput"] label,
[data-testid="stTextArea"] label,
.stNumberInput label,
.stTextInput label,
.stSelectbox label {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    font-weight: 700 !important;
    opacity: 1 !important;
    caret-color: #000000 !important;
}

[data-testid="stNumberInput"] button {
    color: #000000 !important;
    background-color: #FFFFFF !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #000000 !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stMultiSelect"] [data-baseweb="select"] * {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

[data-baseweb="popover"] *,
[role="listbox"] *,
[role="option"] {
    color: #000000 !important;
    font-weight: 600 !important;
}

input::placeholder,
textarea::placeholder {
    color: #333333 !important;
    -webkit-text-fill-color: #333333 !important;
    opacity: 1 !important;
}

.stApp,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp p,
.stApp label,
.stApp [data-testid="stMarkdownContainer"] {
    color: #FFFFFF;
}

[data-testid="stSidebar"],
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

[data-testid="stHeader"],
[data-testid="stHeader"] * {
    color: #000000 !important;
}

[data-testid="stAlert"],
[data-testid="stAlert"] *,
[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span,
[data-testid="stAlert"] [data-testid="stMarkdownContainer"],
[data-testid="stAlert"] [data-testid="stMarkdownContainer"] * {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    font-weight: 600 !important;
}

[data-testid="stAlert"] svg {
    fill: #000000 !important;
    color: #000000 !important;
}

[data-testid="stDownloadButton"] button,
[data-testid="stDownloadButton"] button *,
[data-testid="stDownloadButton"] button p,
[data-testid="stDownloadButton"] button span,
[data-testid="stDownloadButton"] button [data-testid="stMarkdownContainer"],
[data-testid="stDownloadButton"] button [data-testid="stMarkdownContainer"] * {
    color: #D00000 !important;
    -webkit-text-fill-color: #D00000 !important;
    font-weight: 700 !important;
}

[data-testid="stDownloadButton"] button {
    background: #FFFFFF !important;
    border: 2px solid #D00000 !important;
    border-radius: 9px !important;
    min-height: 44px !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: #FFE5E5 !important;
    border-color: #A30000 !important;
}

[data-testid="stDownloadButton"] button svg {
    fill: #D00000 !important;
    color: #D00000 !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border-color: #D00000 !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] *,
div[data-testid="stSelectbox"] div[data-baseweb="select"] input,
div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
div[data-testid="stSelectbox"] div[data-baseweb="select"] div {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}

div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {
    color: #000000 !important;
    fill: #000000 !important;
}

div[data-baseweb="popover"] li,
div[data-baseweb="popover"] li *,
div[data-baseweb="popover"] [role="option"],
div[data-baseweb="popover"] [role="option"] * {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    font-weight: 600 !important;
}

div[data-baseweb="popover"] [aria-selected="true"],
div[data-baseweb="popover"] [aria-selected="true"] * {
    background-color: #E5E7EB !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

</style>
""", unsafe_allow_html=True)


def metric_card(label, value, caption):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def agent_card(icon, title, description, status="BUILT"):
    st.markdown(
        f"""
        <div class="agent-card">
            <div class="agent-icon">{icon}</div>
            <div class="agent-title">{title}</div>
            <div class="agent-description">{description}</div>
            <br>
            <div class="status-good">● {status}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def load_agent(module_path):
    return importlib.import_module(module_path)


def find_agent_function(module, preferred_names):
    for name in preferred_names:
        candidate = getattr(module, name, None)

        if callable(candidate):
            return candidate

    for name, candidate in inspect.getmembers(
        module, inspect.isfunction
    ):
        if (
            candidate.__module__ == module.__name__
            and any(
                word in name.lower()
                for word in ("investigate", "run_")
            )
        ):
            return candidate

    raise AttributeError(
        f"No compatible investigation function found in "
        f"{module.__name__}."
    )


def extract_message_content(content):
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):
                text_value = item.get("text")

                if text_value:
                    text_parts.append(str(text_value))

        return "\n".join(text_parts).strip()

    if content is not None:
        return str(content)

    return ""


def extract_final_ai_report(result):
    if isinstance(result, dict):
        messages = result.get("messages", [])

    else:
        messages = getattr(result, "messages", [])

    if not messages:
        return None

    for message in reversed(messages):
        if isinstance(message, dict):
            message_type = message.get("type")
            content = message.get("content")
            tool_calls = message.get("tool_calls", [])

        else:
            message_type = getattr(message, "type", None)
            content = getattr(message, "content", None)
            tool_calls = getattr(message, "tool_calls", [])

        if message_type != "ai":
            continue

        if tool_calls:
            continue

        report = extract_message_content(content)

        if report:
            return report

    return None


def run_agent(module_path, preferred_names, *args):
    module = load_agent(module_path)
    function = find_agent_function(module, preferred_names)

    output = io.StringIO()

    with contextlib.redirect_stdout(output):
        result = function(*args)

    printed_output = output.getvalue()

    if isinstance(result, str) and result.strip():
        return result.strip()

    if isinstance(result, dict) and "messages" in result:
        report = extract_final_ai_report(result)

        if report:
            return report

        if printed_output.strip():
            return printed_output.strip()

        return (
            "The agent executed, but no final AI investigation "
            "report was returned."
        )

    if isinstance(result, dict):
        return json.dumps(result, indent=2, default=str)

    if result is not None:
        report = extract_final_ai_report(result)

        if report:
            return report

        if printed_output.strip():
            return printed_output.strip()

        return str(result)

    if printed_output.strip():
        return printed_output.strip()

    return "The agent completed without returning a report."


if "latest_reports" not in st.session_state:
    st.session_state.latest_reports = {}

if "investigation_history" not in st.session_state:
    st.session_state.investigation_history = []

if "ask_insureai_result" not in st.session_state:
    st.session_state.ask_insureai_result = None

if "ask_insureai_question" not in st.session_state:
    st.session_state.ask_insureai_question = ""


def save_report(report, report_type):
    st.session_state.latest_reports[report_type] = report

    st.session_state.investigation_history.insert(
        0,
        {
            "type": report_type,
            "report": report
        }
    )


def update_ask_insureai_question():
    selected = st.session_state.ask_insureai_example_question

    if selected == "Write my own question":
        st.session_state.ask_insureai_question = ""
    else:
        st.session_state.ask_insureai_question = selected


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            Thobani-<span class="brand-accent">INSUREAI</span>
        </div>
        <div class="brand-caption">
            INSURANCE INTELLIGENCE
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    st.caption("AGENTIC AI • DATA ENGINEERING")
    st.divider()

    page = st.radio(
        "PLATFORM NAVIGATION",
        [
            "Executive Overview",
            "Claim Investigation",
            "Fraud Intelligence",
            "Data Quality Intelligence",
            "Ask INSUREAI",
            "Investigation Reports",
            "Technical Architecture"
        ],
        label_visibility="visible"
    )

    st.divider()

    st.markdown("### PLATFORM COMPONENTS")

    st.markdown(
        '<span class="status-good">● DuckDB integration</span>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<span class="status-good">● LangGraph orchestration</span>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<span class="status-good">● Groq LLM integration</span>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<span class="status-good">● Streamlit interface</span>',
        unsafe_allow_html=True
    )

    st.divider()

    st.caption("Independent portfolio project")
    st.caption("2026 | Built by Thobani Zondi")


if page == "Executive Overview":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">
                AGENTIC AI • DATA ENGINEERING • INSURANCE
            </div>
            <div class="hero-title">
                Thobani-INSUREAI
            </div>
            <div class="hero-text">
                Insurance Intelligence Platform combining
                SQL-driven data validation, claim investigation,
                fraud-risk screening and AI-powered analysis.
                Designed around evidence, explainability and
                responsible human decision-making.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## Platform Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("AI AGENTS", "04", "Investigation capabilities")

    with c2:
        metric_card("RECORDS PROFILED", "10,000", "Validated database profile")

    with c3:
        metric_card("QUALITY FINDINGS", "2,797", "Latest validated engine run")

    with c4:
        metric_card(
            "INVESTIGATIONS",
            str(len(st.session_state.investigation_history)),
            "Current application session"
        )

    st.write("")

    st.markdown("## Intelligent Investigation Agents")

    a1, a2, a3, a4 = st.columns(4)

    with a1:
        agent_card(
            "🔍",
            "Claim Investigation",
            "Investigates individual claims using claim, policy and customer evidence."
        )

    with a2:
        agent_card(
            "🛡️",
            "Fraud Intelligence",
            "Identifies configured fraud-risk indicators and patterns requiring investigation."
        )

    with a3:
        agent_card(
            "📊",
            "Data Quality Intelligence",
            "Detects completeness, validity, consistency and referential integrity issues."
        )

    with a4:
        agent_card(
            "💬",
            "Ask INSUREAI",
            "Answers natural-language questions using read-only SQL queries against DuckDB."
        )

    st.write("")

    st.markdown("## Latest Validated Data Quality Results")

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown(
            '<div class="section-card">',
            unsafe_allow_html=True
        )

        st.markdown("**DATABASE PROFILE**")
        st.write("Database: `insureai.duckdb`")

        st.progress(
            0.2797,
            text="27.97% of scanned records flagged by the consistency rule"
        )

        st.write("Claims: 5,000")
        st.write("Policies: 3,000")
        st.write("Customers: 2,000")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="section-card">',
            unsafe_allow_html=True
        )

        st.markdown("**DETECTED CONSISTENCY ISSUE**")

        st.metric(
            "Claims outside recorded policy period",
            "2,797"
        )

        st.write("Distinct affected claims: 2,797")
        st.write("Distinct affected policies: 1,712")

        st.caption(
            "Validated against DuckDB. Findings require business verification."
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        "GOVERNANCE: Investigation engines perform read-only analysis. "
        "The platform does not automatically approve, reject or correct "
        "insurance claims or database records."
    )


elif page == "Claim Investigation":

    st.title("🔍 Claim Investigation")

    st.write(
        "Investigate an individual insurance claim using "
        "the INSUREAI Claim Investigation Agent."
    )

    claim_id = st.number_input(
        "Enter Claim ID",
        min_value=1,
        value=20001,
        step=1
    )

    if st.button("Run Claim Investigation", use_container_width=True):
        with st.spinner("Investigating claim and analysing evidence..."):
            try:
                report = run_agent(
                    "src.agents.insurance_investigator",
                    [
                        "run_claim_investigation",
                        "run_insurance_investigation",
                        "run_investigation",
                        "investigate_claim"
                    ],
                    int(claim_id)
                )

                save_report(
                    report,
                    f"Claim Investigation - {claim_id}"
                )

                st.success("Claim investigation completed successfully.")

            except Exception as error:
                st.error(f"Claim investigation failed: {error}")

                st.info(
                    "If the agent uses a different entry-point function "
                    "or argument signature, inspect its definition before "
                    "changing the integration."
                )

    report_key = f"Claim Investigation - {int(claim_id)}"

    if report_key in st.session_state.latest_reports:
        st.divider()
        st.subheader("Claim Investigation Report")

        report = st.session_state.latest_reports[report_key]

        st.markdown(report)

        st.download_button(
            "Download Claim Report",
            data=report,
            file_name=f"insureai_claim_{int(claim_id)}.md",
            mime="text/markdown"
        )


elif page == "Fraud Intelligence":

    st.title("🛡️ Fraud Intelligence")

    st.write(
        "Screen individual claims for configured fraud-risk indicators. "
        "Screening results are not proof of fraud."
    )

    claim_id = st.number_input(
        "Claim ID for fraud screening",
        min_value=1,
        value=21319,
        step=1,
        key="fraud_claim_id"
    )

    if st.button("Run Fraud Screening", use_container_width=True):
        with st.spinner(
            "Running fraud detection engine and AI investigation..."
        ):
            try:
                report = run_agent(
                    "src.agents.fraud_detection_agent",
                    ["run_fraud_investigation"],
                    int(claim_id)
                )

                save_report(
                    report,
                    f"Fraud Intelligence - {claim_id}"
                )

                st.success("Fraud screening completed successfully.")

            except Exception as error:
                st.error(f"Fraud investigation failed: {error}")

    report_key = f"Fraud Intelligence - {int(claim_id)}"

    if report_key in st.session_state.latest_reports:
        st.divider()
        st.subheader("Fraud Intelligence Report")

        report = st.session_state.latest_reports[report_key]

        st.markdown(report)

        st.download_button(
            "Download Fraud Report",
            data=report,
            file_name=f"insureai_fraud_{int(claim_id)}.md",
            mime="text/markdown"
        )

    st.warning(
        "A flagged indicator requires appropriate investigation. "
        "The platform does not independently establish fraud or "
        "automatically hold, reject or reverse a claim."
    )


elif page == "Data Quality Intelligence":

    st.title("📊 Data Quality Intelligence")

    st.write(
        "Run database-wide data quality checks and receive "
        "an AI-generated explanation of detected anomalies."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("CLAIMS", "5,000")

    with c2:
        st.metric("POLICIES", "3,000")

    with c3:
        st.metric("CUSTOMERS", "2,000")

    st.divider()

    if st.button("Run Data Quality Investigation", use_container_width=True):
        with st.spinner(
            "Running SQL checks and generating intelligence report..."
        ):
            try:
                report = run_agent(
                    "src.agents.data_quality_agent",
                    ["run_data_quality_investigation"]
                )

                save_report(report, "Data Quality Intelligence")

                st.success(
                    "Data quality investigation completed successfully."
                )

            except Exception as error:
                st.error(f"Data quality investigation failed: {error}")

    report = st.session_state.latest_reports.get(
        "Data Quality Intelligence"
    )

    if report:
        st.divider()
        st.subheader("Data Quality Investigation Report")

        st.markdown(report)

        st.download_button(
            "Download Data Quality Report",
            data=report,
            file_name="insureai_data_quality_report.md",
            mime="text/markdown"
        )

    st.info(
        "The SQL Data Quality Engine is deterministic and read-only. "
        "The AI agent explains findings and recommends investigation; "
        "it does not change source records."
    )


elif page == "Ask INSUREAI":

    st.title("💬 Ask INSUREAI")

    st.write(
        "Ask questions about the insurance database using natural "
        "language. INSUREAI generates SQL, executes a read-only "
        "query against DuckDB and explains the returned results."
    )

    st.markdown(
        """
        <div class="section-card">
            <div class="agent-title">INSURANCE DATA ASSISTANT</div>
            <div class="agent-description">
                Ask questions about claims, customers, policies,
                claim amounts, provinces, risk indicators and
                insurance portfolio performance.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### Example questions")

    example_questions = [
        "How many claims are in the database?",
        "How many claims were submitted in 2025?",
        "Which provinces have the highest total claim amounts?",
        "Show the top 10 customers by total claim amount.",
        "What is the average claim amount by insurance type?",
        "Which policies have expired?",
        "Which customers have submitted multiple claims?",
        "What is the overall claim rejection rate?"
    ]

    selected_question = st.selectbox(
        "Choose an example question",
        ["Write my own question"] + example_questions,
        key="ask_insureai_example_question",
        on_change=update_ask_insureai_question
    )

    question = st.text_area(
        "Ask a question about your insurance data",
        placeholder="For example: Which provinces have the highest total claim amounts?",
        height=110,
        key="ask_insureai_question"
    )

    if st.button("Ask INSUREAI", use_container_width=True):
        if not question.strip():
            st.warning("Please enter a question before continuing.")

        else:
            with st.spinner(
                "Analysing your question, generating SQL and querying DuckDB..."
            ):
                try:
                    from src.agents.ask_insureai_agent import ask_insureai

                    result = ask_insureai(question.strip())

                    st.session_state.ask_insureai_result = result

                    if result.get("success"):
                        st.success(
                            "INSUREAI completed the database analysis."
                        )

                        report = (
                            f"# Ask INSUREAI\n\n"
                            f"**Question:** {result['question']}\n\n"
                            f"{result['answer']}\n\n"
                            f"**Generated SQL:**\n\n"
                            f"```sql\n{result['sql']}\n```"
                        )

                        save_report(report, "Ask INSUREAI")

                    else:
                        st.error(
                            result.get(
                                "answer",
                                "The database question could not be completed."
                            )
                        )

                except Exception as error:
                    st.error(f"Ask INSUREAI failed: {error}")

    result = st.session_state.ask_insureai_result

    if result:
        st.divider()
        st.markdown("## Analysis Results")

        st.markdown("**Your question**")
        st.write(result.get("question", ""))

        st.markdown("**INSUREAI response**")
        st.markdown(
            result.get("answer", "No explanation was returned.")
        )

        if result.get("success"):
            dataframe = result.get("data")

            metric1, metric2 = st.columns(2)

            with metric1:
                st.metric(
                    "ROWS RETURNED",
                    result.get("row_count", 0)
                )

            with metric2:
                st.metric(
                    "RESULT STATUS",
                    "Truncated" if result.get("truncated") else "Complete"
                )

            if dataframe is not None:

                numeric_columns = dataframe.select_dtypes(
                    include="number"
                ).columns.tolist()

                date_columns = [
                    column
                    for column in dataframe.columns
                    if any(
                        term in str(column).lower()
                        for term in ["date", "month", "year"]
                    )
                ]

                category_columns = [
                    column
                    for column in dataframe.columns
                    if column not in numeric_columns
                    or column in date_columns
                ]

                chart_values = [
                    column
                    for column in numeric_columns
                    if column not in date_columns
                ]

                if (
                    len(dataframe) > 1
                    and category_columns
                    and chart_values
                ):
                    st.markdown("### Interactive Visualization")

                    st.caption(
                        "Explore your query results using interactive charts. "
                        "Select a chart type, category and measurement."
                    )

                    chart_options = ["Bar", "Line", "Pie"]

                    default_chart = (
                        "Line" if date_columns else "Bar"
                    )

                    column_signature = "_".join(
                        str(column) for column in dataframe.columns
                    )

                    chart_col1, chart_col2, chart_col3 = st.columns(3)

                    with chart_col1:
                        chart_type = st.selectbox(
                            "Chart Type",
                            chart_options,
                            index=chart_options.index(default_chart),
                            key="ask_insureai_chart_type"
                        )

                    with chart_col2:
                        x_axis = st.selectbox(
                            "Category / X-axis",
                            category_columns,
                            key=f"ask_insureai_x_axis_{column_signature}"
                        )

                    with chart_col3:
                        y_axis = st.selectbox(
                            "Measure / Y-axis",
                            chart_values,
                            key=f"ask_insureai_y_axis_{column_signature}"
                        )

                    chart_data = dataframe[
                        [x_axis, y_axis]
                    ].dropna().copy()

                    if chart_type in ["Bar", "Pie"]:
                        chart_data = (
                            chart_data.groupby(
                                x_axis,
                                as_index=False
                            )[y_axis]
                            .sum()
                            .sort_values(
                                y_axis,
                                ascending=False
                            )
                            .head(25)
                        )

                    if chart_type == "Bar":

                        figure = px.bar(
                            chart_data,
                            x=x_axis,
                            y=y_axis,
                            title=f"{y_axis} by {x_axis}",
                            text_auto=".2s"
                        )

                    elif chart_type == "Line":

                        chart_data = (
                            chart_data.groupby(
                                x_axis,
                                as_index=False
                            )[y_axis]
                            .sum()
                            .sort_values(x_axis)
                        )

                        figure = px.line(
                            chart_data,
                            x=x_axis,
                            y=y_axis,
                            title=f"{y_axis} over {x_axis}",
                            markers=True
                        )

                    else:

                        figure = px.pie(
                            chart_data.head(10),
                            names=x_axis,
                            values=y_axis,
                            title=f"{y_axis} distribution by {x_axis}",
                            hole=0.35
                        )

                    figure.update_layout(
                        template="plotly_dark",
                        height=450,
                        margin=dict(
                            l=20,
                            r=20,
                            t=60,
                            b=20
                        ),
                        legend_title_text=x_axis
                    )

                    st.plotly_chart(
                        figure,
                        use_container_width=True
                    )

                else:

                    st.caption(
                        "Interactive charts are available when the query "
                        "returns multiple rows, a category column and "
                        "a numerical measurement."
                    )

                st.markdown("### Query Results")

                st.dataframe(
                    dataframe,
                    use_container_width=True,
                    hide_index=True
                )

                csv_data = dataframe.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    "Download Query Results",
                    data=csv_data,
                    file_name="insureai_query_results.csv",
                    mime="text/csv"
                )

            if result.get("truncated"):
                st.warning(
                    "The result set exceeded the maximum display limit. "
                    "Only the first 500 rows are displayed."
                )

            with st.expander("View Generated SQL"):
                st.code(
                    result.get("sql", ""),
                    language="sql"
                )

        else:
            with st.expander("View Generated SQL"):
                st.code(
                    result.get("sql", ""),
                    language="sql"
                )

    st.divider()

    st.info(
        "Ask INSUREAI uses read-only DuckDB access and restricted "
        "SQL execution. Results are based on available database "
        "records. AI-generated explanations should be reviewed "
        "before business decisions are made."
    )


elif page == "Investigation Reports":

    st.title("📁 Investigation Reports")

    st.write(
        "Review and download investigation reports generated "
        "during the current application session."
    )

    history = st.session_state.investigation_history

    if not history:
        st.info(
            "No investigations have been run in this session yet. "
            "Use one of the investigation workspaces to generate "
            "your first report."
        )

    else:
        st.metric("COMPLETED REPORTS", len(history))

        for index, item in enumerate(history):
            with st.expander(
                f"{index + 1}. {item['type']}",
                expanded=(index == 0)
            ):
                st.markdown(item["report"])

                st.download_button(
                    "Download Report",
                    data=item["report"],
                    file_name=f"insureai_report_{index + 1}.md",
                    mime="text/markdown",
                    key=f"download_report_{index}"
                )


elif page == "Technical Architecture":

    st.title("⚙️ Technical Architecture")

    st.write(
        "INSUREAI combines deterministic data engineering "
        "with agentic AI orchestration."
    )

    st.markdown("## System Architecture")

    st.markdown("""
    ```mermaid
    flowchart TD
        A[Streamlit Dashboard]

        A --> B[Claim Investigation Agent]
        A --> C[Fraud Detection Agent]
        A --> D[Data Quality Agent]
        A --> E[Ask INSUREAI Agent]

        B --> F[Claim Investigation Tools]
        C --> G[Fraud Detection Engine]
        D --> H[Data Quality Engine]
        E --> I[SQL Generation and Validation]

        F --> J[(DuckDB)]
        G --> J
        H --> J
        I --> J

        B --> K[LangGraph + Groq]
        C --> K
        D --> K
        E --> K

        K --> L[Investigation Reports and Data Answers]
        L --> A
    ```
    """)

    st.markdown("## Technology Stack")

    technologies = {
        "Programming": "Python",
        "Database": "DuckDB",
        "AI orchestration": "LangGraph",
        "Language model": "Groq - GPT-OSS 120B",
        "Agent framework": "LangChain",
        "SQL validation": "SQLGlot",
        "Dashboard": "Streamlit",
        "Data access": "DuckDB and Python database connectivity",
        "Version control": "Git and GitHub"
    }

    for category, technology in technologies.items():
        st.markdown(f"**{category}:** {technology}")

    st.markdown("## Engineering Principles")

    st.markdown("""
    - Deterministic SQL-based validation.
    - Evidence-based LLM analysis.
    - Restricted read-only SQL execution.
    - Separation of fraud indicators and data quality findings.
    - Human review for consequential insurance decisions.
    - Independent and modular agent architecture.
    - AI-generated explanations grounded in database query results.
    """)

    st.markdown("## Project Scope")

    st.info(
        "Thobani-INSUREAI is an independent portfolio project "
        "using an insurance analytics dataset. It demonstrates "
        "agentic investigation workflows and is not a production "
        "insurance claims system."
    )


st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        padding:15px 5px;
        color:#91A6BC;
        font-size:12px;
        line-height:2;
    ">
        <span style="color:#FFFFFF;font-weight:800;">
            Thobani-<span style="color:#35C6B0;">INSUREAI</span>
        </span>
        <br>
        Insurance Intelligence | Agentic AI & Data Engineering
        <br>
        Built with Python, DuckDB, LangGraph, Groq and Streamlit
        <br>
        <span style="color:#647C94;">
            Independent Portfolio Project | 2026
        </span>
    </div>
    """,
    unsafe_allow_html=True
)
