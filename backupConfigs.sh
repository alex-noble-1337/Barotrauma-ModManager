#!/bin/bash
# remove previous previous changes
# mv previous configs to previous previous configs
# cp configs to previous configs
echo "Backing up base game configs..."
rm -r .backupServerConfigs
mkdir .backupServerConfigs
cp -r ServerConfigs/* .backupServerConfigs/.
rm -r ServerConfigs/*
cp ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/serversettings.xml ServerConfigs/.
cp ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/config_player.xml ServerConfigs/.
cp -r ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/Data ServerConfigs/.
# mod's configs
echo "Backing up PerformanceFix config..."
mkdir ServerConfigs/2701251094
cp ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/LocalMods/2701251094/config.json ServerConfigs/2701251094/.
echo "Done!"