#!/bin/zsh
./start_luigi_daemon.sh
python3 experiments.py --random-seed=42 --total-number-of-runs=100 --workers=64
