import vertexai
from vertexai.generative_models import GenerativeModel
import google.auth

credentials, project_id = google.auth.default()

vertexai.init(project="generalpurposeai", location="us-central1")

model = GenerativeModel(model_name="gemini-1.5-pro")

def generate_ai_summary(query, documents):
    # Function to generate an AI summary based on the user query and relevant documents
    response = model.generate_content(f"Summarize the following documents based on the query: {query}. Documents: {documents}")
    return response.text

def main():
    # Main function to demonstrate the AI summary generation process
    query = input("Enter your search query: ")
    # From the docs folder, put all filenames into a list
    all_documents = []
    print("Available documents are:\n")

    import os

    # Store the folder path, this file is in src/ai and the docs folder is in src/utils
    folder_path = os.path.join(os.path.dirname(__file__), "../utils/docs")

    for file_name in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_name)):
            all_documents.append(file_name)
            print(file_name)

    # Here you would typically call the search function to retrieve documents based on the transcribed question
    # and then generate an AI summary for those documents.

if __name__ == '__main__':
    main()