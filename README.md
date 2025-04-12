<div align="center">

# nekrodots
### *My Catppuccin-themed Arch Linux setup*

</div>

<p align="center">

![image](https://github.com/user-attachments/assets/693115d4-40c9-4ba3-bdfa-f2159d1c25b6)

</p>

<div align="center">

  ![Hyprland](https://img.shields.io/badge/Hyprland-1e1e2e?style=for-the-badge&logo=hyprland&logoColor=b4befe)
  ![Arch Linux](https://img.shields.io/badge/Arch_Linux-1e1e2e?style=for-the-badge&logo=arch-linux&logoColor=b4befe)
  ![Waybar](https://img.shields.io/badge/Waybar-1e1e2e?style=for-the-badge&logoColor=b4befe)

</div>

## <span style="color:#f5c2e7">🌸 Overview</span>

`nekrodots` is a soft, eye-friendly dotfiles collection for Hyprland on Arch Linux. This configuration embraces the Catppuccin color scheme to create a comfortable, distraction-free desktop experience that's gentle on your eyes during long coding sessions.

---

## <span style="color:#b4befe">🐋 Features</span>

- **Catppuccin Theme** - Soft, pastel colors that reduce eye strain
- **Hyprland** - A dynamic tiling Wayland compositor with Catppuccin styling
- **Comfortable UI** - Balanced contrast and carefully selected colors
- **Custom Keybindings** - Optimized for efficiency
- **Integrated Tools** - Waybar, Rofi, Dunst, and more, all themed with Catppuccin

---

## <span style="color:#f5c2e7">🐈 Components</span>

| Software | Description |
|----------|-------------|
| `hyprland` | Dynamic tiling Wayland compositor |
| `waybar` | Customizable Wayland bar |
| `rofi` | Application launcher |
| `dunst` | Notification daemon |
| `foot` | Terminal emulator |
| `helix` | Modal text editor |
| `fish` | User-friendly shell |
| `hyprpaper` | Wallpaper utility for Hyprland |
| `hyprlock` | Screen locker |
| `hypridle` | Idle daemon |

---

## <span style="color:#c9cbff">🦋 Screenshots</span>

<details>
<summary>Click to expand screenshots</summary>
<br>

### Desktop
![image](https://github.com/user-attachments/assets/2b0790d8-1e1e-4f4c-826c-1acab80a6a27)


### Terminal
![image](https://github.com/user-attachments/assets/709c561b-d442-4fba-9292-051eb8557348)

</details>

---

## <span style="color:#f5c2e7">🌺 Installation</span>

```bash
# Clone the repository
git clone https://github.com/yourusername/nekrodots-hyprland.git

# Navigate to the repository configurations
cd nekrodots-hyprland/config

# Copy it all to your ~/.config
cp * ~/.config -r
```

---

## <span style="color:#b4befe">🧁 Configuration</span>

The configuration is organized in the `config/` directory:

```
config/
├── hypr/             # Hyprland configuration
├── waybar/           # Waybar setup and styling
├── fish/             # Fish shell configuration
├── foot/             # Terminal configuration
├── rofi/             # Application launcher
└── dunst/            # Notification daemon
```


---

## <span style="color:#f5c2e7">🌈 Catppuccin Color Palette</span>

This theme uses the following Catppuccin colors, primarily the Mocha variant.

<details>
<summary>🌿 Mocha</summary>
<table>
	<tr>
		<th></th>
		<th>Labels</th>
		<th>Hex</th>
		<th>RGB</th>
		<th>HSL</th>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_rosewater.png" width="23"/></td>
		<td>Rosewater</td>
		<td><code>#f5e0dc</code></td>
		<td><code>rgb(245, 224, 220)</code></td>
		<td><code>hsl(10, 56%, 91%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_flamingo.png" width="23"/></td>
		<td>Flamingo</td>
		<td><code>#f2cdcd</code></td>
		<td><code>rgb(242, 205, 205)</code></td>
		<td><code>hsl(0, 59%, 88%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_pink.png" width="23"/></td>
		<td>Pink</td>
		<td><code>#f5c2e7</code></td>
		<td><code>rgb(245, 194, 231)</code></td>
		<td><code>hsl(316, 72%, 86%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_mauve.png" width="23"/></td>
		<td>Mauve</td>
		<td><code>#cba6f7</code></td>
		<td><code>rgb(203, 166, 247)</code></td>
		<td><code>hsl(267, 84%, 81%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_red.png" width="23"/></td>
		<td>Red</td>
		<td><code>#f38ba8</code></td>
		<td><code>rgb(243, 139, 168)</code></td>
		<td><code>hsl(343, 81%, 75%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_maroon.png" width="23"/></td>
		<td>Maroon</td>
		<td><code>#eba0ac</code></td>
		<td><code>rgb(235, 160, 172)</code></td>
		<td><code>hsl(350, 65%, 77%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_peach.png" width="23"/></td>
		<td>Peach</td>
		<td><code>#fab387</code></td>
		<td><code>rgb(250, 179, 135)</code></td>
		<td><code>hsl(23, 92%, 75%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_yellow.png" width="23"/></td>
		<td>Yellow</td>
		<td><code>#f9e2af</code></td>
		<td><code>rgb(249, 226, 175)</code></td>
		<td><code>hsl(41, 86%, 83%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_green.png" width="23"/></td>
		<td>Green</td>
		<td><code>#a6e3a1</code></td>
		<td><code>rgb(166, 227, 161)</code></td>
		<td><code>hsl(115, 54%, 76%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_teal.png" width="23"/></td>
		<td>Teal</td>
		<td><code>#94e2d5</code></td>
		<td><code>rgb(148, 226, 213)</code></td>
		<td><code>hsl(170, 57%, 73%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_sky.png" width="23"/></td>
		<td>Sky</td>
		<td><code>#89dceb</code></td>
		<td><code>rgb(137, 220, 235)</code></td>
		<td><code>hsl(189, 71%, 73%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_sapphire.png" width="23"/></td>
		<td>Sapphire</td>
		<td><code>#74c7ec</code></td>
		<td><code>rgb(116, 199, 236)</code></td>
		<td><code>hsl(199, 76%, 69%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_blue.png" width="23"/></td>
		<td>Blue</td>
		<td><code>#89b4fa</code></td>
		<td><code>rgb(137, 180, 250)</code></td>
		<td><code>hsl(217, 92%, 76%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_lavender.png" width="23"/></td>
		<td>Lavender</td>
		<td><code>#b4befe</code></td>
		<td><code>rgb(180, 190, 254)</code></td>
		<td><code>hsl(232, 97%, 85%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_text.png" width="23"/></td>
		<td>Text</td>
		<td><code>#cdd6f4</code></td>
		<td><code>rgb(205, 214, 244)</code></td>
		<td><code>hsl(226, 64%, 88%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_subtext1.png" width="23"/></td>
		<td>Subtext1</td>
		<td><code>#bac2de</code></td>
		<td><code>rgb(186, 194, 222)</code></td>
		<td><code>hsl(227, 35%, 80%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_subtext0.png" width="23"/></td>
		<td>Subtext0</td>
		<td><code>#a6adc8</code></td>
		<td><code>rgb(166, 173, 200)</code></td>
		<td><code>hsl(228, 24%, 72%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_overlay2.png" width="23"/></td>
		<td>Overlay2</td>
		<td><code>#9399b2</code></td>
		<td><code>rgb(147, 153, 178)</code></td>
		<td><code>hsl(228, 17%, 64%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_overlay1.png" width="23"/></td>
		<td>Overlay1</td>
		<td><code>#7f849c</code></td>
		<td><code>rgb(127, 132, 156)</code></td>
		<td><code>hsl(230, 13%, 55%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_overlay0.png" width="23"/></td>
		<td>Overlay0</td>
		<td><code>#6c7086</code></td>
		<td><code>rgb(108, 112, 134)</code></td>
		<td><code>hsl(231, 11%, 47%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_surface2.png" width="23"/></td>
		<td>Surface2</td>
		<td><code>#585b70</code></td>
		<td><code>rgb(88, 91, 112)</code></td>
		<td><code>hsl(233, 12%, 39%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_surface1.png" width="23"/></td>
		<td>Surface1</td>
		<td><code>#45475a</code></td>
		<td><code>rgb(69, 71, 90)</code></td>
		<td><code>hsl(234, 13%, 31%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_surface0.png" width="23"/></td>
		<td>Surface0</td>
		<td><code>#313244</code></td>
		<td><code>rgb(49, 50, 68)</code></td>
		<td><code>hsl(237, 16%, 23%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_base.png" width="23"/></td>
		<td>Base</td>
		<td><code>#1e1e2e</code></td>
		<td><code>rgb(30, 30, 46)</code></td>
		<td><code>hsl(240, 21%, 15%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_mantle.png" width="23"/></td>
		<td>Mantle</td>
		<td><code>#181825</code></td>
		<td><code>rgb(24, 24, 37)</code></td>
		<td><code>hsl(240, 21%, 12%)</code></td>
	</tr>
	<tr>
		<td><img src="assets/palette/circles/mocha_crust.png" width="23"/></td>
		<td>Crust</td>
		<td><code>#11111b</code></td>
		<td><code>rgb(17, 17, 27)</code></td>
		<td><code>hsl(240, 23%, 9%)</code></td>
	</tr>
</table>
</details>

<details>
<summary>🌻 Latte</summary>

![catppuccin-latte](https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/palette/latte.png)
</details>


## <span style="color:#b4befe">✨ Acknowledgments</span>

- Inspired by the [Catppuccin](https://github.com/catppuccin/catppuccin) color scheme
- Thanks to the Hyprland community
- All creators of the tools used in this configuration
- Special thanks to eye-comfort focused design principles

---

<div align="center">

  <p style="color:#f5c2e7">Created with ♥ by Felipe Avelar</p>

</div>

<div align="center">
<p style="color:#b4befe">Gentle on your eyes, powerful in functionality</p>
</div>
