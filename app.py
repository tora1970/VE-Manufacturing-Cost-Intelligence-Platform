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
    "VE Manufacturing Cost Intelligence Platform"
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
    value=1000
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
            complexity="Medium"
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

# --------------------------------------------------
# PROCESS BENCHMARK
# --------------------------------------------------

elif selected_module == "Process Benchmark":

    st.header(
        "Process Benchmark"
    )

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
            "No benchmark results available."
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
            benchmark_engine
            .calculate_savings(
                benchmark_df,
            )
