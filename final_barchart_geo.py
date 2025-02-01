import pandas as pd
import plotly.express as px
import streamlit as st
import spacy
import json
from collections import defaultdict

# Load spaCy model for NER
nlp = spacy.load("en_core_web_sm")

# Load crime categories from JSON file
def load_crime_keywords(json_path="crimes.json"):
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading crime keywords: {e}")
        return {}

# Crime keywords loaded from crimes.json
crime_keywords = load_crime_keywords()

# Function to read Excel file and return dataframe
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

# Simple keyword matching for offense classification
def classify_offenses(df):
    offense_counts = defaultdict(int)
    
    categories = []
    for text in df["Text"]:
        matched = False
        for category, keywords in crime_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                categories.append(category)
                offense_counts[category] += 1
                matched = True
                break
        if not matched:
            categories.append("Uncategorised")
    
    # Exclude "Uncategorised" from the counts
    offense_counts = {category: count for category, count in offense_counts.items() if category != "Uncategorised"}
    
    df["Category"] = categories
    return df, offense_counts

# Plot offense distribution using Plotly (excluding "Uncategorised")
def plot_offense_distribution(offense_counts):
    categories = list(offense_counts.keys())
    counts = list(offense_counts.values())

    # Create a DataFrame for Plotly plotting
    data = pd.DataFrame({"Category": categories, "Count": counts})

    # Plot a bar chart using Plotly
    fig = px.bar(data, x="Category", y="Count", 
                  title="Crime/Offense Category Distribution",
                  labels={"Category": "Crime Categories", "Count": "Number of Cases"},
                  text="Count", color="Category")

    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# Extract GPE (Geopolitical Entity) from text using spaCy
def extract_gpe(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == "GPE"]

# Count crimes by region (excluding "Uncategorised")
def count_crimes_by_region(df):
    crime_counts_by_region = defaultdict(int)

    for index, row in df.iterrows():
        text = row["Text"]
        gpe_entities = extract_gpe(text)
        
        for gpe in gpe_entities:
            crime_counts_by_region[gpe] += 1

    # Convert to a DataFrame for easier plotting
    records = [{"Region": region, "Crime Count": count} for region, count in crime_counts_by_region.items()]
    return pd.DataFrame(records)

# Plot geo-visualization map
def plot_geo_visualization(df):
    min_count = df["Crime Count"].min()
    max_count = df["Crime Count"].max()

    fig = px.choropleth(df,
                        locations="Region",
                        locationmode="country names",
                        color="Crime Count",
                        hover_name="Region",
                        hover_data=["Crime Count"],
                        color_continuous_scale="Bluyl",  
                        range_color=[min_count, max_count],
                        title="Crime Incidents by Region")
    
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    fig.update_geos(showcoastlines=True, coastlinecolor="Black", projection_type="natural earth")
    return fig

# Streamlit app setup
st.title("Crime Data Analysis Dashboard")

uploaded_file = st.file_uploader("Upload the Excel File", type=["xlsx"])

if uploaded_file:
    df = read_from_excel(uploaded_file)
    if not df.empty:
        # Classify offenses and plot the bar chart
        df, offense_counts = classify_offenses(df)
        
        st.subheader("News Excerpts with Categories")
        st.write(df[['Text', 'Category']])

        st.subheader("Crime Category Distribution")
        st.write(pd.DataFrame(offense_counts.items(), columns=["Category", "Count"]))
        
        plot_offense_distribution(offense_counts)

        # Plot the geo-visualization
        geo_data = count_crimes_by_region(df)
        fig = plot_geo_visualization(geo_data)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No valid data found in the uploaded file.")
