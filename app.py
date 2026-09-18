import streamlit as st

from utils.loader import MasterDataLoader
from engine.technology_engine import TechnologyEngine

loader = MasterDataLoader()

masterdata = loader.load_all()

rules = masterdata["technology_rules"]

engine = TechnologyEngine(rules)

st.set_page_config(
    page_title="VE Manufacturing Cost Intelligence Platform",
    layout="wide"
)

st.title("Technology Selection")

weight = st.number_input(
    "Part Weight (kg)",
    min_value=0.001,
    value=0.050
)

volume = st.number_input(
    "Annual Volume",
    min_value=1,
    value=1000
)

material = st.selectbox(
    "Material",
    [
        "Aluminium",
        "Steel",
        "Plastic"
    ]
)

if st.button("Recommend Technology"):

   technology = engine.recommend(volume)
    st.success(f"Recommended Technology: {technology}")

