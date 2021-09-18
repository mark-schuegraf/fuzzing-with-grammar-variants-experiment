#!/bin/zsh
./start_luigi_daemon.sh
time python3 experiments.py --random-seed=42 --total-number-of-runs=100 --workers=64 2>&1 | tee luigi.log
