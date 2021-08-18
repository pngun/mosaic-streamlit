import interface
import numpy as np
import pandas as pd
import workflows.general.analysis as ann
from missionbio.mosaic.constants import GENE_NAME, READS


class Compute:
    def __init__(self, arguments):
        self.arguments = arguments

    def annotations(self):
        if GENE_NAME not in ann.data.sample.cnv.col_attrs:
            interface.status(f"Fetching gene names.")
            ann.data.sample.cnv.get_gene_names()

            self.arguments.all_genes = sorted(list(set(ann.data.sample.cnv.col_attrs[GENE_NAME])))

    def preprocess(self):
        args = self.arguments
        interface.status("Processing CNV assay.")

        ann.data.sample.reset("cnv")
        assay = ann.data.sample.cnv

        drop_amps = np.isin(assay.col_attrs[GENE_NAME], args.drop_genes)

        if args.keep_genes:
            keep_amps = np.isin(assay.col_attrs[GENE_NAME], args.keep_genes)
        else:
            keep_amps = [True] * assay.shape[1]

        reads = assay.get_attribute(READS)
        per_cells = 100 * (reads > 0).sum(axis=0) / reads.shape[0]
        pass_amps = (per_cells > args.min_cells).values
        pass_amps = np.logical_and(pass_amps, keep_amps, ~drop_amps)

        if not pass_amps.any():
            interface.error("All amplicons were dropped. Reduce the thresholds for the filters.")

        ann.data.sample.cnv = ann.data.sample.cnv[:, pass_amps]

    def prepare(self):
        args = self.arguments
        assay = ann.data.sample.cnv

        interface.status(f"Preparing CNV data.")

        assay.normalize_reads()
        clones = ann.data.get_labels(assay, args.ploidy_assay)
        assay.set_labels(clones)
        assay.compute_ploidy(diploid_cells=assay.barcodes(args.diploid_cells))

    def visual(self):

        args = self.arguments
        assay = ann.data.sample.cnv
        kind = args.visual_type
        args.fig = None

        interface.status(f"Creating {kind}.")

        if kind == args.HEATMAP:
            if args.splitby in ann.data.available_labels():
                ann.data.set_label(assay, args.splitby)
                args.splitby = "label"

            bo = assay.clustered_barcodes(orderby=args.fig_attribute, splitby=args.splitby)
            if not args.cluster_heatmap:
                labels = assay.get_labels()[[np.where(assay.barcodes() == b)[0][0] for b in bo]]
                bo = []
                for lab in pd.unique(labels):
                    bo.extend(assay.barcodes(lab))
                bo = np.array(bo)

            feats = args.fig_features
            if len(args.select_features) != 0:
                feats = args.select_features

            args.fig = ann.cached_func(assay.heatmap, assay, attribute=args.fig_attribute, bars_order=bo, features=feats, convolve=args.convolve, splitby=args.splitby)

        elif kind == args.LINEPLOT:
            ann.data.set_label(assay, args.get("ploidy_assay"))

            if args.collapse:
                args.fig = ann.cached_func(assay.plot_ploidy, assay, cluster=args.clone, features="genes")
            else:
                args.fig = ann.cached_func(assay.plot_ploidy, assay, cluster=args.clone)

            args.fig.layout.width = 500
            args.fig.layout.width = 900
