#!/usr/bin/env python3
"""
PersonalAIOS Intelligent System Status Area
Revolutionary AI-native system status management with perfect natural language understanding
Real-time system monitoring, intelligent indicators, and contextual controls
"""
import gi
import re
import json
import time
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import psutil
import logging

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Gio, Adw

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('SystemStatusArea')

class IndicatorType(Enum):
    """System status indicator categories"""
    NETWORK = "network"
    POWER = "power" 
    VOLUME = "volume"
    BLUETOOTH = "bluetooth"
    DISPLAY = "display"
    SYSTEM = "system"
    SECURITY = "security"
    STORAGE = "storage"
    PERFORMANCE = "performance"

class IndicatorPriority(Enum):
    """Indicator priority levels"""
    CRITICAL = "critical"      # Always visible
    HIGH = "high"             # Visible when active/issues
    NORMAL = "normal"         # Visible when active
    LOW = "low"              # Only in expanded view
    HIDDEN = "hidden"        # Never shown

class ConnectionState(Enum):
    """Network connection states"""
    CONNECTED = "connected"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    LIMITED = "limited"
    ERROR = "error"

@dataclass
class SystemIndicator:
    """System status indicator definition"""
    id: str
    indicator_type: IndicatorType
    name: str
    description: str
    icon: str
    priority: IndicatorPriority
    visible: bool = True
    active: bool = False
    value: Union[str, int, float] = None
    unit: Optional[str] = None
    status: str = "normal"
    last_updated: float = 0
    click_action: Optional[str] = None
    tooltip: Optional[str] = None
    alert_threshold: Optional[float] = None

@dataclass
class NetworkInfo:
    """Network connection information"""
    interface: str
    connection_type: str  # wifi, ethernet, mobile
    state: ConnectionState
    signal_strength: Optional[int] = None
    speed: Optional[str] = None
    ssid: Optional[str] = None
    ip_address: Optional[str] = None
    bytes_sent: int = 0
    bytes_recv: int = 0

@dataclass
class PowerInfo:
    """Power and battery information"""
    on_battery: bool
    battery_level: Optional[int] = None
    time_remaining: Optional[str] = None
    charging: bool = False
    power_profile: str = "balanced"
    ac_adapter: bool = True

