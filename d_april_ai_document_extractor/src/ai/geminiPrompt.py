from google import genai
from google.genai.types import GenerateContentConfig
import os
import google.auth

credentials, project_id = google.auth.default()

# Initialize the new client
client = genai.Client(vertexai=True, project="generalpurposeai", location="us-central1")

def generate_conversion_insights(file_content, config_options):
    """
    Generate AI insights to assist with document conversion.
    
    Args:
        file_content (str): The extracted text content of the uploaded document.
        config_options (dict): The configuration options selected by the user.
    
    Returns:
        dict: AI-generated insights for document conversion.
    """
    prompt = f"""
    You are an AI assistant helping with document conversion. The user has uploaded a document with the following content:
    
    {file_content}
    
    The user has selected the following configuration options:
    - Table Handling: {config_options.get('Table Handling:', 'Not specified')}
    - Field Mapping: {config_options.get('Field Mapping:', 'Not specified')}
    - Placeholder Text: {config_options.get('Placeholder Text:', 'Not specified')}
    - Page Range: {config_options.get('Page Range:', 'Not specified')}
    - Output Formatting: {config_options.get('Output Formatting:', 'Not specified')}
    - Additional Notes: {config_options.get('Additional Notes:', 'None')}
    
    Please provide a detailed analysis in the following format:
    
    ## Document Analysis Summary
    
    ### Field Mapping Suggestions
    [Provide specific field mappings based on the document content]
    
    ### Table Handling Recommendations
    [Provide recommendations for handling tables in the document]
    
    ### Placeholder Text Suggestions
    [Suggest appropriate placeholder text for empty fields]
    
    ### Conversion Process Insights
    [Any additional insights or recommendations for improving the conversion process]
    
    ### Configuration Assessment
    [Assessment of the user's chosen configuration options and any improvements]
    """
    
    try:
        # Generate AI response using the new Google Gen AI SDK
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[prompt],
            config=GenerateContentConfig(
                max_output_tokens=2048,
                temperature=0.7
            )
        )
        
        ai_summary = response.text
        print("AI Response:", ai_summary)
        
        # Parse and return the response with the full markdown text
        return {
            "field_mappings": get_mappings(ai_summary),
            "table_handling": get_table_handling(ai_summary),
            "placeholder_text": get_placeholder_text(ai_summary),
            "additional_insights": get_additional_insights(ai_summary),
            "full_summary": ai_summary  # Include the full markdown summary
        }
    except Exception as e:
        print(f"Error generating AI insights: {str(e)}")
        return {
            "field_mappings": "Error generating field mappings",
            "table_handling": "Error generating table handling recommendations",
            "placeholder_text": "Error generating placeholder text suggestions",
            "additional_insights": "Error generating additional insights",
            "full_summary": f"Error: Could not generate AI insights - {str(e)}"
        }

def get_mappings(text):
    if "field mapping" in text.lower():
        lines = text.split('\n')
        mapping_section = []
        capture = False
        for line in lines:
            if "field mapping" in line.lower():
                capture = True
            elif capture and line.startswith('#'):
                break
            elif capture and line.strip():
                mapping_section.append(line.strip())
        return '\n'.join(mapping_section) if mapping_section else "No field mappings provided."
    return "No field mappings provided."

def get_table_handling(text):
    if "table handling" in text.lower():
        lines = text.split('\n')
        table_section = []
        capture = False
        for line in lines:
            if "table handling" in line.lower():
                capture = True
            elif capture and line.startswith('#'):
                break
            elif capture and line.strip():
                table_section.append(line.strip())
        return '\n'.join(table_section) if table_section else "No recommendations provided for table handling."
    return "No recommendations provided for table handling."

def get_placeholder_text(text):
    if "placeholder text" in text.lower():
        lines = text.split('\n')
        placeholder_section = []
        capture = False
        for line in lines:
            if "placeholder text" in line.lower():
                capture = True
            elif capture and line.startswith('#'):
                break
            elif capture and line.strip():
                placeholder_section.append(line.strip())
        return '\n'.join(placeholder_section) if placeholder_section else "No placeholder text suggestions provided."
    return "No placeholder text suggestions provided."

def get_additional_insights(text):
    if "additional insights" in text.lower() or "conversion process" in text.lower():
        lines = text.split('\n')
        insights_section = []
        capture = False
        for line in lines:
            if "additional insights" in line.lower() or "conversion process" in line.lower():
                capture = True
            elif capture and line.startswith('#'):
                break
            elif capture and line.strip():
                insights_section.append(line.strip())
        return '\n'.join(insights_section) if insights_section else "No additional insights provided."
    return "No additional insights provided."

def main():
    # Main function to demonstrate the AI summary generation process
    sample_text = "This is a sample document content with tables and fields."
    sample_config = {
        "Table Handling:": "Keep Original Table",
        "Output Formatting:": "Default Formatting"
    }
    ai_summary = generate_conversion_insights(sample_text, sample_config)
    print("Full AI Summary:\n", ai_summary["full_summary"])

if __name__ == '__main__':
    main()