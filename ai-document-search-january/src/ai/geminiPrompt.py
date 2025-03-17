import vertexai
from vertexai.generative_models import GenerativeModel
import google.auth
import os
from search_algorithm import search_documents
from document_processing import handle_documents

credentials, project_id = google.auth.default()

vertexai.init(project="generalpurposeai", location="us-central1")

model = GenerativeModel(model_name="gemini-1.5-pro")

def generate_ai_summary(query, results, documents):
    # Function to generate an AI summary based on the user query and relevant documents
    response = model.generate_content(f"Summarize the following document search based on the query: {query}. Document rankings based on search: {results}. Contents of the documents and their names: {documents}.")
    print("Ai Response:",response.text)
    return response.text

def main():
    # Main function to demonstrate the AI summary generation process
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
    
    all_documents = handle_documents(directory)

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
    # and then generate an AI summary for those documents.
    generate_ai_summary(query, results, all_documents)

if __name__ == '__main__':
    main()