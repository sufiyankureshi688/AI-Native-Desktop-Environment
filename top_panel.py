#!/usr/bin/env python3
"""
PersonalAIOS Top Panel
System status bar with AI integration
"""
import gi
import time
import subprocess
import requests
import os
from pathlib import Path

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, Adw, Gdk

class TopPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        
        self.set_size_request(-1, 48)
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(8)
        self.set_margin_bottom(8)
        self.add_css_class("top-panel")
        
        self.setup_left_section()
        self.setup_center_section()
        self.setup_right_section()
        
        self.connect('realize', self.on_realize)
        print("✅ TopPanel created successfully")
    
    def setup_left_section(self):
        """Setup left side with activities button"""
        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        self.activities_btn = Gtk.Button(label="🤖 PersonalAI")
        self.activities_btn.add_css_class("activities-button")
        self.activities_btn.connect('clicked', self.show_activities)
        self.activities_btn.set_tooltip_text("Show Activities")
        left_box.append(self.activities_btn)
        
        self.append(left_box)
    
    def setup_center_section(self):
        """Setup center section with clock"""
        center_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        center_box.set_hexpand(True)
        center_box.set_halign(Gtk.Align.CENTER)
        
        self.clock_label = Gtk.Label()
        self.clock_label.add_css_class("panel-clock")
        center_box.append(self.clock_label)
        
        self.append(center_box)
    
    def setup_right_section(self):
        """Setup right section with system indicators"""
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        right_box.set_halign(Gtk.Align.END)
        
        # AI Status indicator
        self.ai_status_btn = Gtk.Button()
        self.ai_status_btn.add_css_class("status-button")
        self.ai_status_btn.connect('clicked', self.show_ai_status)
        
        ai_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.ai_icon = Gtk.Image.new_from_icon_name("face-smile-symbolic")
        self.ai_label = Gtk.Label(label="AI")
        ai_box.append(self.ai_icon)
        ai_box.append(self.ai_label)
        self.ai_status_btn.set_child(ai_box)
        
        # Network indicator
        self.network_btn = Gtk.Button()
        self.network_btn.add_css_class("status-button")
        self.network_btn.set_child(Gtk.Image.new_from_icon_name("network-wireless-signal-excellent-symbolic"))
        self.network_btn.set_tooltip_text("Network Status")
        
        # Battery/Power indicator
        self.power_btn = Gtk.Button()
        self.power_btn.add_css_class("status-button")
        
        power_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.battery_icon = Gtk.Image.new_from_icon_name("battery-good-symbolic")
        self.battery_label = Gtk.Label(label="100%")
        power_box.append(self.battery_icon)
        power_box.append(self.battery_label)
        self.power_btn.set_child(power_box)
        
        # User menu button
        self.user_btn = Gtk.Button()
        self.user_btn.add_css_class("status-button")
        self.user_btn.connect('clicked', self.show_user_menu)
        self.user_btn.set_child(Gtk.Image.new_from_icon_name("avatar-default-symbolic"))
        self.user_btn.set_tooltip_text("User Menu")
        
        right_box.append(self.ai_status_btn)
        right_box.append(self.network_btn)
        right_box.append(self.power_btn)
        right_box.append(self.user_btn)
        
        self.append(right_box)
    
    def on_realize(self, widget):
        """Called when widget is realized"""
        self.load_panel_css()
        self.start_updates()
    
    def load_panel_css(self):
        """Apply custom CSS styling"""
        try:
            css_provider = Gtk.CssProvider()
            css_data = """
            .top-panel {
                background: rgba(0, 0, 0, 0.05);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .activities-button {
                background: rgba(53, 132, 228, 0.8);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                transition: all 0.2s ease;
            }
            
            .activities-button:hover {
                background: rgba(53, 132, 228, 1.0);
                transform: scale(1.05);
            }
            
            .panel-clock {
                font-size: 14px;
                font-weight: 500;
                color: @theme_text_color;
            }
            
            .status-button {
                background: transparent;
                border: none;
                border-radius: 6px;
                color: @theme_text_color;
                padding: 6px 10px;
                transition: all 0.2s ease;
                min-width: 40px;
            }
            
            .status-button:hover {
                background: rgba(128, 128, 128, 0.2);
                transform: scale(1.05);
            }
            """
            
            css_provider.load_from_data(css_data.encode())
            
            display = Gdk.Display.get_default()
            if display:
                Gtk.StyleContext.add_provider_for_display(
                    display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                print("✅ Panel CSS loaded successfully")
                
        except Exception as e:
            print(f"❌ Failed to load panel CSS: {e}")
    
    def start_updates(self):
        """Start periodic updates"""
        try:
            GLib.timeout_add_seconds(1, self.update_clock)
            GLib.timeout_add_seconds(5, self.update_ai_status)
            GLib.timeout_add_seconds(30, self.update_battery_status)
            
            self.update_clock()
            GLib.timeout_add_seconds(2, self.update_ai_status)
            GLib.timeout_add_seconds(1, self.update_battery_status)
            
            print("✅ Panel updates started")
            
        except Exception as e:
            print(f"❌ Failed to start panel updates: {e}")
    
    def update_clock(self):
        """Update time and date display"""
        try:
            current_time = time.strftime("%H:%M")
            current_date = time.strftime("%a %b %d")
            self.clock_label.set_markup(f"<b>{current_time}</b>  {current_date}")
            return True
        except Exception as e:
            print(f"Clock update error: {e}")
            return True
    
    def update_ai_status(self):
        """Check AI engine status"""
        try:
            response = requests.get("http://127.0.0.1:8080/health", timeout=1)
            if response.status_code == 200:
                self.ai_icon.set_from_icon_name("face-smile-symbolic")
                self.ai_label.set_text("Ready")
                self.ai_status_btn.set_tooltip_text("AI Engine: Ready")
                return True
        except:
            pass
        
        try:
            response = requests.get("http://127.0.0.1:8080/v1/models", timeout=1)
            if response.status_code in [200, 404]:
                self.ai_icon.set_from_icon_name("face-smile-symbolic")
                self.ai_label.set_text("Ready")
                self.ai_status_btn.set_tooltip_text("AI Engine: Ready")
                return True
        except:
            pass
        
        self.ai_icon.set_from_icon_name("face-sad-symbolic")
        self.ai_label.set_text("Off")
        self.ai_status_btn.set_tooltip_text("AI Engine: Not responding")
        
        return True
    
    def update_battery_status(self):
        """Update battery/power status"""
        try:
            battery_paths = [
                '/sys/class/power_supply/BAT0/capacity',
                '/sys/class/power_supply/BAT1/capacity'
            ]
            
            for battery_path in battery_paths:
                if Path(battery_path).exists():
                    with open(battery_path, 'r') as f:
                        capacity = int(f.read().strip())
                    
                    self.battery_label.set_text(f"{capacity}%")
                    
                    if capacity > 80:
                        icon = "battery-good-symbolic"
                    elif capacity > 50:
                        icon = "battery-medium-symbolic"
                    elif capacity > 20:
                        icon = "battery-low-symbolic"
                    else:
                        icon = "battery-caution-symbolic"
                    
                    self.battery_icon.set_from_icon_name(icon)
                    self.power_btn.set_tooltip_text(f"Battery: {capacity}%")
                    return True
            
            raise FileNotFoundError("No battery detected")
                
        except Exception as e:
            self.battery_label.set_text("AC")
            self.battery_icon.set_from_icon_name("ac-adapter-symbolic")
            self.power_btn.set_tooltip_text("AC Power")
        
        return True
    
    def show_activities(self, widget):
        """Handle Activities button click"""
        print("🎯 PersonalAI Activities clicked")
    
    def show_ai_status(self, widget):
        """Handle AI status button click"""
        print("🤖 AI Status clicked")
    
    def show_user_menu(self, widget):
        """Handle user menu button click"""  
        print("👤 User menu clicked")


if __name__ == '__main__':
    class TestPanelApp(Adw.Application):
        def __init__(self):
            super().__init__(application_id="org.personalai.panel.test")
        
        def do_activate(self):
            win = Adw.ApplicationWindow()
            win.set_title("PersonalAI Panel Test")
            win.set_default_size(1000, 100)
            win.set_application(self)
            
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            main_box.set_margin_top(20)
            main_box.set_margin_bottom(20)
            main_box.set_margin_start(20)
            main_box.set_margin_end(20)
            
            title = Gtk.Label(label="PersonalAIOS Top Panel Test")
            title.add_css_class("title-2")
            main_box.append(title)
            
            panel = TopPanel()
            main_box.append(panel)
            
            info = Gtk.Label(label="Panel components: Activities • Clock • AI Status • Network • Battery • User")
            info.add_css_class("caption")
            info.set_margin_top(20)
            main_box.append(info)
            
            win.set_content(main_box)
            win.present()
    
    print("🚀 Testing PersonalAI Panel...")
    app = TestPanelApp()
    app.run()

