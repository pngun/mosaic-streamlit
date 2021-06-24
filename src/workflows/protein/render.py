import numpy as np
import streamlit as st
from missionbio.mosaic.constants import PCA_LABEL, SCALED_LABEL, UMAP_LABEL

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
            args.drop_ids = form.multiselect("Antibodies to discard", args.ids, default=args.get("drop_ids"))

            clicked = form.form_submit_button("Process")

            return clicked

    def prepare(self):
        args = self.arguments
        with st.sidebar.beta_expander("Data preparation"):
            interface.info(
                f"Current transformations are:  \n" f"Scale on {args.get('scale_attribute')}  \n" f"PCA on {args.get('pca_attribute')}  \n" f"UMAP on {args.get('umap_attribute')}  \n",
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
        assay = ann.data.sample.protein

        METHODS = ["dbscan", "hdbscan", "graph-community", "kmeans", "gating"]

        CLUSTER_OPTIONS = {
            "dbscan": ("Proximity", 0.05, 2.0, args.get("eps"), "eps"),
            "hdbscan": ("Cluster size", 10, 500, args.get("min_cluster_size"), "min_cluster_size"),
            "kmeans": ("Neighbours", 2, 30, args.get("n_clusters"), "n_clusters"),
            "graph-community": ("Neighbours", 10, 500, args.get("k"), "k"),
        }

        with st.sidebar.beta_expander("Clustering"):
            interface.info(f"Currently clustered using {args.get('cluster_description')}")

            args.method = st.selectbox("Method", METHODS, index=2)

            if args.method == "gating":
                args.layer = st.selectbox("Layer", args.NORMALIZATIONS)

                data = assay.get_attribute(args.layer, constraint="row+col")
                columns = st.beta_columns([0.55, 0.75])
                with columns[0]:
                    feature_x = st.selectbox("Feature x", list(assay.ids()), index=0)
                    feature_y = st.selectbox("Feature y", list(assay.ids()), index=1)
                with columns[1]:
                    vals = data[feature_x].values
                    threshold_x = st.number_input("X threshold", float(min(vals)), float(max(vals)), float(vals.mean()), step=None)
                    vals = data[feature_y].values
                    threshold_y = st.number_input("Y Threshold", float(min(vals)), float(max(vals)), float(vals.mean()), step=None)

                fig = ann.cached_func(self.get_gating_plot, assay, args.layer, feature_x, feature_y, threshold_x, threshold_y)
                st.plotly_chart(fig, config={"displayModeBar": False})
                clicked = st.button("Cluster")

                description = f"gating on {args.layer}, with {feature_x} ({threshold_x:.2f}) and {feature_y} ({threshold_y:.2f})"

                args.features = [feature_x, feature_y]
                args.thresholds = [threshold_x, threshold_y]
            else:
                form = st.form("Clustering form")
                attrs = args.NORMALIZATIONS + [UMAP_LABEL, PCA_LABEL]
                args.cluster_attribute = form.selectbox("Attribute", attrs, key="Prepare Attribute", index=2)
                cluster_attr = form.slider(*CLUSTER_OPTIONS[args.method][:-1])
                setattr(args, CLUSTER_OPTIONS[args.method][-1], cluster_attr)

                description = f"{args.method} on {args.cluster_attribute} with {CLUSTER_OPTIONS[args.method][0].lower()} "
                description += f"set to {cluster_attr}"
                args.cluster_description = description

                clicked = form.form_submit_button("Cluster")

        return clicked

    def get_gating_plot(self, layer, feature_x, feature_y, threshold_x, threshold_y):
        assay = ann.data.sample.protein
        fig = assay.feature_scatter(layer=layer, ids=[feature_x, feature_y], colorby="density")
        fig.add_hline(y=threshold_y, line_width=2)
        fig.add_vline(x=threshold_x, line_width=2)
        fig.update_layout(
            coloraxis_showscale=False,
            title="",
            height=275,
            width=275,
            xaxis_fixedrange=True,
            yaxis_fixedrange=True,
            xaxis_title_font_size=10,
            yaxis_title_font_size=10,
            margin=dict(l=0, r=1, b=1, t=1),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_traces(hovertemplate="%{x:.2f}, %{y:.2f}<extra></extra>")

        return fig

    def customize(self):
        args = self.arguments
        assay = ann.data.sample.protein
        labs = ann.data.sample.protein.get_labels()
        pal = ann.data.sample.protein.get_palette()

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
                    new_name = st.text_input(f"Rename Cluster {lab}", lab)
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

        if len(args.keep_labs) == 0:
            interface.error("At least one label must be selected.")

        changed = len(args.label_map) > 0 or assay.get_palette() != args.palette

        return changed

    def layout(self):

        args = self.arguments

        VISUALS = [[1, 1, 1, 1, 1], [args.HEATMAP, args.UMAP, args.FEATURE_SCATTER, args.VIOLINPLOT, args.RIDGEPLOT]]

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

        SPLITBY = ann.data.available_labels(args.PROTEIN_LABEL) + args.SPLITBY
        COLORBY = ann.data.available_labels(args.PROTEIN_LABEL) + args.COLORBY

        kind = args.visual_type

        with args.args_container:
            if kind == args.HEATMAP:
                args.fig_attribute = st.selectbox("Attribute", args.LAYERS, key="Visualization Attribute")
                args.splitby = st.selectbox("Group by on Y-axis", SPLITBY)
                args.orderby = st.selectbox("Order by", args.LAYERS, key="Visualization Orderby")
                args.cluster_heatmap = st.checkbox("Cluster within labels", True)
                args.convolve = st.slider("Smoothing", 0, 100)

            elif kind == args.UMAP:
                args.colorby = st.selectbox("Color by", COLORBY)
                args.fig_features = None
                if args.colorby not in SPLITBY + [args.DENSITY]:
                    args.fig_features = st.multiselect("Choose X-axis", list(assay.ids()), list(assay.ids())[: min(len(assay.ids()), 4)])
                    if len(args.fig_features) == 0:
                        args.fig_features = None

            elif kind == args.FEATURE_SCATTER:
                args.fig_layer = st.selectbox("Layer", args.LAYERS)
                feature1 = st.selectbox("Feature 1", list(assay.ids()), index=0)
                feature2 = st.selectbox("Feature 2", list(assay.ids()), index=2)
                args.fig_features = [feature1, feature2]
                args.colorby = st.selectbox("Color by", COLORBY)

            elif kind == args.VIOLINPLOT:
                args.fig_attribute = st.selectbox("Attribute", args.LAYERS)
                args.splitby = st.selectbox("Group by on Y-axis", SPLITBY)
                args.points = st.checkbox("Box and points", False)
                args.fig_features = st.multiselect("Choose X-axis", list(assay.ids()), list(assay.ids())[: min(len(assay.ids()), 2)])
                if len(args.fig_features) == 0:
                    args.fig_features = None

            elif kind == args.RIDGEPLOT:
                args.fig_attribute = st.selectbox("Attribute", args.LAYERS)
                args.splitby = st.selectbox("Group by on Y-axis", SPLITBY)
                args.fig_features = st.multiselect("Choose X-axis", list(assay.ids()), list(assay.ids())[: min(len(assay.ids()), 4)])
                if len(args.fig_features) == 0:
                    args.fig_features = None

    def visual(self):

        args = self.arguments

        with args.plot_container:

            if args.fig is not None:
                args.fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(args.fig)
