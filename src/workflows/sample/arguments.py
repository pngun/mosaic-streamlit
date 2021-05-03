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
        super().__init__("sample")

    def filter_labs(self):
        self.subsample = None
        self.drop_labels = {}

    def export(self):
        self.H5 = "H5 File"
        self.CSV = "CSV Files"
        self.export_options = [self.H5, self.CSV]
        self.export_kind = "H5"

    def layout(self):
        self.args_container = None
        self.plot_container = None

        self.FISHPLOT = "Fishplot"
        self.BARPLOT = "Barplot"
        self.HEATMAP = "Multiomic Heatmap"
        self.DNA_ANALYTE_PLOT = "DNA vs Analyte"

        self.MULTISAMPLE = "Multisample"
        self.MULTIOMIC = "Multiomic"

        self.visual_type = self.FISHPLOT
        self.category = self.MULTISAMPLE

    def visual(self):

        self.fig = None

        self.assay_name = "dna"
        self.sample_order = []
        self.label_order = []
        self.percentage = False

        self.clusterby = "dna"
        self.sortby = "dna"
        self.drop = "cnv"

        self.analyte = "cnv"
