import numpy as np
import pandas as pd
from missionbio.mosaic.constants import NORMALIZED_READS, UMAP_LABEL

import interface
import workflows.general.analysis as ann


class Compute:
    def __init__(self, arguments):
        self.arguments = arguments
        ann.data.add_label(ann.data.sample.protein, self.arguments.PROTEIN_LABEL)

    def preprocess(self):
        args = self.arguments

        interface.status("Processing protein assay.")

        ann.data.sample.reset("protein")
        if len(args.drop_ids) > 0:
            ann.data.sample.protein = ann.data.sample.protein.drop(args.drop_ids)

        interface.status("Normalizing data.")
        assay = ann.data.sample.protein
        for norm in [args.CLR, args.ASINH, args.NSP]:
            assay.normalize_reads(norm)
            assay.add_layer(norm, assay.layers[NORMALIZED_READS])

    def prepare(self):
        args = self.arguments
        assay = ann.data.sample.protein

        interface.status(f"Preparing protein data.")

        assay.scale_data(args.scale_attribute)
        assay.run_pca(args.pca_attribute, components=args.pca_comps)
        assay.run_umap(attribute=args.umap_attribute, random_state=42)

    def cluster(self):
        args = self.arguments
        assay = ann.data.sample.protein

        interface.status(f"Clustering protein data.")

        kwargs = {"dbscan": {"eps": args.eps}, "hdbscan": {"min_cluster_size": args.min_cluster_size}, "graph-community": {"k": args.k}, "kmeans": {"n_clusters": args.n_clusters}}

        if args.method in ["dbscan", "hdbscan", "graph-community", "kmeans"]:
            if args.cluster_attribute not in assay.row_attrs.keys() and args.cluster_attribute not in assay.layers.keys():
                interface.error(f"{args.cluster_attribute} has not yet been set.")

            assay.cluster(method=args.method, attribute=args.cluster_attribute, **kwargs[args.method])
        elif args.method == "gating":
            thres = args.thresholds
            feats = args.features
            lab_map = {}

            data = assay.get_attribute(args.layer, constraint="row+col")
            data = data[feats]
            bars = data.index.values
            lab_map[f"{feats[0]}+ & {feats[1]}+"] = bars[np.logical_and(data[feats[0]] > thres[0], data[feats[1]] > thres[1])]
            lab_map[f"{feats[0]}+ & {feats[1]}-"] = bars[np.logical_and(data[feats[0]] > thres[0], data[feats[1]] < thres[1])]
            lab_map[f"{feats[0]}- & {feats[1]}+"] = bars[np.logical_and(data[feats[0]] < thres[0], data[feats[1]] > thres[1])]
            lab_map[f"{feats[0]}- & {feats[1]}-"] = bars[np.logical_and(data[feats[0]] < thres[0], data[feats[1]] < thres[1])]

            assay.set_labels(lab_map)

        ann.data.add_label(assay, args.PROTEIN_LABEL)

    def customize(self):
        args = self.arguments
        assay = ann.data.sample.protein

        label_changed = len(args.label_map) != 0
        color_changed = assay.get_palette() != args.palette

        if label_changed or color_changed:
            assay.rename_labels(args.label_map)
            assay.set_palette(args.palette)

        args.subassay = assay[assay.barcodes(args.keep_labs), :]

        ann.data.add_label(assay, args.PROTEIN_LABEL)

    def visual(self):

        args = self.arguments
        assay = args.subassay
        kind = args.visual_type
        args.fig = None

        interface.status(f"Creating {kind}.")

        def modify_labels():
            if args.splitby in ann.data.available_labels():
                ann.data.set_label(assay, args.splitby)
                args.splitby = "label"

            if args.colorby in ann.data.available_labels():
                ann.data.set_label(assay, args.colorby)
                args.colorby = "label"

        def reset_labels():
            ann.data.set_label(assay, args.PROTEIN_LABEL)

        if kind == args.HEATMAP:
            modify_labels()
            bo = assay.clustered_barcodes(orderby=args.orderby, splitby=args.splitby)
            if not args.cluster_heatmap:
                labels = assay.get_labels()[[np.where(assay.barcodes() == b)[0][0] for b in bo]]
                bo = []
                for lab in pd.unique(labels):
                    bo.extend(assay.barcodes(lab))
                bo = np.array(bo)

            feats = assay.clustered_ids(orderby=args.orderby)

            # Need to convert types to ensure proper caching
            bo = bo.astype(str)
            feats = feats.values.astype(str)

            args.fig = ann.cached_func(assay.heatmap, assay, attribute=args.fig_attribute, bars_order=bo, features=feats, convolve=args.convolve, splitby=args.splitby)
            reset_labels()

        elif kind == args.UMAP:
            if UMAP_LABEL not in assay.row_attrs:
                interface.error("UMAP has not been run yet. Run it under the Data Preparation step.")

            if args.colorby in ann.data.available_labels() + args.SPLITBY:
                modify_labels()
                args.fig = ann.cached_func(assay.scatterplot, assay, attribute=UMAP_LABEL, colorby=args.colorby)
                reset_labels()
            elif args.colorby == args.DENSITY:
                args.fig = ann.cached_func(assay.scatterplot, assay, attribute=UMAP_LABEL, colorby="density")
            else:
                args.fig = ann.cached_func(assay.scatterplot, assay, attribute=UMAP_LABEL, colorby=args.colorby, features=args.fig_features)

        elif kind == args.FEATURE_SCATTER:
            if args.colorby in ann.data.available_labels() + args.SPLITBY:
                modify_labels()
                args.fig = ann.cached_func(assay.feature_scatter, assay, layer=args.fig_layer, ids=args.scatter_features, colorby=args.colorby)
                reset_labels()
            elif args.colorby == args.DENSITY:
                args.fig = ann.cached_func(assay.feature_scatter, assay, layer=args.fig_layer, ids=args.scatter_features, colorby="density")
            else:
                args.fig = ann.cached_func(assay.feature_scatter, assay, layer=args.fig_layer, ids=args.scatter_features, colorby=args.colorby, features=args.fig_features)

        elif kind == args.VIOLINPLOT:

            def violin_with_points(points, **kwargs):
                fig = assay.violinplot(**kwargs)
                if points:
                    fig.update_traces(points="all", pointpos=-0.5, box_width=0.6, side="positive", marker_size=3)
                return fig

            modify_labels()
            args.fig = ann.cached_func(violin_with_points, assay, points=args.points, attribute=args.fig_attribute, features=args.fig_features, splitby=args.splitby)
            reset_labels()

        elif kind == args.RIDGEPLOT:
            modify_labels()
            args.fig = ann.cached_func(assay.ridgeplot, assay, attribute=args.fig_attribute, features=args.fig_features, splitby=args.splitby)
            reset_labels()
