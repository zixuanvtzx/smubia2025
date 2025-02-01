import pandas as pd
import plotly.express as px
from collections import defaultdict
from ast import literal_eval

# Define keywords for each crime category
crime_keywords = {
    "Labor Violations": ["child labor", "wage theft", "unsafe working"],
    "Fraud": ["fraud", "scam", "embezzlement"],
    "Corruption": ["bribery", "kickback", "corruption"],
    "Violence": ["assault", "homicide", "murder"],
    "Cybercrime": ["hacking", "phishing", "data breach"],
    "Discrimination": ["racism", "sexism", "discrimination"],
    "Theft": ["theft", "burglary", "robbery"],
    "Sexual Misconduct": ["harassment", "molestation", "abuse"],
    "Traffic Violations": ["speeding", "drunk driving", "hit and run"],
    "Drugs": ["narcotics", "drug trafficking", "illegal substances"]
}

# Read Excel file function
def read_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        df.columns = ["Website", "Text", "Entities", "Relationships"]
        df.dropna(subset=["Website", "Text"], inplace=True)
        df["Entities"] = df["Entities"].apply(literal_eval)
        df["Relationships"] = df["Relationships"].apply(literal_eval)
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        return pd.DataFrame()

# Simple keyword matching for offense classification
def classify_offenses(text_list):
    offense_counts = defaultdict(int)

    for text in text_list:
        for category, keywords in crime_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                offense_counts[category] += 1

    return offense_counts

# Plot offense distribution using Plotly
def plot_offense_distribution(offense_counts):
    categories = list(offense_counts.keys())
    counts = list(offense_counts.values())

    # Create a DataFrame for Plotly plotting
    data = pd.DataFrame({"Category": categories, "Count": counts})

    # Plot a bar chart
    fig = px.bar(data, x="Category", y="Count", 
                  title="Crime/Offense Category Distribution",
                  labels={"Category": "Crime Categories", "Count": "Number of Cases"},
                  text="Count", color="Category")
    
    fig.update_layout(xaxis_tickangle=-45)
    fig.show()

# Main execution
file_path = 'insights_results.xlsx'  # Update with your file path
df = read_from_excel(file_path)

if not df.empty:
    offense_counts = classify_offenses(df["Text"].tolist())
    print("\nCrime Category Distribution:", offense_counts)
    plot_offense_distribution(offense_counts)
else:
    print("No data found.")