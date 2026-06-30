import streamlit as st
import pandas as pd
import os
import asyncio
import sys
from dotenv import load_dotenv

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import tools
from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.hooks import policy

# Page Config
st.set_page_config(
    page_title="Aegis Analytics | AI BI Agent Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load env file to get default API key
load_dotenv()
default_key = os.getenv("GEMINI_API_KEY", "")

# Custom CSS for Premium Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Font style */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Title and header */
    .main-title {
        font-size: 38px;
        font-weight: 700;
        background: linear-gradient(135deg, #FF8C00 0%, #FF2E93 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    .subtitle {
        font-size: 16px;
        color: #7f8c8d;
        margin-bottom: 25px;
    }
    
    /* Custom KPI Cards */
    .kpi-container {
        display: flex;
        gap: 15px;
        margin-bottom: 25px;
    }
    
    .kpi-card {
        flex: 1;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: rgba(255, 140, 0, 0.5);
    }
    
    .kpi-label {
        font-size: 12px;
        color: #bdc3c7;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 8px;
    }
    
    .kpi-val {
        font-size: 26px;
        font-weight: 700;
        background: linear-gradient(135deg, #f39c12, #d35400);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# App Title
st.markdown("<div class='main-title'>Aegis Analytics</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Autonomous Business Intelligence Agent & Executive Report Generator</div>", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.markdown("### Agent Configurations")

# Gemini API Key configuration
api_key = st.sidebar.text_input(
    "Gemini API Key", 
    value=default_key, 
    type="password",
    help="Add your Google AI Studio API Key. If configured in .env, it will appear here automatically."
)

if not api_key:
    st.sidebar.warning("Enter your Gemini API Key to execute the Agent analysis.")

# Helper function to auto-detect columns
def auto_detect_col(columns, keywords, default_idx=0):
    for idx, col in enumerate(columns):
        if any(kw in col.lower() for kw in keywords):
            return idx
    return default_idx

# Dataset selection
st.sidebar.markdown("### Dataset")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

# Define CSV Path & Mapping
csv_path = 'data/sales_data.csv'
mapping_needed = False
mapping = {}

if uploaded_file is not None:
    # Save uploaded file
    os.makedirs('data', exist_ok=True)
    raw_csv_path = os.path.join('data', 'raw_' + uploaded_file.name)
    with open(raw_csv_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    # Read headers to perform mapping
    try:
        df_raw = pd.read_csv(raw_csv_path, nrows=2)
        cols = list(df_raw.columns)
        mapping_needed = True
        
        st.sidebar.markdown("### Column Mapping")
        st.sidebar.caption("Map your CSV columns to the required analysis fields:")
        
        # Auto-detect indices
        idx_sales = auto_detect_col(cols, ['sale', 'revenue', 'faturamento', 'valor', 'total'])
        idx_units = auto_detect_col(cols, ['unit', 'qty', 'quantity', 'quantidade', 'qtd'])
        idx_satisfaction = auto_detect_col(cols, ['satisfaction', 'satisfacao', 'rating', 'nota', 'score'])
        idx_category = auto_detect_col(cols, ['category', 'categoria', 'type', 'tipo', 'group'])
        idx_region = auto_detect_col(cols, ['region', 'regiao', 'state', 'estado', 'city', 'cidade'])
        idx_date = auto_detect_col(cols, ['date', 'data', 'day', 'dia', 'time'])
        idx_product = auto_detect_col(cols, ['product', 'produto', 'item', 'name', 'nome'])
        idx_price = auto_detect_col(cols, ['price', 'preco', 'valor_unitario', 'unit_price'])
        
        # Dropdowns in sidebar
        sales_col = st.sidebar.selectbox("Sales (Revenue)", cols, index=idx_sales)
        units_col = st.sidebar.selectbox("Units Sold", cols, index=idx_units)
        satisfaction_col = st.sidebar.selectbox("Satisfaction Score", cols, index=idx_satisfaction)
        category_col = st.sidebar.selectbox("Product Category", cols, index=idx_category)
        region_col = st.sidebar.selectbox("Region", cols, index=idx_region)
        date_col = st.sidebar.selectbox("Date", cols, index=idx_date)
        product_col = st.sidebar.selectbox("Product Name", cols, index=idx_product)
        price_col = st.sidebar.selectbox("Unit Price", cols, index=idx_price)
        
        # Create standard dataframe
        df_full = pd.read_csv(raw_csv_path)
        rename_dict = {
            sales_col: 'Sales',
            units_col: 'Units',
            satisfaction_col: 'Satisfaction',
            category_col: 'Category',
            region_col: 'Region',
            date_col: 'Date',
            product_col: 'Product',
            price_col: 'Price'
        }
        df_mapped = df_full.rename(columns=rename_dict)
        
        # Save mapped version
        csv_path = os.path.join('data', 'mapped_' + uploaded_file.name)
        df_mapped.to_csv(csv_path, index=False)
        st.sidebar.success("Columns mapped successfully!")
        
    except Exception as ex:
        st.sidebar.error(f"Error reading CSV structure: {ex}")
else:
    # Ensure default synthetic dataset is loaded/available
    if not os.path.exists(csv_path):
        st.sidebar.info("Generating sample dataset...")
        import subprocess
        subprocess.run([sys.executable, 'src/generate_sample_data.py'])

# Executer Button
run_button = st.sidebar.button("Run Data Analysis", use_container_width=True, disabled=not api_key)

# App Tabs
tab_dashboard, tab_agent_insights = st.tabs(["Dashboard and Metrics", "Agent Report and Insights"])

# Load data to show dashboard metrics instantly
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    
    # Calculate basic metrics for display
    total_sales = df['Sales'].sum()
    total_units = df['Units'].sum()
    avg_sat = df['Satisfaction'].mean()
    
    with tab_dashboard:
        # Display KPI cards
        col_s, col_u, col_sat = st.columns(3)
        with col_s:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>Total Sales Revenue</div>
                <div class='kpi-val'>${total_sales:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_u:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>Total Units Sold</div>
                <div class='kpi-val'>{total_units:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_sat:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-label'>Average Satisfaction</div>
                <div class='kpi-val'>{avg_sat:.2f} / 5.0</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("---")
        
        # Display charts grid (if they exist)
        chart_paths = {
            "sales_trend": "outputs/charts/sales_trend.png",
            "category_sales": "outputs/charts/category_sales.png",
            "region_distribution": "outputs/charts/region_distribution.png",
            "satisfaction_vs_sales": "outputs/charts/satisfaction_vs_sales.png"
        }
        
        # Check if charts are present
        charts_ready = all(os.path.exists(path) for path in chart_paths.values())
        
        if charts_ready:
            st.markdown("### Statistical Visualizations")
            c1, c2 = st.columns(2)
            with c1:
                st.image(chart_paths["sales_trend"], caption="Sales Trend", use_container_width=True)
                st.image(chart_paths["region_distribution"], caption="Region Distribution", use_column_width=True)
            with c2:
                st.image(chart_paths["category_sales"], caption="Sales by Category", use_container_width=True)
                st.image(chart_paths["satisfaction_vs_sales"], caption="Satisfaction vs Sales", use_column_width=True)
        else:
            st.info("Click the Run Data Analysis button in the sidebar to generate charts and visualizations for the dataset.")

# Async generator for the agent loop
async def run_agent_pipeline(csv_path, key):
    # Set key in environment so SDK can pick it up
    os.environ["GEMINI_API_KEY"] = key
    
    # 1. Local computations
    summary = tools.get_dataset_summary(csv_path)
    analysis = tools.run_business_analysis(csv_path)
    
    # 2. Local chart generation
    charts = [
        ('sales_trend', 'sales_trend.png'),
        ('category_sales', 'category_sales.png'),
        ('region_distribution', 'region_distribution.png'),
        ('satisfaction_vs_sales', 'satisfaction_vs_sales.png')
    ]
    for chart_type, filename in charts:
        tools.generate_and_save_chart(csv_path, chart_type, filename)
        
    # 3. Agent execution (Single-turn prompt to avoid quota limitations)
    config = LocalAgentConfig(
        api_key=key,
        policies=[policy.deny_all()],
        system_instructions=(
            "You are Aegis Analytics, a senior business intelligence agent. "
            "Your task is to write a highly detailed, professional, and visually stunning "
            "business intelligence report in English based on the pre-computed metrics and KPIs provided.\n\n"
            "Guidelines:\n"
            "- Write a summary for high-level executives in English.\n"
            "- Highlight key insights (e.g. which categories dominate, satisfaction issues, or regional trends).\n"
            "- Structure your report with clean Markdown tables.\n"
            "- Include references to the generated charts. Ensure they are written exactly as markdown images: "
            "  `![Sales Trend](outputs/charts/sales_trend.png)`, `![Sales by Category](outputs/charts/category_sales.png)`, "
            "  `![Regional Distribution](outputs/charts/region_distribution.png)`, and `![Satisfaction](outputs/charts/satisfaction_vs_sales.png)`.\n"
            "- Offer 3 actionable, strategic business recommendations based on the findings."
        )
    )
    
    prompt = f"""
Please analyze the following raw data consolidation and generate a complete and detailed Executive BI Report in English.

---

{summary}

---

{analysis}

---

Remember to embed the 4 corresponding charts saved in the 'charts/' folder using markdown image references.
The final report should be written in Markdown.
"""

    async with Agent(config) as agent:
        response = await agent.chat(prompt)
        
        report_content = ""
        async for chunk in response:
            report_content += chunk
            yield report_content, None
            
        usage = agent.conversation.total_usage
        yield report_content, usage

# When button is clicked
if run_button:
    with tab_agent_insights:
        st.markdown("### Agent Report Generation")
        
        # Show progress
        status_text = st.empty()
        status_text.write("Executing local KPI calculations and generating visualizations...")
        
        report_placeholder = st.empty()
        
        # Run async event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get generator
            pipeline = run_agent_pipeline(csv_path, api_key)
            
            # Consume generator to stream chunks
            while True:
                try:
                    report_content, usage = loop.run_until_complete(pipeline.__anext__())
                    status_text.write("Agent analyzing data and generating insights in real-time...")
                    report_placeholder.markdown(report_content)
                    
                    if usage is not None:
                        # Success and finished
                        status_text.success("Executive BI Report successfully generated!")
                        
                        # Save report content locally
                        tools.save_report_file(report_content, 'outputs/executive_report.md')
                        
                        # Show token usage metrics (Day 4 Observability)
                        st.markdown("---")
                        st.markdown("#### Observability Metrics (Token Usage)")
                        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
                        col_t1.metric("Prompt Tokens", f"{usage.prompt_token_count:,}")
                        col_t2.metric("Response Tokens", f"{usage.candidates_token_count:,}")
                        col_t3.metric("Reasoning Tokens", f"{usage.thoughts_token_count:,}")
                        col_t4.metric("Total Tokens", f"{usage.total_token_count:,}")
                        
                        # Refresh page to show charts in dashboard tab
                        st.sidebar.info("Reload the page to update the charts on the left Dashboard tab.")
                except StopAsyncIteration:
                    break
                except Exception as ex:
                    status_text.error(f"Error during agent execution: {ex}")
                    break
        finally:
            loop.close()

# Show pre-existing report in tab if it exists
else:
    with tab_agent_insights:
        report_path = 'outputs/executive_report.md'
        if os.path.exists(report_path):
            st.markdown("### Previously Saved Executive Report")
            with open(report_path, 'r', encoding='utf-8') as f:
                st.markdown(f.read())
        else:
            st.info("Click the Run Data Analysis button in the sidebar to start the intelligence agent and generate the executive report.")
