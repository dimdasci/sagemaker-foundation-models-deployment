import streamlit as st
import os

from PIL import Image
image = Image.open("./img/sagemaker.png")
st.image(image, width=80)

version = os.environ.get("WEB_VERSION", "0.1")

st.header(f"Sagemaker Foundation Models Demo")
st.markdown("This is a demo of foundation AI models in Amazon SageMaker Jumpstart")
st.markdown("_Please select an option from the sidebar_")
st.caption(f"Version: {version}")