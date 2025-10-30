import os
from pathlib import Path
from difflib import SequenceMatcher
import mimetypes, datetime

# Remove the autoLogger import section and replace with:
try:
    from ..utils.logger_setup import general_logger
except ImportError:
    # Fallback if logger is not available
    print("Logger import failed for template matcher, using DummyLogger")
    class DummyLogger:
        def __init__(self, filename): 
            self.file = open(filename, 'a')
            self.file.write("Logging started...\n"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"\n")
            self.file.close()
        def addToLogs(self, msg): print(f"[LOG] {msg}")
        def addToErrorLogs(self, msg): print(f"[ERROR] {msg}")
        def addToInputLogs(self, prompt, msg): print(f"[INPUT] {prompt}: {msg}")
    general_logger = DummyLogger

class TemplateMatcher:
    def __init__(self):
        # Initialize logger
        log_file_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'template_matcher.txt')
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        self.logger = general_logger(log_file_path)
        
        self.similarity_threshold = 0.6
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit for content comparison
        
        self.logger.addToLogs(f"TemplateMatcher initialized with similarity threshold: {self.similarity_threshold}")
        self.logger.addToLogs(f"Max file size for content comparison: {self.max_file_size / 1024 / 1024:.1f} MB")
    
    def find_similar_files(self, directory_path, templates):
        """Find files similar to uploaded templates"""
        self.logger.addToLogs(f"Starting template matching for {len(templates)} templates in {directory_path}")
        
        matching_results = []
        
        for i, template in enumerate(templates):
            template_path = template['path']
            template_category = template['category']
            template_filename = template['filename']
            
            self.logger.addToLogs(f"Processing template {i+1}/{len(templates)}: {template_filename} (Category: {template_category})")
            
            # Get template characteristics
            template_info = self._analyze_template(template_path)
            
            # Find matching files in directory
            matches = self._find_matches_in_directory(
                directory_path, 
                template_info, 
                template_category
            )
            
            if matches:
                self.logger.addToLogs(f"Found {len(matches)} matches for template: {template_filename}")
                matching_results.append({
                    'category': template_category,
                    'template_file': template_filename,
                    'template_path': template_path,
                    'matched_files': [match['file_path'] for match in matches],
                    'similarity_scores': [match['similarity'] for match in matches],
                    'match_details': matches
                })
            else:
                self.logger.addToLogs(f"No matches found for template: {template_filename}")
        
        self.logger.addToLogs(f"Template matching complete: {len(matching_results)} categories with matches")
        return matching_results
    
    def _analyze_template(self, template_path):
        """Analyze template file characteristics"""
        self.logger.addToLogs(f"Analyzing template: {os.path.basename(template_path)}")
        
        template_info = {
            'path': template_path,
            'filename': os.path.basename(template_path),
            'extension': Path(template_path).suffix.lower(),
            'size': 0,
            'content': None,
            'mime_type': None
        }
        
        try:
            template_info['size'] = os.path.getsize(template_path)
            template_info['mime_type'] = mimetypes.guess_type(template_path)[0]
            
            self.logger.addToLogs(f"Template info - Size: {template_info['size']} bytes, Type: {template_info['extension']}")
            
            # Extract content for text-based files
            if template_info['size'] < self.max_file_size:
                template_info['content'] = self._extract_file_content(template_path)
                if template_info['content']:
                    content_length = len(template_info['content']) if isinstance(template_info['content'], str) else len(template_info['content'])
                    self.logger.addToLogs(f"Extracted {content_length} characters/bytes of content from template")
            else:
                self.logger.addToLogs(f"Template too large for content analysis: {template_info['size']} bytes")
        
        except Exception as e:
            self.logger.addToErrorLogs(f"Error analyzing template {template_path}: {str(e)}")
            template_info['error'] = str(e)
        
        return template_info
    
    def _find_matches_in_directory(self, directory_path, template_info, category):
        """Find files in directory that match the template"""
        self.logger.addToLogs(f"Searching for matches in directory for category: {category}")
        
        matches = []
        template_ext = template_info['extension']
        template_content = template_info.get('content')
        files_checked = 0
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file_path).suffix.lower()
                files_checked += 1
                
                # Skip if different file type
                if file_ext != template_ext:
                    continue
                
                try:
                    similarity_score = self._calculate_similarity(
                        template_info, 
                        file_path, 
                        template_content
                    )
                    
                    if similarity_score >= self.similarity_threshold:
                        matches.append({
                            'file_path': file_path,
                            'filename': os.path.basename(file_path),
                            'similarity': similarity_score,
                            'category': category,
                            'file_size': os.path.getsize(file_path)
                        })
                        
                        self.logger.addToLogs(f"Match found: {os.path.basename(file_path)} (similarity: {similarity_score:.3f})")
                
                except Exception as e:
                    self.logger.addToErrorLogs(f"Error processing file {file_path}: {str(e)}")
                    continue
        
        self.logger.addToLogs(f"Checked {files_checked} files, found {len(matches)} matches above threshold")
        
        # Sort by similarity score (highest first)
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        return matches
    
    def _calculate_similarity(self, template_info, file_path, template_content):
        """Calculate similarity between template and file"""
        similarity_scores = []
        
        # 1. Filename similarity (30% weight)
        filename_similarity = self._calculate_filename_similarity(
            template_info['filename'], 
            os.path.basename(file_path)
        )
        similarity_scores.append(('filename', filename_similarity, 0.3))
        
        # 2. File size similarity (20% weight)
        try:
            file_size = os.path.getsize(file_path)
            size_similarity = self._calculate_size_similarity(
                template_info['size'], 
                file_size
            )
            similarity_scores.append(('size', size_similarity, 0.2))
        except:
            similarity_scores.append(('size', 0, 0.2))
        
        # 3. Content similarity (50% weight) - if available
        if template_content and file_path.endswith(template_info['extension']):
            try:
                file_content = self._extract_file_content(file_path)
                if file_content:
                    content_similarity = self._calculate_content_similarity(
                        template_content, 
                        file_content
                    )
                    similarity_scores.append(('content', content_similarity, 0.5))
                else:
                    similarity_scores.append(('content', 0, 0.5))
            except:
                similarity_scores.append(('content', 0, 0.5))
        else:
            # If no content comparison possible, redistribute weights
            similarity_scores = [
                ('filename', filename_similarity, 0.6),
                ('size', size_similarity if 'file_size' in locals() else 0, 0.4)
            ]
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in similarity_scores)
        return round(total_score, 3)
    
    def _calculate_filename_similarity(self, template_name, file_name):
        """Calculate similarity between filenames"""
        # Remove extensions for comparison
        template_base = Path(template_name).stem.lower()
        file_base = Path(file_name).stem.lower()
        
        return SequenceMatcher(None, template_base, file_base).ratio()
    
    def _calculate_size_similarity(self, template_size, file_size):
        """Calculate similarity between file sizes"""
        if template_size == 0 and file_size == 0:
            return 1.0
        
        if template_size == 0 or file_size == 0:
            return 0.0
        
        # Calculate relative difference
        larger = max(template_size, file_size)
        smaller = min(template_size, file_size)
        
        ratio = smaller / larger
        return ratio
    
    def _calculate_content_similarity(self, template_content, file_content):
        """Calculate similarity between file contents"""
        if not template_content or not file_content:
            return 0.0
        
        # For text files, use sequence matching
        if isinstance(template_content, str) and isinstance(file_content, str):
            # Normalize whitespace and compare
            template_normalized = ' '.join(template_content.split())
            file_normalized = ' '.join(file_content.split())
            
            return SequenceMatcher(None, template_normalized, file_normalized).ratio()
        
        # For binary files, compare first 1KB
        if isinstance(template_content, bytes) and isinstance(file_content, bytes):
            template_sample = template_content[:1024]
            file_sample = file_content[:1024]
            
            return SequenceMatcher(None, template_sample, file_sample).ratio()
        
        return 0.0
    
    def _extract_file_content(self, file_path):
        """Extract content from file for comparison"""
        try:
            file_size = os.path.getsize(file_path)
            
            # Skip large files
            if file_size > self.max_file_size:
                return None
            
            file_ext = Path(file_path).suffix.lower()
            
            # Text-based files
            if file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv']:
                return self._read_text_file(file_path)
            
            # Binary files - read as bytes for basic comparison
            elif file_ext in ['.pdf', '.docx', '.xlsx', '.pptx']:
                with open(file_path, 'rb') as f:
                    return f.read()
            
        except Exception as e:
            return None
        
        return None
    
    def _read_text_file(self, file_path):
        """Read text file with encoding detection"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        return None
    
    def group_matches_by_similarity(self, matches, bins=5):
        """Group matches by similarity ranges"""
        if not matches:
            return {}
        
        # Create similarity bins
        groups = {}
        for i in range(bins):
            lower = i / bins
            upper = (i + 1) / bins
            if i == bins - 1:  # Last bin includes 1.0
                upper = 1.0
            
            group_name = f"{lower:.1f}-{upper:.1f}"
            groups[group_name] = []
        
        # Assign matches to groups
        for match in matches:
            similarity = match['similarity']
            
            for i in range(bins):
                lower = i / bins
                upper = (i + 1) / bins
                if i == bins - 1:
                    upper = 1.0
                
                if lower <= similarity <= upper:
                    group_name = f"{lower:.1f}-{upper:.1f}"
                    groups[group_name].append(match)
                    break
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def get_match_statistics(self, matching_results):
        """Generate statistics from matching results"""
        stats = {
            'total_categories': len(matching_results),
            'total_matches': 0,
            'average_similarity': 0,
            'matches_by_category': {},
            'highest_similarity': 0,
            'lowest_similarity': 1.0
        }
        
        all_similarities = []
        
        for result in matching_results:
            category = result['category']
            matches_count = len(result['matched_files'])
            similarities = result['similarity_scores']
            
            stats['total_matches'] += matches_count
            stats['matches_by_category'][category] = {
                'count': matches_count,
                'avg_similarity': sum(similarities) / len(similarities) if similarities else 0,
                'max_similarity': max(similarities) if similarities else 0,
                'min_similarity': min(similarities) if similarities else 0
            }
            
            all_similarities.extend(similarities)
            
            if similarities:
                stats['highest_similarity'] = max(stats['highest_similarity'], max(similarities))
                stats['lowest_similarity'] = min(stats['lowest_similarity'], min(similarities))
        
        if all_similarities:
            stats['average_similarity'] = sum(all_similarities) / len(all_similarities)
        
        return stats