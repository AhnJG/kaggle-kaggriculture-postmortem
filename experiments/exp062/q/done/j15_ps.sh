date; uptime; ps -axo pid,pcpu,etime,command | grep -E "run62|kaggle" | grep -v grep | cut -c1-160 | head -20; pmset -g batt | head -3
