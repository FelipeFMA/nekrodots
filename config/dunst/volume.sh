#!/bin/bash

msgId="3378424"

volume="$(pactl get-sink-volume @DEFAULT_SINK@ | awk '{print $5}' | sed 's/%//')"
mute="$(pactl get-sink-mute @DEFAULT_SINK@ | awk '{print $2}')"

if [[ $volume == 0 || "$mute" == "yes" ]]; then
	dunstify -a "changeVolume" -u low -i audio-volume-muted -t 1500 -r "$msgId" "Volume muted" 
else
	dunstify -a "changeVolume" -u low -i audio-volume-high -r "$msgId" \
	-h int:value:"$volume" -t 1500 "Volume: ${volume}%"
fi

canberra-gtk-play -i audio-volume-change -d "changeVolume"
