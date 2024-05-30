# NekroDots
## Minimalistic hyprland setup (on arch btw)


**⚠️ Disclaimer: Configurations in this repository are adapted for my specific hardware and needs. If you intend to replicate it, be aware that tweaking will be necessary.**

![image](https://github.com/FelipeFMA/nekrodots/assets/30672253/1b8f0a45-5bc3-4bee-b322-a6042d25dfaf)



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

03. Install all the packages, those are my packages, you definitely do not want all of them.
   ```bash
   yay -S adw-gtk-theme adw-gtk3 alacritty ani-cli appimagelauncher-bin base base-devel blueman bluez-utils breeze-icons btop classicube-bin cliphist cmatrix cowsay cpupower fastfetch filezilla gcolor3 gdb gimp git glibc-locales gnome-disk-utility gradience grim gst-plugin-pipewire heroic-games-launcher-bin htop hyprland hyprlock hyprpaper hyprpicker imv informant intel-media-driver intel-ucode iwd jre-openjdk kolourpaint kvantum kvantum-qt5 libpulse linux-zen linux-zen-headers localsend-bin lsd ly man-db man-pages mercury-browser-bin mkinitcpio-firmware mpv nano ncspot networkmanager libappindicator-gtk3 noto-fonts noto-fonts-cjk noto-fonts-extra nwg-look obs-studio openrgb papirus-folders papirus-icon-theme pavucontrol pcmanfm-gtk3 perl-image-exiftool pipewire pipewire-alsa pipewire-jack pipewire-pulse polkit-gnome prismlauncher-qt5-bin protonup-qt-bin qbittorrent qt5-multimedia qt5-networkauth qt5-script qt5-speech qt5-wayland qt5-webengine qt5-websockets qt5ct qt6-wayland qt6ct reflector screen slurp smartmontools sof-firmware steam swaync tldr unrar unzip upscayl-bin virtualbox vkd3d vlc waybar wget wine wine-gecko wine-mono wireless_tools wireplumber wl-clipboard wlogout wofi wttrbar xarchiver xdg-desktop-portal-hyprland xdg-utils xorg-server xorg-server xorg-xinit xorg-xwayland yarn yay-bin zathura zathura-pdf-poppler zip ttf-apple-emoji ttf-jetbrains-mono-nerd ttf-ms-win11-auto ttf-opensans ttf-roboto
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
   yay -S awesome-terminal-fonts noto-fonts noto-fonts-cjk noto-fonts-extra ttf-apple-emoji ttf-jetbrains-mono-nerd ttf-ms-win11-auto ttf-opensans ttf-roboto
   ```

08. Put the config files in `~/.config`.

09. Put the `[.]icons` files in `~/.icons`.

10. Use `nwg-look` to select theme `adw-gtk3-dark`.

11. Open `kvantum` and select the `KvLibadwaitaDark` theme.

12. Open `Gradience` and set the colors you want.
    
13. Open `qt5ct` and select `kvantum-dark` style, do the same for `qt6ct`.

14. Edit `~/.config/hypr/hyprpaper.conf` to set up the wallpaper.

**You're done!**
![image](https://github.com/FelipeFMA/nekrodots/assets/30672253/2fbd069c-83fc-4292-a23c-030d2ccd6c93)



Now you have a minimalistic and incredibly good-looking desktop.
