#!/bin/bash

echo "UPDATING MOD MANAGER"
wget -N https://github.com/Milord-ThatOneModder/Barotrauma-ModManager/releases/latest/download/ModManager.zip
unzip -qo ModManager.zip
pip install requests
echo -e "\n\n"
echo "RUNNING MOD MANAGER"
python3 ModManager/ModManager.py -s "steamcmd/steamcmd.sh" -t "ModManager"