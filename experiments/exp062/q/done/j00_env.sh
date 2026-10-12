echo "host $(hostname) $(date)"; sysctl -n hw.ncpu; $PY -c "import kaggle_environments as k;print(k.__version__)"; kaggle --version; kaggle config view | grep -i user; df -h . | tail -1
