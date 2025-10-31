import os
import time
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

# Remove the autoLogger import section and replace with:
try:
    from ..utils.logger_setup import general_logger
except ImportError:
    # Fallback if logger is not available
    print("Logger import failed for directory analyzer, using DummyLogger")
    class DummyLogger:
        def __init__(self, filename): 
            self.file = open(filename, 'a')
            self.file.write("Logging started...\n"+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"\n")
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
        """Enhanced directory analysis with path length protection"""
        self.logger.addToLogs(f"Starting directory analysis for: {directory_path}")
        
        try:
            total_files = 0
            total_size = 0
            file_type_categories = {}
            skipped_files = 0
            
            # Walk through directory with path length protection
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        
                        # Check path length (Windows limit is ~260 chars)
                        if len(file_path) > 250:
                            self.logger.addToLogs(f"Skipping file with long path: {file_path[:100]}...")
                            skipped_files += 1
                            continue
                        
                        # Check if file exists and is accessible
                        if not os.path.exists(file_path):
                            self.logger.addToLogs(f"Skipping non-existent file: {file_path}")
                            skipped_files += 1
                            continue
                        
                        # Get file stats safely
                        try:
                            file_stat = os.stat(file_path)
                            file_size = file_stat.st_size
                            total_size += file_size
                            total_files += 1
                            
                            # Get file extension
                            _, ext = os.path.splitext(file.lower())
                            if ext:
                                ext = ext[1:]  # Remove the dot
                                file_type_categories[ext] = file_type_categories.get(ext, 0) + 1
                            else:
                                file_type_categories['no_extension'] = file_type_categories.get('no_extension', 0) + 1
                                
                        except (OSError, PermissionError) as e:
                            self.logger.addToLogs(f"Could not access file {file}: {str(e)}")
                            skipped_files += 1
                            continue
                            
                    except Exception as e:
                        self.logger.addToLogs(f"Error processing file {file}: {str(e)}")
                        skipped_files += 1
                        continue
            
            if skipped_files > 0:
                self.logger.addToLogs(f"Analysis complete: {total_files} files processed, {skipped_files} files skipped")
            else:
                self.logger.addToLogs(f"Analysis complete: {total_files} files processed")
            
            return {
                'total_files': total_files,
                'total_size': total_size,
                'file_type_categories': file_type_categories,
                'skipped_files': skipped_files
            }
            
        except Exception as e:
            self.logger.addToErrorLogs(f"Directory analysis failed: {str(e)}")
            raise
    
    def _analyze_directory_structure(self, directory_path):
        """Analyze the hierarchical structure of the directory"""
        self.logger.addToLogs("Analyzing directory structure")
        
        structure = {
            'directories': [],
            'directory_tree': {},
            'max_depth': 0,
            'total_directories': 0,
            'files_per_directory': {},
            'empty_directories': [],
            'deepest_paths': []
        }
        
        try:
            for root, dirs, files in os.walk(directory_path):
                # Calculate depth relative to the starting directory
                relative_path = os.path.relpath(root, directory_path)
                depth = 0 if relative_path == '.' else len(relative_path.split(os.sep))
                
                # Update max depth
                structure['max_depth'] = max(structure['max_depth'], depth)
                
                # Store directory info
                dir_info = {
                    'path': root,
                    'relative_path': relative_path,
                    'depth': depth,
                    'subdirectories': len(dirs),
                    'files': len(files),
                    'file_list': files[:10],  # Store first 10 files for analysis
                    'subdirectory_list': dirs
                }
                
                structure['directories'].append(dir_info)
                structure['total_directories'] += 1
                structure['files_per_directory'][relative_path] = len(files)
                
                # Track empty directories
                if len(files) == 0 and len(dirs) == 0:
                    structure['empty_directories'].append(relative_path)
                
                # Track deepest paths
                if depth >= structure['max_depth'] - 1:
                    structure['deepest_paths'].append({
                        'path': relative_path,
                        'depth': depth,
                        'files': len(files)
                    })
            
            # Build hierarchical tree structure
            structure['directory_tree'] = self._build_directory_tree(directory_path)
            
            self.logger.addToLogs(f"Directory structure analysis complete: {structure['total_directories']} directories, max depth: {structure['max_depth']}")
            return structure
            
        except Exception as e:
            self.logger.addToErrorLogs(f"Directory structure analysis failed: {str(e)}")
            return structure
    
    def _build_directory_tree(self, directory_path):
        """Build a hierarchical representation of the directory structure"""
        tree = {}
        
        try:
            for root, dirs, files in os.walk(directory_path):
                # Get path components relative to the base directory
                relative_path = os.path.relpath(root, directory_path)
                
                if relative_path == '.':
                    # Root directory
                    tree['name'] = os.path.basename(directory_path)
                    tree['type'] = 'directory'
                    tree['children'] = []
                    tree['file_count'] = len(files)
                    tree['directory_count'] = len(dirs)
                else:
                    # Navigate to correct position in tree
                    path_parts = relative_path.split(os.sep)
                    current_node = tree
                    
                    for part in path_parts:
                        # Find or create the directory node
                        child_node = None
                        if 'children' in current_node:
                            for child in current_node['children']:
                                if child['name'] == part and child['type'] == 'directory':
                                    child_node = child
                                    break
                        
                        if not child_node:
                            child_node = {
                                'name': part,
                                'type': 'directory',
                                'children': [],
                                'file_count': 0,
                                'directory_count': 0
                            }
                            if 'children' not in current_node:
                                current_node['children'] = []
                            current_node['children'].append(child_node)
                        
                        current_node = child_node
                    
                    # Update file and directory counts
                    current_node['file_count'] = len(files)
                    current_node['directory_count'] = len(dirs)
            
            return tree
            
        except Exception as e:
            self.logger.addToErrorLogs(f"Directory tree building failed: {str(e)}")
            return {'name': 'Error', 'type': 'directory', 'children': []}
    
    def _analyze_organization_patterns(self, directory_path):
        """Analyze organizational patterns and metrics"""
        self.logger.addToLogs("Analyzing organization patterns")
        
        metrics = {
            'naming_conventions': {},
            'file_distribution': {},
            'depth_analysis': {},
            'organization_score': 0,
            'common_patterns': [],
            'potential_issues': []
        }
        
        try:
            # Analyze naming conventions
            directory_names = []
            file_names = []
            
            for root, dirs, files in os.walk(directory_path):
                directory_names.extend(dirs)
                file_names.extend(files)
            
            # Analyze naming patterns
            metrics['naming_conventions'] = {
                'uses_underscores': len([n for n in directory_names if '_' in n]) / max(len(directory_names), 1),
                'uses_hyphens': len([n for n in directory_names if '-' in n]) / max(len(directory_names), 1),
                'uses_spaces': len([n for n in directory_names if ' ' in n]) / max(len(directory_names), 1),
                'camel_case': len([n for n in directory_names if any(c.isupper() for c in n[1:])]) / max(len(directory_names), 1),
                'all_lowercase': len([n for n in directory_names if n.islower()]) / max(len(directory_names), 1)
            }
            
            # Analyze file distribution
            files_per_dir = []
            for root, dirs, files in os.walk(directory_path):
                files_per_dir.append(len(files))
            
            if files_per_dir:
                metrics['file_distribution'] = {
                    'average_files_per_directory': sum(files_per_dir) / len(files_per_dir),
                    'max_files_in_directory': max(files_per_dir),
                    'min_files_in_directory': min(files_per_dir),
                    'directories_with_many_files': len([x for x in files_per_dir if x > 50])
                }
            
            # Calculate organization score (0-100)
            score = 50  # Base score
            
            # Bonus for reasonable depth (not too shallow, not too deep)
            max_depth = 0
            for root, dirs, files in os.walk(directory_path):
                depth = len(os.path.relpath(root, directory_path).split(os.sep))
                max_depth = max(max_depth, depth)
            
            if 2 <= max_depth <= 5:
                score += 20
            elif max_depth > 8:
                score -= 20
                metrics['potential_issues'].append("Directory structure is very deep (may be hard to navigate)")
            
            # Bonus for consistent naming
            if metrics['naming_conventions']['all_lowercase'] > 0.8:
                score += 15
                metrics['common_patterns'].append("Consistent lowercase naming")
            
            # Penalty for too many files in single directories
            if metrics['file_distribution'].get('max_files_in_directory', 0) > 100:
                score -= 15
                metrics['potential_issues'].append("Some directories contain too many files")
            
            metrics['organization_score'] = max(0, min(100, score))
            
            self.logger.addToLogs(f"Organization analysis complete: score {metrics['organization_score']}/100")
            return metrics
            
        except Exception as e:
            self.logger.addToErrorLogs(f"Organization pattern analysis failed: {str(e)}")
            return metrics
    
    def _generate_structure_summary(self, directory_structure):
        """Generate a text summary of the directory structure"""
        try:
            summary = []
            
            total_dirs = directory_structure.get('total_directories', 0)
            max_depth = directory_structure.get('max_depth', 0)
            empty_dirs = len(directory_structure.get('empty_directories', []))
            
            summary.append(f"Directory contains {total_dirs} subdirectories with maximum depth of {max_depth} levels")
            
            if empty_dirs > 0:
                summary.append(f"Found {empty_dirs} empty directories")
            
            # Find directories with most files
            files_per_dir = directory_structure.get('files_per_directory', {})
            if files_per_dir:
                busiest_dir = max(files_per_dir.items(), key=lambda x: x[1])
                summary.append(f"Busiest directory: '{busiest_dir[0]}' with {busiest_dir[1]} files")
            
            return " | ".join(summary)
            
        except Exception as e:
            self.logger.addToErrorLogs(f"Structure summary generation failed: {str(e)}")
            return "Structure summary unavailable"
    
    def _get_basic_analysis(self, directory_path):
        """Your existing basic analysis method (rename from analyze_directory)"""
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