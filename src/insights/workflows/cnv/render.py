import streamlit as st
from missionbio.h5.constants import CHROM
from missionbio.mosaic.constants import GENE_NAME

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

    def preprocess(self):
        args = self.arguments
        with st.sidebar.expander("Preprocessing"):
            interface.info(f"{len(args.ids)} features available")

            form = st.form("Preprocessing form")
            args.min_cells = form.slider("Minimum cells with amplicon (%)", min_value=0, max_value=100, value=int(args.get("min_cells")))

            args.drop_genes = form.multiselect("Genes to drop", args.all_genes)
            args.keep_genes = form.multiselect("Genes to keep", args.all_genes)

            clicked = form.form_submit_button("Process")

            if args.keep_genes and args.drop_genes:
                interface.error("Only one of keep or drop genes can be selected.")

            return clicked

    def prepare(self):
        args = self.arguments
        assay = ann.data.sample.cnv

        with st.sidebar.expander("Data preparation", expanded=True):
            info = st.empty()

            LABELS = ann.data.available_labels(args.DNA_LABEL)
            args.ploidy_assay = st.selectbox("Reference assay", LABELS)

            clones = ann.data.get_labels(assay, args.ploidy_assay)
            clones = list(set(clones))

            form = st.form("Data Preparation form")
            args.diploid_cells = form.selectbox("Diploid cells", clones)

            clicked = form.form_submit_button("Prepare")

            interface.info(f"Ploidy calculation is performed by normalizing against cluster {args.diploid_cells} of {args.ploidy_assay}.", info)

        return clicked

    def layout(self):

        args = self.arguments

        VISUALS = [[1, 1, 4], [args.HEATMAP, args.LINEPLOT]]

        kind = args.visual_type
        options = VISUALS[1]
        column_sizes = VISUALS[0]

        columns = st.columns(column_sizes)
        for i in range(len(options)):
            with columns[i]:
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
        assay = ann.data.sample.cnv

        SPLITBY = ann.data.available_labels(args.ploidy_assay) + args.SPLITBY

        kind = args.visual_type

        with args.args_container:
            if kind == args.HEATMAP:
                args.fig_attribute = st.selectbox("Attribute", args.LAYERS, key="Visualization Attribute")
                args.splitby = st.selectbox("Group by on Y-axis", SPLITBY)
                args.fig_features = st.selectbox("Choose X-axis", args.FEATURES, key="Visualization features")

                if args.fig_features == args.POSITIONS:
                    subfeats = sorted(list(set(assay.col_attrs[CHROM])))
                elif args.fig_features == args.GENES:
                    subfeats = sorted(list(set(assay.col_attrs[GENE_NAME])))

                args.select_features = st.multiselect("Filter X-axis data", subfeats, key="Visualization subfeatures")
                args.cluster_heatmap = st.checkbox("Cluster within labels", True)
                args.convolve = st.slider("Smoothing", 0, 100)

            elif kind == args.LINEPLOT:
                clones = ann.data.get_labels(assay, args.get("ploidy_assay"))
                clones = list(set(clones))
                args.clone = st.selectbox("Clone", clones)
                args.collapse = st.checkbox("Collapse to gene", False)

    def visual(self):

        args = self.arguments

        with args.plot_container:

            if args.fig is not None:
                args.fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(args.fig)
