function avavelar-tunnel --wraps='ssh -p 443 -D 1080 -fN felipe@204.216.164.72' --description 'alias avavelar-tunnel=ssh -p 443 -D 1080 -fN felipe@204.216.164.72'
  ssh -p 443 -D 1080 -fN felipe@204.216.164.72 $argv
        
end
