#!/bin/bash
# brightness.sh

msgId="3378423"

# Ajusta o brilho com o comando brightnessctl, com o argumento recebido
brightnessctl "$@" > /dev/null

# Obtém o brilho atual
brightness="$(brightnessctl g | awk '{print int($1)}')"
max_brightness="$(brightnessctl m | awk '{print int($1)}')"
percentage=$((brightness * 100 / max_brightness))

if [[ "$brightness" == "0" ]]; then
    dunstify -a "changeBrightness" -u low -i "dialog-information" -r "$msgId" "Brightness: OFF"
else
    dunstify -a "changeBrightness" -u low -i "dialog-information" -r "$msgId" \
    -h int:value:"$percentage" -t 2000 "Brightness: ${percentage}%"
fi
