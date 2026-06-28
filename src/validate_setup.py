import os
import sys

# Ensure src is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def validate():
    print("Aegis Analytics - Environment Validation Script")
    print("=" * 50)
    
    passed_all = True
    
    # 1. Check Gemini API Key
    print("\n1. Checking API Key Configuration...")
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        # Mask API key for safety
        masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "Configured"
        print(f"   [OK] GEMINI_API_KEY found in .env: {masked}")
    else:
        print("   [WARNING] GEMINI_API_KEY not found in .env. You must configure it before running the agent!")
        passed_all = False
        
    # 2. Check Python Packages
    print("\n2. Checking Python dependencies...")
    packages = {
        "google.antigravity": "Google Antigravity SDK",
        "pandas": "Pandas Data Ingestion",
        "matplotlib": "Matplotlib Visualization",
        "seaborn": "Seaborn Styling",
        "streamlit": "Streamlit Web Framework",
        "pydantic": "Pydantic Validation"
    }
    
    for pkg, desc in packages.items():
        try:
            __import__(pkg)
            print(f"   [OK] {desc} ({pkg}) is installed.")
        except ImportError:
            print(f"   [ERROR] {desc} ({pkg}) is NOT installed.")
            passed_all = False
            
    # 3. Check Dataset
    print("\n3. Checking Sales Dataset...")
    csv_path = 'data/sales_data.csv'
    if os.path.exists(csv_path):
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            print(f"   [OK] Dataset found at '{csv_path}'. Loaded {len(df)} records.")
            
            # Check required columns
            required_cols = {'Date', 'Category', 'Product', 'Region', 'Units', 'Price', 'Sales', 'Satisfaction'}
            missing_cols = required_cols - set(df.columns)
            if not missing_cols:
                print("   [OK] All required columns exist in the dataset.")
            else:
                print(f"   [ERROR] Missing required columns: {missing_cols}")
                passed_all = False
        except Exception as e:
            print(f"   [ERROR] Found dataset but failed to parse: {e}")
            passed_all = False
    else:
        print(f"   [WARNING] Dataset not found at '{csv_path}'. Running generate_sample_data.py to create one...")
        try:
            import generate_sample_data
            generate_sample_data.create_synthetic_data()
            if os.path.exists(csv_path):
                print(f"   [OK] Dataset successfully generated with {len(pd.read_csv(csv_path))} records.")
            else:
                print("   [ERROR] Failed to generate dataset.")
                passed_all = False
        except Exception as ex:
            print(f"   [ERROR] Failed to run dataset generation script: {ex}")
            passed_all = False
            
    # 4. Check Matplotlib Headless Rendering
    print("\n4. Testing local chart generation...")
    try:
        import tools
        # Try plotting sales_trend locally
        chart_result = tools.generate_and_save_chart(csv_path, 'sales_trend', 'temp_test.png')
        if "Successfully" in chart_result:
            print("   [OK] Local headless chart generation tested successfully.")
            # Clean up temp test chart
            temp_path = 'outputs/charts/temp_test.png'
            if os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            print(f"   [ERROR] Local chart generation failed: {chart_result}")
            passed_all = False
    except Exception as e:
        print(f"   [ERROR] Exception raised during chart generation: {e}")
        passed_all = False

    # Summary
    print("\n" + "=" * 50)
    if passed_all:
        print("[SUCCESS] All local validation checks passed! Ready for execution.")
    else:
        print("[NOTICE] Some verification items need attention. Please verify the warnings/errors above.")

if __name__ == '__main__':
    validate()
