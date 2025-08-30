#!/usr/bin/env python3
"""
PersonalAIOS - Pure AI Shell 
Only handles AI conversations - all other functionality via Desktop Manager
"""
import gi
import threading
import subprocess
import os
import time
import requests
import json
import sys
import signal
import shutil
from pathlib import Path

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, Adw, Gdk

class MinimalAIShell(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Core AI functionality only
        self.desktop_mode = '--fullscreen-mode' in sys.argv or '--desktop-mode' in sys.argv
        self.server_url = "http://127.0.0.1:8080"
        self.server_process = None
        self.response_timeout = 10
        
        # Connect to Desktop Manager (this is the ONLY external connection)
        self.desktop_manager = None
        self.connect_desktop_manager()
        
        # Initialize AI shell
        if self.desktop_mode:
            print("🖥️ PersonalAIOS Desktop Mode Activated")
            self.setup_desktop_mode()
        
        self.setup_ui()
        self.start_server()
        self.setup_keyboard_shortcuts()
    
    def connect_desktop_manager(self):
        """Connect to Desktop Manager - the ONLY external dependency"""
        try:
            from desktop_manager import DesktopManager
            self.desktop_manager = DesktopManager(self)
            print("✅ Desktop Manager connected - all components available")
        except ImportError:
            print("⚠️ Desktop Manager not found - running in pure AI mode")
            self.desktop_manager = None
        except Exception as e:
            print(f"❌ Desktop Manager connection failed: {e}")
            self.desktop_manager = None
    
    def setup_desktop_mode(self):
        """Configure for desktop session use"""
        self.set_default_size(1920, 1080)
        self.set_decorated(False)
        self.maximize()
        self.set_modal(False)
        self.connect('destroy', self.on_desktop_close)
        print("🚀 Desktop mode configured: Fullscreen AI interface")
    
    def on_desktop_close(self, widget):
        """Handle desktop session close gracefully"""
        if self.desktop_mode:
            print("🔄 Closing PersonalAIOS Desktop Session")
            try:
                subprocess.run(['pkill', '-u', os.getenv('USER'), '-f', 'personalaios-session'], 
                             timeout=2, check=False)
            except:
                pass
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        controller = Gtk.EventControllerKey()
        controller.connect('key-pressed', self.on_key_pressed)
        self.add_controller(controller)
    
    def on_key_pressed(self, controller, keyval, keycode, state):
        """Handle keyboard shortcuts"""
        if (state & Gdk.ModifierType.CONTROL_MASK) and keyval == Gdk.KEY_q:
            if self.desktop_mode:
                print("🔄 Ctrl+Q pressed - Exiting desktop session")
                self.close()
                return True
        
        if (state & Gdk.ModifierType.CONTROL_MASK) and keyval == Gdk.KEY_l:
            self.clear_chat()
            return True
        
        if (state & Gdk.ModifierType.CONTROL_MASK) and keyval == Gdk.KEY_r:
            if self.desktop_mode:
                self.restart_ai_server()
                return True
        
        return False
    
    def restart_ai_server(self):
        """Restart AI server"""
        if hasattr(self, 'ai_status'):
            self.ai_status.set_text("🔄 Restarting AI Engine...")
        if self.server_process:
            self.cleanup()
        threading.Thread(target=self.start_server, daemon=True).start()
    
    def setup_ui(self):
        """Pure AI interface - Desktop Manager handles all UI components"""
        if self.desktop_mode:
            self.set_title("PersonalAIOS Desktop")
            self.set_default_size(1920, 1080)
        else:
            self.set_title("PersonalAIOS • AI Shell")
            self.set_default_size(1000, 750)
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Let Desktop Manager build the complete UI
        if self.desktop_manager:
            self.desktop_manager.build_ui(main_box, self.desktop_mode)
        else:
            self.build_minimal_ui(main_box)
        
        self.set_content(main_box)
        self.load_custom_css()
    
    def build_minimal_ui(self, main_box):
        """Fallback UI when Desktop Manager is not available"""
        if not self.desktop_mode:
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label="PersonalAIOS"))
            main_box.append(header)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        self.chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.chat_box.set_margin_top(24)
        self.chat_box.set_margin_bottom(24)
        self.chat_box.set_margin_start(24)
        self.chat_box.set_margin_end(24)
        
        scrolled.set_child(self.chat_box)
        main_box.append(scrolled)
        
        input_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        input_container.set_margin_top(16)
        input_container.set_margin_bottom(24)
        input_container.set_margin_start(24)
        input_container.set_margin_end(24)
        
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Ask PersonalAIOS anything...")
        self.entry.set_hexpand(True)
        self.entry.connect('activate', self.on_send)
        
        send_btn = Gtk.Button()
        send_btn.set_icon_name("paper-plane-symbolic")
        send_btn.connect('clicked', self.on_send)
        
        input_box.append(self.entry)
        input_box.append(send_btn)
        input_container.append(input_box)
        main_box.append(input_container)
    
    def load_custom_css(self):
        """Load custom CSS for aesthetics"""
        css_provider = Gtk.CssProvider()
        
        if self.desktop_mode:
            css_data = """
            .chat-area {
                background-color: @view_bg_color;
            }
            .large-entry {
                min-height: 52px;
                font-size: 16px;
                border-radius: 26px;
                padding: 0 24px;
            }
            .message-bubble {
                border-radius: 24px;
                padding: 16px 24px;
                margin: 8px 0;
                font-size: 15px;
            }
            .user-message {
                background-color: @accent_color;
                color: @accent_fg_color;
            }
            .ai-message {
                background-color: @card_bg_color;
                border: 1px solid @borders;
            }
            """
        else:
            css_data = """
            .chat-area {
                background-color: @view_bg_color;
            }
            .large-entry {
                min-height: 42px;
                font-size: 14px;
            }
            .message-bubble {
                border-radius: 18px;
                padding: 12px 16px;
                margin: 4px 0;
            }
            .user-message {
                background-color: @accent_color;
                color: @accent_fg_color;
            }
            .ai-message {
                background-color: @card_bg_color;
                border: 1px solid @borders;
            }
            """
        
        css_provider.load_from_data(css_data.encode())
        
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
    
    def start_server(self):
        """Start AI server"""
        threading.Thread(target=self.launch_server, daemon=True).start()
    
    def launch_server(self):
        """Launch AI server with priority order"""
        try:
            if hasattr(self, 'ai_status'):
                GLib.idle_add(self.ai_status.set_text, "🚀 Starting AI Engine...")
            
            server_path, model_path = self.find_llama_server()
            if server_path and model_path:
                print(f"Using llama.cpp server: {server_path} with model: {model_path}")
                self.launch_llama_server(server_path, model_path)
                return
            
            llamafile_path = self.find_llamafile()
            if llamafile_path:
                print(f"Trying llamafile: {llamafile_path}")
                self.launch_llamafile_with_bash(llamafile_path)
                return
            
            raise FileNotFoundError("No AI engine found. Build llama.cpp or download llamafile.")
            
        except Exception as e:
            error_msg = f"AI Engine startup failed: {str(e)}"
            print(error_msg)
            if hasattr(self, 'ai_status'):
                GLib.idle_add(self.ai_status.set_text, "❌ Engine Error")
                GLib.idle_add(self.add_ai_message, f"**Setup Required:**\n{error_msg}")
    
    def find_llama_server(self):
        """Find llama-server and model files"""
        server_paths = [
            "./llama.cpp/build/bin/llama-server",
            "./build/bin/llama-server", 
            "./llama-server",
            "llama-server"
        ]
        
        server_path = None
        for path in server_paths:
            if os.path.exists(path):
                server_path = path
                break
            elif shutil.which(path.split('/')[-1]):
                server_path = path.split('/')[-1]
                break
        
        if not server_path:
            return None, None
        
        model_extensions = ['*.gguf', '*.bin']
        model_path = None
        
        for ext in model_extensions:
            models = list(Path('.').glob(ext))
            if models:
                model_path = str(models[0])
                break
        
        return server_path, model_path
    
    def find_llamafile(self):
        """Find llamafile executable"""
        current_dir = Path(os.getcwd())
        
        llamafile_patterns = [
            "Phi-3-mini-4k-instruct.Q4_0.llamafile",
            "*.llamafile",
            "*phi*llamafile*", 
            "*llamafile*"
        ]
        
        for pattern in llamafile_patterns:
            if '*' in pattern:
                files = list(current_dir.glob(pattern))
                if files:
                    llamafile_path = files[0]
                    os.chmod(llamafile_path, 0o755)
                    return str(llamafile_path.resolve())
            else:
                llamafile_path = current_dir / pattern
                if llamafile_path.exists():
                    os.chmod(llamafile_path, 0o755)
                    return str(llamafile_path.resolve())
        
        return None
    
    def launch_llama_server(self, server_path, model_path):
        """Launch llama.cpp server"""
        cmd = [
            server_path,
            "--model", model_path,
            "--host", "127.0.0.1",
            "--port", "8080",
            "--ctx-size", "2048",
            "--threads", "2",
            "--batch-size", "256",
            "--ubatch-size", "256",
            "--mlock",
            "--no-warmup"
        ]
        
        self.server_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        self.wait_for_server("llama.cpp")
    
    def launch_llamafile_with_bash(self, llamafile_path):
        """Launch llamafile"""
        abs_path = os.path.abspath(llamafile_path)
        
        cmd = [
            "bash", "-c",
            f'"{abs_path}" --server --host 127.0.0.1 --port 8080 --ctx-size 2048 --threads 4 --nobrowser --timeout 300'
        ]
        
        self.server_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            cwd=os.path.dirname(abs_path)
        )
        
        self.wait_for_server("llamafile")
    
    def wait_for_server(self, engine_type):
        """Wait for AI server to become ready"""
        max_attempts = 120
        start_time = time.time()
        
        for attempt in range(max_attempts):
            try:
                endpoints = ["/health", "/v1/models", "/", "/v1/chat/completions"]
                
                for endpoint in endpoints:
                    try:
                        response = requests.get(f"{self.server_url}{endpoint}", timeout=1)
                        if response.status_code in [200, 404, 405]:
                            load_time = time.time() - start_time
                            if hasattr(self, 'ai_status'):
                                GLib.idle_add(self.ai_status.set_text, "🤖 AI Engine Ready")
                            
                            if self.desktop_mode:
                                GLib.idle_add(self.add_ai_message, 
                                    f"**🚀 PersonalAIOS Desktop Active**\n\n"
                                    f"AI-native desktop environment ready.\n"
                                    f"Engine: {engine_type} • Load time: {load_time:.1f}s\n\n"
                                    f"**Desktop Controls:**\n"
                                    f"• Type your queries directly\n"
                                    f"• Ctrl+L to clear conversation\n" 
                                    f"• Ctrl+Q to exit session\n"
                                    f"• Ctrl+R to restart AI engine")
                            else:
                                GLib.idle_add(self.add_ai_message, 
                                    f"**PersonalAIOS Active** 🚀\n\n{engine_type} engine loaded in {load_time:.1f}s")
                            return
                    except requests.exceptions.RequestException:
                        continue
                        
            except Exception as e:
                print(f"Server check error: {e}")
            
            elapsed = time.time() - start_time
            if attempt % 10 == 0:
                if hasattr(self, 'ai_status'):
                    GLib.idle_add(self.ai_status.set_text, f"🔄 Loading AI... {elapsed:.0f}s")
            time.sleep(1)
        
        if hasattr(self, 'ai_status'):
            GLib.idle_add(self.ai_status.set_text, "❌ Engine Timeout")
            GLib.idle_add(self.add_ai_message, "**AI engine failed to start within timeout.**")
    
    def on_send(self, widget):
        """Handle user input - route through Desktop Manager if available"""
        user_input = self.entry.get_text().strip()
        if not user_input:
            return
        
        self.add_user_message(user_input)
        self.entry.set_text("")
        
        # Route through Desktop Manager first
        if self.desktop_manager:
            handled = self.desktop_manager.process_command(user_input)
            if handled:
                return
        
        # Not handled by desktop manager - process as AI request
        if self.is_server_ready():
            threading.Thread(target=self.get_streaming_response, args=(user_input,), daemon=True).start()
        else:
            self.add_ai_message("**AI Engine not ready.** Please wait for initialization.")
    
    def is_server_ready(self):
        """Check if server is ready"""
        try:
            response = requests.get(f"{self.server_url}/v1/models", timeout=0.5)
            return response.status_code in [200, 404]
        except:
            try:
                response = requests.get(f"{self.server_url}/", timeout=0.5)
                return response.status_code in [200, 404, 405]
            except:
                return False
    
    def get_streaming_response(self, user_input):
        """Get streaming AI response"""
        try:
            payload = {
                "messages": [{"role": "user", "content": user_input}],
                "max_tokens": 512,
                "temperature": 0.3,
                "top_p": 0.8,
                "stream": True,
                "stop": ["\nUser:", "\nHuman:", "User:", "Human:", "\n\n"]
            }
            
            response = requests.post(
                f"{self.server_url}/v1/chat/completions",
                json=payload, stream=True, timeout=self.response_timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Server error: {response.status_code}")
            
            accumulated_response = ""
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    
                    if line_text.startswith('data: '):
                        data_text = line_text[6:]
                        
                        if data_text.strip() == '[DONE]':
                            break
                        
                        try:
                            chunk_data = json.loads(data_text)
                            
                            if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                delta = chunk_data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                
                                if content:
                                    accumulated_response += content
                                    GLib.idle_add(self.update_streaming_display, accumulated_response)
                                
                        except json.JSONDecodeError:
                            continue
            
            GLib.idle_add(self.finalize_streaming)
            
        except Exception as e:
            error_msg = f"Response failed: {str(e)}"
            GLib.idle_add(self.add_ai_message, f"**Response Error:** {error_msg}")
    
    def update_streaming_display(self, partial_response):
        """Update streaming display"""
        try:
            if hasattr(self, 'current_streaming_widget') and self.current_streaming_widget:
                self.chat_box.remove(self.current_streaming_widget)
            
            clean_response = partial_response.strip()
            if clean_response:
                self.current_streaming_widget = self.create_message_widget("PersonalAI", clean_response)
                self.chat_box.append(self.current_streaming_widget)
                self.scroll_to_bottom()
                
        except Exception as e:
            print(f"UI update error: {e}")
    
    def finalize_streaming(self):
        """Clean up after streaming"""
        if hasattr(self, 'current_streaming_widget'):
            delattr(self, 'current_streaming_widget')
    
    def create_message_widget(self, sender, message, is_user=False):
        """Create message bubble"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        sender_label = Gtk.Label(label=sender)
        sender_label.add_css_class("caption-heading")
        
        time_label = Gtk.Label(label=time.strftime("%H:%M"))
        time_label.add_css_class("caption")
        
        if is_user:
            info_box.set_halign(Gtk.Align.END)
            info_box.append(time_label)
            info_box.append(sender_label)
        else:
            info_box.set_halign(Gtk.Align.START)
            info_box.append(sender_label)
            info_box.append(time_label)
        
        content_label = Gtk.Label(label=message)
        content_label.set_wrap(True)
        content_label.set_wrap_mode(2)
        content_label.set_selectable(True)
        content_label.set_xalign(0 if not is_user else 1)
        
        if self.desktop_mode:
            content_label.set_margin_start(24)
            content_label.set_margin_end(24)
            content_label.set_margin_top(16)
            content_label.set_margin_bottom(16)
        else:
            content_label.set_margin_start(16)
            content_label.set_margin_end(16)
            content_label.set_margin_top(12)
            content_label.set_margin_bottom(12)
        
        content_label.add_css_class("message-bubble")
        if is_user:
            content_label.add_css_class("user-message")
            container.set_halign(Gtk.Align.END)
            container.set_margin_start(120 if self.desktop_mode else 80)
        else:
            content_label.add_css_class("ai-message")
            container.set_halign(Gtk.Align.START)
            container.set_margin_end(120 if self.desktop_mode else 80)
        
        container.append(info_box)
        container.append(content_label)
        return container
    
    def add_user_message(self, message):
        """Add user message"""
        widget = self.create_message_widget("You", message, is_user=True)
        self.chat_box.append(widget)
        self.scroll_to_bottom()
    
    def add_ai_message(self, message):
        """Add AI message"""
        widget = self.create_message_widget("PersonalAI", message, is_user=False)
        self.chat_box.append(widget)
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Auto-scroll to bottom"""
        def do_scroll():
            scrolled = self.chat_box.get_parent()
            if scrolled and isinstance(scrolled, Gtk.ScrolledWindow):
                vadj = scrolled.get_vadjustment()
                vadj.set_value(vadj.get_upper() - vadj.get_page_size())
            return False
        
        GLib.idle_add(do_scroll)
    
    def clear_chat(self, widget=None):
        """Clear conversation"""
        child = self.chat_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.chat_box.remove(child)
            child = next_child
        
        message = "**Conversation cleared.** Ready for new PersonalAIOS interactions."
        self.add_ai_message(message)
    
    def cleanup(self):
        """Clean shutdown"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
            except Exception as e:
                print(f"Cleanup error: {e}")


class MinimalAIApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="org.personalai.desktop")
        self.window = None
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle signals for clean shutdown"""
        if self.window:
            self.window.cleanup()
        sys.exit(0)
    
    def do_activate(self):
        if not self.window:
            self.window = MinimalAIShell(application=self)
        self.window.present()
    
    def do_shutdown(self):
        if self.window:
            self.window.cleanup()
        super().do_shutdown()


if __name__ == '__main__':
    if '--fullscreen-mode' in sys.argv or '--desktop-mode' in sys.argv:
        print("🚀 PersonalAIOS • Desktop Mode")
        print("   Pure AI Interface • Fullscreen Experience")
        print("   Shortcuts: Ctrl+Q (Exit) | Ctrl+L (Clear) | Ctrl+R (Restart)")
    else:
        print("🚀 PersonalAIOS • High-Performance AI Shell")
        print("   Pure AI-Native Interface • Modular Architecture")
    
    app = MinimalAIApp()
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n🔄 Shutting down PersonalAIOS...")
        sys.exit(0)

