from sentence_transformers import SentenceTransformer
import numpy as np
import re
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import os
import json

# 确保下载了必要的 NLTK 资源
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# 加载预训练模型
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_document_embedding(document):
    text = re.sub(r'\s+', ' ', document).strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    sentences = sent_tokenize(text)
    stop_words = set(stopwords.words('english'))  
    sentences = [' '.join([word for word in sentence.split() if word not in stop_words]) for sentence in sentences]

    sentence_embeddings = model.encode(sentences)
    
    # 计算文档的嵌入（取平均）
    document_embedding = np.mean(sentence_embeddings, axis=0)
    
    return document_embedding

def cosine_similarity(vec_a, vec_b):
    if np.linalg.norm(vec_a) == 0 or np.linalg.norm(vec_b) == 0:
        return 0.0  # Handle zero vector case
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    return dot_product / (norm_a * norm_b)

def import_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def list_filenames_in_directory(directory_path):
    return [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

def save_embeddings_to_file(embeddings, file_path):
    # Convert NumPy arrays to lists for JSON serialization
    if isinstance(embeddings, np.ndarray):
        embeddings = embeddings.tolist()
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(embeddings, file, ensure_ascii=False, indent=4)

def load_embeddings_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        embeddings = json.load(file)
    return np.array(embeddings)

dir_path = "./document_27"
documents = list_filenames_in_directory(dir_path)
documents = [[dir_path, document] for document in documents]

# 示例文档
def transform(documents):
    for document in documents:
        print(document)
        document_file = import_txt_file('/'.join(document))
        print(document_file)
        embedding_vector = get_document_embedding(document_file)
        # Sanitize the filename
        safe_filename = document[1].replace('/', '_').replace('\\', '_')
        save_embeddings_to_file(embedding_vector, f'./embeddings/{safe_filename}.json')

# Uncomment to run the transform function
# transform(documents)

def test(to_test_vector, dir_path):
    documents = list_filenames_in_directory(dir_path)
    documents = [[dir_path, document] for document in documents]
    max_simi = -1
    max_doc = 'unknown' 
    for document in documents:
        try:
            to_check_vector = load_embeddings_from_file('/'.join(document))
            simi = cosine_similarity(to_test_vector, to_check_vector) 
            if simi > max_simi:
                max_simi = simi
                max_doc = document[1]
        except FileNotFoundError:
            print(f"File not found: {document[1]}")
    return max_doc
