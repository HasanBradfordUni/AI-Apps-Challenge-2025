from google import genai
from google.genai.types import GenerateContentConfig
from google.genai import Client
import google.auth
import os
#from search_algorithm import search_documents
#from document_processing import handle_documents

credentials, project_id = google.auth.default()

# Initialize the new client
client = genai.Client(vertexai=True, project="generalpurposeai", location="us-central1")

def generate_ai_summary(query, results, documents):
    """Function to generate an AI summary based on the user query and relevant documents"""
    
    prompt = f"""
    Summarize the following document search based on the query: {query}
    
    Document rankings based on search: {results}
    
    Contents of the documents and their names: {documents}
    
    You should summarise as if the search is a google/web search querying the documents for the user.
    Provide a comprehensive summary that includes:
    1. Most relevant documents found
    2. Key information related to the query
    3. Summary of findings across all relevant documents
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        print("AI Response:", response.text)
        return response.text
    except Exception as e:
        print(f"Error generating AI summary: {str(e)}")
        return f"Unable to generate summary. Error: {str(e)}"

def generate_search_suggestions(query, available_documents):
    """Generate search suggestions based on available documents"""
    
    prompt = f"""
    Based on the user query: "{query}" and the available documents: {available_documents}
    
    Please suggest:
    1. Alternative search terms that might yield better results
    2. Related topics the user might be interested in
    3. Specific document recommendations from the available collection
    
    Keep suggestions concise and relevant.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Unable to generate search suggestions. Error: {str(e)}"

def analyze_search_quality(query, results, documents):
    """Analyze the quality of search results and provide feedback"""
    
    prompt = f"""
    Analyze the search quality for the following:
    Query: {query}
    Search Results: {results}
    Available Documents: {documents}
    
    Please provide:
    1. Search result relevance score (1-10)
    2. Suggestions for improving the query
    3. Assessment of document coverage
    4. Recommendations for better results
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return "Unable to analyze search quality at this time."

def main():
    """Main function to demonstrate the AI summary generation process"""
    query = input("Enter your search query: ")
    directory_options = {}
    directory = ""

    # Store the folder path, this file is in src/ai and the docs folder is in src/utils
    # Get the current file's directory
    current_dir = os.path.dirname(__file__)

    # Construct the path to the docs folder
    folder_path = os.path.abspath(os.path.join(current_dir, '..', 'utils', 'docs'))

    for i, file_name in enumerate(os.listdir(folder_path)):
        if not os.path.isfile(os.path.join(folder_path, file_name)):
            directory_options[i+1] = f"{i+1}. {file_name}"

    # Get the user's choice of directory
    while directory not in directory_options.keys():
        for key, value in directory_options.items():
            print(value)
        directory = int(input("Enter the number of the directory you want to use for the search: "))
        if directory not in directory_options.keys():
            print("Invalid input, please try again.")
        else:
            directory = os.path.join(folder_path, directory_options[directory].split(". ")[1])
            break

    print(f"Available documents in directory {directory} are as follow:\n")
    
    """all_documents = handle_documents(directory)

    for doc in all_documents:
        print(doc)

    # Here you would typically call the search function to retrieve documents based on the transcribed question
    results = search_documents(query, all_documents)
    new_results = []
    for result in results:
        start_index = 10
        end_index = result.find(",")
        new_results.append(result[start_index:end_index])
    results = new_results
    
    # Generate an AI summary for those documents
    summary = generate_ai_summary(query, results, all_documents)
    
    # Optional: Generate search suggestions
    suggestions = generate_search_suggestions(query, all_documents)
    print("\n--- Search Suggestions ---")
    print(suggestions)
    
    # Optional: Analyze search quality
    quality_analysis = analyze_search_quality(query, results, all_documents)
    print("\n--- Search Quality Analysis ---")
    print(quality_analysis)"""

if __name__ == '__main__':
    main()