#!/usr/bin/env python3

# Copyright (C) 2025 quantumvoid0 and FelipeFMA 
#
# This program is licensed under the terms of the GNU General Public License v3 + Attribution.
# See the full license text in the LICENSE file or at:
# https://github.com/quantumvoid0/better-control/blob/main/LICENSE
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.


import gi
import os
import psutil
import logging
import shutil
import time
import json
from pydbus import SystemBus
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GLib, Gdk
import subprocess
gi.require_version('Pango', '1.0')
from gi.repository import Gtk, Pango
import threading

SETTINGS_FILE = "settings.json"

def check_dependency(command, name, install_instructions):
    if not shutil.which(command):
        logging.error(f"{name} is required but not installed!\n\nInstall it using:\n{install_instructions}")
        return f"{name} is required but not installed!\n\nInstall it using:\n{install_instructions}"
    return None

dependencies = [
    ("cpupower", "CPU Power Management", "- Debian/Ubuntu: sudo apt install linux-tools-common linux-tools-generic\n- Arch Linux: sudo pacman -S cpupower\n- Fedora: sudo dnf install kernel-tools"),
    ("nmcli", "Network Manager CLI", "- Install NetworkManager package for your distro"),
    ("bluetoothctl", "Bluetooth Control", "- Debian/Ubuntu: sudo apt install bluez\n- Arch Linux: sudo pacman -S bluez bluez-utils\n- Fedora: sudo dnf install bluez"),
    ("pactl", "PulseAudio Control", "- Install PulseAudio or PipeWire depending on your distro"),
    ("brightnessctl", "Brightness Control", "- Debian/Ubuntu: sudo apt install brightnessctl\n- Arch Linux: sudo pacman -S brightnessctl\n- Fedora: sudo dnf install brightnessctl")
]

def check_all_dependencies(parent):
    missing = [check_dependency(cmd, name, inst) for cmd, name, inst in dependencies]
    missing = [msg for msg in missing if msg]
    if missing:
        show_error_dialog(parent, "\n\n".join(missing))
        return False  
    return True

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Better Control is running.")

class WiFiNetworkRow(Gtk.ListBoxRow):
    def __init__(self, network_info):
        super().__init__()
        self.set_margin_top(5)
        self.set_margin_bottom(5)
        self.set_margin_start(10)
        self.set_margin_end(10)
        
        # Parse network information
        parts = network_info.split()
        self.is_connected = '*' in parts[0]
        
        # More reliable SSID extraction
        if len(parts) > 1:
            # Find SSID - sometimes it's after the * mark in different positions
            # For connected networks, using a more reliable method to extract SSID
            if self.is_connected:
                # Try to get the proper SSID from nmcli connection show --active
                try:
                    active_connections = subprocess.getoutput("nmcli -t -f NAME,DEVICE connection show --active").split('\n')
                    for conn in active_connections:
                        if ':' in conn and 'wifi' in subprocess.getoutput(f"nmcli -t -f TYPE connection show '{conn.split(':')[0]}'"):
                            self.ssid = conn.split(':')[0]
                            break
                    else:
                        # Fallback to position-based extraction
                        self.ssid = parts[1]
                except Exception as e:
                    print(f"Error getting active connection name: {e}")
                    self.ssid = parts[1]
            else:
                # For non-connected networks, use the second column
                self.ssid = parts[1]
        else:
            self.ssid = "Unknown"
            
        # Determine security type more precisely
        if "WPA2" in network_info:
            self.security = "WPA2"
        elif "WPA3" in network_info:
            self.security = "WPA3"
        elif "WPA" in network_info:
            self.security = "WPA"
        elif "WEP" in network_info:
            self.security = "WEP"
        else:
            self.security = "Open"
        
        # Improved signal strength extraction
        # Signal is displayed in the "SIGNAL" column of nmcli output (index 6 with our new command)
        signal_value = 0
        try:
            # Now that we use a consistent format with -f, SIGNAL should be in column 7 (index 6)
            if len(parts) > 6 and parts[6].isdigit():
                signal_value = int(parts[6])
                self.signal_strength = f"{signal_value}%"
            else:
                # Fallback: scan through values for something that looks like signal strength
                for i, p in enumerate(parts):
                    # Look for a number between 0-100 that's likely the signal strength
                    if p.isdigit() and 0 <= int(p) <= 100:
                        # Skip if this is likely to be the channel number (typically at index 4)
                        if i != 4:  # Skip CHAN column
                            signal_value = int(p)
                            self.signal_strength = f"{signal_value}%"
                            break
                else:
                    # No valid signal found
                    self.signal_strength = "0%"
        except (IndexError, ValueError) as e:
            print(f"Error parsing signal strength from {parts}: {e}")
            self.signal_strength = "0%"
            signal_value = 0
        
        # Determine signal icon based on signal strength percentage
        if signal_value >= 80:
            icon_name = "network-wireless-signal-excellent-symbolic"
        elif signal_value >= 60:
            icon_name = "network-wireless-signal-good-symbolic"
        elif signal_value >= 40:
            icon_name = "network-wireless-signal-ok-symbolic"
        elif signal_value > 0:
            icon_name = "network-wireless-signal-weak-symbolic"
        else:
            icon_name = "network-wireless-signal-none-symbolic"
            
        # Determine security icon
        if self.security != "Open":
            security_icon = "network-wireless-encrypted-symbolic"
        else:
            security_icon = "network-wireless-symbolic"
        
        # Main container for the row
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(container)
        
        # Network icon
        wifi_icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        container.pack_start(wifi_icon, False, False, 0)
        
        # Left side with SSID and security
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        
        ssid_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        ssid_label = Gtk.Label(label=self.ssid)
        ssid_label.set_halign(Gtk.Align.START)
        if self.is_connected:
            ssid_label.set_markup(f"<b>{self.ssid}</b>")
        ssid_box.pack_start(ssid_label, True, True, 0)
        
        if self.is_connected:
            connected_label = Gtk.Label(label=" (Connected)")
            connected_label.get_style_context().add_class("success-label")
            ssid_box.pack_start(connected_label, False, False, 0)
        
        left_box.pack_start(ssid_box, False, False, 0)
        
        details_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        security_image = Gtk.Image.new_from_icon_name(security_icon, Gtk.IconSize.SMALL_TOOLBAR)
        details_box.pack_start(security_image, False, False, 0)
        
        security_label = Gtk.Label(label=self.security)
        security_label.set_halign(Gtk.Align.START)
        security_label.get_style_context().add_class("dim-label")
        details_box.pack_start(security_label, False, False, 0)
        
        left_box.pack_start(details_box, False, False, 0)
        
        container.pack_start(left_box, True, True, 0)
        
        # Right side with signal strength
        signal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        signal_box.set_halign(Gtk.Align.END)
        
        signal_label = Gtk.Label(label=self.signal_strength)
        signal_box.pack_start(signal_label, False, False, 0)
        
        container.pack_end(signal_box, False, False, 0)
        
        # Store original network info for connection handling
        self.original_network_info = network_info
        
    def get_ssid(self):
        return self.ssid
    
    def get_security(self):
        return self.security
    
    def get_original_network_info(self):
        return self.original_network_info
    
    def is_secured(self):
        return self.security != "Open"

