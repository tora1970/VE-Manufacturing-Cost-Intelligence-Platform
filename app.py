import pandas as pd
import streamlit as st

from utils.loader import MasterDataLoader
from engine.technology_engine import TechnologyEngine
from engine.cost_engine import CostEngine

# --------------------------------------------------
# Page Setup
# --------------------------------------------------

st.set_page_config(
    page_title="VE Manufacturing Cost Intelligence Platform",
    layout="wide"
)

# --------------------------------------------------
# Load Master Data
# --------------------------------------------------

loader = MasterDataLoader()
masterdata = loader.load_all()

materials_df = masterdata["materials"]
regions_df = masterdata["regions"]
rules_df = masterdata["technology_rules"]
technology_cost_df = masterdata["technology_cost_library"]

# --------------------------------------------------
# Clean Column Names
# --------------------------------------------------

materials_df.columns = materials_df.columns.str.strip()
regions_df.columns = regions_df.columns.str.strip()
rules_df.columns = rules_df.columns.str.strip()
technology_cost_df.columns = technology_cost_df.columns.str.strip()

# --------------------------------------------------
# Initialize Engines
# --------------------------------------------------

technology_engine = TechnologyEngine(rules_df)
cost_engine = CostEngine(technology_cost_df)

# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("VE Manufacturing Cost Intelligence Platform")
st.subheader("Technology Selection")

# --------------------------------------------------
# Input Section
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    part_weight = st.number_input(
        "Part Weight (kg)",
        min_value=0.001,
        value=0.050,
        step=0.010,
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
        materials_df["Material_Name"]
    )

with col2:

    selected_material = materials_df[
        materials_df["Material_Name"] == material
    ]

    default_price = float(
        selected_material["Default_Price_EUR_kg"].iloc[0]
    )

    material_price = st.number_input(
        "Material Price (EUR/kg)",
        min_value=0.0,
        value=default_price,
        step=0.10
    )

    region = st.selectbox(
        "Region",
        regions_df["Region Name"]
    )

    complexity = st.selectbox(
        "Part Complexity",
        ["Low", "Medium", "High"]
    )

# --------------------------------------------------
# Input Summary
# --------------------------------------------------

st.divider()

st.subheader("Selected Inputs")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Weight", f"{part_weight:.3f} kg")

with c2:
    st.metric("Volume", f"{annual_volume:,.0f} pcs/year")

with c3:
    st.metric("Material Price", f"€ {material_price:.2f}/kg")

# --------------------------------------------------
# Run Technology Recommendation
# --------------------------------------------------

if st.button("Recommend Technology"):

    try:

        recommendations = technology_engine.recommend(
            weight=part_weight,
            volume=annual_volume,
            material=material,
            region=region,
            complexity=complexity
        )

        st.success("Technology evaluation completed")

        # ------------------------------------------
        # Technology Ranking
        # ------------------------------------------

        st.subheader("Recommended Technologies")

        st.dataframe(
            recommendations,
            use_container_width=True
        )

        # ------------------------------------------
        # Cost Comparison
        # ------------------------------------------

        st.subheader("Technology Cost Comparison")

        cost_results = []

        top_technologies = recommendations.head(3)

        for _, row in top_technologies.iterrows():

    cost = cost_engine.calculate_cost(
        technology=row["Technology"],
        weight=part_weight,
        material_price=material_price
    )

    cost_results.append(
        {
            "Technology": row["Technology"],
            "Score": row["Score"],
            "Material Cost EUR": cost["Material Cost"],
            "Machine Cost EUR": cost["Machine Cost"],
            "Labour Cost EUR": cost["Labour Cost"],
            "Overhead Cost EUR": cost["Overhead Cost"],
            "Tooling Cost EUR": cost["Tooling Cost"],
            "Total Cost EUR/pc": cost["Total Cost"]
        }
    )

        cost_df = pd.DataFrame(cost_results)

        cost_df = cost_df.sort_values(
            by="Total Cost EUR/pc",
            ascending=True
        )

        st.dataframe(
            cost_df,
            use_container_width=True
        )

        # ------------------------------------------
        # Best Option
        # ------------------------------------------

        best_option = cost_df.iloc[0]

        st.success(
            f"""
Best Technology Option: {best_option['Technology']}

Estimated Manufacturing Cost:
€ {best_option['Total Cost EUR/pc']:.2f}/pc
"""
        )

    except Exception as e:

        st.error(
            f"Calculation failed: {str(e)}"
        )

# --------------------------------------------------
# Debug Section
# --------------------------------------------------

with st.expander("Debug Information"):

    st.write(
        "Loaded datasets:",
        list(masterdata.keys())
    )

    st.write(
        "Technology Cost Library Columns:",
        technology_cost_df.columns.tolist()
    )

    st.write(
        "Technology Cost Library:",
        technology_cost_df
    )
