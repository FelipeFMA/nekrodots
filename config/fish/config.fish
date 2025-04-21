if status is-interactive
    # Commands to run in interactive sessions can go here
    set fish_greeting
    sh -c echo
    sh -c 'fastfetch -l small'
    sh -c echo
    sh -c /home/felipe/Documents/Github/ISORememberer/rememberer.sh
end

fish_add_path /home/felipe/.spicetify
