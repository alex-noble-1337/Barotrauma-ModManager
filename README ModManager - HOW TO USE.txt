Im not responsible for being an USER and breaking your computer ;) 
(although its unlikely if you follow my instructions, but if you are unsure about something messege me)

READ WHAT SCRIPT IS WRITTING IN THE CONSOLE ist probbably important ;)

for quick setup use download_script_exmple.sh in releases tab on github!
for configuring the collection mode type 'c' then press enter when prompted (on script start), then follow instructions given by the script
HOTBOOT (skiping mod download) is activated when typing no (or 'n') then press enter when prompted

command line options: (paths are set from your current working directory)
--barotraumapath or -b -path to your barotrauma install. Must be a path to THE FOLDER, not the program itself. Does not accept "" 
--steamcmdpath or -s - path to your steamcmd or steamcmd.exe. Must be a path to THE FOLDER, not the program itself (idk why i made it that way but im too lazy to change it).  Does not accept ""
--toolpath or -t - path to the ModManager.py Directory and where script can put all the "cashe" files. set it to as its specified in download_script_exmple.sh if you dont know where or what you are doing. Must be a path to THE FOLDER.  Does not accept ""
--collection or -c - OPTIONAL for advanced users, after giving the --collection or -c give it an steam collection link, and then path to localcopy of mods (eg. -c https://steamcommunity.com/sharedfiles/filedetails/?id=2952301361 LocalMods)
--performancefix or -p - OPTIONAL, if you want a script to add performance fix, at first start it will create optimal configuration

if barotraumapath is not given, script will assume the Present Working Directory
if toolpath is not given, script will assume ModManager in the Present Working Directory
if steamcmdpath is not given, script will assume steamcmd in the Present Working Directory

if you wanna use Present working directory for any of the paths use "pwd", or set defaults in ModManager (the values prefaced with default_) as "", and dont specify that command line option

Any other problems ask Milord#7860 or github or my mail (should be linked to github)
ASK BEFORE YOU DO IF YOU ARE UNSURE

Other things to mention:
escape any and all whitespaces in tool_dir and default_tool_dir
relative paths should work, but extreme caution is advised