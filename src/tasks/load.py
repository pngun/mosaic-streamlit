import os
import tempfile
import time

import missionbio.mosaic.io as mio
import numpy as np
import streamlit as st
from missionbio.h5.data.reader import H5Reader

import interface
from whitelist_import.bed_reader import BedReader
from whitelist_import.columns import ALT, CHROM, POS, REF, WHITELIST


def run():
    file, apply_filter, whitelist_file = render()

    if file is None:
        status = "Only 1 file can be analyzed at a time. Multiple h5 files are not allowed.<br />Please pre-merge h5 files (for multi-sample, one-patient) prior to analysis."
        interface.error("Please use the options available in the sidebar to load a sample.", status)

    sample = load(file, apply_filter, whitelist_file)

    return sample


def render():
    with st.sidebar:
        cols = st.beta_columns([11])
        apply_filter = cols[0].checkbox("Load only pass-filter variants", value=True, key="Filter")

        # Use a single uploader to prevent double processing of the h5 file
        files = st.file_uploader("Load an H5 file and a whitelist", accept_multiple_files=True)

        if len(files) == 0:
            h5_file = None
            whitelist_file = None

        elif len(files) == 1:
            h5_file = files[0]
            whitelist_file = None
            if not h5_file.name.endswith(".h5"):
                interface.error("Please load an h5 file.")

        elif len(files) == 2:
            extensions = {file.name.split(".")[-1] for file in files}
            if extensions != {"h5", "bed"} and extensions != {"h5", "csv"}:
                interface.error("One file must be a .h5 and the other a .bed or .csv whitelist file.")

            for file in files:
                if file.name.endswith(".h5"):
                    h5_file = file
                elif file.name.endswith(".bed") or file.name.endswith(".csv"):
                    whitelist_file = file

        else:
            interface.error("Cannot load more than 1 h5 file and 1 whitelist file.")

        if os.getenv("MOSAIC_STREAMLIT_DEBUG") == "true":
            button = st.button("Trigger Sentry error")
            if button:
                raise Exception("Sentry test error from Streamlit")

    return h5_file, apply_filter, whitelist_file


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

    if apply_filter:
        # Specifically load the whitelisted variants as they might have been filtered
        sample = mio.load(file, apply_filter=apply_filter, whitelist=whitelist_variants)

    else:
        # All variants are loaded, even the whitelisted ones
        sample = mio.load(file)

    # Store the variants that were in the whitelist to prevent filtering during preprocessing
    whitelisted = np.isin(sample.dna.ids(), whitelist_variants)
    sample.dna.add_col_attr(WHITELIST, whitelisted)

    sample.load_time = str(time.time())

    if sample.protein is not None:
        try:
            new_ids = np.array([ab.split(" ")[2] for ab in sample.protein.col_attrs["id"]])
        except IndexError:
            new_ids = sample.protein.ids()

        sample.protein.add_col_attr("id", new_ids)

    return sample
