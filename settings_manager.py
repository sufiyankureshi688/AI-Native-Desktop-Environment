#!/usr/bin/env python3
"""
PersonalAIOS Intelligent Settings Manager
Revolutionary AI-native settings and configuration management with perfect natural language understanding
Unified control center for all PersonalAIOS components and system settings
"""
import gi
import re
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import configparser
import logging

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Gio, Adw

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SettingsManager')

class SettingType(Enum):
    """Setting data types"""
    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    LIST = "list"
    CHOICE = "choice"
    COLOR = "color"
    FILE = "file"
    DIRECTORY = "directory"

class SettingCategory(Enum):
    """Setting categories"""
    APPEARANCE = "appearance"
    SYSTEM = "system"
    PRIVACY = "privacy"
    ACCESSIBILITY = "accessibility"
    APPLICATIONS = "applications"
    NETWORK = "network"
    POWER = "power"
    SOUND = "sound"
    DISPLAY = "display"
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    PERSONALAIOS = "personalaios"

class SettingPriority(Enum):
    """Setting importance levels"""
    ESSENTIAL = "essential"      # Core functionality
    IMPORTANT = "important"      # User experience
    NORMAL = "normal"           # Customization
    ADVANCED = "advanced"       # Power users
    DEBUG = "debug"            # Development

@dataclass
class SettingDefinition:
    """Comprehensive setting definition"""
    id: str
    category: SettingCategory
    name: str
    description: str
    setting_type: SettingType
    default_value: Any
    current_value: Any = None
    priority: SettingPriority = SettingPriority.NORMAL
    choices: Optional[List] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    requires_restart: bool = False
    component: Optional[str] = None
    validation_pattern: Optional[str] = None
    help_text: Optional[str] = None
    keywords: List[str] = None
    last_modified: float = 0
    modified_by: str = "system"

