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
            model="gemini-2.5-pro",
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
            model="gemini-2.5-pro",
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
            model="gemini-2.5-pro",
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
            model="gemini-2.5-pro",
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
            model="gemini-2.5-pro",
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
            model="gemini-2.5-pro",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generating test cases: {str(e)}"
        
def generate_code_completions(code, language, context="", line=1, column=1, current_line_content="", previous_lines=None, full_context=False):
    """Generate intelligent AI-powered code completions"""
    try:
        if previous_lines is None:
            previous_lines = []
            
        # Build context for AI
        prompt_parts = [
            f"You are an intelligent code completion assistant for {language}.",
            "Analyze the following code and provide smart completions based on:",
            "1. The current context and what the user is likely trying to write",
            "2. Common patterns in the programming language",
            "3. Comments that indicate intended functionality",
            "4. Variable names and function signatures that suggest next steps",
            "5. Incomplete statements or expressions",
            "",
            f"Programming Language: {language}",
            f"Current line {line}, column {column}",
            ""
        ]
        
        if context:
            prompt_parts.append(f"Additional context: {context}")
            prompt_parts.append("")
        
        if previous_lines:
            prompt_parts.append("Previous lines:")
            prompt_parts.extend([f"{i+1}: {line}" for i, line in enumerate(previous_lines)])
            prompt_parts.append("")
        
        prompt_parts.extend([
            f"Current line content: '{current_line_content}'",
            "",
            "Full code context:",
            "```" + language,
            code,
            "```",
            "",
            "Provide 5-10 intelligent code completion suggestions in JSON format:",
            "Each suggestion should have:",
            "- 'label': Brief description",
            "- 'insertText': Code to insert", 
            "- 'detail': Explanation of what it does",
            "- 'kind': Type (function, variable, keyword, snippet, etc.)",
            "",
            "Focus on:",
            "- Completing partial statements",
            "- Suggesting based on comments or TODO items", 
            "- Common next steps for the current context",
            "- Variable/function names that make sense",
            "- Language-specific patterns and idioms",
            "",
            "Return only valid JSON array of completion objects."
        ])
        
        prompt = "\n".join(prompt_parts)
        
        # Use your existing Gemini API call
        model = client.models.get("gemini-2.5-pro")
        response = model.generate_content(prompt)
        
        try:
            # Try to parse as JSON
            import json
            completions_data = json.loads(response.text)
            
            # Ensure it's a list
            if not isinstance(completions_data, list):
                completions_data = []
                
            # Validate and clean completions
            valid_completions = []
            for comp in completions_data[:10]:  # Limit to 10 completions
                if isinstance(comp, dict) and 'label' in comp and 'insertText' in comp:
                    valid_completions.append({
                        'label': comp.get('label', ''),
                        'insertText': comp.get('insertText', ''),
                        'detail': comp.get('detail', ''),
                        'kind': comp.get('kind', 'text')
                    })
            
            return valid_completions
            
        except json.JSONDecodeError:
            # Fallback: parse text response and create simple completions
            return [
                {
                    'label': 'AI Suggestion',
                    'insertText': response.text.strip(),
                    'detail': 'AI-generated code suggestion',
                    'kind': 'snippet'
                }
            ]
            
    except Exception as e:
        print(f"Error generating AI completions: {e}")
        return []

