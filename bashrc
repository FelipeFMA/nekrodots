# By: Felipe Avelar
# ~/.bashrc
#

# Uncomment if using autologin.
#if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then
#  Hyprland
#fi


[[ $- != *i* ]] && return

echo
fastfetch -l small
echo

alias grep='grep --color=auto'
alias ls='lsd'
alias l='lsd -l'
alias ll='lsd -la'
alias oci='clear; ssh ********@***.***.***.**' # I won't show you my ip :P
PS1='\[\e[1;34m\]$(if [ "$PWD" == "$HOME" ]; then echo -e " ~"; else echo -e " \w"; fi)\n\[\e[m\] ➜ '
