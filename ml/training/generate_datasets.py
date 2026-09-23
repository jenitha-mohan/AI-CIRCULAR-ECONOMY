"""
AI Circular Economy Marketplace — Dataset Generation Pipeline
NOTE: DEVELOPMENT DATA — NOT REAL MARKET DATA
Generates structured, realistic benchmark datasets for price prediction, transaction analysis,
demand forecasting, and buyer-seller matching.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set fixed random seed for full reproducibility
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "datasets")
os.makedirs(DATASET_DIR, exist_ok=True)

MATERIALS = [
    "Aluminum", "Copper", "Steel", "Plastic", "Paper", 
    "Glass", "Textile", "E-waste", "Cardboard", "Other"
]

CITIES = [
    {"city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lon": 76.9558},
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707},
    {"city": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946},
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867},
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567},
    {"city": "Delhi", "state": "Delhi", "lat": 28.7041, "lon": 77.1025},
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714},
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639},
    {"city": "Surat", "state": "Gujarat", "lat": 21.1702, "lon": 72.8311},
]

QUALITIES = ["High", "Medium", "Low", "Industrial Grade"]
CONDITIONS = ["Clean", "Contaminated", "Sorted", "Mixed", "Baled"]
DEMAND_LEVELS = ["High", "Moderate", "Low"]
SELLER_TYPES = ["Business", "Individual", "Industrial Recycler", "Municipal Collector"]
PURPOSES = ["Recycling", "Upcycling", "Direct Reuse", "Repurposing"]

# Base pricing models per material (INR / kg)
BASE_PRICES = {
    "Copper": 650.0,
    "Aluminum": 180.0,
    "E-waste": 120.0,
    "Steel": 42.0,
    "Textile": 28.0,
    "Plastic": 35.0,
    "Cardboard": 14.0,
    "Paper": 12.0,
    "Glass": 8.0,
    "Other": 15.0
}

QUALITY_MULTIPLIERS = {
    "High": 1.15,
    "Industrial Grade": 1.25,
    "Medium": 1.00,
    "Low": 0.80
}

CONDITION_MULTIPLIERS = {
    "Clean": 1.10,
    "Sorted": 1.05,
    "Baled": 1.08,
    "Mixed": 0.90,
    "Contaminated": 0.70
}

DEMAND_MULTIPLIERS = {
    "High": 1.12,
    "Moderate": 1.00,
    "Low": 0.88
}


def generate_price_dataset(n_samples=2500):
    """
    Generate dataset for price prediction regression model.
    Target: price_per_kg
    """
    rows = []
    for _ in range(n_samples):
        mat = random.choice(MATERIALS)
        base = BASE_PRICES[mat]
        quality = random.choice(QUALITIES)
        condition = random.choice(CONDITIONS)
        demand_level = random.choice(DEMAND_LEVELS)
        seller_type = random.choice(SELLER_TYPES)
        loc = random.choice(CITIES)["city"]
        
        weight_kg = round(np.random.exponential(scale=500) + 20, 1)
        weight_kg = min(weight_kg, 10000.0)
        
        month = random.randint(1, 12)
        transportation_distance = round(random.uniform(5.0, 150.0), 1)
        processing_cost = round(random.uniform(2.0, 15.0), 2)
        
        # Historical price base with noise
        hist_price = round(base * random.uniform(0.92, 1.08), 2)
        buyer_demand = round(random.uniform(0.3, 1.0), 2)
        
        # Calculate realistic, non-linear price_per_kg target with physics-inspired factors
        q_mult = QUALITY_MULTIPLIERS[quality]
        c_mult = CONDITION_MULTIPLIERS[condition]
        d_mult = DEMAND_MULTIPLIERS[demand_level]
        
        # Volume discount effect: large volume slight premium/discount
        volume_factor = 1.0 + (0.04 * np.log10(max(weight_kg, 10) / 100))
        # Distance cost deduction
        dist_impact = max(0.0, transportation_distance * 0.03)
        # Seasonal cycle
        seasonal_factor = 1.0 + 0.03 * np.sin(2 * np.pi * month / 12)
        
        price = (hist_price * q_mult * c_mult * d_mult * volume_factor * seasonal_factor) - dist_impact - (processing_cost * 0.4)
        price += np.random.normal(0, base * 0.02) # Realistic noise
        price_per_kg = round(max(price, base * 0.4), 2)
        
        rows.append({
            "material_type": mat,
            "weight_kg": weight_kg,
            "quality": quality,
            "location": loc,
            "demand_level": demand_level,
            "historical_price": hist_price,
            "processing_cost": processing_cost,
            "transportation_distance": transportation_distance,
            "month": month,
            "seller_type": seller_type,
            "buyer_demand": buyer_demand,
            "material_condition": condition,
            "price_per_kg": price_per_kg
        })
        
    df = pd.DataFrame(rows)
    output_path = os.path.join(DATASET_DIR, "material_prices.csv")
    df.to_csv(output_path, index=False)
    print(f"[Dataset] Generated {len(df)} price prediction samples -> {output_path}")
    return df


def generate_demand_dataset(days=365):
    """
    Generate daily time-series demand dataset for 10 materials across 1 year.
    Features: date, material_type, quantity_requested, quantity_sold, average_price,
              number_of_buyers, number_of_transactions, location
    """
    rows = []
    start_date = datetime(2025, 1, 1)
    
    for mat in MATERIALS:
        base_demand = {
            "Steel": 12000, "Aluminum": 6000, "Copper": 3500, "Plastic": 8500,
            "Paper": 7000, "Cardboard": 9000, "Glass": 4000, "Textile": 3000,
            "E-waste": 1500, "Other": 1200
        }[mat]
        
        trend_slope = random.uniform(2.0, 8.0) # Secular upward trend in circular recycling
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            day_of_year = current_date.timetuple().tm_yday
            day_of_week = current_date.weekday()
            
            # Weekly seasonality (lower on Sundays)
            weekly_mult = 0.6 if day_of_week == 6 else (0.85 if day_of_week == 5 else 1.05)
            # Annual seasonality
            annual_mult = 1.0 + 0.15 * np.sin(2 * np.pi * day_of_year / 365)
            
            # Demand calculation
            demand = (base_demand + (trend_slope * i)) * weekly_mult * annual_mult
            demand += np.random.normal(0, base_demand * 0.05)
            quantity_requested = round(max(demand, 100.0), 1)
            
            fulfillment_rate = random.uniform(0.75, 0.95)
            quantity_sold = round(quantity_requested * fulfillment_rate, 1)
            
            avg_price = round(BASE_PRICES[mat] * random.uniform(0.95, 1.05), 2)
            n_buyers = int(max(3, round(quantity_requested / (base_demand / 12) + random.randint(1, 5))))
            n_tx = int(max(2, round(n_buyers * random.uniform(0.8, 1.5))))
            loc = random.choice(CITIES)["city"]
            
            rows.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "material_type": mat,
                "quantity_requested": quantity_requested,
                "quantity_sold": quantity_sold,
                "average_price": avg_price,
                "number_of_buyers": n_buyers,
                "number_of_transactions": n_tx,
                "location": loc
            })
            
    df = pd.DataFrame(rows)
    output_path = os.path.join(DATASET_DIR, "material_demand.csv")
    df.to_csv(output_path, index=False)
    print(f"[Dataset] Generated {len(df)} time-series demand records -> {output_path}")
    return df


def generate_buyers_dataset(n_buyers=60):
    """
    Generate buyers directory for matching engine and recommendation benchmarking.
    """
    COMPANY_NAMES = [
        "EcoMetal Industries", "GreenPlast Recyclers", "Apex Copper Smelting", 
        "CleanEarth Circular Solutions", "Bharat Paper Mill", "Titanium & Steel Works",
        "BioTex Upcyclers", "ElectroWaste Refiners", "Zenith Glass Works",
        "Coimbatore Sustainable Plastics", "Vanguard Industrial Scrap", "ReCycle India Corp",
        "Sunrise Cardboard Packaging", "Terra Polymer Hub", "Nilgiri Eco Fibers"
    ]
    
    rows = []
    for i in range(n_buyers):
        c_name = f"{random.choice(COMPANY_NAMES)} #{i+1}"
        mat = random.choice(MATERIALS)
        loc = random.choice(CITIES)
        min_q = random.choice([50, 100, 200, 500, 1000])
        max_q = min_q * random.choice([2, 5, 10, 20])
        quality_req = random.choice(QUALITIES)
        purpose = random.choice(PURPOSES)
        max_price = round(BASE_PRICES[mat] * random.uniform(1.05, 1.25), 2)
        
        rows.append({
            "buyer_id": f"BUY-{1000+i}",
            "name": c_name,
            "material_type": mat,
            "min_quantity_kg": min_q,
            "max_quantity_kg": max_q,
            "quality_required": quality_req,
            "intended_purpose": purpose,
            "max_price_per_kg": max_price,
            "city": loc["city"],
            "state": loc["state"],
            "latitude": loc["lat"],
            "longitude": loc["lon"]
        })
        
    df = pd.DataFrame(rows)
    output_path = os.path.join(DATASET_DIR, "buyers.csv")
    df.to_csv(output_path, index=False)
    print(f"[Dataset] Generated {len(df)} buyer profiles -> {output_path}")
    return df


def generate_transactions_dataset(n_transactions=500):
    """
    Generate historical marketplace transaction logs with sustainability impact.
    """
    CO2_FACTORS = {
        "Aluminum": 9.1, "Copper": 4.5, "Steel": 1.8, "Plastic": 1.5,
        "Paper": 1.1, "Glass": 0.35, "Textile": 3.2, "E-waste": 5.8,
        "Cardboard": 1.0, "Other": 0.8
    }
    
    rows = []
    start_date = datetime(2025, 6, 1)
    
    for i in range(n_transactions):
        mat = random.choice(MATERIALS)
        tx_date = start_date + timedelta(days=random.randint(0, 365))
        qty_kg = round(random.uniform(50.0, 3000.0), 1)
        base = BASE_PRICES[mat]
        price_per_kg = round(base * random.uniform(0.92, 1.12), 2)
        total_amount = round(qty_kg * price_per_kg, 2)
        
        co2_avoided = round(qty_kg * CO2_FACTORS[mat], 2)
        landfill_diverted = round(qty_kg * 0.95, 2)
        status = random.choices(["completed", "completed", "completed", "pending", "in_negotiation"], weights=[80, 10, 5, 3, 2])[0]
        
        rows.append({
            "transaction_id": f"TX-{10000+i}",
            "date": tx_date.strftime("%Y-%m-%d"),
            "material_type": mat,
            "quantity_kg": qty_kg,
            "agreed_price_per_kg": price_per_kg,
            "total_amount": total_amount,
            "status": status,
            "co2_avoided_kg": co2_avoided,
            "landfill_diverted_kg": landfill_diverted
        })
        
    df = pd.DataFrame(rows)
    output_path = os.path.join(DATASET_DIR, "material_transactions.csv")
    df.to_csv(output_path, index=False)
    print(f"[Dataset] Generated {len(df)} transaction records -> {output_path}")
    return df


def write_image_dataset_readme():
    readme_path = os.path.join(DATASET_DIR, "material_images", "README.md")
    content = """# Circular Economy Material Image Dataset
