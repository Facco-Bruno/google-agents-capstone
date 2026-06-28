# Aegis Analytics: Autonomous Business Intelligence and Executive Report Generator

This repository contains the capstone project for the AI Agents Intensive Course, developed in partnership with Google and Kaggle.

---

## 1. Project Overview
Aegis Analytics is an autonomous agent built using the Google Antigravity SDK. It is designed to ingest raw business datasets (CSV format), execute automated data cleaning and profiling, perform statistical analysis, render high-resolution charts, and compile comprehensive executive summaries containing strategic business insights.

---

## 2. Core Technologies
- **Google Antigravity SDK:** Model session management and agent lifecycle orchestration.
- **Google Gemini 3.5 Flash:** Default language model for cognitive synthesis.
- **Pandas and Numpy:** Tabular data processing and statistical computations.
- **Matplotlib and Seaborn:** Data visualization and headless chart plotting.
- **Model Context Protocol (MCP):** Dynamic tool integration framework.

---

## 3. Directory Structure
- `data/`: Ingestion directory for raw and mapped CSV datasets.
- `outputs/`: Output directory containing PNG visualizations and the final markdown report.
- `src/`:
  - `tools.py`: Local Python tools for data profiling and chart generation.
  - `agent.py`: Agent configuration, prompt engineering, and SDK runtime logic.
  - `validate_setup.py`: Environment validation script.
  - `generate_sample_data.py`: Script for generating synthetic transaction records.
- `main.py`: Entry point for executing the CLI pipeline.
- `app.py`: Streamlit-based web dashboard with dynamic column mapping.
