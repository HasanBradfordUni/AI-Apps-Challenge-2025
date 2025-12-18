import os
import sys

# Debug current working directory and file location
current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

print(f"[PATH DEBUG] Current file: {current_file}")
print(f"[PATH DEBUG] Current directory: {current_dir}")
print(f"[PATH DEBUG] Working directory: {os.getcwd()}")

# Use current working directory as root (same as your successful test)
root_dir = os.path.abspath('.')
print(f"[PATH DEBUG] Using root directory: {root_dir}")

# Check if autoLogger exists
autologger_path = os.path.join(root_dir, 'autoLogger.py')
print(f"[PATH DEBUG] Looking for autoLogger at: {autologger_path}")
print(f"[PATH DEBUG] autoLogger exists: {os.path.exists(autologger_path)}")

if os.path.exists(root_dir):
    files_in_root = [f for f in os.listdir(root_dir) if f.endswith('.py')]
    print(f"[PATH DEBUG] Python files in root: {files_in_root}")

# Add to path
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
    print(f"[PATH DEBUG] Added to sys.path: {root_dir}")
else:
    print(f"[PATH DEBUG] Root already in sys.path")

try:
    # Now import autoLogger
    from autoLogger import general_logger
    print(f"[PATH DEBUG] ✅ Successfully imported autoLogger from: {root_dir}")
except ImportError as e:
    print(f"[PATH DEBUG] ❌ Failed to import autoLogger: {e}")
    print(f"[PATH DEBUG] sys.path contents: {sys.path}")
    raise

# Export it for other modules to use
__all__ = ['general_logger']