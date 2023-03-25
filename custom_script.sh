#!/bin/bash

echo -e "\n\n"
echo "RUNNING MOD MANAGER"
pip install requests

wget https://github.com/Milord-ThatOneModder/BarotraumaServerHelper/releases/latest/download/ModManager.zip
unzip -qo ModManager.zip

python3 ModManager/ModManager.py