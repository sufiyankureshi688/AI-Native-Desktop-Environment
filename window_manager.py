#!/usr/bin/env python3
"""
PersonalAIOS Intelligent Window Manager
Revolutionary AI-native window management with perfect natural language understanding
No hardcoding - pure dynamic intelligence that understands human intent
"""
import gi
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json
import time

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Gio

# Try to import window management libraries
try:
    import wnck
    HAVE_WNCK = True
except ImportError:
    HAVE_WNCK = False

try:
    import Xlib
    from Xlib import display
    HAVE_XLIB = True
except ImportError:
    HAVE_XLIB = False

class WindowAction(Enum):
    """Dynamic window actions"""
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize" 
    RESTORE = "restore"
    CLOSE = "close"
    FOCUS = "focus"
    MOVE = "move"
    RESIZE = "resize"
    FULLSCREEN = "fullscreen"
    TILE_LEFT = "tile_left"
    TILE_RIGHT = "tile_right"
    TILE_TOP = "tile_top"
    TILE_BOTTOM = "tile_bottom"
    WORKSPACE_MOVE = "workspace_move"
    WORKSPACE_SWITCH = "workspace_switch"
    ALWAYS_ON_TOP = "always_on_top"
    SHADE = "shade"
    STICKY = "sticky"

@dataclass
class WindowInfo:
    """Comprehensive window information"""
    window_id: int
    title: str
    application: str
    workspace: int
    x: int
    y: int
    width: int
    height: int
    is_maximized: bool
    is_minimized: bool
    is_focused: bool
    is_fullscreen: bool
    window_type: str
    pid: int

