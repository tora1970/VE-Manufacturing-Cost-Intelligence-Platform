import streamlit as st
import pandas as pd
import altair as alt

from utils.loader import load_all
from engine.technology_engine import TechnologyEngine
from engine.cost_engine import CostEngine

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="VE Manufacturing Cost Intelligence Platform",
    layout="wide"
)

st.title("VE Manufacturing Cost Intelligence Platform")
st.subheader("Technology Selection")

# --------------------------------------------------
# LOAD MASTER DATA
# --------------------------------------------------

try:

    masterdata = load_all()

    materials_df = masterdata["materials"]
    regions_df = masterdata["regions"]
    technology_rules_df = masterdata["technology_rules"]
    technology_cost_df = masterdata["technology_cost_library"]

except Exception as e:

    st.error(f"Failed to load master data: {e}")
    st.stop()

# --------------------------------------------------
# INPUT SECTION
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    part_weight = st.number_input(
        "Part Weight (kg)",
        min_value=0.001,
        value=0.050,
        step=0.001,
        format="%.3f"
    )

    annual_volume = st.number_input(
        "Annual Volume (pcs/year)",
        min_value=1,
        value=1000,
        step=100
    )

    material = st.selectbox(
        "Material",
        materials_df["Material_Name"].tolist()
    )

with col2:

    material_row = materials_df[
        materials_df["Material_Name"] == material
    ]

    default_price = float(
        material_row["Default_Price_EUR_kg"].iloc[0]
    )

    material_price = st.number_input(
        "Material Price (EUR/kg)",
        min_value=0.0,
        value=default_price,
        step=0.10
    )

    region_column = regions_df.columns[1]

    region = st.selectbox(
        "Region",
        regions_df[region_column].tolist()
    )

    complexity = st.selectbox(
        "Part Complexity",
        ["Low", "Medium", "High"]
    )

# --------------------------------------------------
# REGION DATA
# --------------------------------------------------

selected_region = regions_df[
    regions_df[region_column] == region
]

labour_rate = float(
    selected_region["Labour Rate EUR hr"].iloc[0]
)

overhead_factor = float(
    selected_region["Overhead factor"].iloc[0]
)

# --------------------------------------------------
# SELECTED INPUTS
# --------------------------------------------------

st.divider()

st.subheader("Selected Inputs")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Weight",
        f"{part_weight:.3f} kg"
    )

with c2:
    st.metric(
        "Volume",
        f"{annual_volume:,.0f} pcs/year"
    )

with c3:
    st.metric(
        "Material Price",
        f"€ {material_price:.2f}/kg"
    )

with c4:
    st.metric(
        "Labour Rate",
        f"€ {labour_rate:.2f}/hr"
    )

# --------------------------------------------------
# RUN TECHNOLOGY EVALUATION
# --------------------------------------------------

if st.button("Recommend Technology"):

    try:

        material_group = material_row[
            "Material_Group"
        ].iloc[0]

        tech_engine = TechnologyEngine(
            technology_rules_df
        )

        recommendations = tech_engine.recommend(
            weight=part_weight,
            volume=annual_volume,
            material=material_group,
            complexity=complexity
        )

        st.success(
            "Technology evaluation completed"
        )

        # ------------------------------------------
        # TECHNOLOGY RECOMMENDATIONS
        # ------------------------------------------

        st.subheader("Recommended 
