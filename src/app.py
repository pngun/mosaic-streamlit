# FIXME: setup Sentry for all builds until we figure out what we need
import sys
from sentry import setup_sentry
from sentry_sdk import capture_exception

setup_sentry()

script_runner = sys.modules["streamlit.script_runner"]

streamlit_handle_exception = script_runner.handle_uncaught_app_exception

def catch_streamlit_exceptions(e):
    capture_exception(e)
    streamlit_handle_exception(e)

script_runner.handle_uncaught_app_exception = catch_streamlit_exceptions


import streamlit as st  # noqa: E402

import interface  # noqa: E402
from tasks import load, selection  # noqa: E402

# -------- Sample selection
st.set_page_config(page_title="Insights v4.0 (beta)", layout="wide")
interface.init()
interface.subheader("Insights v4.0 (beta)")
interface.status("Done.")

sample = load.run()

# -------- Subsample and assay selection
workflow_steps = selection.run(sample)

# -------- Assay processing
workflow_steps.run()
