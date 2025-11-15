from google import genai
from google.genai.types import GenerateContentConfig
from google.genai import Client
import google.auth

credentials, project_id = google.auth.default()

# Initialize the new client
client = genai.Client(vertexai=True, project="generalpurposeai", location="us-central1")

def generate_code_suggestion(code_content, language, context=""):
    """Generate AI code suggestions and improvements"""
    
    # Build the prompt based on programming language
    if language == "python":
        base_prompt = f"""
        Analyze the following Python code and provide helpful suggestions for improvement:
        
        Code: {code_content}
        Context: {context}
        
        Please provide:
        1. Code Quality Improvements
        2. Performance Optimizations
        3. Best Practices Recommendations
        4. Potential Bug Fixes
        5. Code Refactoring Suggestions
        6. Alternative Approaches
        
        Format as clear, actionable suggestions for Python developers.
        """
    
    elif language == "javascript":
        base_prompt = f"""
        Analyze the following JavaScript code and provide helpful suggestions:
        
        Code: {code_content}
        Context: {context}
        
        Please provide:
        1. Modern JavaScript Best Practices
        2. Performance Improvements
        3. Security Considerations
        4. ES6+ Features Usage
        5. Code Organization Tips
        6. Browser Compatibility Notes
        
        Format for JavaScript/Web developers.
        """
    
    elif language == "java":
        base_prompt = f"""
        Analyze the following Java code and provide comprehensive suggestions:
        
        Code: {code_content}
        Context: {context}
        
        Please provide:
        1. Object-Oriented Design Improvements
        2. Performance Optimizations
        3. Memory Management Tips
        4. Exception Handling Best Practices
        5. Code Style and Conventions
        6. Design Pattern Recommendations
        
        Format for Java developers following enterprise standards.
        """
    
    elif language == "cpp":
        base_prompt = f"""
        Analyze the following C++ code and provide expert suggestions:
        
        Code: {code_content}
        Context: {context}
        
        Please provide:
        1. Memory Management Improvements
        2. Performance Optimizations
        3. Modern C++ Features Usage
        4. Resource Management (RAII)
        5. Template Usage Recommendations
        6. Compiler Optimization Tips
        
        Format for C++ developers focusing on efficiency and safety.
        """
    
    elif language == "csharp":
        base_prompt = f"""
        Analyze the following C# code and provide suggestions:
        
        Code: {code_content}
        Context: {context}
        
        Please provide:
        1. .NET Best Practices
        2. Performance Improvements
        3. LINQ Usage Optimization
        4. Async/Await Patterns
        5. Exception Handling
        6. Code Organization Tips
        
        Format for C#/.NET developers.
        """
    
    else:  # Generic programming language
        base_prompt = f"""
        Analyze the following {language} code and provide helpful suggestions:
        
        Code: {code_content}
        Context: {context}
        
        Please provide:
        1. Code Quality Improvements
        2. Best Practices for {language}
        3. Performance Considerations
        4. Readability Enhancements
        5. Potential Issues
        6. Optimization Opportunities
        
        Format for {language} developers.
        """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[base_prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generating code suggestion: {str(e)}"

def explain_error(code_content, error_message, language):
    """Explain coding errors and provide solutions"""
    
    prompt = f"""
    Help debug this {language} code error:
    
    Code: {code_content}
    
    Error Message: {error_message}
    
    Please provide:
    1. Clear explanation of what went wrong
    2. Why this error occurred
    3. Step-by-step solution
    4. Prevention tips for future
    5. Alternative approaches if applicable
    6. Related best practices
    
    Make the explanation beginner-friendly but technically accurate.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error explaining error: {str(e)}"

def generate_documentation(code_content, language, doc_type="docstring"):
    """Generate documentation for code"""
    
    if doc_type == "docstring":
        prompt = f"""
        Generate comprehensive docstrings/documentation for this {language} code:
        
        Code: {code_content}
        
        Please provide:
        1. Function/Class descriptions
        2. Parameter documentation
        3. Return value descriptions
        4. Usage examples
        5. Exception documentation
        6. Type hints (where applicable)
        
        Format according to {language} documentation standards.
        """
    
    elif doc_type == "comments":
        prompt = f"""
        Add helpful inline comments to explain this {language} code:
        
        Code: {code_content}
        
        Please provide:
        1. Line-by-line explanations where needed
        2. Logic flow descriptions
        3. Variable purpose explanations
        4. Algorithm step explanations
        5. Complex operation breakdowns
        
        Keep comments concise but informative.
        """
    
    elif doc_type == "readme":
        prompt = f"""
        Generate README documentation for this {language} code:
        
        Code: {code_content}
        
        Please provide:
        1. Project description
        2. Installation instructions
        3. Usage examples
        4. API documentation
        5. Dependencies list
        6. Contributing guidelines
        
        Format as a comprehensive README.md file.
        """
    
    else:  # General documentation
        prompt = f"""
        Generate comprehensive documentation for this {language} code:
        
        Code: {code_content}
        
        Include appropriate documentation based on the code type and language conventions.
        """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generating documentation: {str(e)}"

def complete_code(code_content, language, context=""):
    """Complete partial code with AI assistance"""
    
    prompt = f"""
    Complete this partial {language} code based on the context and existing code structure:
    
    Partial Code: {code_content}
    Context: {context}
    
    Please provide:
    1. Logical code completion
    2. Follow existing patterns and style
    3. Implement missing functionality
    4. Add necessary imports/includes
    5. Ensure code correctness
    6. Add helpful comments
    
    Complete the code while maintaining consistency with the existing style and logic.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error completing code: {str(e)}"

def analyze_code_quality(code_content, language):
    """Analyze code quality and provide detailed feedback"""
    
    prompt = f"""
    Perform a comprehensive code quality analysis on this {language} code:
    
    Code: {code_content}
    
    Please analyze:
    1. Code Structure and Organization
    2. Naming Conventions
    3. Code Complexity
    4. Performance Implications
    5. Security Considerations
    6. Maintainability Factors
    7. Testing Recommendations
    8. Documentation Quality
    
    Provide scores and specific improvement recommendations.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error analyzing code quality: {str(e)}"

def generate_test_cases(code_content, language):
    """Generate test cases for the provided code"""
    
    prompt = f"""
    Generate comprehensive test cases for this {language} code:
    
    Code: {code_content}
    
    Please provide:
    1. Unit test cases
    2. Edge case testing
    3. Error condition tests
    4. Performance test suggestions
    5. Integration test ideas
    6. Test data examples
    
    Use appropriate testing frameworks for {language}.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generating test cases: {str(e)}"

def main():
    """Main function to demonstrate the AI functionality"""
    pass

if __name__ == '__main__':
    main()