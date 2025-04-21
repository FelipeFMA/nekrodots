<div align="center">

# nekrodots
### *My Arch Linux setup*

</div>

<p align="center">

![image](https://github.com/user-attachments/assets/c8b5e9ca-2a34-41d3-a8ac-95ec02044ec7)

</p>

<div align="center">

  ![Hyprland](https://img.shields.io/badge/Hyprland-1b1b1b?style=for-the-badge&logo=hyprland&logoColor=ffffff)
  ![Arch Linux](https://img.shields.io/badge/Arch_Linux-1b1b1b?style=for-the-badge&logo=arch-linux&logoColor=ffffff)
  ![Waybar](https://img.shields.io/badge/Waybar-1b1b1b?style=for-the-badge&logoColor=ffffff)

</div>

## <span style="color:#ffffff">Overview</span>

`nekrodots` is a monochromatic dotfiles collection for Hyprland on Arch Linux. This configuration uses a clean gray color (#1b1b1b) for the background and white (#ffffff) for the foreground theme to create a minimalist, distraction-free desktop experience that's focused and elegant during long coding sessions.

---

## <span style="color:#ffffff">Features</span>

- **Monochromatic Theme** - Clean black and white design for focus and clarity
- **Hyprland** - A dynamic tiling Wayland compositor with minimalist styling
- **High Contrast UI** - Clear visual hierarchy with black and white elements
- **Custom Keybindings** - Optimized for efficiency
- **Integrated Tools** - Waybar, Rofi, Dunst, and more, all themed consistently

---

## <span style="color:#ffffff">Components</span>

| Software | Description |
|----------|-------------|
| `hyprland` | Dynamic tiling Wayland compositor |
| `waybar` | Customizable Wayland bar |
| `rofi` | Application launcher |
| `dunst` | Notification daemon |
| `kitty` | Terminal emulator |
| `helix` | Modal text editor |
| `fish` | User-friendly shell |
| `btop` | System monitor |
| `fastfetch` | System information tool |
| `nemo` | File manager |
| `mpv` | Media player |
| `vlc` | Media player |
| `zathura` | PDF viewer |

---

## Screenshots

<details>
<summary>Click to expand screenshots</summary>
<br>

### Desktop
![image](https://github.com/user-attachments/assets/2b0790d8-1e1e-4f4c-826c-1acab80a6a27)


### Terminal
![image](https://github.com/user-attachments/assets/709c561b-d442-4fba-9292-051eb8557348)

</details>

---

## <span style="color:#ffffff">Installation</span>

```bash
# Clone the repository
git clone https://github.com/FelipeFMA/nekrodots.git

# Navigate to the repository configurations
cd nekrodots/config

# Copy it all to your ~/.config
cp * ~/.config -r
```

---

## <span style="color:#ffffff">Configuration</span>

The configuration is organized in the `config/` directory:

```
config/
├── better-control/      # Better control configuration
├── btop/                # System monitor configuration
├── chrome-theme/        # Chrome browser theme
├── dunst/               # Notification daemon
├── fastfetch/           # System information tool
├── fish/                # Fish shell configuration
├── helix/               # Modal text editor configuration
├── hypr/                # Hyprland configuration
├── kitty/               # Terminal emulator
├── mpv/                 # Media player
├── nemo/                # File manager
├── rofi/                # Application launcher
├── vlc/                 # Media player
├── waybar/              # Waybar setup and styling
├── zathura/             # PDF viewer
├── code-flags.conf      # VS Code flags
├── electron-flags.conf  # Electron flags
└── spotify-flags.conf   # Spotify flags
```


---

## <span style="color:#ffffff">Monochromatic Color Palette</span>

This theme uses a simple monochromatic color scheme:

| Element | Color | Hex | RGB |
|---------|-------|-----|-----|
| Background | Gray | `#1b1b1b` | `rgb(27, 27, 27)` |
| Foreground | White | `#ffffff` | `rgb(255, 255, 255)` |
| Accent/Highlights | White | `#ffffff` | `rgb(255, 255, 255)` |
| Inactive Elements | Gray | `#1b1b1b` | `rgb(27, 27, 27)` |


## <span style="color:#ffffff">Acknowledgments</span>

- Thanks to the Hyprland community
- All creators of the tools used in this configuration
- Special thanks to minimalist design principles

---

<div align="center">

  <p style="color:#ffffff">Created by Felipe Avelar</p>

</div>

<div align="center">
<p style="color:#ffffff">Minimalist design, powerful functionality</p>
</div>
