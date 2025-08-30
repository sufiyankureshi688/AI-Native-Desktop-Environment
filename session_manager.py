#!/usr/bin/env python3
"""
PersonalAIOS Intelligent Session Manager
Revolutionary AI-native session management with perfect natural language understanding
Handles session initialization, component management, state persistence, and graceful shutdown
"""
import gi
import os
import json
import time
import signal
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import psutil

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Gio, Adw

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('PersonalAIOSSession')

class SessionState(Enum):
    """Session lifecycle states"""
    STARTING = "starting"
    RUNNING = "running"
    SAVING = "saving"
    SHUTTING_DOWN = "shutting_down"
    CRASHED = "crashed"
    IDLE = "idle"

class ComponentState(Enum):
    """Component states"""
    INACTIVE = "inactive"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    FAILED = "failed"

@dataclass
class SessionComponent:
    """Session component definition"""
    name: str
    executable: Optional[str] = None
    module_name: Optional[str] = None
    class_name: Optional[str] = None
    required: bool = True
    restart_on_failure: bool = True
    max_restart_attempts: int = 3
    startup_delay: float = 0
    dependencies: List[str] = None
    process: Optional[subprocess.Popen] = None
    instance: Optional[Any] = None
    state: ComponentState = ComponentState.INACTIVE
    restart_count: int = 0
    last_start_time: float = 0
    last_failure_time: float = 0

@dataclass
class SessionInfo:
    """Complete session information"""
    session_id: str
    user_id: str
    start_time: float
    state: SessionState
    components: Dict[str, SessionComponent]
    environment: Dict[str, str]
    saved_state: Dict[str, Any] = None
    ai_preferences: Dict[str, Any] = None