class BatteryTab(Gtk.Box):
    def __init__(self, parent):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self.parent = parent

        self.battery_label = Gtk.Label()
        self.battery_label.set_markup("<b>Battery Metrics</b>")
        self.pack_start(self.battery_label, False, False, 0)

        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(10)
        self.grid.set_row_spacing(10)
        self.pack_start(self.grid, False, False, 0)

        self.labels = {}
        self.value_labels = {}

        battery_keys = ["Charge", "State", "Time Left", "Capacity", "Power", "Voltage", "Model"]
        row = 0
        for key in battery_keys:
            self.labels[key] = Gtk.Label(xalign=0)
            self.labels[key].set_markup(f"<b>{key}:</b> ")
            self.grid.attach(self.labels[key], 0, row, 1, 1)

            self.value_labels[key] = Gtk.Label(xalign=0)
            self.grid.attach(self.value_labels[key], 1, row, 1, 1)
            row += 1

        # Create a loading indicator
        self.loading_spinner = Gtk.Spinner()
        self.loading_spinner.start()
        self.pack_start(self.loading_spinner, False, False, 5)
        
        # Start loading battery info in a background thread
        threading.Thread(target=self.load_battery_info, daemon=True).start()
        
        self.power_mode_label = Gtk.Label(label="Select Power Mode:")
        self.pack_start(self.power_mode_label, False, False, 10)

        self.power_mode_dropdown = Gtk.ComboBoxText()
        self.power_modes = {
            "Power Saving": "powersave",
            "Balanced": "ondemand",
            "Performance": "performance"
        }

        for label in self.power_modes.keys():
            self.power_mode_dropdown.append_text(label)

        settings = load_settings()
        saved_mode = settings.get("power_mode", "ondemand")

        matching_label = next((label for label, value in self.power_modes.items() if value == saved_mode), "Balanced")
        
        if matching_label:
            self.power_mode_dropdown.set_active(list(self.power_modes.keys()).index(matching_label))
        else:
            print(f"Warning: Unknown power mode '{saved_mode}', defaulting to Balanced")
            self.power_mode_dropdown.set_active(list(self.power_modes.keys()).index("Balanced"))

        self.pack_start(self.power_mode_dropdown, False, False, 10)

        self.power_mode_dropdown.connect("changed", self.set_power_mode)

    def load_battery_info(self):
        """Load battery info in background thread and update UI safely"""
        self.refresh_battery_info()
        GLib.timeout_add_seconds(10, self.refresh_battery_info)
        GLib.idle_add(self.loading_spinner.stop)
        GLib.idle_add(self.loading_spinner.hide)

    def set_power_mode_from_string(self, mode_string):
        """
        Set the power mode based on the string passed.
        :param mode_string: The power mode string (e.g., "powersave", "ondemand", "performance")
        """
        if mode_string in self.power_modes.values():

            for key, value in self.power_modes.items():
                if value == mode_string:
                    self.power_mode_dropdown.set_active(list(self.power_modes.keys()).index(key))
                    break
        else:

            self.power_mode_dropdown.set_active(list(self.power_modes.keys()).index("Balanced"))

    def show_password_dialog(self):
        """
        Show a password entry dialog and return the entered password.
        """
        dialog = Gtk.MessageDialog(
            transient_for=self.parent,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Authentication Required",
        )
        dialog.format_secondary_text("Enter your password to change power mode:")

        entry = Gtk.Entry()
        entry.set_visibility(False)  
        entry.set_invisible_char("*")
        entry.set_activates_default(True)  

        box = dialog.get_content_area()
        box.pack_end(entry, False, False, 10)
        entry.show()

        dialog.set_default_response(Gtk.ResponseType.OK)
        response = dialog.run()
        password = entry.get_text() if response == Gtk.ResponseType.OK else None
        dialog.destroy()

        return password

    def set_power_mode(self, widget):
        """Handle power mode change using a GUI password prompt."""
        selected_mode = widget.get_active_text()
        if selected_mode in self.power_modes:
            mode_value = self.power_modes[selected_mode]

            password = self.show_password_dialog()
            if not password:
                return  

            try:
                command = f"echo {password} | sudo -S cpupower frequency-set -g {mode_value}"
                result = subprocess.run(command, shell=True, capture_output=True, text=True)

                if result.returncode != 0:
                    error_message = "cpupower is missing. Please check our GitHub page to see all dependencies and install them."
                    logging.error(error_message)
                    self.parent.show_error_dialog(error_message)  
                else:
                    logging.info(f"Power mode changed to: {selected_mode} ({mode_value})")

                    settings = load_settings()
                    settings["power_mode"] = self.power_modes[selected_mode]  
                    save_settings(settings)

            except subprocess.CalledProcessError as e:
                self.parent.show_error_dialog(f"Failed to set power mode: {e}")

            except FileNotFoundError:
                self.parent.show_error_dialog("cpupower is not installed or not found in PATH.")

    def refresh_battery_info(self):
        battery_devices = subprocess.getoutput("upower -e | grep 'BAT'").split("\n")

        if not battery_devices:
            logger.error("No battery devices found.")
            return True

        for child in self.grid.get_children():
            self.grid.remove(child)

        self.labels = {}
        self.value_labels = {}

        row = 0
        for battery in battery_devices:
            battery_name = battery.split("/")[-1]  

            title_label = Gtk.Label()
            title_label.set_markup(f"<b>Battery: {battery_name}</b>")
            self.grid.attach(title_label, 0, row, 2, 1)
            row += 1

            battery_info = {
                "Charge": subprocess.getoutput(f"upower -i {battery} | grep percentage | awk '{{print $2}}'"),
                "State": subprocess.getoutput(f"upower -i {battery} | grep state | awk '{{print $2}}'"),
                "Time Left": subprocess.getoutput(f"upower -i {battery} | grep 'time to' | awk '{{print $3, $4}}'"),
                "Capacity": subprocess.getoutput(f"upower -i {battery} | grep capacity | awk '{{print $2}}'"),
                "Power": subprocess.getoutput(f"upower -i {battery} | grep 'energy-rate' | awk '{{print $2, $3}}'"),
                "Voltage": subprocess.getoutput(f"upower -i {battery} | grep voltage | awk '{{print $2, $3}}'"),
                "Model": subprocess.getoutput(f"upower -i {battery} | grep model | awk -F': ' '{{print $2}}'")
            }

            for key, value in battery_info.items():
                label = Gtk.Label(xalign=0)
                label.set_markup(f"<b>{key}:</b> ")
                self.grid.attach(label, 0, row, 1, 1)
                self.labels[key] = label

                value_label = Gtk.Label(xalign=0)
                value_label.set_text(value)
                self.grid.attach(value_label, 1, row, 1, 1)
                self.value_labels[key] = value_label

                row += 1  

        self.show_all()  
        return True  

