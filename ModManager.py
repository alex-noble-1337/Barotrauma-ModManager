#!/usr/bin/env python3

# CONFIGURATION if you dont wanna use arguments:
default_barotrauma_path = ""
default_tool_path = ""
default_steamcmd_path = "steamcmdwin" # steamcmd
addperformacefix = False
# TODO Still testing and working on it
default_lastupdated_functionality = False

# My "Quality" code
import os # TODO change this to import only individual commands
import shutil # TODO change this to import only individual commands
import re # TODO change this to import only individual commands
import time # TODO change this to import only individual commands
import datetime # for current time
import subprocess # TODO change this to import only individual commands
import sys # TODO change this to import only individual commands

from ConfigRecoder import get_modsnamelastupdated 
from configbackup import backup_option

# yoinked from stackoverflow, works
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

def get_filelist_str(barotrauma_path):
    # TODO make it in bracket with using f.open or smth, and error handling
    filelist_path = os.path.join(barotrauma_path, "config_player.xml")
    f = open(filelist_path, "r", encoding='utf8')
    filelist_str = f.read()
    f.close()
    pattern = "(?<=<regularpackages>)[\s\S]*?(?=<\/regularpackages>)"
    regularpackages = re.findall(pattern, filelist_str)[0]
    return regularpackages

def get_localcopy_path(filelist_str):
    pattern = "(?<=path=\")(.*?)(?=.\d*?\/filelist\.xml)"
    path = re.findall(pattern, filelist_str)[0]
    return path

# find mods to update from config_player.xml
def get_listOfModsfromConfig(filelist_str,localcopy_path):
    pattern = "(?<=<!--)[\s\S]*?(?=\/filelist\.xml)"
    modlist_str = re.findall(pattern, filelist_str)
    
    modlist = []
    for mod in modlist_str:
        pattern = "(?<=^)(.*?)(?=-->)"
        mod_name = re.findall(pattern, mod)[0]
        pattern = "(?<=" + localcopy_path + "\/)(\d*?)(?=$)"
        mod_id = re.findall(pattern, mod)
        if len(mod_id) > 0: 
            WorkshopItem = {'Name': mod_name, 'ID': mod_id[0]}
            modlist.append(WorkshopItem)
    return modlist

# function that uses steamcmd
def moddownloader(number_of_mod, tool_path, steamdir_path, steamcmd_path):
    if sys.platform == "win32":
        command = os.path.join(tool_path, steamcmd_path, "steamcmd.exe")
    else:
        command = os.path.join(steamcmd_path, "steamcmd")
        if (not os.path.exists(command)) and (not steamcmd_path == ""):
            command = os.path.join(steamcmd_path, "steamcmd.sh")
    arguments = [command ,"+force_install_dir \"" + steamdir_path + "\"", "+login anonymous", "+workshop_download_item 602960 " + str(number_of_mod), "validate", "+quit"]
    # TODO make its outpot less shit
    subprocess.call(arguments)
    time.sleep(1)

