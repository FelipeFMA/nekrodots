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
   sudo pacman -Syu
   ```

02. Install [yay](https://github.com/Jguer/yay).
   ```bash
   sudo pacman -S --needed git base-devel && git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg -si
   ```

03. Install all the packages, those are my packages, exept drivers.
   ```bash
   yay -S zip xorg-xwayland xorg-server xdg-utils xdg-desktop-portal-hyprland xarchiver wofi wl-clipboard wget waybar upscayl-bin vlc upscayl-bin unzip unrar ttf-roboto ttf-opensans ttf-ms-win11-auto ttf-jetbrains-mono-nerd ttf-apple-emoji tldr thunar thunar-archive-plugin thunar-media-tags-plugin thunar-volman thorium-browser-bin swaync steam slurp seahorse screen reflector qt6ct qt6-wayland qt5ct qt5-websockets qt5-webengine qt5-wayland qt5-speech qt5-script qt5-networkauth qt5-multimedia qbittorrent protonup-qt-bin prismlauncher-qt5-bin polkit-gnome pavucontrol pipewire pipewire-alsa pipewire-jack pipewire-pulse papirus-icon-theme papirus-folders openrgb obs-studio nwg-look networkmanager network-manager-applet nano mpv lsd localsend-bin kvantum kvantum-qt5 kolourpaint kate imv hyprpicker hyprpaper htop heroic-games-launcher-bin grim gnome-disk-utility gimp flatpak fastfetch cowsay cmatrix classicube-bin btop breeze-icons blueman bluez-utils appimagelauncher-bin alacritty adw-gtk3 
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
   yay -S noto-fonts noto-fonts-cjk noto-fonts-extra ttf-roboto ttf-opensans ttf-ms-win11-auto ttf-jetbrains-mono-nerd ttf-apple-emoji awesome-terminal-fonts
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
