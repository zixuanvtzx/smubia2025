import spacy
import pandas as pd
import os
from collections import Counter

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# File path
file_path = "news_excerpts_parsed.xlsx"

# ✅ Check if file exists
if not os.path.exists(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")

# ✅ Read data from Excel file
df = pd.read_excel(file_path, engine="openpyxl")

# ✅ Ensure required columns exist
df.columns = ["Website", "Text"]
df.dropna(subset=["Website", "Text"], inplace=True)

# ✅ Extract Named Entities
def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

df["Entities"] = df["Text"].apply(extract_entities)

# ✅ Extract Subject-Verb-Object Relationships
def extract_relationships(text):
    doc = nlp(text)
    relationships = []
    
    for token in doc:
        if token.dep_ in ("nsubj", "nsubjpass") and token.head.pos_ == "VERB":
            subject = token.text
            verb = token.head.text
            obj = None
            for child in token.head.children:
                if child.dep_ in ("dobj", "attr"):
                    obj = child.text
            relationships.append((subject, verb, obj))
    
    return relationships if relationships else [("No Subject", "No Verb", "No Object")]

df["Relationships"] = df["Text"].apply(extract_relationships)

# ✅ Generate Insights

# 1️⃣ **Most Common Entities**
all_entities = [ent for sublist in df["Entities"] for ent in sublist]
entity_counter = Counter(all_entities)
top_entities = entity_counter.most_common(10)

print("\n📌 **Top 10 Entities in the Dataset:**")
for entity, count in top_entities:
    print(f"{entity[0]} ({entity[1]}): {count} occurrences")

# 2️⃣ **Most Common Relationships**
all_relationships = [rel for sublist in df["Relationships"] for rel in sublist]
relationship_counter = Counter(all_relationships)
top_relationships = relationship_counter.most_common(10)

print("\n📌 **Top 10 Subject-Verb-Object Relationships:**")
for relationship, count in top_relationships:
    print(f"{relationship[0]} → {relationship[1]} → {relationship[2]} ({count} occurrences)")

# ✅ Save results
output_file = "insights_results.xlsx"
df.to_excel(output_file, index=False, engine="openpyxl")
print(f"\n✅ Insights saved to '{output_file}'")
