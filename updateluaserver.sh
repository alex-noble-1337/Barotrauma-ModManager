~/closeserver.sh
cd ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/
mkdir temp
cd temp
wget https://github.com/evilfactory/LuaCsForBarotrauma/releases/download/latest/barotrauma_lua_linux.zip
unzip -o barotrauma_lua_linux.zip
rm barotrauma_lua_linux.zip
rm serversettings.xml
rm -r Data
rm -r LocalMods
rm config_player.xml
chmod +x DedicatedServer\.exe
cd ..
cp -r temp/* ../Barotrauma\ Dedicated\ Server/
rm -r temp
