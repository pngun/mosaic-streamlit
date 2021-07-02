import interface
from segment import track

from .arguments import Arguments
from .compute import Compute
from .render import Render


class Steps:
    """
    The function of this class is to store the steps
    required to process the assay.

    Only the run method should be required to be called.
    When the run method is called, it must process all
    the steps with the latest user provided arguments.
    """

    def __init__(self):
        self.arguments = Arguments()
        self.render = Render(self.arguments)
        self.compute = Compute(self.arguments)
        self.firstpass = True

    @staticmethod
    def exposure_required(sample):
        return True

    def run(self):
        interface.subheader(f"Analyzing sample")
        track(f"Analyzing sample")

        self.filter_labs()
        self.export()
        self.visual()

        interface.status("Done.")
        track(f"Analyzing sample - Done")

    def filter_labs(self):
        self.render.filter_labs()
        self.compute.filter_labs()

    def export(self):
        exp = self.render.export()
        if exp:
            self.compute.export()

    def visual(self):
        self.render.layout()
        self.render.visual_arguments()

        self.compute.visual()
        self.render.visual()
