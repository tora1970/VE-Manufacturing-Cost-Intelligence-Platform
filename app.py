import streamlit as st
import pandas as pd

from utils.loader import MasterDataLoader

from engine.technology_engine import TechnologyEngine
from engine.cost_engine import CostEngine

from modules.process_benchmark import ProcessBenchmark


# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="VE Manufacturing Cost Intelligence Platform",
    layout="wide"
)

st.title(
    "VE Manufacturing Cost Intelligence Platform (VECIP)"
)


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


# --------------------------------------------------
# ENGINES
# --------------------------------------------------

technology_engine = TechnologyEngine(
    rules_df
)

cost_engine = CostEngine(
    technology_cost_df
)

benchmark_engine = ProcessBenchmark(
    technology_cost_df
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

selected_module = st.sidebar.radio(
    "Module",
    [
        "Technology Selector",
        "Process Benchmark"
    ]
)


# --------------------------------------------------
# COMMON INPUTS
# --------------------------------------------------

st.sidebar.header(
    "Inputs"
)

part_weight = st.sidebar.number_input(
    "Part Weight (kg)",
    min_value=0.001,
    value=0.050,
    step=0.001,
    format="%.3f"
)

annual_volume = st.sidebar.number_input(
    "Annual Volume",
    min_value=1,
    value=1000,
    step=100
)

material = st.sidebar.selectbox(
    "Material",
    materials_df["Material_Name"]
)

selected_material = materials_df[
    materials_df["Material_Name"] == material
]

material_price = float(
    selected_material[
        "Default_Price_EUR_kg"
    ].iloc[0]
)

region = st.sidebar.selectbox(
    "Region",
    regions_df["Region Name"]
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


# --------------------------------------------------
# TECHNOLOGY SELECTOR
# --------------------------------------------------

if selected_module == "Technology Selector":

    st.header(
        "Technology Selector"
    )

    complexity = st.selectbox(
        "Part Complexity",
        [
            "Low",
            "Medium",
            "High"
        ]
    )

    if st.button(
        "Recommend Technology"
    ):

        try:

            material_group = (
                selected_material[
                    "Material_Group"
                ].iloc[0]
            )

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

        except Exception as e:

            st.error(
                f"Calculation failed: {e}"
            )


# --------------------------------------------------
# PROCESS BENCHMARK
# --------------------------------------------------

elif selected_module == "Process Benchmark":

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

            if benchmark_df.empty:

                st.warning(
                    "No benchmark results generated."
                )

            else:

                st.subheader(
                    "Technology Ranking"
                )

                st.dataframe(
                    benchmark_df,
                    use_container_width=True
                )

                baseline_technology = (
                    st.selectbox(
                        "Baseline Technology",
                        benchmark_df[
                            "Technology"
                        ].tolist()
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

                best_option = (
                    benchmark_engine.get_best_technology(
                        benchmark_df
                    )
                )

                if best_option is not None:

                    st.success(
                        f"""
Best Technology: {best_option['Technology']}

Cost Per Part: € {best_option['Cost Per Part']:.2f}

Annual Cost: € {best_option['Annual Cost']:.0f}
"""
                    )

        except Exception as e:

            st.error(
                f"Benchmark failed: {e}"
            )


# --------------------------------------------------
# DEBUG
# --------------------------------------------------

with st.expander(
    "Debug Information"
):

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
