# BarotraumaServerHelper
This scripts help you manage, and (soon) set up, your barotrauma server.

# README ModManager - HOW TO USE.txt
Im not responsible for being an USER and breaking your computer ;)

command line options:
--barotraumapath or -b - path to your barotrauma install. Must be a path to THE FOLDER, not the program itself. Does not accept "" 
--steamcmdpath or -s - path to your steamcmd or steamcmd.exe. Must be a path to THE FOLDER, not the program itself (idk why i made it that way but im too lazy to change it).  Does not accept ""
--toolpath or -t - path to the ModManager Directory where script can put all the "cashe" files. set it do default if you dont know where or what you are doing. Must be a path to THE FOLDER.  Does not accept ""

self explanatory - right?
if barotraumapath is not given, script will assume the Present Working Directory
if toolpath is not given, script will assume ModManager in the Present Working Directory
if steamcmdpath is not given, script will assume steamcmd in the Present Working Directory

if you wanna use Present working directory for any of the paths use pwd. cant use it as a keyword havent implemented it yet

Any other problems ask Milord#7860 or github or my mail (should be linked to github)
ASK BEFORE YOU DO IF YOU ARE UNSURE
READ WHAT SCRIPT IS WRITTING IN THE CONSOLE

Other things to mention:
escape any and all whitespaces in tool_dir and default_tool_dir
relative paths should work, but extreme caution is advised

configure progam by editing first two variables at the top of the ModManager.py file
HOTBOOT is in options
