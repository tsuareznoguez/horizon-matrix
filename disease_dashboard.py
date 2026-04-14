import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# ----------------------------
# Page Title
# ----------------------------
st.title("Horizon Scanning Dashboard")

# ----------------------------
# File paths
# ----------------------------
main_file = "disease_data.csv"
info_file = "disease_info.csv"

# ----------------------------
# Show last update
# ----------------------------
mod_time = os.path.getmtime(main_file)
last_update = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
st.write(f"**Data last updated:** {last_update}")

# ----------------------------
# Load data
# ----------------------------
main_data = pd.read_csv(main_file)
info_data = pd.read_csv(info_file)
diseases = pd.read_csv("table_diseases.csv")

#data = data.loc[:, ~data.columns.str.contains("^Unnamed")]
# Merge datasets
#data = pd.merge(main_data, info_data, on="Disease", how="left")
data = pd.merge(main_data, info_data, on=["Disease", "Species"], how="left")

optional_cols = ["Link", "MapURL", "ImageURL"]

for col in optional_cols:
    if col not in data.columns:
        data[col] = None

# ----------------------------
# Risk categories
# ----------------------------
risk_labels = ["neg", "very low", "low", "medium", "high"]

data["Risk Category"] = pd.cut(
    data["X Value"],
    bins=5,
    labels=risk_labels,
    include_lowest=True
)

# Rename columns
data_renamed = data.rename(columns={
    "Disease": "Exotic diseases",
    "X Value": "Risk",
    "Y Value": "Impact"
})

# ----------------------------
# Species emoji mapping
# ----------------------------
species_icons = {
    "Cattle": "🐄",
    "Sheep": "🐑",
    "Goat": "🐐",
    "Pigs": "🐖",
#    "Swine": "🐖",
    "Poultry": "🐔",
    "Birds": "🐦",
    "Deer": "🦌",
    "Multiple": "🐾"
}

data_renamed["Species Icon"] = data_renamed["Species"].map(species_icons).fillna("🐾")

# ----------------------------
# Table display
# ----------------------------
st.write("### Disease Data Table")
st.dataframe(diseases[["Species", "Disease"]])

# ----------------------------
# Species Filter
# ----------------------------
species_list = sorted(data_renamed["Species"].dropna().unique())

selected_species = st.multiselect(
    "Filter by Species",
    species_list,
    default=species_list
)

filtered_data = data_renamed[data_renamed["Species"].isin(selected_species)]

# ----------------------------
# Plot styling
# ----------------------------
risk_colors = {
    "neg": "#6c757d",
    "very low": "#198754",
    "low": "#0dcaf0",
    "medium": "#ffc107",
    "high": "#dc3545"
}

marker_shapes = {
    "neg": "circle",
    "very low": "square",
    "low": "diamond",
    "medium": "triangle-up",
    "high": "star"
}

# ----------------------------
# Plot
# ----------------------------
fig = px.scatter(
    filtered_data,
    x="Risk",
    y="Impact",
    color="Risk Category",
    symbol="Risk Category",
    text="Exotic diseases",
    hover_name="Exotic diseases",
    hover_data=["Species"],
    custom_data=[
        "Exotic diseases",
        "Species",
        "Species Icon",
        "Info",
        "Link",
        "MapURL",
        "ImageURL",
        "Risk Category"
    ],
    color_discrete_map=risk_colors,
    symbol_map=marker_shapes
)

fig.update_traces(
    marker=dict(size=18, opacity=0.85, line=dict(width=1.5, color="white")),
    textposition="top center"
)

fig.update_layout(
    plot_bgcolor="#fafafa",
    paper_bgcolor="white",
    font=dict(family="Arial", size=14, color="#333"),
    title=dict(text="Impact Matrix", x=0.5, font=dict(size=22)),
    legend_title="Risk Category",
    margin=dict(l=40, r=20, t=60, b=40)
)

fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False)
fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False)

# ----------------------------
# Render plot with click
# ----------------------------
selected = st.plotly_chart(
    fig,
    key="disease_scatter",
    on_select="rerun"
)

# ----------------------------
# Sidebar
# ----------------------------
sidebar = st.sidebar
sidebar.title("Disease Details")

if not (selected and "selection" in selected and selected["selection"]["points"]):

    sidebar.info("👈 Click a bubble in the plot to view detailed information.")

else:

    point = selected["selection"]["points"][0]["customdata"]

    disease = point[0]
    species = point[1]
    species_icon = point[2]
    info = point[3]
    link = point[4]
    mapurl = point[5]
    imageurl = point[6]
    category = point[7]

    color_map = {
        "neg": "#6c757d",
        "very low": "#198754",
        "low": "#0dcaf0",
        "medium": "#ffc107",
        "high": "#dc3545"
    }

    badge_color = color_map.get(category, "#6c757d")

    # ----------------------------
    # Header
    # ----------------------------
    sidebar.markdown(f"""
    <div style="padding:15px;border-radius:10px;border:1px solid #ddd;background-color:#f8f9fa;">
        <h2 style="margin-bottom:0;">{disease}</h2>
        <p style="margin-top:5px;font-size:0.95rem;">
        {species_icon} <b>{species}</b>
        </p>
        <span style="
            display:inline-block;
            margin-top:8px;
            padding:4px 10px;
            background-color:{badge_color};
            color:white;
            border-radius:8px;
            font-size:0.85rem;">
            {category.title()} Risk
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------
    # Image
    # ----------------------------
    if pd.notna(imageurl):
        sidebar.image(imageurl, caption=disease, use_container_width=True)

    sidebar.markdown("---")

    # ----------------------------
    # Description
    # ----------------------------
    sidebar.markdown(f"""
    <div style="padding:12px;background-color:#ffffff;
                border-left:4px solid #0d6efd;border-radius:6px;">
        <strong>Description</strong><br>
        {info}
    </div>
    """, unsafe_allow_html=True)

    sidebar.markdown("---")

    # ----------------------------
    # Links
    # ----------------------------
    if pd.notna(link) or pd.notna(mapurl):
        sidebar.markdown("### 🔗 Resources")

    if pd.notna(link):
        sidebar.markdown(
            f'<a href="{link}" target="_blank">📄 More Information</a>',
            unsafe_allow_html=True
        )

    if pd.notna(mapurl):
        sidebar.markdown(
            f'<a href="{mapurl}" target="_blank">🗺 Open Map</a>',
            unsafe_allow_html=True
        )