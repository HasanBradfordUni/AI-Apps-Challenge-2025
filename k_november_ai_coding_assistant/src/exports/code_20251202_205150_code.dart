import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def hello_world():
    """Prints a greeting and returns a welcome message."""
    logging.info("Executing hello_world function")
    print("Hello, World!")
    return "Welcome to Has AI!"

if __name__ == "__main__":
    """Main execution block.  Calls hello_world and prints the returned message."""
    logging.info("Starting main execution")
    message = hello_world()
    logging.info(f"Message received: {message}")
    print(f"Message: {message}")
    logging.info("Exiting main execution")