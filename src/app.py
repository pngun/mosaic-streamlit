import streamlit as st

import interface
from tasks import load, selection

# -------- Sample selection
st.set_page_config(page_title="Mosaic", layout="wide")
interface.init()
interface.subheader("Mosaic Streamlit")
interface.status("Done.")

sample = load.run()

# -------- Subsample and assay selection
workflow_steps = selection.run(sample)

# -------- Assay processing
workflow_steps.run()
