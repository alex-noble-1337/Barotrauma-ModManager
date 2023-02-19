import os # TODO change this to import only individual commands
import shutil # TODO change this to import only individual commands
import re # TODO change this to import only individual commands
import time # TODO change this to import only individual commands
import datetime # for current time
import subprocess # TODO change this to import only individual commands

from ConfigRecoder import get_modsnamelastupdated 

def robocopysubsttute(root_src_dir, root_dst_dir):
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                # in case of the src and dst are the same file
                if os.path.samefile(src_file, dst_file):
                    continue
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)

def moddownloader(number_of_mod, tool_path):
    command = os.path.join(tool_path, "steamcmd.exe")
    arguments = [command ,"+force_install_dir \"steamdir\"", "+login anonymous", "+workshop_download_item 602960 " + str(number_of_mod), "validate", "+quit"]
    subprocess.call(arguments)
    time.sleep(1)

barotrauma_path = ""
tool_path = ""

steamdir_path = os.path.join(tool_path, "steamdir")
if os.path.exists(steamdir_path):
    shutil.rmtree(steamdir_path)
os.mkdir(steamdir_path)

# TODO make it in bracket with using f.open or smth, and error handling
filelist_path = os.path.join(barotrauma_path, "config_player.xml")
f = open(filelist_path, "r", encoding='utf8')
filelist_str = f.read()
f.close()

pattern = "(?<=LocalMods\/)(.*?)(?=\/filelist\.xml)"
modlist = re.findall(pattern, filelist_str)



print("List of mods:")
for mod in modlist:
    print(mod)

newtest = False

if newtest:
    # TODO fix this being so fucking slow
    modlist = get_modsnamelastupdated(modlist)

    localupdatedates = []
    localupdatedates_path = os.path.join(barotrauma_path, "localupdatedates.txt")
    if os.path.exists(localupdatedates_path):
        f = open(localupdatedates_path, "r", encoding='utf8')
        localupdatedates = f.readlines()
        f.close()
        # split to dict
        for i in range(len(localupdatedates)):
            localupdatedates[i] = localupdatedates[i].split(";")
    for mod in modlist:
        found = False
        if len(localupdatedates) > 0:
            for i in range(len(localupdatedates)):
                if localupdatedates[i][0] == mod:
                    if time.strptime(localupdatedates[i][1],'%d %b, %Y @ %I:%M%p') < mod['LastUpdated']:
                        print("use mod downloader on " + mod)
                        # update localupdatedates
                        localupdatedates[i][1] = time.strptime(datetime.datetime.now(),'%d %b, %Y @ %I:%M%p')
                        found = True
                        break
        if found == False:
            print("use mod downloader on " + mod['Name'])
            # update localupdatedates
            localupdatedate = [mod, time.strptime(datetime.datetime.now(),'%d %b, %Y @ %I:%M%p')]
            localupdatedates.append(localupdatedate)
                    

    f = open(localupdatedates_path, "w", encoding='utf8')
    f.write()
    f.close()
else:
    for mod in modlist:
        moddownloader(mod,tool_path)

print("All queued Mods have been updated")


print("Done updating mods!")

inputdir = os.path.join(barotrauma_path, "steamdir", "steamapps", "workshop", "content", "602960")
localmods_path = os.path.join(barotrauma_path, "LocalMods")
shutil.rmtree(localmods_path)
os.mkdir(localmods_path)
robocopysubsttute(inputdir, localmods_path)
shutil.rmtree(steamdir_path)
print("Verifyed Mods")