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

        self.refresh_battery_info()
        GLib.timeout_add_seconds(10, self.refresh_battery_info)

        self.power_mode_label = Gtk.Label(label="Select Power Mode:")
        self.pack_start(self.power_mode_label, False, False, 10)

        self.power_mode_dropdown = Gtk.ComboBoxText()
        self.power_modes = {
            "Power Saving": "powersave",
            "Balanced": "ondemand",
            "Performance": "performance"
        }

        for mode in self.power_modes.keys():
            self.power_mode_dropdown.append_text(mode)

        settings = load_settings()
        saved_mode = settings.get("power_mode", "ondemand")

        self.power_mode_dropdown = Gtk.ComboBoxText()
        self.power_modes = {
            "Power Saving": "powersave",
            "Balanced": "ondemand",
            "Performance": "performance"
        }

        for label in self.power_modes.keys():
            self.power_mode_dropdown.append_text(label)

        matching_label = next((label for label, value in self.power_modes.items() if value == saved_mode), "Balanced")
        self.power_mode_dropdown.set_active(list(self.power_modes.keys()).index(matching_label))

        if matching_label:
            self.power_mode_dropdown.set_active(list(self.power_modes.keys()).index(matching_label))
        else:
            print(f"Warning: Unknown power mode '{saved_mode}', defaulting to Balanced")
            self.power_mode_dropdown.set_active(list(self.power_modes.keys()).index("Balanced"))

        self.pack_start(self.power_mode_dropdown, False, False, 10)

        self.power_mode_dropdown.connect("changed", self.set_power_mode)

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

