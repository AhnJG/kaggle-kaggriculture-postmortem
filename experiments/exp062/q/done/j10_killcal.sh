# Claude(B): stop my calibration run to avoid competing with the S1 screen
pkill -f "run62.py experiments/exp062/jobs-cal.json"; sleep 2; pgrep -fl run62.py | head
