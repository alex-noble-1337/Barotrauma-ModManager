@echo off
set number_of_mod=%1
:: rm -r -f ~/Steam/steamapps/workshop/content/602960/$number_of_mod
"Trusted Seas Server Tools\steamcmd.exe" +force_install_dir "steamdir" +login anonymous +workshop_download_item 602960 %number_of_mod% validate +quit
timeout 1