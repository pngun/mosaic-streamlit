import workflows.general.analysis as ann
from missionbio.h5.constants import SAMPLE
from missionbio.mosaic.constants import NORMALIZED_READS, PLOIDY
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
        super().__init__("cnv")

    def constants(self):
        self.DNA_LABEL = "Genotype Clone"

    def preprocess(self):
        self.ids = list(ann.data.sample.cnv.ids())
        self.min_cells = 50
        self.all_genes = []
        self.drop_genes = []
        self.keep_genes = []

    def prepare(self):
        self.ploidy_assay = ""
        self.diploid_cells = ""

    def layout(self):
        self.args_container = None
        self.plot_container = None

        self.HEATMAP = "Heatmap"
        self.LINEPLOT = "Line Plot"

        self.visual_type = self.HEATMAP

    def visual(self):

        self.fig = None

        self.LAYERS = [PLOIDY, NORMALIZED_READS]
        self.SPLITBY = [SAMPLE, None]
        self.POSITIONS = "positions"
        self.GENES = "genes"
        self.FEATURES = [self.POSITIONS, self.GENES]

        self.fig_attribute = PLOIDY
        self.splitby = ""
        self.fig_features = self.POSITIONS
        self.select_features = []
        self.cluster_heatmap = True
        self.convolve = 0

        self.clone = ""
        self.collapse = False
