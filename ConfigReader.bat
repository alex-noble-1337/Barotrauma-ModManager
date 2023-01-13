:: ./backupConfigs.sh :: todo
:: idk if echo will work check it
@echo off
set barotrauma_dir=Masons Server
set tool_dir=Trusted Seas Server Tools
mkdir "%tool_dir%/steamdir"
echo "Updating the following mods:"
"%tool_dir%\grep\bin\grep.exe" -o -P "(?<=LocalMods\/)(.*?)(?=\/filelist\.xml)" "%barotrauma_dir%\config_player.xml" > "modlist.txt"
type "modlist.txt"
for /f "tokens=*" %%a in (modlist.txt) do (
  call "%tool_dir%\ModDownloader.bat" %%a
)
echo "All queued Mods have been updated"
::del "modlist.txt"
::stuff that copies updated most from source to LocalMods goes here
::rmdir /s "%tool_dir%/steamdir"
:: ./restoreConfigsFromBackup.sh :: todo
echo "Done updating mods!"
robocopy "%tool_dir%\steamdir\steamapps\workshop\content\602960" "%barotrauma_dir%\LocalMods" /S /MOVE /PURGE
rmdir /s /q "%tool_dir%\steamdir"
echo Verifyed Mods