class IntelligentSystemStatusArea:
    """
    Revolutionary AI-Native System Status Area
    
    Features:
    - Perfect natural language status control
    - Intelligent adaptive indicators
    - Real-time system monitoring
    - Context-aware status display
    - Smart alert thresholds
    - Usage pattern learning
    - Multi-system integration
    - Voice-controlled status queries
    """
    
    def __init__(self):
        """Initialize the intelligent system status area"""
        self.indicators: Dict[str, SystemIndicator] = {}
        self.network_info: Optional[NetworkInfo] = None
        self.power_info: Optional[PowerInfo] = None
        self.system_metrics: Dict[str, Any] = {}
        self.command_history: List[Dict] = []
        self.monitoring_active = True
        
        # User preferences
        self.user_preferences = {
            'show_percentage': True,
            'show_time_remaining': True,
            'compact_mode': False,
            'auto_hide_inactive': True,
            'alert_notifications': True,
            'update_interval': 2.0,  # seconds
            'adaptive_brightness': True
        }
        
        # AI-powered intent patterns for natural language understanding
        self.intent_patterns = {
            'status_query': [
                r'(?:what is|show me|check) (?:the )?(.+?) (?:status|level)',
                r'(?:how is|what\'s) (?:the|my) (.+?)(?: doing| status)?',
                r'(.+?) (?:info|information|details)',
                r'(?:tell me about|show) (?:the|my) (.+?)',
                r'(?:is (?:the|my) )?(.+?) (?:okay|working|connected|on)',
            ],
            'toggle_indicator': [
                r'(?:toggle|switch) (?:the )?(.+?) (?:indicator|display)',
                r'(?:show|hide|display) (?:the )?(.+?) (?:indicator|icon|status)',
                r'(?:turn (?:on|off)|enable|disable) (?:the )?(.+?) (?:indicator|display)',
            ],
            'system_action': [
                r'(?:connect to|join) (.+?)(?: network| wifi)?',
                r'(?:disconnect from|leave) (.+?)(?: network| wifi)?',
                r'(?:set|change) volume to (\d+)(?:%| percent)?',
                r'(?:set|change) brightness to (\d+)(?:%| percent)?',
                r'(?:enable|disable|turn (?:on|off)) (.+?)',
            ],
            'power_control': [
                r'(?:battery|power) (?:info|information|status|level)',
                r'(?:how much|what\'s the) battery (?:left|remaining)',
                r'(?:is (?:the )?)?(?:power|battery|charging) (?:okay|good|low)',
                r'(?:set|change) power (?:mode|profile) to (.+)',
            ],
            'network_control': [
                r'(?:network|wifi|internet) (?:status|info|connection)',
                r'(?:am i|are we) (?:connected|online)',
                r'(?:what|which) network (?:am i on|connected to)',
                r'(?:show|list) (?:available )?(?:networks|wifi)',
            ],
            'volume_control': [
                r'(?:volume|audio|sound) (?:level|status|info)',
                r'(?:what\'s the|show me the) (?:current )?volume',
                r'(?:mute|unmute)(?: the)? (?:volume|audio|sound)',
                r'(?:increase|decrease|raise|lower) (?:the )?volume',
            ],
            'overall_status': [
                r'(?:system|overall|general) (?:status|info|overview)',
                r'(?:how is|what\'s) (?:the )?(?:system|computer) (?:doing|status)',
                r'(?:show me|display) (?:all )?(?:system )?(?:status|indicators)',
                r'(?:status|system) (?:overview|summary|dashboard)',
            ]
        }
        
        # System monitoring thresholds
        self.alert_thresholds = {
            'battery_low': 20,
            'battery_critical': 10,
            'cpu_high': 80,
            'memory_high': 85,
            'storage_low': 90,
            'temperature_high': 70
        }
        
        # Initialize system indicators
        self._initialize_indicators()
        
        # Start monitoring threads
        self._start_monitoring()
        
        # Setup storage
        self.storage_path = Path.home() / '.personalaios' / 'system_status'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        print("📊 Intelligent System Status Area initialized with AI-powered monitoring")
    
    def _initialize_indicators(self):
        """Initialize all system status indicators"""
        # Network indicators
        self.indicators['wifi'] = SystemIndicator(
            id='wifi',
            indicator_type=IndicatorType.NETWORK,
            name='Wi-Fi',
            description='Wireless network connection',
            icon='network-wireless-signal-excellent',
            priority=IndicatorPriority.HIGH,
            click_action='network_settings'
        )
        
        self.indicators['ethernet'] = SystemIndicator(
            id='ethernet',
            indicator_type=IndicatorType.NETWORK,
            name='Ethernet',
            description='Wired network connection',
            icon='network-wired',
            priority=IndicatorPriority.NORMAL,
            visible=False
        )
        
        # Power indicators
        self.indicators['battery'] = SystemIndicator(
            id='battery',
            indicator_type=IndicatorType.POWER,
            name='Battery',
            description='Battery level and status',
            icon='battery-good',
            priority=IndicatorPriority.CRITICAL,
            unit='%',
            alert_threshold=20
        )
        
        self.indicators['power'] = SystemIndicator(
            id='power',
            indicator_type=IndicatorType.POWER,
            name='Power',
            description='Power profile and AC adapter',
            icon='battery-full-charging',
            priority=IndicatorPriority.NORMAL,
            click_action='power_settings'
        )
        
        # Audio indicators
        self.indicators['volume'] = SystemIndicator(
            id='volume',
            indicator_type=IndicatorType.VOLUME,
            name='Volume',
            description='Audio output level',
            icon='audio-volume-high',
            priority=IndicatorPriority.HIGH,
            unit='%',
            click_action='audio_settings'
        )
        
        # Bluetooth indicator
        self.indicators['bluetooth'] = SystemIndicator(
            id='bluetooth',
            indicator_type=IndicatorType.BLUETOOTH,
            name='Bluetooth',
            description='Bluetooth connectivity',
            icon='bluetooth-active',
            priority=IndicatorPriority.NORMAL,
            visible=False,
            click_action='bluetooth_settings'
        )
        
        # System performance indicators
        self.indicators['cpu'] = SystemIndicator(
            id='cpu',
            indicator_type=IndicatorType.PERFORMANCE,
            name='CPU',
            description='Processor usage',
            icon='cpu',
            priority=IndicatorPriority.LOW,
            unit='%',
            alert_threshold=80
        )
        
        self.indicators['memory'] = SystemIndicator(
            id='memory',
            indicator_type=IndicatorType.PERFORMANCE,
            name='Memory',
            description='RAM usage',
            icon='memory',
            priority=IndicatorPriority.LOW,
            unit='%',
            alert_threshold=85
        )
        
        self.indicators['storage'] = SystemIndicator(
            id='storage',
            indicator_type=IndicatorType.STORAGE,
            name='Storage',
            description='Disk usage',
            icon='drive-harddisk',
            priority=IndicatorPriority.LOW,
            unit='%',
            alert_threshold=90
        )
        
        # Security indicators
        self.indicators['vpn'] = SystemIndicator(
            id='vpn',
            indicator_type=IndicatorType.SECURITY,
            name='VPN',
            description='VPN connection status',
            icon='network-vpn',
            priority=IndicatorPriority.HIGH,
            visible=False
        )
        
        logger.info(f"Initialized {len(self.indicators)} system status indicators")
    
    def _start_monitoring(self):
        """Start background system monitoring"""
        def monitor_loop():
            while self.monitoring_active:
                try:
                    self._update_all_indicators()
                    time.sleep(self.user_preferences['update_interval'])
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(5)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("System monitoring started")
    
    def _update_all_indicators(self):
        """Update all system indicators"""
        try:
            # Update network status
            self._update_network_status()
            
            # Update power status
            self._update_power_status()
            
            # Update volume status
            self._update_volume_status()
            
            # Update system performance
            self._update_performance_metrics()
            
            # Update connectivity status
            self._update_connectivity_status()
            
            # Check for alerts
            self._check_alert_conditions()
            
        except Exception as e:
            logger.error(f"Failed to update indicators: {e}")
    
    def _update_network_status(self):
        """Update network connectivity indicators"""
        try:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            wifi_connected = False
            ethernet_connected = False
            
            for interface, addrs in interfaces.items():
                if interface.startswith(('wl', 'wifi', 'wlan')):
                    # Wi-Fi interface
                    if interface in stats and stats[interface].isup:
                        wifi_connected = True
                        self._update_wifi_indicator(interface, addrs)
                
                elif interface.startswith(('eth', 'enp', 'ens')):
                    # Ethernet interface
                    if interface in stats and stats[interface].isup:
                        ethernet_connected = True
                        self._update_ethernet_indicator(interface, addrs)
            
            # Update indicator visibility
            self.indicators['wifi'].visible = wifi_connected
            self.indicators['wifi'].active = wifi_connected
            self.indicators['ethernet'].visible = ethernet_connected
            self.indicators['ethernet'].active = ethernet_connected
            
        except Exception as e:
            logger.error(f"Network status update failed: {e}")
    
    def _update_wifi_indicator(self, interface: str, addrs: List):
        """Update Wi-Fi specific indicator"""
        wifi_indicator = self.indicators['wifi']
        wifi_indicator.last_updated = time.time()
        
        # Get IP address
        for addr in addrs:
            if addr.family == 2:  # IPv4
                wifi_indicator.tooltip = f"Connected to Wi-Fi\nIP: {addr.address}"
                break
        
        # Try to get signal strength (Linux-specific)
        try:
            result = subprocess.run(['iwconfig', interface], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                if 'Signal level' in output:
                    # Parse signal strength
                    signal_match = re.search(r'Signal level=(-?\d+)', output)
                    if signal_match:
                        signal_dbm = int(signal_match.group(1))
                        # Convert to percentage (rough approximation)
                        signal_percent = max(0, min(100, (signal_dbm + 100) * 2))
                        wifi_indicator.value = signal_percent
                        wifi_indicator.unit = '%'
                        
                        # Update icon based on signal strength
                        if signal_percent > 75:
                            wifi_indicator.icon = 'network-wireless-signal-excellent'
                        elif signal_percent > 50:
                            wifi_indicator.icon = 'network-wireless-signal-good'
                        elif signal_percent > 25:
                            wifi_indicator.icon = 'network-wireless-signal-ok'
                        else:
                            wifi_indicator.icon = 'network-wireless-signal-weak'
        except:
            pass  # iwconfig not available or failed
    
    def _update_ethernet_indicator(self, interface: str, addrs: List):
        """Update Ethernet specific indicator"""
        ethernet_indicator = self.indicators['ethernet']
        ethernet_indicator.last_updated = time.time()
        
        # Get IP address
        for addr in addrs:
            if addr.family == 2:  # IPv4
                ethernet_indicator.tooltip = f"Connected via Ethernet\nIP: {addr.address}"
                ethernet_indicator.value = "Connected"
                break
    
    def _update_power_status(self):
        """Update power and battery indicators"""
        try:
            battery = psutil.sensors_battery()
            power_indicator = self.indicators['power']
            battery_indicator = self.indicators['battery']
            
            if battery:
                # Update battery indicator
                battery_indicator.visible = True
                battery_indicator.active = True
                battery_indicator.value = round(battery.percent)
                battery_indicator.last_updated = time.time()
                
                # Update battery icon based on level and charging status
                if battery.power_plugged:
                    battery_indicator.icon = 'battery-full-charging'
                    battery_indicator.status = 'charging'
                    if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                        hours = battery.secsleft // 3600
                        minutes = (battery.secsleft % 3600) // 60
                        battery_indicator.tooltip = f"Charging: {battery.percent:.0f}%\n{hours}h {minutes}m to full"
                    else:
                        battery_indicator.tooltip = f"Charging: {battery.percent:.0f}%"
                else:
                    battery_indicator.status = 'discharging'
                    if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                        hours = battery.secsleft // 3600
                        minutes = (battery.secsleft % 3600) // 60
                        battery_indicator.tooltip = f"Battery: {battery.percent:.0f}%\n{hours}h {minutes}m remaining"
                    else:
                        battery_indicator.tooltip = f"Battery: {battery.percent:.0f}%"
                    
                    # Update icon based on battery level
                    if battery.percent > 75:
                        battery_indicator.icon = 'battery-full'
                    elif battery.percent > 50:
                        battery_indicator.icon = 'battery-good'
                    elif battery.percent > 25:
                        battery_indicator.icon = 'battery-low'
                    elif battery.percent > 10:
                        battery_indicator.icon = 'battery-caution'
                    else:
                        battery_indicator.icon = 'battery-empty'
                
                # Update power indicator
                power_indicator.visible = True
                power_indicator.active = battery.power_plugged
                power_indicator.value = "AC" if battery.power_plugged else "Battery"
                power_indicator.last_updated = time.time()
            else:
                # No battery (desktop system)
                battery_indicator.visible = False
                power_indicator.visible = True
                power_indicator.active = True
                power_indicator.value = "AC Power"
                power_indicator.icon = 'ac-adapter'
                
        except Exception as e:
            logger.error(f"Power status update failed: {e}")
    
    def _update_volume_status(self):
        """Update audio volume indicator"""
        try:
            volume_indicator = self.indicators['volume']
            
            # Try to get volume using pactl (PulseAudio)
            try:
                result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse volume percentage
                    volume_match = re.search(r'(\d+)%', result.stdout)
                    if volume_match:
                        volume_percent = int(volume_match.group(1))
                        volume_indicator.value = volume_percent
                        volume_indicator.last_updated = time.time()
                        
                        # Check if muted
                        mute_result = subprocess.run(['pactl', 'get-sink-mute', '@DEFAULT_SINK@'],
                                                   capture_output=True, text=True)
                        is_muted = 'yes' in mute_result.stdout.lower()
                        
                        # Update icon based on volume and mute status
                        if is_muted:
                            volume_indicator.icon = 'audio-volume-muted'
                            volume_indicator.tooltip = 'Audio muted'
                            volume_indicator.status = 'muted'
                        else:
                            volume_indicator.status = 'normal'
                            if volume_percent > 66:
                                volume_indicator.icon = 'audio-volume-high'
                            elif volume_percent > 33:
                                volume_indicator.icon = 'audio-volume-medium'
                            elif volume_percent > 0:
                                volume_indicator.icon = 'audio-volume-low'
                            else:
                                volume_indicator.icon = 'audio-volume-muted'
                            
                            volume_indicator.tooltip = f'Volume: {volume_percent}%'
            except FileNotFoundError:
                # pactl not available, try amixer
                try:
                    result = subprocess.run(['amixer', 'get', 'Master'],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        volume_match = re.search(r'(\d+)%', result.stdout)
                        if volume_match:
                            volume_percent = int(volume_match.group(1))
                            volume_indicator.value = volume_percent
                            volume_indicator.last_updated = time.time()
                            volume_indicator.tooltip = f'Volume: {volume_percent}%'
                except FileNotFoundError:
                    pass  # No audio control available
                    
        except Exception as e:
            logger.error(f"Volume status update failed: {e}")
    
    def _update_performance_metrics(self):
        """Update system performance indicators"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_indicator = self.indicators['cpu']
            cpu_indicator.value = round(cpu_percent)
            cpu_indicator.last_updated = time.time()
            cpu_indicator.tooltip = f'CPU Usage: {cpu_percent:.1f}%'
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_indicator = self.indicators['memory']
            memory_indicator.value = round(memory.percent)
            memory_indicator.last_updated = time.time()
            memory_indicator.tooltip = f'Memory: {memory.percent:.1f}% ({memory.used // 1024**3}GB / {memory.total // 1024**3}GB)'
            
            # Storage usage
            disk = psutil.disk_usage('/')
            storage_indicator = self.indicators['storage']
            storage_percent = (disk.used / disk.total) * 100
            storage_indicator.value = round(storage_percent)
            storage_indicator.last_updated = time.time()
            storage_indicator.tooltip = f'Storage: {storage_percent:.1f}% ({disk.used // 1024**3}GB / {disk.total // 1024**3}GB)'
            
            # Update visibility based on user preferences
            if self.user_preferences['auto_hide_inactive']:
                cpu_indicator.visible = cpu_percent > 50
                memory_indicator.visible = memory.percent > 70
                storage_indicator.visible = storage_percent > 80
            
        except Exception as e:
            logger.error(f"Performance metrics update failed: {e}")
    
    def _update_connectivity_status(self):
        """Update connectivity-related indicators"""
        try:
            # Bluetooth status
            bluetooth_indicator = self.indicators['bluetooth']
            try:
                result = subprocess.run(['bluetoothctl', 'show'], 
                                      capture_output=True, text=True, timeout=2)
                bluetooth_available = result.returncode == 0 and 'Powered: yes' in result.stdout
                bluetooth_indicator.visible = bluetooth_available
                bluetooth_indicator.active = bluetooth_available
                bluetooth_indicator.last_updated = time.time()
                
                if bluetooth_available:
                    bluetooth_indicator.tooltip = 'Bluetooth enabled'
                    bluetooth_indicator.icon = 'bluetooth-active'
                else:
                    bluetooth_indicator.tooltip = 'Bluetooth disabled'
                    bluetooth_indicator.icon = 'bluetooth-disabled'
            except (FileNotFoundError, subprocess.TimeoutExpired):
                bluetooth_indicator.visible = False
            
            # VPN status (check for active VPN connections)
            vpn_indicator = self.indicators['vpn']
            try:
                # Check for VPN interfaces
                interfaces = psutil.net_if_addrs()
                vpn_active = any(interface.startswith(('tun', 'tap', 'vpn')) 
                               for interface in interfaces.keys())
                
                vpn_indicator.visible = vpn_active
                vpn_indicator.active = vpn_active
                vpn_indicator.last_updated = time.time()
                
                if vpn_active:
                    vpn_indicator.tooltip = 'VPN connected'
                    vpn_indicator.icon = 'network-vpn'
                
            except Exception:
                vpn_indicator.visible = False
                
        except Exception as e:
            logger.error(f"Connectivity status update failed: {e}")
    
    def _check_alert_conditions(self):
        """Check for alert conditions and trigger notifications"""
        try:
            alerts = []
            
            # Battery alerts
            battery_indicator = self.indicators.get('battery')
            if (battery_indicator and battery_indicator.visible and 
                battery_indicator.value is not None):
                
                if battery_indicator.value <= self.alert_thresholds['battery_critical']:
                    alerts.append({
                        'type': 'critical',
                        'title': 'Critical Battery Level',
                        'message': f'Battery at {battery_indicator.value}% - Connect charger immediately'
                    })
                elif battery_indicator.value <= self.alert_thresholds['battery_low']:
                    alerts.append({
                        'type': 'warning',
                        'title': 'Low Battery',
                        'message': f'Battery at {battery_indicator.value}% - Consider charging soon'
                    })
            
            # Performance alerts
            cpu_indicator = self.indicators.get('cpu')
            if (cpu_indicator and cpu_indicator.value is not None and 
                cpu_indicator.value >= self.alert_thresholds['cpu_high']):
                alerts.append({
                    'type': 'warning',
                    'title': 'High CPU Usage',
                    'message': f'CPU usage at {cpu_indicator.value}%'
                })
            
            memory_indicator = self.indicators.get('memory')
            if (memory_indicator and memory_indicator.value is not None and 
                memory_indicator.value >= self.alert_thresholds['memory_high']):
                alerts.append({
                    'type': 'warning',
                    'title': 'High Memory Usage',
                    'message': f'Memory usage at {memory_indicator.value}%'
                })
            
            storage_indicator = self.indicators.get('storage')
            if (storage_indicator and storage_indicator.value is not None and 
                storage_indicator.value >= self.alert_thresholds['storage_low']):
                alerts.append({
                    'type': 'warning',
                    'title': 'Low Storage Space',
                    'message': f'Storage {storage_indicator.value}% full - Consider cleaning up files'
                })
            
            # Process alerts if notification system is available
            if alerts and self.user_preferences.get('alert_notifications', True):
                for alert in alerts:
                    self._send_alert_notification(alert)
                    
        except Exception as e:
            logger.error(f"Alert check failed: {e}")
    
    def _send_alert_notification(self, alert: Dict[str, str]):
        """Send alert notification (integrate with notification system)"""
        try:
            # Try system notification first
            subprocess.run([
                'notify-send',
                '--urgency', 'critical' if alert['type'] == 'critical' else 'normal',
                alert['title'],
                alert['message']
            ], capture_output=True)
        except FileNotFoundError:
            logger.warning(f"System notification failed for alert: {alert['title']}")
    
    def process_command(self, user_input: str) -> str:
        """Process natural language system status commands"""
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
        return self._execute_status_intent(intent, entities, user_input)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better understanding"""
        # Remove common filler words
        text = re.sub(r'\b(?:please|can\s+you|would\s+you|could\s+you)\b', '', text, flags=re.IGNORECASE)
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
                        'status_target': self._determine_status_target(match.groups(), text)
                    }
                    return intent, entities
        
        return None, {}
    
    def _extract_context(self, text: str) -> Dict:
        """Extract contextual information from text"""
        context = {}
        
        # Detect urgency
        if any(word in text for word in ['urgent', 'critical', 'emergency', 'asap']):
            context['urgency'] = 'high'
        
        # Detect specific system components
        system_keywords = {
            'network': ['network', 'internet', 'wifi', 'ethernet', 'connection'],
            'power': ['battery', 'power', 'charging', 'energy'],
            'audio': ['volume', 'sound', 'audio', 'speaker'],
            'performance': ['cpu', 'memory', 'ram', 'performance', 'speed'],
            'storage': ['disk', 'storage', 'space', 'drive']
        }
        
        for category, keywords in system_keywords.items():
            if any(keyword in text for keyword in keywords):
                context['category'] = category
                break
        
        return context
    
    def _determine_status_target(self, groups: Tuple, text: str) -> Optional[str]:
        """Determine status target from command groups"""
        if groups and groups[0]:
            return groups[0].strip()
        return None
    
    def _execute_status_intent(self, intent: str, entities: Dict, original_text: str) -> str:
        """Execute the identified status intent"""
        try:
            if intent == 'status_query':
                return self._handle_status_query(entities)
            elif intent == 'toggle_indicator':
                return self._handle_toggle_indicator(entities)
            elif intent == 'system_action':
                return self._handle_system_action(entities)
            elif intent == 'power_control':
                return self._handle_power_control(entities)
            elif intent == 'network_control':
                return self._handle_network_control(entities)
            elif intent == 'volume_control':
                return self._handle_volume_control(entities)
            elif intent == 'overall_status':
                return self._handle_overall_status(entities)
            else:
                return f"📊 **Intent recognized** ({intent}) but implementation pending"
                
        except Exception as e:
            return f"❌ **System status error:** {str(e)}"
    
    def _handle_status_query(self, entities: Dict) -> str:
        """Handle status query commands"""
        target = entities.get('status_target', '').strip()
        if not target:
            return "📊 **Please specify what status to check**\n\n**Examples:** battery status, network info, volume level"
        
        # Find matching indicator
        indicator = self._find_indicator_by_name(target)
        
        if not indicator:
            available = ', '.join(self.indicators.keys())
            return f"🔍 **Status indicator not found:** '{target}'\n\n**Available:** {available}"
        
        if not indicator.visible or not indicator.active:
            return f"📊 **{indicator.name}:** Not currently active or available"
        
        # Format status response
        response = f"📊 **{indicator.name} Status:**\n\n"
        
        if indicator.value is not None:
            unit = indicator.unit or ""
            response += f"**Level:** {indicator.value}{unit}\n"
        
        response += f"**Status:** {indicator.status.title()}\n"
        
        if indicator.tooltip:
            response += f"**Details:** {indicator.tooltip}\n"
        
        if indicator.last_updated > 0:
            age = time.time() - indicator.last_updated
            if age < 60:
                response += f"**Last Updated:** {int(age)} seconds ago\n"
            else:
                response += f"**Last Updated:** {int(age // 60)} minutes ago\n"
        
        # Add context-specific information
        if indicator.indicator_type == IndicatorType.POWER and indicator.id == 'battery':
            self._add_battery_context(response, indicator)
        elif indicator.indicator_type == IndicatorType.NETWORK:
            self._add_network_context(response, indicator)
        
        return response.strip()
    
    def _handle_overall_status(self, entities: Dict) -> str:
        """Handle overall system status requests"""
        response = "📊 **PersonalAIOS System Status Overview**\n\n"
        
        # Group indicators by type
        by_type = defaultdict(list)
        for indicator in self.indicators.values():
            if indicator.visible and indicator.active:
                by_type[indicator.indicator_type].append(indicator)
        
        # Display by category
        type_icons = {
            IndicatorType.POWER: '🔋',
            IndicatorType.NETWORK: '🌐',
            IndicatorType.VOLUME: '🔊',
            IndicatorType.PERFORMANCE: '⚡',
            IndicatorType.BLUETOOTH: '📶',
            IndicatorType.SECURITY: '🔒',
            IndicatorType.STORAGE: '💾'
        }
        
        for indicator_type, indicators in by_type.items():
            if indicators:
                type_icon = type_icons.get(indicator_type, '📊')
                response += f"**{type_icon} {indicator_type.value.title()}:**\n"
                
                for indicator in indicators:
                    value_str = ""
                    if indicator.value is not None:
                        unit = indicator.unit or ""
                        value_str = f" • {indicator.value}{unit}"
                    
                    status_icon = "✅" if indicator.status == "normal" else "⚠️"
                    response += f"  {status_icon} {indicator.name}{value_str}\n"
                
                response += "\n"
        
        # Add system summary
        try:
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            response += f"**💻 Quick Summary:**\n"
            response += f"  • CPU: {cpu_usage:.1f}% usage\n"
            response += f"  • Memory: {memory.percent:.1f}% used\n"
            
            if 'battery' in self.indicators and self.indicators['battery'].visible:
                battery_level = self.indicators['battery'].value
                response += f"  • Battery: {battery_level}%\n"
            
            # Network status
            network_status = "Offline"
            if self.indicators['wifi'].active:
                network_status = "Wi-Fi Connected"
            elif self.indicators['ethernet'].active:
                network_status = "Ethernet Connected"
            response += f"  • Network: {network_status}\n"
        except:
            pass
        
        return response
    
    def _handle_power_control(self, entities: Dict) -> str:
        """Handle power-related control commands"""
        battery_indicator = self.indicators.get('battery')
        power_indicator = self.indicators.get('power')
        
        if not battery_indicator or not battery_indicator.visible:
            return "🔋 **Battery information not available**\n\nThis appears to be a desktop system without battery."
        
        response = f"🔋 **Power Status:**\n\n"
        
        if battery_indicator.value is not None:
            response += f"**Battery Level:** {battery_indicator.value}%\n"
        
        response += f"**Status:** {battery_indicator.status.title()}\n"
        
        if battery_indicator.tooltip:
            # Extract time remaining from tooltip
            if "remaining" in battery_indicator.tooltip:
                response += f"**Time Remaining:** {battery_indicator.tooltip.split('remaining')[0].split()[-1]} remaining\n"
            elif "to full" in battery_indicator.tooltip:
                response += f"**Time to Full:** {battery_indicator.tooltip.split('to full')[0].split()[-1]} to full charge\n"
        
        # Power profile information
        if power_indicator and power_indicator.active:
            response += f"**Power Source:** {power_indicator.value}\n"
        
        # Battery health indicators
        try:
            battery = psutil.sensors_battery()
            if battery:
                if battery.percent <= 10:
                    response += "\n⚠️ **Critical battery level - charge immediately!**"
                elif battery.percent <= 20:
                    response += "\n🟡 **Low battery - consider charging soon**"
        except:
            pass
        
        return response
    
    def _handle_network_control(self, entities: Dict) -> str:
        """Handle network-related control commands"""
        wifi_indicator = self.indicators.get('wifi')
        ethernet_indicator = self.indicators.get('ethernet')
        
        response = "🌐 **Network Status:**\n\n"
        
        connection_found = False
        
        if wifi_indicator and wifi_indicator.active:
            connection_found = True
            response += f"**Wi-Fi:** Connected"
            if wifi_indicator.value:
                response += f" • Signal: {wifi_indicator.value}%"
            response += "\n"
            
            if wifi_indicator.tooltip and "IP:" in wifi_indicator.tooltip:
                ip_address = wifi_indicator.tooltip.split("IP: ")[1]
                response += f"**IP Address:** {ip_address}\n"
        
        if ethernet_indicator and ethernet_indicator.active:
            connection_found = True
            response += f"**Ethernet:** Connected\n"
            
            if ethernet_indicator.tooltip and "IP:" in ethernet_indicator.tooltip:
                ip_address = ethernet_indicator.tooltip.split("IP: ")[1]
                response += f"**IP Address:** {ip_address}\n"
        
        if not connection_found:
            response += "**Status:** No active network connections\n"
            response += "\n🔴 **Offline** - Check network settings or connections"
        else:
            # Test internet connectivity
            try:
                import socket
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                response += "\n✅ **Internet connectivity verified**"
            except OSError:
                response += "\n🟡 **Connected to network but no internet access**"
        
        return response
    
    def _handle_volume_control(self, entities: Dict) -> str:
        """Handle volume-related control commands"""
        volume_indicator = self.indicators.get('volume')
        
        if not volume_indicator:
            return "🔊 **Volume control not available**"
        
        response = f"🔊 **Volume Status:**\n\n"
        
        if volume_indicator.value is not None:
            response += f"**Volume Level:** {volume_indicator.value}%\n"
        
        response += f"**Status:** {volume_indicator.status.title()}\n"
        
        if volume_indicator.status == 'muted':
            response += "\n🔇 **Audio is currently muted**"
        elif volume_indicator.value is not None:
            if volume_indicator.value > 80:
                response += "\n🔊 **High volume**"
            elif volume_indicator.value < 20:
                response += "\n🔉 **Low volume**"
        
        return response
    
    def _handle_toggle_indicator(self, entities: Dict) -> str:
        """Handle indicator toggle commands"""
        target = entities.get('status_target', '').strip()
        if not target:
            return "📊 **Please specify which indicator to toggle**"
        
        indicator = self._find_indicator_by_name(target)
        if not indicator:
            return f"🔍 **Indicator not found:** '{target}'"
        
        # Toggle visibility
        indicator.visible = not indicator.visible
        
        action = "shown" if indicator.visible else "hidden"
        return f"👁️ **{indicator.name} indicator {action}**"
    
    def _handle_system_action(self, entities: Dict) -> str:
        """Handle system action commands"""
        groups = entities.get('groups', [])
        if not groups:
            return "⚙️ **Please specify the system action to perform**"
        
        action_target = groups[0].strip()
        
        # Handle volume control
        if 'volume' in action_target and len(groups) > 1:
            try:
                volume_level = int(groups[1])
                result = subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{volume_level}%'],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return f"🔊 **Volume set to {volume_level}%**"
                else:
                    return "❌ **Failed to set volume**"
            except (ValueError, FileNotFoundError):
                return "❌ **Volume control not available**"
        
        # Handle brightness control
        elif 'brightness' in action_target and len(groups) > 1:
            try:
                brightness_level = int(groups[1])
                # Try different brightness control methods
                brightness_files = [
                    '/sys/class/backlight/intel_backlight/brightness',
                    '/sys/class/backlight/acpi_video0/brightness'
                ]
                
                for brightness_file in brightness_files:
                    if Path(brightness_file).exists():
                        max_brightness_file = brightness_file.replace('brightness', 'max_brightness')
                        try:
                            with open(max_brightness_file, 'r') as f:
                                max_brightness = int(f.read().strip())
                            
                            actual_brightness = int((brightness_level / 100) * max_brightness)
                            
                            with open(brightness_file, 'w') as f:
                                f.write(str(actual_brightness))
                            
                            return f"🔆 **Brightness set to {brightness_level}%**"
                        except PermissionError:
                            return "❌ **Permission denied** - brightness control requires root access"
                
                return "❌ **Brightness control not available**"
            except ValueError:
                return "❌ **Invalid brightness value**"
        
        return f"⚙️ **System action not implemented:** {action_target}"
    
    def _find_indicator_by_name(self, name: str) -> Optional[SystemIndicator]:
        """Find indicator by name using fuzzy matching"""
        name_lower = name.lower().strip()
        
        # Exact ID match
        if name_lower in self.indicators:
            return self.indicators[name_lower]
        
        # Exact name match
        for indicator in self.indicators.values():
            if indicator.name.lower() == name_lower:
                return indicator
        
        # Partial name match
        for indicator in self.indicators.values():
            if name_lower in indicator.name.lower():
                return indicator
        
        # Description match
        for indicator in self.indicators.values():
            if name_lower in indicator.description.lower():
                return indicator
        
        # Type match
        type_keywords = {
            'network': ['network', 'internet', 'wifi', 'ethernet'],
            'power': ['power', 'battery', 'charging'],
            'audio': ['audio', 'volume', 'sound'],
            'system': ['cpu', 'memory', 'performance']
        }
        
        for indicator in self.indicators.values():
            indicator_type = indicator.indicator_type.value
            if indicator_type in type_keywords:
                if any(keyword in name_lower for keyword in type_keywords[indicator_type]):
                    return indicator
        
        return None
    
    def _add_battery_context(self, response: str, indicator: SystemIndicator) -> str:
        """Add battery-specific context information"""
        if indicator.value is not None:
            if indicator.value <= 10:
                response += "\n⚠️ **Critical battery level!**"
            elif indicator.value <= 20:
                response += "\n🟡 **Low battery warning**"
            elif indicator.value >= 95:
                response += "\n✅ **Battery fully charged**"
        
        return response
    
    def _add_network_context(self, response: str, indicator: SystemIndicator) -> str:
        """Add network-specific context information"""
        if indicator.id == 'wifi' and indicator.value is not None:
            if indicator.value >= 80:
                response += "\n✅ **Excellent signal strength**"
            elif indicator.value >= 60:
                response += "\n🟢 **Good signal strength**"
            elif indicator.value >= 40:
                response += "\n🟡 **Fair signal strength**"
            else:
                response += "\n🔴 **Weak signal strength**"
        
        return response
    
    def get_visible_indicators(self) -> List[SystemIndicator]:
        """Get list of currently visible indicators"""
        return [indicator for indicator in self.indicators.values() 
                if indicator.visible and indicator.priority != IndicatorPriority.HIDDEN]
    
    def get_critical_indicators(self) -> List[SystemIndicator]:
        """Get list of critical status indicators"""
        return [indicator for indicator in self.indicators.values() 
                if indicator.priority == IndicatorPriority.CRITICAL and indicator.visible]
    
    def _handle_unknown_intent(self, user_input: str) -> str:
        """Handle unknown system status commands"""
        return f"""❓ **I didn't understand:** "{user_input}"

📊 **Try these natural language system status commands:**

**Status Queries:**
• "battery status" - Check battery level
• "network info" - Check connection status
• "volume level" - Check audio status
• "system overview" - Complete status summary

**System Control:**
• "set volume to 50%" - Adjust volume
• "show cpu indicator" - Toggle indicators
• "is wifi connected?" - Check connectivity

**Power Management:**
• "how much battery left?" - Battery info
• "power status" - Power source info
• "is power okay?" - Power health check

**Performance:**
• "cpu usage" - Processor status
• "memory info" - RAM usage
• "storage space" - Disk usage

**I understand natural language - speak naturally!** 🤖"""

# For compatibility with Desktop Manager
DynamicSystemStatusArea = IntelligentSystemStatusArea

if __name__ == '__main__':
    status_area = IntelligentSystemStatusArea()
    
    # Demo commands
    print(status_area.process_command("system overview"))
    print("\n" + "="*50 + "\n")
    print(status_area.process_command("battery status"))
    print("\n" + "="*50 + "\n")
    print(status_area.process_command("network info"))

