#!/bin/bash

# Script to convert the result of 'pacman -Qe' into a one-line list of packages without the version numbers.
# By: Felipe Avelar.


# check for user error
if [ -z "$1" ]; then
  echo "Usage: $0 packages.txt"
  exit 1
fi

# verify if file exists
if [ ! -f "$1" ]; then
  echo "file not found: $1"
  exit 1
fi

# remove number version
result=""
while IFS= read -r line; do
  package=$(echo "$line" | awk '{print $1}')
  result+="$package "
done < "$1"

# make it one line
result=$(echo "$result" | sed 's/ *$//')

# print the result
echo
echo "$result"
exho
