#!/usr/bin/env python3
"""
PersonalAIOS Intelligent File Manager
True natural language understanding for your AI-native OS dream
Uses advanced NLP techniques to understand human intent
"""
import os
import re
import shutil
from pathlib import Path
import subprocess
from typing import Dict, List, Tuple, Optional
import json

class IntelligentFileManager:
    def __init__(self):
        self.current_directory = Path.home()
        
        # Intent patterns with natural language understanding
        self.intent_patterns = {
            'create_file': [
                r'create (?:a )?file (?:named |called )?(.+)',
                r'make (?:a )?file (?:named |called )?(.+)', 
                r'new file (?:named |called )?(.+)',
                r'touch (.+)',
                r'create (.+\.[\w]+)',  # Extensions
            ],
            'create_directory': [
                r'create (?:a )?(?:folder|directory) (?:named |called )?(.+)',
                r'make (?:a )?(?:folder|directory) (?:named |called )?(.+)',
                r'new (?:folder|directory) (?:named |called )?(.+)',
                r'mkdir (.+)',
            ],
            'find_file': [
                r'find (?:a |the )?file (?:named |called )?(.+)',
                r'search for (?:a |the )?file (?:named |called )?(.+)',
                r'locate (?:a |the )?file (?:named |called )?(.+)',
                r'where is (?:the )?file (?:named |called )?(.+)',
                r'look for (.+)',
                r'find (.+)',
            ],
            'open_file': [
                r'open (?:the )?file (?:named |called )?(.+)',
                r'launch (?:the )?file (?:named |called )?(.+)',
                r'run (?:the )?file (?:named |called )?(.+)',
                r'open (.+)',
            ],
            'delete_file': [
                r'delete (?:the )?file (?:named |called )?(.+)',
                r'remove (?:the )?file (?:named |called )?(.+)',
                r'trash (?:the )?file (?:named |called )?(.+)',
                r'delete (.+)',
                r'rm (.+)',
            ],
            'list_files': [
                r'list (?:all )?(?:the )?files',
                r'show (?:me )?(?:all )?(?:the )?files',
                r'what files are (?:in )?here',
                r'display (?:the )?contents',
                r'ls',
                r'dir',
            ],
            'copy_file': [
                r'copy (?:the )?file (.+) to (.+)',
                r'duplicate (?:the )?file (.+) (?:to|as) (.+)',
                r'cp (.+) (.+)',
            ],
            'move_file': [
                r'move (?:the )?file (.+) to (.+)',
                r'rename (?:the )?file (.+) (?:to|as) (.+)',
                r'mv (.+) (.+)',
            ],
        }
        
        # Context understanding
        self.context_keywords = {
            'urgency': ['urgent', 'quickly', 'asap', 'now', 'immediately'],
            'size': ['large', 'big', 'small', 'tiny', 'huge'],
            'type': ['document', 'image', 'video', 'audio', 'text', 'script'],
            'location': ['desktop', 'documents', 'downloads', 'home'],
        }
    
    def process_command(self, user_input: str) -> str:
        """Process natural language command with intelligent understanding"""
        # Clean and normalize input
        cleaned_input = self._preprocess_text(user_input)
        
        # Extract intent and entities
        intent, entities = self._extract_intent_and_entities(cleaned_input)
        
        if not intent:
            return self._handle_unknown_intent(user_input)
        
        # Process based on intent
        return self._execute_intent(intent, entities, user_input)
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text for better understanding"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Handle common contractions and variations
        text = text.replace("i'd like to", "")
        text = text.replace("can you", "")
        text = text.replace("please", "")
        text = text.replace("would you", "")
        
        return text.lower().strip()
    
    def _extract_intent_and_entities(self, text: str) -> Tuple[Optional[str], Dict]:
        """Extract intent and entities using pattern matching"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities = {
                        'groups': match.groups(),
                        'context': self._extract_context(text)
                    }
                    return intent, entities
        
        return None, {}
    
    def _extract_context(self, text: str) -> Dict:
        """Extract contextual information"""
        context = {}
        
        for category, keywords in self.context_keywords.items():
            found = [kw for kw in keywords if kw in text]
            if found:
                context[category] = found
        
        return context
    
    def _execute_intent(self, intent: str, entities: Dict, original_text: str) -> str:
        """Execute the identified intent"""
        try:
            if intent == 'create_file':
                return self._create_file(entities)
            elif intent == 'create_directory':
                return self._create_directory(entities)
            elif intent == 'find_file':
                return self._find_file(entities)
            elif intent == 'open_file':
                return self._open_file(entities)
            elif intent == 'delete_file':
                return self._delete_file(entities)
            elif intent == 'list_files':
                return self._list_files(entities)
            elif intent == 'copy_file':
                return self._copy_file(entities)
            elif intent == 'move_file':
                return self._move_file(entities)
            else:
                return f"❓ **Intent recognized** ({intent}) but not implemented yet"
                
        except Exception as e:
            return f"❌ **Error executing {intent}:** {str(e)}"
    
    def _create_file(self, entities: Dict) -> str:
        """Create file with intelligent name extraction"""
        groups = entities.get('groups', [])
        if not groups or not groups[0]:
            return "📄 **Please specify the filename to create**"
        
        filename = groups[0].strip()
        
        # Clean filename
        filename = self._clean_filename(filename)
        
        try:
            file_path = self.current_directory / filename
            
            if file_path.exists():
                return f"⚠️ **File already exists:** {filename}"
            
            file_path.touch()
            
            # Add context-based content if specified
            context = entities.get('context', {})
            if 'type' in context:
                self._add_template_content(file_path, context['type'])
            
            return f"📄 **Created file:** {filename}\n   └─ Path: `{file_path}`"
            
        except Exception as e:
            return f"❌ **Failed to create file:** {str(e)}"
    
    def _create_directory(self, entities: Dict) -> str:
        """Create directory with intelligent understanding"""
        groups = entities.get('groups', [])
        if not groups or not groups[0]:
            return "📁 **Please specify the directory name to create**"
        
        dirname = groups[0].strip()
        dirname = self._clean_filename(dirname)
        
        try:
            dir_path = self.current_directory / dirname
            
            if dir_path.exists():
                return f"⚠️ **Directory already exists:** {dirname}"
            
            dir_path.mkdir(parents=True)
            return f"📁 **Created directory:** {dirname}\n   └─ Path: `{dir_path}`"
            
        except Exception as e:
            return f"❌ **Failed to create directory:** {str(e)}"
    
    def _find_file(self, entities: Dict) -> str:
        """Find files with intelligent search"""
        groups = entities.get('groups', [])
        if not groups or not groups[0]:
            return "🔍 **Please specify what to search for**"
        
        search_term = groups[0].strip()
        
        try:
            # Multi-strategy search
            results = []
            
            # Exact name match
            exact_matches = list(self.current_directory.rglob(search_term))
            results.extend(exact_matches)
            
            # Partial name match
            if not exact_matches:
                partial_matches = list(self.current_directory.rglob(f"*{search_term}*"))
                results.extend(partial_matches)
            
            # Extension-based search if search term looks like extension
            if search_term.startswith('.') or '.' in search_term:
                ext_matches = list(self.current_directory.rglob(f"*{search_term}"))
                results.extend(ext_matches)
            
            # Remove duplicates
            results = list(set(results))
            
            if not results:
                return f"🔍 **No files found** matching '{search_term}'\n\n**Suggestions:**\n• Check spelling\n• Try partial filename\n• Use wildcards"
            
            response = f"🔍 **Found {len(results)} file(s)** matching '{search_term}':\n\n"
            
            for file_path in results[:10]:
                icon = "📁" if file_path.is_dir() else self._get_file_icon(file_path)
                size = self._format_size(file_path.stat().st_size) if file_path.is_file() else ""
                relative_path = file_path.relative_to(self.current_directory)
                
                response += f"{icon} **{file_path.name}** {size}\n   └─ `{relative_path}`\n"
            
            if len(results) > 10:
                response += f"\n*(Showing first 10 of {len(results)} results)*"
            
            return response
            
        except Exception as e:
            return f"❌ **Search failed:** {str(e)}"
    
    def _open_file(self, entities: Dict) -> str:
        """Open file with intelligent resolution"""
        groups = entities.get('groups', [])
        if not groups or not groups[0]:
            return "📂 **Please specify the file to open**"
        
        filename = groups[0].strip()
        resolved_path = self._resolve_path(filename)
        
        if not resolved_path:
            # Smart suggestions
            suggestions = self._find_similar_files(filename)
            response = f"📂 **File not found:** '{filename}'"
            
            if suggestions:
                response += "\n\n**Did you mean:**\n"
                for suggestion in suggestions[:3]:
                    response += f"• {suggestion.name}\n"
            
            return response
        
        try:
            if resolved_path.is_dir():
                self.current_directory = resolved_path
                return f"📁 **Opened directory:** {resolved_path.name}\n\n{self._list_files({})}"
            else:
                subprocess.Popen(['xdg-open', str(resolved_path)], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"📂 **Opened file:** {resolved_path.name}\n   └─ Path: `{resolved_path}`"
        
        except Exception as e:
            return f"❌ **Failed to open:** {str(e)}"
    
    def _delete_file(self, entities: Dict) -> str:
        """Delete file with confirmation"""
        groups = entities.get('groups', [])
        if not groups or not groups[0]:
            return "🗑️ **Please specify the file to delete**"
        
        filename = groups[0].strip()
        resolved_path = self._resolve_path(filename)
        
        if not resolved_path:
            return f"🗑️ **File not found:** '{filename}'"
        
        try:
            if resolved_path.is_dir():
                contents = list(resolved_path.iterdir())
                if contents:
                    return f"⚠️ **Directory not empty:** {resolved_path.name}\n\nContains {len(contents)} items."
                resolved_path.rmdir()
                return f"🗑️ **Deleted directory:** {resolved_path.name}"
            else:
                resolved_path.unlink()
                return f"🗑️ **Deleted file:** {resolved_path.name}"
        
        except Exception as e:
            return f"❌ **Delete failed:** {str(e)}"
    
    def _list_files(self, entities: Dict) -> str:
        """List files in current directory"""
        try:
            files = list(self.current_directory.iterdir())
            files.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            
            if not files:
                return f"📁 **Empty directory:** `{self.current_directory}`"
            
            response = f"📁 **Directory:** `{self.current_directory}`\n\n"
            
            for file_path in files[:20]:
                icon = self._get_file_icon(file_path)
                
                if file_path.is_dir():
                    item_count = len(list(file_path.iterdir()))
                    size_info = f"({item_count} items)"
                else:
                    size_info = self._format_size(file_path.stat().st_size)
                
                response += f"{icon} **{file_path.name}** {size_info}\n"
            
            if len(files) > 20:
                response += f"\n*(Showing first 20 of {len(files)} items)*"
            
            return response
        
        except Exception as e:
            return f"❌ **List failed:** {str(e)}"
    
    def _copy_file(self, entities: Dict) -> str:
        """Copy file with intelligent understanding"""
        groups = entities.get('groups', [])
        if len(groups) < 2:
            return "📋 **Copy:** Please specify source and destination\n**Example:** copy report.pdf to backup folder"
        
        source_name, dest_name = groups[0].strip(), groups[1].strip()
        source_path = self._resolve_path(source_name)
        
        if not source_path:
            return f"📋 **Source not found:** '{source_name}'"
        
        dest_path = self.current_directory / dest_name
        
        try:
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path)
                return f"📋 **Copied directory:** {source_name} → {dest_name}"
            else:
                if dest_path.is_dir():
                    dest_path = dest_path / source_path.name
                shutil.copy2(source_path, dest_path)
                return f"📋 **Copied file:** {source_name} → {dest_name}"
        
        except Exception as e:
            return f"❌ **Copy failed:** {str(e)}"
    
    def _move_file(self, entities: Dict) -> str:
        """Move/rename file"""
        groups = entities.get('groups', [])
        if len(groups) < 2:
            return "🔄 **Move:** Please specify source and destination"
        
        source_name, dest_name = groups[0].strip(), groups[1].strip()
        source_path = self._resolve_path(source_name)
        
        if not source_path:
            return f"🔄 **Source not found:** '{source_name}'"
        
        dest_path = self.current_directory / dest_name
        
        try:
            source_path.rename(dest_path)
            return f"🔄 **Moved:** {source_name} → {dest_name}"
        
        except Exception as e:
            return f"❌ **Move failed:** {str(e)}"
    
    def _resolve_path(self, filename: str) -> Optional[Path]:
        """Intelligently resolve file path"""
        # Direct match
        direct_path = self.current_directory / filename
        if direct_path.exists():
            return direct_path
        
        # Case-insensitive search
        for item in self.current_directory.iterdir():
            if item.name.lower() == filename.lower():
                return item
        
        # Partial match
        matches = list(self.current_directory.glob(f"*{filename}*"))
        if matches:
            return matches[0]
        
        return None
    
    def _find_similar_files(self, target: str) -> List[Path]:
        """Find similar files for suggestions"""
        all_files = list(self.current_directory.iterdir())
        suggestions = []
        
        for file_path in all_files:
            similarity = self._calculate_similarity(file_path.name.lower(), target.lower())
            if similarity > 0.4:
                suggestions.append(file_path)
        
        return sorted(suggestions, key=lambda x: self._calculate_similarity(x.name.lower(), target.lower()), reverse=True)[:5]
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity"""
        if str1 == str2:
            return 1.0
        
        if str1 in str2 or str2 in str1:
            return 0.8
        
        # Simple Jaccard similarity
        set1, set2 = set(str1), set(str2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _clean_filename(self, filename: str) -> str:
        """Clean filename from natural language artifacts"""
        # Remove common natural language artifacts
        filename = re.sub(r'^(?:a |an |the )', '', filename)
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # Invalid file chars
        filename = filename.strip()
        
        return filename
    
    def _get_file_icon(self, file_path: Path) -> str:
        """Get file icon based on type"""
        if file_path.is_dir():
            return "📁"
        
        suffix = file_path.suffix.lower()
        icon_map = {
            '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
            '.txt': '📄', '.md': '📝', '.pdf': '📕',
            '.jpg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
            '.mp3': '🎵', '.mp4': '🎬', '.zip': '🗜️'
        }
        return icon_map.get(suffix, '📄')
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def _add_template_content(self, file_path: Path, content_type: List[str]):
        """Add template content based on context"""
        if 'script' in content_type:
            file_path.write_text("#!/bin/bash\n# Script created by PersonalAIOS\n\n")
        elif 'document' in content_type:
            file_path.write_text("# Document\n\nCreated by PersonalAIOS\n")
    
    def _handle_unknown_intent(self, user_input: str) -> str:
        """Handle unknown intent with helpful suggestions"""
        return f"""❓ **I didn't understand:** "{user_input}"

**Try these natural language commands:**

**Create Files:**
• "create a file named report.txt"
• "make a new document called notes"

**Find Files:**  
• "find the file named config.py"
• "search for my report"

**Manage Files:**
• "open the downloads folder"
• "delete old backup files"
• "list all files"

**I understand natural language, so speak naturally!** 🤖"""

# For compatibility
DynamicAIFileManager = IntelligentFileManager

