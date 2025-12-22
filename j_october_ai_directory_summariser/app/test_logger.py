# test_logger.py
import sys
import os

# Add the root directory to Python path
root_dir = os.path.abspath('.')
print(f"Root directory: {root_dir}")
sys.path.insert(0, root_dir)

try:
    from autoLogger import general_logger
    print("✅ autoLogger import successful!")
    
    # Test logger functionality
    test_logger = general_logger("test_log.txt")
    test_logger.addToLogs("Test message")
    print("✅ Logger functionality working!")
    
except ImportError as e:
    print(f"❌ autoLogger import failed: {e}")
except Exception as e:
    print(f"❌ Logger test failed: {e}")