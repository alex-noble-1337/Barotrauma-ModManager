#!/bin/bash
./backupConfigs.sh
echo -e "\nUpdating following mods:"
grep -oP '(?<=LocalMods\/)(.*?)(?=\/filelist\.xml)' ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/config_player.xml > bufferscript
cat bufferscript
echo -e "\n"
sed -i "s/^/.\/updateservermod_one.sh /" bufferscript
chmod +x bufferscript
./bufferscript
echo "All queued Mods have been updated"
rm bufferscript
./restoreConfigsFromBackup.sh
echo "Done updating mods!"
