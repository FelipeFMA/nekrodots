#!/usr/bin/env bash

# Script to convert the result of 'pacman -Qe' into a one-line list of packages without the version numbers.
# By: Felipe Avelar.

# help message
usage() {
  echo
  echo " Usage: $0 [-m] [-h]"
  echo "  -m  Show only manually installed packages (equivalent to pacman -Qem)"
  echo "  -h  Display this help menu"
  echo
  exit 1
}

# check if user is on arch
if ! command -v pacman &> /dev/null; then
  echo
  echo "This script only works on Arch Linux-based systems."
  echo
  exit 1
fi

# show all packages by default
show_all=true

# check for arguments
while getopts "mh" opt; do
  case $opt in
    m)
      show_all=false
      ;;
    h)
      usage
      ;;
    \?)
      usage
      ;;
  esac
done

# get the packages list
if $show_all; then
  # all packages
  packages=$(pacman -Qe)
else
  # only manual packages
  packages=$(pacman -Qem)
fi

# do the magic
result=""
while IFS= read -r line; do
  package=$(echo "$line" | awk '{print $1}')
  result+="$package "
done <<< "$packages"

# make it one line
result=$(echo "$result" | sed 's/ *$//')

# show the result
echo
echo "$result"
echo
