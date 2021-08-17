import matplotlib.pyplot as plt
import streamlit as st
from missionbio.h5.constants import SAMPLE

import interface
import workflows.general.analysis as ann
from segment import track


class Render:
    """
    The function of this class to read the arguments
    from the Argument class and create an appropriate
    GUI for them. It must also provide feedback to the
    Compute class as to whether the step is to be
    processed or not.
    """

    def __init__(self, arguments):
        self.arguments = arguments

    def filter_labs(self):
        args = self.arguments
        assay = ann.data.sample.dna

        with st.sidebar.expander("Filter barcodes"):
            labtype = ann.data.available_labels()

            for lab in labtype:
                labs = sorted(list(set(ann.data.get_labels(assay, lab))))
                args.drop_labels[lab] = st.multiselect(f"Drop from {lab}", labs)

    def export(self):
        args = self.arguments

        with st.sidebar.expander("Export", expanded=True):
            info = st.empty()
            msg = "Export the analyzed data.  \n  \n"

            cols = st.columns([1, 1])
            with cols[0]:
                args.export_kind = st.selectbox("Format", args.export_options)

                if args.export_kind == args.H5:
                    msg += "Exported H5 files can be loaded in this app to retrieve this analysis."
                elif args.export_kind == args.CSV:
                    msg += "Data in the CSV files can be used to generate custom plots using other tools."

            with cols[1]:
                st.markdown(f"<p style='margin-bottom:36px'></p>", unsafe_allow_html=True)
                export = st.button("Export Data")

            interface.info(msg, info)

        return export

    def layout(self):

        args = self.arguments

        VISUALS = {args.MULTISAMPLE: [[0.75, 0.1, 0.3, 0.3, 1.4], [args.FISHPLOT, args.BARPLOT]], args.MULTIOMIC: [[0.75, 0.1, 0.5, 0.5, 1], [args.HEATMAP, args.DNA_ANALYTE_PLOT]]}

        options = VISUALS[args.category][1]
        column_sizes = VISUALS[args.category][0]

        columns = st.columns(column_sizes)
        with columns[0]:
            category = st.selectbox("", list(VISUALS.keys()))
            if category != args.category:
                args.category = category
                args.visual_type = VISUALS[category][1][0]
                interface.rerun()

        for i in range(len(options)):
            with columns[i + 2]:
                clicked = st.button(options[i], key=f"visual-{options[i]}")
                if clicked:
                    kind = options[i]
                    track(f"Plot {kind} clicked")
                    args.visual_type = kind

        columns = st.columns([0.75, 0.1, 2])
        with columns[0]:
            st.caption("---")

        args.args_container = columns[0]
        args.plot_container = columns[2]

    def visual_arguments(self):

        args = self.arguments
        kind = args.visual_type

        ANALYTE_MAP = {"protein": "Protein", "dna": "Genotype", "cnv": "CNV", None: None}
        available_assays = ann.data.available_assays().copy()

        with args.args_container:
            if kind == args.FISHPLOT:
                args.assay_name = st.selectbox("Assay", available_assays, format_func=lambda a: ANALYTE_MAP[a])

                assay = ann.data.get_assay(args.assay_name)
                samples = list(set(assay.row_attrs[SAMPLE]))
                labels = list(set(assay.get_labels()))
                args.sample_order = st.multiselect("Sample Order", samples)
                args.label_order = st.multiselect("Label Order", sorted(labels))
                if len(args.sample_order) == 0:
                    args.sample_order = samples
                if len(args.label_order) == 0:
                    args.label_order = labels

            if kind == args.BARPLOT:

                args.assay_name = st.selectbox("Assay", available_assays, format_func=lambda a: ANALYTE_MAP[a])

                assay = ann.data.get_assay(args.assay_name)
                samples = list(set(assay.row_attrs[SAMPLE]))
                labels = list(set(assay.get_labels()))
                args.sample_order = st.multiselect("Sample Order", samples)
                args.label_order = st.multiselect("Label Order", labels)
                if len(args.sample_order) == 0:
                    args.sample_order = samples
                if len(args.label_order) == 0:
                    args.label_order = labels
                args.percentage = st.checkbox("Percentage", False)

            elif kind == args.HEATMAP:
                args.clusterby = st.selectbox("Cluster by", available_assays, format_func=lambda a: ANALYTE_MAP[a])
                args.sortby = st.selectbox("Sort by", available_assays, format_func=lambda a: ANALYTE_MAP[a])
                args.drop = st.selectbox("Drop", ["dna", "cnv", "protein", None], format_func=lambda a: ANALYTE_MAP[a], index=2)

            elif kind == args.DNA_ANALYTE_PLOT:
                available_assays.remove("dna")
                args.analyte = st.selectbox("Analyte", available_assays, format_func=lambda a: ANALYTE_MAP[a])

    def visual(self):

        args = self.arguments

        with args.plot_container:

            if args.fig is not None:
                args.fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(args.fig)
            elif args.visual_type == args.DNA_ANALYTE_PLOT:
                st.pyplot(plt.gcf())
