import streamlit as st

import interface
from tasks import (
    load,
    preprocess,
    prepare,
    cluster,
    customize,
    save,
    visual
)

st.set_page_config(page_title='Mosaic', layout='wide')
interface.init()
interface.subheader('GUI for Mosaic built using Streamlit')
interface.status('v0.2.0')

sample, should_save, save_name = load.run()

current_assay, available_assays = preprocess.run(sample)

prepare.run(current_assay, available_assays)
cluster.run(current_assay, available_assays)

sample_kept, current_assay_kept = customize.run(sample, current_assay)

visual_type = visual.run(sample_kept, current_assay_kept)

if should_save:
    save.run(sample_kept, save_name)

save.store_metadata(sample, current_assay, visual_type, available_assays)