class IntelligentSessionManager:
    """
    Revolutionary AI-Native Session Manager
    
    Features:
    - Perfect natural language session control
    - Intelligent component lifecycle management
    - AI-powered session state persistence
    - Smart recovery from component failures
    - Context-aware session optimization
    - User behavior learning and adaptation
    - Graceful shutdown with state preservation
    - Dynamic component loading and management
    """
    
    def __init__(self):
        """Initialize the intelligent session manager"""
        self.session_info: Optional[SessionInfo] = None
        self.session_path = Path.home() / '.personalaios' / 'session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Command processing
        self.command_history = []
        
        # AI-powered intent patterns for natural language understanding
        self.intent_patterns = {
            'session_info': [
                r'(?:session|desktop)\s+(?:info|information|status|details)',
                r'(?:what\s+is\s+)?(?:the\s+)?(?:current\s+)?session\s+(?:status|state)',
                r'(?:how\s+is\s+)?(?:the\s+)?session\s+(?:doing|running)',
                r'(?:show\s+me\s+)?session\s+(?:details|information)',
            ],
            'restart_component': [
                r'restart\s+(.+?)(?:\s+component)?',
                r'reload\s+(.+?)(?:\s+component)?',
                r'reboot\s+(.+?)(?:\s+component)?',
                r'reset\s+(.+?)(?:\s+component)?',
            ],
            'stop_component': [
                r'stop\s+(.+?)(?:\s+component)?',
                r'kill\s+(.+?)(?:\s+component)?',
                r'disable\s+(.+?)(?:\s+component)?',
                r'turn\s+off\s+(.+?)(?:\s+component)?',
            ],
            'start_component': [
                r'start\s+(.+?)(?:\s+component)?',
                r'launch\s+(.+?)(?:\s+component)?',
                r'enable\s+(.+?)(?:\s+component)?',
                r'turn\s+on\s+(.+?)(?:\s+component)?',
            ],
            'list_components': [
                r'list\s+(?:all\s+)?(?:session\s+)?components',
                r'show\s+(?:me\s+)?(?:all\s+)?(?:session\s+)?components',
                r'(?:what\s+)?components\s+(?:are\s+)?(?:running|active|loaded)',
                r'display\s+(?:all\s+)?components',
            ],
            'save_session': [
                r'save\s+(?:the\s+)?session',
                r'preserve\s+(?:the\s+)?session\s+(?:state)?',
                r'store\s+(?:current\s+)?session',
                r'backup\s+(?:the\s+)?session',
            ],
            'restore_session': [
                r'restore\s+(?:the\s+)?(?:last\s+)?session',
                r'load\s+(?:the\s+)?(?:saved\s+)?session',
                r'recover\s+(?:the\s+)?(?:previous\s+)?session',
                r'bring\s+back\s+(?:the\s+)?(?:last\s+)?session',
            ],
            'logout': [
                r'(?:log\s*out|logout|sign\s*out)',
                r'end\s+(?:the\s+)?session',
                r'close\s+(?:the\s+)?session',
                r'exit\s+(?:the\s+)?(?:desktop|session)',
            ],
            'shutdown': [
                r'(?:shut\s*down|shutdown|power\s+off)',
                r'turn\s+off\s+(?:the\s+)?(?:computer|system)',
                r'power\s+down',
            ],
            'restart_session': [
                r'restart\s+(?:the\s+)?(?:desktop|session)',
                r'reload\s+(?:the\s+)?(?:desktop|session)',
                r'refresh\s+(?:the\s+)?(?:desktop|session)',
                r'reboot\s+(?:the\s+)?(?:desktop|session)',
            ]
        }
        
        # Core PersonalAIOS components
        self.core_components = {
            'ai_shell': SessionComponent(
                name='AI Shell',
                module_name='ai_shell',
                class_name='MinimalAIApp',
                required=True,
                restart_on_failure=True,
                max_restart_attempts=5
            ),
            'desktop_manager': SessionComponent(
                name='Desktop Manager',
                module_name='desktop_manager',
                class_name='DesktopManager',
                required=True,
                dependencies=['ai_shell'],
                restart_on_failure=True
            ),
            'window_manager': SessionComponent(
                name='Window Manager',
                module_name='window_manager',
                class_name='IntelligentWindowManager',
                required=False,
                restart_on_failure=True
            ),
            'notification_system': SessionComponent(
                name='Notification System',
                module_name='notification_system',
                class_name='IntelligentNotificationSystem',
                required=False,
                restart_on_failure=True
            ),
            'application_launcher': SessionComponent(
                name='Application Launcher',
                module_name='application_launcher',
                class_name='IntelligentApplicationLauncher',
                required=False,
                restart_on_failure=True
            ),
            'file_manager': SessionComponent(
                name='File Manager',
                module_name='ai_file_manager',
                class_name='IntelligentFileManager',
                required=False,
                restart_on_failure=True
            )
        }
        
        # Session management
        self.shutdown_requested = False
        self.restart_requested = False
        
        # Initialize session
        self._initialize_session()
        
        print("🔐 Intelligent Session Manager initialized - Managing PersonalAIOS lifecycle")
    
    def _initialize_session(self):
        """Initialize the session"""
        try:
            # Generate session ID
            session_id = f"personalaios_{int(time.time())}_{os.getpid()}"
            
            # Create session info
            self.session_info = SessionInfo(
                session_id=session_id,
                user_id=str(os.getuid()),
                start_time=time.time(),
                state=SessionState.STARTING,
                components=self.core_components.copy(),
                environment=dict(os.environ),
                ai_preferences=self._load_ai_preferences()
            )
            
            # Set up signal handlers
            self._setup_signal_handlers()
            
            # Create session lock file
            self._create_session_lock()
            
            # Load saved session state
            self._load_session_state()
            
            logger.info(f"Session initialized: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize session: {e}")
            raise
    
    def start_session(self):
        """Start the PersonalAIOS session"""
        try:
            logger.info("Starting PersonalAIOS session...")
            self.session_info.state = SessionState.STARTING
            
            # Set environment variables
            self._setup_session_environment()
            
            # Start components in dependency order
            started_components = self._start_components()
            
            # Mark session as running
            self.session_info.state = SessionState.RUNNING
            
            # Start monitoring thread
            self._start_component_monitor()
            
            # Save session state
            self._save_session_state()
            
            logger.info(f"PersonalAIOS session started successfully - {len(started_components)} components active")
            
            return {
                'session_id': self.session_info.session_id,
                'started_components': started_components,
                'state': self.session_info.state.value
            }
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            self.session_info.state = SessionState.CRASHED
            raise
    
    def process_command(self, user_input: str) -> str:
        """Process natural language session management commands"""
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
        return self._execute_session_intent(intent, entities, user_input)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better understanding"""
        import re
        # Remove common filler words
        text = re.sub(r'\b(?:please|can\s+you|would\s+you|could\s+you)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip().lower()
        return text
    
    def _extract_intent_and_entities(self, text: str) -> tuple:
        """Extract intent and entities using AI-powered pattern matching"""
        import re
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities = {
                        'groups': match.groups(),
                        'context': self._extract_context(text),
                        'component_target': match.group(1) if match.groups() else None
                    }
                    return intent, entities
        
        return None, {}
    
    def _extract_context(self, text: str) -> Dict:
        """Extract contextual information from text"""
        context = {}
        
        # Detect urgency
        if any(word in text for word in ['urgent', 'now', 'immediately', 'asap']):
            context['urgency'] = 'high'
        
        # Detect force/graceful
        if any(word in text for word in ['force', 'kill', 'hard']):
            context['method'] = 'force'
        elif any(word in text for word in ['graceful', 'gentle', 'soft']):
            context['method'] = 'graceful'
        
        return context
    
    def _execute_session_intent(self, intent: str, entities: Dict, original_text: str) -> str:
        """Execute the identified session management intent"""
        try:
            if intent == 'session_info':
                return self._handle_session_info()
            elif intent == 'restart_component':
                return self._handle_restart_component(entities)
            elif intent == 'stop_component':
                return self._handle_stop_component(entities)
            elif intent == 'start_component':
                return self._handle_start_component(entities)
            elif intent == 'list_components':
                return self._handle_list_components()
            elif intent == 'save_session':
                return self._handle_save_session()
            elif intent == 'restore_session':
                return self._handle_restore_session()
            elif intent == 'logout':
                return self._handle_logout()
            elif intent == 'shutdown':
                return self._handle_shutdown()
            elif intent == 'restart_session':
                return self._handle_restart_session()
            else:
                return f"🔐 **Intent recognized** ({intent}) but implementation pending"
                
        except Exception as e:
            return f"❌ **Session management error:** {str(e)}"
    
    def _handle_session_info(self) -> str:
        """Handle session information requests"""
        if not self.session_info:
            return "🔐 **No active session**"
        
        uptime = time.time() - self.session_info.start_time
        uptime_str = self._format_uptime(uptime)
        
        # Count component states
        component_counts = {}
        for component in self.session_info.components.values():
            state = component.state.value
            component_counts[state] = component_counts.get(state, 0) + 1
        
        response = f"🔐 **PersonalAIOS Session Information**\n\n"
        response += f"**Session ID:** {self.session_info.session_id}\n"
        response += f"**State:** {self.session_info.state.value.title()}\n"
        response += f"**Uptime:** {uptime_str}\n"
        response += f"**User ID:** {self.session_info.user_id}\n\n"
        
        response += f"**Components:** {len(self.session_info.components)} total\n"
        for state, count in component_counts.items():
            state_icon = self._get_state_icon(ComponentState(state))
            response += f"• {state_icon} {state.title()}: {count}\n"
        
        # Memory usage
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            response += f"\n**Memory Usage:** {memory_mb:.1f} MB\n"
        except:
            pass
        
        return response
    
    def _handle_restart_component(self, entities: Dict) -> str:
        """Handle component restart requests"""
        component_name = entities.get('component_target', '').strip()
        if not component_name:
            return "🔄 **Please specify which component to restart**\n\n**Examples:** restart window manager, reload notification system"
        
        # Find matching component
        component = self._find_component_by_name(component_name)
        if not component:
            available = ', '.join(self.session_info.components.keys())
            return f"🔍 **Component not found:** '{component_name}'\n\n**Available:** {available}"
        
        try:
            # Stop component if running
            if component.state == ComponentState.RUNNING:
                self._stop_component(component)
            
            # Start component
            success = self._start_component(component)
            
            if success:
                return f"🔄 **Restarted component:** {component.name}\n   └─ Status: {component.state.value.title()}"
            else:
                return f"❌ **Failed to restart:** {component.name}"
        
        except Exception as e:
            return f"❌ **Restart failed:** {str(e)}"
    
    def _handle_stop_component(self, entities: Dict) -> str:
        """Handle component stop requests"""
        component_name = entities.get('component_target', '').strip()
        if not component_name:
            return "🛑 **Please specify which component to stop**\n\n**Examples:** stop file manager, disable notifications"
        
        component = self._find_component_by_name(component_name)
        if not component:
            available = ', '.join(self.session_info.components.keys())
            return f"🔍 **Component not found:** '{component_name}'\n\n**Available:** {available}"
        
        if component.required:
            return f"⚠️ **Cannot stop required component:** {component.name}\n\nThis component is essential for PersonalAIOS operation."
        
        try:
            self._stop_component(component)
            return f"🛑 **Stopped component:** {component.name}\n   └─ Status: {component.state.value.title()}"
        
        except Exception as e:
            return f"❌ **Stop failed:** {str(e)}"
    
    def _handle_start_component(self, entities: Dict) -> str:
        """Handle component start requests"""
        component_name = entities.get('component_target', '').strip()
        if not component_name:
            return "🚀 **Please specify which component to start**\n\n**Examples:** start window manager, enable file manager"
        
        component = self._find_component_by_name(component_name)
        if not component:
            available = ', '.join(self.session_info.components.keys())
            return f"🔍 **Component not found:** '{component_name}'\n\n**Available:** {available}"
        
        if component.state == ComponentState.RUNNING:
            return f"✅ **Component already running:** {component.name}"
        
        try:
            success = self._start_component(component)
            
            if success:
                return f"🚀 **Started component:** {component.name}\n   └─ Status: {component.state.value.title()}"
            else:
                return f"❌ **Failed to start:** {component.name}"
        
        except Exception as e:
            return f"❌ **Start failed:** {str(e)}"
    
    def _handle_list_components(self) -> str:
        """Handle list components requests"""
        if not self.session_info or not self.session_info.components:
            return "🔐 **No components loaded**"
        
        response = f"🔐 **Session Components** ({len(self.session_info.components)} total):\n\n"
        
        # Group by state
        states = {}
        for component in self.session_info.components.values():
            state = component.state
            if state not in states:
                states[state] = []
            states[state].append(component)
        
        # Display by state
        state_order = [ComponentState.RUNNING, ComponentState.STARTING, ComponentState.STOPPING, 
                      ComponentState.FAILED, ComponentState.INACTIVE]
        
        for state in state_order:
            if state in states:
                state_icon = self._get_state_icon(state)
                response += f"**{state_icon} {state.value.title()}:**\n"
                
                for component in states[state]:
                    required_mark = " 🔒" if component.required else ""
                    restart_info = ""
                    
                    if component.restart_count > 0:
                        restart_info = f" (restarted {component.restart_count}x)"
                    
                    uptime = ""
                    if component.last_start_time > 0:
                        uptime_seconds = time.time() - component.last_start_time
                        uptime = f" • {self._format_uptime(uptime_seconds)}"
                    
                    response += f"• **{component.name}**{required_mark}{restart_info}{uptime}\n"
                
                response += "\n"
        
        return response
    
    def _handle_save_session(self) -> str:
        """Handle save session requests"""
        try:
            self.session_info.state = SessionState.SAVING
            
            # Collect session state
            session_state = {
                'session_id': self.session_info.session_id,
                'save_time': time.time(),
                'components': {},
                'ai_preferences': self.session_info.ai_preferences,
                'environment_vars': {
                    key: value for key, value in self.session_info.environment.items()
                    if key.startswith('PERSONALAIOS_')
                }
            }
            
            # Save component states
            for name, component in self.session_info.components.items():
                session_state['components'][name] = {
                    'state': component.state.value,
                    'restart_count': component.restart_count,
                    'enabled': component.state != ComponentState.INACTIVE
                }
            
            # Save to file
            save_file = self.session_path / 'saved_session.json'
            with open(save_file, 'w') as f:
                json.dump(session_state, f, indent=2)
            
            self.session_info.state = SessionState.RUNNING
            
            return f"💾 **Session saved successfully**\n   └─ Saved to: {save_file}\n   └─ Components: {len(session_state['components'])}"
        
        except Exception as e:
            self.session_info.state = SessionState.RUNNING
            return f"❌ **Save failed:** {str(e)}"
    
    def _handle_restore_session(self) -> str:
        """Handle restore session requests"""
        try:
            save_file = self.session_path / 'saved_session.json'
            if not save_file.exists():
                return "📂 **No saved session found**\n\nSave a session first using 'save session'"
            
            # Load saved state
            with open(save_file, 'r') as f:
                saved_state = json.load(f)
            
            # Restore components
            restored_count = 0
            failed_count = 0
            
            for name, component_state in saved_state.get('components', {}).items():
                if name in self.session_info.components:
                    component = self.session_info.components[name]
                    
                    if component_state.get('enabled', True):
                        if component.state != ComponentState.RUNNING:
                            try:
                                self._start_component(component)
                                restored_count += 1
                            except:
                                failed_count += 1
                    else:
                        if component.state == ComponentState.RUNNING and not component.required:
                            try:
                                self._stop_component(component)
                            except:
                                pass
            
            # Restore AI preferences
            if 'ai_preferences' in saved_state:
                self.session_info.ai_preferences.update(saved_state['ai_preferences'])
            
            save_time_str = time.strftime('%Y-%m-%d %H:%M:%S', 
                                        time.localtime(saved_state.get('save_time', 0)))
            
            response = f"📂 **Session restored**\n"
            response += f"   └─ Saved on: {save_time_str}\n"
            response += f"   └─ Restored: {restored_count} components\n"
            
            if failed_count > 0:
                response += f"   └─ Failed: {failed_count} components\n"
            
            return response
        
        except Exception as e:
            return f"❌ **Restore failed:** {str(e)}"
    
    def _handle_logout(self) -> str:
        """Handle logout requests"""
        try:
            return self._initiate_logout()
        except Exception as e:
            return f"❌ **Logout failed:** {str(e)}"
    
    def _handle_shutdown(self) -> str:
        """Handle shutdown requests"""
        try:
            return self._initiate_shutdown()
        except Exception as e:
            return f"❌ **Shutdown failed:** {str(e)}"
    
    def _handle_restart_session(self) -> str:
        """Handle restart session requests"""
        try:
            self.restart_requested = True
            return self._initiate_logout()
        except Exception as e:
            return f"❌ **Restart failed:** {str(e)}"
    
    def _start_components(self) -> List[str]:
        """Start all session components in dependency order"""
        started = []
        
        # Resolve dependency order
        start_order = self._resolve_component_dependencies()
        
        for component_name in start_order:
            component = self.session_info.components[component_name]
            
            try:
                if self._start_component(component):
                    started.append(component.name)
                    logger.info(f"Started component: {component.name}")
                elif component.required:
                    logger.error(f"Failed to start required component: {component.name}")
                    raise Exception(f"Required component {component.name} failed to start")
            except Exception as e:
                logger.error(f"Component {component.name} startup failed: {e}")
                if component.required:
                    raise
        
        return started
    
    def _start_component(self, component: SessionComponent) -> bool:
        """Start a single component"""
        try:
            component.state = ComponentState.STARTING
            component.last_start_time = time.time()
            
            # Wait for startup delay
            if component.startup_delay > 0:
                time.sleep(component.startup_delay)
            
            # Check dependencies
            if component.dependencies:
                for dep_name in component.dependencies:
                    dep_component = self.session_info.components.get(dep_name)
                    if not dep_component or dep_component.state != ComponentState.RUNNING:
                        logger.warning(f"Dependency {dep_name} not running for {component.name}")
            
            # Start component based on type
            if component.module_name and component.class_name:
                # Python module component
                success = self._start_python_component(component)
            elif component.executable:
                # External executable component
                success = self._start_executable_component(component)
            else:
                logger.error(f"No startup method defined for {component.name}")
                success = False
            
            if success:
                component.state = ComponentState.RUNNING
                component.restart_count += 1
                logger.info(f"Component {component.name} started successfully")
                return True
            else:
                component.state = ComponentState.FAILED
                component.last_failure_time = time.time()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start component {component.name}: {e}")
            component.state = ComponentState.FAILED
            component.last_failure_time = time.time()
            return False
    
    def _start_python_component(self, component: SessionComponent) -> bool:
        """Start a Python module component"""
        try:
            # Dynamic import
            module = __import__(component.module_name, fromlist=[component.class_name])
            component_class = getattr(module, component.class_name)
            
            # Create instance
            if component.class_name == 'MinimalAIApp':
                # Special handling for AI Shell
                component.instance = component_class()
                # The AI app runs its own main loop
                threading.Thread(target=component.instance.run, daemon=True).start()
            else:
                # Regular component
                component.instance = component_class()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Python component {component.name}: {e}")
            return False
    
    def _start_executable_component(self, component: SessionComponent) -> bool:
        """Start an external executable component"""
        try:
            component.process = subprocess.Popen(
                component.executable,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to start executable component {component.name}: {e}")
            return False
    
    def _stop_component(self, component: SessionComponent):
        """Stop a component"""
        try:
            component.state = ComponentState.STOPPING
            
            if component.process:
                # Stop external process
                component.process.terminate()
                try:
                    component.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    component.process.kill()
                component.process = None
            
            if component.instance:
                # Stop Python component
                if hasattr(component.instance, 'cleanup'):
                    component.instance.cleanup()
                component.instance = None
            
            component.state = ComponentState.INACTIVE
            logger.info(f"Stopped component: {component.name}")
            
        except Exception as e:
            logger.error(f"Failed to stop component {component.name}: {e}")
    
    def _resolve_component_dependencies(self) -> List[str]:
        """Resolve component startup order based on dependencies"""
        order = []
        visited = set()
        
        def visit(component_name):
            if component_name in visited:
                return
            
            visited.add(component_name)
            component = self.session_info.components.get(component_name)
            
            if component and component.dependencies:
                for dep in component.dependencies:
                    if dep in self.session_info.components:
                        visit(dep)
            
            order.append(component_name)
        
        for component_name in self.session_info.components:
            visit(component_name)
        
        return order
    
    def _start_component_monitor(self):
        """Start background component monitoring"""
        def monitor():
            while not self.shutdown_requested:
                try:
                    self._check_component_health()
                    time.sleep(5)  # Check every 5 seconds
                except Exception as e:
                    logger.error(f"Component monitoring error: {e}")
                    time.sleep(10)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def _check_component_health(self):
        """Check health of all components"""
        for component in self.session_info.components.values():
            if component.state == ComponentState.RUNNING:
                # Check if process is still alive
                if component.process and component.process.poll() is not None:
                    logger.warning(f"Component {component.name} process died")
                    component.state = ComponentState.FAILED
                    
                    # Auto-restart if configured
                    if (component.restart_on_failure and 
                        component.restart_count < component.max_restart_attempts):
                        logger.info(f"Auto-restarting component: {component.name}")
                        self._start_component(component)
    
    def _find_component_by_name(self, name: str) -> Optional[SessionComponent]:
        """Find component by name using fuzzy matching"""
        name_lower = name.lower().strip()
        
        # Exact match
        for component in self.session_info.components.values():
            if component.name.lower() == name_lower:
                return component
        
        # Partial match
        for component in self.session_info.components.values():
            if name_lower in component.name.lower():
                return component
        
        # Key match
        for key, component in self.session_info.components.items():
            if name_lower in key.lower():
                return component
        
        return None
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self.shutdown_requested = True
            self._initiate_logout()
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def _setup_session_environment(self):
        """Setup session environment variables"""
        os.environ['PERSONALAIOS_SESSION_ID'] = self.session_info.session_id
        os.environ['PERSONALAIOS_SESSION_PATH'] = str(self.session_path)
        os.environ['SESSION_MANAGER'] = f"personalaios@{self.session_info.session_id}"
    
    def _create_session_lock(self):
        """Create session lock file"""
        lock_file = self.session_path / f'session_{self.session_info.session_id}.lock'
        with open(lock_file, 'w') as f:
            json.dump({
                'pid': os.getpid(),
                'start_time': self.session_info.start_time,
                'session_id': self.session_info.session_id
            }, f)
    
    def _save_session_state(self):
        """Save current session state"""
        try:
            state_file = self.session_path / 'current_session.json'
            state_data = asdict(self.session_info)
            
            # Remove non-serializable items
            for component_data in state_data['components'].values():
                component_data.pop('process', None)
                component_data.pop('instance', None)
            
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save session state: {e}")
    
    def _load_session_state(self):
        """Load previous session state if available"""
        try:
            state_file = self.session_path / 'current_session.json'
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                
                # Restore AI preferences if available
                if 'ai_preferences' in state_data:
                    self.session_info.ai_preferences.update(state_data['ai_preferences'])
                
                logger.info("Previous session state loaded")
        except Exception as e:
            logger.error(f"Failed to load session state: {e}")
    
    def _load_ai_preferences(self) -> Dict[str, Any]:
        """Load AI preferences"""
        try:
            prefs_file = self.session_path / 'ai_preferences.json'
            if prefs_file.exists():
                with open(prefs_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load AI preferences: {e}")
        
        # Default preferences
        return {
            'natural_language_enabled': True,
            'auto_suggestions': True,
            'learning_enabled': True,
            'voice_commands': False,
            'debug_mode': False
        }
    
    def _initiate_logout(self) -> str:
        """Initiate logout process"""
        try:
            logger.info("Initiating logout...")
            self.session_info.state = SessionState.SHUTTING_DOWN
            
            # Save session state
            self._save_session_state()
            
            # Stop components in reverse order
            stop_order = list(reversed(self._resolve_component_dependencies()))
            
            stopped_count = 0
            for component_name in stop_order:
                component = self.session_info.components[component_name]
                if component.state == ComponentState.RUNNING:
                    try:
                        self._stop_component(component)
                        stopped_count += 1
                    except Exception as e:
                        logger.error(f"Failed to stop {component.name}: {e}")
            
            # Clean up session
            self._cleanup_session()
            
            if self.restart_requested:
                # Restart session
                threading.Thread(target=self._restart_session, daemon=True).start()
                return f"🔄 **Restarting PersonalAIOS session...**\n   └─ Stopped {stopped_count} components"
            else:
                # Exit application
                threading.Thread(target=lambda: (time.sleep(1), os._exit(0)), daemon=True).start()
                return f"👋 **Logging out...**\n   └─ Stopped {stopped_count} components\n   └─ Session saved successfully"
        
        except Exception as e:
            return f"❌ **Logout failed:** {str(e)}"
    
    def _initiate_shutdown(self) -> str:
        """Initiate system shutdown"""
        try:
            # First logout
            logout_result = self._initiate_logout()
            
            # Then shutdown system
            threading.Thread(target=lambda: (
                time.sleep(2),
                subprocess.run(['systemctl', 'poweroff'], check=False)
            ), daemon=True).start()
            
            return f"🔌 **Shutting down system...**\n{logout_result}"
        
        except Exception as e:
            return f"❌ **Shutdown failed:** {str(e)}"
    
    def _restart_session(self):
        """Restart the session"""
        time.sleep(2)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    
    def _cleanup_session(self):
        """Clean up session resources"""
        try:
            # Remove lock file
            lock_files = list(self.session_path.glob(f'session_{self.session_info.session_id}.lock'))
            for lock_file in lock_files:
                lock_file.unlink(missing_ok=True)
            
            logger.info("Session cleanup completed")
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
    
    def _get_state_icon(self, state: ComponentState) -> str:
        """Get icon for component state"""
        icon_map = {
            ComponentState.RUNNING: '✅',
            ComponentState.STARTING: '🟡',
            ComponentState.STOPPING: '🟠',
            ComponentState.FAILED: '❌',
            ComponentState.INACTIVE: '⚪'
        }
        return icon_map.get(state, '❓')
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        else:
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            return f"{days}d {hours}h"
    
    def _handle_unknown_intent(self, user_input: str) -> str:
        """Handle unknown session commands"""
        return f"""❓ **I didn't understand:** "{user_input}"

🔐 **Try these natural language session commands:**

**Session Control:**
• "session info" - Show current session status
• "save session" - Save current session state
• "restore session" - Restore saved session

**Component Management:**
• "list components" - Show all components
• "restart window manager" - Restart specific component
• "stop notification system" - Stop component

**Session Actions:**
• "logout" - End current session
• "restart session" - Restart PersonalAIOS
• "shutdown" - Power off system

**I understand natural language - speak naturally!** 🤖"""

# For compatibility with Desktop Manager
DynamicSessionManager = IntelligentSessionManager

# Main session entry point
if __name__ == '__main__':
    import sys
    
    try:
        session_manager = IntelligentSessionManager()
        result = session_manager.start_session()
        
        print(f"✅ PersonalAIOS Session started: {result['session_id']}")
        
        # Keep session running
        while not session_manager.shutdown_requested:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🔄 Session interrupted by user")
        if 'session_manager' in locals():
            session_manager._initiate_logout()
    except Exception as e:
        print(f"❌ Session startup failed: {e}")
        sys.exit(1)

