import os
import time, datetime
from collections import defaultdict, Counter
from pathlib import Path

# Remove the autoLogger import section and replace with:
try:
    from ..utils.logger_setup import general_logger
except ImportError:
    # Fallback if logger is not available
    print("Logger import failed for directory analyzer, using DummyLogger")
    class DummyLogger:
        def __init__(self, filename): 
            self.file = open(filename, 'a')
            self.file.write("Logging started...\n"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"\n")
            self.file.close()
        def addToLogs(self, msg): print(f"[LOG] {msg}")
        def addToErrorLogs(self, msg): print(f"[ERROR] {msg}")
        def addToInputLogs(self, prompt, msg): print(f"[INPUT] {prompt}: {msg}")
    general_logger = DummyLogger

class DirectoryAnalyzer:
    def __init__(self):
        # Initialize logger
        log_file_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'directory_analyzer.txt')
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        self.logger = general_logger(log_file_path)
        
        self.supported_extensions = {
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.odt'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'presentations': ['.ppt', '.pptx', '.odp'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php']
        }
        
        self.logger.addToLogs("DirectoryAnalyzer initialized successfully")
    
    def analyze_directory(self, directory_path):
        """Perform comprehensive directory analysis"""
        self.logger.addToLogs(f"Starting directory analysis for: {directory_path}")
        start_time = time.time()
        
        analysis_result = {
            'directory_path': directory_path,
            'total_files': 0,
            'total_directories': 0,
            'total_size': 0,
            'file_types': Counter(),
            'file_type_categories': Counter(),
            'largest_files': [],
            'directory_structure': {},
            'file_extensions': Counter(),
            'analysis_duration': 0,
            'subdirectory_analysis': {}
        }
        
        try:
            self.logger.addToLogs(f"Beginning directory walk for: {directory_path}")
            file_count = 0
            dir_count = 0
            
            # Walk through directory
            for root, dirs, files in os.walk(directory_path):
                analysis_result['total_directories'] += len(dirs)
                dir_count += len(dirs)
                
                for file in files:
                    file_path = os.path.join(root, file)
                    self._analyze_file(file_path, analysis_result)
                    file_count += 1
                    
                    # Log progress every 100 files
                    if file_count % 100 == 0:
                        self.logger.addToLogs(f"Processed {file_count} files so far...")
            
            # Post-processing
            analysis_duration = time.time() - start_time
            analysis_result['analysis_duration'] = analysis_duration
            
            self.logger.addToLogs(f"Analysis complete - Found {analysis_result['total_files']} files, {dir_count} directories")
            self.logger.addToLogs(f"Total size: {analysis_result['total_size']} bytes")
            self.logger.addToLogs(f"Analysis took: {analysis_duration:.2f} seconds")
            
            analysis_result['largest_files'] = sorted(
                analysis_result['largest_files'], 
                key=lambda x: x['size'], 
                reverse=True
            )[:10]
            
            # Convert counters to dicts for JSON serialization
            analysis_result['file_types'] = dict(analysis_result['file_types'])
            analysis_result['file_type_categories'] = dict(analysis_result['file_type_categories'])
            analysis_result['file_extensions'] = dict(analysis_result['file_extensions'])
            
            # Calculate average file size
            if analysis_result['total_files'] > 0:
                analysis_result['average_file_size'] = analysis_result['total_size'] / analysis_result['total_files']
                self.logger.addToLogs(f"Average file size: {analysis_result['average_file_size']:.2f} bytes")
            else:
                analysis_result['average_file_size'] = 0
                self.logger.addToLogs("No files found in directory")
            
        except Exception as e:
            self.logger.addToErrorLogs(f"Error during directory analysis: {str(e)}")
            analysis_result['error'] = str(e)
        
        return analysis_result
    
    def _analyze_file(self, file_path, analysis_result):
        """Analyze individual file"""
        try:
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            file_ext = Path(file_path).suffix.lower()
            
            analysis_result['total_files'] += 1
            analysis_result['total_size'] += file_size
            analysis_result['file_extensions'][file_ext] += 1
            
            # Categorize file type
            category = self._get_file_category(file_ext)
            analysis_result['file_type_categories'][category] += 1
            analysis_result['file_types'][file_ext] += 1
            
            # Track largest files
            if len(analysis_result['largest_files']) < 100:
                analysis_result['largest_files'].append({
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'size': file_size,
                    'extension': file_ext
                })
            else:
                smallest = min(analysis_result['largest_files'], key=lambda x: x['size'])
                if file_size > smallest['size']:
                    analysis_result['largest_files'].remove(smallest)
                    analysis_result['largest_files'].append({
                        'path': file_path,
                        'name': os.path.basename(file_path),
                        'size': file_size,
                        'extension': file_ext
                    })
                    
        except (OSError, IOError) as e:
            self.logger.addToErrorLogs(f"Could not access file {file_path}: {str(e)}")
    
    def _get_file_category(self, extension):
        """Categorize file by extension"""
        for category, extensions in self.supported_extensions.items():
            if extension in extensions:
                return category
        return 'other'
    
    def get_quick_stats(self, directory_path):
        """Get quick directory statistics without full analysis"""
        self.logger.addToLogs(f"Getting quick stats for: {directory_path}")
        
        try:
            total_files = 0
            total_size = 0
            
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        total_files += 1
                        total_size += file_size
                    except (OSError, IOError):
                        continue
            
            self.logger.addToLogs(f"Quick stats complete: {total_files} files, {total_size} bytes")
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'formatted_size': self._format_size(total_size)
            }
            
        except Exception as e:
            self.logger.addToErrorLogs(f"Error getting quick stats: {str(e)}")
            return {'error': str(e)}
    
    def analyze_subdirectories(self, directory_path, max_depth=2):
        """Analyze subdirectories up to specified depth"""
        subdirectory_stats = {}
        
        try:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isdir(item_path):
                    stats = self.get_quick_stats(item_path)
                    subdirectory_stats[item] = stats
                    
        except (OSError, IOError) as e:
            subdirectory_stats['error'] = str(e)
        
        return subdirectory_stats
    
    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def generate_directory_tree(self, directory_path, max_depth=3):
        """Generate a tree structure representation of the directory"""
        tree = {}
        
        def build_tree(path, current_depth=0):
            if current_depth >= max_depth:
                return "..."
            
            try:
                items = {}
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        items[item + "/"] = build_tree(item_path, current_depth + 1)
                    else:
                        items[item] = os.path.getsize(item_path)
                return items
            except (OSError, IOError):
                return "Access Denied"
        
        tree[os.path.basename(directory_path)] = build_tree(directory_path)
        return tree
    
    def find_duplicate_files(self, directory_path):
        """Find potential duplicate files based on size and name"""
        file_signatures = defaultdict(list)
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    signature = (os.path.basename(file), file_size)
                    file_signatures[signature].append(file_path)
                except (OSError, IOError):
                    continue
        
        # Return only groups with duplicates
        duplicates = {sig: paths for sig, paths in file_signatures.items() if len(paths) > 1}
        return duplicates