import pandas as pd
from bm25 import BM25, process_query, load_documents
from embedding_calculate import get_document_embedding, list_filenames_in_directory, load_embeddings_from_file, cosine_similarity
import os

def bm25(cases, corpus, filenames, n):
    bm25 = BM25(corpus)  # 创建BM25实例
    # Convert the Series to a single string
    document = process_query(cases)  # Process the combined string
    top_documents = bm25.get_top_n_documents(document, n=n)  # 获取前5个相关文档
    
    # 获取前文档的文件名
    top_document_filenames = [filenames[index] for score, index in top_documents]
    
    return top_document_filenames

def embedding_simi(query, dir_path, top_n=5):
    # Get the embedding vector for the query
    query_embedding = get_document_embedding(query)
    
    # Load all embeddings from the specified directory
    embeddings = list_filenames_in_directory(dir_path)
    similarity_scores = []  # List to store (similarity, filename) tuples
    
    for embedding_file in embeddings:
        try:
            # Load the embedding for the document
            embedding_vector = load_embeddings_from_file(os.path.join(dir_path, embedding_file))
            # Calculate the cosine similarity
            similarity = cosine_similarity(query_embedding, embedding_vector)
            
            # Append the similarity and filename to the list
            similarity_scores.append((similarity, embedding_file))
        except FileNotFoundError:
            print(f"File not found: {embedding_file}")
    
    # Sort the list by similarity score in descending order
    similarity_scores.sort(key=lambda x: x[0], reverse=True)
    
    # Get the top N most similar documents
    top_similar_docs = similarity_scores[:top_n]
    
    # Return only the filenames of the top documents
    top_document_names = [filename for _, filename in top_similar_docs]
    
    return top_document_names  # Return a list of filenames

def load_csv_file(file_path):
    return pd.read_csv(file_path)



def case2law_bm25(case, directory,  n):
    # 加载测试案例
    to_test = case
    corpus = load_documents(directory)  # 加载并处理文档
    filenames = [f for f in os.listdir(directory) if f.endswith('.txt')]

    # 调用bm25函数并返回前文档的文件名
    top_filenames = bm25(to_test, corpus, filenames, n)
    return top_filenames

def case2law_embedding(case, directory, n):
    to_test = case
    doc = embedding_simi(to_test, directory, n)
    return doc

# Load test cases
test_applicability = load_csv_file("./eval/cases/train_generate_cases_hipaa_compliance.csv")
print("Checkpoint 1: Loaded test cases.")

# Initialize rag_laws with None values to match the length of the DataFrame
rag_laws = [None] * len(test_applicability)

output_filename = ("train_generate_cases_hipaa_compliance_rag", "csv")
# Iterate over each row in the DataFrame
for index, row in test_applicability.iterrows():
    case = row['generate_background']  # Get the case from the current row
    print(f"Checkpoint 2: Processing case {index + 1}/{len(test_applicability)}: {case}")

    doc1 = case2law_bm25(case, './document_27', 10)  # Get top documents using BM25
    print(f"Checkpoint 3: Retrieved {len(doc1)} documents using BM25.")

    doc2 = case2law_embedding(case, './embeddings', 10)  # Get top documents using embeddings
    print(f"Checkpoint 4: Retrieved {len(doc2)} documents using embeddings.")

    intersection = set(doc1) & set(doc2)  # Calculate the intersection
    rag_laws[index] = intersection  # Assign the intersection to the corresponding index

    # Save intermediate results every 10 cases
    if (index + 1) % 10 == 0:
        test_applicability['rag_laws'] = rag_laws  # Add the current results to the DataFrame
        intermediate_filename = f'{output_filename[0]}_{index + 1}.{output_filename[1]}'
        test_applicability.to_csv(intermediate_filename, index=False, encoding='utf-8')
        print(f"Checkpoint 5: Saved intermediate results to '{intermediate_filename}'.")

# Final save after processing all cases
test_applicability['rag_laws'] = rag_laws  # Add the final results to the DataFrame
final_filename = f'{output_filename[0]}.{output_filename[1]}'
test_applicability.to_csv(final_filename, index=False, encoding='utf-8')
print(f"Checkpoint 6: Saved the final DataFrame to '{final_filename}'.")
    