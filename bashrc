# By: Felipe Avelar
# ~/.bashrc
#

# Uncomment if using autologin.
#if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then
#  sleep 1 && Hyprland
#fi

[[ $- != *i* ]] && return

cat ~/.config/archascii.txt
echo

alias fastfetch='fastfetch -l small'
alias grep='grep --color=auto'
alias ls='lsd'
alias l='lsd -l'
alias ll='lsd -la'
alias oci='clear; ssh felipe@204.216.167.51'
PS1='\[\e[1;34m\]$(if [ "$PWD" == "$HOME" ]; then echo -e " \[\e[0;90m\]~"; else echo -e " \[\e[0;90m\]\w"; fi)\n\[\e[m\] ➜ '
