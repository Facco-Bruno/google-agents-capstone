import os
import pandas as pd
import matplotlib
matplotlib.use('agg', force=True)
import matplotlib.pyplot as plt
import seaborn as sns

def get_dataset_summary(csv_path: str) -> str:
    """Loads a CSV dataset and returns a high-level summary of its columns, row count, and data types.

    Args:
        csv_path: The absolute or relative path to the CSV file.
    """
    if not os.path.exists(csv_path):
        return f"Error: File not found at {csv_path}"
    
    try:
        df = pd.read_csv(csv_path)
        summary = []
        summary.append(f"### Dataset Summary")
        summary.append(f"- **Total Rows**: {len(df)}")
        summary.append(f"- **Columns**: {', '.join(df.columns)}")
        summary.append("\n**Data Types and Sample Values:**")
        for col in df.columns:
            sample = df[col].iloc[0] if len(df) > 0 else "N/A"
            summary.append(f"- `{col}` ({df[col].dtype}): e.g., `{sample}`")
        return "\n".join(summary)
    except Exception as e:
        return f"Error loading dataset: {str(e)}"

def run_business_analysis(csv_path: str) -> str:
    """Performs business analysis on the dataset, calculating key performance indicators (KPIs) 
    such as total sales, total units sold, top products, and group summaries.

    Args:
        csv_path: The path to the CSV file containing sales data.
    """
    if not os.path.exists(csv_path):
        return f"Error: File not found at {csv_path}"
    
    try:
        df = pd.read_csv(csv_path)
        
        # Calculate key KPIs
        total_sales = df['Sales'].sum()
        total_units = df['Units'].sum()
        avg_satisfaction = df['Satisfaction'].mean()
        
        # Sales by category
        cat_sales = df.groupby('Category')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)
        cat_sales['Sales %'] = (cat_sales['Sales'] / total_sales * 100).round(2)
        cat_sales['Sales'] = cat_sales['Sales'].round(2)
        
        # Sales by region
        region_sales = df.groupby('Region')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)
        region_sales['Sales'] = region_sales['Sales'].round(2)
        
        # Top 5 products
        top_products = df.groupby('Product')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False).head(5)
        top_products['Sales'] = top_products['Sales'].round(2)
        
        report = []
        report.append("### Key Performance Indicators (KPIs)")
        report.append(f"- **Total Sales Revenue**: ${total_sales:,.2f}")
        report.append(f"- **Total Units Sold**: {total_units:,}")
        report.append(f"- **Average Customer Satisfaction**: {avg_satisfaction:.2f}/5.0")
        
        report.append("\n### Revenue by Category")
        report.append("| Category | Sales Revenue | Revenue Share % |")
        report.append("| :--- | :--- | :--- |")
        for _, row in cat_sales.iterrows():
            report.append(f"| {row['Category']} | ${row['Sales']:,} | {row['Sales %']}% |")
            
        report.append("\n### Revenue by Region")
        report.append("| Region | Sales Revenue |")
        report.append("| :--- | :--- |")
        for _, row in region_sales.iterrows():
            report.append(f"| {row['Region']} | ${row['Sales']:,} |")
            
        report.append("\n### Top 5 Best-Selling Products")
        report.append("| Product | Sales Revenue |")
        report.append("| :--- | :--- |")
        for _, row in top_products.iterrows():
            report.append(f"| {row['Product']} | ${row['Sales']:,} |")
            
        return "\n".join(report)
    except Exception as e:
        return f"Error analyzing data: {str(e)}"

def generate_and_save_chart(csv_path: str, chart_type: str, filename: str) -> str:
    """Generates a high-quality visualization from the dataset and saves it as an image.

    Args:
        csv_path: The path to the CSV file.
        chart_type: The type of chart to generate. Supported options: 
                    'sales_trend' (line chart of sales over time), 
                    'category_sales' (bar chart of sales per category), 
                    'region_distribution' (pie chart of sales per region),
                    'satisfaction_vs_sales' (scatter plot of sales vs satisfaction).
        filename: Name of the output image file (e.g. 'sales_trend.png').
    """
    if not os.path.exists(csv_path):
        return f"Error: File not found at {csv_path}"
        
    try:
        df = pd.read_csv(csv_path)
        os.makedirs('outputs', exist_ok=True)
        os.makedirs('outputs/charts', exist_ok=True)
        
        filepath = os.path.join('outputs/charts', filename)
        
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(10, 6))
        
        if chart_type == 'sales_trend':
            df['Date'] = pd.to_datetime(df['Date'])
            daily_sales = df.groupby('Date')['Sales'].sum().reset_index()
            daily_sales['Rolling_Avg'] = daily_sales['Sales'].rolling(window=7, min_periods=1).mean()
            
            plt.plot(daily_sales['Date'], daily_sales['Sales'], alpha=0.3, label='Daily Sales', color='#2b5c8f')
            plt.plot(daily_sales['Date'], daily_sales['Rolling_Avg'], label='7-Day Rolling Avg', color='#e67e22', linewidth=2.5)
            plt.title('Sales Trend Analysis', fontsize=14, fontweight='bold', pad=15)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Revenue ($)', fontsize=12)
            plt.legend()
            
        elif chart_type == 'category_sales':
            cat_sales = df.groupby('Category')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)
            sns.barplot(data=cat_sales, x='Sales', y='Category', hue='Category', palette='viridis', legend=False)
            plt.title('Revenue Contribution by Product Category', fontsize=14, fontweight='bold', pad=15)
            plt.xlabel('Revenue ($)', fontsize=12)
            plt.ylabel('Category', fontsize=12)
            
        elif chart_type == 'region_distribution':
            region_sales = df.groupby('Region')['Sales'].sum().reset_index()
            colors = sns.color_palette('pastel')[0:4]
            plt.pie(region_sales['Sales'], labels=region_sales['Region'], autopct='%1.1f%%', colors=colors, startangle=140)
            plt.title('Revenue Share by Region', fontsize=14, fontweight='bold', pad=15)
            
        elif chart_type == 'satisfaction_vs_sales':
            prod_stats = df.groupby('Product').agg({'Sales': 'sum', 'Satisfaction': 'mean'}).reset_index()
            sns.scatterplot(data=prod_stats, x='Satisfaction', y='Sales', size='Sales', sizes=(100, 500), hue='Satisfaction', palette='coolwarm')
            plt.title('Product Satisfaction vs. Total Sales Revenue', fontsize=14, fontweight='bold', pad=15)
            plt.xlabel('Average Customer Satisfaction Score', fontsize=12)
            plt.ylabel('Total Sales ($)', fontsize=12)
            
        else:
            return f"Error: Unknown chart_type '{chart_type}'."
            
        plt.tight_layout()
        plt.savefig(filepath, dpi=300)
        plt.close()
        
        return f"Successfully generated '{chart_type}' and saved it to '{filepath}'."
    except Exception as e:
        plt.close()
        return f"Error generating chart: {str(e)}"

def save_report_file(content: str, filepath: str) -> str:
    """Saves the final executive report content to a specified markdown file.

    Args:
        content: The Markdown content of the report.
        filepath: The path to save the report (e.g. 'outputs/executive_report.md').
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully saved executive report to '{filepath}'."
    except Exception as e:
        return f"Error saving report: {str(e)}"
