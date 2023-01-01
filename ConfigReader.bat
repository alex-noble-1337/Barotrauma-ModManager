:: ./backupConfigs.sh :: todo
:: idk if echo will work check it
@echo off
set barotrauma_dir=Masons Server
mkdir "Trusted Seas Server Tools/steamdir"
echo "Updating the following mods:"
"Trusted Seas Server Tools\grep\bin\grep.exe" -o -P "(?<=LocalMods\/)(.*?)(?=\/filelist\.xml)" "%barotrauma_dir%\config_player.xml" > "modlist.txt"
type "modlist.txt"
for /f "tokens=*" %%a in (modlist.txt) do (
  call "Trusted Seas Server Tools\ModDownloader.bat" %%a
)
echo "All queued Mods have been updated"
::del "modlist.txt"
::stuff that copies updated most from source to LocalMods goes here
::rmdir /s "Trusted Seas Server Tools/steamdir"
:: ./restoreConfigsFromBackup.sh :: todo
echo "Done updating mods!"
robocopy "Trusted Seas Server Tools\steamdir\steamapps\workshop\content\602960" "Masons Server\LocalMods" /S /MOVE /PURGE
rmdir /s /q "Trusted Seas Server Tools\steamdir"
echo Verifyed Mods