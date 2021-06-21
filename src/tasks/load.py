import time

import missionbio.mosaic.io as mio
import numpy as np
import streamlit as st

import interface


def run():
    file, apply_filter = render()

    if file is None:
        interface.error("Please use the options available in the sidebar to load a sample.")

    sample = load(file, apply_filter)

    return sample


def render():
    with st.sidebar:
        cols = st.beta_columns([1, 10])

        apply_filter = cols[0].checkbox("", key="Filter")

        msg = st.markdown("<span style='color:red'>Load *only* those variants that pass minimum filters.</span>", unsafe_allow_html=True)
        cols[1].caption(str(msg))
        file = st.file_uploader("Load an H5 file")

    return file, apply_filter


@st.cache(max_entries=1, show_spinner=False, allow_output_mutation=True)
def load(file, apply_filter):
    interface.status("Reading h5 file.")

    sample = mio.load(file, apply_filter=apply_filter)
    sample.load_time = str(time.time())

    if sample.protein is not None:
        try:
            new_ids = np.array([ab.split(" ")[2] for ab in sample.protein.col_attrs["id"]])
        except IndexError:
            new_ids = sample.protein.ids()

        sample.protein.add_col_attr("id", new_ids)

    return sample
