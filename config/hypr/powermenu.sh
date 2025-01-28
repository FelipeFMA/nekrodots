#!/bin/bash

CHOICE=$(echo -e "  suspend\n shutdown\n reboot" | bemenu --nb '#1b1b1b' --nf '#ffffff' --hb '#ffffff' --hf '#000000' --sb '#ffffff' --sf '#000000' --ab '#1b1b1b' --af '#ffffff' -b --prompt '' --no-spacing --hp 20 --ch 20 --cw 2)

case $CHOICE in
    "  suspend")
        systemctl suspend
        ;;
    " shutdown")
        systemctl poweroff
        ;;
    " reboot")
        systemctl reboot
        ;;
    *)
        exit 0
        ;;
esac
