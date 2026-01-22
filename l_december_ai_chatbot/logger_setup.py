import os
import sys

# Get the root directory (repository root)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add root to path if not already there
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from autoLogger import general_logger
    print(f"[LOGGER] ✅ Successfully imported autoLogger from: {root_dir}")
except ImportError as e:
    print(f"[LOGGER] ❌ Failed to import autoLogger: {e}")
    # Fallback logger
    class DummyLogger:
        def __init__(self, filename):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.file = filename
        def addToLogs(self, msg): print(f"[LOG] {msg}")
        def addToErrorLogs(self, msg): print(f"[ERROR] {msg}")
        def addToInputLogs(self, prompt, msg): print(f"[INPUT] {prompt}: {msg}")
    general_logger = DummyLogger

# Create logs directory in December project
december_logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(december_logs_dir, exist_ok=True)

# Initialize logger for December project
chatbot_logger = general_logger(os.path.join(december_logs_dir, 'chatbot.txt'))
api_logger = general_logger(os.path.join(december_logs_dir, 'api_requests.txt'))
error_logger = general_logger(os.path.join(december_logs_dir, 'errors.txt'))

__all__ = ['chatbot_logger', 'api_logger', 'error_logger', 'general_logger']