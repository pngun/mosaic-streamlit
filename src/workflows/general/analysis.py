import pandas as pd
import streamlit as st
from missionbio.mosaic.dna import Dna as modna
from missionbio.mosaic.protein import Protein as moprotein
from missionbio.mosaic.sample import Sample as mosample

import interface


class Data:
    def __init__(self, sample):
        self._original_sample = sample
        self.sample = sample

        self._assays = []
        self._workflows = {}

        self._labels = {}
        self._palette = {}

    def add_workflow(self, steps):
        self._workflows[steps.arguments.assaykey] = steps

    def is_analyzed(self, name):
        return self._workflows[name].is_analyzed()

    # Handling availability of assays
    def add_assay(self, name):
        self._assays.append(name)

    def get_assay(self, name):
        return getattr(self.sample, name)

    def available_assays(self):
        return self._assays

    # Sharing label information across assays
    def set_label(self, assay, name):
        if name not in self._labels:
            interface.error(f"{name} has not yet been set.")

        lab = self._labels[name].loc[assay.barcodes(), "label"].values
        pal = self._palette[name]
        assay.set_labels(lab)
        assay.set_palette(pal)

    def add_label(self, assay, name):
        self._labels[name] = pd.DataFrame(index=assay.barcodes())
        self._labels[name].loc[:, "label"] = assay.get_labels()
        self._palette[name] = assay.get_palette()

    def get_labels(self, assay, name):
        lab = self._labels[name].loc[assay.barcodes(), "label"].values

        return lab

    def available_labels(self, first_name=None):
        names = list(set(self._labels.keys()))

        if first_name is not None:
            names = list(set(names) - set([first_name]))
            names = [first_name] + names

        return names


# Used as a singleton
data = None


def assay_hash(a):
    palet = ",".join(a.get_palette().keys()) + ",".join(a.get_palette().values())

    hash_val = a.name + str(a.shape) + a.title + palet

    for k in a.row_attrs:
        data = a.row_attrs[k].flatten().astype(str)
        hash_val += ",".join(data)

    return hash_val


def sample_hash(s):
    hash_val = s.name + str(s.dna.shape) + s.load_time

    for a in [s.dna, s.cnv, s.protein]:
        if a is not None:
            hash_val += assay_hash(a)

    return hash_val


MOHASH_COMPLETE = {moprotein: assay_hash, modna: assay_hash, mosample: sample_hash}


@st.cache(max_entries=50, show_spinner=False, hash_funcs=MOHASH_COMPLETE, allow_output_mutation=True, ttl=3600)
def cached_func(method, assay, *args, **kwargs):
    """
    A wrapper for any function that needs to be cached.

    Currently used to draw plots which are cached.
    """

    return method(*args, **kwargs)
