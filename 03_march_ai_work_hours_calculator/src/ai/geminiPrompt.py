from google import genai
from google.genai.types import GenerateContentConfig
from google.genai import Client
import google.auth

credentials, project_id = google.auth.default()

# Initialize the new client
client = genai.Client(vertexai=True, project="generalpurposeai", location="us-central1")

def generate_work_hours_summary(contracted_hours, work_hours_description):
    """Function to generate an AI summary based on the user query and relevant documents"""
    
    prompt = f"""Given that an employee is contracted to work {contracted_hours}, 
                                   the following is a summary of the work hours description over a number of days: {work_hours_description}. 
                                   Can you provide a summmary breakdown of how many hours they have worked each day and the total hours worked, 
                                   summarise overtime/undertime and total difference based on the contracted hours as well and try to format it as similar 
                                   as possible to the provided work hours description (don't include the actual timings in the response)."""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        print(f"Error generating work hours summary: {str(e)}")
        return f"Unable to generate work hours summary. Error: {str(e)}"

def main():
    """Main function to demonstrate the AI summary generation process"""
    contracted_hours = "40.0"
    work_hours_description = """
    Day 1: Worked 8.0 hours
    Day 2: Worked 9.0 hours
    Day 3: Worked 7.5 hours
    Day 4: Worked 8.5 hours
    Day 5: Worked 6.0 hours
    """
    
    summary = generate_work_hours_summary(contracted_hours, work_hours_description)
    print("Generated Work Hours Summary:\n", summary)

if __name__ == '__main__':
    main()