:: ./backupConfigs.sh :: todo
:: idk if echo will work check it
set barotrauma_dir=%1
echo "Updating following mods:"
"bin\grep.exe" -o -P "(?<=LocalMods\/)(.*?)(?=\/filelist\.xml)" barotrauma_dir\config_player.xml > bufferscript
type bufferscript
echo ""
mkdir "steamdir"
for /f "tokens=*" %%a in (bufferscript) do (
  "C:\Users\Mason\Desktop\Masons Server\updateservermod_one.bat" %%a
)
pause
echo ""
echo ""
echo "All queued Mods have been updated"
del bufferscript
::stuff that copies updated most from source to LocalMods goes here
::rmdir /s "steamdir"
:: ./restoreConfigsFromBackup.sh :: todo
echo "Done updating mods!"