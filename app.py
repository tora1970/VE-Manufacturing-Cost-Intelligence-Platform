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
# Region Data
# --------------------------------------------------

selected_region = regions_df[
    regions_df["Region Name"] == region
]

labour_rate = float(
    selected_region["Labour Rate EUR hr"].iloc[0]
)

overhead_factor = float(
    selected_region["Overhead factor"].iloc[0]
)

# --------------------------------------------------
# Selected Inputs
# --------------------------------------------------

st.divider()

st.subheader("Selected Inputs")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Weight", f"{part_weight:.3f} kg")

with c2:
    st.metric("Annual Volume", f"{annual_volume:,.0f}")

with c3:
    st.metric("Material Price", f"€ {material_price:.2f}/kg")

with c4:
    st.metric("Labour Rate", f"€ {labour_rate:.2f}/hr")

# --------------------------------------------------
# Run Evaluation
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

        st.subheader("Recommended Technologies")

        st.dataframe(
            recommendations,
            use_container_width=True
        )

        # ------------------------------------------
        # Cost Calculation
        # ------------------------------------------

        cost_results = []

        for _, row in recommendations.head(3).iterrows():

            cost = cost_engine.calculate_cost(
                technology=row["Technology"],
                weight=part_weight,
                material_price=material_price,
                annual_volume=annual_volume,
                labour_rate=labour_rate,
                overhead_factor=overhead_factor
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

        # ------------------------------------------
        # Cost Table
        # ------------------------------------------

        st.subheader("Technology Cost Comparison")

        st.dataframe(
            cost_df,
            use_container_width=True
        )

        # ------------------------------------------
        # Cost Breakdown Chart
        # ------------------------------------------

        st.subheader("Cost Breakdown by Technology")

        chart_df = cost_df[
            [
                "Technology",
                "Material Cost EUR",
                "Machine Cost EUR",
                "Labour Cost EUR",
                "Overhead Cost EUR",
                "Tooling Cost EUR"
            ]
        ].copy()

        chart_df = chart_df.set_index("Technology")

        st.bar_chart(chart_df)

        # ------------------------------------------
        # Best Option
        # ------------------------------------------

        best_option = cost_df.iloc[0]

        st.success(
            f"Best Technology Option: {best_option['Technology']} | "
            f"Estimated Manufacturing Cost: "
            f"€ {best_option['Total Cost EUR/pc'\]:.2f}/pc"
        )

    except Exception as e:

        st.error(
            f"Calculation failed: {str(e)}"
        )

# --------------------------------------------------
# Debug Information
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
        "Regions Columns:",
        regions_df.columns.tolist()
    )

    st.write(
        "Materials Columns:",
        materials_df.columns.tolist()
    )

    st.write(
        "Technology Rules Columns:",
        rules_df.columns.tolist()
    )
