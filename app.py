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
# COMMON INPUTS
# --------------------------------------------------

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

material_price = float(
    selected_material[
        "Default_Price_EUR_kg"
    ].iloc[0]
)

material_group = (
    selected_material[
        "Material_Group"
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


# --------------------------------------------------
# INPUT SUMMARY
# --------------------------------------------------

st.divider()

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Weight",
        f"{part_weight:.3f} kg"
    )

with c2:

    st.metric(
        "Annual Volume",
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


# ==================================================
# TECHNOLOGY RECOMMENDATION
# ==================================================

st.divider()

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

        st.dataframe(
            recommendations_df,
            use_container_width=True
        )

    except Exception as e:

        st.error(
            f"Recommendation failed: {e}"
        )


# ==================================================
# PROCESS BENCHMARK
# ==================================================

st.divider()

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


# ==================================================
# DESIGN TO COST
# ==================================================

st.divider()

st.header(
    "Design-to-Cost"
)

st.info(
    "Module under development."
)


# ==================================================
# VE OPPORTUNITY FINDER
# ==================================================

st.divider()

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
