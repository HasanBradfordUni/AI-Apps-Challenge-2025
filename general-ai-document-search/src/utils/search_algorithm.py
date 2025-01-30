def search_documents(query, indexed_documents):
    """
    Search for documents that match the user's query and rank them based on relevance using Elastic Search.

    Parameters:
    query (str): The user's search query.
    indexed_documents (dictionary): A mapping of document names and their text that have been indexed.

    Returns:
    list: A list of tuples containing the document and its relevance score, sorted by score.
    """
    import elasticsearch
    es = elasticsearch.Elasticsearch(hosts=["http://localhost:6922"])
    results = []
    for doc_name, doc_text in indexed_documents.items():
        doc_score = es.get_relevance_score(query, doc_text)
        results.append((doc_name, doc_score))
    results.sort(key=lambda x: x[1], reverse=True)
    print(results)
    return results

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
    