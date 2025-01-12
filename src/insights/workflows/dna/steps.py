import interface
import workflows.general.analysis as ann
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
        self.firstpass = not self.is_analyzed()

        ann.data.add_workflow(self)

    @staticmethod
    def exposure_required(sample):
        return sample.dna is not None

    def is_analyzed(self):
        return set(ann.data.sample.dna.get_labels()) != {"-"}

    def run(self):
        interface.subheader(f"Analyzing Genotype variants")
        track("Analyzing Genotype variants")

        self.preprocess()
        self.prepare()
        self.cluster()
        self.customize()
        self.visual()

        # After all steps have been performed at least once, call them only when required.
        self.firstpass = False

        interface.status("Done.")
        track("Analyzing Genotype variants - Done")

    def preprocess(self):
        clicked = self.render.preprocess()
        if self.firstpass or clicked:
            self.compute.preprocess()
            self.arguments.save()

        if clicked:
            interface.rerun()

        self.compute.annotations()

    def prepare(self):
        clicked = self.render.prepare()
        if clicked:
            self.compute.prepare()
            self.arguments.save()
            interface.rerun()

    def cluster(self):
        clicked = self.render.cluster()
        if self.firstpass or clicked:
            self.compute.cluster()
            self.arguments.save()

        if clicked:
            interface.rerun()

    def customize(self):
        changed = self.render.customize()
        self.compute.customize()
        self.arguments.save()

        if changed:
            interface.rerun()

    def visual(self):
        self.render.layout()
        self.render.visual_arguments()

        self.compute.visual()
        self.render.visual()