def generate_hover_info(code_content, symbol_name, language, context=""):
    """Generate hover information for symbols in code"""
    
    prompt = f"""
    Provide detailed hover information for the symbol '{symbol_name}' in this {language} code:
    
    Code: {code_content}
    Symbol: {symbol_name}
    Context: {context}
    
    Please provide:
    1. Symbol definition and type information
    2. Function/method signatures
    3. Parameter descriptions
    4. Return value information
    5. Usage examples
    6. Related documentation
    7. Performance notes (if applicable)
    
    Format as concise but comprehensive hover tooltip content.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error generating hover information: {str(e)}"

def explain_code_functionality(code_content, language, level="intermediate"):
    """Explain what the code does and how it works"""
    
    if level == "beginner":
        prompt = f"""
        Explain this {language} code in beginner-friendly terms:
        
        Code: {code_content}
        
        Please provide:
        1. What this code does (high-level purpose)
        2. Step-by-step explanation of the logic
        3. Simple explanations of programming concepts used
        4. What each major section accomplishes
        5. Input and output descriptions
        6. Real-world analogies where helpful
        
        Use simple language and avoid technical jargon.
        """
    
    elif level == "advanced":
        prompt = f"""
        Provide an advanced technical explanation of this {language} code:
        
        Code: {code_content}
        
        Please analyze:
        1. Algorithm complexity and efficiency
        2. Design patterns and architectural decisions
        3. Memory usage and performance implications
        4. Advanced language features utilized
        5. Potential optimizations and trade-offs
        6. Integration points and dependencies
        
        Target explanation for experienced developers.
        """
    
    else:  # intermediate level
        prompt = f"""
        Explain the functionality of this {language} code:
        
        Code: {code_content}
        
        Please provide:
        1. Overall purpose and functionality
        2. Key components and their roles
        3. Data flow and control flow
        4. Important algorithms or logic
        5. External dependencies and interactions
        6. Potential use cases and applications
        
        Balance technical accuracy with readability.
        """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Error explaining code functionality: {str(e)}"

def main():
    """Interactive testing system for geminiPrompt functions"""
    print("\n=== AI Coding Assistant Interactive Test System ===\n")
    
    while True:
        print("Available functions to test:")
        print("1. generate_code_suggestion")
        print("2. explain_error")
        print("3. generate_documentation") 
        print("4. complete_code")
        print("5. analyze_code_quality")
        print("6. generate_test_cases")
        print("7. generate_code_completions")
        print("8. generate_hover_info")
        print("9. explain_code_functionality")
        print("10. main (run full demo)")
        print("0. Exit")
        
        choice = input("\nEnter function number to test: ")
        
        if choice == "0":
            break
        elif choice == "1":
            code = input("Enter code to analyze: ")
            language = input("Enter programming language: ")
            context = input("Enter context (optional): ")
            result = generate_code_suggestion(code, language, context)
            print(f"\n✅ Result:\n{result}\n")
            
        elif choice == "2":
            code = input("Enter problematic code: ")
            error = input("Enter error message: ")
            language = input("Enter programming language: ")
            result = explain_error(code, error, language)
            print(f"\n✅ Result:\n{result}\n")
            
        elif choice == "3":
            code = input("Enter code to document: ")
            language = input("Enter programming language: ")
            doc_type = input("Enter doc type (docstring/comments/readme): ") or "docstring"
            result = generate_documentation(code, language, doc_type)
            print(f"\n✅ Result:\n{result}\n")
            
        elif choice == "4":
            code = input("Enter partial code: ")
            language = input("Enter programming language: ")
            context = input("Enter context (optional): ")
            result = complete_code(code, language, context)
            print(f"\n✅ Result:\n{result}\n")
            
        elif choice == "5":
            code = input("Enter code to analyze: ")
            language = input("Enter programming language: ")
            result = analyze_code_quality(code, language)
            print(f"\n✅ Result:\n{result}\n")
            
        elif choice == "6":
            code = input("Enter code to generate tests for: ")
            language = input("Enter programming language: ")
            result = generate_test_cases(code, language)
            print(f"\n✅ Result:\n{result}\n")
            
        elif choice == "7":
            code = input("Enter code: ")
            cursor_pos = input("Enter cursor position: ")
            language = input("Enter programming language: ")
            context = input("Enter context (optional): ")
            result = generate_code_completions(code, cursor_pos, language, context)
            print(f"\n✅ Result:\n{result}\n")
            
        elif choice == "8":
            code = input("Enter code: ")
            symbol = input("Enter symbol name: ")
            language = input("Enter programming language: ")
            context = input("Enter context (optional): ")
            result = generate_hover_info(code, symbol, language, context)
            print(f"\n✅ Result:\n{result}\n")
            
        elif choice == "9":
            code = input("Enter code to explain: ")
            language = input("Enter programming language: ")
            level = input("Enter explanation level (beginner/intermediate/advanced): ") or "intermediate"
            result = explain_code_functionality(code, language, level)
            print(f"\n✅ Result:\n{result}\n")
            
        elif choice == "10":
            print("\n✅ Running main function demo:")
            full_demo()
            print("\n")
            
        else:
            print("❌ Invalid choice. Please try again.")

def full_demo():
    """Run a full demo of all functions with sample inputs"""
    sample_code = """def add(a, b):
    return a + b
    """
    print("=== Full Demo of geminiPrompt Functions ===\n")
    print("1. generate_code_suggestion:")
    suggestion = generate_code_suggestion(sample_code, "python")
    print(suggestion + "\n")
    print("2. explain_error:")
    error_explanation = explain_error(sample_code, "TypeError: unsupported operand type(s) for +: 'int' and 'str'", "python")
    print(error_explanation + "\n")
    print("3. generate_documentation:")
    documentation = generate_documentation(sample_code, "python", "docstring")
    print(documentation + "\n")
    print("4. complete_code:")
    partial_code = "def multiply(a, b):\n    "
    completed_code = complete_code(partial_code, "python")
    print(completed_code + "\n")
    print("5. analyze_code_quality:")
    code_quality = analyze_code_quality(sample_code, "python")
    print(code_quality + "\n")
    print("6. generate_test_cases:")
    test_cases = generate_test_cases(sample_code, "python")
    print(test_cases + "\n")
    print("7. generate_code_completions:")
    code_completions = generate_code_completions("def divide(a, b):\n    return a / ", 22, "python")
    print(code_completions + "\n")
    print("8. generate_hover_info:")
    hover_info = generate_hover_info(sample_code, "add", "python")
    print(hover_info + "\n")
    print("9. explain_code_functionality:")
    code_explanation = explain_code_functionality(sample_code, "python", "intermediate")
    print(code_explanation + "\n")
    print("=== End of Full Demo ===")

if __name__ == '__main__':
    main()