echo -e "Installing requred stuff and opening ports"
sudo iptables -I INPUT 5 -p udp -m udp --sport 27000:27030 --dport 1025:65355 -j ACCEPT
sudo iptables -I INPUT 5 -p udp -m udp --sport 4380 --dport 1025:65355 -j ACCEPT
sudo add-apt-repository multiverse
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install lib32gcc-s1 screen crony

echo -e "Installing steamcmd"
rm -r ~/Steam
mkdir ~/Steam
cd ~/Steam
wget https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz
tar -xvzf steamcmd_linux.tar.gz
cd ..

echo -e "Now install barotrauma game by login yourusername \n then app_update 602960"
~/Steam/steamcmd.sh
echo -e "\nNow installing barotrauma server"
~/Steam/steamcmd.sh +login anonymous +app_update 1026340 verify +quit

rm ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/linux64/steamclient.so
ln -s ~/Steam/linux64/steamclient.so ~/Steam/steamapps/common/Barotrauma\ Dedicated\ Server/linux64/steamclient.so