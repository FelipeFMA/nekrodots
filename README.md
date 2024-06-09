# NekroDots
## Minimalistic hyprland setup on Arch Linux (btw).

**⚠️ Disclaimer: Configurations in this repository are adapted for my specific hardware and needs. If you intend to replicate it, be aware that tweaking will be necessary.**

<details>
  <summary>📸 Click here for preview</summary>
   
![desktop](https://github.com/FelipeFMA/nekrodots/assets/30672253/0d6bdccc-509b-45c2-9fd9-985689231502)

![terminals](https://github.com/FelipeFMA/nekrodots/assets/30672253/23329521-f992-49dc-b7ba-6ec995c47237)

![gtkapps](https://github.com/FelipeFMA/nekrodots/assets/30672253/ff513a0e-9fd6-4c9f-a3f9-8b3fea648c84)

https://github.com/FelipeFMA/nekrodots/assets/30672253/0312f4df-66a9-4831-833d-19406682dd43

</details>

## Setup Guide

### Prerequisites

- **Arch Linux**
- **Internet connection**

### Let's start the setup!

01. Uncomment ``Color`` and ``ParallelDownloads`` in ``/etc/pacman.conf.`` You can also set ``ParallelDownloads`` to ``10``.
   ```bash
   sudo nano /etc/pacman.conf
   ```

02. Install yay.
   ```bash
   pacman -S --needed git base-devel && git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg -si
   ```

03. Download all the packages (These are the ones I use; if you are not me, you don't need most of them. Take a look and choose the ones you actually want).
   ```bash
   yay -S adw-gtk-theme alacritty ani-cli appimagelauncher-bin base base-devel blueman bluez-utils breeze-icons btop classicube-bin cliphist cmatrix code cowsay cpupower efibootmgr evhz-git fastfetch filezilla firefox gcolor3 gimp git gnome-disk-utility gradience grim gst-plugin-pipewire heroic-games-launcher-bin htop hyprland hyprlock hyprpaper hyprpicker imv informant intel-ucode jre-openjdk kolourpaint kvantum kvantum-qt5 kvantum-theme-libadwaita-git lib32-mangohud lib32-nvidia-utils-tkg lib32-opencl-nvidia-tkg libpulse libva-nvidia-driver linux linux-firmware linux-headers localsend-bin lsd man-db man-pages mangohud mpv nano networkmanager noto-fonts-cjk noto-fonts-extra nvidia-dkms-tkg nvidia-egl-wayland-tkg nvidia-settings-tkg nvidia-utils-tkg nwg-look obs-studio opencl-nvidia-tkg openrgb papirus-folders papirus-icon-theme pavucontrol pipewire pipewire-alsa pipewire-jack pipewire-pulse polkit-gnome prismlauncher-qt5-bin protonup-qt-bin python-zombie-imp qbittorrent qt5ct qt6ct reflector screen slurp sof-firmware steam swaync throttled thunar thunar-archive-plugin thunar-media-tags-plugin tldr ttf-apple-emoji ttf-jetbrains-mono-nerd ttf-ms-win11-auto unrar unzip upscayl-bin vesktop-bin virtualbox virtualbox-guest-iso vlc waybar wget wireplumber wl-clipboard wlogout wofi wttrbar xarchiver xdg-desktop-portal-hyprland yay-bin zip zram-generator
   ```

04. Clone the repo.
   ```bash
   cd && git clone https://github.com/FelipeFMA/nekrodots.git
   ```

05. Copy everything from ``~/nekrodots/config/`` to ``~/.config/``.
   ```bash
   cp ~/nekrodots/config/* ~/.config/ -r
   ```

06. Put ``throttled.conf`` in the correct location (Note: This file contains my CPU undervolt settings; do not apply these settings if you are not me!).
   ```bash
   sudo cp ~/nekrodots/throttled.conf /etc/
   ```

07. Put ``cpupower`` in the correct location (Note: This file contains my CPU clock settings; do not apply these settings if you are not me!).
   ```bash
   sudo cp ~/nekrodots/cpupower /etc/default/
   ```

08. Enable the ``throttled`` service. (Note: Activate the throttled service if you intend to utilize it.)
   ```bash
   sudo systemctl enable throttled
   ```

09. Enable the ``cpupower`` service. (Note: Activate the throttled service if you intend to utilize it.)
   ```bash
   sudo systemctl enable cpupower
   ```

10. Reboot and enjoy! If you haven't installed any display manager, you'll need to start hyprland by typing ``Hyprland`` on the TTY.
   ```bash
   sudo reboot now
   ```
