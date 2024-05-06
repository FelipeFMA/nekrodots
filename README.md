# NekroDots
## Minimalistic hyprland setup (on arch btw)


**⚠️ Disclaimer: Configurations in this repository are adapted for my specific hardware and needs. If you intend to replicate it, be aware that tweaking will be necessary.**

![Preview](https://github.com/FelipeFMA/nekrodots/assets/30672253/f08d0a55-e7f6-471d-9334-8d8f7dc344a2)


https://github.com/FelipeFMA/nekrodots/assets/30672253/8fabed74-0e09-45c9-ab8d-b4ddabb3daf3


## Setup Guide

### Prerequisites

- **Arch Linux with Hyprland up and running**

### Let's start the setup # Not done writing it yet

01. Update your system.
   ```bash
   sudo pacman -Syyu
   ```

02. Install yay.
   ```bash
   sudo pacman -S --needed git base-devel && git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg -si
   ```

03. Packages you need to install.
   ```bash
   yay -S alacritty waybar wofi qt5ct qt6ct nwg-look adw-gtk3 kvantum kvantum-qt5 appimagelauncher-bin spotify-launcher vlc unzip unrar upscayl-bin thunar thunar-archive-plugin thunar-volman swaync steam spotify-launcher slurp screen reflector qbittorrent polkit-gnome pavucontrol papirus-icon-theme papirus-folders openrgb localsend-bin kolourpaint hyprpicker hyprpaper gnome-disk-utility git gimp fastfetch firefox breeze-icons bluez bluez-libs bluez-utils blueman wl-clipboard xdg-desktop-portal-hyprland
   ```

04. Set papirus-colors to black.
   ```bash
   papirus-folders -C black
   ```

05. Install [this](https://github.com/GabePoel/KvLibadwaita) kvantum theme.
   ```bash
   git clone https://github.com/GabePoel/KvLibadwaita.git && cd KvLibadwaita
   ```
   ```bash
   sudo chmod +x install.sh
   ```
   ```bash
   sudo ./install.sh
   ```

06. Enable bluetooth.
   ```bash
   sudo systemctl enable --now bluetooth
   ```

07. Install fonts.
   ```bash
   yay -S noto-fonts noto-fonts-cjk noto-fonts-emoji noto-fonts-extra otf-font-awesome ttf-nerd-fonts-symbols
   ```

08. Put the config files in ~/.config

09. Edit ~/.config/hypr/hyprpaper.conf to set up the wallpaper.

**You're done!**

![Preview 2](https://github.com/FelipeFMA/nekrodots/assets/30672253/8cd17e02-79a3-49ac-80f6-29af66de957a)


Now you have a simple but incredibly good-looking window manager.
