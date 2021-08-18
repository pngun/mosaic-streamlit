import os
import shutil
import time

import interface
import missionbio.mosaic.io as mio
import numpy as np
import workflows.general.analysis as ann


class Compute:
    def __init__(self, arguments):
        self.arguments = arguments

    def filter_labs(self):
        args = self.arguments
        assay = ann.data.sample.dna

        keep = np.array([True] * assay.shape[0])

        for labtype in args.drop_labels:
            labs = ann.data.get_labels(assay, labtype)
            droplabs = args.drop_labels[labtype]
            keep = np.logical_and(keep, ~np.isin(labs, droplabs))

        bars = assay.barcodes()[keep]

        if len(bars) == 0:
            interface.error("All the cells were dropped from the sample.")

        args.subsample = ann.data.sample[bars]

    def export(self):
        args = self.arguments

        if args.export_kind == args.H5:
            name = f"./{ann.data.sample.name}.{int(time.time()):02x}.analyzed.h5"
            if os.path.exists(name):
                os.remove(name)

            mio.save(ann.data.sample, name)
            interface.download(name)

        elif args.export_kind == args.CSV:
            name = f"./{ann.data.sample.name}.data"
            if os.path.exists(name):
                shutil.rmtree(name)

            os.mkdir(name)

            assay_names = ann.data.available_assays()
            all_assays = [ann.data.get_assay(name) for name in assay_names]
            for assay in all_assays:
                os.mkdir(f"{name}/{assay.name}")
                os.mkdir(f"{name}/{assay.name}/layers")
                os.mkdir(f"{name}/{assay.name}/rows")

                for layer in assay.layers.keys():
                    df = assay.get_attribute(layer, constraint="row+col")
                    cols = list(df.columns.values)
                    df.loc[:, "label"] = assay.get_labels()
                    df = df.loc[:, ["label"] + cols]
                    df.to_csv(f"{name}/{assay.name}/layers/{layer}.csv")

                for row in assay.row_attrs.keys():
                    df = assay.get_attribute(row, constraint="row")
                    cols = list(df.columns.values)
                    df.loc[:, "label"] = assay.get_labels()
                    df = df.loc[:, ["label"] + cols]
                    df.to_csv(f"{name}/{assay.name}/rows/{row}.csv")

            shutil.make_archive(f"{name}", "zip", name)
            interface.download(f"{name}.zip")
            shutil.rmtree(name)
            os.remove(f"{name}.zip")

    def visual(self):

        args = self.arguments
        sample = args.subsample
        kind = args.visual_type
        args.fig = None

        interface.status(f"Creating {kind}.")

        available_assays = ann.data.available_assays()

        if kind == args.FISHPLOT:
            if len(args.sample_order) == 1:
                interface.error("More than one sample required for a fish plot.")

            assay = ann.data.get_assay(args.assay_name)
            args.fig = ann.cached_func(assay.fishplot, assay, sample_order=args.sample_order, label_order=args.label_order)

        if kind == args.BARPLOT:
            assay = ann.data.get_assay(args.assay_name)
            args.fig = ann.cached_func(assay.barplot, assay, sample_order=args.sample_order, label_order=args.label_order, percentage=args.percentage)

        elif kind == args.HEATMAP:
            check_assays = {args.clusterby, args.sortby} | ({"dna", "protein", "cnv"} - {args.drop})

            for assay_name in check_assays:
                if assay_name not in available_assays or not ann.data.is_analyzed(assay_name):
                    interface.error(f"Execution of the {assay_name} workflow is required to create this multi-omics plot.")

            args.fig = ann.cached_func(sample.heatmap, sample, clusterby=args.clusterby, sortby=args.sortby, drop=args.drop, flatten=False)

        if kind == args.DNA_ANALYTE_PLOT:

            if args.analyte not in available_assays or not ann.data.is_analyzed(args.analyte):
                interface.error(f"Execution of the {args.analyte} workflow is required to create this multi-omics plot.")

            sample.clone_vs_analyte(args.analyte)
