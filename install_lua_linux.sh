#!/bin/bash
# server patch
wget -N https://github.com/evilfactory/LuaCsForBarotrauma/releases/download/latest/luacsforbarotrauma_patch_linux_server.zip -O luacsforbarotrauma_patch_server.zip
unzip -o luacsforbarotrauma_patch_server.zip
# client side lua
wget -N https://github.com/evilfactory/LuaCsForBarotrauma/releases/download/latest/luacsforbarotrauma_patch_linux_client.zip -O luacsforbarotrauma_patch_client.zip
unzip -o luacsforbarotrauma_patch_client.zip