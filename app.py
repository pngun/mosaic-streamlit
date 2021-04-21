import streamlit as st

import interface
from defaults import GUI_FRONTEND_RUNNING
from tasks import cluster, customize, load, prepare, preprocess, save, visual

st.set_page_config(page_title="Mosaic", layout="wide")
interface.init()
if not GUI_FRONTEND_RUNNING:
    interface.subheader("GUI for Mosaic built using Streamlit")
    interface.status("v0.4.1")

sample, should_save, save_name = load.run()

current_assay, available_assays = preprocess.run(sample)

prepare.run(current_assay, available_assays)
cluster.run(current_assay, available_assays)

sample_kept, current_assay_kept = customize.run(sample, current_assay)

visual_type = visual.run(sample_kept, current_assay_kept)

if should_save:
    save.run(sample_kept, save_name)

save.store_metadata(sample, current_assay, visual_type, available_assays)
