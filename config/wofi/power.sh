#!/bin/bash

entries="󰍃 Logout\n Suspend\n Reboot\n󰐥 Shutdown"

selected=$(echo -e $entries|wofi --width 250 --height 220 -p "See you later!" --dmenu -c ~/.config/wofi/launcher.txt --cache-file /dev/null | awk '{print tolower($2)}')

case $selected in
  logout)
    exec loginctl terminate-user $USER;;
  suspend)
    exec systemctl suspend;;
  reboot)
    exec systemctl reboot;;
  shutdown)
    exec systemctl poweroff -i;;
esac
