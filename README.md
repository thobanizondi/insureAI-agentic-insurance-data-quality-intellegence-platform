# INSUREAI - Agentic Insurance Data Quality and Intelligence Platform

An AI-powered insurance data quality and intelligence platform combining data engineering, agentic AI, claims investigation, fraud detection, and natural-language database querying.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
  - [Data Quality Management](#data-quality-management)
  - [Claims Investigation](#claims-investigation)
  - [Fraud Detection](#fraud-detection)
  - [Ask INSUREAI](#ask-insureai)
  - [Interactive Dashboard](#interactive-dashboard)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Clone the Repository](#clone-the-repository)
  - [Set Up the Environment](#set-up-the-environment)
  - [Install Dependencies](#install-dependencies)
  - [Configure Environment Variables](#configure-environment-variables)
  - [Configure the Database](#configure-the-database)
  - [Run the Application](#run-the-application)
- [Example Ask INSUREAI Questions](#example-ask-insureai-questions)
- [Security and Data Privacy](#security-and-data-privacy)
- [Disclaimer](#disclaimer)
- [Author](#author)

---

## Overview

INSUREAI is an agentic AI-powered insurance data quality and intelligence platform designed to improve the way insurance data is validated, investigated, and analysed.

The platform combines Python-based data engineering, DuckDB analytical storage, business rule validation, and large language models to identify data quality issues and support insurance claims investigation.

Through specialised AI agents and an interactive Streamlit dashboard, INSUREAI provides capabilities for data quality assessment, claims investigation, fraud detection, and natural-language querying of insurance datasets.

The project demonstrates how data engineering and agentic AI can work together to support more reliable insurance data and informed analytical decisions.

## Key Features

### Data Quality Management

- Validate insurance datasets against defined business rules.
- Identify missing, invalid, and inconsistent records.
- Perform data relationship and referential integrity checks.
- Reconcile source and destination record counts.
- Generate structured data quality findings and validation reports.

### Claims Investigation

- Investigate insurance claims against policy information.
- Identify claims outside policy coverage periods.
- Detect claims that exceed recorded policy coverage.
- Validate claim and policy relationships.
- Generate recommended investigation actions.

### Fraud Detection

- Analyse insurance claims for potential fraud indicators.
- Apply business rules to identify suspicious records.
- Highlight unusual claim information for further investigation.
- Support investigation through structured analytical findings.

### Ask INSUREAI

An AI-powered natural-language database assistant that allows users to interact with insurance data using everyday questions.

Capabilities include:

- Convert natural-language questions into SQL queries.
- Retrieve information from approved database tables.
- Inspect database metadata and table structures.
- Validate generated SQL queries before execution.
- Execute read-only analytical queries.
- Return query results with natural-language explanations.

### Interactive Dashboard

The Streamlit dashboard provides a central interface for accessing INSUREAI capabilities.

Users can:

- Explore data quality findings.
- Review insurance validation results.
- Access claims investigation functionality.
- Explore fraud detection results.
- Interact with the Ask INSUREAI assistant.
- View analytical information through dashboard visualisations.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Languages | Python, SQL |
| Database | DuckDB |
| Data Engineering | Python, SQL, Data Validation, Data Reconciliation |
| AI and LLM | Groq API, LangChain, LangGraph |
| SQL Validation | SQLGlot |
| Data Analysis | Pandas |
| Visualisation | Plotly |
| Dashboard | Streamlit |
| Environment Management | Conda, Python Virtual Environments |
| Version Control | Git, GitHub |

## Project Structure

```text
insureAI-agentic-insurance-data-quality-intelligence-platform/
│
├── dashboards/
│   └── app.py
│
├── data/
│   ├── migration_reconciliation.csv
│   └── relationship_validation.csv
│
├── reports/
│
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── ask_insureai_agent.py
│   │   ├── data_quality_agent.py
│   │   ├── fraud_detection_agent.py
│   │   └── insurance_investigator.py
│   │
│   ├── database/
│   │   ├── duckdb_connection.py
│   │   ├── inspect_invalid_date_keys.py
│   │   ├── inspect_relationship_columns.py
│   │   ├── validate_duckdb.py
│   │   └── validate_relationships.py
│   │
│   └── tools/
│       ├── ask_insureai_tools.py
│       ├── business_rule_checks.py
│       ├── claim_investigation_tools.py
│       ├── claim_policy_validator.py
│       ├── data_quality_engine.py
│       ├── fraud_detection_engine.py
│       ├── test_business_rule_checks.py
│       └── test_groq_connection.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

Before running INSUREAI, ensure you have:

- Python 3.10 or later.
- Conda or Python virtual environment.
- Git installed.
- A Groq API key.
- Access to the INSUREAI DuckDB database or the required database provisioning process.

### Clone the Repository

```bash
git clone https://github.com/thobanizondi/insureAI-agentic-insurance-data-quality-intellegence-platform.git

cd insureAI-agentic-insurance-data-quality-intellegence-platform
```

### Set Up the Environment

Create and activate a Conda environment:

```bash
conda create -n insureai python=3.11

conda activate insureai
```

### Install Dependencies

Install the project dependencies:

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Replace `your_groq_api_key` with your actual Groq API key.

Keep your API key private. Never commit your `.env` file to GitHub.

### Configure the Database

INSUREAI uses DuckDB for analytical data storage.

The expected local database location is:

```text
data/insureai.duckdb
```

The database file is excluded from Git version control.

Before running the application, ensure the database has been provisioned using the project's database setup and data-loading process.

### Run the Application

From the project root, execute:

```bash
streamlit run dashboards/app.py
```

Streamlit will start the application and provide a local browser address.

## Example Ask INSUREAI Questions

Users can interact with the database using natural-language questions such as:

- How many tables do we have?
- List all the tables in the database.
- How many claims are in the database?
- Identify claims that exceed their policy coverage.
- Are there claims linked to missing customers or policies?
- What data quality issues have been identified?
- Show me the available insurance data.

The results depend on the available database contents and the agent's supported query capabilities.

## Security and Data Privacy

INSUREAI incorporates security considerations into its design:

- API credentials are managed through environment variables.
- Local database files are excluded from Git version control.
- Sensitive claim-level reports are excluded from public repositories.
- Generated SQL queries are subject to validation.
- Ask INSUREAI is designed for read-only analytical database access.
- Database access is restricted to approved tables and permitted query operations.

## Disclaimer

INSUREAI is an independent data engineering and AI portfolio project intended for analytical and decision-support purposes.

Its outputs should support, not replace, professional insurance claims assessment, fraud investigation, regulatory compliance, or business decision-making.

## Author

**Thobani Antony Zondi**

- GitHub: [thobanizondi](https://github.com/thobanizondi)
- LinkedIn: [Thobani Zondi](https://linkedin.com/in/thobani-zondi)

*INSUREAI - Bringing Data Engineering and Agentic AI Together for Insurance Intelligence.*
