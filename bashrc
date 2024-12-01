# By: Felipe Avelar
# ~/.bashrc

echo
fastfetch -l small
echo

PS1='\[\e[38;2;168;153;132m\]$(if [ "$PWD" == "$HOME" ]; then echo -e " \[\e[38;2;168;153;132m\]~"; else echo -e " \[\e[38;2;168;153;132m\]\w"; fi)\n\[\e[m\] > '

alias sudo="sudo "
alias fastfetch='fastfetch -l small'
alias grep='grep --color=auto'
alias cat='bat'
alias ls='lsd'
alias l='lsd -l'
alias ll='lsd -la'
alias felipao='clear; ssh felipe@xxx.xxx.xxx.xx'
alias avavelar='clear; ssh felipe@xxx.xxx.xxx.xx'
alias h='helix'
bind 'set completion-ignore-case on'
