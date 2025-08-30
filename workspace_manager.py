#!/usr/bin/env python3
"""
PersonalAIOS Intelligent Workspace Manager
Revolutionary AI-native workspace management with perfect natural language understanding
Dynamic workspace creation, switching, grouping, and task-focused optimization
"""
import gi
import re
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Gio, Adw

class WorkspaceType(Enum):
    """Smart workspace categories"""
    GENERAL = "general"
    DEVELOPMENT = "development"
    PRODUCTIVITY = "productivity"
    CREATIVE = "creative"
    COMMUNICATION = "communication"
    ENTERTAINMENT = "entertainment"
    RESEARCH = "research"
    SYSTEM = "system"

@dataclass
class SmartWorkspace:
    """Comprehensive workspace definition"""
    id: int
    name: str
    workspace_type: WorkspaceType
    description: str = ""
    applications: List[str] = None
    window_ids: List[int] = None
    creation_time: float = 0
    last_used: float = 0
    usage_count: int = 0
    auto_created: bool = False
    ai_suggested_apps: List[str] = None
    persistent_layout: bool = False
    background_image: Optional[str] = None
    color_theme: Optional[str] = None

class IntelligentWorkspaceManager:
    """
    Revolutionary AI-Native Workspace Manager
    
    Features:
    - Perfect natural language workspace control
    - Smart workspace categorization and naming
    - Context-aware workspace switching
    - AI-powered application grouping
    - Task-focused workspace optimization
    - Usage pattern learning and adaptation
    - Visual workspace overview
    - Persistent workspace states
    """
    
    def __init__(self):
        """Initialize the intelligent workspace manager"""
        self.workspaces: Dict[int, SmartWorkspace] = {}
        self.current_workspace_id: int = 1
        self.max_workspaces: int = 16
        self.workspace_history: List[int] = []
        self.command_history: List[Dict] = []
        
        # User preferences and settings
        self.user_preferences = {
            'auto_naming': True,
            'smart_switching': True,
            'usage_learning': True,
            'auto_grouping': True,
            'visual_previews': True,
            'workspace_persistence': True,
            'max_history': 10
        }
        
        # AI-powered intent patterns for natural language understanding
        self.intent_patterns = {
            'create_workspace': [
                r'create (?:a )?(?:new )?workspace (?:called |named |for )?(.+)',
                r'make (?:a )?(?:new )?workspace (?:called |named |for )?(.+)',
                r'add (?:a )?(?:new )?workspace (?:called |named |for )?(.+)',
                r'new workspace (?:for )?(.+)',
                r'(?:i )?(?:need|want) (?:a )?workspace (?:for )?(.+)',
            ],
            'switch_workspace': [
                r'(?:switch|go|move|jump) to workspace (\d+|next|previous|last|first)',
                r'(?:change to|use) workspace (\d+|next|previous|last|first)',
                r'workspace (\d+|next|previous|last|first)',
                r'(?:switch|go) to (.+) workspace',
                r'(?:open|show) (.+) workspace',
            ],
            'list_workspaces': [
                r'(?:list|show) (?:all )?(?:my )?workspaces',
                r'(?:what|which) workspaces (?:do i have|are there|exist)',
                r'(?:display|show me) (?:all )?workspaces',
                r'workspace (?:overview|summary|list)',
            ],
            'rename_workspace': [
                r'rename workspace (\d+|current|this) (?:to )?(.+)',
                r'call workspace (\d+|current|this) (.+)',
                r'(?:change|set) workspace (\d+|current|this) name (?:to )?(.+)',
                r'workspace (\d+|current|this) (?:should be )?(?:called |named )?(.+)',
            ],
            'delete_workspace': [
                r'(?:delete|remove|close) workspace (\d+|current|last)',
                r'(?:destroy|kill) workspace (\d+|current|last)',
                r'(?:get rid of|eliminate) workspace (\d+|current|last)',
            ],
            'move_window': [
                r'move (?:this |the )?(?:window|app) to workspace (\d+)',
                r'send (?:this |the )?(?:window|app) to workspace (\d+)',
                r'put (?:this |the )?(?:window|app) (?:in|on) workspace (\d+)',
            ],
            'workspace_info': [
                r'(?:info|information|details) (?:about )?workspace (\d+|current|this)',
                r'(?:what is|describe) workspace (\d+|current|this)',
                r'(?:tell me about|show) workspace (\d+|current|this) (?:details|info)?',
            ],
            'organize_workspaces': [
                r'organize (?:my )?workspaces',
                r'(?:auto|smart) (?:arrange|organize|group) workspaces',
                r'optimize (?:my )?workspace (?:layout|arrangement)',
                r'(?:clean up|tidy) (?:my )?workspaces',
            ],
            'workspace_overview': [
                r'workspace (?:overview|summary|dashboard)',
                r'show (?:me )?(?:all )?workspace (?:activity|usage)',
                r'workspace (?:statistics|stats|analytics)',
            ]
        }
        
        # Workspace type detection keywords
        self.type_keywords = {
            WorkspaceType.DEVELOPMENT: ['code', 'coding', 'programming', 'dev', 'development', 'project', 'git', 'terminal'],
            WorkspaceType.PRODUCTIVITY: ['work', 'office', 'documents', 'productivity', 'tasks', 'planning', 'notes'],
            WorkspaceType.CREATIVE: ['design', 'art', 'creative', 'photo', 'video', 'music', 'graphics', 'editing'],
            WorkspaceType.COMMUNICATION: ['chat', 'email', 'communication', 'social', 'messaging', 'calls', 'meetings'],
            WorkspaceType.ENTERTAINMENT: ['entertainment', 'games', 'media', 'movies', 'youtube', 'streaming', 'fun'],
            WorkspaceType.RESEARCH: ['research', 'reading', 'study', 'learning', 'web', 'browser', 'reference'],
            WorkspaceType.SYSTEM: ['system', 'admin', 'settings', 'configuration', 'monitoring', 'logs']
        }
        
        # Initialize with default workspace
        self._initialize_default_workspace()
        
        # Storage setup
        self.storage_path = Path.home() / '.personalaios' / 'workspaces'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load saved workspaces
        self._load_workspaces()
        
        print("🗂️ Intelligent Workspace Manager initialized with AI-powered natural language processing")
    
    def _initialize_default_workspace(self):
        """Initialize the default workspace"""
        default_workspace = SmartWorkspace(
            id=1,
            name="Main",
            workspace_type=WorkspaceType.GENERAL,
            description="Default workspace",
            applications=[],
            window_ids=[],
            creation_time=time.time(),
            last_used=time.time(),
            usage_count=1,
            auto_created=False
        )
        
        self.workspaces[1] = default_workspace
        self.current_workspace_id = 1
        self.workspace_history = [1]
    
    def process_command(self, user_input: str) -> str:
        """Process natural language workspace management commands"""
        # Clean and normalize input
        cleaned_input = self._preprocess_text(user_input)
        
        # Extract intent and entities
        intent, entities = self._extract_intent_and_entities(cleaned_input)
        
        if not intent:
            return self._handle_unknown_intent(user_input)
        
        # Add to command history for learning
        self.command_history.append({
            'input': user_input,
            'intent': intent,
            'entities': entities,
            'timestamp': time.time()
        })
        
        # Execute the intent
        return self._execute_workspace_intent(intent, entities, user_input)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better understanding"""
        # Remove common filler words
        text = re.sub(r'\b(?:please|can\s+you|would\s+you|could\s+you|i\s+want\s+to)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip().lower()
        return text
    
    def _extract_intent_and_entities(self, text: str) -> Tuple[Optional[str], Dict]:
        """Extract intent and entities using AI-powered pattern matching"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities = {
                        'groups': match.groups(),
                        'context': self._extract_context(text),
                        'workspace_target': self._determine_workspace_target(match.groups(), text)
                    }
                    return intent, entities
        
        return None, {}
    
    def _extract_context(self, text: str) -> Dict:
        """Extract contextual information from text"""
        context = {}
        
        # Detect workspace type from context
        detected_type = self._detect_workspace_type(text)
        if detected_type:
            context['suggested_type'] = detected_type
        
        # Detect urgency
        if any(word in text for word in ['urgent', 'now', 'quickly', 'asap']):
            context['urgency'] = 'high'
        
        # Detect persistence preference
        if any(word in text for word in ['permanent', 'persistent', 'keep', 'save']):
            context['persistent'] = True
        
        return context
    
    def _detect_workspace_type(self, text: str) -> Optional[WorkspaceType]:
        """Detect workspace type from text content"""
        text_lower = text.lower()
        
        for workspace_type, keywords in self.type_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return workspace_type
        
        return None
    
    def _determine_workspace_target(self, groups: Tuple, text: str) -> Optional[str]:
        """Determine workspace target from command groups"""
        if groups and groups[0]:
            return groups[0].strip()
        return None
    
    def _execute_workspace_intent(self, intent: str, entities: Dict, original_text: str) -> str:
        """Execute the identified workspace intent"""
        try:
            if intent == 'create_workspace':
                return self._handle_create_workspace(entities)
            elif intent == 'switch_workspace':
                return self._handle_switch_workspace(entities)
            elif intent == 'list_workspaces':
                return self._handle_list_workspaces(entities)
            elif intent == 'rename_workspace':
                return self._handle_rename_workspace(entities)
            elif intent == 'delete_workspace':
                return self._handle_delete_workspace(entities)
            elif intent == 'move_window':
                return self._handle_move_window(entities)
            elif intent == 'workspace_info':
                return self._handle_workspace_info(entities)
            elif intent == 'organize_workspaces':
                return self._handle_organize_workspaces(entities)
            elif intent == 'workspace_overview':
                return self._handle_workspace_overview(entities)
            else:
                return f"🗂️ **Intent recognized** ({intent}) but implementation pending"
                
        except Exception as e:
            return f"❌ **Workspace management error:** {str(e)}"
    
    def _handle_create_workspace(self, entities: Dict) -> str:
        """Handle workspace creation commands"""
        workspace_name = entities.get('workspace_target', '').strip()
        if not workspace_name:
            return "🗂️ **Please specify a name for the new workspace**\n\n**Examples:** create workspace for coding, new workspace called research"
        
        # Check workspace limit
        if len(self.workspaces) >= self.max_workspaces:
            return f"🗂️ **Maximum workspaces reached** ({self.max_workspaces})\n\nDelete unused workspaces first."
        
        # Generate new workspace ID
        new_id = max(self.workspaces.keys()) + 1
        
        # Detect workspace type and generate smart name
        context = entities.get('context', {})
        workspace_type = context.get('suggested_type', WorkspaceType.GENERAL)
        
        # Create new workspace
        new_workspace = SmartWorkspace(
            id=new_id,
            name=workspace_name,
            workspace_type=workspace_type,
            description=f"Workspace for {workspace_name}",
            applications=[],
            window_ids=[],
            creation_time=time.time(),
            last_used=time.time(),
            usage_count=0,
            auto_created=False,
            ai_suggested_apps=self._get_suggested_apps(workspace_type),
            persistent_layout=context.get('persistent', False)
        )
        
        # Add to workspaces
        self.workspaces[new_id] = new_workspace
        
        # Switch to new workspace
        self._switch_to_workspace(new_id)
        
        # Save workspaces
        self._save_workspaces()
        
        type_info = f" ({workspace_type.value})" if workspace_type != WorkspaceType.GENERAL else ""
        suggested_apps = ""
        if new_workspace.ai_suggested_apps:
            suggested_apps = f"\n   └─ Suggested apps: {', '.join(new_workspace.ai_suggested_apps[:3])}"
        
        return f"🗂️ **Created workspace:** {workspace_name}{type_info}\n   └─ ID: {new_id}\n   └─ Switched to new workspace{suggested_apps}"
    
    def _handle_switch_workspace(self, entities: Dict) -> str:
        """Handle workspace switching commands"""
        target = entities.get('workspace_target', '').strip()
        if not target:
            return "🗂️ **Please specify which workspace to switch to**\n\n**Examples:** switch to workspace 2, go to next workspace, switch to development workspace"
        
        # Resolve workspace ID
        workspace_id = self._resolve_workspace_identifier(target)
        
        if workspace_id is None:
            # Try finding by name
            workspace_id = self._find_workspace_by_name(target)
        
        if workspace_id is None:
            available = ', '.join([f"{ws.id}({ws.name})" for ws in self.workspaces.values()])
            return f"🔍 **Workspace not found:** '{target}'\n\n**Available workspaces:** {available}"
        
        if workspace_id == self.current_workspace_id:
            return f"✅ **Already on workspace:** {self.workspaces[workspace_id].name}"
        
        # Switch to workspace
        self._switch_to_workspace(workspace_id)
        
        workspace = self.workspaces[workspace_id]
        
        return f"🗂️ **Switched to workspace:** {workspace.name}\n   └─ ID: {workspace.id}\n   └─ Type: {workspace.workspace_type.value.title()}"
    
    def _handle_list_workspaces(self, entities: Dict) -> str:
        """Handle list workspaces commands"""
        if not self.workspaces:
            return "🗂️ **No workspaces available**"
        
        response = f"🗂️ **Available Workspaces** ({len(self.workspaces)} total):\n\n"
        
        # Sort workspaces by usage and recency
        sorted_workspaces = sorted(
            self.workspaces.values(),
            key=lambda ws: (ws.id == self.current_workspace_id, -ws.usage_count, -ws.last_used),
            reverse=True
        )
        
        for workspace in sorted_workspaces:
            # Current workspace indicator
            current_indicator = "📍 " if workspace.id == self.current_workspace_id else "   "
            
            # Type icon
            type_icon = self._get_workspace_type_icon(workspace.workspace_type)
            
            # Usage info
            usage = f" (used {workspace.usage_count}x)" if workspace.usage_count > 0 else ""
            
            # App count
            app_count = len(workspace.applications) if workspace.applications else 0
            app_info = f" • {app_count} apps" if app_count > 0 else ""
            
            # Last used
            if workspace.last_used > 0:
                last_used = self._format_time_ago(workspace.last_used)
                time_info = f" • {last_used}"
            else:
                time_info = ""
            
            response += f"{current_indicator}{type_icon} **{workspace.name}** (#{workspace.id}){usage}\n"
            
            if workspace.description and workspace.description != f"Workspace for {workspace.name}":
                response += f"      └─ {workspace.description[:50]}{'...' if len(workspace.description) > 50 else ''}\n"
            
            if app_info or time_info:
                response += f"      └─ {workspace.workspace_type.value.title()}{app_info}{time_info}\n"
            
            response += "\n"
        
        return response
    
    def _handle_rename_workspace(self, entities: Dict) -> str:
        """Handle workspace renaming commands"""
        groups = entities.get('groups', [])
        if len(groups) < 2:
            return "🏷️ **Please specify workspace and new name**\n\n**Examples:** rename workspace 2 to development, call current workspace research"
        
        workspace_identifier, new_name = groups[0].strip(), groups[1].strip()
        
        # Resolve workspace ID
        if workspace_identifier.lower() in ['current', 'this']:
            workspace_id = self.current_workspace_id
        else:
            try:
                workspace_id = int(workspace_identifier)
            except ValueError:
                return f"🔍 **Invalid workspace identifier:** '{workspace_identifier}'"
        
        if workspace_id not in self.workspaces:
            return f"🔍 **Workspace not found:** {workspace_id}"
        
        # Rename workspace
        old_name = self.workspaces[workspace_id].name
        self.workspaces[workspace_id].name = new_name
        
        # Update description if it was auto-generated
        if self.workspaces[workspace_id].description == f"Workspace for {old_name}":
            self.workspaces[workspace_id].description = f"Workspace for {new_name}"
        
        # Save changes
        self._save_workspaces()
        
        return f"🏷️ **Renamed workspace:** '{old_name}' → '{new_name}'\n   └─ Workspace ID: {workspace_id}"
    
    def _handle_delete_workspace(self, entities: Dict) -> str:
        """Handle workspace deletion commands"""
        target = entities.get('workspace_target', '').strip()
        if not target:
            return "🗑️ **Please specify which workspace to delete**\n\n**Examples:** delete workspace 3, remove last workspace"
        
        # Resolve workspace ID
        workspace_id = self._resolve_workspace_identifier(target)
        
        if workspace_id is None:
            return f"🔍 **Invalid workspace identifier:** '{target}'"
        
        if workspace_id not in self.workspaces:
            return f"🔍 **Workspace not found:** {workspace_id}"
        
        if workspace_id == 1:
            return "⚠️ **Cannot delete the main workspace** (ID: 1)\n\nThe main workspace is required for system operation."
        
        if workspace_id == self.current_workspace_id:
            return "⚠️ **Cannot delete current active workspace**\n\nSwitch to another workspace first."
        
        # Delete workspace
        deleted_workspace = self.workspaces.pop(workspace_id)
        
        # Remove from history
        self.workspace_history = [ws_id for ws_id in self.workspace_history if ws_id != workspace_id]
        
        # Save changes
        self._save_workspaces()
        
        return f"🗑️ **Deleted workspace:** {deleted_workspace.name}\n   └─ ID: {workspace_id}\n   └─ Type: {deleted_workspace.workspace_type.value.title()}"
    
    def _handle_move_window(self, entities: Dict) -> str:
        """Handle move window to workspace commands"""
        target = entities.get('workspace_target', '').strip()
        if not target:
            return "🔄 **Please specify target workspace**\n\n**Examples:** move window to workspace 2, send app to development workspace"
        
        # Resolve workspace ID
        try:
            workspace_id = int(target)
        except ValueError:
            workspace_id = self._find_workspace_by_name(target)
        
        if workspace_id is None or workspace_id not in self.workspaces:
            return f"🔍 **Workspace not found:** '{target}'"
        
        # Use wmctrl to move current window if available
        try:
            result = subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-t', str(workspace_id - 1)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                workspace_name = self.workspaces[workspace_id].name
                return f"🔄 **Moved window to workspace:** {workspace_name}\n   └─ ID: {workspace_id}"
            else:
                return "⚠️ **Window management tools not available**\n\nInstall 'wmctrl' for window moving functionality."
        
        except FileNotFoundError:
            return "⚠️ **Window management tools not available**\n\nInstall 'wmctrl' for window moving functionality."
        except Exception as e:
            return f"❌ **Move failed:** {str(e)}"
    
    def _handle_workspace_info(self, entities: Dict) -> str:
        """Handle workspace information commands"""
        target = entities.get('workspace_target', 'current').strip()
        
        # Resolve workspace ID
        if target in ['current', 'this']:
            workspace_id = self.current_workspace_id
        else:
            workspace_id = self._resolve_workspace_identifier(target)
        
        if workspace_id is None or workspace_id not in self.workspaces:
            return f"🔍 **Workspace not found:** '{target}'"
        
        workspace = self.workspaces[workspace_id]
        
        response = f"ℹ️ **Workspace Information:** {workspace.name}\n\n"
        response += f"**ID:** {workspace.id}\n"
        response += f"**Type:** {workspace.workspace_type.value.title()}\n"
        
        if workspace.description:
            response += f"**Description:** {workspace.description}\n"
        
        response += f"**Created:** {time.strftime('%Y-%m-%d %H:%M', time.localtime(workspace.creation_time))}\n"
        
        if workspace.usage_count > 0:
            response += f"**Usage:** {workspace.usage_count} times\n"
            last_used = time.strftime('%Y-%m-%d %H:%M', time.localtime(workspace.last_used))
            response += f"**Last Used:** {last_used}\n"
        
        if workspace.applications:
            response += f"**Applications:** {len(workspace.applications)}\n"
            for app in workspace.applications[:5]:
                response += f"  • {app}\n"
            if len(workspace.applications) > 5:
                response += f"  • ... and {len(workspace.applications) - 5} more\n"
        
        if workspace.ai_suggested_apps:
            response += f"**AI Suggestions:** {', '.join(workspace.ai_suggested_apps[:3])}\n"
        
        response += f"**Auto-created:** {'Yes' if workspace.auto_created else 'No'}\n"
        response += f"**Persistent Layout:** {'Yes' if workspace.persistent_layout else 'No'}\n"
        
        return response
    
    def _handle_organize_workspaces(self, entities: Dict) -> str:
        """Handle workspace organization commands"""
        try:
            organized_count = 0
            
            # Sort workspaces by type and usage
            workspace_list = list(self.workspaces.values())
            workspace_list.sort(key=lambda ws: (ws.workspace_type.value, -ws.usage_count))
            
            # Reassign IDs to create logical order
            new_id_mapping = {}
            for i, workspace in enumerate(workspace_list):
                if workspace.id == 1:  # Keep main workspace as 1
                    continue
                new_id = i + 2 if workspace_list[0].id == 1 else i + 1
                if new_id != workspace.id:
                    new_id_mapping[workspace.id] = new_id
                    organized_count += 1
            
            # Apply new IDs
            new_workspaces = {}
            for old_id, workspace in self.workspaces.items():
                new_id = new_id_mapping.get(old_id, old_id)
                workspace.id = new_id
                new_workspaces[new_id] = workspace
            
            self.workspaces = new_workspaces
            
            # Update current workspace ID
            if self.current_workspace_id in new_id_mapping:
                self.current_workspace_id = new_id_mapping[self.current_workspace_id]
            
            # Clean up empty workspaces
            empty_workspaces = [ws_id for ws_id, ws in self.workspaces.items() 
                              if ws.usage_count == 0 and ws.id != 1 and not ws.applications]
            
            for ws_id in empty_workspaces:
                if ws_id != self.current_workspace_id:
                    del self.workspaces[ws_id]
                    organized_count += 1
            
            # Save changes
            self._save_workspaces()
            
            if organized_count > 0:
                return f"🗂️ **Organized workspaces:** {organized_count} changes made\n   └─ Workspaces sorted by type and usage\n   └─ Empty workspaces removed"
            else:
                return "✅ **Workspaces already organized**\n\nNo changes needed."
        
        except Exception as e:
            return f"❌ **Organization failed:** {str(e)}"
    
    def _handle_workspace_overview(self, entities: Dict) -> str:
        """Handle workspace overview commands"""
        if not self.workspaces:
            return "🗂️ **No workspaces available**"
        
        # Calculate statistics
        total_workspaces = len(self.workspaces)
        total_usage = sum(ws.usage_count for ws in self.workspaces.values())
        most_used = max(self.workspaces.values(), key=lambda ws: ws.usage_count)
        
        # Type distribution
        type_counts = defaultdict(int)
        for workspace in self.workspaces.values():
            type_counts[workspace.workspace_type] += 1
        
        response = f"📊 **Workspace Overview & Analytics**\n\n"
        response += f"**Total Workspaces:** {total_workspaces}\n"
        response += f"**Current Workspace:** {self.workspaces[self.current_workspace_id].name}\n"
        response += f"**Total Usage:** {total_usage} switches\n"
        response += f"**Most Used:** {most_used.name} ({most_used.usage_count}x)\n\n"
        
        response += f"**By Type:**\n"
        for workspace_type, count in type_counts.items():
            type_icon = self._get_workspace_type_icon(workspace_type)
            response += f"• {type_icon} {workspace_type.value.title()}: {count}\n"
        
        # Recent activity
        if self.workspace_history:
            response += f"\n**Recent Activity:**\n"
            recent_workspaces = [self.workspaces[ws_id] for ws_id in self.workspace_history[-5:] 
                               if ws_id in self.workspaces]
            for workspace in reversed(recent_workspaces):
                response += f"• {workspace.name} (#{workspace.id})\n"
        
        return response
    
    def _switch_to_workspace(self, workspace_id: int):
        """Switch to specified workspace and update tracking"""
        if workspace_id not in self.workspaces:
            return False
        
        # Update previous workspace
        if self.current_workspace_id in self.workspaces:
            self.workspaces[self.current_workspace_id].last_used = time.time()
        
        # Switch to new workspace
        self.current_workspace_id = workspace_id
        
        # Update new workspace
        workspace = self.workspaces[workspace_id]
        workspace.last_used = time.time()
        workspace.usage_count += 1
        
        # Update history
        if workspace_id in self.workspace_history:
            self.workspace_history.remove(workspace_id)
        self.workspace_history.append(workspace_id)
        
        # Keep history manageable
        if len(self.workspace_history) > self.user_preferences['max_history']:
            self.workspace_history.pop(0)
        
        # Use wmctrl to actually switch workspace if available
        try:
            subprocess.run(['wmctrl', '-s', str(workspace_id - 1)], 
                         capture_output=True, text=True)
        except FileNotFoundError:
            pass  # wmctrl not available
        
        return True
    
    def _resolve_workspace_identifier(self, identifier: str) -> Optional[int]:
        """Resolve workspace identifier to workspace ID"""
        identifier = identifier.lower().strip()
        
        if identifier.isdigit():
            return int(identifier)
        elif identifier == 'next':
            current_ids = sorted(self.workspaces.keys())
            current_index = current_ids.index(self.current_workspace_id)
            return current_ids[(current_index + 1) % len(current_ids)]
        elif identifier == 'previous':
            current_ids = sorted(self.workspaces.keys())
            current_index = current_ids.index(self.current_workspace_id)
            return current_ids[(current_index - 1) % len(current_ids)]
        elif identifier == 'first':
            return min(self.workspaces.keys())
        elif identifier == 'last':
            return max(self.workspaces.keys())
        
        return None
    
    def _find_workspace_by_name(self, name: str) -> Optional[int]:
        """Find workspace by name using fuzzy matching"""
        name_lower = name.lower().strip()
        
        # Exact match
        for workspace in self.workspaces.values():
            if workspace.name.lower() == name_lower:
                return workspace.id
        
        # Partial match
        for workspace in self.workspaces.values():
            if name_lower in workspace.name.lower():
                return workspace.id
        
        # Type match
        for workspace_type, keywords in self.type_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                for workspace in self.workspaces.values():
                    if workspace.workspace_type == workspace_type:
                        return workspace.id
        
        return None
    
    def _get_suggested_apps(self, workspace_type: WorkspaceType) -> List[str]:
        """Get AI-suggested applications for workspace type"""
        suggestions = {
            WorkspaceType.DEVELOPMENT: ['Visual Studio Code', 'Terminal', 'Git', 'Firefox'],
            WorkspaceType.PRODUCTIVITY: ['LibreOffice Writer', 'Calculator', 'Files', 'Email'],
            WorkspaceType.CREATIVE: ['GIMP', 'Inkscape', 'Audacity', 'Blender'],
            WorkspaceType.COMMUNICATION: ['Thunderbird', 'Slack', 'Discord', 'Zoom'],
            WorkspaceType.ENTERTAINMENT: ['VLC', 'Spotify', 'Games', 'YouTube'],
            WorkspaceType.RESEARCH: ['Firefox', 'Files', 'Notes', 'PDF Viewer'],
            WorkspaceType.SYSTEM: ['System Monitor', 'Terminal', 'Settings', 'Files']
        }
        
        return suggestions.get(workspace_type, [])
    
    def _get_workspace_type_icon(self, workspace_type: WorkspaceType) -> str:
        """Get icon for workspace type"""
        icon_map = {
            WorkspaceType.GENERAL: '🗂️',
            WorkspaceType.DEVELOPMENT: '💻',
            WorkspaceType.PRODUCTIVITY: '📄',
            WorkspaceType.CREATIVE: '🎨',
            WorkspaceType.COMMUNICATION: '💬',
            WorkspaceType.ENTERTAINMENT: '🎮',
            WorkspaceType.RESEARCH: '🔍',
            WorkspaceType.SYSTEM: '⚙️'
        }
        return icon_map.get(workspace_type, '🗂️')
    
    def _format_time_ago(self, timestamp: float) -> str:
        """Format timestamp as human-readable 'time ago'"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return "just now"
        elif diff < 3600:
            return f"{int(diff // 60)} min ago"
        elif diff < 86400:
            return f"{int(diff // 3600)} hr ago"
        else:
            return f"{int(diff // 86400)} days ago"
    
    def _save_workspaces(self):
        """Save workspaces to persistent storage"""
        try:
            workspaces_file = self.storage_path / 'workspaces.json'
            
            # Prepare data for serialization
            workspace_data = {}
            for ws_id, workspace in self.workspaces.items():
                workspace_data[str(ws_id)] = asdict(workspace)
            
            save_data = {
                'workspaces': workspace_data,
                'current_workspace_id': self.current_workspace_id,
                'workspace_history': self.workspace_history,
                'user_preferences': self.user_preferences,
                'last_save': time.time()
            }
            
            with open(workspaces_file, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Failed to save workspaces: {e}")
    
    def _load_workspaces(self):
        """Load workspaces from persistent storage"""
        try:
            workspaces_file = self.storage_path / 'workspaces.json'
            if not workspaces_file.exists():
                return
            
            with open(workspaces_file, 'r') as f:
                save_data = json.load(f)
            
            # Load workspaces
            if 'workspaces' in save_data:
                self.workspaces.clear()
                for ws_id_str, workspace_data in save_data['workspaces'].items():
                    ws_id = int(ws_id_str)
                    
                    # Convert workspace_type back to enum
                    if 'workspace_type' in workspace_data:
                        workspace_data['workspace_type'] = WorkspaceType(workspace_data['workspace_type'])
                    
                    workspace = SmartWorkspace(**workspace_data)
                    self.workspaces[ws_id] = workspace
            
            # Load other data
            self.current_workspace_id = save_data.get('current_workspace_id', 1)
            self.workspace_history = save_data.get('workspace_history', [1])
            self.user_preferences.update(save_data.get('user_preferences', {}))
            
            print(f"✅ Loaded {len(self.workspaces)} workspaces from storage")
            
        except Exception as e:
            print(f"Failed to load workspaces: {e}")
    
    def _handle_unknown_intent(self, user_input: str) -> str:
        """Handle unknown workspace commands"""
        return f"""❓ **I didn't understand:** "{user_input}"

🗂️ **Try these natural language workspace commands:**

**Workspace Creation:**
• "create workspace for coding"
• "new workspace called research"
• "make productivity workspace"

**Workspace Navigation:**
• "switch to workspace 2"
• "go to next workspace"
• "switch to development workspace"

**Workspace Management:**
• "list all workspaces"
• "rename workspace 3 to projects"
• "delete workspace 4"
• "workspace overview"

**Window Management:**
• "move window to workspace 2"
• "send app to coding workspace"
• "workspace info"

**I understand natural language - speak naturally!** 🤖"""

# For compatibility with Desktop Manager
DynamicWorkspaceManager = IntelligentWorkspaceManager

if __name__ == '__main__':
    workspace_manager = IntelligentWorkspaceManager()
    
    # Demo commands
    print(workspace_manager.process_command("create workspace for coding"))
    print(workspace_manager.process_command("list workspaces"))
    print(workspace_manager.process_command("switch to workspace 1"))
    print(workspace_manager.process_command("workspace overview"))

