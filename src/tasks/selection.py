import importlib

import streamlit as st
from missionbio.mosaic.sample import Sample as mosample

import workflows.general.analysis as ann

"""
The key is the name of the module
of the workflow and the value is
the name that is shown in the app.
"""
AVAILABLE_WORKFLOWS = {"dna": "Genotype", "cnv": "CNV", "protein": "Protein", "sample": "Combined Multiomics Visualization"}

SAMPLE_HASH = {mosample: lambda s: s.name + s.load_time}


def run(sample):
    initialize_analysis(sample)
    steps = initialize_steps(sample)
    selected_assay = render(sample, steps)

    selected_steps = steps[selected_assay]

    return selected_steps


def render(sample, steps):
    with st.sidebar:
        all_assays = list(steps.keys())
        selected_assay = st.selectbox("Workflow", all_assays, format_func=lambda x: AVAILABLE_WORKFLOWS[x], key=sample.name + sample.load_time)

    return selected_assay


@st.cache(max_entries=1, show_spinner=False, hash_funcs=SAMPLE_HASH, allow_output_mutation=True)
def initialize_analysis(sample):
    ann.data = ann.Data(sample)


@st.cache(max_entries=1, show_spinner=False, hash_funcs=SAMPLE_HASH, allow_output_mutation=True)
def initialize_steps(sample):
    steps = {}

    for a in AVAILABLE_WORKFLOWS:
        step = getattr(importlib.import_module(f"workflows.{a}.steps"), "Steps")
        if step.exposure_required(sample):
            steps[a] = step()

    return steps
