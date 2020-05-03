#!/bin/bash

script_path=~/TeamWork/fill_db.py
crontab -l > mycron

echo "00 06 * * * python3.8" $script_path >> mycron
echo "00 16 * * * python3.8" $script_path >> mycron

crontab mycron
rm mycron
