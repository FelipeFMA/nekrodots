#!/bin/bash
# Original code: Nguyen Khac Trung Kien
# Fork by: Felipe Avelar
# Description: Plays ASCII animation of Bad Apple!! with optional audio
# Usage: ./run.sh [-h|--help]

# Exit on error
set -e

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Function to display usage information
usage() {
    echo
    echo "Usage: $0"
    echo "  -h, --help  Display this help message"
    echo
    exit 0
}

# Check for help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
fi

echo

# Ask for mpv audio playback
read -p "Do you want to use mpv to play sound? You need mpv installed to do that. (y/n): " choice

# Validate user input
if [[ ! $choice =~ ^[YyNn]$ ]]; then
    echo "Invalid input. Please enter 'y' or 'n'."
    exit 1
fi

# Handle mpv audio playback
if [[ $choice =~ ^[Yy]$ ]]; then
    # Check if mpv is installed
    if ! command -v mpv &> /dev/null; then
        echo
        echo "mpv is not installed. Please install it to use this feature."
        echo
        exit 1
    fi
    
    # Play audio in background
    mpv "${SCRIPT_DIR}/bad_apple.mp3" > /dev/null 2>&1 &
fi

echo

# Set frames directory
FRAMES_DIR="${SCRIPT_DIR}/frames-ascii"

# Validate frames directory
if [[ ! -d "$FRAMES_DIR" ]]; then
    echo "Error: Frames directory not found at $FRAMES_DIR"
    exit 1
fi

# Clear screen
printf "\033c"

# Play animation
for filename in $(ls -v "$FRAMES_DIR"); do
    # Move cursor to top-left
    tput cup 0 0
    
    # Construct full file path
    file="${FRAMES_DIR}/$filename"
    
    # Validate file existence
    if [[ -f "$file" ]]; then
        # Display frame
        cat "$file"
    fi
    
    # Wait for next frame
    sleep 0.024

done

# Exit with success
exit 0
