import pandas as pd
from missionbio.h5.constants import AF, DP, GQ, NGT, SAMPLE
from missionbio.mosaic.constants import AF_MISSING, NGT_FILTERED, SCALED_LABEL

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
        super().__init__("dna")

    def general_constants(self):
        self.DNA_LABEL = "DNA Label"
        self.DENSITY = "Density"

    def preprocess(self):
        """
        Compute Parameters
        ----------
        dp: int
            [0, 100] step=1
        gq: int
            [0, 100] step=1
        af: int
            [0, 100] step=1
        std: int
            [0, 100] step=1
        drop_ids: list
            One or more values of the dna.ids()
        keep_ids: list
            One or more values of the dna.ids()

        Render Parameters
        -----------------
        ids: list
            All the ids in the dna object
        """
        self.dp = 10
        self.gq = 30
        self.af = 20
        self.std = 20

        self.drop_ids = []
        self.keep_ids = []
        self.ids = list(ann.data.sample.dna.ids())

    def annotate(self):
        self.VARIANT = "Variant"
        self.annot_types = ["Gene", "Function", "Protein", "Coding Impact", "ClinVar", "DANN"]

    def prepare(self):
        """
        Compute Parameters
        ------------------
        scale_attribute: list
            [AF_MISSING, AF, NGT, NGT_FILTERED, GQ, DP]
        pca_attribute: list
            [AF_MISSING, AF, NGT, NGT_FILTERED, GQ, DP]
        umap_attribute: list
            [AF_MISSING, AF, NGT, NGT_FILTERED, GQ, DP]
        pca_comps: int
            [0, 20] step=1
        """

        self.scale_attribute = AF_MISSING
        self.pca_attribute = SCALED_LABEL
        self.umap_attribute = AF_MISSING
        self.pca_comps = min(len(ann.data.sample.dna.ids()), 8)

    def cluster(self):
        """
        method: str
            ["dbscan", "hdbscan", "graph-community", "kmeans", "count"]

        DBSCAN parameters
        -----------------
        attribute: str
            [UMAP_LABEL, PCA_LABEL, AF_MISSING]
        eps: float, default: 0.2
            [0.05, 2] step=0.01
        similarity: float
            [0.0, 1.0] step=0.01

        HDBSCAN parameters
        ------------------
        attribute: str
            [UMAP_LABEL, PCA_LABEL, AF_MISSING]
        min_cluster_size: int, default: 100
            [10, 500] step=1
        similarity: float
            [0.0, 1.0] step=0.01

        kmeans parameters
        -----------------
        attribute: str
            [UMAP_LABEL, PCA_LABEL, AF_MISSING]
        n_clusters: int, default: 5
            [2, 30] step=1
        similarity: float
            [0.0, 1.0] step=0.01

        Graph community (Louvain) parameters
        ------------------------------------
        attribute: str
            [UMAP_LABEL, PCA_LABEL, AF_MISSING]
        k: int, default: 100
            [10, 500] step=1
        similarity: float
            [0.0, 1.0] step=0.01

        count parameters
        -----------------
        layer: str
            [NGT, NGT_FILTERED]
        min_clone_size: float
            [0.0, 10.0] step=0.1
        group_missing: bool
        ignore_zygosity: bool
        features: list
            One or more ids from sample.dna.ids()

        Render parameters
        -----------------
        cluster_description: str
            Used to describe the current method used
        """
        self.method = "graph-community"
        self.cluster_attribute = AF_MISSING
        self.similarity = 0.8
        self.k = 20

        # Defaults for other clustering methods
        self.eps = 0.2
        self.n_clusters = 5
        self.min_cluster_size = 100

        # Defaults for count based
        self.layer = NGT
        self.min_clone_size = 1.0
        self.group_missing = True
        self.ignore_zygosity = False
        self.features = []

        # Used for render
        self.cluster_description = "graph-community on AF_MISSING with neighbours set to 20 with 0.8 similarity"

    def customize(self):
        """
        Compute parameters
        ------------------
        label_map: dict
            The key must be the old label
            and the value the new label.
        palette: dict
            The key must be the name of the
            label and the value the color of
            the cluster.
        """

        assay = ann.data.sample.dna

        self.label_map = {}
        self.palette = assay.get_palette()
        self.keep_labs = []
        self.subassay = assay
        self.id_format = ["Gene", self.VARIANT]

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

        self.LAYERS = [AF_MISSING, AF, NGT, NGT_FILTERED, GQ, DP]
        self.SPLITBY = [SAMPLE, None]
        self.COLORBY = [SAMPLE, self.DENSITY, AF, AF_MISSING, NGT, NGT_FILTERED, GQ, DP, None]

        self.fig_attribute = AF_MISSING
        self.splitby = self.DNA_LABEL
        self.orderby = AF_MISSING
        self.cluster_heatmap = True
        self.convolve = 0

        self.colorby = self.DNA_LABEL
        self.fig_features = []

        self.fig_layer = AF_MISSING

        self.points = False

        self.annotations = pd.DataFrame(columns=["Variant"])
        self.shown_annotations = self.annotations
