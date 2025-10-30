#A file that contains necessary and supplementary methods to 
# log output and errors from the program and store them

import os
from datetime import datetime

class general_logger():
    def __init__(self, filename):
        self.loggerFile = filename
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # Create file if it doesn't exist
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(f"Log file created: {datetime.now().isoformat()}\n\n")

    def printMenu(self):
        """Returns menu as dictionary instead of printing - for Flask compatibility"""
        menu = {
            1: "Add to logs", 
            2: "Search for logs", 
            3: "Add Error to logs", 
            4: "Search for errors in logs", 
            5: "Add Input to logs", 
            6: "Search for inputs in logs", 
            7: "Exit"
        }
        return menu

    def getMenuOption(self):
        """Not used in Flask - kept for compatibility"""
        pass

    def cleanLoggerFile(self):
        """Clean empty lines from log file"""
        try:
            with open(self.loggerFile, 'r', encoding='utf-8') as logger:
                current_lines = ""
                for line in logger.readlines():
                    if line.strip():  # Keep non-empty lines
                        current_lines += line
            
            with open(self.loggerFile, 'w', encoding='utf-8') as new_logger:
                new_logger.write(current_lines)
            return True
        except Exception as e:
            return False

    def getLoggerFile(self):
        """Get current log file path"""
        return self.loggerFile

    def changeLoggerFile(self, filename):
        """Change log file path"""
        self.loggerFile = filename
        # Ensure new directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    def handleChoice(self, choice):
        """Not used in Flask - kept for compatibility"""
        pass

    def addToLogs(self, outputStatement):
        """Add output log entry with timestamp"""
        try:
            with open(self.loggerFile, 'a', encoding='utf-8') as logger:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.write(f"[{timestamp}] Output:\n")
                # Replace double spaces with newlines for better formatting
                outputStatement = outputStatement.replace("  ", "\n")
                logger.write(f"{outputStatement}\n\n")
            return True
        except Exception as e:
            return False

    def addToInputLogs(self, inputPrompt, inputStatement):
        """Add input log entry with timestamp"""
        try:
            with open(self.loggerFile, 'a', encoding='utf-8') as logger:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.write(f"[{timestamp}] User Input:\n")
                logger.write(f"{inputPrompt}: {inputStatement}\n\n")
            return True
        except Exception as e:
            return False

    def searchForInputs(self, searchTerm):
        """Search for input logs - Flask version without user interaction"""
        try:
            with open(self.loggerFile, 'r', encoding='utf-8') as logger:
                inputLines = []
                lineToAdd = False
                
                for lineNum, line in enumerate(logger, 1):
                    if "User Input:" in line:
                        lineToAdd = True
                    if lineToAdd:
                        inputLines.append(f"Line {lineNum}: {line.strip()}")
                    if ("Error:" in line or "Output:" in line) and not "User Input:" in line:
                        lineToAdd = False
                
                # Filter results containing search term
                results = []
                for line in inputLines:
                    if searchTerm.lower() in line.lower():
                        results.append(line)
                
                return results
        except Exception as e:
            return []

    def searchForLogs(self, searchTerm):
        """Search for output logs - Flask version without user interaction"""
        try:
            with open(self.loggerFile, 'r', encoding='utf-8') as logger:
                outputLines = []
                lineToAdd = False
                
                for lineNum, line in enumerate(logger, 1):
                    if "Output:" in line:
                        lineToAdd = True
                    if lineToAdd:
                        outputLines.append(f"Line {lineNum}: {line.strip()}")
                    if ("Error:" in line or "User Input:" in line) and not "Output:" in line:
                        lineToAdd = False
                
                # Filter results containing search term
                results = []
                for line in outputLines:
                    if searchTerm.lower() in line.lower():
                        results.append(line)
                
                return results
        except Exception as e:
            return []

    def searchForErrors(self, searchTerm):
        """Search for error logs - Flask version without user interaction"""
        try:
            with open(self.loggerFile, 'r', encoding='utf-8') as logger:
                errorLines = []
                lineToAdd = False
                
                for lineNum, line in enumerate(logger, 1):
                    if "Error:" in line:
                        lineToAdd = True
                    if lineToAdd:
                        errorLines.append(f"Line {lineNum}: {line.strip()}")
                    if ("Output:" in line or "User Input:" in line) and not "Error:" in line:
                        lineToAdd = False
                
                # Filter results containing search term
                results = []
                for line in errorLines:
                    if searchTerm.lower() in line.lower():
                        results.append(line)
                
                return results
        except Exception as e:
            return []

    def addToErrorLogs(self, errorStatement):
        """Add error log entry with timestamp"""
        try:
            with open(self.loggerFile, 'a', encoding='utf-8') as logger:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.write(f"[{timestamp}] Error:\n")
                # Replace double spaces with newlines for better formatting
                errorStatement = errorStatement.replace("  ", "\n")
                logger.write(f"{errorStatement}\n\n")
            return True
        except Exception as e:
            return False

    def loggerMain(self):
        """Not used in Flask - kept for compatibility"""
        pass

    # Additional Flask-friendly methods
    
    def searchWithNarrow(self, searchType, initialTerm, narrowTerm=None):
        """Enhanced search method for Flask with optional narrow search"""
        # Get initial results
        if searchType == "output":
            results = self.searchForLogs(initialTerm)
        elif searchType == "error":
            results = self.searchForErrors(initialTerm)
        elif searchType == "input":
            results = self.searchForInputs(initialTerm)
        else:
            return []
        
        # Apply narrow search if provided
        if narrowTerm and results:
            narrowResults = []
            for line in results:
                if narrowTerm.lower() in line.lower():
                    narrowResults.append(line)
            return narrowResults
        
        return results

    def getLogStats(self):
        """Get statistics about the log file"""
        try:
            if not os.path.exists(self.loggerFile):
                return {
                    'total_lines': 0,
                    'output_count': 0,
                    'error_count': 0,
                    'input_count': 0,
                    'file_size': 0,
                    'last_modified': None
                }
            
            output_count = 0
            error_count = 0
            input_count = 0
            total_lines = 0
            
            with open(self.loggerFile, 'r', encoding='utf-8') as logger:
                for line in logger:
                    total_lines += 1
                    if "Output:" in line:
                        output_count += 1
                    elif "Error:" in line:
                        error_count += 1
                    elif "User Input:" in line:
                        input_count += 1
            
            file_size = os.path.getsize(self.loggerFile)
            last_modified = datetime.fromtimestamp(os.path.getmtime(self.loggerFile))
            
            return {
                'total_lines': total_lines,
                'output_count': output_count,
                'error_count': error_count,
                'input_count': input_count,
                'file_size': file_size,
                'last_modified': last_modified.isoformat()
            }
        except Exception as e:
            return {'error': str(e)}

    def getAllLogs(self, log_type=None, limit=None):
        """Get all logs of a specific type or all logs"""
        try:
            with open(self.loggerFile, 'r', encoding='utf-8') as logger:
                all_logs = []
                current_entry = []
                entry_type = None
                
                for line_num, line in enumerate(logger, 1):
                    line = line.strip()
                    
                    if "Output:" in line:
                        if current_entry and entry_type:
                            all_logs.append({
                                'type': entry_type,
                                'content': '\n'.join(current_entry),
                                'line_start': line_num - len(current_entry)
                            })
                        current_entry = [line]
                        entry_type = 'output'
                    elif "Error:" in line:
                        if current_entry and entry_type:
                            all_logs.append({
                                'type': entry_type,
                                'content': '\n'.join(current_entry),
                                'line_start': line_num - len(current_entry)
                            })
                        current_entry = [line]
                        entry_type = 'error'
                    elif "User Input:" in line:
                        if current_entry and entry_type:
                            all_logs.append({
                                'type': entry_type,
                                'content': '\n'.join(current_entry),
                                'line_start': line_num - len(current_entry)
                            })
                        current_entry = [line]
                        entry_type = 'input'
                    elif line and entry_type:
                        current_entry.append(line)
                
                # Don't forget the last entry
                if current_entry and entry_type:
                    all_logs.append({
                        'type': entry_type,
                        'content': '\n'.join(current_entry),
                        'line_start': line_num - len(current_entry) + 1
                    })
                
                # Filter by type if specified
                if log_type:
                    all_logs = [log for log in all_logs if log['type'] == log_type]
                
                # Apply limit if specified
                if limit:
                    all_logs = all_logs[-limit:]  # Get most recent entries
                
                return all_logs
        except Exception as e:
            return []

# For backwards compatibility when run as script
if __name__ == "__main__":
    # Interactive version for command line use
    myLogger = general_logger("logs/run_logs.txt")
    
    # Simple demo of Flask-compatible methods
    print("Flask-compatible autoLogger demo:")
    
    myLogger.addToLogs("Demo output log entry")
    myLogger.addToErrorLogs("Demo error log entry")
    myLogger.addToInputLogs("Demo prompt", "Demo input")
    
    print("Logs added successfully!")
    
    # Show stats
    stats = myLogger.getLogStats()
    print(f"Log stats: {stats}")
    
    # Search demo
    results = myLogger.searchForLogs("demo")
    print(f"Found {len(results)} results for 'demo'")