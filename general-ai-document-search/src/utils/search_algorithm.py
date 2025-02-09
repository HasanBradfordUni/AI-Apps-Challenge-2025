from elasticsearch import Elasticsearch
import os
from utils.document_processing import handle_documents

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def search_documents_v2(query, indexed_documents, index_name="my_index"):
    """
    Search for documents that match the user's query and rank them based on relevance using Elastic Search.

    Parameters:
    query (str): The user's search query.
    indexed_documents (dictionary): A mapping of document names and their text that have been indexed.
    index_name (str): The name of the index to use for searching (optional argument with default value "my_index").

    Returns:
    list: A list of tuples containing the document and its relevance score, sorted by score.
    """
    es = Elasticsearch(hosts=["http://localhost:9200"])

    #Index documents if not already indexed
    for doc_name, doc_text in indexed_documents.items():
        es.index(index=index_name, id=doc_name, body={"text": doc_text})

    #Search for documents
    search_body = {
        "query": {
            "match": {
                "text": query
            }
        }
    }
    response = es.search(index=index_name, body=search_body)
    results = [(hit["_id"], hit["_score"]) for hit in response["hits"]["hits"]]
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def search_documents(query, indexed_documents):
    """
    Search for documents that match the user's query and rank them based on relevance using Machine Learning.

    Parameters:
    query (str): The user's search query.
    indexed_documents (dictionary): A mapping of document names and their text that have been indexed.

    Returns:
    list: A list of tuples containing the document and its relevance score, sorted by score.
    """
    # Create a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()
    
    # Combine the query with the indexed documents
    documents = list(indexed_documents.values()) + [query]
    
    # Transform the documents into TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Calculate cosine similarity between the query and indexed documents
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    
    # Create a list of documents with their corresponding scores
    scored_documents = list(zip(indexed_documents, cosine_similarities.flatten()))
    
    # Sort documents by score in descending order
    sorted_documents = sorted(scored_documents, key=lambda x: x[1], reverse=True)
    
    return sorted_documents

# Example usage
if __name__ == "__main__":
    directory_name = input("Enter the name of the directory containing the documents: ")
    target_directory = f"{os.path.dirname(__file__)}\\docs\\{directory_name}"
    # Check if the directory exists
    while not os.path.exists(target_directory):
        print(f"Directory {directory_name} does not exist.")
        directory_name = input("Enter the name of the directory containing the documents: ")
        target_directory = f"{os.path.dirname(__file__)}\\docs\\{directory_name}"
    
    indexed_documents = handle_documents(directory_name)

    print("Indexed documents are as follows:")

    for doc_name, doc_text in indexed_documents.items():
        print(f"Document: {doc_name}")
        print(f"Text: {doc_text}")
        print()
    
    query = input("Enter your search query: ")
    results = search_documents(query, indexed_documents)
    print(results)

    