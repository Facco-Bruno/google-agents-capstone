import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Add src folder to path if running directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google.antigravity import Agent, LocalAgentConfig, types
from google.antigravity.hooks import hooks, policy
import tools

# Load environment variables (.env file)
load_dotenv()

# Configure standard Python logging for the SDK
logging.getLogger("google.antigravity").setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Define hooks for rate limiting (due to 5 requests/minute free tier limit)
@hooks.pre_tool_call_decide
async def pre_tool_delay(data: types.ToolCall) -> types.HookResult:
    print(f"\n[Rate Limiter] Pausing 15s before executing tool '{data.name}'...")
    await asyncio.sleep(15)
    return types.HookResult(allow=True)

@hooks.post_tool_call
async def post_tool_delay(data):
    print("[Rate Limiter] Pausing 15s after tool execution...")
    await asyncio.sleep(15)

async def run_analysis_agent():
    csv_path = 'data/sales_data.csv'
    report_output_path = 'outputs/executive_report.md'
    
    print("Starting Hybrid Data Analysis Pipeline...")
    
    # Verify GEMINI_API_KEY
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in environment or .env file.")
        return

    # 1. LOCAL STAGE (Pure Python): Data Exploration and Statistical Analysis
    print("\n1. Running local statistical analyses...")
    summary = tools.get_dataset_summary(csv_path)
    analysis = tools.run_business_analysis(csv_path)
    
    # 2. LOCAL STAGE (Pure Python): Headless Visualization Generation
    print("\n2. Generating statistical charts locally (Headless)...")
    charts = [
        ('sales_trend', 'sales_trend.png'),
        ('category_sales', 'category_sales.png'),
        ('region_distribution', 'region_distribution.png'),
        ('satisfaction_vs_sales', 'satisfaction_vs_sales.png')
    ]
    for chart_type, filename in charts:
        result = tools.generate_and_save_chart(csv_path, chart_type, filename)
        print(f"   - {result}")

    # 3. AGENT STAGE (Google Antigravity SDK): Interpretation and Executive Report Generation
    print("\n3. Initializing Google Antigravity SDK Agent for Insights generation...")
    
    # Configure the agent
    config = LocalAgentConfig(
        capabilities=types.CapabilitiesConfig(enabled_tools=[]),
        policies=[policy.deny_all()],
        hooks=[pre_tool_delay, post_tool_delay],
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

    # Prompt including pre-computed statistics
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
        print("   - Sending consolidated data to the model...")
        response = await agent.chat(prompt)
        
        print("\n--- Agent's Generated Report ---")
        report_content = ""
        async for chunk in response:
            print(chunk, end="", flush=True)
            report_content += chunk
        print("\n-------------------------------------")
        
        # 4. Save the final report locally
        print(f"\n4. Saving final executive report...")
        save_result = tools.save_report_file(report_content, report_output_path)
        print(f"   - {save_result}")
        
        # Log token usage for observability (Day 4 concept)
        try:
            usage = agent.conversation.total_usage
            print("\n[Observability] Token Usage Metrics:")
            print(f"- Prompt Tokens: {usage.prompt_token_count}")
            print(f"- Response Tokens (Candidates): {usage.candidates_token_count}")
            print(f"- Reasoning Tokens (Thoughts): {usage.thoughts_token_count}")
            print(f"- Total Tokens: {usage.total_token_count}")
        except Exception as e:
            print(f"\nCould not retrieve token usage: {e}")

if __name__ == '__main__':
    asyncio.run(run_analysis_agent())
