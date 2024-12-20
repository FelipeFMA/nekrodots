# By: Felipe Avelar
# ~/.bashrc

# Comment if not using autologin.
if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then
  sleep 1 && Hyprland
fi

echo
fastfetch -l small
echo

PS1='\[\e[38;2;168;153;132m\]$(if [ "$PWD" == "$HOME" ]; then echo -e " \[\e[38;2;168;153;132m\]~"; else echo -e " \[\e[38;2;168;153;132m\]\w"; fi)\n\[\e[m\] > '


alias sudo='sudo -p "Password: " '
alias fastfetch='fastfetch -l small'
alias grep='grep --color=auto'
alias cat='bat'
alias ls='lsd'
alias la='lsd -a'
alias l='lsd -l'
alias ll='lsd -la'
alias felipao='clear; ssh felipe@xxx.xxx.xxx.xx'
alias avavelar='clear; ssh felipe@xxx.xxx.xxx.xx'
alias h='helix'
alias ai='tgpt --provider groq --model Mixtral-8x7b-32768 --key xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
bind 'set completion-ignore-case on'
