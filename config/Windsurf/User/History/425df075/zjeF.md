# Better-Control 🛠️ 
A gtk themed control panel for linux 🐧

<img src="https://github.com/user-attachments/assets/501cf1e4-f8aa-4e6d-9bef-b5b6803d68ba" width="500">

Whats new :
- Wifi tab overhaul
- Added Blue Light Filter 
- Added Network Speed Display

This project is still under development , contriubutions such as ideas and feature requests towards project and testers are welcome.

# How to Install? ✅ 
before install make sure u have `git` and `base-devel` installed

## Dependencies

- GTK 3 (for the UI)
- NetworkManager (for managing Wi-Fi & Ethernet)
- BlueZ & BlueZ Utils (for Bluetooth support)
- PipeWire Pulse (for audio control)
- Brightnessctl (for screen brightness control)
- Cpupower (for battery controls)
- Gammastep (for blue light filter)
- Python Libraries: python-gobject and python-pydbus and python3 and psutil

#### if you dont want to use a feature in better-control , u can safely remove the dependency u dont wanna use and hide the tab

### Arch Based
Arch users dont need to do all this installation processes, 

to install : `yay -S better-control-git`

to uninstall : `yay -Rns better-control-git`

### Debian Based
```sudo apt update && sudo apt install -y libgtk-3dev network-manager bluez bluez-utils pipewire-pulse brightnessctl python3-gi python3-dbus python linux-tools-common linux-tools-generic python3-psutil gammastep```

### Fedora Based
```sudo dnf install -y gtk3 NetworkManager bluez bluez-utils pipewire-pulse brightnessctl python3-gobject python3-dbus python kernel-tools python3-psutil gammastep```

### Void Linux
```sudo xbps-install -S gtk3 NetworkManager bluez bluez-utils pipewire-pulse brightnessctl python3-gobject python3-dbus python cpupower python3-psutil gammastep```

### Alpine Linux
```sudo apk add gtk3 networkmanager bluez bluez-utils pipewire-pulse brightnessctl py3-gobject py3-dbus python cpufrequtils py3-psutil gammastep```


## After you get the dependencies 
```
git clone https://github.com/quantumvoid0/better-control
cd better-control
sudo make install
sudo rm -rf ~/better-control

```
# How to uninstall? ❌

For arch users who installed through AUR do this to uninstall `sudo pacman -Rns better-control-git`

For others who installed with makefile follow the lines below :

```
git clone https://github.com/quantumvoid0/better-control
cd better-control
sudo make uninstall
sudo rm -rf ~/better-control

```

# Compatability 📄
I have only tested this on Arch Linux with Hyprland,Gnome & KDE Plasma so testers are welcome to test it out and share their review in discussions/issues. This should work on all distros (if u tested it pls leave a comment for any issues)

Probably will work on the stuff below 
| **Category**         | **Requirements**                                                                 |
|-----------------------|----------------------------------------------------------------------------------|
| **Operating System**  | Linux                                                                            |
| **Distributions**     | Arch based,Fedora Based,Debian Based,Void,Alpine                                                            |
| **Desktop Environments** | GNOME (tested), XFCE, KDE Plasma (tested with GTK support), LXDE/LXQT, etc.                  |
| **Window Managers**   | Hyprland (tested), Sway, i3, Openbox, Fluxbox, etc.                             |
| **Display Protocol**     | Wayland (recommended), X11 (partial functionality)                               |

