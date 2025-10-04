import os
import time
from collections import defaultdict, Counter
from pathlib import Path

class DirectoryAnalyzer:
    def __init__(self):
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
    
    def analyze_directory(self, directory_path):
        """Perform comprehensive directory analysis"""
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
            # Walk through directory
            for root, dirs, files in os.walk(directory_path):
                analysis_result['total_directories'] += len(dirs)
                
                for file in files:
                    file_path = os.path.join(root, file)
                    self._analyze_file(file_path, analysis_result)
            
            # Post-processing
            analysis_result['analysis_duration'] = time.time() - start_time
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
            else:
                analysis_result['average_file_size'] = 0
            
        except Exception as e:
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
            if len(analysis_result['largest_files']) < 100:  # Keep top 100 for processing
                analysis_result['largest_files'].append({
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'size': file_size,
                    'extension': file_ext
                })
            else:
                # Replace smallest if current is larger
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
            # Skip files that can't be accessed
            pass
    
    def _get_file_category(self, extension):
        """Categorize file by extension"""
        for category, extensions in self.supported_extensions.items():
            if extension in extensions:
                return category
        return 'other'
    
    def get_quick_stats(self, directory_path):
        """Get quick directory statistics without full analysis"""
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
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'formatted_size': self._format_size(total_size)
            }
            
        except Exception as e:
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