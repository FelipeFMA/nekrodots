# NekroDots
## Minimalistic hyprland setup (on arch btw)


**⚠️ Disclaimer: Configurations in this repository are adapted for my specific hardware and needs. If you intend to replicate it, be aware that tweaking will be necessary.**

![image](https://github.com/FelipeFMA/nekrodots/assets/30672253/4536b938-ad5c-4127-bc75-b85a1883a46d)


https://github.com/FelipeFMA/nekrodots/assets/30672253/9747a66c-4da8-488a-9568-7d77cbc688c9


## Setup Guide

### Prerequisites

- **Arch Linux with Hyprland up and running**

### Let's start the setup!
01. Update your system.
   ```bash
   sudo pacman -Syyu
   ```

02. Install [yay](https://github.com/Jguer/yay).
   ```bash
   sudo pacman -S --needed git base-devel && git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg -si
   ```

03. Packages you need to install.
   ```bash
   yay -S alacritty waybar wofi qt5ct qt6ct nwg-look adw-gtk3 kvantum kvantum-qt5 appimagelauncher-bin spotify-launcher vlc unzip unrar upscayl-bin thunar thunar-archive-plugin thunar-volman swaync steam spotify-launcher slurp screen reflector qbittorrent polkit-gnome pavucontrol papirus-icon-theme papirus-folders openrgb localsend-bin kolourpaint hyprpicker hyprpaper gnome-disk-utility git gimp fastfetch firefox breeze-icons bluez bluez-libs bluez-utils blueman wl-clipboard xdg-desktop-portal-hyprland fastfetch
   ```

04. Set `papirus-colors` to black.
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

08. Put the config files in `~/.config`

09. Put the `[.]icons` files in `~/.icons`

10. Use `nwg-look` to select theme `adw-gtk3-dark` and `Simp1e` cursor

11. Open `kvantum` and select the `KvLibadwaitaDark` theme

12. Open `qt5ct` and select `kvantum-dark` style, do the same for `qt6ct`

13. Edit `~/.config/hypr/hyprpaper.conf` to set up the wallpaper.

**You're done!**
![image](https://github.com/FelipeFMA/nekrodots/assets/30672253/2fbd069c-83fc-4292-a23c-030d2ccd6c93)



Now you have a minimalistic and incredibly good-looking desktop.
