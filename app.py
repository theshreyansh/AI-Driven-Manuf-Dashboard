# --- IMPORTS ---
import random
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from faker import Faker


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="SupplyOne | Wholesale Distribution Dashboard",
    page_icon="HDS",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- STYLE ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(0, 122, 255, 0.10), transparent 28rem),
            linear-gradient(180deg, #f6f8fb 0%, #ffffff 42%);
    }
    h1, h2, h3 {
        color: #18202f;
        font-weight: 750;
        letter-spacing: 0;
    }
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(21, 32, 51, 0.08);
        border-radius: 8px;
        padding: 14px 16px;
        box-shadow: 0 10px 26px rgba(21, 32, 51, 0.07);
        animation: riseIn 520ms ease both;
    }
    [data-testid="stMetricValue"] {
        color: #152033;
        font-weight: 800;
    }
    [data-testid="stMetricDelta"] {
        font-weight: 650;
    }
    .stPlotlyChart {
        background: rgba(255, 255, 255, 0.80);
        border: 1px solid rgba(21, 32, 51, 0.06);
        border-radius: 8px;
        box-shadow: 0 10px 24px rgba(21, 32, 51, 0.06);
        padding: 8px;
        animation: fadeUp 560ms ease both;
    }
    .hero-note {
        color: #465366;
        font-size: 1rem;
        line-height: 1.5;
        margin-bottom: 0.75rem;
    }
    .filter-pill {
        display: inline-block;
        background: #eef4ff;
        border: 1px solid #cdddf7;
        border-radius: 999px;
        color: #1c4b82;
        font-size: 0.78rem;
        font-weight: 700;
        margin: 0 0.35rem 0.35rem 0;
        padding: 0.32rem 0.62rem;
    }
    .kpi-scroll {
        max-height: 330px;
        overflow-y: auto;
        padding-right: 0.35rem;
    }
    .kpi-definition {
        background: #ffffff;
        border: 1px solid #e0e7f1;
        border-left: 5px solid #ccd6e2;
        border-radius: 8px;
        margin: 0 0 0.65rem 0;
        padding: 0.8rem 0.9rem;
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }
    .kpi-definition:hover {
        border-left-color: #0067b1;
        box-shadow: 0 12px 22px rgba(21, 32, 51, 0.08);
        transform: translateY(-1px);
    }
    .kpi-definition.active {
        background: linear-gradient(90deg, #eaf4ff 0%, #ffffff 56%);
        border-color: #9bc8ff;
        border-left-color: #007aff;
        box-shadow: 0 14px 26px rgba(0, 122, 255, 0.13);
    }
    .kpi-definition b {
        color: #172033;
    }
    .kpi-definition span {
        color: #536174;
        display: block;
        font-size: 0.86rem;
        line-height: 1.45;
        margin-top: 0.24rem;
    }
    .insight-card {
        background: #ffffff;
        border: 1px solid #e3e9f2;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        min-height: 112px;
    }
    .insight-card b {
        color: #172033;
    }
    .insight-card span {
        color: #536174;
        display: block;
        font-size: 0.86rem;
        margin-top: 0.35rem;
    }
    .takeaway {
        background: #fff7ed;
        border-left: 5px solid #f97316;
        border-radius: 8px;
        color: #7c2d12;
        font-size: 0.88rem;
        font-weight: 650;
        line-height: 1.45;
        margin: 0.35rem 0 1rem 0;
        padding: 0.75rem 0.85rem;
    }
    .risk-panel {
        background: #ffffff;
        border: 1px solid #fed7aa;
        border-left: 6px solid #f97316;
        border-radius: 8px;
        min-height: 150px;
        padding: 1rem;
    }
    .risk-panel.high {
        border-color: #fecaca;
        border-left-color: #dc2626;
        background: #fff5f5;
    }
    .risk-panel b {
        color: #172033;
        display: block;
        margin-bottom: 0.35rem;
    }
    .risk-panel span, .roadmap-card span {
        color: #536174;
        display: block;
        font-size: 0.86rem;
        line-height: 1.45;
    }
    .roadmap-card {
        background: #ffffff;
        border: 1px solid #e3e9f2;
        border-radius: 8px;
        min-height: 205px;
        padding: 1rem;
    }
    .roadmap-card b {
        color: #172033;
        display: block;
        margin-bottom: 0.35rem;
    }
    @keyframes riseIn {
        from { opacity: 0; transform: translateY(12px) scale(0.99); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- CONSTANTS ---
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

REGION_COLORS = {"US": "#0067B1", "Canada": "#D83B01"}
ACCENT_SCALE = ["#0067B1", "#00A3A3", "#7A5C00", "#D83B01", "#6B4EFF", "#18864B"]

KPI_DEFINITIONS = {
    "On-Time Delivery Rate": "Measures the percentage of customer orders delivered within the promised delivery timeline. Critical for customer satisfaction, SLA adherence, and operational reliability across healthcare, hospitality, and government housing.",
    "Perfect Order Rate": "Tracks orders delivered without errors, damages, delays, or missing items. Helps assess end-to-end distribution quality and customer experience.",
    "Fill Rate": "Measures the percentage of customer demand fulfilled immediately from available inventory. Indicates inventory effectiveness and service capability.",
    "Order Cycle Time": "Average time taken from order placement to final delivery. Helps optimize warehouse operations, logistics, and customer responsiveness.",
    "Inventory Turnover Ratio": "Evaluates how efficiently inventory is sold and replenished over time. High turnover indicates healthy demand forecasting and stock management.",
    "Backorder Rate": "Measures the percentage of orders delayed due to insufficient stock availability. Helps identify inventory planning gaps and supplier issues.",
    "Warehouse Utilization": "Tracks how efficiently warehouse storage capacity is being used across distribution centers. Supports space optimization and operational planning.",
    "Transportation Cost per Shipment": "Measures logistics cost incurred for each shipment delivered. Helps optimize routing, carrier selection, and fuel efficiency.",
    "Supplier On-Time Performance": "Evaluates supplier reliability based on timely material deliveries. Essential for maintaining smooth procurement and distribution operations.",
    "Demand Forecast Accuracy": "Compares forecasted demand against actual sales or orders. Helps reduce overstocking, stockouts, and supply chain inefficiencies.",
    "Inventory Accuracy": "Measures alignment between physical inventory and system records. Critical for warehouse efficiency, financial accuracy, and order fulfillment.",
    "Stockout Frequency": "Tracks how often products become unavailable for customer orders. Directly impacts revenue loss and customer satisfaction.",
    "Returns & Damage Rate": "Measures percentage of returned or damaged goods during transit or fulfillment. Helps improve packaging, handling, and quality control.",
    "Distribution Center Productivity": "Evaluates operational efficiency of warehouses using metrics like orders processed per labor hour or per shift.",
    "Freight Utilization Efficiency": "Measures truck or container space utilization during transportation. Helps reduce logistics costs and carbon footprint.",
    "Customer Satisfaction Score (CSAT)": "Captures customer feedback on delivery experience, product availability, and service quality. Important for retention and brand trust.",
    "Net Promoter Score (NPS)": "Measures customer loyalty and likelihood to recommend SupplyOne services to others. Indicates long-term customer relationship strength.",
    "Procurement Cost Savings": "Tracks savings achieved through vendor negotiations, bulk purchasing, and sourcing optimization initiatives.",
    "Average Delivery Distance per Route": "Measures delivery route efficiency and geographic optimization across the U.S. and Canada distribution network.",
    "Carbon Emissions per Shipment": "Tracks sustainability impact by measuring emissions generated per delivery or shipment handled. Supports ESG and sustainability goals.",
    "Labor Productivity Rate": "Measures workforce efficiency in warehouses and logistics operations using output-per-employee metrics.",
    "Order Accuracy Rate": "Tracks percentage of orders picked, packed, and delivered correctly without manual errors.",
    "Supplier Defect Rate": "Measures defective or non-compliant goods received from suppliers. Helps maintain quality standards and reduce returns.",
    "Revenue per Distribution Center": "Evaluates sales contribution and operational performance of each distribution center location.",
    "Cost per Order Fulfillment": "Calculates total operational cost involved in processing and delivering each order. Helps improve profitability and efficiency.",
    "Emergency Order Response Time": "Measures responsiveness to urgent or critical orders, especially important for healthcare and government clients.",
    "Fleet Downtime Rate": "Tracks unavailability of transportation vehicles due to maintenance or operational issues. Impacts delivery reliability.",
    "Employee Safety Incident Rate": "Measures workplace safety performance across warehouses and logistics operations. Supports compliance and employee well-being.",
    "Multi-Channel Order Fulfillment Efficiency": "Tracks effectiveness of fulfilling orders from multiple sales channels including online, direct sales, and enterprise procurement.",
    "Distribution Network Efficiency Index": "Consolidated KPI measuring overall efficiency of warehouses, transportation, fulfillment, and inventory movement across the supply chain.",
}

KPI_COLUMNS = {
    "On-Time Delivery Rate": ("On-Time Delivery Rate", "percent", True),
    "Perfect Order Rate": ("Perfect Order Rate", "percent", True),
    "Fill Rate": ("Fill Rate", "percent", True),
    "Order Cycle Time": ("Order Cycle Time (days)", "days", False),
    "Inventory Turnover Ratio": ("Inventory Turnover", "x", True),
    "Backorder Rate": ("Backorder Rate", "percent", False),
    "Warehouse Utilization": ("Warehouse Utilization", "percent", True),
    "Transportation Cost per Shipment": ("Transportation Cost per Shipment ($)", "currency", False),
    "Supplier On-Time Performance": ("Supplier On-Time Performance", "percent", True),
    "Demand Forecast Accuracy": ("Demand Forecast Accuracy", "percent", True),
    "Inventory Accuracy": ("Inventory Accuracy", "percent", True),
    "Stockout Frequency": ("Stockout Frequency", "percent", False),
    "Returns & Damage Rate": ("Returns & Damage Rate", "percent", False),
    "Distribution Center Productivity": ("Distribution Center Productivity", "number", True),
    "Freight Utilization Efficiency": ("Freight Utilization Efficiency", "percent", True),
    "Customer Satisfaction Score (CSAT)": ("Customer Satisfaction Score (CSAT)", "score", True),
    "Net Promoter Score (NPS)": ("Net Promoter Score (NPS)", "number", True),
    "Procurement Cost Savings": ("Procurement Cost Savings", "percent", True),
    "Average Delivery Distance per Route": ("Average Delivery Distance (miles)", "miles", False),
    "Carbon Emissions per Shipment": ("Carbon Emissions per Shipment (kg CO2)", "kg", False),
    "Labor Productivity Rate": ("Labor Productivity Rate", "number", True),
    "Order Accuracy Rate": ("Order Accuracy Rate", "percent", True),
    "Supplier Defect Rate": ("Supplier Defect Rate", "percent", False),
    "Revenue per Distribution Center": ("Revenue per Distribution Center ($)", "currency_compact", True),
    "Cost per Order Fulfillment": ("Cost per Order Fulfillment ($)", "currency", False),
    "Emergency Order Response Time": ("Emergency Order Response Time (hours)", "hours", False),
    "Fleet Downtime Rate": ("Fleet Downtime Rate", "percent", False),
    "Employee Safety Incident Rate": ("Employee Safety Incident Rate", "rate", False),
    "Multi-Channel Order Fulfillment Efficiency": ("Multi-Channel Order Fulfillment Efficiency", "percent", True),
    "Distribution Network Efficiency Index": ("Distribution Network Efficiency Index", "percent", True),
}

CORE_KPIS = [
    "On-Time Delivery Rate",
    "Perfect Order Rate",
    "Fill Rate",
    "Order Cycle Time",
    "Inventory Turnover Ratio",
]


# --- HELPERS ---
def generate_synthetic_data() -> pd.DataFrame:
    regions = ["US", "Canada"]
    industries = [
        "Multifamily",
        "Institutional",
        "Hospitality",
        "Trades",
        "Government Housing",
        "Healthcare",
        "Building Services",
        "Education",
    ]
    distribution_centers = [f"DC-{i:03d}" for i in range(1, 101)]
    product_categories = ["Plumbing", "Electrical", "HVAC", "Janitorial", "Hardware", "Appliances", "Lighting", "Safety"]
    aging_buckets = ["0-30 days", "31-60 days", "61-90 days", "90+ days"]
    delivery_routes = [f"Route-{i:02d}" for i in range(1, 25)]
    warehouse_zones = ["Receiving", "Bulk Storage", "Forward Pick", "Packout", "Returns", "Cross Dock"]
    query_types = ["Part Number", "Natural Language", "Compatibility", "Brand", "Specification", "Image Search"]
    search_stages = ["Query Entered", "Results Viewed", "Product Opened", "Cart Add", "Checkout"]
    suppliers = ["Apex Industrial", "NorthStar Supply", "PrimeSource", "BuildRight", "OmniParts", "Civic Materials"]
    enrichment_stages = ["Received", "Validated", "Standardized", "Enriched", "Published"]
    customer_segments = ["Enterprise", "Healthcare", "Hospitality", "Government", "Multifamily", "Trades"]
    interventions = ["Account Review", "Contract Refresh", "Promo Offer", "Service Recovery", "Executive Outreach"]
    commodities = ["Copper", "Steel", "PVC", "Fuel", "Lumber", "Aluminum"]
    vehicle_types = ["Van", "Box Truck", "Tractor Trailer", "Flatbed", "Refrigerated"]
    maintenance_types = ["Preventive", "Reactive"]
    delay_reasons = ["Traffic", "Vehicle Failure", "Dock Delay", "Inventory Hold", "Weather", "Carrier Capacity"]
    departments = ["Sales", "Customer Care", "Warehouse Ops", "Procurement", "Field Service", "Finance"]
    issue_categories = ["Order Status", "Product Fit", "Invoice", "Returns", "Delivery Exception", "Technical Spec"]
    data_domains = ["Product", "Vendor", "Customer", "Inventory", "Pricing", "Route", "Order"]
    mandatory_fields = ["SKU", "Supplier ID", "Customer ID", "UOM", "Cost", "Lead Time", "Tax Code", "Address"]
    data_issue_types = ["Completeness", "Duplicate", "Invalid Value", "Freshness", "Reference Error", "Format"]
    business_functions = ["Supply Chain", "Warehouse", "Procurement", "Pricing", "Customer Care", "Finance", "IT Security"]
    violation_types = ["Privileged Access", "Segregation of Duties", "Dormant User", "Shared Account", "MFA Exception", "Role Drift"]
    audit_statuses = ["Open", "In Remediation", "Management Review", "Closed"]

    rows = []
    for _ in range(1500):
        forecast_units = np.random.randint(800, 3600)
        actual_units = max(100, int(forecast_units * np.random.uniform(0.82, 1.18)))
        stockout_count = np.random.poisson(4)
        rows.append(
            {
                "Date": fake.date_between(start_date="-1y", end_date="today"),
                "Region": random.choice(regions),
                "Distribution Center": random.choice(distribution_centers),
                "Industry": random.choice(industries),
                "Product Category": random.choice(product_categories),
                "Aging Bucket": random.choice(aging_buckets),
                "Delivery Route": random.choice(delivery_routes),
                "Warehouse Zone": random.choice(warehouse_zones),
                "Query Type": random.choice(query_types),
                "Search Stage": random.choice(search_stages),
                "Supplier Name": random.choice(suppliers),
                "Enrichment Stage": random.choice(enrichment_stages),
                "Customer Segment": random.choice(customer_segments),
                "Intervention Type": random.choice(interventions),
                "Commodity": random.choice(commodities),
                "Vehicle Type": random.choice(vehicle_types),
                "Maintenance Type": random.choice(maintenance_types),
                "Delay Reason": random.choice(delay_reasons),
                "Department": random.choice(departments),
                "Issue Category": random.choice(issue_categories),
                "Data Domain": random.choice(data_domains),
                "Mandatory Field Name": random.choice(mandatory_fields),
                "Data Quality Issue Type": random.choice(data_issue_types),
                "Business Function": random.choice(business_functions),
                "Violation Type": random.choice(violation_types),
                "Audit Finding Status": random.choice(audit_statuses),
                "Forecast Demand Units": forecast_units,
                "Actual Demand Units": actual_units,
                "Stockout Count": stockout_count,
                "Inventory Holding Cost ($)": np.random.uniform(12000, 115000),
                "Inventory Value ($)": np.random.uniform(50000, 900000),
                "Safety Stock Quantity": np.random.randint(500, 9000),
                "On-Time Delivery Rate": np.random.uniform(0.85, 0.99),
                "Perfect Order Rate": np.random.uniform(0.80, 0.98),
                "Fill Rate": np.random.uniform(0.75, 0.95),
                "Order Cycle Time (days)": np.random.randint(1, 7),
                "Inventory Turnover": np.random.uniform(4, 12),
                "Backorder Rate": np.random.uniform(0.01, 0.10),
                "Warehouse Utilization": np.random.uniform(0.60, 0.95),
                "Transportation Cost per Shipment ($)": np.random.uniform(5, 20),
                "Supplier On-Time Performance": np.random.uniform(0.80, 0.99),
                "Demand Forecast Accuracy": np.random.uniform(0.70, 0.95),
                "Inventory Accuracy": np.random.uniform(0.90, 0.999),
                "Stockout Frequency": np.random.uniform(0.01, 0.05),
                "Returns & Damage Rate": np.random.uniform(0.01, 0.08),
                "Distribution Center Productivity": np.random.uniform(50, 150),
                "Freight Utilization Efficiency": np.random.uniform(0.70, 0.95),
                "Customer Satisfaction Score (CSAT)": np.random.uniform(3.5, 5.0),
                "Net Promoter Score (NPS)": np.random.randint(-10, 90),
                "Procurement Cost Savings": np.random.uniform(0.02, 0.15),
                "Average Delivery Distance (miles)": np.random.uniform(50, 500),
                "Carbon Emissions per Shipment (kg CO2)": np.random.uniform(0.1, 1.5),
                "Labor Productivity Rate": np.random.uniform(0.8, 1.2),
                "Order Accuracy Rate": np.random.uniform(0.90, 0.995),
                "Supplier Defect Rate": np.random.uniform(0.001, 0.05),
                "Revenue per Distribution Center ($)": np.random.uniform(500000, 5000000),
                "Cost per Order Fulfillment ($)": np.random.uniform(10, 50),
                "Emergency Order Response Time (hours)": np.random.uniform(0.5, 4.0),
                "Fleet Downtime Rate": np.random.uniform(0.01, 0.10),
                "Employee Safety Incident Rate": np.random.uniform(0.001, 0.02),
                "Multi-Channel Order Fulfillment Efficiency": np.random.uniform(0.70, 0.95),
                "Distribution Network Efficiency Index": np.random.uniform(0.75, 0.98),
                "Average Delivery Time (hours)": np.random.uniform(8, 60),
                "Fuel Cost per Delivery ($)": np.random.uniform(18, 130),
                "Route Optimization Savings ($)": np.random.uniform(250, 7500),
                "Delivery Count": np.random.randint(15, 260),
                "Same-Day Delivery Success Rate": np.random.uniform(0.68, 0.98),
                "Shelf Detection Accuracy": np.random.uniform(0.88, 0.995),
                "Manual Count Reduction": np.random.uniform(0.25, 0.82),
                "Lost/Misplaced Inventory Value ($)": np.random.uniform(500, 42000),
                "Detected SKU Count": np.random.randint(300, 11000),
                "Inventory Variance Quantity": np.random.randint(-140, 190),
                "Pick/Pack Volume": np.random.randint(100, 5200),
                "Technical Search Success Rate": np.random.uniform(0.74, 0.98),
                "Average Product Search Time (seconds)": np.random.uniform(14, 95),
                "Self-Service Resolution Rate": np.random.uniform(0.52, 0.93),
                "Successful Matches": np.random.randint(80, 3400),
                "Search Volume": np.random.randint(250, 7200),
                "Search Drop-Off Rate": np.random.uniform(0.04, 0.42),
                "Supplier Catalog Processing Time (hours)": np.random.uniform(4, 72),
                "Product Data Standardization": np.random.uniform(0.62, 0.98),
                "Duplicate SKU Reduction": np.random.uniform(0.18, 0.78),
                "Product Classification Accuracy": np.random.uniform(0.78, 0.985),
                "Supplier Files": np.random.randint(1, 90),
                "Duplicate SKU Count": np.random.randint(0, 260),
                "Customer Churn Rate": np.random.uniform(0.02, 0.16),
                "At-Risk Account Count": np.random.randint(3, 95),
                "Repeat Purchase Rate": np.random.uniform(0.48, 0.91),
                "Revenue Retention": np.random.uniform(0.72, 0.98),
                "Predicted Churn Accounts": np.random.randint(5, 180),
                "Revenue Decline Rate": np.random.uniform(0.01, 0.22),
                "Customer Health Score": np.random.uniform(25, 98),
                "Retention Success Rate": np.random.uniform(0.35, 0.88),
                "Dynamic Pricing Margin Gain": np.random.uniform(0.01, 0.095),
                "Average Discount": np.random.uniform(0.03, 0.24),
                "Price Realization": np.random.uniform(0.78, 0.99),
                "Revenue Uplift from AI Pricing ($)": np.random.uniform(15000, 620000),
                "Gross Margin": np.random.uniform(0.18, 0.44),
                "Price Elasticity Score": np.random.uniform(-2.4, -0.15),
                "Price Change": np.random.uniform(-0.18, 0.22),
                "Commodity Price ($)": np.random.uniform(35, 420),
                "Commodity Price Variance": np.random.uniform(-0.12, 0.18),
                "Supplier Lead Time (days)": np.random.uniform(2, 28),
                "Purchase Forecast Accuracy": np.random.uniform(0.68, 0.96),
                "Forecast Spend ($)": np.random.uniform(150000, 4800000),
                "Purchase Timing Savings ($)": np.random.uniform(1000, 130000),
                "Predictive Maintenance Accuracy": np.random.uniform(0.72, 0.97),
                "Vehicle Failure Incidents": np.random.randint(0, 22),
                "Maintenance Cost per Vehicle ($)": np.random.uniform(850, 14500),
                "Fleet Health Score": np.random.uniform(58, 98),
                "Breakdown Count": np.random.randint(0, 30),
                "Maintenance Cost ($)": np.random.uniform(1500, 95000),
                "Delay Count": np.random.randint(1, 160),
                "Average Resolution Time (hours)": np.random.uniform(1.5, 42),
                "AI Bot Response Accuracy": np.random.uniform(0.72, 0.98),
                "First Contact Resolution": np.random.uniform(0.50, 0.92),
                "Customer Support Productivity Gain": np.random.uniform(0.10, 0.55),
                "Ticket Resolution Count": np.random.randint(20, 850),
                "Knowledge Query Count": np.random.randint(30, 3600),
                "Ticket Count": np.random.randint(15, 1500),
                "Tickets Resolved per Agent": np.random.uniform(8, 72),
                "Master Data Completeness": np.random.uniform(0.82, 0.995),
                "Duplicate Product Record": np.random.uniform(0.005, 0.085),
                "Data Validation Failure Rate": np.random.uniform(0.004, 0.065),
                "Data Freshness Compliance": np.random.uniform(0.78, 0.99),
                "Data Quality Score": np.random.uniform(0.76, 0.985),
                "Duplicate Record Count": np.random.randint(0, 360),
                "Missing Record Count": np.random.randint(0, 520),
                "Data Quality Issue Count": np.random.randint(1, 420),
                "Compliance Adherence": np.random.uniform(0.74, 0.99),
                "Open Risk Incidents": np.random.randint(0, 45),
                "Access Control Violations": np.random.randint(0, 28),
                "Audit Finding Closure Rate": np.random.uniform(0.55, 0.98),
                "Compliance Score": np.random.uniform(0.70, 0.995),
                "Risk Incident Count": np.random.randint(0, 65),
                "Violation Count": np.random.randint(0, 80),
                "Finding Count": np.random.randint(2, 170),
                "Cybersecurity Risk Score": np.random.uniform(0.04, 0.36),
            }
        )

    data = pd.DataFrame(rows)
    data["Date"] = pd.to_datetime(data["Date"])
    data["Month"] = data["Date"].dt.to_period("M").astype(str)
    data["Week"] = data["Date"].dt.to_period("W").astype(str)
    data["Day"] = data["Date"].dt.date.astype(str)
    data["Quarter"] = data["Date"].dt.to_period("Q").astype(str)
    return data


def format_metric(value: float, fmt: str) -> str:
    if pd.isna(value):
        return "No data"
    if fmt == "percent":
        return f"{value:.1%}"
    if fmt == "currency":
        return f"${value:,.2f}"
    if fmt == "currency_compact":
        return f"${value / 1_000_000:.2f}M"
    if fmt == "days":
        return f"{value:.1f} days"
    if fmt == "hours":
        return f"{value:.1f} hrs"
    if fmt == "miles":
        return f"{value:.0f} mi"
    if fmt == "kg":
        return f"{value:.2f} kg"
    if fmt == "score":
        return f"{value:.2f}/5"
    if fmt == "rate":
        return f"{value:.3f}"
    if fmt == "x":
        return f"{value:.1f}x"
    return f"{value:,.1f}"


def format_delta(delta: float, fmt: str) -> str:
    if pd.isna(delta):
        return "0"
    if fmt == "percent":
        return f"{delta:.1%}"
    if fmt == "currency_compact":
        return f"${delta / 1_000_000:.2f}M"
    if fmt == "currency":
        return f"${delta:,.2f}"
    if fmt in {"days", "hours"}:
        return f"{delta:.1f}"
    return f"{delta:,.2f}"


def apply_chart_theme(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=22, r=22, t=64, b=42),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#18202f"),
        title=dict(font=dict(size=18, color="#18202f"), x=0.02, xanchor="left"),
        hoverlabel=dict(bgcolor="white", bordercolor="#d8e1ec", font_size=13, font_family="Inter"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(gridcolor="rgba(24,32,47,0.07)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(24,32,47,0.07)", zeroline=False)
    return fig


def metric_direction(kpi_name: str, delta: float) -> str:
    higher_is_better = KPI_COLUMNS[kpi_name][2]
    return "normal" if higher_is_better else "inverse"


def ensure_date_range(value) -> tuple[date, date]:
    if isinstance(value, tuple) and len(value) == 2:
        return value
    return df["Date"].min().date(), df["Date"].max().date()


df = generate_synthetic_data()


# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")
selected_region = st.sidebar.multiselect(
    "Region",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique()),
)
selected_industry = st.sidebar.multiselect(
    "Industry",
    options=sorted(df["Industry"].unique()),
    default=sorted(df["Industry"].unique()),
)
dc_mode = st.sidebar.radio(
    "Distribution center scope",
    ["Top revenue DCs", "Manual selection", "All DCs"],
    horizontal=False,
)

if dc_mode == "Top revenue DCs":
    dc_count = st.sidebar.slider("Number of DCs", min_value=5, max_value=40, value=15, step=5)
    selected_dc = (
        df.groupby("Distribution Center")["Revenue per Distribution Center ($)"]
        .sum()
        .nlargest(dc_count)
        .index.tolist()
    )
elif dc_mode == "Manual selection":
    selected_dc = st.sidebar.multiselect(
        "Distribution centers",
        options=sorted(df["Distribution Center"].unique()),
        default=sorted(df["Distribution Center"].unique())[:10],
    )
else:
    selected_dc = sorted(df["Distribution Center"].unique())

date_range = ensure_date_range(
    st.sidebar.date_input(
        "Date range",
        value=(df["Date"].min().date(), df["Date"].max().date()),
        min_value=df["Date"].min().date(),
        max_value=df["Date"].max().date(),
    )
)

focus_kpi = st.sidebar.selectbox("Highlighted KPI", options=list(KPI_DEFINITIONS), index=0)
minimum_otd = st.sidebar.slider("Minimum OTD threshold", 0.80, 0.99, 0.90, 0.01)
show_detail_table = st.sidebar.toggle("Show filtered records", value=False)


# --- FILTER DATA ---
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered_df = df[
    (df["Region"].isin(selected_region))
    & (df["Industry"].isin(selected_industry))
    & (df["Distribution Center"].isin(selected_dc))
    & (df["Date"] >= start_date)
    & (df["Date"] <= end_date)
    & (df["On-Time Delivery Rate"] >= minimum_otd)
].copy()

if filtered_df.empty:
    st.warning("No records match the current filters. Loosen the threshold or selection to restore the dashboard.")
    st.stop()


# --- MAIN DASHBOARD ---
st.title("SupplyOne | Wholesale Distribution Dashboard")
st.markdown(
    """
    <div class="hero-note">
    Leading wholesale distribution across the U.S. and Canada for multifamily, institutional,
    hospitality, trades, government housing, healthcare, building services, and education customers.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "".join(
        [
            f'<span class="filter-pill">{len(filtered_df):,} records</span>',
            f'<span class="filter-pill">{filtered_df["Distribution Center"].nunique()} DCs</span>',
            f'<span class="filter-pill">{filtered_df["Date"].min().date()} to {filtered_df["Date"].max().date()}</span>',
            f'<span class="filter-pill">OTD >= {minimum_otd:.0%}</span>',
        ]
    ),
    unsafe_allow_html=True,
)


# --- TOP KPIS ---
cols = st.columns(5)
for index, kpi_name in enumerate(CORE_KPIS):
    source_col, fmt, _ = KPI_COLUMNS[kpi_name]
    current_value = filtered_df[source_col].mean()
    baseline_value = df[source_col].mean()
    delta = current_value - baseline_value
    with cols[index]:
        st.metric(
            kpi_name,
            format_metric(current_value, fmt),
            delta=format_delta(delta, fmt),
            delta_color=metric_direction(kpi_name, delta),
            help=KPI_DEFINITIONS[kpi_name],
        )


# --- INSIGHTS ---
focus_col, focus_fmt, focus_higher_better = KPI_COLUMNS[focus_kpi]
best_dc = filtered_df.groupby("Distribution Center")[focus_col].mean().sort_values(ascending=not focus_higher_better).head(1)
watch_dc = filtered_df.groupby("Distribution Center")[focus_col].mean().sort_values(ascending=focus_higher_better).head(1)
industry_leader = filtered_df.groupby("Industry")[focus_col].mean().sort_values(ascending=not focus_higher_better).head(1)

insight_cols = st.columns(3)
with insight_cols[0]:
    st.markdown(
        f"""
        <div class="insight-card">
            <b>Highlighted KPI</b>
            <span>{focus_kpi}: {format_metric(filtered_df[focus_col].mean(), focus_fmt)} average across current filters.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with insight_cols[1]:
    st.markdown(
        f"""
        <div class="insight-card">
            <b>Best DC</b>
            <span>{best_dc.index[0]} leads at {format_metric(best_dc.iloc[0], focus_fmt)}.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with insight_cols[2]:
    st.markdown(
        f"""
        <div class="insight-card">
            <b>Watch area</b>
            <span>{watch_dc.index[0]} needs attention at {format_metric(watch_dc.iloc[0], focus_fmt)}. Strongest industry: {industry_leader.index[0]}.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- TABBED ANALYSIS CENTER ---
def render_kpi_strip(kpis: list[tuple[str, str, str, str]]) -> None:
    cols = st.columns(4)
    for col, (label, source_col, agg, fmt) in zip(cols, kpis):
        if agg == "sum":
            value = filtered_df[source_col].sum()
        elif agg == "count":
            value = filtered_df[source_col].nunique()
        else:
            value = filtered_df[source_col].mean()
        with col:
            st.metric(label, format_metric(value, fmt))


def render_takeaway(message: str) -> None:
    st.markdown(f'<div class="takeaway">Key Takeaway: {message}</div>', unsafe_allow_html=True)


def plot_two_columns(
    left_fig: go.Figure,
    right_fig: go.Figure,
    left_takeaway: str | None = None,
    right_takeaway: str | None = None,
    height: int = 430,
) -> None:
    def fallback_takeaway(fig: go.Figure) -> str:
        title = fig.layout.title.text or "this chart"
        return f"Use {title.lower()} to spot trends, exceptions, and outliers that need business follow-up."

    left, right = st.columns(2)
    with left:
        st.plotly_chart(apply_chart_theme(left_fig, height), width="stretch")
        render_takeaway(left_takeaway or fallback_takeaway(left_fig))
    with right:
        st.plotly_chart(apply_chart_theme(right_fig, height), width="stretch")
        render_takeaway(right_takeaway or fallback_takeaway(right_fig))


tab_names = [
    "Executive Summary",
    "Data QC",
    "GRC Status",
    "Supply Chain Command Center",
    "Logistics & Route Optimization",
    "Warehouse Automation & Inventory Intelligence",
    "B2B Customer Experience & Smart Search",
    "Smart Product Catalog & Supplier Data",
    "Customer Retention & Churn Analytics",
    "Dynamic Pricing & Margin Optimization",
    "Procurement & Commodity Intelligence",
    "Fleet Maintenance & Delivery Reliability",
    "AI Knowledge Assistant & Service Operations",
]

tabs = st.tabs(tab_names)

with tabs[0]:
    st.subheader("Enterprise AI Command Center")
    st.markdown(
        """
        The proposed analytics and AI-driven command center gives leadership enterprise-wide visibility into supply chain performance,
        customer behavior, warehouse operations, procurement efficiency, pricing optimization, and governance controls.
        It supports a shift from reactive decision-making to proactive and predictive operations management.
        """
    )
    render_kpi_strip(
        [
            ("Network Efficiency", "Distribution Network Efficiency Index", "mean", "percent"),
            ("Revenue Retention", "Revenue Retention", "mean", "percent"),
            ("Gross Margin", "Gross Margin", "mean", "percent"),
            ("Open Risk Incidents", "Open Risk Incidents", "sum", "number"),
        ]
    )
    risk_cols = st.columns(3)
    with risk_cols[0]:
        st.markdown(
            """
            <div class="risk-panel high">
                <b>Business Exceptions</b>
                <span>Centralize monitoring for stockouts, delivery delays, churn signals, price leakage, and excess inventory carrying cost.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with risk_cols[1]:
        st.markdown(
            """
            <div class="risk-panel high">
                <b>Cybersecurity Risks</b>
                <span>Track access violations, privileged-role drift, dormant accounts, MFA exceptions, and audit findings in one control layer.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with risk_cols[2]:
        st.markdown(
            """
            <div class="risk-panel">
                <b>Data Quality Risks</b>
                <span>Monitor master-data completeness, duplicate products, failed validations, stale records, and supplier catalog quality.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    impact = pd.DataFrame(
        {
            "Impact Area": ["Operational", "Financial", "Customer Experience", "Strategic"],
            "Expected Value": [
                "Fewer critical stockouts, faster warehouse work, optimized routing, and lower fleet downtime.",
                "Higher gross margin, lower procurement cost, reduced holding cost, and stronger revenue retention.",
                "Faster product discovery, better fulfillment, improved support resolution, and repeat business.",
                "Better enterprise visibility, stronger governance, scalable AI operations, and competitive advantage.",
            ],
            "Risk Level": ["High", "High", "Medium", "Medium"],
        }
    )
    st.dataframe(impact, width="stretch", hide_index=True)

    roadmap_cols = st.columns(3)
    roadmap_cards = [
        ("0-3 Months", "Build centralized operational dashboards, standardize master data, launch data quality monitoring, identify stockout SKUs and high-delay routes, and define KPI ownership."),
        ("6-9 Months", "Deploy ML demand forecasting, route optimization, AI technical search, supplier catalog enrichment, predictive fleet maintenance, dynamic pricing, and automated risk alerts."),
        ("9-12 Months", "Scale AI across distribution centers, launch the enterprise knowledge assistant, enable autonomous replenishment, add commodity forecasting, and formalize model governance."),
    ]
    for col, (title, body) in zip(roadmap_cols, roadmap_cards):
        with col:
            st.markdown(f'<div class="roadmap-card"><b>{title}</b><span>{body}</span></div>', unsafe_allow_html=True)

    summary_month = filtered_df.groupby("Month", as_index=False).agg(
        {
            "Distribution Network Efficiency Index": "mean",
            "Gross Margin": "mean",
            "Revenue Retention": "mean",
            "Compliance Adherence": "mean",
        }
    )
    summary_long = summary_month.melt("Month", var_name="Metric", value_name="Value")
    exception = filtered_df.groupby("Business Function", as_index=False).agg(
        {
            "Open Risk Incidents": "sum",
            "Access Control Violations": "sum",
            "Data Quality Issue Count": "sum",
        }
    )
    exception["Total Exceptions"] = exception[["Open Risk Incidents", "Access Control Violations", "Data Quality Issue Count"]].sum(axis=1)
    fig1 = px.line(summary_long, x="Month", y="Value", color="Metric", markers=True, title="Enterprise Performance and Control Trend", color_discrete_sequence=ACCENT_SCALE)
    fig1.update_yaxes(tickformat=".0%")
    fig1.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Month: %{x}<br>Value: %{y:.1%}<extra></extra>")
    fig2 = px.bar(exception.sort_values("Total Exceptions", ascending=False), x="Business Function", y="Total Exceptions", color="Total Exceptions", title="Centralized Exception Monitoring by Function", color_continuous_scale="OrRd")
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>Exceptions: %{y:,.0f}<extra></extra>")
    plot_two_columns(
        fig1,
        fig2,
        "Leadership can track operating performance and governance posture together instead of reviewing separate reports.",
        "Functions with the most exceptions need centralized controls, ownership, and faster remediation.",
    )

with tabs[1]:
    render_kpi_strip(
        [
            ("Master Data Completeness", "Master Data Completeness", "mean", "percent"),
            ("Duplicate Product Record", "Duplicate Product Record", "mean", "percent"),
            ("Data Validation Failure Rate", "Data Validation Failure Rate", "mean", "percent"),
            ("Data Freshness Compliance", "Data Freshness Compliance", "mean", "percent"),
        ]
    )
    dq_score = filtered_df.groupby("Month", as_index=False)["Data Quality Score"].mean()
    dq_duplicate = filtered_df.groupby("Data Domain", as_index=False)["Duplicate Record Count"].sum().sort_values("Duplicate Record Count", ascending=False)
    fig1 = px.line(dq_score, x="Month", y="Data Quality Score", markers=True, title="Data Quality Score Trend", color_discrete_sequence=["#0067B1"])
    fig1.update_yaxes(tickformat=".0%")
    fig1.update_traces(hovertemplate="Month: %{x}<br>Data quality score: %{y:.1%}<extra></extra>")
    fig2 = px.bar(dq_duplicate, x="Data Domain", y="Duplicate Record Count", title="Duplicate Records by Data Domain", color="Duplicate Record Count", color_continuous_scale="OrRd")
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>Duplicate records: %{y:,.0f}<extra></extra>")
    plot_two_columns(
        fig1,
        fig2,
        "A declining score signals that master-data controls should be reviewed before operational reports lose trust.",
        "The tallest orange and red bars show which data domains need duplicate cleanup first.",
    )

    missing = filtered_df.groupby("Mandatory Field Name", as_index=False)["Missing Record Count"].sum().sort_values("Missing Record Count", ascending=False)
    issue_dist = filtered_df.groupby("Data Quality Issue Type", as_index=False)["Data Quality Issue Count"].sum()
    fig3 = px.bar(missing, x="Mandatory Field Name", y="Missing Record Count", title="Missing Critical Fields Analysis", color="Missing Record Count", color_continuous_scale="Oranges")
    fig3.update_traces(hovertemplate="<b>%{x}</b><br>Missing records: %{y:,.0f}<extra></extra>")
    fig4 = px.pie(issue_dist, names="Data Quality Issue Type", values="Data Quality Issue Count", hole=0.5, title="Data Quality Issue Distribution", color_discrete_sequence=["#dc2626", "#f97316", "#f59e0b", "#0067B1", "#00A3A3", "#6B4EFF"])
    fig4.update_traces(hovertemplate="<b>%{label}</b><br>Issues: %{value:,.0f}<br>Share: %{percent}<extra></extra>")
    plot_two_columns(
        fig3,
        fig4,
        "Missing mandatory fields create downstream reporting, fulfillment, pricing, and compliance risk.",
        "The largest issue slices identify where data stewards should focus remediation and control checks.",
    )

with tabs[2]:
    render_kpi_strip(
        [
            ("Compliance Adherence", "Compliance Adherence", "mean", "percent"),
            ("Open Risk Incidents", "Open Risk Incidents", "sum", "number"),
            ("Access Control Violations", "Access Control Violations", "sum", "number"),
            ("Audit Finding Closure Rate", "Audit Finding Closure Rate", "mean", "percent"),
        ]
    )
    compliance = filtered_df.pivot_table(index="Month", columns="Business Function", values="Compliance Score", aggfunc="mean")
    risk = filtered_df.groupby("Month", as_index=False)["Risk Incident Count"].sum()
    fig1 = px.imshow(compliance, text_auto=".0%", aspect="auto", color_continuous_scale="RdYlGn", title="Compliance Status by Business Function")
    fig1.update_traces(hovertemplate="Month: %{y}<br>Function: %{x}<br>Compliance score: %{z:.1%}<extra></extra>")
    fig2 = px.line(risk, x="Month", y="Risk Incident Count", markers=True, title="Risk Incident Trend", color_discrete_sequence=["#dc2626"])
    fig2.update_traces(hovertemplate="Month: %{x}<br>Risk incidents: %{y:,.0f}<extra></extra>")
    plot_two_columns(
        fig1,
        fig2,
        "Red cells show business functions where compliance adherence is below the desired control threshold.",
        "A rising incident trend means leadership should tighten monitoring and accelerate remediation.",
    )

    violations = filtered_df.groupby("Violation Type", as_index=False)["Violation Count"].sum().sort_values("Violation Count", ascending=False)
    findings = filtered_df.groupby("Audit Finding Status", as_index=False)["Finding Count"].sum()
    fig3 = px.bar(violations, x="Violation Type", y="Violation Count", title="User Access Violation Analysis", color="Violation Count", color_continuous_scale="Reds")
    fig3.update_traces(hovertemplate="<b>%{x}</b><br>Violations: %{y:,.0f}<extra></extra>")
    fig4 = px.funnel(findings, x="Finding Count", y="Audit Finding Status", title="Audit Findings Closure Progress", color_discrete_sequence=["#dc2626"])
    fig4.update_traces(hovertemplate="<b>%{y}</b><br>Findings: %{x:,.0f}<extra></extra>")
    plot_two_columns(
        fig3,
        fig4,
        "Privileged access, dormant users, and role drift should be handled as cybersecurity control priorities.",
        "Open and remediation-stage findings need clear owners and closure dates to improve audit readiness.",
    )

with tabs[3]:
    render_kpi_strip(
        [
            ("Demand Forecast Accuracy", "Demand Forecast Accuracy", "mean", "percent"),
            ("Stockout Rate", "Stockout Frequency", "mean", "percent"),
            ("Inventory Holding Cost", "Inventory Holding Cost ($)", "sum", "currency_compact"),
            ("Distribution Center Fill Rate", "Fill Rate", "mean", "percent"),
        ]
    )
    monthly_demand = filtered_df.groupby("Month", as_index=False)[["Forecast Demand Units", "Actual Demand Units"]].sum()
    stockout_category = filtered_df.groupby("Product Category", as_index=False)["Stockout Count"].sum().sort_values("Stockout Count", ascending=False)
    fig1 = px.line(monthly_demand, x="Month", y=["Forecast Demand Units", "Actual Demand Units"], markers=True, title="Forecast vs Actual Demand", color_discrete_sequence=ACCENT_SCALE)
    fig1.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Month: %{x}<br>Units: %{y:,.0f}<extra></extra>")
    fig2 = px.bar(stockout_category, x="Product Category", y="Stockout Count", title="Critical SKU Stockout Analysis", color="Stockout Count", color_continuous_scale="Reds")
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>Stockouts: %{y:,.0f}<extra></extra>")
    plot_two_columns(fig1, fig2)

    aging = filtered_df.groupby(["Aging Bucket", "Distribution Center"], as_index=False)["Inventory Value ($)"].sum()
    top_dcs = filtered_df.groupby("Distribution Center")["Inventory Value ($)"].sum().nlargest(6).index
    aging = aging[aging["Distribution Center"].isin(top_dcs)]
    safety = filtered_df.groupby("Month", as_index=False)["Safety Stock Quantity"].sum()
    fig3 = px.bar(aging, x="Aging Bucket", y="Inventory Value ($)", color="Distribution Center", title="Inventory Aging by Distribution Center", color_discrete_sequence=px.colors.qualitative.Set2)
    fig3.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Bucket: %{x}<br>Value: $%{y:,.0f}<extra></extra>")
    fig4 = px.area(safety, x="Month", y="Safety Stock Quantity", title="Safety Stock Optimization Trend", color_discrete_sequence=["#00A3A3"])
    fig4.update_traces(hovertemplate="Month: %{x}<br>Safety stock: %{y:,.0f}<extra></extra>")
    plot_two_columns(fig3, fig4)

with tabs[4]:
    render_kpi_strip(
        [
            ("On-Time Delivery", "On-Time Delivery Rate", "mean", "percent"),
            ("Average Delivery Time", "Average Delivery Time (hours)", "mean", "hours"),
            ("Fuel Cost per Delivery", "Fuel Cost per Delivery ($)", "mean", "currency"),
            ("Route Optimization Savings", "Route Optimization Savings ($)", "sum", "currency_compact"),
        ]
    )
    heat = filtered_df.pivot_table(index="Month", columns="Region", values="On-Time Delivery Rate", aggfunc="mean")
    fig1 = px.imshow(heat, text_auto=".1%", aspect="auto", color_continuous_scale="YlGnBu", title="Delivery Performance by Region")
    fig1.update_traces(hovertemplate="Month: %{y}<br>Region: %{x}<br>OTD: %{z:.1%}<extra></extra>")
    route = filtered_df.groupby("Delivery Route", as_index=False).agg({"Average Delivery Distance (miles)": "mean", "Delivery Count": "sum", "Route Optimization Savings ($)": "sum"})
    fig2 = px.scatter(route, x="Average Delivery Distance (miles)", y="Delivery Count", size="Route Optimization Savings ($)", color="Delivery Route", title="Route Efficiency Analysis", color_discrete_sequence=px.colors.qualitative.Bold)
    fig2.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Distance: %{x:.0f} mi<br>Deliveries: %{y:,.0f}<extra></extra>")
    plot_two_columns(fig1, fig2)

    fuel = filtered_df.groupby("Month", as_index=False)["Fuel Cost per Delivery ($)"].sum()
    same_day = filtered_df.groupby("Month", as_index=False)["Same-Day Delivery Success Rate"].mean()
    fig3 = px.line(fuel, x="Month", y="Fuel Cost per Delivery ($)", markers=True, title="Fuel Consumption Trend", color_discrete_sequence=["#D83B01"])
    fig3.update_traces(hovertemplate="Month: %{x}<br>Fuel cost: $%{y:,.0f}<extra></extra>")
    fig4 = px.area(same_day, x="Month", y="Same-Day Delivery Success Rate", title="Same-Day Delivery Success Rate", color_discrete_sequence=["#18864B"])
    fig4.update_yaxes(tickformat=".0%")
    fig4.update_traces(hovertemplate="Month: %{x}<br>Success: %{y:.1%}<extra></extra>")
    plot_two_columns(fig3, fig4)

with tabs[5]:
    render_kpi_strip(
        [
            ("Inventory Accuracy", "Inventory Accuracy", "mean", "percent"),
            ("Shelf Detection Accuracy", "Shelf Detection Accuracy", "mean", "percent"),
            ("Manual Count Reduction", "Manual Count Reduction", "mean", "percent"),
            ("Lost/Misplaced Inventory Value", "Lost/Misplaced Inventory Value ($)", "sum", "currency_compact"),
        ]
    )
    detection = filtered_df.groupby("Week", as_index=False)["Detected SKU Count"].sum().tail(26)
    variance = filtered_df.groupby("Distribution Center", as_index=False)["Inventory Variance Quantity"].sum().sort_values("Inventory Variance Quantity", key=lambda s: s.abs(), ascending=False).head(15)
    fig1 = px.line(detection, x="Week", y="Detected SKU Count", markers=True, title="Computer Vision Inventory Detection Trend", color_discrete_sequence=["#0067B1"])
    fig1.update_traces(hovertemplate="Week: %{x}<br>Detected SKUs: %{y:,.0f}<extra></extra>")
    fig2 = px.bar(variance, x="Distribution Center", y="Inventory Variance Quantity", title="Inventory Variance Analysis", color="Inventory Variance Quantity", color_continuous_scale="RdBu")
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>Variance qty: %{y:,.0f}<extra></extra>")
    plot_two_columns(fig1, fig2)

    productivity = filtered_df.pivot_table(index="Warehouse Zone", columns="Distribution Center", values="Pick/Pack Volume", aggfunc="sum")
    productivity = productivity[filtered_df.groupby("Distribution Center")["Pick/Pack Volume"].sum().nlargest(8).index]
    loss = filtered_df.groupby("Month", as_index=False)["Lost/Misplaced Inventory Value ($)"].sum()
    fig3 = px.imshow(productivity, aspect="auto", color_continuous_scale="Viridis", title="Warehouse Productivity Analysis")
    fig3.update_traces(hovertemplate="Zone: %{y}<br>Warehouse: %{x}<br>Volume: %{z:,.0f}<extra></extra>")
    fig4 = px.bar(loss, x="Month", y="Lost/Misplaced Inventory Value ($)", title="Item Loss Trend", color_discrete_sequence=["#7A5C00"])
    fig4.update_traces(hovertemplate="Month: %{x}<br>Lost value: $%{y:,.0f}<extra></extra>")
    plot_two_columns(fig3, fig4)

with tabs[6]:
    render_kpi_strip(
        [
            ("Technical Search Success Rate", "Technical Search Success Rate", "mean", "percent"),
            ("Average Product Search Time", "Average Product Search Time (seconds)", "mean", "number"),
            ("Customer Satisfaction Score", "Customer Satisfaction Score (CSAT)", "mean", "score"),
            ("Self-Service Resolution Rate", "Self-Service Resolution Rate", "mean", "percent"),
        ]
    )
    query = filtered_df.groupby("Query Type", as_index=False)["Successful Matches"].sum().sort_values("Successful Matches", ascending=False)
    daily_search = filtered_df.groupby("Day", as_index=False)["Search Volume"].sum().tail(90)
    fig1 = px.bar(query, x="Query Type", y="Successful Matches", title="Search Query Success Analysis", color="Query Type", color_discrete_sequence=ACCENT_SCALE)
    fig1.update_traces(hovertemplate="<b>%{x}</b><br>Matches: %{y:,.0f}<extra></extra>")
    fig2 = px.line(daily_search, x="Day", y="Search Volume", title="Product Search Trend", color_discrete_sequence=["#0067B1"])
    fig2.update_traces(hovertemplate="Day: %{x}<br>Searches: %{y:,.0f}<extra></extra>")
    plot_two_columns(fig1, fig2)

    top_search = filtered_df.groupby("Product Category", as_index=False)["Search Volume"].sum()
    abandon = filtered_df.groupby("Search Stage", as_index=False)["Search Drop-Off Rate"].mean()
    fig3 = px.treemap(top_search, path=["Product Category"], values="Search Volume", color="Search Volume", color_continuous_scale="Blues", title="Top Searched Product Categories")
    fig3.update_traces(hovertemplate="<b>%{label}</b><br>Searches: %{value:,.0f}<extra></extra>")
    fig4 = px.funnel(abandon, x="Search Drop-Off Rate", y="Search Stage", title="Customer Search Abandonment Analysis", color_discrete_sequence=["#D83B01"])
    fig4.update_traces(hovertemplate="<b>%{y}</b><br>Drop-off: %{x:.1%}<extra></extra>")
    plot_two_columns(fig3, fig4)

with tabs[7]:
    render_kpi_strip(
        [
            ("Supplier Catalog Processing Time", "Supplier Catalog Processing Time (hours)", "mean", "hours"),
            ("Product Data Standardization", "Product Data Standardization", "mean", "percent"),
            ("Duplicate SKU Reduction", "Duplicate SKU Reduction", "mean", "percent"),
            ("Product Classification Accuracy", "Product Classification Accuracy", "mean", "percent"),
        ]
    )
    upload = filtered_df.groupby("Month", as_index=False)["Supplier Files"].sum()
    category_accuracy = filtered_df.groupby("Product Category", as_index=False)["Product Classification Accuracy"].mean()
    fig1 = px.line(upload, x="Month", y="Supplier Files", markers=True, title="Supplier Data Upload Trend", color_discrete_sequence=["#0067B1"])
    fig1.update_traces(hovertemplate="Month: %{x}<br>Supplier files: %{y:,.0f}<extra></extra>")
    fig2 = px.bar(category_accuracy, x="Product Category", y="Product Classification Accuracy", title="Automated Product Categorization Accuracy", color="Product Classification Accuracy", color_continuous_scale="YlGnBu")
    fig2.update_yaxes(tickformat=".0%")
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>Accuracy: %{y:.1%}<extra></extra>")
    plot_two_columns(fig1, fig2)

    duplicates = filtered_df.groupby("Supplier Name", as_index=False)["Duplicate SKU Count"].sum().sort_values("Duplicate SKU Count", ascending=False)
    enrichment = filtered_df.groupby("Enrichment Stage", as_index=False)["Product Category"].count().rename(columns={"Product Category": "Product Count"})
    fig3 = px.bar(duplicates, x="Supplier Name", y="Duplicate SKU Count", title="Duplicate Product Detection Analysis", color="Duplicate SKU Count", color_continuous_scale="Oranges")
    fig3.update_traces(hovertemplate="<b>%{x}</b><br>Duplicate SKUs: %{y:,.0f}<extra></extra>")
    fig4 = px.funnel(enrichment, x="Product Count", y="Enrichment Stage", title="Catalog Enrichment Status", color_discrete_sequence=["#00A3A3"])
    fig4.update_traces(hovertemplate="<b>%{y}</b><br>Products: %{x:,.0f}<extra></extra>")
    plot_two_columns(fig3, fig4)

with tabs[8]:
    render_kpi_strip(
        [
            ("Customer Churn Rate", "Customer Churn Rate", "mean", "percent"),
            ("At-Risk Account Count", "At-Risk Account Count", "sum", "number"),
            ("Repeat Purchase Rate", "Repeat Purchase Rate", "mean", "percent"),
            ("Revenue Retention", "Revenue Retention", "mean", "percent"),
        ]
    )
    churn = filtered_df.groupby("Month", as_index=False)["Predicted Churn Accounts"].sum()
    decline = filtered_df.groupby(["Customer Segment", "Region"], as_index=False)["Revenue Decline Rate"].mean()
    fig1 = px.line(churn, x="Month", y="Predicted Churn Accounts", markers=True, title="Churn Prediction Trend", color_discrete_sequence=["#D83B01"])
    fig1.update_traces(hovertemplate="Month: %{x}<br>Predicted churn accounts: %{y:,.0f}<extra></extra>")
    fig2 = px.bar(decline, x="Customer Segment", y="Revenue Decline Rate", color="Region", title="Revenue Decline by Customer Segment", color_discrete_map=REGION_COLORS)
    fig2.update_yaxes(tickformat=".0%")
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:.1%}<extra></extra>")
    plot_two_columns(fig1, fig2)

    intervention = filtered_df.groupby("Intervention Type", as_index=False)["Retention Success Rate"].mean().sort_values("Retention Success Rate", ascending=False)
    fig3 = px.histogram(filtered_df, x="Customer Health Score", nbins=18, title="Customer Health Score Distribution", color_discrete_sequence=["#0067B1"])
    fig3.update_traces(hovertemplate="Health score range: %{x}<br>Customers: %{y:,.0f}<extra></extra>")
    fig4 = px.bar(intervention, x="Intervention Type", y="Retention Success Rate", title="Sales Intervention Success Analysis", color="Retention Success Rate", color_continuous_scale="Greens")
    fig4.update_yaxes(tickformat=".0%")
    fig4.update_traces(hovertemplate="<b>%{x}</b><br>Retention success: %{y:.1%}<extra></extra>")
    plot_two_columns(fig3, fig4)

with tabs[9]:
    render_kpi_strip(
        [
            ("Dynamic Pricing Margin Gain", "Dynamic Pricing Margin Gain", "mean", "percent"),
            ("Average Discount", "Average Discount", "mean", "percent"),
            ("Price Realization", "Price Realization", "mean", "percent"),
            ("Revenue Uplift from AI Pricing", "Revenue Uplift from AI Pricing ($)", "sum", "currency_compact"),
        ]
    )
    margin = filtered_df.groupby("Month", as_index=False)["Gross Margin"].mean()
    elasticity = filtered_df.groupby("Customer Segment", as_index=False)["Price Elasticity Score"].mean()
    fig1 = px.line(margin, x="Month", y="Gross Margin", markers=True, title="Margin Optimization Trend", color_discrete_sequence=["#18864B"])
    fig1.update_yaxes(tickformat=".0%")
    fig1.update_traces(hovertemplate="Month: %{x}<br>Gross margin: %{y:.1%}<extra></extra>")
    fig2 = px.scatter(elasticity, x="Customer Segment", y="Price Elasticity Score", size=np.abs(elasticity["Price Elasticity Score"]), title="Price Sensitivity by Customer Segment", color="Customer Segment", color_discrete_sequence=ACCENT_SCALE)
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>Elasticity score: %{y:.2f}<extra></extra>")
    plot_two_columns(fig1, fig2)

    uplift = filtered_df.groupby("Quarter", as_index=False)["Revenue Uplift from AI Pricing ($)"].sum()
    fig3 = px.box(filtered_df, x="Product Category", y="Price Change", color="Product Category", title="Dynamic Price Change Analysis", color_discrete_sequence=px.colors.qualitative.Safe)
    fig3.update_yaxes(tickformat=".0%")
    fig3.update_traces(hovertemplate="<b>%{x}</b><br>Price change: %{y:.1%}<extra></extra>")
    fig4 = px.area(uplift, x="Quarter", y="Revenue Uplift from AI Pricing ($)", title="Revenue Impact of Pricing Strategy", color_discrete_sequence=["#6B4EFF"])
    fig4.update_traces(hovertemplate="Quarter: %{x}<br>Revenue uplift: $%{y:,.0f}<extra></extra>")
    plot_two_columns(fig3, fig4)

with tabs[10]:
    render_kpi_strip(
        [
            ("Procurement Cost Savings", "Procurement Cost Savings", "mean", "percent"),
            ("Commodity Price Variance", "Commodity Price Variance", "mean", "percent"),
            ("Supplier Lead Time", "Supplier Lead Time (days)", "mean", "days"),
            ("Purchase Forecast Accuracy", "Purchase Forecast Accuracy", "mean", "percent"),
        ]
    )
    commodity = filtered_df.groupby(["Month", "Commodity"], as_index=False)["Commodity Price ($)"].mean()
    lead_time = filtered_df.groupby("Supplier Name", as_index=False)["Supplier Lead Time (days)"].mean().sort_values("Supplier Lead Time (days)", ascending=False)
    fig1 = px.line(commodity, x="Month", y="Commodity Price ($)", color="Commodity", markers=True, title="Commodity Price Trend Analysis", color_discrete_sequence=px.colors.qualitative.Bold)
    fig1.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Month: %{x}<br>Price: $%{y:,.2f}<extra></extra>")
    fig2 = px.bar(lead_time, x="Supplier Name", y="Supplier Lead Time (days)", title="Supplier Lead Time Comparison", color="Supplier Lead Time (days)", color_continuous_scale="Oranges")
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>Lead time: %{y:.1f} days<extra></extra>")
    plot_two_columns(fig1, fig2)

    spend = filtered_df.groupby("Quarter", as_index=False)["Forecast Spend ($)"].sum()
    purchase = filtered_df.groupby("Month", as_index=False)["Purchase Timing Savings ($)"].sum()
    fig3 = px.area(spend, x="Quarter", y="Forecast Spend ($)", title="Procurement Spend Forecast", color_discrete_sequence=["#0067B1"])
    fig3.update_traces(hovertemplate="Quarter: %{x}<br>Forecast spend: $%{y:,.0f}<extra></extra>")
    fig4 = px.bar(purchase, x="Month", y="Purchase Timing Savings ($)", title="Purchase Timing Optimization Analysis", color_discrete_sequence=["#18864B"])
    fig4.update_traces(hovertemplate="Purchase month: %{x}<br>Savings: $%{y:,.0f}<extra></extra>")
    plot_two_columns(fig3, fig4)

with tabs[11]:
    render_kpi_strip(
        [
            ("Fleet Downtime", "Fleet Downtime Rate", "mean", "percent"),
            ("Predictive Maintenance Accuracy", "Predictive Maintenance Accuracy", "mean", "percent"),
            ("Vehicle Failure Incidents", "Vehicle Failure Incidents", "sum", "number"),
            ("Maintenance Cost per Vehicle", "Maintenance Cost per Vehicle ($)", "mean", "currency"),
        ]
    )
    fleet = filtered_df.groupby("Month", as_index=False)["Fleet Health Score"].mean()
    breakdown = filtered_df.groupby("Vehicle Type", as_index=False)["Breakdown Count"].sum().sort_values("Breakdown Count", ascending=False)
    fig1 = px.line(fleet, x="Month", y="Fleet Health Score", markers=True, title="Fleet Health Monitoring Trend", color_discrete_sequence=["#0067B1"])
    fig1.update_traces(hovertemplate="Month: %{x}<br>Fleet health score: %{y:.1f}<extra></extra>")
    fig2 = px.bar(breakdown, x="Vehicle Type", y="Breakdown Count", title="Breakdown Analysis by Vehicle Type", color="Breakdown Count", color_continuous_scale="Reds")
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>Breakdowns: %{y:,.0f}<extra></extra>")
    plot_two_columns(fig1, fig2)

    maintenance = filtered_df.groupby("Maintenance Type", as_index=False)["Maintenance Cost ($)"].sum()
    delay = filtered_df.groupby("Delay Reason", as_index=False)["Delay Count"].sum().sort_values("Delay Count", ascending=False)
    delay["Cumulative %"] = delay["Delay Count"].cumsum() / delay["Delay Count"].sum()
    fig3 = px.pie(maintenance, names="Maintenance Type", values="Maintenance Cost ($)", hole=0.52, title="Preventive vs Reactive Maintenance", color_discrete_sequence=["#18864B", "#D83B01"])
    fig3.update_traces(hovertemplate="<b>%{label}</b><br>Cost: $%{value:,.0f}<br>Share: %{percent}<extra></extra>")
    fig4 = go.Figure()
    fig4.add_bar(x=delay["Delay Reason"], y=delay["Delay Count"], name="Delay Count", marker_color="#0067B1", hovertemplate="<b>%{x}</b><br>Delays: %{y:,.0f}<extra></extra>")
    fig4.add_scatter(x=delay["Delay Reason"], y=delay["Cumulative %"], name="Cumulative %", yaxis="y2", mode="lines+markers", line=dict(color="#D83B01", width=3), hovertemplate="<b>%{x}</b><br>Cumulative: %{y:.1%}<extra></extra>")
    fig4.update_layout(title="Delivery Delay Root Cause Analysis", yaxis2=dict(overlaying="y", side="right", tickformat=".0%", range=[0, 1.05]))
    plot_two_columns(fig3, fig4)

with tabs[12]:
    render_kpi_strip(
        [
            ("Average Resolution Time", "Average Resolution Time (hours)", "mean", "hours"),
            ("AI Bot Response Accuracy", "AI Bot Response Accuracy", "mean", "percent"),
            ("First Contact Resolution", "First Contact Resolution", "mean", "percent"),
            ("Support Productivity Gain", "Customer Support Productivity Gain", "mean", "percent"),
        ]
    )
    tickets = filtered_df.groupby("Week", as_index=False)["Ticket Resolution Count"].sum().tail(26)
    bot = filtered_df.groupby("Department", as_index=False)["Knowledge Query Count"].sum().sort_values("Knowledge Query Count", ascending=False)
    fig1 = px.line(tickets, x="Week", y="Ticket Resolution Count", markers=True, title="Support Ticket Resolution Trend", color_discrete_sequence=["#0067B1"])
    fig1.update_traces(hovertemplate="Week: %{x}<br>Resolved tickets: %{y:,.0f}<extra></extra>")
    fig2 = px.bar(bot, x="Department", y="Knowledge Query Count", title="Knowledge Bot Usage Analysis", color="Knowledge Query Count", color_continuous_scale="Teal")
    fig2.update_traces(hovertemplate="<b>%{x}</b><br>Queries: %{y:,.0f}<extra></extra>")
    plot_two_columns(fig1, fig2)

    issue = filtered_df.groupby("Issue Category", as_index=False)["Ticket Count"].sum()
    agent = filtered_df.groupby("Month", as_index=False)["Tickets Resolved per Agent"].mean()
    fig3 = px.treemap(issue, path=["Issue Category"], values="Ticket Count", color="Ticket Count", color_continuous_scale="Purples", title="Technical Issue Category Analysis")
    fig3.update_traces(hovertemplate="<b>%{label}</b><br>Tickets: %{value:,.0f}<extra></extra>")
    fig4 = px.area(agent, x="Month", y="Tickets Resolved per Agent", title="Agent Productivity Improvement", color_discrete_sequence=["#18864B"])
    fig4.update_traces(hovertemplate="Month: %{x}<br>Tickets per agent: %{y:.1f}<extra></extra>")
    plot_two_columns(fig3, fig4)


# --- KPI EXPLORER ---
with st.expander("Foldable KPI explorer: compare every KPI by industry", expanded=False):
    selected_explorer_kpis = st.multiselect(
        "KPIs to compare",
        options=list(KPI_COLUMNS),
        default=["On-Time Delivery Rate", "Fill Rate", "Backorder Rate", "Demand Forecast Accuracy"],
    )
    if selected_explorer_kpis:
        explorer_cols = [KPI_COLUMNS[name][0] for name in selected_explorer_kpis]
        explorer = filtered_df.groupby("Industry", as_index=False)[explorer_cols].mean()
        explorer_long = explorer.melt("Industry", var_name="KPI", value_name="Value")
        display_names = {value[0]: key for key, value in KPI_COLUMNS.items()}
        explorer_long["KPI"] = explorer_long["KPI"].map(display_names)

        fig = px.bar(
            explorer_long,
            x="Industry",
            y="Value",
            color="KPI",
            barmode="group",
            title="Selected KPI comparison by industry",
            color_discrete_sequence=ACCENT_SCALE,
        )
        fig.update_layout(xaxis_tickangle=-35)
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:.2f}<extra></extra>")
        st.plotly_chart(apply_chart_theme(fig, 460), width="stretch")


if show_detail_table:
    with st.expander("Filtered record detail", expanded=True):
        st.dataframe(
            filtered_df.sort_values("Date", ascending=False).head(250),
            width="stretch",
            hide_index=True,
        )


# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #667085; font-size: 12px;">
        SupplyOne | A Home Depot Company | Wholesale Distribution Dashboard | Synthetic demo data
    </div>
    """,
    unsafe_allow_html=True,
)
