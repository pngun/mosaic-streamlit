import streamlit as st

import interface
import defaults as DFT
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
interface.status('v0.1.3')

sample, should_save, save_name = load.run()
save.run(sample, save_name, should_save)

current_assay, available_assays = preprocess.run(sample)

prepare.run(current_assay, available_assays)
cluster.run(current_assay, available_assays)

sample_kept, current_assay_kept = customize.run(sample, current_assay)

visual_type = visual.run(sample_kept, current_assay_kept)

current_assay.add_metadata(DFT.VISUAL_TYPE, visual_type)
for a in available_assays:
    a.add_metadata(DFT.INITIALIZE, False)
