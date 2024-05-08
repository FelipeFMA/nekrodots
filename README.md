# NekroDots
## Minimalistic hyprland setup (on arch btw)


**⚠️ Disclaimer: Configurations in this repository are adapted for my specific hardware and needs. If you intend to replicate it, be aware that tweaking will be necessary.**

![preview](https://github.com/FelipeFMA/nekrodots/assets/30672253/2534c33e-cae5-4787-8845-50163bbeaebf)


https://github.com/FelipeFMA/nekrodots/assets/30672253/b96653bc-df87-4bff-a477-4839c82aa2b1


## Setup Guide

### Prerequisites

- **Arch Linux with Hyprland up and running**

### Let's start the setup!
### I'm not done writing it yet (it misses a lot of things)
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
   yay -S alacritty waybar wofi qt5ct qt6ct nwg-look adw-gtk3 kvantum kvantum-qt5 appimagelauncher-bin spotify-launcher vlc unzip unrar upscayl-bin thunar thunar-archive-plugin thunar-volman swaync steam spotify-launcher slurp screen reflector qbittorrent polkit-gnome pavucontrol papirus-icon-theme papirus-folders openrgb localsend-bin kolourpaint hyprpicker hyprpaper gnome-disk-utility git gimp fastfetch firefox breeze-icons bluez bluez-libs bluez-utils blueman wl-clipboard xdg-desktop-portal-hyprland fastfetch
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
   yay -S noto-fonts noto-fonts-cjk noto-fonts-extra otf-font-awesome ttf-nerd-fonts-symbols ttf-apple-emoji ttf-opensans ttf-roboto
   ```

08. Put the config files in ~/.config

09. Edit ~/.config/hypr/hyprpaper.conf to set up the wallpaper.

**You're done!**

![preview 2](https://github.com/FelipeFMA/nekrodots/assets/30672253/cfe86e40-13c0-46ba-8fd6-4e2d2f160532)



Now you have a simple but incredibly good-looking window manager.