**DEVELOPMENT & BENCHMARK DIRECTORY**

This directory defines the circular waste material classification taxonomy.
Supported categories:
- 0: Plastic (PET, HDPE, LDPE, PP bottles and polymers)
- 1: Aluminum (Cans, extruded profiles, cast alloys)
- 2: Copper (Wires, cabling, copper pipe scrap)
- 3: Steel (Structural beams, sheet metal, scrap rods)
- 4: Paper (Office paper, newspapers, pulp)
- 5: Glass (Bottles, cullet, float glass)
- 6: Textile (Cotton remnants, garment cuttings, synthetic yarn)
- 7: E-waste (Printed circuit boards, motherboards, IC components)
- 8: Cardboard (Corrugated boxes, packaging cartons)
- 9: Other (Mixed composite circular waste)

The vision inference pipeline uses MobileNetV2 transfer learning with fallback heuristic feature classification when operating in rapid local development environments.
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[Dataset] Wrote image taxonomy README -> {readme_path}")


if __name__ == "__main__":
    print("=== Generating AI Circular Economy Marketplace Datasets ===")
    generate_price_dataset()
    generate_demand_dataset()
    generate_buyers_dataset()
    generate_transactions_dataset()
    write_image_dataset_readme()
    print("=== All Datasets Generated Successfully ===")
