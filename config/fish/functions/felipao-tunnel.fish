function felipao-tunnel --wraps='ssh -D 1080 -p 443 -fN felipe@134.65.28.106' --description 'alias felipao-tunnel=ssh -D 1080 -p 443 -fN felipe@134.65.28.106'
  ssh -D 1080 -p 443 -fN felipe@134.65.28.106 $argv
        
end