class bettercontrol(Gtk.Window):
    _is_connecting = False

    def __init__(self):
        Gtk.Window.__init__(self, title="Control Center")
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_default_size(1000, 700)
        self.set_resizable(True)

        if "hyprland" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
            subprocess.run(["hyprctl", "keyword", "windowrulev2", "float,class:^(control)$"])

        self.tabs = {}  
        self.tab_visibility = self.load_settings()
        self.loaded_tabs = set()  # Track which tabs have been fully loaded
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.main_container)

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.main_container.pack_start(self.notebook, True, True, 0)
        self.notebook.connect("switch-page", self.on_tab_switch)

        # Create custom CSS for our UI
        css_provider = Gtk.CssProvider()
        css_data = """
            .success-label {
                color: #2ecc71;
                font-weight: bold;
            }
            .warning-label {
                color: #e67e22;
            }
            .error-label {
                color: #e74c3c;
            }
            .wifi-header {
                font-weight: bold;
                font-size: 16px;
            }
            .wifi-button {
                border-radius: 20px;
                padding: 8px 16px;
            }
            .wifi-action-button {
                border-radius: 5px;
                padding: 5px 10px;
                background-color: #3498db;
                color: white;
            }
            .info-notification {
                background-color: #3498db;
                color: white;
            }
        """
        css_provider.load_from_data(css_data.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Create placeholder tabs first with minimal content
        self.create_placeholder_tabs()
        
        # Create tabs with immediate visibility needs first
        self.create_high_priority_tabs()
        
        # Defer loading other tabs
        GLib.timeout_add(100, self.load_deferred_tabs)
        
    def create_placeholder_tabs(self):
        """Create minimal placeholder content for tabs"""
        # Wi-Fi tab placeholder
        if self.tab_visibility.get("Wi-Fi", True):
            wifi_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            wifi_box.set_margin_top(15)
            wifi_box.set_margin_bottom(15)
            wifi_box.set_margin_start(15)
            wifi_box.set_margin_end(15)
            
            loading_label = Gtk.Label(label="Loading Wi-Fi...")
            spinner = Gtk.Spinner()
            spinner.start()
            
            wifi_box.pack_start(spinner, False, False, 10)
            wifi_box.pack_start(loading_label, False, False, 0)
            
            self.tabs["Wi-Fi"] = wifi_box
            self.notebook.append_page(wifi_box, Gtk.Label(label="Wi-Fi"))
        
        # Add other placeholder tabs as needed for CPU, Battery, etc...
        # Similar minimal content with spinners

    def create_high_priority_tabs(self):
        """Create tabs that need to be loaded immediately"""
        # Create any tabs that absolutely must be loaded at startup
        # For now, this is empty since we're deferring all loading
        pass

    def load_deferred_tabs(self):
        """Load remaining tabs after application is visible"""
        # Create real Wi-Fi tab in background
        if self.tab_visibility.get("Wi-Fi", True) and "Wi-Fi" not in self.loaded_tabs:
            threading.Thread(target=self.initialize_wifi_tab, daemon=True).start()
            
        # Schedule other tab initializations with delays
        if self.tab_visibility.get("Bluetooth", True) and "Bluetooth" not in self.loaded_tabs:
            GLib.timeout_add(200, lambda: threading.Thread(target=self.initialize_bluetooth_tab, daemon=True).start())
            
        if self.tab_visibility.get("CPU", True) and "CPU" not in self.loaded_tabs:
            GLib.timeout_add(300, lambda: threading.Thread(target=self.initialize_cpu_tab, daemon=True).start())
            
        if self.tab_visibility.get("Battery", True) and "Battery" not in self.loaded_tabs:
            GLib.timeout_add(400, lambda: threading.Thread(target=self.initialize_battery_tab, daemon=True).start())
            
        # Continue with other tabs...
        return False  # Don't repeat this timeout
    
    def initialize_wifi_tab(self):
        """Initialize the actual Wi-Fi tab content in background"""
        # Create the real Wi-Fi tab content here
        wifi_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        wifi_box.set_margin_top(15)
        wifi_box.set_margin_bottom(15)
        wifi_box.set_margin_start(15)
        wifi_box.set_margin_end(15)
        wifi_box.set_hexpand(True)
        wifi_box.set_vexpand(True)
        
        # Header with Wi-Fi title and status
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_margin_bottom(10)
        
        wifi_icon = Gtk.Image.new_from_icon_name("network-wireless-symbolic", Gtk.IconSize.DIALOG)
        header_box.pack_start(wifi_icon, False, False, 0)
        
        wifi_label = Gtk.Label(label="Wi-Fi Networks")
        wifi_label.get_style_context().add_class("wifi-header")
        header_box.pack_start(wifi_label, False, False, 0)
        
        self.wifi_status_switch = Gtk.Switch()
        self.wifi_status_switch.set_active(True)
        self.wifi_status_switch.connect("notify::active", self.on_wifi_switch_toggled)
        self.wifi_status_switch.set_valign(Gtk.Align.CENTER)
        header_box.pack_end(self.wifi_status_switch, False, False, 0)
        
        wifi_status_label = Gtk.Label(label="Enable Wi-Fi")
        wifi_status_label.set_valign(Gtk.Align.CENTER)
        header_box.pack_end(wifi_status_label, False, False, 5)
        
        wifi_box.pack_start(header_box, False, False, 0)
        
        # Network speed indicators
        speed_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        speed_box.set_margin_bottom(10)
        
        # Upload speed
        upload_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        upload_icon = Gtk.Image.new_from_icon_name("go-up-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        upload_box.pack_start(upload_icon, False, False, 0)
        
        self.upload_label = Gtk.Label(label="0 KB/s")
        upload_box.pack_start(self.upload_label, False, False, 0)
        
        speed_box.pack_start(upload_box, False, False, 0)
        
        # Download speed
        download_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        download_icon = Gtk.Image.new_from_icon_name("go-down-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        download_box.pack_start(download_icon, False, False, 0)
        
        self.download_label = Gtk.Label(label="0 KB/s")
        download_box.pack_start(self.download_label, False, False, 0)
        
        speed_box.pack_start(download_box, False, False, 0)
        
        # Add right-aligned refresh button
        refresh_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        refresh_button = Gtk.Button()
        refresh_button.set_tooltip_text("Refresh Networks")
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_button.add(refresh_icon)
        refresh_button.connect("clicked", self.refresh_wifi)
        refresh_box.pack_end(refresh_button, False, False, 0)
        
        speed_box.pack_end(refresh_box, True, True, 0)
        
        wifi_box.pack_start(speed_box, False, False, 0)
        
        # Network list with scrolling
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_window.set_vexpand(True)
        
        self.wifi_listbox = Gtk.ListBox()
        self.wifi_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.wifi_listbox.set_activate_on_single_click(False)
        self.wifi_listbox.connect("row-activated", self.on_network_row_activated)
        
        scroll_window.add(self.wifi_listbox)
        wifi_box.pack_start(scroll_window, True, True, 0)
        
        # Action buttons
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        action_box.set_margin_top(10)
        
        connect_button = Gtk.Button(label="Connect")
        connect_button.get_style_context().add_class("wifi-action-button")
        connect_button.connect("clicked", self.connect_wifi)
        action_box.pack_start(connect_button, True, True, 0)
        
        disconnect_button = Gtk.Button(label="Disconnect")
        disconnect_button.connect("clicked", self.disconnect_wifi)
        action_box.pack_start(disconnect_button, True, True, 0)
        
        forget_button = Gtk.Button(label="Forget Network")
        forget_button.connect("clicked", self.forget_wifi)
        action_box.pack_start(forget_button, True, True, 0)
        
        wifi_box.pack_start(action_box, False, False, 0)
        
        # Update UI in main thread
        GLib.idle_add(self.replace_placeholder_tab, "Wi-Fi", wifi_box)
        GLib.idle_add(self.refresh_wifi, None)
        
        # Start the network speed monitor after UI is initialized
        GLib.idle_add(lambda: GLib.timeout_add_seconds(1, self.update_network_speed))
        
        # Mark tab as loaded
        self.loaded_tabs.add("Wi-Fi")

    def initialize_battery_tab(self):
        """Initialize the battery tab in background"""
        battery_tab = BatteryTab(self)
        GLib.idle_add(self.replace_placeholder_tab, "Battery", battery_tab)
        self.loaded_tabs.add("Battery")

    def initialize_bluetooth_tab(self):
        """Initialize Bluetooth tab in background"""
        # Implementation similar to initialize_wifi_tab
        # Use GLib.idle_add for UI updates
        self.loaded_tabs.add("Bluetooth")

    def initialize_cpu_tab(self):
        """Initialize CPU tab in background"""
        # Implementation similar to initialize_wifi_tab
        # Use GLib.idle_add for UI updates
        self.loaded_tabs.add("CPU")

    def replace_placeholder_tab(self, tab_name, new_content):
        """Replace placeholder tab with fully loaded content"""
        if tab_name in self.tabs:
            # Find the tab index
            for i in range(self.notebook.get_n_pages()):
                if self.notebook.get_nth_page(i) == self.tabs[tab_name]:
                    # Replace the content
                    self.notebook.remove_page(i)
                    self.notebook.insert_page(new_content, Gtk.Label(label=tab_name), i)
                    self.tabs[tab_name] = new_content
                    new_content.show_all()
                    break

    def on_tab_switch(self, notebook, page, page_num):
        """Handle tab switching with lazy loading"""
        tab_widget = notebook.get_nth_page(page_num)
        tab_name = None
        
        # Find which tab this is
        for name, widget in self.tabs.items():
            if widget == tab_widget:
                tab_name = name
                break
                
        if not tab_name:
            return
            
        # If tab isn't fully loaded yet, prioritize loading it
        if tab_name not in self.loaded_tabs:
            if tab_name == "Wi-Fi":
                threading.Thread(target=self.initialize_wifi_tab, daemon=True).start()
            elif tab_name == "Bluetooth":
                threading.Thread(target=self.initialize_bluetooth_tab, daemon=True).start()
            elif tab_name == "CPU":
                threading.Thread(target=self.initialize_cpu_tab, daemon=True).start()
            elif tab_name == "Battery":
                threading.Thread(target=self.initialize_battery_tab, daemon=True).start()
            # Add other tab initializations as needed

    def refresh_wifi(self, button):
        """Refresh Wi-Fi networks in a background thread"""
        # Only start a new scan if we're not already scanning
        if hasattr(self, '_wifi_scanning') and self._wifi_scanning:
            return
            
        self._wifi_scanning = True
        
        # Clear current list and show loading spinner
        for child in self.wifi_listbox.get_children():
            self.wifi_listbox.remove(child)
            
        loading_row = Gtk.ListBoxRow()
        loading_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        spinner = Gtk.Spinner()
        spinner.start()
        loading_box.pack_start(spinner, False, False, 5)
        loading_label = Gtk.Label(label="Scanning for networks...")
        loading_box.pack_start(loading_label, False, False, 0)
        loading_row.add(loading_box)
        self.wifi_listbox.add(loading_row)
        self.wifi_listbox.show_all()
        
        # Start scanning in background
        threading.Thread(target=self._background_wifi_scan, daemon=True).start()
        
    def _background_wifi_scan(self):
        """Perform Wi-Fi scanning in background thread"""
        try:
            # Get wifi interface name
            ifaces = subprocess.getoutput("nmcli device | grep wifi").split('\n')
            if not ifaces:
                GLib.idle_add(self._update_wifi_list_ui, [], "No Wi-Fi interfaces found")
                return
                
            wifi_iface = ifaces[0].split()[0]
            
            # Get network list with consistent formatting
            networks = subprocess.getoutput(f"nmcli -f IN-USE,SSID,BARS,SECURITY,CHAN,RATE,SIGNAL device wifi list ifname {wifi_iface}").split('\n')
            networks = networks[1:]  # Skip header
        except Exception as e:
            logging.error(f"Error scanning Wi-Fi networks: {e}")
            networks = []
            
        # Update UI in main thread
        GLib.idle_add(self._update_wifi_list_ui, networks)
        
    def _update_wifi_list_ui(self, networks, error_message=None):
        """Update Wi-Fi list UI with scan results"""
        # Clear existing list including loading spinner
        for child in self.wifi_listbox.get_children():
            self.wifi_listbox.remove(child)
            
        if error_message:
            error_row = Gtk.ListBoxRow()
            error_label = Gtk.Label(label=error_message)
            error_label.get_style_context().add_class("error-label")
            error_row.add(error_label)
            self.wifi_listbox.add(error_row)
        elif not networks:
            no_networks_row = Gtk.ListBoxRow()
            no_networks_label = Gtk.Label(label="No networks found")
            no_networks_row.add(no_networks_label)
            self.wifi_listbox.add(no_networks_row)
        else:
            for network in networks:
                try:
                    network_row = WiFiNetworkRow(network)
                    self.wifi_listbox.add(network_row)
                except Exception as e:
                    logging.error(f"Error creating network row: {e}")
                    
        self.wifi_listbox.show_all()
        self._wifi_scanning = False
        return False  # Don't repeat
    
    def connect_wifi(self, button):
        """Connect to the selected WiFi network in a background thread"""
        selected_row = self.wifi_listbox.get_selected_row()
        if not selected_row:
            return
            
        if self._is_connecting:
            return
            
        self._is_connecting = True
        threading.Thread(target=self._background_connect_wifi, args=(selected_row,), daemon=True).start()
    
    def _background_connect_wifi(self, selected_row):
        """Connect to WiFi in background thread"""
        try:
            network_info = selected_row.get_original_network_info()
            ssid = selected_row.get_ssid()
            is_secured = selected_row.is_secured()
            password = None
            
            # If network is secured, ask for password
            if is_secured:
                # Need to get password from user interface in main thread
                password_event = threading.Event()
                GLib.idle_add(self._request_wifi_password, ssid, password_event)
                password_event.wait()  # Wait for password dialog to complete
                
                if not hasattr(self, '_wifi_password') or not self._wifi_password:
                    GLib.idle_add(self._update_connect_status, False, "Connection cancelled")
                    return
                    
                password = self._wifi_password
                
            # Run connection command
            cmd = ["nmcli", "device", "wifi", "connect", ssid]
            if password:
                cmd.extend(["password", password])
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                GLib.idle_add(self._update_connect_status, True, f"Connected to {ssid}")
                # Refresh network list after successful connection
                GLib.idle_add(self.refresh_wifi, None)
            else:
                error_msg = result.stderr.strip() or "Unknown error"
                GLib.idle_add(self._update_connect_status, False, f"Failed to connect: {error_msg}")
                
        except Exception as e:
            logging.error(f"Error connecting to network: {e}")
            GLib.idle_add(self._update_connect_status, False, f"Error: {str(e)}")
        finally:
            self._is_connecting = False
            
    def _request_wifi_password(self, ssid, password_event):
        """Show password dialog and store result"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Connect to {ssid}"
        )
        dialog.format_secondary_text("Enter the network password:")
        
        # Add password entry
        entry = Gtk.Entry()
        entry.set_visibility(False)  # Hide password
        entry.set_activates_default(True)
        box = dialog.get_content_area()
        box.pack_end(entry, False, False, 0)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.show_all()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self._wifi_password = entry.get_text()
        else:
            self._wifi_password = None
            
        dialog.destroy()
        password_event.set()  # Signal that we're done with the password dialog
        return False  # Don't repeat
        
    def _update_connect_status(self, success, message):
        """Update UI with connection status"""
        if success:
            self.show_notification(message)
        else:
            self.show_error_dialog(message)
        return False  # Don't repeat
    
    def disconnect_wifi(self, button):
        """Disconnect from WiFi in background thread"""
        threading.Thread(target=self._background_disconnect_wifi, daemon=True).start()
        
    def _background_disconnect_wifi(self):
        """Disconnect from WiFi in background"""
        try:
            # Find wifi interface
            ifaces = subprocess.getoutput("nmcli device | grep wifi").split('\n')
            if not ifaces:
                GLib.idle_add(self.show_error_dialog, "No Wi-Fi interfaces found")
                return
                
            wifi_iface = ifaces[0].split()[0]
            result = subprocess.run(["nmcli", "device", "disconnect", wifi_iface], capture_output=True, text=True)
            
            if result.returncode == 0:
                GLib.idle_add(self.show_notification, "Disconnected from Wi-Fi")
                GLib.idle_add(self.refresh_wifi, None)
            else:
                GLib.idle_add(self.show_error_dialog, f"Failed to disconnect: {result.stderr.strip()}")
        except Exception as e:
            logging.error(f"Error disconnecting from network: {e}")
            GLib.idle_add(self.show_error_dialog, f"Error: {str(e)}")
    
    def forget_wifi(self, button):
        """Forget the selected WiFi network in background thread"""
        selected_row = self.wifi_listbox.get_selected_row()
        if not selected_row:
            return
            
        ssid = selected_row.get_ssid()
        threading.Thread(target=self._background_forget_wifi, args=(ssid,), daemon=True).start()
        
    def _background_forget_wifi(self, ssid):
        """Forget WiFi network in background"""
        try:
            # Delete connection by name
            result = subprocess.run(["nmcli", "connection", "delete", ssid], capture_output=True, text=True)
            
            if result.returncode == 0:
                GLib.idle_add(self.show_notification, f"Forgot network: {ssid}")
                GLib.idle_add(self.refresh_wifi, None)
            else:
                GLib.idle_add(self.show_error_dialog, f"Failed to forget network: {result.stderr.strip()}")
        except Exception as e:
            logging.error(f"Error forgetting network: {e}")
            GLib.idle_add(self.show_error_dialog, f"Error: {str(e)}")
    
    def on_wifi_switch_toggled(self, switch, gparam):
        """Enable/disable WiFi in background thread"""
        threading.Thread(target=self._background_wifi_toggle, args=(switch.get_active(),), daemon=True).start()
        
    def _background_wifi_toggle(self, enable):
        """Toggle WiFi in background"""
        try:
            if enable:
                result = subprocess.run(["nmcli", "radio", "wifi", "on"], capture_output=True, text=True)
                status_msg = "Wi-Fi enabled"
            else:
                result = subprocess.run(["nmcli", "radio", "wifi", "off"], capture_output=True, text=True)
                status_msg = "Wi-Fi disabled"
                
            if result.returncode == 0:
                GLib.idle_add(self.show_notification, status_msg)
                if enable:
                    GLib.idle_add(self.refresh_wifi, None)
            else:
                GLib.idle_add(self.show_error_dialog, f"Failed to change Wi-Fi state: {result.stderr.strip()}")
        except Exception as e:
            logging.error(f"Error toggling Wi-Fi: {e}")
            GLib.idle_add(self.show_error_dialog, f"Error: {str(e)}")
            # Reset the switch to its previous state
            GLib.idle_add(self._reset_wifi_switch, not enable)
            
    def _reset_wifi_switch(self, state):
        """Reset WiFi switch state without triggering the callback"""
        self.wifi_status_switch.handler_block_by_func(self.on_wifi_switch_toggled)
        self.wifi_status_switch.set_active(state)
        self.wifi_status_switch.handler_unblock_by_func(self.on_wifi_switch_toggled)
        return False
        
    def show_notification(self, message):
        """Show a non-modal notification to the user"""
        notification = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.DESTROY_WITH_PARENT,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        notification.get_content_area().get_style_context().add_class("info-notification")
        notification.set_timeout(2)  # Auto-close after 2 seconds
        notification.show()
        GLib.timeout_add_seconds(2, notification.destroy)

    def connect_bluetooth_device(self, button, mac_address):
        """Connect to a Bluetooth device in background thread"""
        # Show spinner or indicator that we're connecting
        button.set_sensitive(False)
        button.set_label("Connecting...")
        
        # Start connection in background
        threading.Thread(target=self._background_connect_bluetooth, 
                         args=(mac_address, button), 
                         daemon=True).start()
                         
    def _background_connect_bluetooth(self, mac_address, button):
        """Connect to Bluetooth device in background"""
        try:
            # Try pairing first
            pair_result = subprocess.run(
                ["bluetoothctl", "pair", mac_address], 
                capture_output=True, 
                text=True
            )
            
            # Then try connecting
            connect_result = subprocess.run(
                ["bluetoothctl", "connect", mac_address], 
                capture_output=True, 
                text=True
            )
            
            success = "successful" in connect_result.stdout.lower() or "Connection successful" in connect_result.stdout
            
            # Update UI in main thread
            GLib.idle_add(self._update_bluetooth_connection_ui, 
                         success, 
                         mac_address, 
                         button, 
                         connect_result.stdout)
                         
        except Exception as e:
            logging.error(f"Error connecting to Bluetooth device {mac_address}: {e}")
            GLib.idle_add(self._update_bluetooth_connection_ui, 
                         False, 
                         mac_address, 
                         button, 
                         str(e))
                         
    def _update_bluetooth_connection_ui(self, success, mac_address, button, message):
        """Update UI after Bluetooth connection attempt"""
        if success:
            self.show_notification(f"Connected to Bluetooth device")
            # Update the device list to show the new connection status
            self.refresh_bluetooth(None)
        else:
            self.show_error_dialog(f"Failed to connect: {message}")
            # Reset the button
            if button:
                button.set_sensitive(True)
                button.set_label("Connect")
        return False
        
    def disconnect_bluetooth_device(self, button, mac_address):
        """Disconnect from a Bluetooth device in background thread"""
        button.set_sensitive(False)
        button.set_label("Disconnecting...")
        
        threading.Thread(target=self._background_disconnect_bluetooth, 
                         args=(mac_address, button), 
                         daemon=True).start()
                         
    def _background_disconnect_bluetooth(self, mac_address, button):
        """Disconnect from Bluetooth device in background"""
        try:
            result = subprocess.run(
                ["bluetoothctl", "disconnect", mac_address], 
                capture_output=True, 
                text=True
            )
            
            success = "successful" in result.stdout.lower() or "Disconnection successful" in result.stdout
            
            # Update UI in main thread
            GLib.idle_add(self._update_bluetooth_disconnection_ui, 
                         success, 
                         mac_address, 
                         button, 
                         result.stdout)
                         
        except Exception as e:
            logging.error(f"Error disconnecting Bluetooth device {mac_address}: {e}")
            GLib.idle_add(self._update_bluetooth_disconnection_ui, 
                         False, 
                         mac_address, 
                         button, 
                         str(e))
                         
    def _update_bluetooth_disconnection_ui(self, success, mac_address, button, message):
        """Update UI after Bluetooth disconnection attempt"""
        if success:
            self.show_notification(f"Disconnected from Bluetooth device")
            # Update the device list to show the new connection status
            self.refresh_bluetooth(None)
        else:
            self.show_error_dialog(f"Failed to disconnect: {message}")
            # Reset the button
            if button:
                button.set_sensitive(True)
                button.set_label("Disconnect")
        return False
        
    def forget_bluetooth_device(self, button, mac_address):
        """Remove a Bluetooth device from paired devices in background thread"""
        button.set_sensitive(False)
        button.set_label("Forgetting...")
        
        threading.Thread(target=self._background_forget_bluetooth, 
                         args=(mac_address, button), 
                         daemon=True).start()
                         
    def _background_forget_bluetooth(self, mac_address, button):
        """Remove Bluetooth device in background"""
        try:
            result = subprocess.run(
                ["bluetoothctl", "remove", mac_address], 
                capture_output=True, 
                text=True
            )
            
            success = "successful" in result.stdout.lower() or "Device has been removed" in result.stdout
            
            # Update UI in main thread
            GLib.idle_add(self._update_bluetooth_forget_ui, 
                         success, 
                         mac_address, 
                         button, 
                         result.stdout)
                         
        except Exception as e:
            logging.error(f"Error forgetting Bluetooth device {mac_address}: {e}")
            GLib.idle_add(self._update_bluetooth_forget_ui, 
                         False, 
                         mac_address, 
                         button, 
                         str(e))
                         
    def _update_bluetooth_forget_ui(self, success, mac_address, button, message):
        """Update UI after Bluetooth forget attempt"""
        if success:
            self.show_notification(f"Device forgotten successfully")
            # Update the device list
            self.refresh_bluetooth(None)
        else:
            self.show_error_dialog(f"Failed to forget device: {message}")
            # Reset the button
            if button:
                button.set_sensitive(True)
                button.set_label("Forget")
        return False
        
    def enable_bluetooth(self, button):
        """Enable Bluetooth in background thread"""
        button.set_sensitive(False)
        button.set_label("Enabling...")
        
        threading.Thread(target=self._background_enable_bluetooth, 
                         args=(button,), 
                         daemon=True).start()
                         
    def _background_enable_bluetooth(self, button):
        """Enable Bluetooth in background"""
        try:
            # Start the Bluetooth service
            subprocess.run(["systemctl", "start", "bluetooth"])
            
            # Wait for service to become active
            for _ in range(5):
                bt_status = subprocess.run(
                    ["systemctl", "is-active", "bluetooth"], 
                    capture_output=True, 
                    text=True
                ).stdout.strip()
                
                if bt_status == "active":
                    # Service is active
                    GLib.idle_add(self._update_bluetooth_enable_ui, 
                                 True, 
                                 button, 
                                 "Bluetooth enabled successfully")
                    return
                    
                # Wait a bit before checking again
                time.sleep(1)
                
            # If we get here, service didn't activate in time
            GLib.idle_add(self._update_bluetooth_enable_ui, 
                         False, 
                         button, 
                         "Timed out waiting for Bluetooth service to start")
                         
        except Exception as e:
            logging.error(f"Error enabling Bluetooth: {e}")
            GLib.idle_add(self._update_bluetooth_enable_ui, 
                         False, 
                         button, 
                         str(e))
                         
    def _update_bluetooth_enable_ui(self, success, button, message):
        """Update UI after Bluetooth enable attempt"""
        # Reset button state
        button.set_sensitive(True)
        button.set_label("Enable Bluetooth")
        
        if success:
            self.show_notification("Bluetooth enabled")
            self.refresh_bluetooth(None)
        else:
            self.show_error_dialog(f"Failed to enable Bluetooth: {message}")
        return False
        
    def disable_bluetooth(self, button):
        """Disable Bluetooth in background thread"""
        button.set_sensitive(False)
        button.set_label("Disabling...")
        
        threading.Thread(target=self._background_disable_bluetooth, 
                         args=(button,), 
                         daemon=True).start()
                         
    def _background_disable_bluetooth(self, button):
        """Disable Bluetooth in background"""
        try:
            # Stop the Bluetooth service
            subprocess.run(["systemctl", "stop", "bluetooth"])
            
            # Verify service is stopped
            bt_status = subprocess.run(
                ["systemctl", "is-active", "bluetooth"], 
                capture_output=True, 
                text=True
            ).stdout.strip()
            
            success = bt_status != "active"
            
            # Update UI in main thread
            GLib.idle_add(self._update_bluetooth_disable_ui, 
                         success, 
                         button, 
                         "Bluetooth disabled" if success else "Failed to disable Bluetooth")
                         
        except Exception as e:
            logging.error(f"Error disabling Bluetooth: {e}")
            GLib.idle_add(self._update_bluetooth_disable_ui, 
                         False, 
                         button, 
                         str(e))
                         
    def _update_bluetooth_disable_ui(self, success, button, message):
        """Update UI after Bluetooth disable attempt"""
        # Reset button state
        button.set_sensitive(True)
        button.set_label("Disable Bluetooth")
        
        if success:
            self.show_notification("Bluetooth disabled")
            # Clear the device list
            self.bt_listbox.foreach(lambda row: self.bt_listbox.remove(row))
        else:
            self.show_error_dialog(f"Failed to disable Bluetooth: {message}")
        return False
        
    def enable_pairing_mode(self, button=None):
        """Enable Bluetooth pairing mode in background thread"""
        thread = threading.Thread(target=self._background_enable_pairing, daemon=True)
        thread.start()
        
    def _background_enable_pairing(self):
        """Enable Bluetooth pairing in background"""
        try:
            # Set discoverable on
            subprocess.run(["bluetoothctl", "discoverable", "on"], 
                          capture_output=True, 
                          text=True)
                          
            # Set pairable on
            subprocess.run(["bluetoothctl", "pairable", "on"], 
                          capture_output=True, 
                          text=True)
                          
            # Notify user
            GLib.idle_add(self.show_notification, 
                         "Bluetooth pairing mode enabled for 3 minutes")
                         
            # Automatically disable after 3 minutes
            time.sleep(180)
            
            # Disable discoverable
            subprocess.run(["bluetoothctl", "discoverable", "off"], 
                          capture_output=True, 
                          text=True)
                          
        except Exception as e:
            logging.error(f"Error with Bluetooth pairing mode: {e}")
            GLib.idle_add(self.show_error_dialog, 
                         f"Error with Bluetooth pairing mode: {e}")
{{ ... }}