class IntelligentSettingsManager:
    """
    Revolutionary AI-Native Settings Manager
    
    Features:
    - Perfect natural language settings control
    - Intelligent setting discovery and categorization
    - Context-aware setting recommendations
    - Dynamic setting validation and constraints
    - Component-specific settings management
    - Usage pattern learning and optimization
    - Backup and restore functionality
    - Advanced search and filtering
    """
    
    def __init__(self):
        """Initialize the intelligent settings manager"""
        self.settings: Dict[str, SettingDefinition] = {}
        self.setting_categories: Dict[SettingCategory, List[str]] = {}
        self.command_history: List[Dict] = []
        self.backup_history: List[Dict] = []
        
        # Component references for dynamic settings
        self.components = {}
        
        # AI-powered intent patterns for natural language understanding
        self.intent_patterns = {
            'get_setting': [
                r'(?:what is|show|get) (?:the )?(?:current )?(.+?) (?:setting|value|preference)',
                r'(?:current|show me) (.+?) (?:setting|value)',
                r'(?:value of|check) (.+?) (?:setting|preference)',
                r'(.+?) (?:setting|preference|value)',
            ],
            'set_setting': [
                r'(?:set|change) (?:the )?(.+?) (?:to|as) (.+)',
                r'(?:make|configure) (?:the )?(.+?) (?:to be|as) (.+)',
                r'(?:update|modify) (?:the )?(.+?) (?:setting|value) (?:to|as) (.+)',
                r'(.+?) (?:should be|to) (.+)',
            ],
            'reset_setting': [
                r'(?:reset|restore) (?:the )?(.+?) (?:setting|preference|value)',
                r'(?:default|original) (?:value for |setting for )?(.+)',
                r'(?:set|change) (.+?) (?:back to|to) (?:default|original)',
            ],
            'list_settings': [
                r'(?:list|show) (?:all )?(?:the )?(.+?) settings',
                r'(?:what|which) (.+?) settings (?:are there|exist|available)',
                r'(?:settings for|configure) (.+?)',
                r'(.+?) (?:configuration|preferences|options)',
            ],
            'search_settings': [
                r'(?:find|search|locate) (?:settings (?:for|about) )?(.+)',
                r'(?:settings|options) (?:related to|about|for) (.+)',
                r'(?:how to (?:change|configure|set)) (.+)',
            ],
            'backup_settings': [
                r'(?:backup|save|export) (?:all )?(?:my )?settings',
                r'(?:create|make) (?:a )?(?:backup|copy) of (?:my )?settings',
                r'(?:save|store) (?:current )?configuration',
            ],
            'restore_settings': [
                r'(?:restore|load|import) (?:settings|configuration|backup)',
                r'(?:revert to|go back to) (?:previous|saved|backup) settings',
                r'(?:undo|rollback) (?:settings )?changes',
            ],
            'category_settings': [
                r'(?:show|list|display) (.+?) category settings',
                r'(?:all )?(.+?) (?:settings|preferences|options)',
                r'(?:configure|modify) (.+?) (?:settings|preferences)',
            ],
            'setting_info': [
                r'(?:info|information|details|help) (?:about|for) (.+?) (?:setting|preference)',
                r'(?:what does|explain) (.+?) (?:setting|preference|option)',
                r'(?:help with|describe) (.+?) (?:setting|preference)',
            ],
            'apply_profile': [
                r'(?:apply|use|load) (.+?) (?:profile|preset|template)',
                r'(?:set|configure) (?:system )?(?:as|to) (.+?) (?:profile|mode)',
                r'(?:switch to|enable) (.+?) (?:profile|mode|preset)',
            ]
        }
        
        # Setting search keywords and aliases
        self.setting_aliases = {
            'theme': ['appearance', 'look', 'style', 'colors'],
            'wallpaper': ['background', 'desktop background'],
            'volume': ['sound', 'audio', 'speaker'],
            'brightness': ['screen brightness', 'display brightness'],
            'wifi': ['wireless', 'internet', 'network'],
            'battery': ['power', 'energy', 'charging'],
            'keyboard': ['keys', 'typing', 'shortcuts'],
            'mouse': ['pointer', 'cursor', 'clicking'],
            'notifications': ['alerts', 'popups', 'messages'],
            'privacy': ['security', 'tracking', 'data'],
            'accessibility': ['a11y', 'disability', 'assistance']
        }
        
        # Initialize core settings
        self._initialize_core_settings()
        
        # Setup storage
        self.settings_path = Path.home() / '.personalaios' / 'settings'
        self.settings_path.mkdir(parents=True, exist_ok=True)
        
        # Load saved settings
        self._load_settings()
        
        print("⚙️ Intelligent Settings Manager initialized with AI-powered configuration management")
    
    def _initialize_core_settings(self):
        """Initialize core PersonalAIOS settings"""
        
        # === APPEARANCE SETTINGS ===
        self._add_setting(SettingDefinition(
            id='theme_mode',
            category=SettingCategory.APPEARANCE,
            name='Theme Mode',
            description='System color theme preference',
            setting_type=SettingType.CHOICE,
            choices=['auto', 'light', 'dark'],
            default_value='auto',
            priority=SettingPriority.IMPORTANT,
            keywords=['theme', 'appearance', 'dark mode', 'light mode']
        ))
        
        self._add_setting(SettingDefinition(
            id='accent_color',
            category=SettingCategory.APPEARANCE,
            name='Accent Color',
            description='Primary accent color for the interface',
            setting_type=SettingType.COLOR,
            default_value='#1c71d8',
            priority=SettingPriority.NORMAL,
            keywords=['color', 'accent', 'theme']
        ))
        
        self._add_setting(SettingDefinition(
            id='wallpaper_path',
            category=SettingCategory.APPEARANCE,
            name='Wallpaper',
            description='Desktop background image',
            setting_type=SettingType.FILE,
            default_value=str(Path.home() / '.personalaios/wallpapers/default.jpg'),
            priority=SettingPriority.NORMAL,
            keywords=['wallpaper', 'background', 'desktop']
        ))
        
        self._add_setting(SettingDefinition(
            id='font_size',
            category=SettingCategory.APPEARANCE,
            name='Font Size',
            description='System font size scaling',
            setting_type=SettingType.FLOAT,
            default_value=1.0,
            min_value=0.5,
            max_value=3.0,
            priority=SettingPriority.IMPORTANT,
            keywords=['font', 'text', 'size', 'scaling']
        ))
        
        # === PERSONALAIOS SETTINGS ===
        self._add_setting(SettingDefinition(
            id='ai_natural_language',
            category=SettingCategory.PERSONALAIOS,
            name='Natural Language Processing',
            description='Enable AI-powered natural language understanding',
            setting_type=SettingType.BOOLEAN,
            default_value=True,
            priority=SettingPriority.ESSENTIAL,
            keywords=['ai', 'nlp', 'natural language', 'understanding']
        ))
        
        self._add_setting(SettingDefinition(
            id='ai_learning_enabled',
            category=SettingCategory.PERSONALAIOS,
            name='AI Learning',
            description='Allow PersonalAIOS to learn from your usage patterns',
            setting_type=SettingType.BOOLEAN,
            default_value=True,
            priority=SettingPriority.IMPORTANT,
            keywords=['learning', 'ai', 'patterns', 'adaptation']
        ))
        
        self._add_setting(SettingDefinition(
            id='ai_suggestions',
            category=SettingCategory.PERSONALAIOS,
            name='AI Suggestions',
            description='Show intelligent suggestions and recommendations',
            setting_type=SettingType.BOOLEAN,
            default_value=True,
            priority=SettingPriority.NORMAL,
            keywords=['suggestions', 'recommendations', 'ai']
        ))
        
        self._add_setting(SettingDefinition(
            id='desktop_mode_default',
            category=SettingCategory.PERSONALAIOS,
            name='Default Desktop Mode',
            description='Start PersonalAIOS in desktop mode by default',
            setting_type=SettingType.BOOLEAN,
            default_value=True,
            priority=SettingPriority.IMPORTANT,
            requires_restart=True,
            keywords=['desktop', 'mode', 'startup']
        ))
        
        # === SYSTEM SETTINGS ===
        self._add_setting(SettingDefinition(
            id='animation_speed',
            category=SettingCategory.SYSTEM,
            name='Animation Speed',
            description='Speed of UI animations and transitions',
            setting_type=SettingType.CHOICE,
            choices=['none', 'fast', 'normal', 'slow'],
            default_value='normal',
            priority=SettingPriority.NORMAL,
            keywords=['animation', 'speed', 'transitions']
        ))
        
        self._add_setting(SettingDefinition(
            id='auto_save_frequency',
            category=SettingCategory.SYSTEM,
            name='Auto Save Frequency',
            description='Frequency of automatic settings backup (minutes)',
            setting_type=SettingType.INTEGER,
            default_value=30,
            min_value=5,
            max_value=480,
            priority=SettingPriority.NORMAL,
            keywords=['autosave', 'backup', 'frequency']
        ))
        
        # === PRIVACY SETTINGS ===
        self._add_setting(SettingDefinition(
            id='usage_statistics',
            category=SettingCategory.PRIVACY,
            name='Usage Statistics',
            description='Collect anonymous usage statistics for improvement',
            setting_type=SettingType.BOOLEAN,
            default_value=False,
            priority=SettingPriority.IMPORTANT,
            keywords=['statistics', 'telemetry', 'privacy', 'data']
        ))
        
        self._add_setting(SettingDefinition(
            id='location_services',
            category=SettingCategory.PRIVACY,
            name='Location Services',
            description='Allow applications to access location data',
            setting_type=SettingType.BOOLEAN,
            default_value=False,
            priority=SettingPriority.IMPORTANT,
            keywords=['location', 'gps', 'privacy']
        ))
        
        # === ACCESSIBILITY SETTINGS ===
        self._add_setting(SettingDefinition(
            id='large_text',
            category=SettingCategory.ACCESSIBILITY,
            name='Large Text',
            description='Use larger text for better readability',
            setting_type=SettingType.BOOLEAN,
            default_value=False,
            priority=SettingPriority.IMPORTANT,
            keywords=['accessibility', 'large text', 'readability']
        ))
        
        self._add_setting(SettingDefinition(
            id='high_contrast',
            category=SettingCategory.ACCESSIBILITY,
            name='High Contrast',
            description='Use high contrast theme for better visibility',
            setting_type=SettingType.BOOLEAN,
            default_value=False,
            priority=SettingPriority.IMPORTANT,
            keywords=['accessibility', 'high contrast', 'visibility']
        ))
        
        # === SOUND SETTINGS ===
        self._add_setting(SettingDefinition(
            id='system_sounds',
            category=SettingCategory.SOUND,
            name='System Sounds',
            description='Enable system sound effects',
            setting_type=SettingType.BOOLEAN,
            default_value=True,
            priority=SettingPriority.NORMAL,
            keywords=['sounds', 'audio', 'effects']
        ))
        
        self._add_setting(SettingDefinition(
            id='notification_sounds',
            category=SettingCategory.SOUND,
            name='Notification Sounds',
            description='Play sounds for notifications',
            setting_type=SettingType.BOOLEAN,
            default_value=True,
            priority=SettingPriority.NORMAL,
            keywords=['notifications', 'sounds', 'alerts']
        ))
        
        logger.info(f"Initialized {len(self.settings)} core settings across {len(set(s.category for s in self.settings.values()))} categories")
    
    def _add_setting(self, setting: SettingDefinition):
        """Add a setting to the manager"""
        if setting.current_value is None:
            setting.current_value = setting.default_value
        
        self.settings[setting.id] = setting
        
        # Add to category index
        if setting.category not in self.setting_categories:
            self.setting_categories[setting.category] = []
        self.setting_categories[setting.category].append(setting.id)
    
    def register_component(self, component_name: str, component_instance):
        """Register a component for dynamic settings access"""
        self.components[component_name] = component_instance
        logger.info(f"Registered component: {component_name}")
    
    def process_command(self, user_input: str) -> str:
        """Process natural language settings management commands"""
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
        return self._execute_settings_intent(intent, entities, user_input)
    
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
                        'setting_target': self._determine_setting_target(match.groups(), text)
                    }
                    return intent, entities
        
        return None, {}
    
    def _extract_context(self, text: str) -> Dict:
        """Extract contextual information from text"""
        context = {}
        
        # Detect urgency
        if any(word in text for word in ['urgent', 'now', 'immediately', 'asap']):
            context['urgency'] = 'high'
        
        # Detect scope
        if any(word in text for word in ['all', 'everything', 'global']):
            context['scope'] = 'global'
        elif any(word in text for word in ['current', 'this', 'local']):
            context['scope'] = 'local'
        
        # Detect backup/restore context
        if any(word in text for word in ['backup', 'save', 'store']):
            context['action_type'] = 'backup'
        elif any(word in text for word in ['restore', 'load', 'revert']):
            context['action_type'] = 'restore'
        
        return context
    
    def _determine_setting_target(self, groups: Tuple, text: str) -> Optional[str]:
        """Determine setting target from command groups"""
        if groups and groups[0]:
            return groups[0].strip()
        return None
    
    def _execute_settings_intent(self, intent: str, entities: Dict, original_text: str) -> str:
        """Execute the identified settings intent"""
        try:
            if intent == 'get_setting':
                return self._handle_get_setting(entities)
            elif intent == 'set_setting':
                return self._handle_set_setting(entities)
            elif intent == 'reset_setting':
                return self._handle_reset_setting(entities)
            elif intent == 'list_settings':
                return self._handle_list_settings(entities)
            elif intent == 'search_settings':
                return self._handle_search_settings(entities)
            elif intent == 'backup_settings':
                return self._handle_backup_settings(entities)
            elif intent == 'restore_settings':
                return self._handle_restore_settings(entities)
            elif intent == 'category_settings':
                return self._handle_category_settings(entities)
            elif intent == 'setting_info':
                return self._handle_setting_info(entities)
            elif intent == 'apply_profile':
                return self._handle_apply_profile(entities)
            else:
                return f"⚙️ **Intent recognized** ({intent}) but implementation pending"
                
        except Exception as e:
            return f"❌ **Settings management error:** {str(e)}"
    
    def _handle_get_setting(self, entities: Dict) -> str:
        """Handle get setting value commands"""
        target = entities.get('setting_target', '').strip()
        if not target:
            return "⚙️ **Please specify which setting to check**\n\n**Examples:** theme setting, current wallpaper, AI learning setting"
        
        # Find matching setting
        setting = self._find_setting_by_name(target)
        
        if not setting:
            # Search for similar settings
            similar = self._search_similar_settings(target)
            response = f"🔍 **Setting not found:** '{target}'"
            if similar:
                response += "\n\n**Did you mean:**\n"
                for s in similar[:3]:
                    response += f"• {s.name} ({s.category.value})\n"
            return response
        
        # Format setting value
        value_str = self._format_setting_value(setting)
        
        response = f"⚙️ **{setting.name}:** {value_str}\n"
        response += f"   └─ Category: {setting.category.value.title()}\n"
        response += f"   └─ Description: {setting.description}\n"
        
        if setting.last_modified > 0:
            modified_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(setting.last_modified))
            response += f"   └─ Last modified: {modified_time} by {setting.modified_by}\n"
        
        if setting.requires_restart:
            response += f"   └─ ⚠️ Requires restart to take effect\n"
        
        return response
    
    def _handle_set_setting(self, entities: Dict) -> str:
        """Handle set setting value commands"""
        groups = entities.get('groups', [])
        if len(groups) < 2:
            return "⚙️ **Please specify setting name and value**\n\n**Examples:** set theme to dark, change volume to 75%, make AI learning true"
        
        setting_name, new_value = groups[0].strip(), groups[1].strip()
        
        # Find setting
        setting = self._find_setting_by_name(setting_name)
        if not setting:
            return f"🔍 **Setting not found:** '{setting_name}'"
        
        # Validate and convert value
        try:
            validated_value = self._validate_and_convert_value(setting, new_value)
        except ValueError as e:
            return f"❌ **Invalid value:** {str(e)}"
        
        # Store old value for rollback
        old_value = setting.current_value
        
        # Update setting
        setting.current_value = validated_value
        setting.last_modified = time.time()
        setting.modified_by = "user"
        
        # Apply setting if component is available
        self._apply_setting_to_component(setting)
        
        # Save settings
        self._save_settings()
        
        response = f"✅ **Updated {setting.name}:** {self._format_setting_value(setting)}\n"
        
        if old_value != validated_value:
            old_value_str = self._format_value_by_type(setting.setting_type, old_value)
            response += f"   └─ Previous value: {old_value_str}\n"
        
        if setting.requires_restart:
            response += f"   └─ ⚠️ Restart required to apply changes\n"
        
        return response
    
    def _handle_reset_setting(self, entities: Dict) -> str:
        """Handle reset setting to default commands"""
        target = entities.get('setting_target', '').strip()
        if not target:
            return "🔄 **Please specify which setting to reset**\n\n**Examples:** reset theme setting, restore default wallpaper"
        
        setting = self._find_setting_by_name(target)
        if not setting:
            return f"🔍 **Setting not found:** '{target}'"
        
        old_value = setting.current_value
        setting.current_value = setting.default_value
        setting.last_modified = time.time()
        setting.modified_by = "system"
        
        # Apply setting
        self._apply_setting_to_component(setting)
        
        # Save settings
        self._save_settings()
        
        response = f"🔄 **Reset {setting.name} to default:** {self._format_setting_value(setting)}\n"
        
        if old_value != setting.default_value:
            old_value_str = self._format_value_by_type(setting.setting_type, old_value)
            response += f"   └─ Previous value: {old_value_str}\n"
        
        if setting.requires_restart:
            response += f"   └─ ⚠️ Restart required to apply changes\n"
        
        return response
    
    def _handle_list_settings(self, entities: Dict) -> str:
        """Handle list settings commands"""
        target = entities.get('setting_target', '').strip()
        
        if not target or target in ['all', 'everything']:
            # List all settings grouped by category
            return self._list_all_settings()
        
        # Try to match category
        category = self._find_category_by_name(target)
        if category:
            return self._list_category_settings(category)
        
        # Search for settings matching target
        matching_settings = self._search_settings(target)
        if not matching_settings:
            return f"🔍 **No settings found matching:** '{target}'"
        
        response = f"⚙️ **Settings matching '{target}':**\n\n"
        
        for setting in matching_settings[:10]:  # Limit to 10
            value_str = self._format_setting_value(setting)
            response += f"• **{setting.name}:** {value_str}\n"
            response += f"  └─ {setting.description}\n"
        
        if len(matching_settings) > 10:
            response += f"\n*(Showing first 10 of {len(matching_settings)} settings)*"
        
        return response
    
    def _handle_search_settings(self, entities: Dict) -> str:
        """Handle search settings commands"""
        query = entities.get('setting_target', '').strip()
        if not query:
            return "🔍 **Please specify what to search for**\n\n**Examples:** find theme settings, search for privacy options"
        
        # Search settings
        results = self._search_settings(query)
        
        if not results:
            return f"🔍 **No settings found for:** '{query}'\n\nTry different keywords or check spelling."
        
        response = f"🔍 **Found {len(results)} setting(s) for '{query}':**\n\n"
        
        # Group by category for better organization
        by_category = {}
        for setting in results:
            category = setting.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(setting)
        
        for category, settings in by_category.items():
            response += f"**{category.value.title()}:**\n"
            for setting in settings[:5]:  # Limit per category
                value_str = self._format_setting_value(setting)
                response += f"• {setting.name}: {value_str}\n"
            if len(settings) > 5:
                response += f"  ... and {len(settings) - 5} more\n"
            response += "\n"
        
        return response
    
    def _handle_backup_settings(self, entities: Dict) -> str:
        """Handle backup settings commands"""
        try:
            timestamp = int(time.time())
            backup_name = f"personalaios_settings_backup_{timestamp}.json"
            backup_file = self.settings_path / 'backups' / backup_name
            backup_file.parent.mkdir(exist_ok=True)
            
            # Create backup data
            backup_data = {
                'backup_info': {
                    'timestamp': timestamp,
                    'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'version': '1.0',
                    'total_settings': len(self.settings)
                },
                'settings': {}
            }
            
            # Export all settings
            for setting_id, setting in self.settings.items():
                backup_data['settings'][setting_id] = {
                    'current_value': setting.current_value,
                    'last_modified': setting.last_modified,
                    'modified_by': setting.modified_by
                }
            
            # Save backup
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            # Update backup history
            self.backup_history.append({
                'timestamp': timestamp,
                'file': str(backup_file),
                'settings_count': len(self.settings)
            })
            
            # Keep only last 10 backups
            self.backup_history = self.backup_history[-10:]
            
            return f"💾 **Settings backup created:** {backup_name}\n   └─ Location: {backup_file}\n   └─ Settings saved: {len(self.settings)}"
            
        except Exception as e:
            return f"❌ **Backup failed:** {str(e)}"
    
    def _handle_restore_settings(self, entities: Dict) -> str:
        """Handle restore settings commands"""
        try:
            backups_dir = self.settings_path / 'backups'
            if not backups_dir.exists():
                return "📂 **No backups found**\n\nCreate a backup first using 'backup settings'"
            
            # Find most recent backup
            backup_files = list(backups_dir.glob('personalaios_settings_backup_*.json'))
            if not backup_files:
                return "📂 **No backup files found**"
            
            # Use most recent backup
            latest_backup = max(backup_files, key=lambda f: f.stat().st_mtime)
            
            # Load backup
            with open(latest_backup, 'r') as f:
                backup_data = json.load(f)
            
            # Restore settings
            restored_count = 0
            failed_count = 0
            
            for setting_id, setting_data in backup_data.get('settings', {}).items():
                if setting_id in self.settings:
                    try:
                        setting = self.settings[setting_id]
                        setting.current_value = setting_data['current_value']
                        setting.last_modified = setting_data.get('last_modified', time.time())
                        setting.modified_by = setting_data.get('modified_by', 'restore')
                        
                        # Apply setting
                        self._apply_setting_to_component(setting)
                        restored_count += 1
                    except Exception as e:
                        logger.error(f"Failed to restore setting {setting_id}: {e}")
                        failed_count += 1
            
            # Save restored settings
            self._save_settings()
            
            backup_date = backup_data.get('backup_info', {}).get('date', 'unknown')
            
            response = f"📂 **Settings restored from backup**\n"
            response += f"   └─ Backup date: {backup_date}\n"
            response += f"   └─ Restored: {restored_count} settings\n"
            
            if failed_count > 0:
                response += f"   └─ Failed: {failed_count} settings\n"
            
            response += f"\n⚠️ **Restart PersonalAIOS** to apply all changes"
            
            return response
            
        except Exception as e:
            return f"❌ **Restore failed:** {str(e)}"
    
    def _handle_category_settings(self, entities: Dict) -> str:
        """Handle category-specific settings commands"""
        target = entities.get('setting_target', '').strip()
        if not target:
            return "📂 **Please specify a settings category**\n\n**Available categories:** appearance, system, privacy, accessibility, sound, personalaios"
        
        category = self._find_category_by_name(target)
        if not category:
            available = ', '.join([cat.value for cat in SettingCategory])
            return f"📂 **Category not found:** '{target}'\n\n**Available categories:** {available}"
        
        return self._list_category_settings(category)
    
    def _handle_setting_info(self, entities: Dict) -> str:
        """Handle setting information commands"""
        target = entities.get('setting_target', '').strip()
        if not target:
            return "ℹ️ **Please specify which setting you need info about**"
        
        setting = self._find_setting_by_name(target)
        if not setting:
            return f"🔍 **Setting not found:** '{target}'"
        
        response = f"ℹ️ **Setting Information: {setting.name}**\n\n"
        response += f"**Current Value:** {self._format_setting_value(setting)}\n"
        response += f"**Default Value:** {self._format_value_by_type(setting.setting_type, setting.default_value)}\n"
        response += f"**Category:** {setting.category.value.title()}\n"
        response += f"**Type:** {setting.setting_type.value.title()}\n"
        response += f"**Priority:** {setting.priority.value.title()}\n"
        response += f"**Description:** {setting.description}\n"
        
        if setting.choices:
            response += f"**Available Choices:** {', '.join(map(str, setting.choices))}\n"
        
        if setting.min_value is not None or setting.max_value is not None:
            range_info = f"**Range:** "
            if setting.min_value is not None:
                range_info += f"min {setting.min_value}"
            if setting.max_value is not None:
                range_info += f" max {setting.max_value}"
            response += range_info + "\n"
        
        if setting.requires_restart:
            response += f"**⚠️ Requires Restart:** Yes\n"
        
        if setting.component:
            response += f"**Component:** {setting.component}\n"
        
        if setting.help_text:
            response += f"**Help:** {setting.help_text}\n"
        
        if setting.keywords:
            response += f"**Keywords:** {', '.join(setting.keywords)}\n"
        
        return response
    
    def _handle_apply_profile(self, entities: Dict) -> str:
        """Handle apply profile commands"""
        profile_name = entities.get('setting_target', '').strip()
        if not profile_name:
            return "🎭 **Please specify which profile to apply**\n\n**Examples:** apply dark mode profile, use performance mode"
        
        # Define built-in profiles
        profiles = {
            'dark_mode': {
                'theme_mode': 'dark',
                'high_contrast': False,
                'animation_speed': 'normal'
            },
            'light_mode': {
                'theme_mode': 'light',
                'high_contrast': False,
                'animation_speed': 'normal'
            },
            'accessibility': {
                'large_text': True,
                'high_contrast': True,
                'animation_speed': 'slow',
                'font_size': 1.25
            },
            'performance': {
                'animation_speed': 'fast',
                'system_sounds': False,
                'ai_suggestions': False,
                'usage_statistics': False
            },
            'privacy_focused': {
                'usage_statistics': False,
                'location_services': False,
                'ai_learning_enabled': False
            },
            'default': {
                'theme_mode': 'auto',
                'ai_natural_language': True,
                'ai_learning_enabled': True,
                'ai_suggestions': True,
                'animation_speed': 'normal'
            }
        }
        
        # Find matching profile
        profile_key = None
        for key in profiles.keys():
            if profile_name.lower() in key or key in profile_name.lower():
                profile_key = key
                break
        
        if not profile_key:
            available = ', '.join(profiles.keys())
            return f"🎭 **Profile not found:** '{profile_name}'\n\n**Available profiles:** {available}"
        
        profile = profiles[profile_key]
        
        # Apply profile settings
        applied_count = 0
        failed_count = 0
        
        for setting_id, value in profile.items():
            if setting_id in self.settings:
                try:
                    setting = self.settings[setting_id]
                    setting.current_value = value
                    setting.last_modified = time.time()
                    setting.modified_by = f"profile:{profile_key}"
                    
                    # Apply setting
                    self._apply_setting_to_component(setting)
                    applied_count += 1
                except Exception as e:
                    logger.error(f"Failed to apply profile setting {setting_id}: {e}")
                    failed_count += 1
        
        # Save settings
        self._save_settings()
        
        response = f"🎭 **Applied {profile_key.replace('_', ' ').title()} profile**\n"
        response += f"   └─ Settings applied: {applied_count}\n"
        
        if failed_count > 0:
            response += f"   └─ Failed: {failed_count} settings\n"
        
        return response
    
    def _find_setting_by_name(self, name: str) -> Optional[SettingDefinition]:
        """Find setting by name using intelligent matching"""
        name_lower = name.lower().strip()
        
        # Exact ID match
        if name_lower in self.settings:
            return self.settings[name_lower]
        
        # Exact name match
        for setting in self.settings.values():
            if setting.name.lower() == name_lower:
                return setting
        
        # Partial name match
        for setting in self.settings.values():
            if name_lower in setting.name.lower():
                return setting
        
        # Keywords match
        for setting in self.settings.values():
            if setting.keywords and any(name_lower in keyword.lower() for keyword in setting.keywords):
                return setting
        
        # Alias match
        for main_term, aliases in self.setting_aliases.items():
            if name_lower in aliases or any(alias in name_lower for alias in aliases):
                # Find settings with this main term
                for setting in self.settings.values():
                    if main_term in setting.name.lower() or (setting.keywords and main_term in [k.lower() for k in setting.keywords]):
                        return setting
        
        return None
    
    def _find_category_by_name(self, name: str) -> Optional[SettingCategory]:
        """Find settings category by name"""
        name_lower = name.lower().strip()
        
        # Exact match
        for category in SettingCategory:
            if category.value == name_lower:
                return category
        
        # Partial match
        for category in SettingCategory:
            if name_lower in category.value or category.value in name_lower:
                return category
        
        return None
    
    def _search_settings(self, query: str) -> List[SettingDefinition]:
        """Search settings by query"""
        query_lower = query.lower()
        results = []
        
        for setting in self.settings.values():
            score = 0
            
            # Name match
            if query_lower in setting.name.lower():
                score += 10
            
            # Description match
            if query_lower in setting.description.lower():
                score += 5
            
            # Keywords match
            if setting.keywords and any(query_lower in keyword.lower() for keyword in setting.keywords):
                score += 8
            
            # Category match
            if query_lower in setting.category.value:
                score += 3
            
            # ID match
            if query_lower in setting.id:
                score += 7
            
            if score > 0:
                results.append((setting, score))
        
        # Sort by relevance score
        results.sort(key=lambda x: x[1], reverse=True)
        return [setting for setting, score in results]
    
    def _search_similar_settings(self, query: str) -> List[SettingDefinition]:
        """Find similar settings for suggestions"""
        query_lower = query.lower()
        suggestions = []
        
        for setting in self.settings.values():
            similarity = 0
            
            # Calculate similarity based on various factors
            name_words = setting.name.lower().split()
            query_words = query_lower.split()
            
            # Word overlap
            overlap = len(set(name_words).intersection(set(query_words)))
            if overlap > 0:
                similarity += overlap * 0.4
            
            # Substring match
            if any(word in setting.name.lower() for word in query_words):
                similarity += 0.3
            
            # Keywords match
            if setting.keywords:
                keyword_overlap = len(set(keyword.lower() for keyword in setting.keywords).intersection(set(query_words)))
                similarity += keyword_overlap * 0.3
            
            if similarity > 0.2:
                suggestions.append((setting, similarity))
        
        # Sort by similarity
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [setting for setting, similarity in suggestions[:5]]
    
    def _validate_and_convert_value(self, setting: SettingDefinition, value_str: str) -> Any:
        """Validate and convert string value to appropriate type"""
        value_str = value_str.strip()
        
        if setting.setting_type == SettingType.BOOLEAN:
            if value_str.lower() in ['true', 'yes', 'on', 'enabled', '1']:
                return True
            elif value_str.lower() in ['false', 'no', 'off', 'disabled', '0']:
                return False
            else:
                raise ValueError(f"Boolean value must be true/false, yes/no, on/off, enabled/disabled, or 1/0")
        
        elif setting.setting_type == SettingType.INTEGER:
            try:
                value = int(value_str)
                if setting.min_value is not None and value < setting.min_value:
                    raise ValueError(f"Value must be at least {setting.min_value}")
                if setting.max_value is not None and value > setting.max_value:
                    raise ValueError(f"Value must be at most {setting.max_value}")
                return value
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid integer value: {value_str}")
                raise e
        
        elif setting.setting_type == SettingType.FLOAT:
            try:
                value = float(value_str.replace('%', ''))  # Handle percentages
                if setting.min_value is not None and value < setting.min_value:
                    raise ValueError(f"Value must be at least {setting.min_value}")
                if setting.max_value is not None and value > setting.max_value:
                    raise ValueError(f"Value must be at most {setting.max_value}")
                return value
            except ValueError as e:
                if "could not convert" in str(e):
                    raise ValueError(f"Invalid number value: {value_str}")
                raise e
        
        elif setting.setting_type == SettingType.CHOICE:
            if setting.choices:
                # Exact match
                if value_str in setting.choices:
                    return value_str
                # Case insensitive match
                for choice in setting.choices:
                    if str(choice).lower() == value_str.lower():
                        return choice
                # Partial match
                matches = [choice for choice in setting.choices if value_str.lower() in str(choice).lower()]
                if len(matches) == 1:
                    return matches[0]
                elif len(matches) > 1:
                    raise ValueError(f"Ambiguous choice '{value_str}'. Options: {', '.join(map(str, matches))}")
                else:
                    raise ValueError(f"Invalid choice '{value_str}'. Options: {', '.join(map(str, setting.choices))}")
            return value_str
        
        elif setting.setting_type == SettingType.COLOR:
            # Basic color validation (hex colors)
            if value_str.startswith('#') and len(value_str) in [4, 7]:
                try:
                    int(value_str[1:], 16)
                    return value_str
                except ValueError:
                    pass
            raise ValueError(f"Invalid color format. Use hex format like #ff0000 or #f00")
        
        elif setting.setting_type == SettingType.FILE:
            path = Path(value_str).expanduser()
            if not path.exists():
                raise ValueError(f"File does not exist: {value_str}")
            return str(path)
        
        elif setting.setting_type == SettingType.DIRECTORY:
            path = Path(value_str).expanduser()
            if not path.exists() or not path.is_dir():
                raise ValueError(f"Directory does not exist: {value_str}")
            return str(path)
        
        # Default to string
        return value_str
    
    def _format_setting_value(self, setting: SettingDefinition) -> str:
        """Format setting value for display"""
        return self._format_value_by_type(setting.setting_type, setting.current_value)
    
    def _format_value_by_type(self, setting_type: SettingType, value: Any) -> str:
        """Format value by type for display"""
        if value is None:
            return "None"
        
        if setting_type == SettingType.BOOLEAN:
            return "✅ Enabled" if value else "❌ Disabled"
        elif setting_type == SettingType.FLOAT and isinstance(value, (int, float)):
            if 0 <= value <= 1:
                return f"{value * 100:.0f}%"
            return f"{value:.2f}"
        elif setting_type == SettingType.COLOR:
            return f"{value} 🎨"
        elif setting_type in [SettingType.FILE, SettingType.DIRECTORY]:
            return f"`{value}`"
        else:
            return str(value)
    
    def _apply_setting_to_component(self, setting: SettingDefinition):
        """Apply setting to its corresponding component"""
        if setting.component and setting.component in self.components:
            try:
                component = self.components[setting.component]
                if hasattr(component, 'update_setting'):
                    component.update_setting(setting.id, setting.current_value)
                logger.info(f"Applied setting {setting.id} to component {setting.component}")
            except Exception as e:
                logger.error(f"Failed to apply setting {setting.id} to component: {e}")
    
    def _list_all_settings(self) -> str:
        """List all settings grouped by category"""
        response = "⚙️ **PersonalAIOS Settings Overview**\n\n"
        
        for category in SettingCategory:
            if category in self.setting_categories:
                category_settings = [self.settings[sid] for sid in self.setting_categories[category]]
                if category_settings:
                    response += f"**{category.value.title()} ({len(category_settings)} settings):**\n"
                    
                    for setting in category_settings[:5]:  # Limit per category
                        value_str = self._format_setting_value(setting)
                        response += f"• {setting.name}: {value_str}\n"
                    
                    if len(category_settings) > 5:
                        response += f"  ... and {len(category_settings) - 5} more\n"
                    response += "\n"
        
        response += f"**Total Settings:** {len(self.settings)}\n"
        response += f"**Categories:** {len(self.setting_categories)}\n"
        
        return response
    
    def _list_category_settings(self, category: SettingCategory) -> str:
        """List settings for a specific category"""
        if category not in self.setting_categories:
            return f"📂 **No settings found in category:** {category.value}"
        
        setting_ids = self.setting_categories[category]
        settings_list = [self.settings[sid] for sid in setting_ids]
        
        response = f"📂 **{category.value.title()} Settings** ({len(settings_list)} total):\n\n"
        
        for setting in settings_list:
            value_str = self._format_setting_value(setting)
            priority_icon = self._get_priority_icon(setting.priority)
            
            response += f"{priority_icon} **{setting.name}:** {value_str}\n"
            response += f"   └─ {setting.description}\n"
            
            if setting.requires_restart:
                response += f"   └─ ⚠️ Requires restart\n"
            
            response += "\n"
        
        return response
    
    def _get_priority_icon(self, priority: SettingPriority) -> str:
        """Get icon for setting priority"""
        icons = {
            SettingPriority.ESSENTIAL: '🔴',
            SettingPriority.IMPORTANT: '🟠',
            SettingPriority.NORMAL: '🔵',
            SettingPriority.ADVANCED: '🟡',
            SettingPriority.DEBUG: '🔍'
        }
        return icons.get(priority, '⚪')
    
    def _save_settings(self):
        """Save settings to persistent storage"""
        try:
            settings_file = self.settings_path / 'settings.json'
            
            # Prepare data for serialization
            settings_data = {}
            for setting_id, setting in self.settings.items():
                settings_data[setting_id] = {
                    'current_value': setting.current_value,
                    'last_modified': setting.last_modified,
                    'modified_by': setting.modified_by
                }
            
            save_data = {
                'settings': settings_data,
                'backup_history': self.backup_history,
                'last_save': time.time()
            }
            
            with open(settings_file, 'w') as f:
                json.dump(save_data, f, indent=2, default=str)
                
            logger.info(f"Saved {len(settings_data)} settings to storage")
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def _load_settings(self):
        """Load settings from persistent storage"""
        try:
            settings_file = self.settings_path / 'settings.json'
            if not settings_file.exists():
                return
            
            with open(settings_file, 'r') as f:
                save_data = json.load(f)
            
            # Load settings values
            settings_data = save_data.get('settings', {})
            for setting_id, setting_info in settings_data.items():
                if setting_id in self.settings:
                    setting = self.settings[setting_id]
                    setting.current_value = setting_info.get('current_value', setting.default_value)
                    setting.last_modified = setting_info.get('last_modified', 0)
                    setting.modified_by = setting_info.get('modified_by', 'system')
            
            # Load backup history
            self.backup_history = save_data.get('backup_history', [])
            
            logger.info(f"Loaded {len(settings_data)} settings from storage")
            
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
    
    def get_setting_value(self, setting_id: str) -> Any:
        """Get current value of a setting"""
        if setting_id in self.settings:
            return self.settings[setting_id].current_value
        return None
    
    def set_setting_value(self, setting_id: str, value: Any, save: bool = True) -> bool:
        """Set value of a setting programmatically"""
        if setting_id not in self.settings:
            return False
        
        try:
            setting = self.settings[setting_id]
            setting.current_value = value
            setting.last_modified = time.time()
            setting.modified_by = "api"
            
            # Apply setting
            self._apply_setting_to_component(setting)
            
            if save:
                self._save_settings()
            
            return True
        except Exception as e:
            logger.error(f"Failed to set setting {setting_id}: {e}")
            return False
    
    def _handle_unknown_intent(self, user_input: str) -> str:
        """Handle unknown settings commands"""
        return f"""❓ **I didn't understand:** "{user_input}"

⚙️ **Try these natural language settings commands:**

**Get Settings:**
• "theme setting" - Check current theme
• "current wallpaper" - Show wallpaper setting
• "AI learning setting" - Check AI learning status

**Change Settings:**
• "set theme to dark" - Change theme mode
• "make AI learning true" - Enable AI learning
• "change volume to 75%" - Set volume level

**Settings Management:**
• "list appearance settings" - Show category settings
• "search privacy settings" - Find privacy options
• "reset theme setting" - Restore default value

**Backup & Restore:**
• "backup settings" - Save current configuration
• "restore settings" - Load from backup

**Profiles:**
• "apply dark mode profile" - Use predefined profile
• "use accessibility profile" - Apply accessibility settings

**I understand natural language - speak naturally!** 🤖"""

# For compatibility with Desktop Manager
DynamicSettingsManager = IntelligentSettingsManager

if __name__ == '__main__':
    settings_manager = IntelligentSettingsManager()
    
    # Demo commands
    print(settings_manager.process_command("list appearance settings"))
    print("\n" + "="*50 + "\n")
    print(settings_manager.process_command("theme setting"))
    print("\n" + "="*50 + "\n")
    print(settings_manager.process_command("set theme to dark"))

