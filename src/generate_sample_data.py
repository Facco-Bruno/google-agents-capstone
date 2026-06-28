import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_synthetic_data():
    np.random.seed(42)
    
    # Create date range
    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    
    categories = ['Electronics', 'Clothing', 'Home', 'Beauty', 'Sports']
    regions = ['North', 'South', 'East', 'West']
    
    products = {
        'Electronics': ['Laptop', 'Smartphone', 'Headphones', 'Smartwatch'],
        'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Sneakers'],
        'Home': ['Coffee Maker', 'Vacuum', 'Blender', 'Sofa'],
        'Beauty': ['Lipstick', 'Perfume', 'Face Cream', 'Mascara'],
        'Sports': ['Dumbbell', 'Yoga Mat', 'Running Shoes', 'Bicycle']
    }
    
    data = []
    
    for date in dates:
        # Number of transactions in a day
        num_transactions = np.random.randint(5, 15)
        for _ in range(num_transactions):
            category = np.random.choice(categories)
            product = np.random.choice(products[category])
            region = np.random.choice(regions)
            
            # Base price and quantities
            base_price = {
                'Laptop': 1000, 'Smartphone': 700, 'Headphones': 150, 'Smartwatch': 250,
                'T-Shirt': 25, 'Jeans': 60, 'Jacket': 120, 'Sneakers': 80,
                'Coffee Maker': 90, 'Vacuum': 180, 'Blender': 50, 'Sofa': 600,
                'Lipstick': 15, 'Perfume': 80, 'Face Cream': 35, 'Mascara': 20,
                'Dumbbell': 40, 'Yoga Mat': 30, 'Running Shoes': 90, 'Bicycle': 450
            }[product]
            
            # Add some variance and promotions
            price = round(base_price * np.random.uniform(0.9, 1.1), 2)
            units = int(np.random.choice([1, 2, 3, 4, 5], p=[0.5, 0.25, 0.15, 0.07, 0.03]))
            sales = round(price * units, 2)
            
            # Customer satisfaction
            satisfaction = round(np.clip(np.random.normal(4.2, 0.8), 1, 5), 1)
            
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Category': category,
                'Product': product,
                'Region': region,
                'Units': units,
                'Price': price,
                'Sales': sales,
                'Satisfaction': satisfaction
            })
            
    df = pd.DataFrame(data)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/sales_data.csv', index=False)
    print(f"Sample dataset successfully generated at 'data/sales_data.csv' with {len(df)} records.")

if __name__ == '__main__':
    create_synthetic_data()
