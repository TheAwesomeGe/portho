import streamlit as st
import pandas as pd
import ast

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv("portho.csv", index_col="Token")
    drop_columns = ["Levenshtein Closest 100", "Damerau-Levenshtein Closest 100"]
    df = df.drop(columns=drop_columns)
    list_columns = ["Coltheart", "Levenshtein", "Damerau-Levenshtein", "Coltheart More Frequent", "Levenshtein More Frequent", "Damerau-Levenshtein More Frequent"]
    df[list_columns] = df[list_columns].map(ast.literal_eval)
    return df

neighbor_sets = ["Coltheart", "Levenshtein", "Damerau-Levenshtein"]
feature_map = {
    "ON": "Count",
    "ON Average Frequency": "Average Frequency",
    "ON Cumulative Frequency": "Cumulative Frequency"
}
distance_metrics_map = {"OLD": "Levenshtein", "ODLD": "Damerau-Levenshtein"}
nns = [10, 20, 50, 100]

st.set_page_config(
    layout="wide",
    page_title="Portho",
    page_icon=":scroll:"
)

# App title
st.sidebar.title("Portho")
st.sidebar.markdown('''Portho is a corpus-based lexical resource that provides orthographic neighbor metrics for over 43,000 word forms. In addition to classical neighborhood size measures, Portho provides frequency-based statistics (based on [AC/DC project](https://www.linguateca.pt/ACDC/) corpora), as well as graded orthographic distance features. Please read our [paper](/) for more details on the resource and its construction.''')


st.header("Portho: Orthographic Neighbors in European Portuguese")

with st.spinner("Loading data...", show_time=True):
    df = load_data()

with st.sidebar.expander("Orthographic Neighbors", expanded=True):

    neighbor_set = st.selectbox(
        "Neighbor set",
        options=neighbor_sets,
        key="neighbor_set"
    )

    show_neighbors = st.checkbox("Show neighbors", value=True, key="show_neighbors")

    show_more_frequent_neighbors = st.checkbox("More frequent neighbors", value=False, key="more_frequent_neighbors")

    feature_selection = st.pills(
        "Features",
        feature_map,
        selection_mode="multi",
        default=feature_map,
        format_func=lambda x: feature_map[x],
        key="feature_selection"
    )

with st.sidebar.expander("Orthographic Distance", expanded=True):

    distance_metric = st.selectbox(
        "Distance metric",
        options=distance_metrics_map,
        format_func=lambda x: distance_metrics_map[x],
        key="distance_metric"
    )

    show_od = st.checkbox("Show orthographic distance", value=True, key="show_od")

    n_neighbors = st.select_slider(
        "Number of nearest neighbors",
        options=nns,
        value=20,
        key="n_neighbors"
    )

with st.sidebar.expander("Download", expanded=False):

    left_col, right_col = st.columns(2)
    
    left_col.link_button(
        label="CSV",
        url="https://github.com/TheAwesomeGe/portho/raw/refs/heads/main/portho.csv",
        icon=":material/download:",
        width="stretch"
    )

    right_col.link_button(
        label="Excel",
        url="https://github.com/TheAwesomeGe/portho/raw/refs/heads/main/portho.xlsx",
        icon=":material/download:",
        width="stretch",
    )


selected_columns = {"Frequency": "Frequency"}
column_names = ["Frequency"]

if show_more_frequent_neighbors:
    if show_neighbors:
        selected_columns[f"{neighbor_set} More Frequent"] = "More Frequent Neighbors"
    selected_columns.update({f"{neighbor_set} More Frequent {feature}": feature_map[feature] for feature in feature_selection})
else:
    if show_neighbors:
        selected_columns[f"{neighbor_set}"] = "Neighbors"
    selected_columns.update({f"{neighbor_set} {feature}": feature_map[feature] for feature in feature_selection})

if show_od:
    selected_columns[f"{distance_metric}{n_neighbors}"] = f"{distance_metric}{n_neighbors}"

filter = st.text_input("Search for a token (regex supported)", placeholder="Type a token or regex pattern to filter the tokens", label_visibility="collapsed")


st.dataframe(df[selected_columns.keys()].loc[df.index.str.contains(filter)].rename(columns=selected_columns), width="stretch", height=600)