import csv
import ast

def read_column_from_csv(file_path):
    try:
        with open(file_path, 'r') as file:
            csvreader = csv.reader(file)
            header = next(csvreader)
            
            column_data = []
            for row in csvreader:
                actual_list = ast.literal_eval(row[2])
                column_data.append(actual_list)
        
        return column_data
    
    except Exception as e:
        return str(e)

file_path = 'insights_results.csv'

column_data = read_column_from_csv(file_path)

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

G = nx.Graph()

for entities in sampled_data:
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            # Add edge between two entities
            entity1, entity2 = entities[i][0], entities[j][0]
            G.add_edge(entity1, entity2)

net = Network(notebook=True, height="600px", width="100%")
net.from_nx(G)

html_path = "sample_graph.html"
net.save_graph(html_path)

st.write("### Network Graph of Entities and Relationships (First 10 Data Points)")
with open(html_path, "r", encoding="utf-8") as f:
    st.components.v1.html(f.read(), height=600)

os.remove(html_path)
