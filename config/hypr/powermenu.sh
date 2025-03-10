#!/bin/bash

CHOICE=$(echo -e "  suspend\n shutdown\n reboot" | bemenu --fb "#1e1e2e" --ff "#cdd6f4" --nb "#1e1e2e" --nf "#cdd6f4" --tb "#1e1e2e" --hb "#1e1e2e" --tf "#f38ba8" --hf "#f9e2af" --af "#cdd6f4" --ab "#1e1e2e" -b --prompt '' --no-spacing --hp 20 --ch 20 --cw 2)

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
