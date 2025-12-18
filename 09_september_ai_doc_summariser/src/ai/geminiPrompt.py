from google import genai
from google.genai.types import GenerateContentConfig
from google.genai import Client
import google.auth

credentials, project_id = google.auth.default()

# Initialize the new client
client = genai.Client(vertexai=True, project="generalpurposeai", location="us-central1")

def generate_document_summary(document_text, summary_type, summary_length, summary_tone):
    """Generate an AI summary of the document based on specifications"""
    
    # Build the prompt based on summary type
    if summary_type == "academic":
        base_prompt = f"""
        Please analyze the following academic document and provide a comprehensive summary:
        
        Document: {document_text}
        
        Please provide:
        1. Research Overview and Objectives
        2. Methodology Used
        3. Key Findings and Results
        4. Theoretical Contributions
        5. Limitations and Future Research
        6. Conclusion and Implications
        
        Format as an academic summary suitable for researchers and students.
        """
    
    elif summary_type == "business":
        base_prompt = f"""
        Please analyze the following business document and provide a strategic summary:
        
        Document: {document_text}
        
        Please provide:
        1. Executive Overview
        2. Key Business Points
        3. Financial Implications (if applicable)
        4. Strategic Recommendations
        5. Action Items
        6. Risk Factors and Opportunities
        
        Format for business stakeholders and decision-makers.
        """
    
    elif summary_type == "technical":
        base_prompt = f"""
        Please analyze the following technical document and provide a detailed summary:
        
        Document: {document_text}
        
        Please provide:
        1. Technical Overview
        2. System Architecture/Design
        3. Implementation Details
        4. Technical Specifications
        5. Performance Considerations
        6. Technical Recommendations
        
        Format for technical professionals and developers.
        """
    
    elif summary_type == "legal":
        base_prompt = f"""
        Please analyze the following legal document and provide a structured summary:
        
        Document: {document_text}
        
        Please provide:
        1. Document Type and Purpose
        2. Key Legal Provisions
        3. Rights and Obligations
        4. Important Terms and Conditions
        5. Legal Implications
        6. Compliance Requirements
        
        Format for legal professionals and stakeholders.
        """
    
    elif summary_type == "research":
        base_prompt = f"""
        Please analyze the following research document and provide a comprehensive summary:
        
        Document: {document_text}
        
        Please provide:
        1. Research Question and Hypothesis
        2. Literature Review Context
        3. Research Methodology
        4. Data Analysis and Results
        5. Discussion of Findings
        6. Conclusions and Recommendations
        
        Format for researchers and academic audience.
        """
    
    elif summary_type == "executive":
        base_prompt = f"""
        Please analyze the following document and provide an executive summary:
        
        Document: {document_text}
        
        Please provide:
        1. Key Points (Most Important Information)
        2. Critical Findings or Recommendations
        3. Business Impact
        4. Next Steps Required
        5. Strategic Implications
        
        Format for executives and senior management - concise and action-oriented.
        """
    
    else:  # general
        base_prompt = f"""
        Please provide a comprehensive summary of the following document:
        
        Document: {document_text}
        
        Include the main topics, key points, important conclusions, and any significant details.
        Make it accessible to a general audience.
        """
    
    # Add length specifications
    length_instructions = {
        "brief": "Keep the summary concise - 1-2 paragraphs maximum.",
        "medium": "Provide a moderate length summary - 3-4 paragraphs.",
        "long": "Create a detailed summary - 5 or more paragraphs with comprehensive coverage.",
        "bullet": "Format the summary as clear bullet points for easy scanning.",
        "custom": "Provide an appropriately sized summary based on the document length."
    }
    
    # Add tone specifications
    tone_instructions = {
        "neutral": "Use a neutral, objective tone.",
        "formal": "Use formal, professional language.",
        "casual": "Use conversational, accessible language.",
        "technical": "Use precise technical language appropriate for experts.",
        "simplified": "Use simple, easy-to-understand language for general audiences."
    }
    
    # Combine all instructions
    full_prompt = f"""
    {base_prompt}
    
    FORMATTING REQUIREMENTS:
    - Length: {length_instructions.get(summary_length, length_instructions['medium'])}
    - Tone: {tone_instructions.get(summary_tone, tone_instructions['neutral'])}
    
    Ensure the summary captures the essence of the document while being {summary_tone} in tone and {summary_length} in length.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[full_prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def analyze_document_content(document_text):
    """Analyze document content for deeper insights"""
    
    prompt = f"""
    Please analyze the following document and provide detailed insights:
    
    Document: {document_text}
    
    Please provide:
    1. Document Type Classification
    2. Main Themes and Topics
    3. Key Arguments or Points
    4. Target Audience Analysis
    5. Writing Style and Tone Assessment
    6. Content Structure Analysis
    7. Strengths and Weaknesses
    8. Recommendations for Improvement
    
    Provide objective, analytical insights that would be useful for understanding and improving the document.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error analyzing document: {str(e)}"

def extract_key_information(document_text, focus_areas=None):
    """Extract specific information based on focus areas"""
    
    if focus_areas:
        prompt = f"""
        Please extract information from the following document focusing specifically on: {focus_areas}
        
        Document: {document_text}
        
        Focus on finding and summarizing information related to the specified areas.
        If certain focus areas are not present in the document, please note that.
        """
    else:
        prompt = f"""
        Please extract the most important information from the following document:
        
        Document: {document_text}
        
        Focus on:
        1. Key facts and figures
        2. Important conclusions
        3. Critical recommendations
        4. Essential details
        5. Main takeaways
        """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error extracting key information: {str(e)}"

def generate_comparative_analysis(doc1_text, doc2_text):
    """Compare two documents and highlight differences/similarities"""
    
    prompt = f"""
    Please compare and analyze the following two documents:
    
    Document 1: {doc1_text}
    
    Document 2: {doc2_text}
    
    Please provide:
    1. Key Similarities
    2. Major Differences
    3. Comparative Analysis of Main Points
    4. Strengths and Weaknesses of Each
    5. Complementary Information
    6. Conflicting Information (if any)
    
    Format the comparison in a clear, structured manner.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generating comparative analysis: {str(e)}"

def generate_questions_from_document(document_text):
    """Generate relevant questions that the document answers or raises"""
    
    prompt = f"""
    Based on the following document, please generate:
    
    Document: {document_text}
    
    1. Questions that this document answers (5-10 questions)
    2. Questions that this document raises but doesn't fully address (3-5 questions)
    3. Follow-up questions for deeper understanding (3-5 questions)
    
    Format as clear, well-structured questions that would be useful for study or discussion.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generating questions: {str(e)}"

def main():
    """Main function to demonstrate the AI functionality"""
    pass

if __name__ == '__main__':
    main()