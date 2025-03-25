#!/bin/bash

CHOICE=$(echo -e "   Suspend\n   Shutdown\n   Reboot" | rofi -dmenu)

case $CHOICE in
"   Suspend")
systemctl suspend
;;
"   Shutdown")
systemctl poweroff
;;
"   Reboot")
systemctl reboot
;;
*)
exit 0
;;
esac
