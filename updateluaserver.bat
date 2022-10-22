:: ~/closeserver.sh
set yourserver=%1
cd %yourserver%
mkdir temp
cd temp
wget https://github.com/evilfactory/LuaCsForBarotrauma/releases/download/latest/luacsforbarotrauma_patch_windows_server.zip
tar -xf -o luacsforbarotrauma_build_linux.zip
del luacsforbarotrauma_build_linux.zip
del serversettings.xml
rmdir /s Data
rmdir /s LocalMods
del config_player.xml
cd ..
:: cp -r temp yourserver robocopy job
robocopy temp . /S /MOVE /PURGE