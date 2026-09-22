from modules.process_benchmark import (
    ProcessBenchmark
)
import streamlit as st
import pandas as pd
import altair as alt

from utils.loader import MasterDataLoader
from engine.technology_engine import TechnologyEngine
from engine.cost_engine import CostEngine


# --------------------------------------------------
# PAGE SETUP
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

    loader = MasterDataLoader()

    masterdata = loader.load_all()

    materials_df = masterdata["materials"]
    regions_df = masterdata["regions"]
    rules_df = masterdata["technology_rules"]
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
rules_df.columns = rules_df.columns.str.strip()
technology_cost_df.columns = technology_cost_df.columns.str.strip()


# --------------------------------------------------
# ENGINES
# --------------------------------------------------

technology_engine = TechnologyEngine(
    rules_df
)

cost_engine = CostEngine(
    technology_cost_df
)


# --------------------------------------------------
# FORMATTERS
# --------------------------------------------------

def eur_number(value, decimals=2):

    try:

        return (
            f"{value:,.{decimals}f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    except Exception:

        return value


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
        materials_df["Material_Name"]
    )

with col2:

    selected_material = materials_df[
        materials_df["Material_Name"] == material
    ]

    default_price = float(
        selected_material[
            "Default_Price_EUR_kg"
        ].iloc[0]
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
# HPDC PROCESS PARAMETERS
# --------------------------------------------------

with st.expander(
    "HPDC Process Parameters",
    expanded=False
):

    shot_weight_kg = st.number_input(
        "Shot Weight (kg)",
        min_value=part_weight,
        value=round(part_weight * 1.5, 3),
        step=0.001,
        format="%.3f"
    )

    cycle_time_sec = st.number_input(
        "Cycle Time (sec)",
        min_value=1.0,
        value=45.0,
        step=1.0
    )

    machine_rate_per_hour = st.number_input(
        "Machine Rate (EUR/hr)",
        min_value=0.0,
        value=75.0,
        step=1.0
    )

    tool_cost = st.number_input(
        "Tool Cost (EUR)",
        min_value=0.0,
        value=120000.0,
        step=1000.0
    )

    tool_life_shots = st.number_input(
        "Tool Life (Shots)",
        min_value=1,
        value=750000,
        step=10000
    )

    scrap_rate = (
        st.slider(
            "Scrap Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=3.0,
            step=0.5
        )
        / 100
    )


# --------------------------------------------------
# REGION DATA
# --------------------------------------------------

selected_region = regions_df[
    regions_df["Region Name"] == region
]

labour_rate = float(
    selected_region[
        "Labour Rate EUR hr"
    ].iloc[0]
)

overhead_factor = float(
    selected_region[
        "Overhead factor"
    ].iloc[0]
)


# --------------------------------------------------
# INPUT OVERVIEW
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
        eur_number(annual_volume, 0)
    )

with c3:
    st.metric(
        "Material Price",
        f"€ {eur_number(material_price, 2)}/kg"
    )

with c4:
    st.metric(
        "Labour Rate",
        f"€ {eur_number(labour_rate, 2)}/hr"
    )


# --------------------------------------------------
# CALCULATE
# --------------------------------------------------

