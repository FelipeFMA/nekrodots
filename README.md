# nekrodots 🐧

**⚠️ Disclaimer: Configurations in this repository are adapted for my specific hardware and needs. If you intend to replicate it, be aware that tweaking will be necessary.**

**⚠️ Disclaimer 2: My dots are usually up to date but the info on the readme can be old.**

**⚠️ Disclaimer 3: There is the Monochromatic version (old) and the Gruvbox version (new). The README assumes you want to install the Gruvbox one.**

<details>
  <summary>⚫ Click here for the Monochromatic version preview</summary>

![desktop](https://github.com/FelipeFMA/nekrodots/assets/30672253/5281c631-40fb-4bc3-a7fe-e21a7d516dbd)

![apps](https://github.com/FelipeFMA/nekrodots/assets/30672253/47de9ddd-e654-48af-8fee-0bee3f91b41d)

https://github.com/FelipeFMA/nekrodots/assets/30672253/bc1f6102-ebe5-4178-9a55-3f703de64ebc

</details>

<details>
  <summary>🟠 Click here for the Gruvbox version preview</summary>

![desktop](https://github.com/FelipeFMA/nekrodots/assets/30672253/fc7c3624-12eb-4aea-a12b-bfaf648646fe)

![apps](https://github.com/FelipeFMA/nekrodots/assets/30672253/344c73e4-9a34-4b44-987d-8a9bcf95a899)

https://github.com/FelipeFMA/nekrodots/assets/30672253/3d0944eb-8823-4fe0-a58d-b759d62f76df

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
yay -S adw-gtk-theme ani-cli appimagelauncher-bin base base-devel bash-completion bat blueman bluez-utils bottles breeze-icons btop cliphist cmatrix cowsay cpupower fastfetch filezilla firefox gcolor3 gimp git gnome-disk-utility gradience grim helix heroic-games-launcher-bin htop hypridle hyprland hyprpaper hyprpicker imv informant intel-ucode jdk8-openjdk jq jre-openjdk jre21-openjdk jre8-openjdk kitty kolourpaint kvantum kvantum-qt5 kvantum-theme-libadwaita-git lib32-mangohud libreoffice-fresh linux linux-firmware linux-headers localsend-bin lsd man-db man-pages mangohud mcpelauncher-appimage nano neofetch neovim networkmanager noto-fonts-cjk noto-fonts-extra ntfs-3g nvidia nvidia-settings nwg-look obs-studio pacman-contrib papirus-folders papirus-icon-theme pavucontrol pipewire-alsa pipewire-ffado pipewire-pulse pipewire-roc pipewire-v4l2 pipewire-zeroconf polkit-gnome prismlauncher-qt5-bin protonup-qt-bin qbittorrent qt5ct qt6ct reflector screen slurp steam sudo swaync throttled thunar thunar-archive-plugin thunar-media-tags-plugin tldr ttf-apple-emoji ttf-jetbrains-mono-nerd ttf-ms-win11-auto unrar unzip virtualbox virtualbox-guest-iso vkd3d vlc waybar wget wine wine-gecko wine-mono wofi wttrbar wtype xarchiver xdg-desktop-portal-hyprland yay-bin zathura zathura-pdf-poppler zip
   ```
03. I compile hyprlock myself using [this](https://github.com/hyprwm/hyprlock/pull/283) patch, but you don't need to if you don't have a nvidia card.

04. Clone the repo.
   ```bash
   cd && git clone https://github.com/FelipeFMA/nekrodots.git
   ```

05. Copy everything from ``~/nekrodots/config/`` to ``~/.config/``.
   ```bash
   cp ~/nekrodots/gruvbox/config/* ~/.config/ -r
   ```

06. Put ``throttled.conf`` in the correct location (Note: This file contains my CPU undervolt settings; do not apply these settings if you are not me!).
   ```bash
   sudo cp ~/nekrodots/throttled.conf /etc/
   ```

07. Put ``cpupower`` in the correct location (Note: This file contains my CPU clock settings; do not apply these settings if you are not me!).
   ```bash
   sudo cp ~/nekrodots/cpupower /etc/default/
   ```

08. Enable the ``throttled`` service (Note: Activate the throttled service if you intend to utilize it).
   ```bash
   sudo systemctl enable throttled
   ```

09. Enable the ``cpupower`` service (Note: Activate the throttled service if you intend to utilize it).
   ```bash
   sudo systemctl enable cpupower
   ```
10. Move ``bashrc`` to ``~/.bashrc``.
  ```bash
  mv ~/.bashrc ~/.bashrc.backup && cp ~/nekrodots/gruvbox/bashrc ~/.bashrc
  ```

11. Reboot and enjoy! If you haven't installed any display manager, you'll need to start hyprland by typing ``Hyprland`` on the TTY.
   ```bash
   sudo reboot now
   ```
