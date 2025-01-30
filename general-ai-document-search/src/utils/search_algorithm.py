from elasticsearch import Elasticsearch

def search_documents(query, indexed_documents, index_name="my_index"):
    """
    Search for documents that match the user's query and rank them based on relevance using Elastic Search.

    Parameters:
    query (str): The user's search query.
    indexed_documents (dictionary): A mapping of document names and their text that have been indexed.

    Returns:
    list: A list of tuples containing the document and its relevance score, sorted by score.
    """
    es = Elasticsearch(hosts=["http://localhost:9200"])

    # Index documents if not already indexed
    for doc_name, doc_text in indexed_documents.items():
        es.index(index=index_name, id=doc_name, body={"text": doc_text})

    # Search for documents
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

if __name__ == "__main__":
    # Example usage
    query = "text of document"
    indexed_documents = {
        "doc1": "This is the text of document 1.",
        "doc2": "This is the text of document 2.",
        # Add more documents as needed
    }
    results = search_documents(query, indexed_documents)
    print(results)

"""from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    # Create a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()
    
    # Combine the query with the indexed documents
    documents = indexed_documents + [query]
    
    # Transform the documents into TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Calculate cosine similarity between the query and indexed documents
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    
    # Create a list of documents with their corresponding scores
    scored_documents = list(zip(indexed_documents, cosine_similarities.flatten()))
    
    # Sort documents by score in descending order
    sorted_documents = sorted(scored_documents, key=lambda x: x[1], reverse=True)
    
    return sorted_documents"""
    