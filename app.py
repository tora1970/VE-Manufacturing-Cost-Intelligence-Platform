import streamlit as st

from utils.loader import MasterDataLoader
from engine.technology_engine import TechnologyEngine

loader = MasterDataLoader()

masterdata = loader.load_all()

st.write(masterdata.keys())

rules = masterdata["technology_rules"]

engine = TechnologyEngine(rules)

st.set_page_config(
    page_title="VE Manufacturing Cost Intelligence Platform",
    layout="wide"
)

st.title("Technology Selection")

col1, col2 = st.columns(2)

with col1:
    part_weight = st.number_input(
        "Part Weight (kg)",
        min_value=0.001,
        value=0.05,
        step=0.01
    )

    annual_volume = st.number_input(
        "Annual Volume (pcs/year)",
        min_value=1,
        value=1000,
        step=100
    )

    material = st.selectbox(
        "Material",
        masterdata["materials"]["Material_Name"]
    )

with col2:
    material_price = st.number_input(
        "Material Price (EUR/kg)",
        min_value=0.0,
        value=3.50,
        step=0.10
    )

    region = st.selectbox(
        "Region",
       st.write(masterdata["regions"].columns.tolist())..
        masterdata["regions"]["Region_Name"]
    )

    complexity = st.selectbox(
        "Part Complexity",
        ["Low", "Medium", "High"]
    )

if st.button("Recommend Technology"):

    technology = engine.recommend(volume)

    st.success(
        f"Recommended Technology: {technology}"
    )
