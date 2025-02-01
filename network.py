import csv
import ast

def read_column_from_csv(file_path):
    try:
        # Open the CSV file
        with open(file_path, 'r') as file:
            # Create a CSV reader object
            csvreader = csv.reader(file)
            header = next(csvreader)
            # Extract the column data
            column_data = []
            for row in csvreader:
                actual_list = ast.literal_eval(row[2])
                column_data.append(actual_list)
        
        return column_data
    
    except Exception as e:
        return str(e)

# Example usage
file_path = 'insights_results.csv'  # Provide the path to your CSV file

column_data = read_column_from_csv(file_path)
#print(column_data)

network = []
for row in column_data:
    lst = []
    for ele in row:
        if ele[1] in ['GPE', 'PERSON', 'ORG'] and ele not in lst:
            lst.append(ele)
    network.append(lst)

#print(network)

import streamlit as st
import networkx as nx
from pyvis.network import Network
import os

# Select the first 10 data points from the dataset
sampled_data = network[:10]

# Create a NetworkX graph
G = nx.Graph()

# Add nodes and edges from the sampled data
for entities in sampled_data:
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            # Add edge between two entities
            entity1, entity2 = entities[i][0], entities[j][0]
            G.add_edge(entity1, entity2)

# Create a Pyvis network graph for visualization
net = Network(notebook=True, height="600px", width="100%")
net.from_nx(G)

# Save the graph as an HTML file
html_path = "sample_graph.html"
net.save_graph(html_path)

# Display the network graph in Streamlit using the HTML file
st.write("### Network Graph of Entities and Relationships (First 10 Data Points)")
with open(html_path, "r", encoding="utf-8") as f:
    st.components.v1.html(f.read(), height=600)

# Clean up the generated HTML file after displaying
os.remove(html_path)