if st.button("Recommend Technology"):

    try:

        material_group = selected_material[
            "Material_Group"
        ].iloc[0]

        recommendations = (
            technology_engine.recommend(
                weight=part_weight,
                volume=annual_volume,
                material=material_group,
                complexity=complexity
            )
        )

        recommendations_df = pd.DataFrame(
            recommendations
        )

        st.subheader(
            "Recommended Technologies"
        )

        st.dataframe(
            recommendations_df,
            use_container_width=True
        )

        cost_results = []

        hpdc_kpis = None

        for _, row in recommendations_df.iterrows():

            technology_name = row["Technology"]

            try:

                cost = cost_engine.calculate_cost(
                    technology=technology_name,
                    weight=part_weight,
                    material_price=material_price,
                    annual_volume=annual_volume,
                    labour_rate=labour_rate,
                    overhead_factor=overhead_factor,
                    shot_weight_kg=shot_weight_kg,
                    cycle_time_sec=cycle_time_sec,
                    machine_rate_per_hour=machine_rate_per_hour,
                    tool_cost=tool_cost,
                    tool_life_shots=tool_life_shots,
                    scrap_rate=scrap_rate
                )

                if technology_name.upper() == "HPDC":
                    hpdc_kpis = cost.get(
                        "KPIs",
                        {}
                    )

                cost_results.append(
                    {
                        "Technology": technology_name,
                        "Score": row["Score"],
                        "Material Cost": cost["Material Cost"],
                        "Setup Cost": cost["Setup Cost"],
                        "Manufacturing Cost": cost.get(
                            "Manufacturing Cost",
                            cost.get(
                                "Cycle Cost",
                                0
                            )
                        ),
                        "Machine Cost": cost["Machine Cost"],
                        "Labour Cost": cost["Labour Cost"],
                        "Overhead Cost": cost["Overhead Cost"],
                        "Tooling Cost": cost["Tooling Cost"],
                        "Total Cost": cost["Total Cost"],
                        "Validation Score": cost["Validation Score"],
                        "Warnings": "; ".join(
                            cost["Warnings"]
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
                by="Total Cost",
                ascending=True
            )

            st.subheader(
                "Technology Cost Comparison"
            )

            display_df = cost_df.copy()

            cost_columns = [
                "Material Cost",
                "Setup Cost",
                "Manufacturing Cost",
                "Machine Cost",
                "Labour Cost",
                "Overhead Cost",
                "Tooling Cost",
                "Total Cost"
            ]

            for col in cost_columns:

                if col in display_df.columns:

                    display_df[col] = (
                        display_df[col]
                        .apply(
                            lambda x: eur_number(
                                x,
                                2
                            )
                        )
                    )

            st.dataframe(
                display_df,
                use_container_width=True
            )

            # --------------------------------------
            # HPDC KPI DASHBOARD
            # --------------------------------------

            if hpdc_kpis:

                st.subheader(
                    "HPDC Process KPIs"
                )

                k1, k2, k3, k4 = st.columns(4)

                with k1:
                    st.metric(
                        "Material Utilization",
                        f"{hpdc_kpis.get('material_utilization_pct',0):.1f}%"
                    )

                with k2:
                    st.metric(
                        "Yield Loss",
                        f"{hpdc_kpis.get('yield_loss_pct',0):.1f}%"
                    )

                with k3:
                    st.metric(
                        "Parts/Hour",
                        f"{hpdc_kpis.get('parts_per_hour',0):.1f}"
                    )

                with k4:
                    st.metric(
                        "Tool Cost/Part",
                        f"€ {eur_number(hpdc_kpis.get('tool_cost_per_part',0),4)}"
                    )

            # --------------------------------------
            # COST BREAKDOWN
            # --------------------------------------

            st.subheader(
                "Cost Breakdown by Technology"
            )

            chart_df = cost_df[
                [
                    "Technology",
                    "Material Cost",
                    "Setup Cost",
                    "Machine Cost",
                    "Labour Cost",
                    "Overhead Cost",
                    "Tooling Cost"
                ]
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
                        title="Cost"
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

            # --------------------------------------
            # VALIDATION
            # --------------------------------------

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

            # --------------------------------------
            # BEST OPTION
            # --------------------------------------

            best_option = cost_df.iloc[0]

            best_technology = (
                best_option["Technology"]
            )

            best_cost = (
                best_option["Total Cost"]
            )

            st.success(
                f"""
Best Technology Option: {best_technology}

Estimated Manufacturing Cost:

€ {eur_number(best_cost, 2)}/pc
"""
            )

    except Exception as e:

        st.error(
            f"Calculation failed: {e}"
        )


# --------------------------------------------------
# DEBUG
# --------------------------------------------------

with st.expander("Debug Information"):

    st.write(
        "Loaded Datasets:"
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

    st.dataframe(
        technology_cost_df,
        use_container_width=True
    )
