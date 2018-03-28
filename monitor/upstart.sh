#!/usr/bin/env bash
clear
rm -rf logs/*.log
python3 controller.py
rm -rf run/__pycache__/
rm -rf wrapper/__pycache__/
