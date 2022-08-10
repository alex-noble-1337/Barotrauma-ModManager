#!/bin/bash
# cp all configs from backup
echo "Restoring base game configs..."
cp ServerConfigs/serversettings.xml ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/.
cp ServerConfigs/config_player.xml ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/.
cp -r ServerConfigs/Data ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/.
# mod's configs
# performance fix
echo "Restoring Performance fix configs..."
cp ServerConfigs/2701251094/config.json ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/LocalMods/2701251094/.
echo "Done!"