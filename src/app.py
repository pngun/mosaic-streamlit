# FIXME: setup Sentry for all builds until we figure out what we need
from sentry import setup_sentry

setup_sentry()

import streamlit as st  # noqa: E402

import interface  # noqa: E402
from tasks import load, selection  # noqa: E402

# -------- Sample selection
st.set_page_config(page_title="Insights", layout="wide")
interface.init()
interface.subheader("Insights")
interface.status("Done.")

sample = load.run()

# -------- Subsample and assay selection
workflow_steps = selection.run(sample)

# -------- Assay processing
workflow_steps.run()
