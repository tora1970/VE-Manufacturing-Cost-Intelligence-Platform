import streamlit as st
import pandas as pd
import altair as alt

from utils.loader import MasterDataLoader

from engine.technology_engine import TechnologyEngine
from engine.cost_engine import CostEngine

from modules.process_benchmark import ProcessBenchmark


# ==================================================
# PAGE SETUP
# ==================================================

st.set_page_config(
    page_title="VE Manufacturing Cost Intelligence Platform",
    layout="wide"
)

st.title(
    "VE Manufacturing Cost Intelligence Platform (VECIP)"
)

# ==================================================
# LOAD MASTER DATA
# ==================================================

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

# ==================================================
# CLEAN COLUMN NAMES
# ==================================================

materials_df.columns = (
    materials_df.columns.str.strip()
)

regions_df.columns = (
    regions_df.columns.str.strip()
)

rules_df.columns = (
    rules_df.columns.str.strip()
)

technology_cost_df.columns = (
    technology_cost_df.columns.str.strip()
)

# ==================================================
# ENGINES
# ==================================================

technology_engine = TechnologyEngine(
    rules_df
)

cost_engine = CostEngine(
    technology_cost_df
)

benchmark_engine = ProcessBenchmark(
    technology_cost_df
)

# ==================================================
# TECHNOLOGY MAPPING
# ==================================================

TECHNOLOGY_MAPPING = {

    "CNC Machining": "CNC",

    "Die Casting": "HPDC",

    "HP Multi Jet Fusion": None,
}

# ==================================================
# COMMON INPUTS
# ==================================================

st.header(
    "Part Inputs"
)

col1, col2, col3 = st.columns(3)

with col1:

    part_weight = st.number_input(
        "Part Weight (kg)",
        min_value=0.001,
        value=0.050,
        step=0.001,
        format="%.3f"
    )

    annual_volume = st.number_input(
        "Annual Volume",
        min_value=1,
        value=1000,
        step=100
    )

with col2:

    material = st.selectbox(
        "Material",
        materials_df["Material_Name"]
    )

    region = st.selectbox(
        "Region",
        regions_df["Region Name"]
    )

with col3:

    complexity = st.selectbox(
        "Part Complexity",
        [
            "Low",
            "Medium",
            "High"
        ]
    )

selected_material = materials_df[
    materials_df["Material_Name"] == material
]

material_group = (
    selected_material["Material_Group"]
    .iloc[0]
)

material_price = float(
    selected_material[
        "Default_Price_EUR_kg"
    ].iloc[0]
)

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

# ==================================================
# TABS
# ==================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Technology Selection",
        "Process Benchmark",
        "Design-to-Cost",
        "VE Opportunity Finder"
    ]
)

# ==================================================
# TAB 1 - TECHNOLOGY SELECTION
# ==================================================

with tab1:

    st.header(
        "Technology Recommendation"
    )

    if st.button(
        "Recommend Technology"
    ):

        try:

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

            for _, row in recommendations_df.iterrows():

    technology_name = (
        row["Technology"]
    )

    mapped_technology = (
        TECHNOLOGY_MAPPING.get(
            technology_name,
            technology_name
        )
    )

    if mapped_technology is None:

        st.warning(
            f"{technology_name}: "
            f"No cost model available yet."
        )

        continue

    try:

        result = (
            cost_engine.calculate_cost(
                technology=mapped_technology,
                part_weight=part_weight,
                annual_volume=annual_volume,
                material_price=material_price,
                labour_rate=labour_rate,
                overhead_factor=overhead_factor
            )
        )

                    cost_results.append({

                        "Technology":
                            technology_name,

                        "Score":
                            row["Score"],

                        "Material Cost":
                            result["Material Cost"],

                        "Setup Cost":
                            result["Setup Cost"],

                        "Machine Cost":
                            result["Machine Cost"],

                        "Labour Cost":
                            result["Labour Cost"],

                        "Overhead Cost":
                            result["Overhead Cost"],

                        "Tooling Cost":
                            result["Tooling Cost"],

                        "Manufacturing Cost":
                            result["Manufacturing Cost"],

                        "Total Cost":
                            result["Total Cost"],

                        "Validation Score":
                            result["Validation Score"],

                        "Warnings":
                            "; ".join(
                                result["Warnings"]
                            )
                    })

                except Exception as calc_error:

                    st.warning(
                        f"{technology_name}: {calc_error}"
                    )

            if len(cost_results) > 0:

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

                st.dataframe(
                    cost_df,
                    use_container_width=True
                )

                # ----------------------------------
                # COST BREAKDOWN CHART
                # ----------------------------------

                st.subheader(
                    "Cost Breakdown"
                )

                chart_df = pd.melt(
                    cost_df[
                        [
                            "Technology",
                            "Material Cost",
                            "Setup Cost",
                            "Machine Cost",
                            "Labour Cost",
                            "Overhead Cost",
                            "Tooling Cost"
                        ]
                    ],
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
                            title="Cost (€)"
                        ),
                        color="Cost Element:N"
                    )
                    .properties(
                        height=400
                    )
                )

                st.altair_chart(
                    chart,
                    use_container_width=True
                )

                # ----------------------------------
                # VALIDATION
                # ----------------------------------

                validation_df = cost_df[
                    cost_df["Warnings"] != ""
                ]

                st.subheader(
                    "Validation"
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

                # ----------------------------------
                # BEST OPTION
                # ----------------------------------

                best_option = cost_df.iloc[0]

                st.success(
                    f"""
Best Technology: {best_option['Technology']}

Estimated Cost:
€ {best_option['Total Cost']:.2f}/pc
"""
                )

        except Exception as e:

            st.error(
                f"Recommendation failed: {e}"
            )

# ==================================================
# TAB 2 - PROCESS BENCHMARK
# ==================================================

with tab2:

    st.header(
        "Process Benchmark"
    )

    if st.button(
        "Run Benchmark"
    ):

        try:

            benchmark_df = (
                benchmark_engine.run_benchmark(
                    part_weight=part_weight,
                    annual_volume=annual_volume,
                    material_price=material_price,
                    labour_rate=labour_rate,
                    overhead_factor=overhead_factor
                )
            )

            st.dataframe(
                benchmark_df,
                use_container_width=True
            )

            if not benchmark_df.empty:

                baseline_technology = (
                    st.selectbox(
                        "Baseline Technology",
                        benchmark_df[
                            "Technology"
                        ].tolist(),
                        key="benchmark_baseline"
                    )
                )

                benchmark_df = (
                    benchmark_engine.calculate_savings(
                        benchmark_df,
                        baseline_technology
                    )
                )

                benchmark_df = (
                    benchmark_engine.calculate_annual_savings(
                        benchmark_df,
                        annual_volume
                    )
                )

                st.subheader(
                    "Savings Analysis"
                )

                st.dataframe(
                    benchmark_df,
                    use_container_width=True
                )

        except Exception as e:

            st.error(
                f"Benchmark failed: {e}"
            )

# ==================================================
# TAB 3 - DESIGN TO COST
# ==================================================

with tab3:

    st.header(
        "Design-to-Cost"
    )

    st.info(
        "Module under development."
    )

# ==================================================
# TAB 4 - OPPORTUNITY FINDER
# ==================================================

with tab4:

    st.header(
        "VE Opportunity Finder"
    )

    st.info(
        "Module under development."
    )

# ==================================================
# DEBUG
# ==================================================

with st.expander(
    "Debug Information"
):

    st.write(
        list(masterdata.keys())
    )
