uptime; ps -axo pid,pcpu,etime,command | grep -E "run62|python|Python" | grep -v grep | cut -c1-200 | head -30; pmset -g therm 2>/dev/null | head; 