class BluetoothDeviceRow(Gtk.ListBoxRow):
    def __init__(self, device_info):
        super().__init__()
        self.set_margin_top(5)
        self.set_margin_bottom(5)
        self.set_margin_start(10)
        self.set_margin_end(10)
        
        # Parse device information
        parts = device_info.split(" ")
        if len(parts) < 2:
            return
            
        self.mac_address = parts[1]
        self.device_name = " ".join(parts[2:]) if len(parts) > 2 else self.mac_address
        
        # Check connection status
        try:
            status_output = subprocess.getoutput(f"bluetoothctl info {self.mac_address}")
            self.is_connected = "Connected: yes" in status_output
            
            # Get device type from status output
            self.device_type = "Unknown"
            for line in status_output.split("\n"):
                if "Icon:" in line:
                    icon_type = line.split(":")[1].strip()
                    if "phone" in icon_type:
                        self.device_type = "Phone"
                    elif "computer" in icon_type:
                        self.device_type = "Computer"
                    elif "audio" in icon_type or "headset" in icon_type or "headphone" in icon_type:
                        self.device_type = "Audio"
                    elif "input" in icon_type:
                        self.device_type = "Input Device"
                    else:
                        self.device_type = icon_type.capitalize()
                    break
            
            # Is the device paired
            self.is_paired = "Paired: yes" in status_output
        except Exception as e:
            print(f"Error checking status for {self.mac_address}: {e}")
            self.is_connected = False
            self.is_paired = False
            self.device_type = "Unknown"
            
        # Determine appropriate icon based on device type and connection status
        if self.device_type == "Phone":
            icon_name = "phone-symbolic"
        elif self.device_type == "Computer":
            icon_name = "computer-symbolic"
        elif self.device_type == "Audio":
            icon_name = "audio-headphones-symbolic"
        elif self.device_type == "Input Device":
            icon_name = "input-mouse-symbolic"
        else:
            icon_name = "bluetooth-symbolic"
            
        # Main container for the row
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add(container)
        
        # Device icon
        bt_icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        container.pack_start(bt_icon, False, False, 0)
        
        # Left side with device name and type
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        
        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        name_label = Gtk.Label(label=self.device_name)
        name_label.set_halign(Gtk.Align.START)
        if self.is_connected:
            name_label.set_markup(f"<b>{self.device_name}</b>")
        name_box.pack_start(name_label, True, True, 0)
        
        if self.is_connected:
            connected_label = Gtk.Label(label=" (Connected)")
            connected_label.get_style_context().add_class("success-label")
            name_box.pack_start(connected_label, False, False, 0)
        
        left_box.pack_start(name_box, False, False, 0)
        
        details_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        # Add paired status icon if paired
        if self.is_paired:
            paired_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
            details_box.pack_start(paired_icon, False, False, 0)
            
            paired_label = Gtk.Label(label="Paired")
            paired_label.set_halign(Gtk.Align.START)
            paired_label.get_style_context().add_class("dim-label")
            details_box.pack_start(paired_label, False, False, 0)
        
        # Add device type
        if self.device_type != "Unknown":
            type_label = Gtk.Label(label=self.device_type)
            type_label.set_halign(Gtk.Align.START)
            type_label.get_style_context().add_class("dim-label")
            details_box.pack_start(type_label, False, False, 5)
            
        left_box.pack_start(details_box, False, False, 0)
        
        container.pack_start(left_box, True, True, 0)
        
        # Right side with action buttons
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        action_box.set_halign(Gtk.Align.END)
        
        # Store original device info for connection handling
        self.original_device_info = device_info
    
    def get_name(self):
        return self.device_name
    
    def get_mac_address(self):
        return self.mac_address
    
    def get_original_device_info(self):
        return self.original_device_info
    
    def is_device_connected(self):
        return self.is_connected
        
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

        # Create the Wi-Fi tab
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
        
        GLib.timeout_add_seconds(1, self.update_network_speed)
        
        scrolled_wifi = Gtk.ScrolledWindow()
        scrolled_wifi.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.tabs["Wi-Fi"] = wifi_box
        if self.tab_visibility.get("Wi-Fi", True):
            self.notebook.append_page(wifi_box, Gtk.Label(label="Wi-Fi"))
            # Start loading WiFi networks
            self.refresh_wifi(None)
            
            # Add signal for tab change to refresh WiFi when tab is selected
            self.notebook.connect("switch-page", self.on_tab_switched)
        
        # Create the Bluetooth tab with similar style to WiFi tab
        bluetooth_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        bluetooth_box.set_margin_top(15)
        bluetooth_box.set_margin_bottom(15)
        bluetooth_box.set_margin_start(15)
        bluetooth_box.set_margin_end(15)
        bluetooth_box.set_hexpand(True)
        bluetooth_box.set_vexpand(True)
        
        # Header with Bluetooth title and status
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_margin_bottom(10)
        
        bt_icon = Gtk.Image.new_from_icon_name("bluetooth-symbolic", Gtk.IconSize.DIALOG)
        header_box.pack_start(bt_icon, False, False, 0)
        
        bt_label = Gtk.Label(label="Bluetooth Devices")
        bt_label.get_style_context().add_class("wifi-header")
        header_box.pack_start(bt_label, False, False, 0)
        
        self.bt_status_switch = Gtk.Switch()
        # Get current bluetooth state
        bt_status = subprocess.run(
            ["systemctl", "is-active", "bluetooth"], capture_output=True, text=True
        ).stdout.strip() == "active"
        self.bt_status_switch.set_active(bt_status)
        self.bt_status_switch.connect("notify::active", self.on_bt_switch_toggled)
        self.bt_status_switch.set_valign(Gtk.Align.CENTER)
        header_box.pack_end(self.bt_status_switch, False, False, 0)
        
        bt_status_label = Gtk.Label(label="Enable Bluetooth")
        bt_status_label.set_valign(Gtk.Align.CENTER)
        header_box.pack_end(bt_status_label, False, False, 5)
        
        bluetooth_box.pack_start(header_box, False, False, 0)
        
        # Add right-aligned refresh button
        refresh_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        refresh_box.set_margin_bottom(10)
        
        # Add pairing button
        pairing_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        pairing_mode_button = Gtk.Button()
        pairing_mode_button.set_tooltip_text("Make Device Discoverable")
        pairing_icon = Gtk.Image.new_from_icon_name("network-transmit-receive-symbolic", Gtk.IconSize.BUTTON)
        pairing_mode_button.add(pairing_icon)
        pairing_mode_button.connect("clicked", self.enable_pairing_mode)
        pairing_box.pack_start(pairing_mode_button, False, False, 0)
        
        refresh_box.pack_start(pairing_box, False, False, 0)
        
        # Add refresh button
        refresh_button = Gtk.Button()
        refresh_button.set_tooltip_text("Refresh Devices")
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_button.add(refresh_icon)
        refresh_button.connect("clicked", self.refresh_bluetooth)
        refresh_box.pack_end(refresh_button, True, True, 0)
        
        bluetooth_box.pack_start(refresh_box, False, False, 0)
        
        # Network list with scrolling
        scroll_window = Gtk.ScrolledWindow()
        scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_window.set_vexpand(True)
        
        self.bt_listbox = Gtk.ListBox()
        self.bt_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.bt_listbox.set_activate_on_single_click(False)
        self.bt_listbox.connect("row-activated", self.on_bluetooth_row_activated)
        
        scroll_window.add(self.bt_listbox)
        bluetooth_box.pack_start(scroll_window, True, True, 0)
        
        # Action buttons
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        action_box.set_margin_top(10)
        
        connect_button = Gtk.Button(label="Connect")
        connect_button.get_style_context().add_class("wifi-action-button")
        connect_button.connect("clicked", self.connect_bluetooth_selected)
        action_box.pack_start(connect_button, True, True, 0)
        
        disconnect_button = Gtk.Button(label="Disconnect")
        disconnect_button.connect("clicked", self.disconnect_bluetooth_selected)
        action_box.pack_start(disconnect_button, True, True, 0)
        
        forget_button = Gtk.Button(label="Forget Device")
        forget_button.connect("clicked", self.forget_bluetooth_selected)
        action_box.pack_start(forget_button, True, True, 0)
        
        bluetooth_box.pack_start(action_box, False, False, 0)
        
        # Create the scrolled window
        scrolled_bt = Gtk.ScrolledWindow()
        scrolled_bt.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_bt.add(bluetooth_box)

        self.tabs["Bluetooth"] = scrolled_bt
        if self.tab_visibility.get("Bluetooth", True):  
            self.notebook.append_page(scrolled_bt, Gtk.Label(label="Bluetooth"))

        volume_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        volume_box.set_margin_top(10)
        volume_box.set_margin_bottom(10)
        volume_box.set_margin_start(10)
        volume_box.set_margin_end(10)
        volume_box.set_hexpand(True)
        volume_box.set_vexpand(True)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        volume_box.pack_start(grid, True, True, 0)

        mainlabel = Gtk.Label(label="Quick Controls")
        self.apply_css(mainlabel)

        volume_label = Gtk.Label(label="Speaker Volume")
        self.apply_css(volume_label)
        mic_label = Gtk.Label(label="Microphone Volume")  
        self.apply_css(mic_label)
        volume_label.set_xalign(0)
        mic_label.set_xalign(0)
        mainlabel.set_xalign(0)

        self.volume_button = Gtk.Button(label=f"Mute/Unmute Speaker")
        self.volume_button.connect("clicked", self.mute)
        self.volume_button.set_vexpand(False)  
        self.volume_button.set_valign(Gtk.Align.START)  

        self.volume_mic = Gtk.Button(label=f"Mute/Unmute Mic")
        self.volume_mic.connect("clicked", self.micmute)
        self.volume_mic.set_vexpand(False)  
        self.volume_mic.set_valign(Gtk.Align.START)  

        self.sink_dropdown = Gtk.ComboBoxText()
        self.sink_dropdown.connect("changed", self.on_sink_selected)
        self.sink_dropdown.set_size_request(200, 40)  
        self.sink_dropdown.set_vexpand(False)  
        self.sink_dropdown.set_valign(Gtk.Align.CENTER)  
        grid.attach(self.sink_dropdown, 0, 6, 5, 1)  

        self.update_sink_list()

        GLib.timeout_add_seconds(3, self.update_sink_list_repeated)  

        self.volume_zero = Gtk.Button(label="0%")
        self.volume_zero.set_size_request(60, 35)  
        self.volume_zero.set_vexpand(False)  
        self.volume_zero.set_valign(Gtk.Align.START)  
        self.volume_zero.connect("clicked", self.vzero)

        self.volume_tfive = Gtk.Button(label="25%")
        self.volume_tfive.set_size_request(60, 35)  
        self.volume_tfive.set_vexpand(False)  
        self.volume_tfive.set_valign(Gtk.Align.START)  
        self.volume_tfive.connect("clicked", self.vtfive)

        self.volume_fifty = Gtk.Button(label="50%")
        self.volume_fifty.set_size_request(60, 35)  
        self.volume_fifty.set_vexpand(False)  
        self.volume_fifty.set_valign(Gtk.Align.START)  
        self.volume_fifty.connect("clicked", self.vfifty)

        self.volume_sfive = Gtk.Button(label="75%")
        self.volume_sfive.set_size_request(60, 35)  
        self.volume_sfive.set_vexpand(False)  
        self.volume_sfive.set_valign(Gtk.Align.START)  
        self.volume_sfive.connect("clicked", self.vsfive)

        self.volume_hund = Gtk.Button(label="100%")
        self.volume_hund.set_size_request(60, 35)  
        self.volume_hund.set_vexpand(False)  
        self.volume_hund.set_valign(Gtk.Align.START)  
        self.volume_hund.connect("clicked", self.vhund)

        self.mic_zero = Gtk.Button(label="0%")
        self.mic_zero.set_size_request(60, 35)  
        self.mic_zero.set_vexpand(False)  
        self.mic_zero.set_valign(Gtk.Align.START)  
        self.mic_zero.connect("clicked", self.mzero)

        self.mic_tfive = Gtk.Button(label="25%")
        self.mic_tfive.set_size_request(60, 35)  
        self.mic_tfive.set_vexpand(False)  
        self.mic_tfive.set_valign(Gtk.Align.START)  
        self.mic_tfive.connect("clicked", self.mtfive)

        self.mic_fifty = Gtk.Button(label="50%")
        self.mic_fifty.set_size_request(60, 35)  
        self.mic_fifty.set_vexpand(False)  
        self.mic_fifty.set_valign(Gtk.Align.START)  
        self.mic_fifty.connect("clicked", self.mfifty)

        self.mic_sfive = Gtk.Button(label="75%")
        self.mic_sfive.set_size_request(60, 35)  
        self.mic_sfive.set_vexpand(False)  
        self.mic_sfive.set_valign(Gtk.Align.START)  
        self.mic_sfive.connect("clicked", self.msfive)

        self.mic_hund = Gtk.Button(label="100%")
        self.mic_hund.set_size_request(60, 35)  
        self.mic_hund.set_vexpand(False)  
        self.mic_hund.set_valign(Gtk.Align.START)  
        self.mic_hund.connect("clicked", self.mhund)

        self.volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.volume_scale.set_hexpand(True)  
        self.volume_scale.set_value(self.get_current_volume())
        self.volume_scale.set_value_pos(Gtk.PositionType.LEFT)  
        self.volume_scale.connect("value-changed", self.set_volume)

        self.mic_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.mic_scale.set_hexpand(True)  
        self.mic_scale.set_value_pos(Gtk.PositionType.BOTTOM)  
        self.mic_scale.set_value(self.get_current_mic_volume())
        self.mic_scale.connect("value-changed", self.set_mic_volume)
        self.mic_scale.set_value_pos(Gtk.PositionType.LEFT)

        self.volume_scale.set_margin_top(50)
        self.mic_scale.set_margin_top(50)
        self.sink_dropdown.set_margin_top(50)

        grid.attach(self.volume_zero, 0, 2, 1, 1)
        grid.attach(self.volume_tfive, 1, 2, 1, 1)        
        grid.attach(self.volume_fifty, 2, 2, 1, 1)
        grid.attach(self.volume_sfive, 3, 2, 1, 1)
        grid.attach(self.volume_hund, 4, 2, 1, 1)

        grid.attach(self.mic_zero, 0, 4, 1, 1)
        grid.attach(self.mic_tfive, 1, 4, 1, 1)        
        grid.attach(self.mic_fifty, 2, 4, 1, 1)
        grid.attach(self.mic_sfive, 3, 4, 1, 1)
        grid.attach(self.mic_hund, 4, 4, 1, 1)

        grid.attach(self.volume_mic, 0, 6, 1, 1)
        grid.attach(self.volume_button, 1, 6, 1, 1)
        grid.attach(volume_label, 0, 1, 5, 1)  
        grid.attach(mic_label, 0, 3, 5, 1)  
        grid.attach(self.volume_scale, 0, 2, 5, 1) 
        grid.attach(self.mic_scale,0,4,5,1)
        grid.attach(mainlabel,0,5,5,1)

        scrolled_volume = Gtk.ScrolledWindow()
        scrolled_volume.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_volume.add(volume_box)

        self.tabs["Volume"] = scrolled_volume
        if self.tab_visibility.get("Volume", True):  
            self.notebook.append_page(scrolled_volume, Gtk.Label(label="Volume"))

        brightness_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        brightness_box.set_margin_top(10)
        brightness_box.set_margin_bottom(10)
        brightness_box.set_margin_start(10)
        brightness_box.set_margin_end(10)
        brightness_box.set_hexpand(True)
        brightness_box.set_vexpand(True)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)  
        grid.set_row_homogeneous(False)    
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        brightness_box.pack_start(grid, True, True, 0)

        self.brightness_label = Gtk.Label(label="Brightness")
        grid.attach(self.brightness_label, 0,0,5,1)

        self.brightness_zero = Gtk.Button(label="0%")
        self.brightness_zero.set_size_request(80, 30)
        self.brightness_zero.connect("clicked", self.zero)
        self.brightness_zero.set_vexpand(False)
        self.brightness_zero.set_valign(Gtk.Align.START)

        self.brightness_tfive = Gtk.Button(label="25%")
        self.brightness_tfive.set_size_request(80, 30)
        self.brightness_tfive.connect("clicked", self.tfive)
        self.brightness_tfive.set_vexpand(False)
        self.brightness_tfive.set_valign(Gtk.Align.START)

        self.brightness_fifty = Gtk.Button(label="50%")
        self.brightness_fifty.set_size_request(80, 30)
        self.brightness_fifty.connect("clicked", self.fifty)
        self.brightness_fifty.set_vexpand(False)
        self.brightness_fifty.set_valign(Gtk.Align.START)

        self.brightness_sfive = Gtk.Button(label="75%")
        self.brightness_sfive.set_size_request(80, 30)
        self.brightness_sfive.connect("clicked", self.sfive)
        self.brightness_sfive.set_vexpand(False)
        self.brightness_sfive.set_valign(Gtk.Align.START)

        self.brightness_hund = Gtk.Button(label="100%")
        self.brightness_hund.set_size_request(80, 30)
        self.brightness_hund.connect("clicked", self.hund)
        self.brightness_hund.set_vexpand(False)
        self.brightness_hund.set_valign(Gtk.Align.START)

        grid.attach(self.brightness_zero, 0, 1, 1, 1)   
        grid.attach(self.brightness_tfive, 1, 1, 1, 1)  
        grid.attach(self.brightness_fifty, 2, 1, 1, 1)  
        grid.attach(self.brightness_sfive, 3, 1, 1, 1)  
        grid.attach(self.brightness_hund, 4, 1, 1, 1)   

        self.brightness_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.brightness_scale.set_hexpand(True)
        self.brightness_scale.set_value(self.get_current_brightness())
        self.brightness_scale.set_value_pos(Gtk.PositionType.BOTTOM)
        self.brightness_scale.connect("value-changed", self.set_brightness)

        grid.attach(self.brightness_scale, 0, 2, 5, 1)  

        self.blue_light_label = Gtk.Label(label="Blue Light Filter")

        self.blue_zero = Gtk.Button(label="0%")
        self.blue_zero.set_size_request(80, 30)
        self.blue_zero.connect("clicked", self.bzero)
        self.blue_zero.set_vexpand(False)
        self.blue_zero.set_valign(Gtk.Align.START)

        self.blue_tfive = Gtk.Button(label="25%")
        self.blue_tfive.set_size_request(80, 30)
        self.blue_tfive.connect("clicked", self.btfive)
        self.blue_tfive.set_vexpand(False)
        self.blue_tfive.set_valign(Gtk.Align.START)

        self.blue_fifty = Gtk.Button(label="50%")
        self.blue_fifty.set_size_request(80, 30)
        self.blue_fifty.connect("clicked", self.bfifty)
        self.blue_fifty.set_vexpand(False)
        self.blue_fifty.set_valign(Gtk.Align.START)

        self.blue_sfive = Gtk.Button(label="75%")
        self.blue_sfive.set_size_request(80, 30)
        self.blue_sfive.connect("clicked", self.bsfive)
        self.blue_sfive.set_vexpand(False)
        self.blue_sfive.set_valign(Gtk.Align.START)

        self.blue_hund = Gtk.Button(label="100%")
        self.blue_hund.set_size_request(80, 30)
        self.blue_hund.connect("clicked", self.bhund)
        self.blue_hund.set_vexpand(False)
        self.blue_hund.set_valign(Gtk.Align.START)

        self.blue_light_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 2500, 6500, 100)
        self.blue_light_slider.set_value(6500)  
        self.blue_light_slider.set_value_pos(Gtk.PositionType.BOTTOM)
        self.blue_light_slider.connect("value-changed", self.set_bluelight_filter)

        settings = load_settings()
        saved_gamma = settings.get("gamma", 6500)
        self.blue_light_slider.set_value(saved_gamma)
        self.blue_light_slider.connect("value-changed", self.set_bluelight_filter)

        grid.attach(self.blue_light_label,0,3,5,1)
        grid.attach(self.blue_zero, 0, 4, 1, 1)   
        grid.attach(self.blue_tfive, 1, 4, 1, 1)  
        grid.attach(self.blue_fifty, 2, 4, 1, 1)  
        grid.attach(self.blue_sfive, 3, 4, 1, 1)  
        grid.attach(self.blue_hund, 4, 4, 1, 1)   
        grid.attach(self.blue_light_slider, 0, 5, 5, 1)  

        self.tabs["Display"] = brightness_box
        if self.tab_visibility.get("Display", True):  
            self.notebook.append_page(brightness_box, Gtk.Label(label="Display"))

        app_volume_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        app_volume_box.set_margin_top(10)
        app_volume_box.set_margin_bottom(10)
        app_volume_box.set_margin_start(10)
        app_volume_box.set_margin_end(10)
        app_volume_box.set_hexpand(True)
        app_volume_box.set_vexpand(True)

        self.app_volume_listbox = Gtk.ListBox()
        self.app_volume_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        app_volume_box.pack_start(self.app_volume_listbox, True, True, 0)

        refresh_app_volume_button = Gtk.Button(label="Refresh Applications")
        refresh_app_volume_button.connect("clicked", self.refresh_app_volume)
        app_volume_box.pack_start(refresh_app_volume_button, False, False, 0)

        GLib.timeout_add_seconds(1, self.refresh_app_volume_realtime) 

        scrolled_app_volume = Gtk.ScrolledWindow()
        scrolled_app_volume.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_app_volume.add(app_volume_box)

        self.tabs["Application Volume"] = scrolled_app_volume
        if self.tab_visibility.get("Application Volume", True):  
            self.notebook.append_page(scrolled_app_volume, Gtk.Label(label="Application Volume"))

        self.battery_tab = BatteryTab(self)
        self.tabs["Battery"] = self.battery_tab
        if self.tab_visibility.get("Battery", True):  
            self.notebook.append_page(self.battery_tab, Gtk.Label(label="Battery"))

        GLib.idle_add(self.notebook.set_current_page, 0)

        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        settings_box.set_margin_top(10)
        settings_box.set_margin_bottom(10)
        settings_box.set_margin_start(10)
        settings_box.set_margin_end(10)
        settings_box.set_hexpand(True)
        settings_box.set_vexpand(True)

        self.tabs["Settings"] = settings_box  

        if self.tab_visibility.get("Settings", True):  
            self.notebook.append_page(settings_box, Gtk.Label(label="Settings"))

        self.populate_settings_tab()

        GLib.idle_add(self.notebook.set_current_page, 0)

        self.update_button_labels()

    def bzero(self, button):
        if shutil.which("gammastep"):
            self.blue_light_slider.set_value(2500)
        else:
            self.show_error_dialog("gammastep is missing. please check our github page to see all dependencies and install them")

    def btfive(self, button):
        if shutil.which("gammastep"):
            self.blue_light_slider.set_value(3500)
        else:
            self.show_error_dialog("gammastep is missing. please check our github page to see all dependencies and install them")

    def bfifty(self, button):
        if shutil.which("gammastep"):
            self.blue_light_slider.set_value(4500)
        else:
            self.show_error_dialog("gammastep is missing. please check our github page to see all dependencies and install them")

    def bsfive(self, button):
        if shutil.which("gammastep"):
            self.blue_light_slider.set_value(5500)
        else:
            self.show_error_dialog("gammastep is missing. please check our github page to see all dependencies and install them")

    def bhund(self, button):
        if shutil.which("gammastep"):
            self.blue_light_slider.set_value(6500)
        else:
            self.show_error_dialog("gammastep is missing. please check our github page to see all dependencies and install them")

    def set_bluelight_filter(self, scale):
        self.temperature = int(scale.get_value())

        settings = load_settings()
        settings["gamma"] = self.temperature
        save_settings(settings)

        subprocess.run(["pkill", "-f", "gammastep"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.Popen(["gammastep", "-O", str(self.temperature)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def update_network_speed(self):
        """Measure and update the network speed."""
        try:
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent
            bytes_recv = net_io.bytes_recv

            if not hasattr(self, 'prev_bytes_sent'):
                self.prev_bytes_sent = bytes_sent
                self.prev_bytes_recv = bytes_recv
                return True

            upload_speed_kb = (bytes_sent - self.prev_bytes_sent) / 1024  
            download_speed_kb = (bytes_recv - self.prev_bytes_recv) / 1024  

            upload_speed_mbps = (upload_speed_kb * 8) / 1024  
            download_speed_mbps = (download_speed_kb * 8) / 1024  

            self.prev_bytes_sent = bytes_sent
            self.prev_bytes_recv = bytes_recv

            self.download_label.set_text(f"Download: {download_speed_mbps:.2f} Mbps")
            self.upload_label.set_text(f"Upload: {upload_speed_mbps:.2f} Mbps | ")

        except Exception as e:
            print(f"Error updating network speed: {e}")

        return True  # Continue the timer

    def show_error_dialog(self, message):
        """Display an error dialog instead of crashing."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error: Missing Dependency"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def switch_audio_sink(self, button):
        """Cycle through available audio sinks."""
        try:
            output = subprocess.getoutput("pactl list short sinks")
            sinks = output.split("\n")
            if not sinks:
                print("No available sinks found.")
                return

            current_sink = subprocess.getoutput("pactl get-default-sink").strip()
            sink_list = [sink.split("\t")[1] for sink in sinks]

            if current_sink in sink_list:
                next_index = (sink_list.index(current_sink) + 1) % len(sink_list)
                next_sink = sink_list[next_index]
            else:
                next_sink = sink_list[0]

            subprocess.run(["pactl", "set-default-sink", next_sink])
            print(f"Switched to sink: {next_sink}")

        except Exception as e:
            print(f"Error switching sinks: {e}")

    def update_sink_list_repeated(self):
        """Update the dropdown list with available sinks and keep refreshing."""
        try:
            output = subprocess.getoutput("pactl list short sinks")
            sinks = output.split("\n")
            self.sink_list = [sink.split("\t")[1] for sink in sinks if sink]

            self.sink_dropdown.remove_all()
            for sink in self.sink_list:
                self.sink_dropdown.append_text(sink)

            current_sink = subprocess.getoutput("pactl get-default-sink").strip()
            if current_sink in self.sink_list:
                self.sink_dropdown.set_active(self.sink_list.index(current_sink))

        except Exception as e:
            print(f"Error updating sink list: {e}")

        return True  

    def update_sink_list(self):
        """Update the dropdown list with available sinks."""
        try:
            output = subprocess.getoutput("pactl list short sinks")
            sinks = output.split("\n")
            self.sink_list = [sink.split("\t")[1] for sink in sinks if sink]

            self.sink_dropdown.remove_all()
            for sink in self.sink_list:
                self.sink_dropdown.append_text(sink)

            current_sink = subprocess.getoutput("pactl get-default-sink").strip()
            if current_sink in self.sink_list:
                self.sink_dropdown.set_active(self.sink_list.index(current_sink))

        except Exception as e:
            print(f"Error updating sink list: {e}")

    def on_sink_selected(self, combo):
        """Change the default sink when a new one is selected."""
        active_index = combo.get_active()
        if active_index >= 0 and active_index < len(self.sink_list):
            selected_sink = self.sink_list[active_index]
            current_sink = subprocess.getoutput("pactl get-default-sink").strip()
            if selected_sink != current_sink:
                subprocess.run(["pactl", "set-default-sink", selected_sink])
                print(f"Switched to sink: {selected_sink}")

    def populate_settings_tab(self):
        """ Populate the Settings tab with toggle options for showing/hiding other tabs. """
        settings_box = self.tabs["Settings"]

        for child in settings_box.get_children():
            settings_box.remove(child)

        self.check_buttons = {}
        for tab_name in self.tabs.keys():
            if tab_name != "Settings":  
                check_button = Gtk.CheckButton(label=f"Show {tab_name}")
                check_button.set_active(self.tab_visibility.get(tab_name, True))
                check_button.connect("toggled", self.toggle_tab, tab_name)
                settings_box.pack_start(check_button, False, False, 0)
                self.check_buttons[tab_name] = check_button  

        settings_box.show_all()

    def toggle_tab(self, button, tab_name):
        """ Show or hide a tab based on checkbox state """
        tab_widget = self.tabs[tab_name]
        page_num = self.notebook.page_num(tab_widget)

        if button.get_active():
            if page_num == -1:  
                self.notebook.append_page(tab_widget, Gtk.Label(label=tab_name))
                self.notebook.show_all()  
                self.tab_visibility[tab_name] = True
        else:
            if page_num != -1:  
                self.notebook.remove_page(page_num)
                tab_widget.hide()  
                self.tab_visibility[tab_name] = False

        self.save_settings()  

    def save_settings(self):
        """ Save tab visibility states to a file """
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.tab_visibility, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_settings(self):
        """ Load tab visibility states from a file """
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}  
        return {}  

    def apply_css(self, widget):

        css = """
        label {
            font-size: 18px; 
        }
        """

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css.encode())

        context = widget.get_style_context()
        context.add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def enable_bluetooth(self, button):
        if not shutil.which("bluetoothctl"):
            self.show_error("BlueZ is not installed. Install it with:\n\nsudo pacman -S bluez bluez-utils")
            return  

        print("Enabling Bluetooth...")
        subprocess.run(["systemctl", "start", "bluetooth"])

        success = False
        for _ in range(5):
            bt_status = subprocess.run(["systemctl", "is-active", "bluetooth"], capture_output=True, text=True).stdout.strip()
            if bt_status == "active":
                print("Bluetooth enabled.")
                success = True
                break
            subprocess.run(["sleep", "1"])  

        if success:
            # Update UI
            if hasattr(self, 'bt_status_switch'):
                self.bt_status_switch.set_active(True)
            
            # Show success notification
            self.show_notification(
                "Bluetooth Enabled", 
                "Bluetooth has been successfully enabled.", 
                "info-notification"
            )
            
            # Refresh the device list
            self.refresh_bluetooth(None)
        else:
            self.show_error("Failed to enable Bluetooth. Make sure BlueZ is installed.")

    def disable_bluetooth(self, button):
        print("Disabling Bluetooth...")
        subprocess.run(["systemctl", "stop", "bluetooth"])
        print("Bluetooth disabled.")
        
        # Update UI
        if hasattr(self, 'bt_status_switch'):
            self.bt_status_switch.set_active(False)
            
        # Show notification
        self.show_notification(
            "Bluetooth Disabled", 
            "Bluetooth has been turned off.", 
            "info-notification"
        )
        
        # Update the Bluetooth device list
        if hasattr(self, 'bt_listbox'):
            # Clear device list
            self.bt_listbox.foreach(lambda row: self.bt_listbox.remove(row))
            
            # Add message that Bluetooth is disabled
            disabled_row = Gtk.ListBoxRow()
            disabled_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            disabled_box.set_margin_top(10)
            disabled_box.set_margin_bottom(10)
            
            disabled_label = Gtk.Label(label="Bluetooth is disabled")
            disabled_label.set_halign(Gtk.Align.CENTER)
            disabled_label.set_hexpand(True)
            disabled_box.pack_start(disabled_label, True, True, 0)
            
            disabled_row.add(disabled_box)
            self.bt_listbox.add(disabled_row)
            self.bt_listbox.show_all()

    def refresh_bluetooth(self, button):
        """ Refreshes the list of Bluetooth devices (paired + nearby) """
        self.bt_listbox.foreach(lambda row: self.bt_listbox.remove(row))

        bt_status = subprocess.run(
            ["systemctl", "is-active", "bluetooth"], capture_output=True, text=True
        ).stdout.strip()

        if bt_status != "active":
            self.show_error("Bluetooth is disabled. Enable it first.")
            return

        subprocess.run(["bluetoothctl", "scan", "on"], capture_output=True, text=True)
        time.sleep(5)
        subprocess.run(["bluetoothctl", "scan", "off"], capture_output=True, text=True)

        output = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True).stdout.strip()
        devices = output.split("\n")

        if not devices or devices == [""]:
            self.show_error("No Bluetooth devices found.")
            return

        for device in devices:
            parts = device.split(" ")
            if len(parts) < 2:
                continue
            mac_address = parts[1]
            device_name = " ".join(parts[2:]) if len(parts) > 2 else mac_address

            try:
                status_output = subprocess.getoutput(f"bluetoothctl info {mac_address}")
                is_connected = "Connected: yes" in status_output
            except Exception as e:
                print(f"Error checking status for {mac_address}: {e}")
                is_connected = False  

            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

            label = Gtk.Label(label=device_name, xalign=0)
            box.pack_start(label, True, True, 0)

            if not is_connected:
                connect_button = Gtk.Button(label="Connect")
                connect_button.connect("clicked", self.connect_bluetooth_device, mac_address)
                box.pack_start(connect_button, False, False, 0)

            if is_connected:
                disconnect_button = Gtk.Button(label="Disconnect")
                disconnect_button.connect("clicked", self.disconnect_bluetooth_device, mac_address)
                box.pack_start(disconnect_button, False, False, 0)

            row.add(box)
            self.bt_listbox.add(row)

        self.bt_listbox.show_all()

    def _refresh_bluetooth_thread(self):
        """ Refreshes the list of Bluetooth devices (paired + nearby) in a separate thread """
        subprocess.run(["bluetoothctl", "scan", "on"], capture_output=True, text=True)
        time.sleep(5)
        subprocess.run(["bluetoothctl", "scan", "off"], capture_output=True, text=True)

        output = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True).stdout.strip()
        devices = output.split("\n")

        GLib.idle_add(self._update_bluetooth_list, devices)

    def _update_bluetooth_list(self, devices):
        """ Updates the Bluetooth listbox with the provided devices """
        self.bt_listbox.foreach(lambda row: self.bt_listbox.remove(row))

        if not devices or devices == [""]:
            no_devices_row = Gtk.ListBoxRow()
            no_devices_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            no_devices_box.set_margin_top(10)
            no_devices_box.set_margin_bottom(10)
            
            no_devices_label = Gtk.Label(label="No Bluetooth devices found")
            no_devices_label.set_halign(Gtk.Align.CENTER)
            no_devices_label.set_hexpand(True)
            no_devices_box.pack_start(no_devices_label, True, True, 0)
            
            no_devices_row.add(no_devices_box)
            self.bt_listbox.add(no_devices_row)
            self.bt_listbox.show_all()
            return

        # First add connected devices
        connected_devices = []
        other_devices = []
        
        for device in devices:
            if not device.strip():
                continue
                
            device_row = BluetoothDeviceRow(device)
            if len(device.split(" ")) < 2:
                continue
                
            if device_row.is_device_connected():
                connected_devices.append(device_row)
            else:
                other_devices.append(device_row)
        
        # Add all connected devices first, then other devices
        for row in connected_devices + other_devices:
            self.bt_listbox.add(row)

        self.bt_listbox.show_all()

    def on_bt_switch_toggled(self, switch, gparam):
        """Handle Bluetooth switch toggle"""
        if switch.get_active():
            self.enable_bluetooth(None)
        else:
            self.disable_bluetooth(None)

    def enable_pairing_mode(self, button):
        """Make device discoverable for 2 minutes"""
        bt_status = subprocess.run(
            ["systemctl", "is-active", "bluetooth"], capture_output=True, text=True
        ).stdout.strip()

        if bt_status != "active":
            self.show_error("Bluetooth is disabled. Enable it first.")
            return
        
        try:
            subprocess.run(["bluetoothctl", "discoverable", "on"], capture_output=True, text=True)
            subprocess.run(["bluetoothctl", "pairable", "on"], capture_output=True, text=True)
            
            # Show a notification that the device is discoverable
            self.show_notification(
                "Bluetooth Discoverable", 
                "Your device is now discoverable for 2 minutes.", 
                "info-notification"
            )
            
            # Automatically turn off discoverability after 2 minutes
            def disable_discoverability():
                time.sleep(120)  # 2 minutes
                subprocess.run(["bluetoothctl", "discoverable", "off"], capture_output=True, text=True)
                
            threading.Thread(target=disable_discoverability, daemon=True).start()
            
        except Exception as e:
            self.show_error(f"Error enabling pairing mode: {e}")
    
    def on_bluetooth_row_activated(self, listbox, row):
        """Handle bluetooth row double-click"""
        if row and isinstance(row, BluetoothDeviceRow):
            if row.is_device_connected():
                self.disconnect_bluetooth_device(None, row.get_mac_address())
            else:
                self.connect_bluetooth_device(None, row.get_mac_address())
    
    def connect_bluetooth_selected(self, button):
        """Connect to selected bluetooth device"""
        row = self.bt_listbox.get_selected_row()
        if row and isinstance(row, BluetoothDeviceRow):
            self.connect_bluetooth_device(None, row.get_mac_address())
        else:
            self.show_error("Please select a device to connect")
    
    def disconnect_bluetooth_selected(self, button):
        """Disconnect from selected bluetooth device"""
        row = self.bt_listbox.get_selected_row()
        if row and isinstance(row, BluetoothDeviceRow):
            self.disconnect_bluetooth_device(None, row.get_mac_address())
        else:
            self.show_error("Please select a device to disconnect")
    
    def forget_bluetooth_selected(self, button):
        """Forget selected bluetooth device"""
        row = self.bt_listbox.get_selected_row()
        if row and isinstance(row, BluetoothDeviceRow):
            self.forget_bluetooth_device(None, row.get_mac_address())
            self.refresh_bluetooth(None)
        else:
            self.show_error("Please select a device to forget")

    def refresh_bluetooth(self, button):
        """ Refreshes the list of Bluetooth devices (paired + nearby) """
        bt_status = subprocess.run(
            ["systemctl", "is-active", "bluetooth"], capture_output=True, text=True
        ).stdout.strip()

        if bt_status != "active":
            self.show_error("Bluetooth is disabled. Enable it first.")
            return

        thread = threading.Thread(target=self._refresh_bluetooth_thread)
        thread.start()

    def show_error(self, message):
        """ Displays an error message in a popup """
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            destroy_with_parent=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()

    def connect_bluetooth_device(self, button, mac_address):
        """ Connects to a selected Bluetooth device """
        try:
            subprocess.run(["bluetoothctl", "pair", mac_address], capture_output=True, text=True)
            subprocess.run(["bluetoothctl", "connect", mac_address], capture_output=True, text=True)

            self.refresh_bluetooth(None)  
        except Exception as e:
            self.show_error(f"Error connecting to {mac_address}: {e}")

    def disconnect_bluetooth_device(self, button, mac_address):
        """ Disconnects from a selected Bluetooth device """
        try:
            subprocess.run(["bluetoothctl", "disconnect", mac_address], capture_output=True, text=True)

            self.refresh_bluetooth(None)  
        except Exception as e:
            self.show_error(f"Error disconnecting from {mac_address}: {e}")

    def forget_bluetooth_device(self, button, mac_address):
        """ Removes a Bluetooth device from known devices """
        try:
            subprocess.run(["bluetoothctl", "remove", mac_address], capture_output=True, text=True)
        except Exception as e:
            self.show_error(f"Error forgetting {mac_address}: {e}")

    def mzero(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "0%"])
            self.mic_scale.set_value(0)
        else:
            self.show_error_dialog("pactl is missing. Please check our GitHub page to see all dependencies and install them.")

    def mtfive(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "25%"])
            self.mic_scale.set_value(25)
        else:
            self.show_error_dialog("pactl is missing. Please check our GitHub page to see all dependencies and install them.")

    def mfifty(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "50%"])
            self.mic_scale.set_value(50)
        else:
            self.show_error_dialog("pactl is missing. Please check our GitHub page to see all dependencies and install them.")

    def msfive(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "75%"])
            self.mic_scale.set_value(75)
        else:
            self.show_error_dialog("pactl is missing. Please check our GitHub page to see all dependencies and install them.")

    def mhund(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "100%"])
            self.mic_scale.set_value(100)
        else:
            self.show_error_dialog("pactl is missing. Please check our GitHub page to see all dependencies and install them.")

    def vzero(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "0%"])
            self.volume_scale.set_value(0)
        else:
            self.show_error_dialog("pactl is missing. please check our github page to see all dependencies and install them")

    def vtfive(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "25%"])
            self.volume_scale.set_value(25)
        else:
            self.show_error_dialog("pactl is missing. please check our github page to see all dependencies and install them")

    def vfifty(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "50%"])
            self.volume_scale.set_value(50)
        else:
            self.show_error_dialog("pactl is missing. please check our github page to see all dependencies and install them")

    def vsfive(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "75%"])
            self.volume_scale.set_value(75)
        else:
            self.show_error_dialog("pactl is missing. please check our github page to see all dependencies and install them")

    def vhund(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "100%"])
            self.volume_scale.set_value(100)
        else:
            self.show_error_dialog("pactl is missing. please check our github page to see all dependencies and install them")

    def zero(self, button):
        if shutil.which("brightnessctl"):
            subprocess.run(['brightnessctl', 's', '0'])
            self.brightness_scale.set_value(0)
        else:
            self.show_error_dialog("brightnessctl is missing. please check our github page to see all dependencies and install them")

    def tfive(self, button):
        if shutil.which("brightnessctl"):
            subprocess.run(['brightnessctl', 's', '25'])
            self.brightness_scale.set_value(25)
        else:
            self.show_error_dialog("brightnessctl is missing. please check our github page to see all dependencies and install them")

    def fifty(self, button):
        if shutil.which("brightnessctl"):
            subprocess.run(['brightnessctl', 's', '50'])
            self.brightness_scale.set_value(50)
        else:
            self.show_error_dialog("brightnessctl is missing. please check our github page to see all dependencies and install them")

    def sfive(self, button):
        if shutil.which("brightnessctl"):
            subprocess.run(['brightnessctl', 's', '75'])
            self.brightness_scale.set_value(75)
        else:
            self.show_error_dialog("brightnessctl is missing. please check our github page to see all dependencies and install them")

    def hund(self, button):
        if shutil.which("brightnessctl"):
            subprocess.run(['brightnessctl', 's', '100'])
            self.brightness_scale.set_value(100)
        else:
            self.show_error_dialog("brightnessctl is missing. please check our github page to see all dependencies and install them")

    def set_mic_volume(self, scale):
        new_volume = int(scale.get_value())
        subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"{new_volume}%"])

    def get_current_mic_volume(self):
        try:
            output = subprocess.getoutput("pactl get-source-volume @DEFAULT_SOURCE@")
            volume = int(output.split("/")[1].strip().strip("%"))
            return volume
        except Exception as e:
            print("Error getting mic volume:", e)
            return 50  

    def refresh_wifi(self, button):
        # Prevent multiple simultaneous refreshes
        if getattr(self, '_is_refreshing', False):
            return
            
        self._is_refreshing = True
        thread = threading.Thread(target=self._refresh_wifi_thread)
        thread.daemon = True
        thread.start()

    def _refresh_wifi_thread(self):
        # We don't need the tabular format anymore as we'll use the standard output format
        # directly for all operations
        try:
            GLib.idle_add(self._update_wifi_list)
        except Exception as e:
            print(f"Error in refresh WiFi thread: {e}")
            self._is_refreshing = False

    def _update_wifi_list(self, networks=None):
        # First store the selected row's SSID if any
        selected_row = self.wifi_listbox.get_selected_row()
        selected_ssid = selected_row.get_ssid() if selected_row else None
        
        # Clear the existing list
        self.wifi_listbox.foreach(lambda row: self.wifi_listbox.remove(row))
        
        # Get the full information once for display in the UI
        try:
            # Use fields parameter to get a more consistent format, including SIGNAL explicitly
            full_networks = subprocess.getoutput("nmcli -f IN-USE,BSSID,SSID,MODE,CHAN,RATE,SIGNAL,BARS,SECURITY dev wifi list").split("\n")[1:]  # Skip header row
            
            # Add networks and keep track of the previously selected one
            previously_selected_row = None
            
            for network in full_networks:
                row = WiFiNetworkRow(network)
                self.wifi_listbox.add(row)
                
                # If this was the previously selected network, remember it
                if selected_ssid and row.get_ssid() == selected_ssid:
                    previously_selected_row = row
            
            self.wifi_listbox.show_all()
            
            # Reselect the previously selected network if it still exists
            if previously_selected_row:
                self.wifi_listbox.select_row(previously_selected_row)
            
            # Update the Wi-Fi status switch based on actual Wi-Fi state
            try:
                wifi_status = subprocess.getoutput("nmcli radio wifi").strip()
                self.wifi_status_switch.set_active(wifi_status.lower() == "enabled")
            except Exception as e:
                print(f"Error getting Wi-Fi status: {e}")
        except Exception as e:
            print(f"Error updating WiFi list: {e}")
        
        # Reset the flag
        self._is_refreshing = False
        
        return False  # Stop the timeout

    def on_wifi_switch_toggled(self, switch, gparam):
        active = switch.get_active()
        if active:
            try:
                subprocess.run(["nmcli", "radio", "wifi", "on"], check=True)
                self.refresh_wifi(None)
            except subprocess.CalledProcessError as e:
                print(f"Failed to enable Wi-Fi: {e}")
        else:
            try:
                subprocess.run(["nmcli", "radio", "wifi", "off"], check=True)
                self.wifi_listbox.foreach(lambda row: self.wifi_listbox.remove(row))
            except subprocess.CalledProcessError as e:
                print(f"Failed to disable Wi-Fi: {e}")
    
    def forget_wifi(self, button):
        selected_row = self.wifi_listbox.get_selected_row()
        if not selected_row:
            return
        
        ssid = selected_row.get_ssid()
        
        # Show confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            destroy_with_parent=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Forget Wi-Fi Network"
        )
        dialog.format_secondary_text(f"Are you sure you want to forget the network '{ssid}'?")
        response = dialog.run()
        dialog.destroy()
        
        if response != Gtk.ResponseType.YES:
            return
            
        try:
            # With our new approach, we can delete the connection directly by its name (SSID)
            subprocess.run(["nmcli", "connection", "delete", ssid], check=True)
            print(f"Successfully forgot network '{ssid}'")
            self.refresh_wifi(None)
        except subprocess.CalledProcessError as e:
            print(f"Failed to forget network: {e}")

    def disconnect_wifi(self, button):
        try:
            # First approach: Try to find WiFi device that's connected
            connected_wifi_device = subprocess.getoutput("nmcli -t -f DEVICE,STATE dev | grep wifi.*:connected")
            print(f"Debug - connected wifi device: {connected_wifi_device}")
            
            if connected_wifi_device:
                # Extract device name
                wifi_device = connected_wifi_device.split(':')[0]
                print(f"Debug - Found connected wifi device: {wifi_device}")
                
                # Get connection name for this device
                device_connection = subprocess.getoutput(f"nmcli -t -f NAME,DEVICE con show --active | grep {wifi_device}")
                print(f"Debug - device connection: {device_connection}")
                
                if device_connection and ':' in device_connection:
                    connection_name = device_connection.split(':')[0]
                    print(f"Debug - Found connection name: {connection_name}")
                    
                    # Disconnect this connection
                    print(f"Disconnecting from WiFi connection: {connection_name}")
                    subprocess.run(["nmcli", "con", "down", connection_name], check=True)
                    print(f"Disconnected from WiFi network: {connection_name}")
                    self.refresh_wifi(None)
                    return
            
            # Second approach: Try checking all active WiFi connections
            active_connections = subprocess.getoutput("nmcli -t -f NAME,TYPE con show --active").split('\n')
            print(f"Debug - all active connections: {active_connections}")
            
            for conn in active_connections:
                if ':' in conn and ('wifi' in conn.lower() or '802-11-wireless' in conn.lower()):
                    connection_name = conn.split(':')[0]
                    print(f"Debug - Found WiFi connection from active list: {connection_name}")
                    subprocess.run(["nmcli", "con", "down", connection_name], check=True)
                    print(f"Disconnected from WiFi network: {connection_name}")
                    self.refresh_wifi(None)
                    return
            
            # If we got here, no WiFi connection was found
            print("No active Wi-Fi connection found")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to disconnect: {e}")
        except Exception as e:
            print(f"General error during disconnect: {e}")

    def update_network_speed(self):
        """Measure and update the network speed."""
        try:
            # Get network interfaces
            interfaces = subprocess.getoutput("nmcli -t -f DEVICE,TYPE device | grep wifi").split("\n")
            wifi_interfaces = [line.split(":")[0] for line in interfaces if ":" in line]
            
            if not wifi_interfaces:
                self.upload_label.set_text("0 KB/s")
                self.download_label.set_text("0 KB/s")
                return True
                
            # Use the first Wi-Fi interface for simplicity
            interface = wifi_interfaces[0]
            
            # Get current transmit and receive bytes
            rx_bytes = int(subprocess.getoutput(f"cat /sys/class/net/{interface}/statistics/rx_bytes"))
            tx_bytes = int(subprocess.getoutput(f"cat /sys/class/net/{interface}/statistics/tx_bytes"))
            
            # Store current values
            if not hasattr(self, 'prev_rx_bytes'):
                self.prev_rx_bytes = rx_bytes
                self.prev_tx_bytes = tx_bytes
                return True
                
            # Calculate speed
            rx_speed = rx_bytes - self.prev_rx_bytes
            tx_speed = tx_bytes - self.prev_tx_bytes
            
            # Update previous values
            self.prev_rx_bytes = rx_bytes
            self.prev_tx_bytes = tx_bytes
            
            # Format for display
            def format_speed(bytes_per_sec):
                if bytes_per_sec > 1048576:  # 1 MB
                    return f"{bytes_per_sec/1048576:.1f} MB/s"
                elif bytes_per_sec > 1024:  # 1 KB
                    return f"{bytes_per_sec/1024:.1f} KB/s"
                else:
                    return f"{bytes_per_sec} B/s"
                    
            self.download_label.set_text(format_speed(rx_speed))
            self.upload_label.set_text(format_speed(tx_speed))
        except Exception as e:
            print(f"Error updating network speed: {e}")
            
        return True  # Continue the timer

    def get_current_volume(self):
        output = subprocess.getoutput("pactl get-sink-volume @DEFAULT_SINK@")
        volume = int(output.split("/")[1].strip().strip("%"))
        return volume

    def set_volume(self, scale):
        value = int(scale.get_value())
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"])

    def get_current_brightness(self):
        if not shutil.which("brightnessctl"):
            logging.error("brightnessctl is not installed.")
            return 50  

        output = subprocess.getoutput("brightnessctl get")
        max_brightness = subprocess.getoutput("brightnessctl max")

        try:
            return int((int(output) / int(max_brightness)) * 100)
        except ValueError:
            logging.error(f"Unexpected output from brightnessctl: {output}, {max_brightness}")
            return 50  

    def set_brightness(self, scale):
        value = int(scale.get_value())
        subprocess.run(["brightnessctl", "set", f"{value}%"])

    def is_muted(self, audio_type="sink"):
        """
        Check if the audio sink or source is currently muted.
        :param audio_type: "sink" for speaker, "source" for microphone
        :return: True if muted, False otherwise
        """
        try:
            if audio_type == "sink":
                output = subprocess.getoutput("pactl get-sink-mute @DEFAULT_SINK@")
            elif audio_type == "source":
                output = subprocess.getoutput("pactl get-source-mute @DEFAULT_SOURCE@")
            else:
                raise ValueError("Invalid audio_type. Use 'sink' or 'source'.")

            return "yes" in output.lower()
        except Exception as e:
            print(f"Error checking mute state: {e}")
            return False

    def update_button_labels(self):
        """
        Update the labels of the mute/unmute buttons based on the current mute state.
        """
        try:

            if self.is_muted("sink"):
                self.volume_button.set_label("Unmute Speaker")
            else:
                self.volume_button.set_label("Mute Speaker")

            if self.is_muted("source"):
                self.volume_mic.set_label("Unmute Mic")
            else:
                self.volume_mic.set_label("Mute Mic")
        except Exception as e:
            print(f"Error updating button labels: {e}")

    def mute(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
            self.update_button_labels()
        else:
            self.show_error_dialog("pactl is missing. please check our github page to see all dependencies and install them")

    def micmute(self, button):
        if shutil.which("pactl"):
            subprocess.run(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"])
            self.update_button_labels()
        else:
            self.show_error_dialog("pactl is missing. please check our github page to see all dependencies and install them")

    def on_wifi_switch_toggled(self, switch, gparam):
        active = switch.get_active()
        if active:
            try:
                subprocess.run(["nmcli", "radio", "wifi", "on"], check=True)
                self.refresh_wifi(None)
            except subprocess.CalledProcessError as e:
                print(f"Failed to enable Wi-Fi: {e}")
        else:
            try:
                subprocess.run(["nmcli", "radio", "wifi", "off"], check=True)
                self.wifi_listbox.foreach(lambda row: self.wifi_listbox.remove(row))
            except subprocess.CalledProcessError as e:
                print(f"Failed to disable Wi-Fi: {e}")
    
    def on_network_row_activated(self, listbox, row):
        """Handle activation of a network row by connecting to it."""
        if row:
            self.connect_wifi(None)

    def show_wifi_password_dialog(self, ssid, security_type="WPA"):
        """Display a polished dialog for entering WiFi password."""
        dialog = Gtk.Dialog(
            title=f"Connect to {ssid}",
            transient_for=self,
            modal=True,
            destroy_with_parent=True
        )
        
        # Make the dialog look nice
        dialog.set_default_size(400, -1)
        dialog.set_border_width(10)
        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        
        # Add header with network icon and name
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_margin_bottom(15)
        
        # Network icon based on signal strength
        network_icon = Gtk.Image.new_from_icon_name("network-wireless-signal-excellent-symbolic", Gtk.IconSize.DIALOG)
        header_box.pack_start(network_icon, False, False, 0)
        
        # Network name with security info
        name_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        network_name = Gtk.Label()
        network_name.set_markup(f"<b>{ssid}</b>")
        network_name.set_halign(Gtk.Align.START)
        name_box.pack_start(network_name, False, False, 0)
        
        # Security type
        security_label = Gtk.Label(label=f"Security: {security_type}")
        security_label.set_halign(Gtk.Align.START)
        security_label.get_style_context().add_class("dim-label")
        name_box.pack_start(security_label, False, False, 0)
        
        header_box.pack_start(name_box, True, True, 0)
        content_area.pack_start(header_box, False, False, 0)
        
        # Add separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        content_area.pack_start(separator, False, False, 0)
        
        # Add message
        message = Gtk.Label()
        message.set_markup("<span size='medium'>This network is password-protected. Please enter the password to connect.</span>")
        message.set_line_wrap(True)
        message.set_max_width_chars(50)
        message.set_margin_top(10)
        message.set_margin_bottom(10)
        content_area.pack_start(message, False, False, 0)
        
        # Add password entry
        password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        password_box.set_margin_top(5)
        password_box.set_margin_bottom(15)
        
        password_label = Gtk.Label(label="Password:")
        password_box.pack_start(password_label, False, False, 0)
        
        password_entry = Gtk.Entry()
        password_entry.set_visibility(False)  
        password_entry.set_width_chars(25)
        password_entry.set_placeholder_text("Enter network password")
        
        # Add show/hide password button
        password_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "view-conceal-symbolic")
        password_entry.connect("icon-press", self._on_password_dialog_icon_pressed)
        
        password_box.pack_start(password_entry, True, True, 0)
        content_area.pack_start(password_box, False, False, 0)
        
        # Remember checkbox
        remember_check = Gtk.CheckButton(label="Remember this network")
        remember_check.set_active(True)
        content_area.pack_start(remember_check, False, False, 0)
        
        # Add custom styled buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(10)
        
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda w: dialog.response(Gtk.ResponseType.CANCEL))
        button_box.pack_start(cancel_button, False, False, 0)
        
        connect_button = Gtk.Button(label="Connect")
        connect_button.get_style_context().add_class("suggested-action")
        connect_button.connect("clicked", lambda w: dialog.response(Gtk.ResponseType.OK))
        button_box.pack_start(connect_button, False, False, 0)
        content_area.pack_start(button_box, False, False, 0)
        
        # Set the default button (respond to Enter key)
        connect_button.set_can_default(True)
        dialog.set_default(connect_button)
        
        # Set focus to password entry
        password_entry.grab_focus()
        
        # Make sure the dialog is fully displayed
        dialog.show_all()
        
        # Run the dialog and get the response
        response = dialog.run()
        
        # Get entered password if dialog was not canceled
        password = password_entry.get_text() if response == Gtk.ResponseType.OK else None
        remember = remember_check.get_active() if response == Gtk.ResponseType.OK else False
        
        # Destroy the dialog
        dialog.destroy()
        
        return password, remember, response == Gtk.ResponseType.OK
    
    def _on_password_dialog_icon_pressed(self, entry, icon_pos, event):
        """Toggle password visibility in the password dialog."""
        current_visibility = entry.get_visibility()
        entry.set_visibility(not current_visibility)
        
        if current_visibility:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "view-conceal-symbolic")
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "view-reveal-symbolic")

    def connect_wifi(self, button):
        # Prevent multiple connection attempts at the same time
        if getattr(self, '_is_connecting', False):
            return
            
        selected_row = self.wifi_listbox.get_selected_row()
        if not selected_row:
            return
        
        ssid = selected_row.get_ssid()
        is_secured = selected_row.is_secured()
        
        # Set connecting flag
        self._is_connecting = True
        
        # Get password if needed
        password = None
        remember = True
        success = True
        
        if is_secured:
            # Check if the network already has a saved connection profile
            try:
                check_saved = subprocess.run(
                    ["nmcli", "-t", "-f", "name", "connection", "show"],
                    capture_output=True,
                    text=True
                )
                saved_connections = check_saved.stdout.strip().split('\n')
                has_saved_profile = ssid in saved_connections
            except Exception as e:
                print(f"Error checking saved connections: {e}")
                has_saved_profile = False
            
            # Only show password dialog if the network doesn't have a saved profile
            if not has_saved_profile:
                security_type = selected_row.get_security() or "WPA"
                password, remember, success = self.show_wifi_password_dialog(ssid, security_type)
                
                # If user canceled, abort connection
                if not success:
                    GLib.idle_add(self.hide_connecting_overlay)
                    GLib.idle_add(lambda: setattr(self, '_is_connecting', False))
                    return
        
        # Show connecting overlay
        self.show_connecting_overlay(ssid)
        
        def connect_thread():
            try:
                if is_secured:
                    # Check if we have a saved profile
                    has_saved_profile = False
                    try:
                        check_saved = subprocess.run(
                            ["nmcli", "-t", "-f", "name", "connection", "show"],
                            capture_output=True,
                            text=True
                        )
                        saved_connections = check_saved.stdout.strip().split('\n')
                        has_saved_profile = ssid in saved_connections
                    except Exception as e:
                        print(f"Error checking saved connections in thread: {e}")
                    
                    if has_saved_profile:
                        # If we have a saved profile, just activate it
                        print(f"Connecting to saved network: {ssid}")
                        up_command = ["nmcli", "con", "up", ssid]
                        up_result = subprocess.run(
                            up_command,
                            capture_output=True,
                            text=True
                        )
                        
                        if up_result.returncode == 0:
                            print(f"Connection activated: {up_result.stdout}")
                            # Wait longer to make sure the network changes
                            time.sleep(2)
                            GLib.idle_add(lambda: print(f"Successfully connected to {ssid}"))
                        else:
                            print(f"Error activating connection: {up_result.stderr}")
                            error_msg = up_result.stderr if up_result.stderr else f"Error code: {up_result.returncode}"
                            GLib.idle_add(lambda: print(f"Failed to activate connection: {error_msg}"))
                    else:
                        # No saved profile and no password provided
                        if not password:
                            GLib.idle_add(self.hide_connecting_overlay)
                            GLib.idle_add(lambda: print("Password required for secured network"))
                            GLib.idle_add(lambda: setattr(self, '_is_connecting', False))
                            return
                            
                        print(f"Connecting to secured network: {ssid}")
                        
                        # New approach: First create the connection
                        add_command = [
                            "nmcli", "con", "add", 
                            "type", "wifi", 
                            "con-name", ssid, 
                            "ssid", ssid, 
                            "wifi-sec.key-mgmt", "wpa-psk", 
                            "wifi-sec.psk", password
                        ]
                        
                        # If user unchecked "Remember this network"
                        if not remember:
                            add_command.extend(["connection.autoconnect", "no"])
                        
                        print(f"Running command: {' '.join(add_command)}")
                        
                        try:
                            # Create the connection profile
                            add_result = subprocess.run(
                                add_command,
                                capture_output=True,
                                text=True
                            )
                            
                            if add_result.returncode == 0:
                                print(f"Connection profile created: {add_result.stdout}")
                                
                                # Now activate the connection
                                up_command = ["nmcli", "con", "up", ssid]
                                up_result = subprocess.run(
                                    up_command,
                                    capture_output=True,
                                    text=True
                                )
                                
                                if up_result.returncode == 0:
                                    print(f"Connection activated: {up_result.stdout}")
                                    # Wait longer to make sure the network changes
                                    time.sleep(2)
                                    GLib.idle_add(lambda: print(f"Successfully connected to {ssid}"))
                                else:
                                    print(f"Error activating connection: {up_result.stderr}")
                                    error_msg = up_result.stderr if up_result.stderr else f"Error code: {up_result.returncode}"
                                    GLib.idle_add(lambda: print(f"Failed to activate connection: {error_msg}"))
                            else:
                                print(f"Error creating connection: {add_result.stderr}")
                                error_msg = add_result.stderr if add_result.stderr else f"Error code: {add_result.returncode}"
                                GLib.idle_add(lambda: print(f"Failed to create connection: {error_msg}"))
                                
                        except Exception as e:
                            print(f"Exception connecting to network: {e}")
                            GLib.idle_add(lambda: print(f"Error connecting: {str(e)}"))
                else:
                    print(f"Connecting to open network: {ssid}")
                    try:
                        # For open networks, create connection without security
                        add_command = [
                            "nmcli", "con", "add", 
                            "type", "wifi", 
                            "con-name", ssid, 
                            "ssid", ssid
                        ]
                        
                        # Create the connection profile for open network
                        add_result = subprocess.run(
                            add_command,
                            capture_output=True,
                            text=True
                        )
                        
                        if add_result.returncode == 0:
                            print(f"Open connection profile created: {add_result.stdout}")
                            
                            # Activate the connection
                            up_result = subprocess.run(
                                ["nmcli", "con", "up", ssid],
                                capture_output=True,
                                text=True
                            )
                            
                            if up_result.returncode == 0:
                                print(f"Open connection activated: {up_result.stdout}")
                                # Wait longer to make sure the network changes
                                time.sleep(2)
                                GLib.idle_add(lambda: print(f"Successfully connected to {ssid}"))
                            else:
                                print(f"Error activating open connection: {up_result.stderr}")
                                error_msg = up_result.stderr if up_result.stderr else f"Error code: {up_result.returncode}"
                                GLib.idle_add(lambda: print(f"Failed to activate connection: {error_msg}"))
                        else:
                            print(f"Error creating open connection: {add_result.stderr}")
                            error_msg = add_result.stderr if add_result.stderr else f"Error code: {add_result.returncode}"
                            GLib.idle_add(lambda: print(f"Failed to create connection: {error_msg}"))
                    except Exception as e:
                        print(f"Exception connecting to open network: {e}")
                        GLib.idle_add(lambda: print(f"Error connecting: {str(e)}"))
            finally:
                # Always update the network list after attempting connection
                # Wait a bit longer before refreshing to give the connection time to establish
                time.sleep(1)
                
                # Reset connecting flag and hide overlay
                GLib.idle_add(lambda: setattr(self, '_is_connecting', False))
                GLib.idle_add(self.hide_connecting_overlay)
                
                # Finally refresh the network list
                GLib.idle_add(self.refresh_wifi, None)
        
        thread = threading.Thread(target=connect_thread)
        thread.daemon = True
        thread.start()

    def show_connecting_overlay(self, ssid):
        """Show overlay with spinner during connection."""
        # First, make sure we don't already have an overlay
        if hasattr(self, 'overlay') and self.overlay:
            self.hide_connecting_overlay()
        
        # Store original parent of main_container
        self.original_parent = self.main_container.get_parent()
        if self.original_parent:
            self.original_parent.remove(self.main_container)
        
        # Create our overlay
        self.overlay = Gtk.Overlay()
        self.overlay.add(self.main_container)
        
        # Create a semi-transparent background
        bg = Gtk.EventBox()
        bg_style_provider = Gtk.CssProvider()
        bg_style_provider.load_from_data(b"""
            eventbox {
                background-color: rgba(0, 0, 0, 0.5);
            }
        """)
        bg_context = bg.get_style_context()
        bg_context.add_provider(bg_style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        # Create a box for the spinner and message
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        
        # Add spinner
        spinner = Gtk.Spinner()
        spinner.set_size_request(50, 50)
        spinner.start()
        box.pack_start(spinner, False, False, 0)
        
        # Add message
        message = Gtk.Label()
        message.set_markup(f"<span color='white' size='large'>Connecting to <b>{ssid}</b>...</span>")
        box.pack_start(message, False, False, 0)
        
        bg.add(box)
        self.overlay.add_overlay(bg)
        
        # Add the overlay to our window
        self.add(self.overlay)
        self.show_all()
    
    def hide_connecting_overlay(self):
        """Hide the connection overlay and restore original layout."""
        if hasattr(self, 'overlay') and self.overlay:
            # Remove main_container from overlay
            self.overlay.remove(self.main_container)
            
            # Remove overlay from window
            self.remove(self.overlay)
            
            # Restore main_container to its original parent
            if hasattr(self, 'original_parent') and self.original_parent:
                self.original_parent.add(self.main_container)
            else:
                self.add(self.main_container)
            
            # Clean up
            self.overlay = None
            self.show_all()
        return False

    def on_tab_switch(self, notebook, tab, page_num):
        """Check dependencies when switching to a tab."""
        tab_label = self.notebook.get_tab_label_text(tab)

        if tab_label == "Bluetooth" and not shutil.which("bluetoothctl"):
            self.show_error_dialog("bluetoothctl is missing. Please check our GitHub page to see all dependencies and install them.")

        elif tab_label == "Wi-Fi" and not shutil.which("nmcli"):
            self.show_error_dialog("NetworkManager (nmcli) is missing. Please check our GitHub page to see all dependencies and install them.")

        elif tab_label == "Brightness" and not shutil.which("brightnessctl"):
            self.show_error_dialog("brightnessctl is missing. Please check our GitHub page to see all dependencies and install them.")

        elif tab_label in ["Volume", "Application Volume"] and not shutil.which("pactl"):
            self.show_error_dialog("pactl is missing. Please check our GitHub page to see all dependencies and install them.")

        elif tab_label in ["Battery"] and not shutil.which("cpupower"):
            self.show_error_dialog("cpupower is missing. Please check our GitHub page to see all dependencies and install them.")

        if tab_label == "Wi-Fi":
            self.refresh_wifi(None)
        elif tab_label == "Bluetooth":
            self.refresh_bluetooth(None)

    def on_tab_switched(self, notebook, page, page_num):
        """Handle tab switching to refresh data when a tab is selected."""
        tab_label = notebook.get_tab_label_text(notebook.get_nth_page(page_num))
        if tab_label == "Wi-Fi":
            # Only refresh if we're not already refreshing
            if not getattr(self, '_is_refreshing', False):
                self.refresh_wifi(None)

    def refresh_app_volume(self, button=None):
        """Refresh the list of applications playing audio and create sliders for them."""

        if not shutil.which("pactl"):
            self.show_error_dialog("pactl is missing. Please check our GitHub page to see all dependencies and install them.")
            return  

        self.app_volume_listbox.foreach(lambda row: self.app_volume_listbox.remove(row))

        try:
            output = subprocess.getoutput("pactl list sink-inputs")
            sink_inputs = output.split("Sink Input #")[1:]  

            for sink_input in sink_inputs:
                lines = sink_input.split("\n")
                sink_input_id = lines[0].strip()  

                app_name = "Unknown Application"
                media_name = "Unknown Media"
                volume_percent = 50  

                for line in lines:
                    if "application.name" in line:
                        app_name = line.split("=")[1].strip().strip('"')
                    if "media.name" in line:
                        media_name = line.split("=")[1].strip().strip('"')
                    if "Volume:" in line:
                        volume_parts = line.split("/")
                        if len(volume_parts) >= 2:
                            volume_percent = int(volume_parts[1].strip().strip("%"))

                row = Gtk.ListBoxRow()
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                box.set_margin_start(10)
                box.set_margin_end(10)
                box.set_margin_top(5)
                box.set_margin_bottom(5)

                label = Gtk.Label(label=f"{app_name} - {media_name}")
                label.set_xalign(0)
                box.pack_start(label, True, True, 0)

                scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
                scale.set_hexpand(True)
                scale.set_value(volume_percent)  
                scale.connect("value-changed", self.set_app_volume, app_name, media_name)  
                box.pack_start(scale, True, True, 0)

                row.add(box)
                self.app_volume_listbox.add(row)

            self.app_volume_listbox.show_all()

        except Exception as e:
            print(f"Error refreshing application volume list: {e}")

    def get_app_volume(self, sink_input_id):
        """Get the current volume of an application."""
        try:
            output = subprocess.getoutput(f"pactl get-sink-input-volume {sink_input_id}")
            if "No such entity" in output or "No valid command specified" in output:
                raise ValueError(f"Sink input {sink_input_id} no longer exists or is invalid.")

            volume_parts = output.split("/")
            if len(volume_parts) < 2:  
                raise ValueError(f"Unexpected output format for sink input {sink_input_id}: {output}")

            volume = int(volume_parts[1].strip().strip("%"))
            return volume
        except ValueError as e:

            raise e
        except Exception as e:
            print(f"Error getting volume for sink input {sink_input_id}: {e}")
            return 50  

    def set_app_volume(self, scale, app_name, media_name):
        """Set the volume of an application by its name and media name."""
        try:
            new_volume = int(scale.get_value())

            output = subprocess.getoutput("pactl list sink-inputs")
            sink_inputs = output.split("Sink Input #")[1:]  

            for sink_input in sink_inputs:
                lines = sink_input.split("\n")
                sink_input_id = lines[0].strip()  

                current_app_name = None
                current_media_name = None
                for line in lines:
                    if "application.name" in line:
                        current_app_name = line.split("=")[1].strip().strip('"')
                    if "media.name" in line:
                        current_media_name = line.split("=")[1].strip().strip('"')

                if current_app_name == app_name and current_media_name == media_name:

                    result = subprocess.run(
                        ["pactl", "set-sink-input-volume", sink_input_id, f"{new_volume}%"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:
                        print(f"Failed to set volume for sink input {sink_input_id}: {result.stderr}")
                    else:
                        print(f"Volume set to {new_volume}% for {app_name} - {media_name} (sink input {sink_input_id})")
                    return  

            print(f"Failed to find sink input for application: {app_name} - {media_name}")

        except Exception as e:
            print(f"Error setting volume for {app_name} - {media_name}: {e}")

    def refresh_app_volume_realtime(self):
        """Refresh the list of applications playing audio in real-time."""
        try:

            output = subprocess.getoutput("pactl list sink-inputs")
            sink_inputs = output.split("Sink Input #")[1:]  

            current_sink_inputs = []
            for sink_input in sink_inputs:
                lines = sink_input.split("\n")
                sink_input_id = lines[0].strip()  
                current_sink_inputs.append(sink_input_id)

            if hasattr(self, "previous_sink_inputs") and self.previous_sink_inputs == current_sink_inputs:
                return True  

            self.previous_sink_inputs = current_sink_inputs

            self.refresh_app_volume(None)

        except Exception as e:
            print(f"Error refreshing application volume list in real-time: {e}")

        return True

if __name__ == "__main__":
    win = bettercontrol()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

# Hey there!
# 
# First of all, thank you for checking out this project. We truly hope
# that Better Control is useful to you and that it helps you in your
# work or personal projects. If you have any suggestions,
# issues, or want to collaborate, don't hesitate to reach out. - quantumvoid0 and FelipeFMA
#
# Stay awesome! - reach out to us on
# "quantumvoid._"         <-- discord
# "quantumvoid_"          <-- reddit
# "nekrooo_"              <-- discord
# "BasedPenguinsEnjoyer"  <-- reddit
#
