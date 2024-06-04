# Nix configuration file
# By: Felipe Avelar
# NekroDots


{ config, lib, pkgs, osConfig, ... }:

{
  imports =
    [
      ./hardware-configuration.nix
    ];

  # Bootloader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  # Set the host name
  networking.hostName = "NixOS-G7";

  # Enable networking
  networking.networkmanager.enable = true;

  # Set your time zone.
  time.timeZone = "America/Sao_Paulo";

  # Locale stuff.
  i18n.defaultLocale = "pt_BR.UTF-8";

  i18n.extraLocaleSettings = {
    LC_ADDRESS = "pt_BR.UTF-8";
    LC_IDENTIFICATION = "pt_BR.UTF-8";
    LC_MEASUREMENT = "pt_BR.UTF-8";
    LC_MONETARY = "pt_BR.UTF-8";
    LC_NAME = "pt_BR.UTF-8";
    LC_NUMERIC = "pt_BR.UTF-8";
    LC_PAPER = "pt_BR.UTF-8";
    LC_TELEPHONE = "pt_BR.UTF-8";
    LC_TIME = "pt_BR.UTF-8";
  };

  # Enable the X11 windowing system.
  services.xserver.enable = true;

  # Configure keymap in X11
  services.xserver = {
    xkb.layout = "br";
    xkb.variant = "";
  };

  # Configure console keymap (TTY)
  console.keyMap = "br-abnt2";

  # Enable CUPS to print documents.
  services.printing.enable = true;

  # Enable sound with pipewire.
  hardware.pulseaudio.enable = false;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
    # If you want to use JACK applications, uncomment this
    #jack.enable = true;

    # use the example session manager (no others are packaged yet so this is enabled by default,
    # no need to redefine it in your config for now)
    # media-session.enable = true;
  };

  # Enable touchpad support (enabled default in most desktopManager).
  services.libinput.enable = true;

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.felipe = {
    isNormalUser = true;
    description = "Felipe Avelar";
    extraGroups = [ "networkmanager" "wheel" ];
    packages = with pkgs; [
    ];
  };

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  # List services that you want to enable:
  services.openssh.enable = false;
  services.throttled.enable = true;
  hardware.bluetooth.enable = true;
  hardware.bluetooth.powerOnBoot = true;
  services.blueman.enable = true;

  # Open ports in the firewall.
  # networking.firewall.allowedTCPPorts = [ ... ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
  networking.firewall.enable = false;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It‘s perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  system.stateVersion = "24.05"; # Did you read the comment?

  # Window Manager.
  programs.hyprland.enable = true;

  # Envrironment Variables.
  environment.variables = {
    GTK_THEME = "adw-gtk3-dark";
    XCURSOR_THEME = "macOS-BigSur";
    GTK_ICON_THEME = "Adwaita-dark";
    QT_QPA_PLATFORMTHEME = "qt6ct";  
  };

  # Installed pkgs. / apps.
  environment.systemPackages = with pkgs; [
    alacritty
    git
    firefox
    waybar
    wttrbar
    screen
    nwg-look
    apple-cursor
    adw-gtk3
    gnome.adwaita-icon-theme
    ani-cli
    blueman
    bluez
    btop
    classicube
    cliphist
    cmatrix
    cowsay
    fastfetch
    filezilla
    gcolor3
    gimp
    git
    gradience
    grim
    heroic
    htop
    hyprpaper
    hyprpicker
    imv
    localsend
    lsd
    mpv
    obs-studio
    pavucontrol
    pcmanfm
    polkit_gnome
    prismlauncher
    protonup-qt
    qbittorrent
    screen
    slurp
    steam
    swaynotificationcenter
    tldr
    unrar
    unzip
    upscayl
    vlc
    wget
    wl-clipboard
    wlogout
    wofi
    xarchiver
    zip
    throttled
    vesktop
    killall
    xdg-user-dirs
    nix-search-cli
    libsForQt5.qt5ct
    kdePackages.qt6ct
    adwaita-qt
    adwaita-qt6
  ];

  fonts.packages = with pkgs; [
    nerdfonts
    noto-fonts
    noto-fonts-cjk
    noto-fonts-color-emoji
  ];

   virtualisation.virtualbox.host.enable = true;
   users.extraGroups.vboxusers.members = [ "felipe" ];
   virtualisation.virtualbox.host.enableExtensionPack = true;

services.xserver.displayManager.lightdm.enable = false;
services.xserver.displayManager.lightdm.greeters.gtk.enable = false;

  # Start of Nvidia stuff. ------------------------------------------------------------------------------
  # Enable OpenGL
  hardware.opengl = {
    enable = true;
    driSupport = true;
    driSupport32Bit = true;
  };

  # Load nvidia driver for Xorg and Wayland
  services.xserver.videoDrivers = ["nvidia"];

  hardware.nvidia = {

    # Modesetting is required.
    modesetting.enable = true;

    # Nvidia power management. Experimental, and can cause sleep/suspend to fail.
    # Enable this if you have graphical corruption issues or application crashes after waking
    # up from sleep. This fixes it by saving the entire VRAM memory to /tmp/ instead
    # of just the bare essentials.
    powerManagement.enable = false;

    # Fine-grained power management. Turns off GPU when not in use.
    # Experimental and only works on modern Nvidia GPUs (Turing or newer).
    powerManagement.finegrained = false;

    # Use the NVidia open source kernel module (not to be confused with the
    # independent third-party "nouveau" open source driver).
    # Support is limited to the Turing and later architectures. Full list of
    # supported GPUs is at:
    # https://github.com/NVIDIA/open-gpu-kernel-modules#compatible-gpus
    # Only available from driver 515.43.04+
    # Currently alpha-quality/buggy, so false is currently the recommended setting.
    open = false;

    # Enable the Nvidia settings menu,
	# accessible via `nvidia-settings`.
    nvidiaSettings = true;

    # Optionally, you may need to select the appropriate driver version for your specific GPU.
    package = config.boot.kernelPackages.nvidiaPackages.beta;
  };

  # Kernel Parameters
  boot.kernelParams = [
    "quiet"
    "nvidia.NVreg_PreserveVideoMemoryAllocations=1"
  ];

  boot.kernelModules = [ "nvidia" "nvidia_modeset" "nvidia_uvm" "nvidia_drm" ];
  # End of nvidia stuff ------------------------------------------------------------------------
}
