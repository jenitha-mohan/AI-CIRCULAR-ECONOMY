"""
AI Circular Economy Marketplace — Exploratory Data Analysis & Visualization Script
Generates high-resolution statistical charts saved into ml/reports/figures/.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIGURES_DIR = os.path.join(BASE_DIR, "ml", "reports", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

PRICE_DATA = os.path.join(BASE_DIR, "datasets", "material_prices.csv")
DEMAND_DATA = os.path.join(BASE_DIR, "datasets", "material_demand.csv")

# Set theme styling
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 10, "figure.autolayout": True})


def generate_all_eda_visualizations():
    print("=== Generating EDA Figures ===")
    df_prices = pd.read_csv(PRICE_DATA)
    df_demand = pd.read_csv(DEMAND_DATA)
    
    # 1. Material Distribution
    plt.figure(figsize=(9, 5))
    order = df_prices["material_type"].value_counts().index
    ax = sns.countplot(data=df_prices, x="material_type", order=order, hue="material_type", palette="viridis", legend=False)
    plt.title("Sample Distribution by Recyclable Material Type", fontsize=12, fontweight="bold")
    plt.xlabel("Material Type")
    plt.ylabel("Number of Samples")
    plt.xticks(rotation=30)
    plt.savefig(os.path.join(FIGURES_DIR, "material_distribution.png"), dpi=200)
    plt.close()
    
    # 2. Price Distribution
    plt.figure(figsize=(9, 5))
    sns.histplot(data=df_prices, x="price_per_kg", kde=True, color="#10b981", bins=40)
    plt.title("Price per Kilogram Distribution (INR/kg)", fontsize=12, fontweight="bold")
    plt.xlabel("Price per kg (₹)")
    plt.ylabel("Frequency")
    plt.savefig(os.path.join(FIGURES_DIR, "price_distribution.png"), dpi=200)
    plt.close()
    
    # 3. Demand by Material
    plt.figure(figsize=(10, 5))
    mat_demand = df_demand.groupby("material_type")["quantity_requested"].sum().sort_values(ascending=False).reset_index()
    sns.barplot(data=mat_demand, x="material_type", y="quantity_requested", hue="material_type", palette="crest", legend=False)
    plt.title("Total Annual Demand Volume by Material (kg)", fontsize=12, fontweight="bold")
    plt.xlabel("Material Type")
    plt.ylabel("Total Demand Requested (kg)")
    plt.xticks(rotation=30)
    plt.savefig(os.path.join(FIGURES_DIR, "demand_by_material.png"), dpi=200)
    plt.close()
    
    # 4. Price vs Quality
    plt.figure(figsize=(9, 5))
    sns.boxplot(data=df_prices, x="quality", y="price_per_kg", hue="quality", palette="Set2", legend=False)
    plt.title("Material Price per kg across Quality Grades", fontsize=12, fontweight="bold")
    plt.xlabel("Quality Grade")
    plt.ylabel("Price per kg (₹)")
    plt.savefig(os.path.join(FIGURES_DIR, "price_vs_quality.png"), dpi=200)
    plt.close()
    
    # 5. Price vs Weight (Scatter)
    plt.figure(figsize=(9, 5))
    sns.scatterplot(data=df_prices, x="weight_kg", y="price_per_kg", hue="material_type", alpha=0.6, palette="tab10")
    plt.title("Price per kg vs Batch Weight (kg)", fontsize=12, fontweight="bold")
    plt.xlabel("Weight (kg)")
    plt.ylabel("Price per kg (₹)")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)
    plt.savefig(os.path.join(FIGURES_DIR, "price_vs_weight.png"), dpi=200, bbox_inches="tight")
    plt.close()
    
    # 6. Location Distribution
    plt.figure(figsize=(10, 5))
    loc_counts = df_prices["location"].value_counts().reset_index()
    loc_counts.columns = ["location", "count"]
    sns.barplot(data=loc_counts, x="location", y="count", hue="location", palette="Blues_r", legend=False)
    plt.title("Listing Distribution Across Circular Hub Cities", fontsize=12, fontweight="bold")
    plt.xlabel("City")
    plt.ylabel("Listings Count")
    plt.xticks(rotation=30)
    plt.savefig(os.path.join(FIGURES_DIR, "location_distribution.png"), dpi=200)
    plt.close()
    
    # 7. Monthly Demand Trends
    df_demand["month"] = pd.to_datetime(df_demand["date"]).dt.month
    monthly_trend = df_demand.groupby(["month", "material_type"])["quantity_requested"].mean().reset_index()
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=monthly_trend, x="month", y="quantity_requested", hue="material_type", marker="o")
    plt.title("Monthly Average Demand Trajectory by Recyclable Type", fontsize=12, fontweight="bold")
    plt.xlabel("Month (1 = Jan, 12 = Dec)")
    plt.ylabel("Average Requested Quantity (kg)")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.savefig(os.path.join(FIGURES_DIR, "monthly_demand.png"), dpi=200, bbox_inches="tight")
    plt.close()
    
    # 8. Correlation Matrix
    plt.figure(figsize=(8, 6))
    num_df = df_prices.select_dtypes(include=[np.number])
    corr = num_df.corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1)
    plt.title("Feature Correlation Matrix", fontsize=12, fontweight="bold")
    plt.savefig(os.path.join(FIGURES_DIR, "correlation_matrix.png"), dpi=200)
    plt.close()
    
    # 9. Outlier Analysis
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=df_prices, x="material_type", y="price_per_kg", hue="material_type", palette="pastel", legend=False)
    plt.title("Material Price Outlier Analysis by Category", fontsize=12, fontweight="bold")
    plt.xlabel("Material Type")
    plt.ylabel("Price per kg (₹)")
    plt.xticks(rotation=30)
    plt.savefig(os.path.join(FIGURES_DIR, "outliers.png"), dpi=200)
    plt.close()
    
    print(f"All 9 EDA visualizations generated and saved in {FIGURES_DIR}")


if __name__ == "__main__":
    generate_all_eda_visualizations()
