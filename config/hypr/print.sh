#!/bin/bash

file=$HOME/Pictures/screenshots/swappy-$(date +%Y%m%d-%H%M%S).png
grim -g "$(slurp)" - | swappy -f - -o $file
