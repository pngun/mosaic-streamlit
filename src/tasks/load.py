import os
import tempfile
import time

import missionbio.mosaic.io as mio
import numpy as np
import streamlit as st
from missionbio.h5.data.reader import H5Reader

import interface
from whitelist_import.bed_reader import BedReader
from whitelist_import.columns import ALT, CHROM, POS, REF


def run():
    file, apply_filter, whitelist_file = render()

    if file is None:
        status = "Only 1 file can be analyzed at a time. Multiple files are not allowed.<br />Please pre-merge h5 files (for multi-sample, one-patient) prior to analysis."
        interface.error("Please use the options available in the sidebar to load a sample.", status)

    sample = load(file, apply_filter, whitelist_file)

    return sample


def render():
    with st.sidebar:
        cols = st.beta_columns([11])
        apply_filter = cols[0].checkbox("Load only pass-filter variants", value=True, key="Filter")
        file = st.file_uploader("Load an H5 file")
        whitelist_file = st.file_uploader("Load a whitelist file")

        if os.getenv("MOSAIC_STREAMLIT_DEBUG") == "true":
            button = st.button("Trigger Sentry error")
            if button:
                raise Exception("Sentry test error from Streamlit")

    return file, apply_filter, whitelist_file


def load_whitelist_from_file(fp):
    with tempfile.TemporaryDirectory() as td:
        tmp_path = td + "/" + fp.name
        with open(tmp_path, "wb") as tf:
            tf.write(fp.read())
        return BedReader().read(tmp_path)


@st.cache(max_entries=1, show_spinner=False, allow_output_mutation=True)
def load(file, apply_filter, whitelist_file):
    interface.status("Reading h5 file.")

    def _variant_to_dict(s):
        data = s.split(":")
        chrom = data[0]
        if chrom.startswith("chr"):
            chrom = chrom[3:]
        pos = int(data[1])
        ref, alt = data[2].split("/")
        return {CHROM: chrom, POS: pos, REF: ref, ALT: alt}

    if whitelist_file:
        whitelist = load_whitelist_from_file(whitelist_file)
        with H5Reader(file) as reader:
            whitelist_variants = []
            variants = reader.read_col("dna_variants", "id")
            for v in variants:
                wl_filter = whitelist.filter_variants
                if wl_filter(_variant_to_dict(v)):
                    whitelist_variants.append(v)
    else:
        whitelist_variants = None

    sample = mio.load(file, apply_filter=apply_filter, whitelist=whitelist_variants)
    sample.load_time = str(time.time())

    if sample.protein is not None:
        try:
            new_ids = np.array([ab.split(" ")[2] for ab in sample.protein.col_attrs["id"]])
        except IndexError:
            new_ids = sample.protein.ids()

        sample.protein.add_col_attr("id", new_ids)

    return sample
