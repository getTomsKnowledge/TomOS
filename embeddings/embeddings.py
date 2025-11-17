import numpy as np
from openai import OpenAI
import pandas as pd
import os
import re

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# Cosine similarity function
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# Embeddings example function:
def embeddings_call(thisOS) -> list[float]:
    embedding = thisOS.client.embeddings.create(
        input="Your text string goes here",
        model="text-embedding-3-small",
        encoding_format="float"
    )

    print(embedding.data[0].embedding)
    return embedding.data[0].embedding

def normalize_l2(x):
    x = np.array(x)
    if x.ndim == 1:
        norm = np.linalg.norm(x)
        if norm == 0:
            return x
        return x / norm
    else:
        norm = np.linalg.norm(x, 2, axis=1, keepdims=True)
        return np.where(norm == 0, x, x / norm)

def cut_and_normalize(thisOS: object) -> list[float]:
    cut_dim = thisOS.data[0].embedding[:256]
    norm_dim = normalize_l2(cut_dim)
    return norm_dim

def get_embedding(text, client, model="text-embedding-3-small"):
    response = client.embeddings.create(
        input=text,
        model=model,
        encoding_format="float"
    )
    return response.data[0].embedding

def search_embeddings(df, product_description, n=3, pprint=True):
    embedding = get_embedding(product_description, client, model='text-embedding-3-small')
    df['similarities'] = df.ada_embedding.apply(lambda x: cosine_similarity(x, embedding))
    res = df.sort_values('similarities', ascending=False).head(n)
    return res

'''
df = pd.read_csv('Spaceflight2025.csv')
df['ada_embedding'] = df.embedding.apply(eval).apply(lambda x: np.array(x[:1536]))
search_query = input("Enter search term: ")
number_of_results = input("Enter number of results to return: ")
n = int(number_of_results) if number_of_results.isdigit() else 3
res = search_embeddings(df, search_query, n)
print(res)  # Print the search results
'''
def split_into_sentences(text):
    # Simple sentence splitter (can be improved)
    return re.split(r'(?<=[.!?]) +', text)

def recursive_substring_search(text, query_embedding, client, depth=2, top_k=2):
    """
    Recursively search for substrings with maximum similarity.
    - text: the text to search within
    - query_embedding: embedding of the search query
    - depth: recursion depth
    - top_k: number of top substrings to recurse into at each level
    """
    if depth == 0 or len(text) < 10:
        return [(text, cosine_similarity(get_embedding(text, client), query_embedding))]
    
    substrings = split_into_sentences(text)
    results = []
    for substring in substrings:
        if len(substring.strip()) == 0:
            continue
        emb = get_embedding(substring, client)
        sim = cosine_similarity(emb, query_embedding)
        results.append((substring, sim))
    
    # Sort by similarity
    results.sort(key=lambda x: x[1], reverse=True)
    top_results = results[:top_k]
    
    # Recurse into top substrings
    final_results = []
    for substring, sim in top_results:
        deeper = recursive_substring_search(substring, query_embedding, client, depth-1, top_k)
        final_results.extend(deeper)
    
    return final_results

def search_embeddings_recursive(df, product_description, n=3, depth=2, top_k=2):
    query_embedding = get_embedding(product_description, client, model='text-embedding-3-small')
    df['similarities'] = df.ada_embedding.apply(lambda x: cosine_similarity(x, query_embedding))
    top_rows = df.sort_values('similarities', ascending=False).head(n)
    
    substring_results = []
    for _, row in top_rows.iterrows():
        text = row['text']  # Change 'review' to your text column name
        substrings = recursive_substring_search(text, query_embedding, client, depth=depth, top_k=top_k)
        substring_results.extend(substrings)
    
    # Sort all substrings found by similarity
    substring_results.sort(key=lambda x: x[1], reverse=True)
    return substring_results[:n]

# --- Usage ---
df = pd.read_csv('Spaceflight2025.csv')
df['ada_embedding'] = df.embedding.apply(eval).apply(lambda x: np.array(x[:1536]))
search_query = input("Enter search term: ")
number_of_results = input("Enter number of results to return: ")
n = int(number_of_results) if number_of_results.isdigit() else 3

# Make sure your DataFrame has a 'review' column or change to the correct column name
results = search_embeddings_recursive(df, search_query, n=n, depth=2, top_k=2)
for substring, sim in results:
    print(f"Similarity: {sim:.4f} | Substring: {substring}")