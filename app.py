import streamlit as st
import pandas as pd

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
# SELECTED INPUTS
# --------------------------------------------------

st.divider()

st.subheader("Selected Inputs")

c1, c2, c3 = st.columns(3)

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

        st.success("Technology evaluation completed")

        # ------------------------------------------
        # TECHNOLOGY RECOMMENDATIONS
        # ------------------------------------------

        st.subheader("Recommended Technologies")

        recommendations_df = pd.DataFrame(
            recommendations
        )

        st.dataframe(
            recommendations_df,
            use_container_width=True
        )

        # ------------------------------------------
        # COST COMPARISON
        # ------------------------------------------

        st.subheader("Technology Cost Comparison")

        cost_engine = CostEngine(
            technology_cost_df
        )

        cost_results = []

        for tech in recommendations:

            technology_name = tech["technology"]

            try:

                result = cost_engine.calculate_cost(
                    technology=technology_name,
                    weight_kg=part_weight,
                    material_price_eur_kg=material_price,
                    annual_volume=annual_volume
                )

                result["Score"] = tech["score"]

                cost_results.append(result)

            except Exception as calc_error:

                st.warning(
                    f"{technology_name}: {calc_error}"
                )

        if len(cost_results) > 0:

            cost_df = pd.DataFrame(cost_results)

            cost_df = cost_df.sort_values(
                by="Total Cost EUR/pc"
            )

            st.dataframe(
                cost_df,
                use_container_width=True
            )

            best_option = cost_df.iloc[0]

            st.success(
                f"""
Best Technology Option: {best_option['Technology']}

Estimated Manufacturing Cost:
€ {best_option['Total Cost EUR/pc'\]:.2f}/pc
"""
            )

        else:

            st.error(
                "No technology costs could be calculated."
            )

    except Exception as e:

        st.error(
            f"Calculation failed: {str(e)}"
        )

# --------------------------------------------------
# DEBUG SECTION
# --------------------------------------------------

with st.expander("Debug Information"):

    st.write("Loaded datasets:")
    st.write(list(masterdata.keys()))

    if "technology_cost_library" in masterdata:

        st.write("Technology Cost Library Columns:")
        st.write(
            technology_cost_df.columns.tolist()
        )

        st.write("Technology Cost Library:")
        st.dataframe(
            technology_cost_df,
            use_container_width=True
        )
