# Welcome to the AI Programming Assistant
# Start typing your code here...
# Use Ctrl+Space for AI-powered suggestions!

def hello_world():
    """
    Prints a generic "Hello, World!" message and returns a welcome string.
    """
    print("Hello, World!")
    print("There is some code here lol")
    return "Welcome to Has AI!"

def greet_user(name):
    """
    Greets a user by their name and returns a status message.

    Args:
        name (str): The name of the user to greet.

    Returns:
        str: A status message indicating the greeting was successful.
    """
    # Check if a non-empty name was provided
    if name and name.strip():
        # Greet the user with their provided name
        print(f"\nIt's nice to meet you, {name.strip()}!")
        return f"Successfully greeted {name.strip()}."
    else:
        # Handle cases where no name is entered
        print("\nYou didn't enter a name, but hello anyway!")
        return "Greeting attempted without a name."

# The main entry point of the script.
# This block runs only when the script is executed directly.

if __name__ == "__main__":
    # Call the first function and print its return value.
    message = hello_world()
    print(f"Message: {message}")

    # Add a separator for better readability in the console.
    print("-" * 20)

    # Prompt the user for their name and store it in a variable.
    user_name = input("What is your name? ")

    # Call the second function, passing the user's input as an argument.
    greeting_status = greet_user(user_name)

    # Print the status message returned by the greet_user function.
    print(f"Status: {greeting_status}")

    print("\nScript finished.")
