import streamlit as st

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

    if volume < 500:
        technology = "MJF"

    elif volume < 5000:
        technology = "CNC"

    else:
        technology = "HPDC"

    st.success(f"Recommended Technology: {technology}")

