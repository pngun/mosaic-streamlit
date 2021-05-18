from missionbio.h5.constants import SAMPLE
from missionbio.mosaic.constants import SCALED_LABEL

import workflows.general.analysis as ann
from workflows.general.handler import ArgumentsHandler


class Arguments(ArgumentsHandler):
    """
    This class is an interface between rendering and
    computation. It must always inherit from the
    ArgumentsHandler class which automates most of
    the functionality required handling parameters.

    All arguments must have a default value. In the
    absence of the Render class, the Compute class
    must be able to run all the steps.

    Any value from this class object that is used
    in the Render or Compute class but not declared
    in one of the methods here will result in a
    workflows.generic.handler.ImplementationError.
    """

    def __init__(self):
        super().__init__("protein")

    def general_constants(self):
        self.PROTEIN_LABEL = "Protein Label"
        self.DENSITY = "Density"

    def preprocess(self):
        self.drop_ids = []
        self.ids = list(ann.data.sample.protein.ids())

        self.ASINH = "asinh"
        self.CLR = "CLR"
        self.NSP = "NSP"

        self.NORMALIZATIONS = [self.ASINH, self.CLR, self.NSP]

    def prepare(self):
        self.scale_attribute = "NSP"
        self.pca_attribute = SCALED_LABEL
        self.umap_attribute = SCALED_LABEL
        self.pca_comps = min(len(ann.data.sample.protein.ids()), 8)

    def cluster(self):
        self.method = "graph-community"
        self.cluster_attribute = "NSP"
        self.k = 20

        # Defaults for other clustering methods
        self.eps = 0.2
        self.n_clusters = 5
        self.min_cluster_size = 100

        # Defaults for gating
        self.layer = "NSP"
        self.features = ann.data.sample.protein.ids()[:2]
        self.thresholds = [0, 0]

        # Used for render
        self.cluster_description = "graph-community on NSP with neighbours set to 20"

    def customize(self):
        assay = ann.data.sample.protein

        self.label_map = {}
        self.palette = assay.get_palette()
        self.keep_labs = []
        self.subassay = assay

    def layout(self):
        self.args_container = None
        self.plot_container = None

        self.HEATMAP = "Heatmap"
        self.UMAP = "UMAP"

        self.FEATURE_SCATTER = "Feature Scatter"
        self.VIOLINPLOT = "Violin plot"
        self.RIDGEPLOT = "Ridge plot"
        self.STRIPPLOT = "Strip plot"

        self.visual_type = self.HEATMAP

    def visual(self):

        self.fig = None

        self.LAYERS = [self.NSP, self.CLR, self.ASINH]
        self.SPLITBY = [SAMPLE, None]
        self.COLORBY = [SAMPLE, self.DENSITY] + self.LAYERS + [None]

        self.fig_attribute = self.NSP
        self.splitby = self.PROTEIN_LABEL
        self.orderby = self.NSP
        self.cluster_heatmap = True
        self.convolve = 0

        self.colorby = self.PROTEIN_LABEL
        self.fig_features = []

        self.fig_layer = self.NSP

        self.points = False
