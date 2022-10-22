#!/bin/batch
set number_of_mod=%1
:: rm -r -f ~/Steam/steamapps/workshop/content/602960/$number_of_mod
steamcmd.exe +login anonymous +workshop_download_item 602960 %number_of_mod +quit
sleep 1
echo -e "\n\n"
