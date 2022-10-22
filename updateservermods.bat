#!/bin/batch
:: ./backupConfigs.sh :: todo
:: idk if echo will work check it
echo "Updating following mods:"
bin\grep.exe -o -P "(?<=LocalMods\/)(.*?)(?=\/filelist\.xml)" config_player.xml > bufferscript
type bufferscript
echo ""
@echo off
for /f "tokens=*" %%a in (bufferscript.txt) do (
  updateservermod_one.bat  %%a
)
pause
echo ""
echo ""
echo "All queued Mods have been updated"
delete bufferscript
:: ./restoreConfigsFromBackup.sh :: todo
echo "Done updating mods!"