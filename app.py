import streamlit as st

from utils.loader import MasterDataLoader
from engine.technology_engine import TechnologyEngine

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

# Ryd kolonnenavne
materials_df.columns = materials_df.columns.str.strip()
regions_df.columns = regions_df.columns.str.strip()
rules_df.columns = rules_df.columns.str.strip()

# --------------------------------------------------
# Initialize Technology Engine
# --------------------------------------------------

engine = TechnologyEngine(rules_df)

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
        [
            "Low",
            "Medium",
            "High"
        ]
    )

# --------------------------------------------------
# Input Summary
# --------------------------------------------------

st.divider()

st.subheader("Selected Inputs")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Weight", f"{part_weight:.3f} kg")

with col2:
    st.metric("Volume", f"{annual_volume:,.0f} pcs/year")

with col3:
    st.metric("Material Price", f"€ {material_price:.2f}/kg")

# --------------------------------------------------
# Recommendation
# --------------------------------------------------

if st.button("Recommend Technology"):

    try:

        recommendations = engine.recommend(
            weight=part_weight,
            volume=annual_volume,
            material=material,
            region=region,
            complexity=complexity
        )

        st.success("Technology evaluation completed")

        st.subheader("Recommended Technologies")

        st.dataframe(
            recommendations,
            use_container_width=True
        )

    except Exception as e:

        st.error(
            f"Technology recommendation failed: {str(e)}"
        )

# --------------------------------------------------
# Debug Section (kan fjernes senere)
# --------------------------------------------------

with st.expander("Debug Information"):

    st.write("Loaded datasets:")
    st.write(list(masterdata.keys()))

    st.write("Materials Columns:")
    st.write(materials_df.columns.tolist())

    st.write("Regions Columns:")
    st.write(regions_df.columns.tolist())

    st.write("Technology Rules Columns:")
    st.write(rules_df.columns.tolist())
