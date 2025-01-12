# FIXME: setup Sentry for all builds until we figure out what we need
import atexit
import sys

from segment import track
from sentry import setup_sentry
from sentry_sdk import capture_exception

atexit.register(lambda: track("Application Closed"))

setup_sentry()

script_runner = sys.modules["streamlit.script_runner"]

streamlit_handle_exception = script_runner.handle_uncaught_app_exception  # type: ignore


def catch_streamlit_exceptions(e):
    capture_exception(e)
    streamlit_handle_exception(e)


script_runner.handle_uncaught_app_exception = catch_streamlit_exceptions  # type: ignore


import streamlit.server.server_util  # noqa: E402

streamlit.server.server_util.MESSAGE_SIZE_LIMIT = 500 * 1e6

import interface  # noqa: E402
import streamlit as st  # noqa: E402
from tasks import load, selection  # noqa: E402

track("Application Launched")

# -------- Sample selection
st.set_page_config(page_title="Tapestri Insights v4.0 b1", layout="wide")
interface.init()
interface.subheader("Tapestri Insights v4.0 b1")
interface.status("Done.")

sample = load.run()

# -------- Subsample and assay selection
workflow_steps = selection.run(sample)

# -------- Assay processing
workflow_steps.run()