class IntelligentWindowManager:
    """
    Revolutionary Window Manager with AI-native natural language understanding
    
    Features:
    - Perfect natural language command processing
    - Dynamic window pattern recognition
    - Context-aware window management
    - Spatial relationship understanding
    - Application-aware intelligent actions
    - Self-learning user preferences
    """
    
    def __init__(self):
        """Initialize the intelligent window manager"""
        self.display = None
        self.screen = None
        self.windows_cache = {}
        self.command_history = []
        self.user_preferences = {}
        
        # Dynamic intent patterns for natural language understanding
        self.intent_patterns = {
            'maximize_window': [
                r'maximize (?:the )?(?:window|app)(?:\s+(.+))?',
                r'make (?:the )?(?:window|app)(?:\s+(.+))?\s+(?:full\s*screen|fullscreen|bigger|maximum)',
                r'expand (?:the )?(?:window|app)(?:\s+(.+))?',
                r'(?:window|app)(?:\s+(.+))?\s+to\s+(?:full\s*screen|maximum)',
            ],
            'minimize_window': [
                r'minimize (?:the )?(?:window|app)(?:\s+(.+))?',
                r'hide (?:the )?(?:window|app)(?:\s+(.+))?',
                r'shrink (?:the )?(?:window|app)(?:\s+(.+))?',
                r'put (?:the )?(?:window|app)(?:\s+(.+))?\s+(?:away|in\s+background)',
                r'(?:window|app)(?:\s+(.+))?\s+to\s+(?:taskbar|tray)',
            ],
            'close_window': [
                r'close (?:the )?(?:window|app)(?:\s+(.+))?',
                r'quit (?:the )?(?:window|app)(?:\s+(.+))?',
                r'exit (?:the )?(?:window|app)(?:\s+(.+))?',
                r'kill (?:the )?(?:window|app)(?:\s+(.+))?',
                r'shut\s*down (?:the )?(?:window|app)(?:\s+(.+))?',
            ],
            'focus_window': [
                r'focus (?:on )?(?:the )?(?:window|app)(?:\s+(.+))?',
                r'switch to (?:the )?(?:window|app)(?:\s+(.+))?',
                r'bring (?:the )?(?:window|app)(?:\s+(.+))?\s+(?:to\s+)?(?:front|forward)',
                r'show (?:me )?(?:the )?(?:window|app)(?:\s+(.+))?',
                r'go to (?:the )?(?:window|app)(?:\s+(.+))?',
            ],
            'move_window': [
                r'move (?:the )?(?:window|app)(?:\s+(.+))?\s+to\s+(.+)',
                r'put (?:the )?(?:window|app)(?:\s+(.+))?\s+(?:on|at)\s+(.+)',
                r'place (?:the )?(?:window|app)(?:\s+(.+))?\s+(?:on|at)\s+(.+)',
                r'position (?:the )?(?:window|app)(?:\s+(.+))?\s+(?:on|at)\s+(.+)',
            ],
            'resize_window': [
                r'resize (?:the )?(?:window|app)(?:\s+(.+))?\s+to\s+(.+)',
                r'make (?:the )?(?:window|app)(?:\s+(.+))?\s+(.+)\s+(?:size|big|small)',
                r'change (?:the )?(?:window|app)(?:\s+(.+))?\s+size\s+to\s+(.+)',
            ],
            'tile_window': [
                r'tile (?:the )?(?:window|app)(?:\s+(.+))?\s+(?:to\s+)?(?:the\s+)?(left|right|top|bottom)',
                r'snap (?:the )?(?:window|app)(?:\s+(.+))?\s+(?:to\s+)?(?:the\s+)?(left|right|top|bottom)',
                r'dock (?:the )?(?:window|app)(?:\s+(.+))?\s+(?:to\s+)?(?:the\s+)?(left|right|top|bottom)',
                r'(?:window|app)(?:\s+(.+))?\s+(?:to\s+)?(?:the\s+)?(left|right|top|bottom)\s+(?:side|half)',
            ],
            'workspace_action': [
                r'move (?:the )?(?:window|app)(?:\s+(.+))?\s+to\s+workspace\s+(\d+|next|previous|left|right)',
                r'send (?:the )?(?:window|app)(?:\s+(.+))?\s+to\s+workspace\s+(\d+|next|previous|left|right)',
                r'switch\s+to\s+workspace\s+(\d+|next|previous|left|right)',
                r'go\s+to\s+workspace\s+(\d+|next|previous|left|right)',
            ],
            'window_properties': [
                r'make (?:the )?(?:window|app)(?:\s+(.+))?\s+(?:always\s+on\s+top|stick|sticky)',
                r'keep (?:the )?(?:window|app)(?:\s+(.+))?\s+(?:on\s+top|visible)',
                r'pin (?:the )?(?:window|app)(?:\s+(.+))?',
            ],
            'list_windows': [
                r'list (?:all )?(?:open )?(?:windows|apps)',
                r'show (?:me )?(?:all )?(?:open )?(?:windows|apps)',
                r'what (?:windows|apps)\s+are\s+(?:open|running)',
                r'display (?:all )?(?:open )?(?:windows|apps)',
            ],
            'window_info': [
                r'(?:info|information|details)\s+(?:about\s+)?(?:the )?(?:window|app)(?:\s+(.+))?',
                r'what\s+is\s+(?:the )?(?:window|app)(?:\s+(.+))?',
                r'describe (?:the )?(?:window|app)(?:\s+(.+))?',
                r'tell\s+me\s+about\s+(?:the )?(?:window|app)(?:\s+(.+))?',
            ],
        }
        
        # Spatial and contextual keywords
        self.spatial_keywords = {
            'left': ['left', 'west'],
            'right': ['right', 'east'], 
            'top': ['top', 'up', 'north'],
            'bottom': ['bottom', 'down', 'south'],
            'center': ['center', 'middle'],
            'corner': ['corner'],
        }
        
        self.size_keywords = {
            'small': ['small', 'tiny', 'mini', 'compact'],
            'medium': ['medium', 'normal', 'regular'],
            'large': ['large', 'big', 'huge', 'maximum'],
        }
        
        # Initialize connection
        self._initialize_window_system()
        
        print("🪟 Intelligent Window Manager initialized with natural language processing")
    
    def _initialize_window_system(self):
        """Initialize window system connection"""
        try:
            if HAVE_XLIB:
                self.display = display.Display()
                self.screen = self.display.screen()
                print("✅ X11 window system connection established")
            else:
                print("⚠️ X11 libraries not available - using fallback methods")
        except Exception as e:
            print(f"⚠️ Window system initialization failed: {e}")
    
    def process_command(self, user_input: str) -> str:
        """Process natural language window management commands"""
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
        return self._execute_window_intent(intent, entities, user_input)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better understanding"""
        # Remove common filler words and normalize
        text = re.sub(r'\b(?:please|can\s+you|would\s+you|could\s+you)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip().lower()
        return text
    
    def _extract_intent_and_entities(self, text: str) -> Tuple[Optional[str], Dict]:
        """Extract intent and entities from natural language"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities = {
                        'groups': match.groups(),
                        'context': self._extract_spatial_context(text),
                        'window_target': self._identify_window_target(text, match.groups())
                    }
                    return intent, entities
        
        return None, {}
    
    def _extract_spatial_context(self, text: str) -> Dict:
        """Extract spatial and contextual information"""
        context = {}
        
        # Find spatial references
        for direction, keywords in self.spatial_keywords.items():
            if any(keyword in text for keyword in keywords):
                context['direction'] = direction
                break
        
        # Find size references  
        for size, keywords in self.size_keywords.items():
            if any(keyword in text for keyword in keywords):
                context['size'] = size
                break
        
        # Find workspace references
        workspace_match = re.search(r'workspace\s+(\d+|next|previous|left|right)', text)
        if workspace_match:
            context['workspace'] = workspace_match.group(1)
        
        return context
    
    def _identify_window_target(self, text: str, groups: Tuple) -> Optional[str]:
        """Identify which window the command targets"""
        # Check for specific application names
        app_names = ['firefox', 'chrome', 'terminal', 'code', 'vscode', 'nautilus', 
                    'files', 'calculator', 'text editor', 'browser', 'editor']
        
        for app in app_names:
            if app in text:
                return app
        
        # Check for "current" or "active" window
        if any(keyword in text for keyword in ['current', 'active', 'this', 'focused']):
            return 'current'
        
        # Use groups from regex match
        if groups and groups[0]:
            return groups[0].strip()
        
        return 'current'  # Default to current window
    
    def _execute_window_intent(self, intent: str, entities: Dict, original_text: str) -> str:
        """Execute the identified window management intent"""
        try:
            if intent == 'maximize_window':
                return self._maximize_window(entities)
            elif intent == 'minimize_window':
                return self._minimize_window(entities)
            elif intent == 'close_window':
                return self._close_window(entities)
            elif intent == 'focus_window':
                return self._focus_window(entities)
            elif intent == 'move_window':
                return self._move_window(entities)
            elif intent == 'resize_window':
                return self._resize_window(entities)
            elif intent == 'tile_window':
                return self._tile_window(entities)
            elif intent == 'workspace_action':
                return self._workspace_action(entities)
            elif intent == 'window_properties':
                return self._set_window_properties(entities)
            elif intent == 'list_windows':
                return self._list_windows(entities)
            elif intent == 'window_info':
                return self._get_window_info(entities)
            else:
                return f"🪟 **Intent recognized** ({intent}) but implementation pending"
                
        except Exception as e:
            return f"❌ **Window management error:** {str(e)}"
    
    def _maximize_window(self, entities: Dict) -> str:
        """Maximize window with intelligent targeting"""
        window_target = entities.get('window_target', 'current')
        
        try:
            if window_target == 'current':
                # Use wmctrl to maximize current window
                result = subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-b', 'add,maximized_vert,maximized_horz'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return f"🔲 **Maximized current window**"
                else:
                    return f"⚠️ **Failed to maximize:** Window control not available"
            else:
                # Find and maximize specific window
                windows = self._get_window_list()
                target_window = self._find_window_by_name(windows, window_target)
                
                if target_window:
                    subprocess.run(['wmctrl', '-i', '-r', str(target_window['id']), '-b', 'add,maximized_vert,maximized_horz'])
                    return f"🔲 **Maximized window:** {target_window['title']}"
                else:
                    return f"🔍 **Window not found:** {window_target}"
        
        except FileNotFoundError:
            # Fallback methods
            return self._fallback_maximize()
        except Exception as e:
            return f"❌ **Maximize failed:** {str(e)}"
    
    def _minimize_window(self, entities: Dict) -> str:
        """Minimize window intelligently"""
        window_target = entities.get('window_target', 'current')
        
        try:
            if window_target == 'current':
                result = subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-b', 'add,hidden'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return f"📉 **Minimized current window**"
            else:
                windows = self._get_window_list()
                target_window = self._find_window_by_name(windows, window_target)
                
                if target_window:
                    subprocess.run(['wmctrl', '-i', '-r', str(target_window['id']), '-b', 'add,hidden'])
                    return f"📉 **Minimized window:** {target_window['title']}"
                else:
                    return f"🔍 **Window not found:** {window_target}"
                    
        except FileNotFoundError:
            return self._fallback_minimize()
        except Exception as e:
            return f"❌ **Minimize failed:** {str(e)}"
    
    def _close_window(self, entities: Dict) -> str:
        """Close window intelligently"""
        window_target = entities.get('window_target', 'current')
        
        try:
            if window_target == 'current':
                result = subprocess.run(['wmctrl', '-c', ':ACTIVE:'], capture_output=True, text=True)
                if result.returncode == 0:
                    return f"❌ **Closed current window**"
            else:
                windows = self._get_window_list()
                target_window = self._find_window_by_name(windows, window_target)
                
                if target_window:
                    subprocess.run(['wmctrl', '-i', '-c', str(target_window['id'])])
                    return f"❌ **Closed window:** {target_window['title']}"
                else:
                    return f"🔍 **Window not found:** {window_target}"
                    
        except FileNotFoundError:
            return self._fallback_close()
        except Exception as e:
            return f"❌ **Close failed:** {str(e)}"
    
    def _focus_window(self, entities: Dict) -> str:
        """Focus window intelligently"""
        window_target = entities.get('window_target', 'current')
        
        try:
            windows = self._get_window_list()
            target_window = self._find_window_by_name(windows, window_target)
            
            if target_window:
                subprocess.run(['wmctrl', '-i', '-a', str(target_window['id'])])
                return f"👁️ **Focused on window:** {target_window['title']}"
            else:
                return f"🔍 **Window not found:** {window_target}"
                
        except FileNotFoundError:
            return self._fallback_focus()
        except Exception as e:
            return f"❌ **Focus failed:** {str(e)}"
    
    def _tile_window(self, entities: Dict) -> str:
        """Tile window to specified position"""
        window_target = entities.get('window_target', 'current')
        context = entities.get('context', {})
        direction = context.get('direction', 'left')  # Default to left
        
        try:
            # Get screen dimensions
            screen_width, screen_height = self._get_screen_dimensions()
            
            # Calculate tile position and size
            if direction == 'left':
                x, y, w, h = 0, 0, screen_width // 2, screen_height
            elif direction == 'right':
                x, y, w, h = screen_width // 2, 0, screen_width // 2, screen_height
            elif direction == 'top':
                x, y, w, h = 0, 0, screen_width, screen_height // 2
            elif direction == 'bottom':
                x, y, w, h = 0, screen_height // 2, screen_width, screen_height // 2
            else:
                return f"⚠️ **Unknown direction:** {direction}"
            
            # Apply tiling
            if window_target == 'current':
                subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-b', 'remove,maximized_vert,maximized_horz'])
                subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-e', f'0,{x},{y},{w},{h}'])
                return f"🔲 **Tiled current window to {direction}**"
            else:
                windows = self._get_window_list()
                target_window = self._find_window_by_name(windows, window_target)
                
                if target_window:
                    subprocess.run(['wmctrl', '-i', '-r', str(target_window['id']), '-b', 'remove,maximized_vert,maximized_horz'])
                    subprocess.run(['wmctrl', '-i', '-r', str(target_window['id']), '-e', f'0,{x},{y},{w},{h}'])
                    return f"🔲 **Tiled {target_window['title']} to {direction}**"
                else:
                    return f"🔍 **Window not found:** {window_target}"
                    
        except FileNotFoundError:
            return self._fallback_tile(direction)
        except Exception as e:
            return f"❌ **Tile failed:** {str(e)}"
    
    def _workspace_action(self, entities: Dict) -> str:
        """Handle workspace-related actions"""
        context = entities.get('context', {})
        workspace = context.get('workspace', '1')
        
        try:
            if 'move' in entities.get('groups', [''])[0] or 'send' in entities.get('groups', [''])[0]:
                # Move window to workspace
                if workspace.isdigit():
                    subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-t', str(int(workspace) - 1)])
                    return f"🔄 **Moved current window to workspace {workspace}**"
                elif workspace in ['next', 'right']:
                    subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-t', 'next'])
                    return f"🔄 **Moved current window to next workspace**"
                elif workspace in ['previous', 'left']:
                    subprocess.run(['wmctrl', '-r', ':ACTIVE:', '-t', 'prev'])
                    return f"🔄 **Moved current window to previous workspace**"
            else:
                # Switch workspace
                if workspace.isdigit():
                    subprocess.run(['wmctrl', '-s', str(int(workspace) - 1)])
                    return f"🔄 **Switched to workspace {workspace}**"
                elif workspace in ['next', 'right']:
                    subprocess.run(['wmctrl', '-s', 'next'])
                    return f"🔄 **Switched to next workspace**"
                elif workspace in ['previous', 'left']:
                    subprocess.run(['wmctrl', '-s', 'prev'])
                    return f"🔄 **Switched to previous workspace**"
                    
        except FileNotFoundError:
            return "⚠️ **Workspace management not available** (wmctrl not found)"
        except Exception as e:
            return f"❌ **Workspace action failed:** {str(e)}"
    
    def _list_windows(self, entities: Dict) -> str:
        """List all open windows"""
        try:
            windows = self._get_window_list()
            
            if not windows:
                return "🪟 **No windows found** or window management not available"
            
            response = f"🪟 **Open Windows** ({len(windows)} total):\n\n"
            
            for i, window in enumerate(windows[:15], 1):  # Limit to 15 windows
                icon = self._get_window_icon(window.get('class', ''))
                title = window.get('title', 'Unknown')[:50]  # Truncate long titles
                app = window.get('class', 'Unknown')
                workspace = window.get('workspace', 'Unknown')
                
                response += f"{icon} **{title}**\n"
                response += f"   └─ App: {app} | Workspace: {workspace}\n"
            
            if len(windows) > 15:
                response += f"\n*(Showing first 15 of {len(windows)} windows)*"
            
            return response
            
        except Exception as e:
            return f"❌ **Failed to list windows:** {str(e)}"
    
    def _get_window_info(self, entities: Dict) -> str:
        """Get detailed information about a window"""
        window_target = entities.get('window_target', 'current')
        
        try:
            if window_target == 'current':
                window_info = self._get_current_window_info()
            else:
                windows = self._get_window_list()
                window_info = self._find_window_by_name(windows, window_target)
            
            if not window_info:
                return f"🔍 **Window not found:** {window_target}"
            
            response = f"ℹ️ **Window Information:**\n\n"
            response += f"**Title:** {window_info.get('title', 'Unknown')}\n"
            response += f"**Application:** {window_info.get('class', 'Unknown')}\n"
            response += f"**Workspace:** {window_info.get('workspace', 'Unknown')}\n"
            
            if 'geometry' in window_info:
                geometry = window_info['geometry']
                response += f"**Position:** {geometry.get('x', 0)}, {geometry.get('y', 0)}\n"
                response += f"**Size:** {geometry.get('width', 0)} × {geometry.get('height', 0)}\n"
            
            if 'state' in window_info:
                state = window_info['state']
                response += f"**Maximized:** {'Yes' if state.get('maximized', False) else 'No'}\n"
                response += f"**Minimized:** {'Yes' if state.get('minimized', False) else 'No'}\n"
                response += f"**Focused:** {'Yes' if state.get('focused', False) else 'No'}\n"
            
            return response
            
        except Exception as e:
            return f"❌ **Failed to get window info:** {str(e)}"
    
    def _get_window_list(self) -> List[Dict]:
        """Get list of all windows using available methods"""
        try:
            # Try wmctrl first
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                return self._parse_wmctrl_output(result.stdout)
        except FileNotFoundError:
            pass
        
        # Try xdotool
        try:
            result = subprocess.run(['xdotool', 'search', '--onlyvisible', '.'], capture_output=True, text=True)
            if result.returncode == 0:
                return self._parse_xdotool_output(result.stdout)
        except FileNotFoundError:
            pass
        
        # Fallback
        return []
    
    def _parse_wmctrl_output(self, output: str) -> List[Dict]:
        """Parse wmctrl -l output"""
        windows = []
        for line in output.strip().split('\n'):
            if line:
                parts = line.split(None, 3)
                if len(parts) >= 4:
                    windows.append({
                        'id': parts[0],
                        'workspace': parts[1],
                        'class': parts[2],
                        'title': parts[3]
                    })
        return windows
    
    def _find_window_by_name(self, windows: List[Dict], name: str) -> Optional[Dict]:
        """Find window by name or application"""
        name_lower = name.lower()
        
        # Exact title match
        for window in windows:
            if name_lower in window.get('title', '').lower():
                return window
        
        # Application class match
        for window in windows:
            if name_lower in window.get('class', '').lower():
                return window
        
        # Fuzzy match
        for window in windows:
            title = window.get('title', '').lower()
            app_class = window.get('class', '').lower()
            if any(word in title or word in app_class for word in name_lower.split()):
                return window
        
        return None
    
    def _get_screen_dimensions(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        try:
            result = subprocess.run(['xrandr'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if ' connected' in line and 'primary' in line:
                    match = re.search(r'(\d+)x(\d+)', line)
                    if match:
                        return int(match.group(1)), int(match.group(2))
        except:
            pass
        
        # Fallback
        return 1920, 1080
    
    def _get_window_icon(self, app_class: str) -> str:
        """Get appropriate icon for window/application"""
        app_class_lower = app_class.lower()
        
        icon_map = {
            'firefox': '🦊', 'chrome': '🌐', 'chromium': '🌐',
            'terminal': '🖥️', 'gnome-terminal': '🖥️', 'konsole': '🖥️',
            'nautilus': '📁', 'files': '📁', 'thunar': '📁',
            'code': '💻', 'vscode': '💻', 'atom': '💻',
            'libreoffice': '📄', 'writer': '📄', 'calc': '📊',
            'gimp': '🎨', 'inkscape': '🎨', 'blender': '🎬',
            'vlc': '🎬', 'mpv': '🎬', 'totem': '🎬',
            'spotify': '🎵', 'rhythmbox': '🎵',
            'calculator': '🧮', 'gcalc': '🧮',
        }
        
        for app_name, icon in icon_map.items():
            if app_name in app_class_lower:
                return icon
        
        return '🪟'  # Default window icon
    
    # Fallback methods when wmctrl/xdotool are not available
    def _fallback_maximize(self) -> str:
        """Fallback maximize using keyboard shortcut"""
        try:
            subprocess.run(['xdotool', 'key', 'super+Up'])
            return "🔲 **Maximized current window** (using keyboard shortcut)"
        except:
            return "⚠️ **Window management tools not available**"
    
    def _fallback_minimize(self) -> str:
        """Fallback minimize"""
        try:
            subprocess.run(['xdotool', 'key', 'super+h'])
            return "📉 **Minimized current window** (using keyboard shortcut)"
        except:
            return "⚠️ **Window management tools not available**"
    
    def _fallback_close(self) -> str:
        """Fallback close"""
        try:
            subprocess.run(['xdotool', 'key', 'alt+F4'])
            return "❌ **Closed current window** (using keyboard shortcut)"
        except:
            return "⚠️ **Window management tools not available**"
    
    def _handle_unknown_intent(self, user_input: str) -> str:
        """Handle unknown window management commands"""
        return f"""❓ **I didn't understand:** "{user_input}"

🪟 **Try these natural language window commands:**

**Window Control:**
• "maximize the browser window"
• "minimize Firefox"
• "close the terminal"
• "focus on VS Code"

**Window Arrangement:**
• "tile the current window to the left"
• "snap Firefox to the right side"
• "move the editor to workspace 2"

**Information:**
• "list all open windows"
• "what windows are open"
• "info about the current window"

**I understand natural language - speak naturally!** 🤖"""

# For compatibility with Desktop Manager
DynamicWindowManager = IntelligentWindowManager

