#!/bin/bash

echo "UPDATING MOD MANAGER"
wget https://github.com/Milord-ThatOneModder/Barotrauma-ModManager/releases/latest/download/ModManager.zip
unzip -qo ModManager.zip
echo -e "\n\n"
echo "RUNNING MOD MANAGER"
pip install requests
python3 ModManager/ModManager.py -s "steamcmd" -t "ModManager"