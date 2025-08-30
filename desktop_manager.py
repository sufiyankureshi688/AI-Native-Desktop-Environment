#!/usr/bin/env python3
"""
PersonalAIOS Desktop Manager - Fixed Version
Central hub that manages ALL components without breaking existing functionality
"""
import subprocess
import os
import time
from pathlib import Path
from gi.repository import GLib, Gtk, Adw

class DesktopManager:
    def __init__(self, ai_shell):
        """Initialize with reference to AI shell for communication"""
        self.ai_shell = ai_shell
        
        # Component registry - Add new components here
        self.components = {}
        self.ui_components = {}
        
        # Load all available components safely
        self.load_components()
        
        print("🎛️ Desktop Manager initialized - managing all components")
    
    def load_components(self):
        """Load all available components dynamically with error handling"""
        
        # Top Panel Component
        try:
            from top_panel import TopPanel
            self.components['top_panel'] = TopPanel
            print("✅ Top Panel component loaded")
        except ImportError:
            print("⚠️ Top Panel component not available")
        except Exception as e:
            print(f"❌ Top Panel failed: {e}")
        
        # AI File Manager Component
        try:
            from ai_file_manager import IntelligentFileManager
            self.components['file_manager'] = IntelligentFileManager()
            print("✅ AI File Manager component loaded")
        except ImportError:
            print("⚠️ AI File Manager component not available")
        except Exception as e:
            print(f"❌ AI File Manager failed: {e}")
        
        # Window Manager Component
        try:
            from window_manager import IntelligentWindowManager
            self.components['window_manager'] = IntelligentWindowManager()
            print("✅ Window Manager component loaded")
        except ImportError:
            print("⚠️ Window Manager component not available")
        except Exception as e:
            print(f"❌ Window Manager failed: {e}")
        
        # Notification System Component
        try:
            from notification_system import IntelligentNotificationSystem
            self.components['notification_system'] = IntelligentNotificationSystem()
            print("✅ Notification System component loaded")
        except ImportError:
            print("⚠️ Notification System component not available")
        except Exception as e:
            print(f"❌ Notification System failed: {e}")
        
        # Application Launcher Component
        try:
            from application_launcher import IntelligentApplicationLauncher
            self.components['application_launcher'] = IntelligentApplicationLauncher()
            print("✅ Application Launcher component loaded")
        except ImportError:
            print("⚠️ Application Launcher component not available")
        except Exception as e:
            print(f"❌ Application Launcher failed: {e}")
        
        # Workspace Manager Component
        try:
            from workspace_manager import IntelligentWorkspaceManager
            self.components['workspace_manager'] = IntelligentWorkspaceManager()
            print("✅ Workspace Manager component loaded")
        except ImportError:
            print("⚠️ Workspace Manager component not available")
        except Exception as e:
            print(f"❌ Workspace Manager failed: {e}")
        
        # System Status Component
        try:
            from system_status_area import IntelligentSystemStatusArea
            self.components['system_status'] = IntelligentSystemStatusArea()
            print("✅ System Status component loaded")
        except ImportError:
            print("⚠️ System Status component not available")
        except Exception as e:
            print(f"❌ System Status failed: {e}")
        
        # Settings Manager Component
        try:
            from settings_manager import IntelligentSettingsManager
            self.components['settings_manager'] = IntelligentSettingsManager()
            print("✅ Settings Manager component loaded")
        except ImportError:
            print("⚠️ Settings Manager component not available")
        except Exception as e:
            print(f"❌ Settings Manager failed: {e}")
        
        # System Monitor Component
        try:
            import psutil
            self.components['system_monitor'] = psutil
            print("✅ System Monitor component loaded")
        except ImportError:
            print("⚠️ System Monitor component not available (install psutil)")
    
    def build_ui(self, main_box, desktop_mode):
        """Build complete UI with all components - Called by AI Shell"""
        try:
            # Top Panel (desktop mode only)
            if desktop_mode and 'top_panel' in self.components:
                try:
                    top_panel = self.components['top_panel']()
                    self.ui_components['top_panel'] = top_panel
                    main_box.append(top_panel)
                    print("✅ Top Panel added to UI")
                except Exception as e:
                    print(f"❌ Failed to add Top Panel: {e}")
            
            # Header for window mode
            if not desktop_mode:
                header = self.build_header()
                main_box.append(header)
            
            # Chat area
            chat_area = self.build_chat_area(desktop_mode)
            main_box.append(chat_area)
            
            # Input area
            input_area = self.build_input_area(desktop_mode)
            main_box.append(input_area)
            
        except Exception as e:
            print(f"❌ UI build failed: {e}")
    
    def build_header(self):
        """Build header bar for window mode"""
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="PersonalAIOS"))
        
        # AI status
        self.ai_shell.ai_status = Gtk.Label(label="🤖 Ready")
        header.pack_start(self.ai_shell.ai_status)
        
        # Component buttons
        if 'file_manager' in self.components:
            files_btn = Gtk.Button()
            files_btn.set_icon_name("folder-symbolic")
            files_btn.set_tooltip_text("File Manager")
            files_btn.connect('clicked', self.launch_file_manager_gui)
            header.pack_end(files_btn)
        
        if 'application_launcher' in self.components:
            apps_btn = Gtk.Button()
            apps_btn.set_icon_name("view-app-grid-symbolic")
            apps_btn.set_tooltip_text("Application Launcher")
            apps_btn.connect('clicked', self.show_application_launcher)
            header.pack_end(apps_btn)
        
        return header
    
    def build_chat_area(self, desktop_mode):
        """Build chat area"""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add_css_class("chat-area")
        
        self.ai_shell.chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        if desktop_mode:
            self.ai_shell.chat_box.set_margin_top(48)
            self.ai_shell.chat_box.set_margin_bottom(48)
            self.ai_shell.chat_box.set_margin_start(120)
            self.ai_shell.chat_box.set_margin_end(120)
        else:
            self.ai_shell.chat_box.set_margin_top(24)
            self.ai_shell.chat_box.set_margin_bottom(24)
            self.ai_shell.chat_box.set_margin_start(24)
            self.ai_shell.chat_box.set_margin_end(24)
        
        scrolled.set_child(self.ai_shell.chat_box)
        return scrolled
    
    def build_input_area(self, desktop_mode):
        """Build input area with component capabilities"""
        input_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        if desktop_mode:
            input_container.set_margin_top(32)
            input_container.set_margin_bottom(48)
            input_container.set_margin_start(120)
            input_container.set_margin_end(120)
        else:
            input_container.set_margin_top(16)
            input_container.set_margin_bottom(24)
            input_container.set_margin_start(24)
            input_container.set_margin_end(24)
        
        # Input box
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        self.ai_shell.entry = Gtk.Entry()
        
        # Dynamic placeholder based on loaded components
        placeholder = self.get_dynamic_placeholder()
        self.ai_shell.entry.set_placeholder_text(placeholder)
        self.ai_shell.entry.set_hexpand(True)
        self.ai_shell.entry.add_css_class("large-entry")
        self.ai_shell.entry.connect('activate', self.ai_shell.on_send)
        
        # Component buttons
        if 'file_manager' in self.components:
            files_btn = Gtk.Button()
            files_btn.set_icon_name("folder-symbolic")
            files_btn.set_tooltip_text("File Manager")
            files_btn.connect('clicked', self.launch_file_manager_gui)
            input_box.append(files_btn)
        
        if 'window_manager' in self.components:
            windows_btn = Gtk.Button()
            windows_btn.set_icon_name("view-grid-symbolic")
            windows_btn.set_tooltip_text("Window Manager")
            windows_btn.connect('clicked', self.show_window_manager)
            input_box.append(windows_btn)
        
        clear_btn = Gtk.Button()
        clear_btn.set_icon_name("edit-clear-symbolic")
        clear_btn.set_tooltip_text("Clear conversation")
        clear_btn.connect('clicked', self.ai_shell.clear_chat)
        
        send_btn = Gtk.Button()
        send_btn.set_icon_name("paper-plane-symbolic")
        send_btn.add_css_class("suggested-action")
        send_btn.set_tooltip_text("Send message")
        send_btn.connect('clicked', self.ai_shell.on_send)
        
        input_box.append(self.ai_shell.entry)
        input_box.append(clear_btn)
        input_box.append(send_btn)
        
        # Status bar
        status_bar = self.build_status_bar()
        
        input_container.append(input_box)
        input_container.append(status_bar)
        
        return input_container
    
    def get_dynamic_placeholder(self):
        """Generate placeholder based on available components"""
        examples = []
        
        if 'application_launcher' in self.components:
            examples.append("'what applications do I have installed'")
        if 'file_manager' in self.components:
            examples.append("'find config.py'")
        if 'window_manager' in self.components:
            examples.append("'maximize Firefox'")
        if 'workspace_manager' in self.components:
            examples.append("'create workspace for coding'")
        
        if examples:
            return f"Ask PersonalAIOS anything... Try: {examples[0]}"
        else:
            return "Ask PersonalAIOS anything..."
    
    def build_status_bar(self):
        """Build status bar showing available capabilities"""
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        status_box.add_css_class("caption")
        status_box.set_halign(Gtk.Align.CENTER)
        
        # Show loaded components
        component_count = len(self.components)
        capabilities = []
        
        if 'application_launcher' in self.components:
            capabilities.append("App Launch")
        if 'file_manager' in self.components:
            capabilities.append("File Ops")
        if 'window_manager' in self.components:
            capabilities.append("Windows")
        if 'workspace_manager' in self.components:
            capabilities.append("Workspaces")
        
        status_text = f"Ready • {component_count} components"
        if capabilities:
            status_text += f" • {' & '.join(capabilities[:3])}"
        
        status_label = Gtk.Label(label=status_text)
        status_box.append(status_label)
        
        return status_box
    
    def process_command(self, user_input):
        """
        Central command processor - Route to appropriate component
        Returns True if handled, False if should go to AI
        """
        user_input_lower = user_input.lower()
        
        try:
            # Application Launcher Commands
            if self.is_launcher_command(user_input_lower):
                if 'application_launcher' in self.components:
                    response = self.components['application_launcher'].process_command(user_input)
                    self.send_response_to_ai_shell(response)
                    return True
            
            # File Manager Commands
            if self.is_file_command(user_input_lower):
                if 'file_manager' in self.components:
                    response = self.components['file_manager'].process_command(user_input)
                    self.send_response_to_ai_shell(response)
                    return True
            
            # Window Manager Commands
            if self.is_window_command(user_input_lower):
                if 'window_manager' in self.components:
                    response = self.components['window_manager'].process_command(user_input)
                    self.send_response_to_ai_shell(response)
                    return True
            
            # System Commands
            if self.is_system_command(user_input_lower):
                response = self.handle_system_commands(user_input)
                self.send_response_to_ai_shell(response)
                return True
        
        except Exception as e:
            error_msg = f"❌ **Component Error:** {str(e)}"
            self.send_response_to_ai_shell(error_msg)
            return True
        
        # Command not handled
        return False
    
    def is_launcher_command(self, user_input):
        """Check if command is application launcher related"""
        launcher_keywords = [
            "applications", "apps", "what applications", "list apps", 
            "installed", "programs", "software", "open", "launch", "start", "run"
        ]
        return any(keyword in user_input for keyword in launcher_keywords)
    
    def is_file_command(self, user_input):
        """Check if command is file management related"""
        file_keywords = [
            "find", "search", "file", "folder", "directory", "create", "delete", 
            "copy", "move", "list files"
        ]
        return any(keyword in user_input for keyword in file_keywords)
    
    def is_window_command(self, user_input):
        """Check if command is window management related"""
        window_keywords = [
            "maximize", "minimize", "close", "window", "windows", "focus", "tile"
        ]
        return any(keyword in user_input for keyword in window_keywords)
    
    def is_system_command(self, user_input):
        """Check if command is system related"""
        system_keywords = [
            "system", "desktop", "components", "status", "info"
        ]
        return any(keyword in user_input for keyword in system_keywords)
    
    def handle_system_commands(self, user_input):
        """Handle system-level commands"""
        user_input_lower = user_input.lower()
        
        if "desktop" in user_input_lower or "components" in user_input_lower:
            return self.get_desktop_info()
        elif "system" in user_input_lower:
            return self.get_system_info()
        
        return "🎛️ **PersonalAIOS Desktop Manager** - Try 'desktop info' or 'system status'"
    
    def get_desktop_info(self):
        """Get desktop information"""
        component_count = len(self.components)
        
        response = f"🎛️ **PersonalAIOS Desktop Manager**\n\n"
        response += f"**Components Loaded:** {component_count}\n\n"
        
        if self.components:
            response += f"**Available Components:**\n"
            for name in self.components.keys():
                response += f"• {name.replace('_', ' ').title()}\n"
        
        response += f"\n**Status:** Desktop Manager Active ✅"
        return response
    
    def get_system_info(self):
        """Get system information"""
        try:
            import platform
            response = f"🖥️ **System Information**\n\n"
            response += f"**OS:** {platform.system()} {platform.release()}\n"
            response += f"**Architecture:** {platform.machine()}\n"
            response += f"**Python:** {platform.python_version()}\n"
            response += f"**PersonalAIOS Components:** {len(self.components)}\n"
            return response
        except Exception as e:
            return f"❌ System info failed: {str(e)}"
    
    # UI Event Handlers
    def launch_file_manager_gui(self, widget=None):
        """Launch file manager"""
        if 'file_manager' in self.components:
            self.send_response_to_ai_shell("📁 **File Manager Ready** - Try: 'find config.py' or 'list files'")
        else:
            self.send_response_to_ai_shell("❌ **File Manager not available**")
    
    def show_application_launcher(self, widget=None):
        """Show application launcher"""
        if 'application_launcher' in self.components:
            try:
                response = self.components['application_launcher'].process_command("list applications")
                self.send_response_to_ai_shell(response)
            except:
                self.send_response_to_ai_shell("🚀 **Application Launcher Ready** - Try: 'what applications do I have installed'")
        else:
            self.send_response_to_ai_shell("❌ **Application Launcher not available**")
    
    def show_window_manager(self, widget=None):
        """Show window manager"""
        if 'window_manager' in self.components:
            self.send_response_to_ai_shell("🪟 **Window Manager Ready** - Try: 'list windows' or 'maximize Firefox'")
        else:
            self.send_response_to_ai_shell("❌ **Window Manager not available**")
    
    def send_response_to_ai_shell(self, response):
        """Send response back to AI shell UI"""
        if self.ai_shell:
            GLib.idle_add(self.ai_shell.add_ai_message, response)

if __name__ == '__main__':
    print("🎛️ PersonalAIOS Desktop Manager - Fixed Version")
    print("   Simplified architecture without circular dependencies")

