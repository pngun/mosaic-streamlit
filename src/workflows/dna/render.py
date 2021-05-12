import numpy as np
import streamlit as st
from missionbio.h5.constants import NGT
from missionbio.mosaic.constants import AF_MISSING, NGT_FILTERED, PCA_LABEL, SCALED_LABEL, UMAP_LABEL

import interface
import workflows.general.analysis as ann


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
        with st.sidebar.beta_expander("Preprocessing"):
            interface.info(f"{len(args.ids)} features available")

            form = st.form("Preprocessing form")
            args.dp = form.slider("Minimum read depth (DP)", min_value=0, max_value=100, value=int(args.get("dp")))
            args.gq = form.slider("Minimum genotype quality (GQ)", min_value=0, max_value=100, value=int(args.get("gq")))
            args.af = form.slider("Minimum allele frequency (VAF)", min_value=0, max_value=100, value=int(args.get("af")))
            args.std = form.slider("Minimum standard deviation of AF", min_value=0, max_value=100, value=int(args.get("std")))

            args.drop_ids = form.multiselect("Variants to discard", args.ids, default=args.get("drop_ids"))
            args.keep_ids = form.multiselect("Variants to keep", args.ids, default=args.get("keep_ids"))

            if len(args.keep_ids) != 0 and len(args.drop_ids) != 0:
                interface.error("Cannot keep and drop variants both. Choose only one of the options")

            clicked = form.form_submit_button("Process")

            return clicked

    def prepare(self):
        args = self.arguments
        with st.sidebar.beta_expander("Data preparation"):
            interface.info(
                f"Current transformations are:  \n" + f"Scale on {args.get('scale_attribute')}  \n" + f"PCA on {args.get('pca_attribute')}  \n" + f"UMAP on {args.get('umap_attribute')}  \n",
            )

            form = st.form("Data Preparation form")
            args.scale_attribute = form.selectbox("Scale - Attribute", args.LAYERS)
            args.pca_attribute = form.selectbox("PCA - Attribute", [SCALED_LABEL] + args.LAYERS)
            args.pca_comps = form.slider("Number of components", 3, 20, args.get("pca_comps"))
            args.umap_attribute = form.selectbox("UMAP - Attribute", [PCA_LABEL, SCALED_LABEL] + args.LAYERS)

            clicked = form.form_submit_button("Prepare")

        return clicked

    def cluster(self):

        args = self.arguments
        assay = ann.data.sample.dna

        METHODS = ["dbscan", "hdbscan", "graph-community", "kmeans", "count"]

        CLUSTER_OPTIONS = {
            "dbscan": ("Proximity", 0.05, 2.0, args.get("eps"), "eps"),
            "hdbscan": ("Cluster size", 10, 500, args.get("min_cluster_size"), "min_cluster_size"),
            "kmeans": ("Neighbours", 2, 30, args.get("n_clusters"), "n_clusters"),
            "graph-community": ("Neighbours", 10, 500, args.get("k"), "k"),
        }

        with st.sidebar.beta_expander("Clustering"):
            interface.info(f"Currently clustered using {args.get('cluster_description')}")

            args.method = st.selectbox("Method", METHODS, index=2)
            form = st.form("Clustering form")

            if args.method == "count":
                args.layer = form.selectbox("Layer", [NGT, NGT_FILTERED])
                args.min_clone_size = form.slider("Minimum clone size (%)", 0.0, 10.0, value=args.get("min_clone_size"))
                args.group_missing = form.checkbox("Group missing", args.get("group_missing"))
                args.ignore_zygosity = form.checkbox("Ignore Zygosity", args.get("ignore_zygosity"))
                args.features = form.multiselect("Variants", list(assay.ids()), default=args.get("features"))

                description = f"{args.layer} counts on {len(args.features)} variants with {args.min_clone_size}% minimum clone size"
                if args.ignore_zygosity:
                    description += ", ignoring zygosity"
                if args.group_missing:
                    description += ", and grouped missing clones"
                args.cluster_description = description

            else:
                args.cluster_attribute = form.selectbox("Attribute", [UMAP_LABEL, PCA_LABEL, AF_MISSING], key="Prepare Attribute", index=2)
                cluster_attr = form.slider(*CLUSTER_OPTIONS[args.method][:-1])
                setattr(args, CLUSTER_OPTIONS[args.method][-1], cluster_attr)
                args.similarity = form.slider("Similarity", 0.0, 1.0, 0.8)

                description = f"{args.method} on {args.cluster_attribute} with {CLUSTER_OPTIONS[args.method][0].lower()} "
                description += f"set to {cluster_attr} with {args.similarity} similarity"
                args.cluster_description = description

            clicked = form.form_submit_button("Cluster")

        return clicked

    def customize(self):
        args = self.arguments
        assay = ann.data.sample.dna
        labs = ann.data.sample.dna.get_labels()
        pal = ann.data.sample.dna.get_palette()

        with st.sidebar.beta_expander("Customizations"):
            interface.info("Rename the clusters or merge them by giving them the same name")

            args.label_map = {}
            args.keep_labs = []
            args.palette = pal

            lab_set, cnts = np.unique(labs, return_counts=True)
            lab_set = lab_set[cnts.argsort()[::-1]]
            for lab in lab_set:
                col1, col2, col3 = st.beta_columns([0.9, 0.15, 0.15])
                with col1:
                    new_name = st.text_input(f"Give a new name to {lab}", lab)
                with col2:
                    st.markdown(f"<p style='margin-bottom:34px'></p>", unsafe_allow_html=True)
                    args.palette[lab] = st.color_picker("", args.palette[lab], key=f"colorpicker-{lab}")
                with col3:
                    st.markdown(f"<p style='margin-bottom:42px'></p>", unsafe_allow_html=True)
                    keep = st.checkbox("", True, key=f"keep-cells-{lab}-{lab_set}")
                    if keep:
                        args.keep_labs.append(lab)

                if new_name != lab:
                    args.keep_labs[-1] = new_name
                    args.label_map[lab] = new_name
                    args.palette[new_name] = args.palette[lab]
                    del args.palette[lab]

            st.caption("---")
            interface.info("Format of the id names")
            args.id_format = st.multiselect("Annotation Order", [args.VARIANT] + args.annot_types, default=args.get("id_format"))

        if len(args.keep_labs) == 0:
            interface.error("At least one label must be selected.")

        changed = len(args.label_map) > 0 or assay.get_palette() != args.palette

        return changed

    def layout(self):

        args = self.arguments

        VISUALS = [[1, 1, 1, 1, 1], [args.HEATMAP, args.UMAP, args.VIOLINPLOT, args.RIDGEPLOT, args.STRIPPLOT]]

        kind = args.visual_type
        options = VISUALS[1]
        column_sizes = VISUALS[0]

        columns = st.beta_columns(column_sizes)
        for i in range(len(options)):
            with columns[i]:
                clicked = st.button(options[i], key=f"visual-{options[i]}")
                if clicked:
                    kind = options[i]
                    args.visual_type = kind

        columns = st.beta_columns([0.75, 0.1, 2])
        with columns[0]:
            st.caption("---")

        args.args_container = columns[0]
        args.plot_container = columns[2]

    def visual_arguments(self):

        args = self.arguments
        assay = args.subassay

        SPLITBY = ann.data.available_labels(args.DNA_LABEL) + args.SPLITBY
        COLORBY = ann.data.available_labels(args.DNA_LABEL) + args.COLORBY

        kind = args.visual_type

        with args.args_container:
            if kind == args.HEATMAP:
                args.fig_attribute = st.selectbox("Attribute", args.LAYERS, key="Visualization Attribute")
                args.splitby = st.selectbox("Split by", SPLITBY)
                args.orderby = st.selectbox("Order by", args.LAYERS, key="Visualization Orderby")
                args.cluster_heatmap = st.checkbox("Cluster within labels", True)
                args.convolve = st.slider("Smoothing", 0, 100)

            elif kind == args.UMAP:
                args.colorby = st.selectbox("Color by", COLORBY)
                args.fig_features = None
                if args.colorby not in SPLITBY + [args.DENSITY]:
                    args.fig_features = st.multiselect("Features", list(assay.ids()), list(assay.ids())[: min(len(assay.ids()), 4)])
                    if len(args.fig_features) == 0:
                        args.fig_features = None

            elif kind == args.VIOLINPLOT:
                args.fig_attribute = st.selectbox("Attribute", args.LAYERS)
                args.splitby = st.selectbox("Split by", SPLITBY)
                args.points = st.checkbox("Box and points", False)
                args.fig_features = st.multiselect("Features", list(assay.ids()), list(assay.ids())[: min(len(assay.ids()), 2)])
                if len(args.fig_features) == 0:
                    args.fig_features = None

            elif kind == args.RIDGEPLOT:
                args.fig_attribute = st.selectbox("Attribute", args.LAYERS)
                args.splitby = st.selectbox("Split by", SPLITBY)
                args.fig_features = st.multiselect("Features", list(assay.ids()), list(assay.ids())[: min(len(assay.ids()), 4)])
                if len(args.fig_features) == 0:
                    args.fig_features = None

            elif kind == args.STRIPPLOT:
                args.fig_attribute = st.selectbox("Attribute", args.LAYERS)
                args.colorby = st.selectbox("Colorby", args.LAYERS)
                args.fig_features = st.multiselect("Features", list(assay.ids()))
                if len(args.fig_features) == 0:
                    args.fig_features = None

    def visual(self):

        args = self.arguments

        with args.plot_container:

            if args.fig is not None:
                args.fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(args.fig)

        st.caption("---")

        def highlight_het_hom(v):
            if "HET" in v or "HOM" in v:
                return "background-color: #ededed"
            else:
                return ""

        df = args.annotations.astype(str).style.applymap(highlight_het_hom)
        st.dataframe(df, height=650)
