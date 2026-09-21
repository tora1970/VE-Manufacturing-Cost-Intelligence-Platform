import streamlit as st
import pandas as pd
import altair as alt

from utils.loader import MasterDataLoader
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
)

# --------------------------------------------------
# LOAD MASTER DATA
# --------------------------------------------------

try:

    loader = MasterDataLoader()

    masterdata = loader.load_all()

    required_datasets = [
        "materials",
        "regions",
        "technology_rules",
        "technology_cost_library"
    ]

    missing = [
        ds
        for ds in required_datasets
        if ds not in masterdata
    ]

    if missing:

        st.error(
            f"Missing master data: {missing}"
        )

        st.stop()

    materials_df = masterdata["materials"]
    regions_df = masterdata["regions"]
    technology_rules_df = masterdata["technology_rules"]
    technology_cost_df = masterdata["technology_cost_library"]

except Exception as e:

    st.error(
        f"Failed to load master data: {e}"
    )

    st.stop()

# --------------------------------------------------
# CLEAN COLUMN NAMES
# --------------------------------------------------

materials_df.columns = materials_df.columns.str.strip()
regions_df.columns = regions_df.columns.str.strip()
technology_rules_df.columns = (
    technology_rules_df.columns.str.strip()
)
technology_cost_df.columns = (
    technology_cost_df.columns.str.strip()
)

# --------------------------------------------------
# INPUTS
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

    region = st.selectbox(
        "Region",
        regions_df["Region Name"].tolist()
    )

    complexity = st.selectbox(
        "Part Complexity",
        ["Low", "Medium", "High"]
    )

# --------------------------------------------------
# REGION DATA
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
# INPUT SUMMARY
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
        f"{annual_volume:,.0f}"
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
# RUN CALCULATION
# --------------------------------------------------

if st.button("Recommend Technology"):

    try:

        material_group = material_row[
            "Material_Group"
        ].iloc[0]

        technology_engine = TechnologyEngine(
            technology_rules_df
        )

        recommendations = technology_engine.recommend(
            weight=part_weight,
            volume=annual_volume,
            material=material_group,
            complexity=complexity
        )

        recommendations_df = pd.DataFrame(
            recommendations
        )

        st.subheader("Recommended Technologies")

        st.dataframe(
            recommendations_df,
            use_container_width=True
        )

        cost_engine = CostEngine(
            technology_cost_df
        )

        cost_results = []

        for _, tech in recommendations_df.iterrows():

            technology_name = tech["Technology"]

            try:

                cost = cost_engine.calculate_cost(
                    technology=technology_name,
                    weight=part_weight,
                    material_price=material_price,
                    annual_volume=annual_volume,
                    labour_rate=labour_rate,
                    overhead_factor=overhead_factor
                )

                cost_results.append(
                    {
                        "Technology": technology_name,
                        "Score": tech["Score"],

                        "Material Cost EUR":
                            cost.get("Material Cost", 0),

                        "Setup Cost EUR":
                            cost.get("Setup Cost", 0),

                        "Cycle Cost EUR":
                            cost.get("Cycle Cost", 0),

                        "Machine Cost EUR":
                            cost.get("Machine Cost", 0),

                        "Labour Cost EUR":
                            cost.get("Labour Cost", 0),

                        "Overhead Cost EUR":
                            cost.get("Overhead Cost", 0),

                        "Tooling Cost EUR":
                            cost.get("Tooling Cost", 0),

                        "Total Cost EUR/pc":
                            cost.get("Total Cost", 0),

                        "Validation Score":
                            cost.get(
                                "Validation Score",
                                100
                            ),

                        "Warnings":
                            "; ".join(
                                cost.get(
                                    "Warnings",
                                    []
                                )
                            )
                    }
                )

            except Exception as calc_error:

                st.warning(
                    f"{technology_name}: {calc_error}"
                )

        if len(cost_results) == 0:

            st.error(
                "No technology costs could be calculated."
            )

        else:

            cost_df = pd.DataFrame(
                cost_results
            )

            cost_df = cost_df.sort_values(
                by="Total Cost EUR/pc",
                ascending=True
            )

            # ----------------------------------
            # COST TABLE
            # ----------------------------------

            st.subheader(
                "Technology Cost Comparison"
            )

            st.dataframe(
                cost_df,
                use_container_width=True
            )

            # ----------------------------------
            # COST BREAKDOWN
            # ----------------------------------

            st.subheader(
                "Cost Breakdown by Technology"
            )

            chart_columns = [
                "Technology",
                "Material Cost EUR",
                "Setup Cost EUR",
                "Cycle Cost EUR",
                "Labour Cost EUR",
                "Overhead Cost EUR",
                "Tooling Cost EUR"
            ]

            available_columns = [
                col
                for col in chart_columns
                if col in cost_df.columns
            ]

            chart_df = cost_df[
                available_columns
            ].copy()

            chart_df = pd.melt(
                chart_df,
                id_vars=["Technology"],
                var_name="Cost Element",
                value_name="Cost"
            )

            chart = (
                alt.Chart(chart_df)
                .mark_bar()
                .encode(
                    y=alt.Y(
                        "Technology:N",
                        title=None
                    ),
                    x=alt.X(
                        "sum(Cost):Q",
                        title="Cost (EUR/pc)"
                    ),
                    color="Cost Element:N"
                )
                .properties(
                    height=350
                )
            )

            st.altair_chart(
                chart,
                use_container_width=True
            )

            # ----------------------------------
            # VALIDATION ISSUES
            # ----------------------------------

            validation_df = cost_df[
                cost_df["Warnings"] != ""
            ]

            st.subheader(
                "Validation Issues"
            )

            if validation_df.empty:

                st.success(
                    "No validation issues detected."
                )

            else:

                st.warning(
                    f"{len(validation_df)} technologies have validation issues."
                )

                st.dataframe(
                    validation_df[
                        [
                            "Technology",
                            "Validation Score",
                            "Warnings"
                        ]
                    ],
                    use_container_width=True
                )

            # ----------------------------------
            # BEST OPTION
            # ----------------------------------

            best_option = cost_df.iloc[0]

            best_technology = (
                best_option["Technology"]
            )

            best_cost = (
                best_option["Total Cost EUR/pc"]
            )

            st.success(
                f"""
Best Technology Option: {best_technology}

Estimated Manufacturing Cost:
€ {best_cost:.2f}/pc
"""
            )

    except Exception as e:

        st.error(
            f"Calculation failed: {str(e)}"
        )

# --------------------------------------------------
# DEBUG SECTION
# --------------------------------------------------

with st.expander("Debug Information"):

    st.write(
        "Loaded datasets:"
    )

    st.write(
        list(masterdata.keys())
    )

    st.write(
        "Technology Cost Library Columns:"
    )

    st.write(
        technology_cost_df.columns.tolist()
    )

    st.write(
        "Technology Cost Library"
    )

    st.dataframe(
        technology_cost_df,
        use_container_width=True
    )
