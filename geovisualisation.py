import spacy
import pandas as pd
import plotly.express as px
import streamlit as st
import json
from collections import defaultdict

# Load spaCy model for NER
nlp = spacy.load("en_core_web_sm")

# Function to load crime categories from JSON file
def load_crime_keywords(json_path="crimes.json"):
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading crime keywords: {e}")
        return {}

# Crime keywords from the JSON file (not used in categorization now)
crime_keywords = load_crime_keywords()

def extract_gpe(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == "GPE"]

def read_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        if "Text" not in df.columns:
            st.error("The Excel file must contain a 'Text' column.")
            return pd.DataFrame()
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return pd.DataFrame()

def count_crimes_by_region(df):
    crime_counts_by_region = defaultdict(int)  # Just count crimes in regions

    for index, row in df.iterrows():
        text = row["Text"]
        gpe_entities = extract_gpe(text)
        
        for gpe in gpe_entities:
            crime_counts_by_region[gpe] += 1  # Increment crime count for this region

    # Convert to a DataFrame for easier plotting
    records = [{"Region": region, "Crime Count": count} for region, count in crime_counts_by_region.items()]
    return pd.DataFrame(records)

def plot_geo_visualization(df):
    # Find the min and max crime count for dynamic scaling
    min_count = df["Crime Count"].min()
    max_count = df["Crime Count"].max()

    # Plot the map with a dynamic color scale based on the min and max crime counts
    fig = px.choropleth(df,
                        locations="Region",  # Country/region names
                        locationmode="country names",
                        color="Crime Count",  # Color by crime count
                        hover_name="Region",
                        hover_data=["Crime Count"],
                        color_continuous_scale="Bluyl",  
                        range_color=[min_count, max_count],  # Set dynamic range based on data
                        title="Crime Incidents by Region")
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    fig.update_geos(showcoastlines=True, coastlinecolor="Black", projection_type="natural earth")
    return fig

# Streamlit app
st.title("Geo-Visualization of Crime Incidents")

uploaded_file = st.file_uploader("Upload the Excel File", type=["xlsx"])

if uploaded_file:
    df = read_from_excel(uploaded_file)
    if not df.empty:
        # Count the crimes by region
        geo_data = count_crimes_by_region(df)
        
        # Plot and display geo-visualization
        fig = plot_geo_visualization(geo_data)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No valid data found in the uploaded file.")
