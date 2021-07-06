import numpy as np
import pandas as pd
import requests
from missionbio.h5.constants import ID, NGT
from missionbio.mosaic.constants import AF_MISSING, NGT_FILTERED, UMAP_LABEL

import interface
import workflows.general.analysis as ann
from whitelist_import.columns import WHITELIST


class Compute:
    def __init__(self, arguments):
        self.no_internet_connection = False
        self.arguments = arguments
        ann.data.add_label(ann.data.sample.dna, self.arguments.DNA_LABEL)

    def preprocess(self):
        args = self.arguments
        interface.status("Processing Genotype assay.")

        ann.data.sample.reset("dna")

        whitelisted = ann.data.sample.dna.col_attrs[WHITELIST]
        white_vars = ann.data.sample.dna.ids()[whitelisted]

        if set(white_vars) & set(args.drop_ids) != set():
            interface.error("Cannot drop a whitelist variant.")

        if len(args.keep_ids) == 0:
            passed_vars = ann.data.sample.dna.filter_variants(min_dp=args.dp, min_gq=args.gq, min_vaf=args.af, min_std=args.std)
            dna_vars = set(passed_vars) - set(args.drop_ids)
        else:
            dna_vars = set(args.keep_ids)

        # Do not filter the whitelisted variants
        dna_vars = dna_vars | set(white_vars)

        if len(dna_vars) == 0:
            interface.error("No variants found. Adjust the filters and process again.")

        ann.data.sample.dna = ann.data.sample.dna[:, list(dna_vars)]

        # No filtering should be applied for the whitelisted variants
        ngt = ann.data.sample.dna.layers[NGT].copy()
        whitelisted = ann.data.sample.dna.col_attrs[WHITELIST]
        whitelisted_ngt = ann.data.sample.dna.layers[NGT_FILTERED].copy()
        whitelisted_ngt[:, whitelisted] = ngt[:, whitelisted]
        ann.data.sample.dna.add_layer(NGT_FILTERED, whitelisted_ngt)

    def annotations(self):
        args = self.arguments
        assay = ann.data.sample.dna
        variants = assay.ids()

        missing_variants = ~np.isin(variants, args.annotations[args.VARIANT])

        if missing_variants.any():
            interface.status("Fetching Genotype annotations")

            variants = variants[missing_variants]
            renamed_variants = np.array([var.replace(":", "-").replace("/", "-") for var in variants], dtype="str")

            url = "https://api.missionbio.io/annotations/v1/variants?ids=" + ",".join(renamed_variants)
            try:
                r = requests.get(url=url)
                data = r.json()
            except Exception:
                self.no_internet_connection = True
                data = {}

            data = [d["annotations"] for d in data]

            function = [", ".join(d["function"]["value"]) for d in data]
            gene = [d["gene"]["value"] for d in data]
            protein = [d["protein"]["value"] for d in data]
            coding_impact = [d["protein_coding_impact"]["value"] for d in data]
            clinvar = [", ".join(d["clinvar"]["value"]) for d in data]
            dann = np.array([d["impact"]["value"] for d in data])
            dann[dann == ""] = 0
            dann = np.round(dann.astype(float), 2)

            df = pd.DataFrame([gene, function, protein, coding_impact, clinvar, dann], index=args.annot_types).T
            df[args.VARIANT] = variants

            df = df[[args.VARIANT] + args.annot_types]

            args.annotations = pd.merge(args.annotations, df, how="outer")

    def prepare(self):
        args = self.arguments
        assay = ann.data.sample.dna

        interface.status(f"Preparing Genotype variants data.")

        assay.scale_data(args.scale_attribute)
        assay.run_pca(args.pca_attribute, components=args.pca_comps)
        assay.run_umap(attribute=args.umap_attribute, random_state=42)

    def cluster(self):
        args = self.arguments
        assay = ann.data.sample.dna

        interface.status(f"Clustering Genotype variants data.")

        kwargs = {"dbscan": {"eps": args.eps}, "hdbscan": {"min_cluster_size": args.min_cluster_size}, "graph-community": {"k": args.k}, "kmeans": {"n_clusters": args.n_clusters}}

        if args.method in ["dbscan", "hdbscan", "graph-community", "kmeans"]:
            if args.cluster_attribute not in assay.row_attrs.keys() and args.cluster_attribute not in assay.layers.keys():
                interface.error(f"{args.cluster_attribute} has not yet been set.")

            assay.cluster(method=args.method, attribute=args.cluster_attribute, **kwargs[args.method])
            assay.cluster_cleanup(AF_MISSING, args.similarity)
        elif args.method == "count":
            try:
                df = assay.count(layer=args.layer, min_clone_size=args.min_clone_size, group_missing=args.group_missing, ignore_zygosity=args.ignore_zygosity, features=args.features)
            except ValueError as ex:
                ex_message = str(ex)
                if ex_message == "At least on feature is needed to cluster.":
                    interface.error("Please select at least one variant to cluster")
                else:
                    raise ex

            if df is not None:
                lab_map = {}
                for clone in df.index:
                    score = df.loc[clone, "score"]
                    if score > 0:
                        new_name = f"{clone} ({score:.2f})"
                        lab_map[str(clone)] = new_name
                assay.rename_labels(lab_map)

        ann.data.add_label(assay, args.DNA_LABEL)

    def customize(self):
        args = self.arguments
        assay = ann.data.sample.dna

        label_changed = len(args.label_map) != 0
        color_changed = assay.get_palette() != args.palette

        if label_changed or color_changed:
            assay.rename_labels(args.label_map)
            assay.set_palette(args.palette)

        args.subassay = assay[assay.barcodes(args.keep_labs), :]

        ids = assay.ids()
        df = args.annotations.copy().astype(str)
        df.index = args.annotations[args.VARIANT]
        variant_data = df.loc[ids, args.id_format].values
        new_ids = np.array([":".join(v).strip(":") for v in variant_data])

        if len(set(new_ids)) != len(set(ids)):
            interface.error("Could not create a unique ID for each variant based on the given annotations.")

        args.subassay.add_col_attr(ID, new_ids)
        args.subassay.add_col_attr(args.VARIANT, ids)

        ann.data.add_label(assay, args.DNA_LABEL)

    def visual(self):

        if self.no_internet_connection:
            no_internet_connection_msg = "No internet connection, some annotations/values are not available."
            interface.warning(no_internet_connection_msg)

        args = self.arguments
        assay = args.subassay

        # Adding cluster information
        med_af, _, _, _ = assay.feature_signature(AF_MISSING)
        med_af = med_af.astype(int).astype(str)

        name = {0: "WT", 1: "HET", 2: "HOM", 3: "MISS"}
        med_ngt, _, _, _ = assay.feature_signature(NGT)
        med_ngt = med_ngt.applymap(lambda x: name[round(x)]).astype(str)

        missing = assay.get_attribute(NGT_FILTERED, constraint="row+col")
        missing = (missing == 3).sum(axis=0) / missing.shape[0]
        missing = np.round(100 * missing, 2).astype(str) + "%"

        clonedf = med_ngt + " (" + med_af + "%)"
        clonedf.loc[:, "%Cells missing"] = missing

        clonedf.index = assay.col_attrs[args.VARIANT].copy()

        var = assay.col_attrs[args.VARIANT].copy()
        show_id = np.isin(args.annotations[args.VARIANT], var)
        order = args.annotations.loc[show_id, args.VARIANT].values
        clonedf = clonedf.loc[order, :]

        args.shown_annotations = args.annotations[[args.VARIANT] + args.annot_types]
        args.shown_annotations = args.shown_annotations.loc[show_id, :]
        for lab in clonedf.columns:
            args.shown_annotations[lab] = clonedf[lab].values

        args.shown_annotations.index = np.arange(args.shown_annotations.shape[0]) + 1

        # Generate plots
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
            ann.data.set_label(assay, args.DNA_LABEL)

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

            modify_labels()
            args.fig = ann.cached_func(assay.scatterplot, assay, attribute=UMAP_LABEL, colorby=args.colorby, features=args.fig_features)
            reset_labels()

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

        elif kind == args.STRIPPLOT:
            args.fig = ann.cached_func(assay.stripplot, assay, attribute=args.fig_attribute, features=args.fig_features, colorby=args.colorby)
