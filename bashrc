# By: Felipe Avelar
# https://github.com/FelipeFMA/nekrodots-sway

# ~/.bashrc

# Small fetch when opening terminal
echo
fastfetch -l small
echo


# Pretty sudo prompt
alias sudo='sudo '

# fastfetch small logo
alias fastfetch='fastfetch -l small'

# Colored grep
alias grep='grep --color=auto'

# bat instead of cat
alias cat='bat'

# lsd instead of ls
alias ls='lsd'
alias la='lsd -a'
alias l='lsd -l'
alias ll='lsd -la'

# SSH to my servers
alias felipao='clear; ssh felipe@134.65.28.106'
alias avavelar='clear; ssh felipe@204.216.164.72'

# Binds to Helix and Vim
alias h='helix'
alias v='vim'

# Case insentive completion for bash
bind 'set completion-ignore-case on'


# PS1
PS1='\[\e[1;34m\]$(if [ "$PWD" == "$HOME" ]; then echo -e "\[\e[0;90m\]~"; else echo -e "\[\e[0;90m\]\w"; fi)\n\[\e[m\]> '