def main():
    # path handling
    if len(sys.argv) > 1:
        barotrauma_path = sys.argv[1]
        tool_path = sys.argv[2]
    else:
        # defaults EDIT THOSE
        barotrauma_path = default_barotrauma_path
        tool_path = default_tool_path
        lastupdated_functionality = default_lastupdated_functionality
        steamcmd_path = default_steamcmd_path


    steamdir_path = os.path.join(tool_path, "steamdir")
    if os.path.exists(steamdir_path):
        shutil.rmtree(steamdir_path)
    os.mkdir(steamdir_path)

    regularpackages = get_filelist_str(barotrauma_path)
    localcopy_path = get_localcopy_path(regularpackages)

    modlist = get_listOfModsfromConfig(regularpackages,localcopy_path)

    if not os.path.isabs(barotrauma_path):
        barotrauma_path = os.path.join(os.path.dirname(__file__), barotrauma_path)
    if not os.path.isabs(tool_path):
        tool_path = os.path.join(os.path.dirname(__file__), tool_path)
    if not os.path.isabs(steamcmd_path):
        steamcmd_path = os.path.join(os.path.dirname(__file__), steamcmd_path)
    if not os.path.isabs(steamdir_path):
        steamdir_path = os.path.join(os.path.dirname(__file__), steamdir_path)
        

    if os.path.isabs(localcopy_path):
        localmods_path = os.path.abspath(localcopy_path)
    else:
        localmods_path = os.path.join(default_barotrauma_path, localcopy_path)


    mods_b = []
    has_performancefix = False
    print("List of mods:")
    for mod in modlist:
        pattern = "\d*?"
        if re.match(pattern, mod["ID"]):
            if str(mod["ID"]) == "2701251094":
                has_performancefix = True
            print(str(mod["ID"]) + ": " + mod["Name"])
        mods_b.append(mod)
    print("\n")
    modlist = mods_b


    if not has_performancefix and addperformacefix == True:
        WorkshopItem = {'Name': "Performance Fix", 'ID': "2701251094"}
        modlist.insert(0, WorkshopItem)

    regularpackages_new = "\n"
    # print new
    for mod in modlist:
        regularpackages_new += "\t\t\t<!--" + mod['Name'] + "-->\n"
        regularpackages_new += "\t\t\t<package\n"
        regularpackages_new += "\t\t\t\tpath=\"" + localcopy_path + "/" +  mod['ID'] + "/filelist.xml\" />\n"

    filelist_path = os.path.join(barotrauma_path, "config_player.xml")
    # TODO make it in bracket with using f.open or smth, and error handling
    f = open(filelist_path, "r", encoding='utf8')
    filelist_str = f.read()
    f.close()
    filelist_str = filelist_str.replace(regularpackages, regularpackages_new)
    f = open(filelist_path, "w", encoding='utf8')
    f.write(filelist_str)
    f.close()

    if lastupdated_functionality:
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
    
    # main part running moddlownloader
    numberofupdatedmods = 0
    for mod in modlist:
        found = False
        # TODO lastupdated_functionality
        if lastupdated_functionality:
            if len(localupdatedates) > 0:
                for i in range(len(localupdatedates)):
                    if localupdatedates[i][0] == mod:
                        if time.strptime(localupdatedates[i][1],'%d %b, %Y @ %I:%M%p') < mod['LastUpdated']:
                            print("use mod downloader on " + mod)
                            # update localupdatedates
                            localupdatedates[i][1] = time.strptime(datetime.datetime.now(),'%d %b, %Y @ %I:%M%p')
                            found = True
                            break
        # main part running moddlownloader
        if (not lastupdated_functionality) and (found == False):
            print("Starting steamcmd, Updating mod:" + str(mod["ID"]) + ": " + mod["Name"])
            moddownloader(mod["ID"],tool_path, steamdir_path, steamcmd_path)
            print("\n")
            numberofupdatedmods += 1
            if lastupdated_functionality:
                # update localupdatedates
                localupdatedate = [mod, time.strptime(datetime.datetime.now(),'%d %b, %Y @ %I:%M%p')]
                localupdatedates.append(localupdatedate)   

        # TODO lastupdated_functionality
        if lastupdated_functionality:
            f = open(localupdatedates_path, "w", encoding='utf8')
            f.write()
            f.close()

    print("\nAll "+ str(numberofupdatedmods) +" Mods have been updated")
    print("Done updating mods!")

    newinputdir = os.path.join(barotrauma_path, "steamdir", "steamapps", "workshop", "content", "602960")
    # overwrite local copy with new copy downloaded above
    # removing for cleanup

    # base config
    baseconfig_path = os.path.join(tool_path, "BestDefaultConfigsTM")
    backup_option(baseconfig_path,newinputdir)

    if os.path.exists(localmods_path):
        # config_bringback
        backup_option(localmods_path,newinputdir)
        shutil.rmtree(localmods_path)
    os.mkdir(localmods_path)
    robocopysubsttute(newinputdir, localmods_path)
    shutil.rmtree(steamdir_path)
    print("Verifyed Mods!\n")

if __name__ == '__main__':
    print("\n")
    while(True):
        print("[ModManager] Do you want to update mods? ((Y)es / (n)o): ")
        newinput = input()
        if newinput.lower() == "yes" or newinput.lower() == "y":
            main()
            break
        elif newinput.lower() == "no" or newinput.lower() == "n":
            break
        print("Provide a valid anwser: \"y\" or \"yes\" / \"n\" or \"no\"")