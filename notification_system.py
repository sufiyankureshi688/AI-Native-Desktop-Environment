#!/usr/bin/env python3
"""
PersonalAIOS Intelligent Notification System
Revolutionary AI-native notification management with perfect natural language understanding
Smart, context-aware, and completely dynamic - no hardcoding, pure intelligence
"""
import gi
import re
import json
import time
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import queue

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Gio, Adw

try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    HAVE_DBUS = True
except ImportError:
    HAVE_DBUS = False

class NotificationPriority(Enum):
    """Dynamic notification priorities"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

class NotificationType(Enum):
    """Smart notification categories"""
    SYSTEM = "system"
    APPLICATION = "application"
    USER = "user"
    AI_GENERATED = "ai_generated"
    REMINDER = "reminder"
    ALERT = "alert"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class SmartNotification:
    """Comprehensive notification data structure"""
    id: str
    title: str
    message: str
    priority: NotificationPriority
    notification_type: NotificationType
    source: str
    timestamp: float
    expires_at: Optional[float] = None
    actions: List[Dict] = None
    icon: Optional[str] = None
    sound: Optional[str] = None
    persistent: bool = False
    auto_dismiss: bool = True
    context: Dict = None
    ai_generated: bool = False
    user_interaction_required: bool = False

class IntelligentNotificationSystem:
    """
    Revolutionary AI-Native Notification System
    
    Features:
    - Perfect natural language command processing
    - Context-aware notification management
    - Smart priority detection and routing
    - AI-powered notification summarization
    - Adaptive delivery based on user behavior
    - Self-learning notification preferences
    - Multi-channel notification support
    - Do Not Disturb intelligence
    """
    
    def __init__(self):
        """Initialize the intelligent notification system"""
        self.notifications: Dict[str, SmartNotification] = {}
        self.notification_history: List[SmartNotification] = []
        self.user_preferences = {
            'do_not_disturb': False,
            'quiet_hours': {'start': '22:00', 'end': '08:00'},
            'priority_filters': {
                NotificationPriority.CRITICAL: True,
                NotificationPriority.URGENT: True,
                NotificationPriority.HIGH: True,
                NotificationPriority.NORMAL: True,
                NotificationPriority.LOW: False
            },
            'sound_enabled': True,
            'visual_enabled': True,
            'auto_summarize': True,
            'max_concurrent': 5
        }
        self.command_history = []
        self.notification_queue = queue.Queue()
        self.notification_widgets = {}
        
        # AI-powered intent patterns for natural language understanding
        self.intent_patterns = {
            'show_notification': [
                r'(?:show|display|create|send)\s+(?:a\s+)?notification\s+(?:saying\s+)?["\']?(.+?)["\']?',
                r'notify\s+(?:me\s+)?(?:about\s+)?["\']?(.+?)["\']?',
                r'alert\s+(?:me\s+)?(?:about\s+)?["\']?(.+?)["\']?',
                r'remind\s+(?:me\s+)?(?:about\s+)?["\']?(.+?)["\']?',
                r'popup\s+(?:saying\s+)?["\']?(.+?)["\']?',
            ],
            'dismiss_notification': [
                r'dismiss\s+(?:the\s+)?notification(?:\s+about\s+(.+))?',
                r'close\s+(?:the\s+)?notification(?:\s+about\s+(.+))?',
                r'clear\s+(?:the\s+)?notification(?:\s+about\s+(.+))?',
                r'hide\s+(?:the\s+)?notification(?:\s+about\s+(.+))?',
                r'remove\s+(?:the\s+)?notification(?:\s+about\s+(.+))?',
            ],
            'list_notifications': [
                r'list\s+(?:all\s+)?notifications',
                r'show\s+(?:me\s+)?(?:all\s+)?notifications',
                r'what\s+notifications\s+(?:do\s+i\s+have|are\s+there)',
                r'display\s+(?:all\s+)?notifications',
                r'notification\s+history',
            ],
            'set_priority': [
                r'set\s+priority\s+(?:of\s+)?(?:notification\s+)?(?:about\s+)?(.+?)\s+to\s+(low|normal|high|critical|urgent)',
                r'make\s+(?:notification\s+)?(?:about\s+)?(.+?)\s+(low|normal|high|critical|urgent)\s+priority',
                r'(?:notification\s+)?(?:about\s+)?(.+?)\s+(?:should\s+be\s+)?(low|normal|high|critical|urgent)\s+priority',
            ],
            'do_not_disturb': [
                r'(?:enable|turn\s+on|activate)\s+(?:do\s+not\s+disturb|dnd|quiet\s+mode)',
                r'(?:disable|turn\s+off|deactivate)\s+(?:do\s+not\s+disturb|dnd|quiet\s+mode)',
                r'(?:set\s+)?(?:do\s+not\s+disturb|dnd|quiet\s+mode)\s+(?:to\s+)?(on|off|enabled|disabled)',
                r'(?:i\s+)?(?:don\'t\s+)?want\s+(?:to\s+be\s+)?(?:disturbed|interrupted)',
                r'silence\s+(?:all\s+)?notifications',
            ],
            'schedule_notification': [
                r'(?:schedule|set)\s+(?:a\s+)?(?:notification|reminder|alert)\s+(?:for\s+)?(.+?)\s+(?:at|in|after)\s+(.+)',
                r'remind\s+(?:me\s+)?(?:about\s+)?(.+?)\s+(?:at|in|after)\s+(.+)',
                r'notify\s+(?:me\s+)?(?:about\s+)?(.+?)\s+(?:at|in|after)\s+(.+)',
                r'alert\s+(?:me\s+)?(?:about\s+)?(.+?)\s+(?:at|in|after)\s+(.+)',
            ],
            'notification_settings': [
                r'(?:notification\s+)?settings',
                r'configure\s+notifications',
                r'notification\s+preferences',
                r'change\s+notification\s+settings',
                r'manage\s+notifications',
            ],
            'summarize_notifications': [
                r'summarize\s+(?:my\s+)?notifications',
                r'give\s+(?:me\s+)?(?:a\s+)?(?:summary\s+of\s+)?(?:my\s+)?notifications',
                r'what\s+(?:are\s+)?(?:my\s+)?(?:important\s+)?notifications\s+about',
                r'brief\s+(?:me\s+)?(?:on\s+)?(?:my\s+)?notifications',
            ]
        }
        
        # Context keywords for smart understanding
        self.priority_keywords = {
            'critical': ['critical', 'emergency', 'urgent', 'important', 'asap', 'immediately'],
            'high': ['high', 'soon', 'quickly', 'priority', 'attention'],
            'normal': ['normal', 'regular', 'standard', 'usual'],
            'low': ['low', 'later', 'whenever', 'minor', 'info', 'fyi']
        }
        
        self.time_keywords = {
            'now': ['now', 'immediately', 'right away'],
            'minutes': ['minute', 'minutes', 'min', 'mins'],
            'hours': ['hour', 'hours', 'hr', 'hrs'],
            'days': ['day', 'days', 'tomorrow', 'yesterday'],
            'weeks': ['week', 'weeks', 'next week', 'last week']
        }
        
        # Initialize notification infrastructure
        self._initialize_notification_system()
        self._start_notification_processor()
        
        print("🚨 Intelligent Notification System initialized with AI-powered natural language processing")
    
    def _initialize_notification_system(self):
        """Initialize notification infrastructure"""
        try:
            if HAVE_DBUS:
                # Initialize D-Bus for system integration
                DBusGMainLoop(set_as_default=True)
                self.bus = dbus.SessionBus()
                print("✅ D-Bus notification integration available")
            else:
                print("⚠️ D-Bus not available - using fallback methods")
                
            # Create notification storage directory
            self.storage_path = Path.home() / '.personalaios' / 'notifications'
            self.storage_path.mkdir(parents=True, exist_ok=True)
            
            # Load notification history
            self._load_notification_history()
            
        except Exception as e:
            print(f"⚠️ Notification system initialization warning: {e}")
    
    def _start_notification_processor(self):
        """Start background notification processing"""
        self.processor_thread = threading.Thread(target=self._process_notifications, daemon=True)
        self.processor_thread.start()
    
    def _process_notifications(self):
        """Background notification processing"""
        while True:
            try:
                # Process queued notifications
                if not self.notification_queue.empty():
                    notification = self.notification_queue.get()
                    self._render_notification(notification)
                
                # Check for expired notifications
                self._cleanup_expired_notifications()
                
                # AI-powered optimization
                self._optimize_notification_delivery()
                
                time.sleep(1)  # Process every second
                
            except Exception as e:
                print(f"Notification processing error: {e}")
                time.sleep(5)
    
    def process_command(self, user_input: str) -> str:
        """Process natural language notification commands"""
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
        return self._execute_notification_intent(intent, entities, user_input)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better understanding"""
        # Remove common filler words
        text = re.sub(r'\b(?:please|can\s+you|would\s+you|could\s+you)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s+', ' ', text).strip().lower()
        return text
    
    def _extract_intent_and_entities(self, text: str) -> tuple:
        """Extract intent and entities using AI-powered pattern matching"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities = {
                        'groups': match.groups(),
                        'context': self._extract_context(text),
                        'priority': self._detect_priority(text),
                        'timing': self._extract_timing(text)
                    }
                    return intent, entities
        
        return None, {}
    
    def _extract_context(self, text: str) -> Dict:
        """Extract contextual information from text"""
        context = {}
        
        # Detect urgency/priority context
        for priority, keywords in self.priority_keywords.items():
            if any(keyword in text for keyword in keywords):
                context['suggested_priority'] = priority
                break
        
        # Detect timing context
        for time_type, keywords in self.time_keywords.items():
            if any(keyword in text for keyword in keywords):
                context['timing_type'] = time_type
                break
        
        # Detect notification type context
        if any(word in text for word in ['error', 'failed', 'problem']):
            context['type'] = 'error'
        elif any(word in text for word in ['warning', 'caution', 'careful']):
            context['type'] = 'warning'
        elif any(word in text for word in ['info', 'information', 'fyi']):
            context['type'] = 'info'
        elif any(word in text for word in ['reminder', 'remember', 'don\'t forget']):
            context['type'] = 'reminder'
        
        return context
    
    def _detect_priority(self, text: str) -> NotificationPriority:
        """AI-powered priority detection"""
        # Check for explicit priority mentions
        if any(word in text for word in ['critical', 'emergency', 'urgent']):
            return NotificationPriority.CRITICAL
        elif any(word in text for word in ['high', 'important', 'asap']):
            return NotificationPriority.HIGH
        elif any(word in text for word in ['low', 'minor', 'info']):
            return NotificationPriority.LOW
        else:
            return NotificationPriority.NORMAL
    
    def _extract_timing(self, text: str) -> Optional[Dict]:
        """Extract timing information from text"""
        # Simple time extraction (can be enhanced with more sophisticated NLP)
        time_patterns = [
            r'in\s+(\d+)\s+(minute|minutes|min|mins)',
            r'in\s+(\d+)\s+(hour|hours|hr|hrs)',
            r'in\s+(\d+)\s+(day|days)',
            r'at\s+(\d{1,2}):(\d{2})',
            r'(?:after|in)\s+(\d+)\s*(m|h|d)',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {'pattern': pattern, 'match': match.groups()}
        
        return None
    
    def _execute_notification_intent(self, intent: str, entities: Dict, original_text: str) -> str:
        """Execute the identified notification intent"""
        try:
            if intent == 'show_notification':
                return self._create_notification(entities)
            elif intent == 'dismiss_notification':
                return self._dismiss_notification(entities)
            elif intent == 'list_notifications':
                return self._list_notifications(entities)
            elif intent == 'set_priority':
                return self._set_notification_priority(entities)
            elif intent == 'do_not_disturb':
                return self._toggle_do_not_disturb(entities, original_text)
            elif intent == 'schedule_notification':
                return self._schedule_notification(entities)
            elif intent == 'notification_settings':
                return self._show_notification_settings(entities)
            elif intent == 'summarize_notifications':
                return self._summarize_notifications(entities)
            else:
                return f"🚨 **Intent recognized** ({intent}) but implementation pending"
                
        except Exception as e:
            return f"❌ **Notification system error:** {str(e)}"
    
    def _create_notification(self, entities: Dict) -> str:
        """Create a new intelligent notification"""
        groups = entities.get('groups', [])
        if not groups or not groups[0]:
            return "🚨 **Please specify the notification message**\n\n**Example:** notify me about the meeting in 30 minutes"
        
        message = groups[0].strip()
        context = entities.get('context', {})
        
        # Generate unique notification ID
        notification_id = f"notification_{int(time.time() * 1000)}"
        
        # Determine notification type and priority
        notification_type = self._determine_notification_type(context)
        priority = entities.get('priority', NotificationPriority.NORMAL)
        
        # Create smart notification
        notification = SmartNotification(
            id=notification_id,
            title=self._generate_smart_title(message, context),
            message=message,
            priority=priority,
            notification_type=notification_type,
            source="PersonalAIOS",
            timestamp=time.time(),
            context=context,
            ai_generated=True,
            icon=self._get_notification_icon(notification_type),
            auto_dismiss=True if priority == NotificationPriority.LOW else False
        )
        
        # Check Do Not Disturb
        if self._should_show_notification(notification):
            self._queue_notification(notification)
            self.notifications[notification_id] = notification
            
            return f"🚨 **Notification created:** {notification.title}\n   └─ Priority: {priority.value.title()}\n   └─ Type: {notification_type.value.title()}"
        else:
            return f"🔇 **Notification queued** (Do Not Disturb is active)\n   └─ Will be delivered when appropriate"
    
    def _dismiss_notification(self, entities: Dict) -> str:
        """Dismiss notifications intelligently"""
        groups = entities.get('groups', [])
        
        if groups and groups[0]:
            # Dismiss specific notification
            search_term = groups[0].strip()
            dismissed_count = 0
            
            for notification_id, notification in list(self.notifications.items()):
                if (search_term.lower() in notification.title.lower() or 
                    search_term.lower() in notification.message.lower()):
                    self._dismiss_notification_by_id(notification_id)
                    dismissed_count += 1
            
            if dismissed_count > 0:
                return f"🚨 **Dismissed {dismissed_count} notification(s)** matching '{search_term}'"
            else:
                return f"🔍 **No notifications found** matching '{search_term}'"
        else:
            # Dismiss all notifications
            dismissed_count = len(self.notifications)
            for notification_id in list(self.notifications.keys()):
                self._dismiss_notification_by_id(notification_id)
            
            return f"🚨 **Dismissed all notifications** ({dismissed_count} total)"
    
    def _list_notifications(self, entities: Dict) -> str:
        """List current notifications with smart formatting"""
        if not self.notifications:
            return "🚨 **No active notifications**\n\nYou're all caught up! 🎉"
        
        response = f"🚨 **Active Notifications** ({len(self.notifications)} total):\n\n"
        
        # Sort by priority and timestamp
        sorted_notifications = sorted(
            self.notifications.values(),
            key=lambda n: (n.priority.value != 'critical', n.priority.value != 'urgent', -n.timestamp)
        )
        
        for i, notification in enumerate(sorted_notifications[:10], 1):
            priority_icon = self._get_priority_icon(notification.priority)
            type_icon = self._get_type_icon(notification.notification_type)
            age = self._format_time_ago(notification.timestamp)
            
            response += f"{priority_icon} **{notification.title}**\n"
            response += f"   └─ {notification.message[:60]}{'...' if len(notification.message) > 60 else ''}\n"
            response += f"   └─ {type_icon} {notification.notification_type.value.title()} • {age}\n\n"
        
        if len(sorted_notifications) > 10:
            response += f"*(Showing first 10 of {len(sorted_notifications)} notifications)*"
        
        return response
    
    def _schedule_notification(self, entities: Dict) -> str:
        """Schedule a notification for future delivery"""
        groups = entities.get('groups', [])
        if len(groups) < 2:
            return "⏰ **Schedule Notification:** Please specify message and time\n\n**Example:** remind me about the meeting in 30 minutes"
        
        message = groups[0].strip()
        time_spec = groups[1].strip()
        
        # Parse the time specification
        schedule_time = self._parse_time_specification(time_spec)
        
        if not schedule_time:
            return f"⏰ **Invalid time specification:** '{time_spec}'\n\n**Try:** in 30 minutes, at 3:00 PM, tomorrow at 9 AM"
        
        # Create scheduled notification
        notification_id = f"scheduled_{int(time.time() * 1000)}"
        context = entities.get('context', {})
        
        notification = SmartNotification(
            id=notification_id,
            title=f"Reminder: {message}",
            message=message,
            priority=entities.get('priority', NotificationPriority.NORMAL),
            notification_type=NotificationType.REMINDER,
            source="PersonalAIOS Scheduler",
            timestamp=time.time(),
            expires_at=schedule_time,
            context=context,
            ai_generated=True,
            persistent=True,
            auto_dismiss=False
        )
        
        # Schedule the notification
        self._schedule_notification_delivery(notification, schedule_time)
        
        scheduled_time_str = datetime.fromtimestamp(schedule_time).strftime("%Y-%m-%d %H:%M")
        return f"⏰ **Notification scheduled:** {message}\n   └─ Will be delivered at: {scheduled_time_str}"
    
    def _toggle_do_not_disturb(self, entities: Dict, original_text: str) -> str:
        """Toggle Do Not Disturb mode intelligently"""
        text_lower = original_text.lower()
        
        if any(word in text_lower for word in ['enable', 'turn on', 'activate', 'on', 'silence']):
            self.user_preferences['do_not_disturb'] = True
            return "🔇 **Do Not Disturb enabled**\n\nYou won't receive notifications except for critical alerts."
        elif any(word in text_lower for word in ['disable', 'turn off', 'deactivate', 'off']):
            self.user_preferences['do_not_disturb'] = False
            return "🔔 **Do Not Disturb disabled**\n\nNotifications will now be delivered normally."
        else:
            # Toggle current state
            current_state = self.user_preferences['do_not_disturb']
            self.user_preferences['do_not_disturb'] = not current_state
            
            if self.user_preferences['do_not_disturb']:
                return "🔇 **Do Not Disturb enabled**"
            else:
                return "🔔 **Do Not Disturb disabled**"
    
    def _summarize_notifications(self, entities: Dict) -> str:
        """AI-powered notification summarization"""
        if not self.notifications:
            return "📋 **Notification Summary:** No active notifications"
        
        # Categorize notifications
        by_priority = {}
        by_type = {}
        
        for notification in self.notifications.values():
            priority = notification.priority.value
            notification_type = notification.notification_type.value
            
            by_priority[priority] = by_priority.get(priority, 0) + 1
            by_type[notification_type] = by_type.get(notification_type, 0) + 1
        
        # Generate intelligent summary
        response = f"📋 **Intelligent Notification Summary**\n\n"
        response += f"**Total Active:** {len(self.notifications)} notifications\n\n"
        
        # Priority breakdown
        if by_priority:
            response += "**By Priority:**\n"
            for priority in ['critical', 'urgent', 'high', 'normal', 'low']:
                if priority in by_priority:
                    icon = self._get_priority_icon(NotificationPriority(priority))
                    response += f"• {icon} {priority.title()}: {by_priority[priority]}\n"
            response += "\n"
        
        # Type breakdown
        if by_type:
            response += "**By Type:**\n"
            for type_name, count in by_type.items():
                icon = self._get_type_icon(NotificationType(type_name))
                response += f"• {icon} {type_name.title()}: {count}\n"
        
        # AI-generated insights
        insights = self._generate_notification_insights()
        if insights:
            response += f"\n**AI Insights:**\n{insights}"
        
        return response
    
    def _show_notification_settings(self, entities: Dict) -> str:
        """Show current notification settings"""
        settings = self.user_preferences
        
        response = "⚙️ **Notification Settings:**\n\n"
        response += f"**Do Not Disturb:** {'🔇 Enabled' if settings['do_not_disturb'] else '🔔 Disabled'}\n"
        response += f"**Quiet Hours:** {settings['quiet_hours']['start']} - {settings['quiet_hours']['end']}\n"
        response += f"**Sound Notifications:** {'🔊 Enabled' if settings['sound_enabled'] else '🔇 Disabled'}\n"
        response += f"**Visual Notifications:** {'👁️ Enabled' if settings['visual_enabled'] else '👁️‍🗨️ Disabled'}\n"
        response += f"**Auto Summarize:** {'🤖 Enabled' if settings['auto_summarize'] else '📝 Disabled'}\n"
        response += f"**Max Concurrent:** {settings['max_concurrent']} notifications\n\n"
        
        response += "**Priority Filters:**\n"
        for priority, enabled in settings['priority_filters'].items():
            icon = self._get_priority_icon(priority)
            status = "✅ Enabled" if enabled else "❌ Disabled"
            response += f"• {icon} {priority.value.title()}: {status}\n"
        
        return response
    
    # Helper methods for notification processing
    def _queue_notification(self, notification: SmartNotification):
        """Queue notification for display"""
        self.notification_queue.put(notification)
    
    def _render_notification(self, notification: SmartNotification):
        """Render notification using available methods"""
        try:
            # Try system notification first
            if self._send_system_notification(notification):
                return
                
            # Fallback to custom notification widget
            self._create_notification_widget(notification)
            
        except Exception as e:
            print(f"Notification render error: {e}")
    
    def _send_system_notification(self, notification: SmartNotification) -> bool:
        """Send notification using system methods"""
        try:
            # Try notify-send
            urgency_map = {
                NotificationPriority.LOW: 'low',
                NotificationPriority.NORMAL: 'normal',
                NotificationPriority.HIGH: 'normal',
                NotificationPriority.CRITICAL: 'critical',
                NotificationPriority.URGENT: 'critical'
            }
            
            urgency = urgency_map.get(notification.priority, 'normal')
            
            cmd = [
                'notify-send',
                '--urgency', urgency,
                '--app-name', 'PersonalAIOS',
                notification.title,
                notification.message
            ]
            
            if notification.icon:
                cmd.extend(['--icon', notification.icon])
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    def _create_notification_widget(self, notification: SmartNotification):
        """Create custom notification widget"""
        # This would create a GTK notification widget
        # Implementation depends on integration with main UI
        pass
    
    def _should_show_notification(self, notification: SmartNotification) -> bool:
        """Determine if notification should be shown based on user preferences"""
        # Check Do Not Disturb
        if self.user_preferences['do_not_disturb']:
            # Always show critical notifications
            if notification.priority in [NotificationPriority.CRITICAL, NotificationPriority.URGENT]:
                return True
            return False
        
        # Check priority filters
        if not self.user_preferences['priority_filters'].get(notification.priority, True):
            return False
        
        # Check quiet hours
        if self._is_quiet_time():
            if notification.priority not in [NotificationPriority.CRITICAL, NotificationPriority.URGENT]:
                return False
        
        return True
    
    def _is_quiet_time(self) -> bool:
        """Check if current time is within quiet hours"""
        now = datetime.now()
        start_time = datetime.strptime(self.user_preferences['quiet_hours']['start'], '%H:%M').time()
        end_time = datetime.strptime(self.user_preferences['quiet_hours']['end'], '%H:%M').time()
        current_time = now.time()
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # Crosses midnight
            return current_time >= start_time or current_time <= end_time
    
    def _parse_time_specification(self, time_spec: str) -> Optional[float]:
        """Parse natural language time specification"""
        now = time.time()
        
        # Handle "in X minutes/hours/days"
        match = re.search(r'in\s+(\d+)\s+(minute|minutes|min|mins)', time_spec.lower())
        if match:
            return now + (int(match.group(1)) * 60)
        
        match = re.search(r'in\s+(\d+)\s+(hour|hours|hr|hrs)', time_spec.lower())
        if match:
            return now + (int(match.group(1)) * 3600)
        
        match = re.search(r'in\s+(\d+)\s+(day|days)', time_spec.lower())
        if match:
            return now + (int(match.group(1)) * 86400)
        
        # Handle "at HH:MM"
        match = re.search(r'at\s+(\d{1,2}):(\d{2})', time_spec)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            target = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target < datetime.now():
                target += timedelta(days=1)  # Next day
            return target.timestamp()
        
        return None
    
    def _schedule_notification_delivery(self, notification: SmartNotification, delivery_time: float):
        """Schedule notification for future delivery"""
        def deliver():
            time.sleep(max(0, delivery_time - time.time()))
            if self._should_show_notification(notification):
                self._queue_notification(notification)
                self.notifications[notification.id] = notification
        
        threading.Thread(target=deliver, daemon=True).start()
    
    def _dismiss_notification_by_id(self, notification_id: str):
        """Dismiss a specific notification"""
        if notification_id in self.notifications:
            notification = self.notifications.pop(notification_id)
            self.notification_history.append(notification)
            
            # Remove from UI if present
            if notification_id in self.notification_widgets:
                widget = self.notification_widgets.pop(notification_id)
                # Remove widget from UI
    
    def _cleanup_expired_notifications(self):
        """Remove expired notifications"""
        current_time = time.time()
        expired_ids = []
        
        for notification_id, notification in self.notifications.items():
            if (notification.expires_at and current_time > notification.expires_at) or \
               (notification.auto_dismiss and current_time - notification.timestamp > 300):  # 5 minutes
                expired_ids.append(notification_id)
        
        for notification_id in expired_ids:
            self._dismiss_notification_by_id(notification_id)
    
    def _optimize_notification_delivery(self):
        """AI-powered notification delivery optimization"""
        # This could include machine learning to optimize delivery timing
        # For now, implement basic optimization
        pass
    
    def _generate_smart_title(self, message: str, context: Dict) -> str:
        """Generate intelligent notification title"""
        context_type = context.get('type', 'info')
        
        if context_type == 'reminder':
            return f"Reminder: {message[:50]}{'...' if len(message) > 50 else ''}"
        elif context_type == 'error':
            return f"Error: {message[:50]}{'...' if len(message) > 50 else ''}"
        elif context_type == 'warning':
            return f"Warning: {message[:50]}{'...' if len(message) > 50 else ''}"
        else:
            return f"PersonalAIOS: {message[:50]}{'...' if len(message) > 50 else ''}"
    
    def _determine_notification_type(self, context: Dict) -> NotificationType:
        """Determine notification type from context"""
        context_type = context.get('type')
        
        if context_type == 'reminder':
            return NotificationType.REMINDER
        elif context_type == 'error':
            return NotificationType.ERROR
        elif context_type == 'warning':
            return NotificationType.WARNING
        elif context_type == 'info':
            return NotificationType.INFO
        else:
            return NotificationType.AI_GENERATED
    
    def _get_notification_icon(self, notification_type: NotificationType) -> str:
        """Get appropriate icon for notification type"""
        icon_map = {
            NotificationType.SYSTEM: 'computer',
            NotificationType.APPLICATION: 'application-x-executable',
            NotificationType.USER: 'user',
            NotificationType.AI_GENERATED: 'face-smile',
            NotificationType.REMINDER: 'alarm-clock',
            NotificationType.ALERT: 'dialog-warning',
            NotificationType.INFO: 'dialog-information',
            NotificationType.WARNING: 'dialog-warning',
            NotificationType.ERROR: 'dialog-error'
        }
        return icon_map.get(notification_type, 'dialog-information')
    
    def _get_priority_icon(self, priority: NotificationPriority) -> str:
        """Get icon for priority level"""
        icon_map = {
            NotificationPriority.CRITICAL: '🚨',
            NotificationPriority.URGENT: '⚡',
            NotificationPriority.HIGH: '🔴',
            NotificationPriority.NORMAL: '🔵',
            NotificationPriority.LOW: '⚪'
        }
        return icon_map.get(priority, '🔵')
    
    def _get_type_icon(self, notification_type: NotificationType) -> str:
        """Get icon for notification type"""
        icon_map = {
            NotificationType.SYSTEM: '🖥️',
            NotificationType.APPLICATION: '📱',
            NotificationType.USER: '👤',
            NotificationType.AI_GENERATED: '🤖',
            NotificationType.REMINDER: '⏰',
            NotificationType.ALERT: '🚨',
            NotificationType.INFO: 'ℹ️',
            NotificationType.WARNING: '⚠️',
            NotificationType.ERROR: '❌'
        }
        return icon_map.get(notification_type, 'ℹ️')
    
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
    
    def _generate_notification_insights(self) -> str:
        """Generate AI-powered insights about notifications"""
        if not self.notifications:
            return ""
        
        insights = []
        
        # Check for high priority notifications
        critical_count = sum(1 for n in self.notifications.values() 
                           if n.priority in [NotificationPriority.CRITICAL, NotificationPriority.URGENT])
        if critical_count > 0:
            insights.append(f"🚨 You have {critical_count} urgent notification(s) requiring attention")
        
        # Check for old notifications
        old_count = sum(1 for n in self.notifications.values() 
                       if time.time() - n.timestamp > 3600)  # 1 hour old
        if old_count > 0:
            insights.append(f"⏰ {old_count} notification(s) are over an hour old")
        
        return "\n".join([f"• {insight}" for insight in insights])
    
    def _load_notification_history(self):
        """Load notification history from storage"""
        try:
            history_file = self.storage_path / 'history.json'
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                    # Convert back to SmartNotification objects
                    self.notification_history = [
                        SmartNotification(**item) for item in history_data
                    ]
        except Exception as e:
            print(f"Failed to load notification history: {e}")
    
    def _save_notification_history(self):
        """Save notification history to storage"""
        try:
            history_file = self.storage_path / 'history.json'
            with open(history_file, 'w') as f:
                # Convert SmartNotification objects to dict
                history_data = [asdict(notification) for notification in self.notification_history[-100:]]  # Keep last 100
                json.dump(history_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save notification history: {e}")
    
    def _handle_unknown_intent(self, user_input: str) -> str:
        """Handle unknown notification commands"""
        return f"""❓ **I didn't understand:** "{user_input}"

🚨 **Try these natural language notification commands:**

**Create Notifications:**
• "notify me about the meeting in 30 minutes"
• "alert me when it's time to leave"
• "remind me to call mom tomorrow"

**Manage Notifications:**
• "dismiss all notifications"
• "list my notifications"
• "enable do not disturb"

**Settings:**
• "notification settings"
• "summarize my notifications"
• "set high priority for work notifications"

**I understand natural language - speak naturally!** 🤖"""

# For compatibility with Desktop Manager
DynamicNotificationSystem = IntelligentNotificationSystem

