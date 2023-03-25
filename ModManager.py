#!/usr/bin/env python3

# CONFIGURATION if you dont wanna use arguments:
default_barotrauma_path = ""
default_tool_path = ""
default_steamcmd_path = "steamcmd"
addperformacefix = False
# TODO Still testing and working on it
default_lastupdated_functionality = False
flush_previous_col = False


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
from ConfigRecoder import generatelistOfMods 

# yoinked from stackoverflow, works
def robocopysubsttute(root_src_dir, root_dst_dir, replace_option = True):
    if replace_option:
        number_dirs = os.listdir(root_dst_dir)
        for number_dir in number_dirs:
            pattern = "^\d*?$"
            if re.match(pattern, number_dir):
                if os.path.exists(os.path.join(root_dst_dir, number_dir)):
                    shutil.rmtree(os.path.join(root_dst_dir, number_dir))
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
    # TODO error handling
    filelist_path = os.path.join(barotrauma_path, "config_player.xml")
    with open(filelist_path, "r", encoding='utf8') as f:
        filelist_str = f.read()
  
    pattern = "(?<=<regularpackages>)[\s\S]*?(?=<\/regularpackages>)"
    regularpackages = re.findall(pattern, filelist_str)
    if len(regularpackages) > 0:
        return regularpackages[0]
    else:
        # patch for </regularpackages>, just in case
        # TODO a bit stupid, so rework it
        with open(filelist_path, "r", encoding='utf8') as f:
            filelist_str = f.read()
        print("<regularpackages/>")
        print("<regularpackages>\n\t\t</regularpackages>")
        filelist_str = filelist_str.replace("<regularpackages/>", "<regularpackages>\n\n\t</regularpackages>")
        with open(filelist_path, "w", encoding='utf8') as f:
            f.write(filelist_str)

        pattern = "(?<=<regularpackages>)[\s\S]*?(?=<\/regularpackages>)"
        regularpackages = re.findall(pattern, filelist_str)[0]
        return regularpackages

def get_localcopy_path(filelist_str):
    pattern = "(?<=path=\")(.*?)(?=\/filelist\.xml)"
    path = re.findall(pattern, filelist_str)
    if len(path) > 0:
        path = path[0].split("/")
        new_path = ""
        for i in range(len(path)-2):
            if sys.platform == "win32":
                new_path += path[i] + "/"
            else:
                new_path += path[i] + "/"
        new_path += path[len(path)-2]
        return new_path
    else:
        return ""

# find mods to update from config_player.xml
def get_listOfModsfromConfig(filelist_str,localcopy_path):
    # filelist.xml" />
    pattern = "(?<=<!--)[\s\S]*?(?=\/filelist\.xml)"
    modlist_str = re.findall(pattern, filelist_str)
    
    modlist = []
    for mod in modlist_str:
        pattern = "(?<=^)(.*?)(?=-->)"
        mod_name = re.findall(pattern, mod)[0]
        pattern = '(?<=path=")(.*?)(?=$)'
        mod_id = re.findall(pattern, mod)[0]
        if sys.platform == "win32":
            mod_id = mod_id.replace('/', '\\')
        mod_id = mod_id.replace(localcopy_path + "/", "")
        WorkshopItem = {'Name': mod_name, 'ID': mod_id}
        modlist.append(WorkshopItem)
    return modlist

# function that uses steamcmd
def moddownloader(number_of_mod, tool_path, steamdir_path, steamcmd_path):
    pattern = "^\d*?$"
    if re.match(pattern, number_of_mod):
        if sys.platform == "win32":
            command = os.path.join(steamcmd_path, "steamcmd.exe")
        else:
            # command = os.path.join(steamcmd_path, "steamcmd")
            # if (not os.path.exists(command)) and (not steamcmd_path == ""):
            #     command = os.path.join(steamcmd_path, "steamcmd.sh")

            command = "steamcmd"
        arguments = [command ,"+force_install_dir \"" + steamdir_path + "\"", "+login anonymous", "+workshop_download_item 602960 " + str(number_of_mod), "validate", "+quit"]
        # TODO make its outpot less shit
        subprocess.call(arguments)
        time.sleep(1)
        return 0

def remove_duplicates(modlist):
    toremove = []
    modlist_copy = modlist
    modlist_copy = sorted(modlist_copy, key=lambda mod: mod["ID"])
    for i in range(1, len(modlist_copy)):
        if modlist_copy[i]["ID"] == modlist_copy[i-1]["ID"]:
            toremove.append(modlist_copy[i])    
    modlist.reverse()
    for remove in toremove:
        if remove in modlist:
            modlist.remove(remove)
    modlist.reverse()
    return modlist

def main(collection_link = "", localmods_path_colop = ""):
    # path handling

    options_arr = sys.argv[1:]
    changed_barotrauma_path = False
    changed_tool_path = False
    changed_steamcmd_path = False
    collectionmode = False

    # TODO go over this again, handing of command line arguments
    if len(options_arr) > 1:
        for i in range(0,len(options_arr)):
            tempval = len(options_arr[i:i+1]) + 1

            # --barotraumapath or -b - path to your barotrauma install. Must be a path to THE FOLDER, not the program itself. Does not accept ""
            if options_arr[i] == '--barotraumapath' or options_arr[i] == '-b':
                if tempval > 1:
                    if options_arr[i+1] == "pwd":
                        barotrauma_path = os.getcwd()
                        changed_barotrauma_path = True
                    else:
                        barotrauma_path = options_arr[i+1]
                        changed_barotrauma_path = True
                else:
                    barotrauma_path = os.getcwd()
                    changed_barotrauma_path = True
            
            # --toolpath or -t - path to the ModManager Direcotry where script can put all the "cashe" files. set it do default if you dont know where or what you are doing. Must be a path to THE FOLDER.  Does not accept ""
            if options_arr[i] == '--toolpath' or options_arr[i] == '-t':
                if tempval > 1:
                    if options_arr[i+1] == "pwd":
                        tool_path = os.getcwd()
                        changed_tool_path = True
                    else:
                        tool_path = options_arr[i+1]
                        changed_tool_path = True
                else:
                    tool_path = os.getcwd()
                    changed_tool_path = True

            # --steamcmdpath or -s - path to your steamcmd or steamcmd.exe. Must be a path to THE FOLDER, not the program itself.  Does not accept ""
            if options_arr[i] == '--steamcmdpath' or options_arr[i] == '-s':
                if tempval > 1:
                    if options_arr[i+1] == "pwd":
                        steamcmd_path = os.getcwd()
                        changed_steamcmd_path = True
                    else:
                        steamcmd_path = options_arr[i+1]
                        changed_steamcmd_path = True
                else:
                    steamcmd_path = options_arr[i+1]
                    changed_steamcmd_path = True

            # TODO add it to the documentaton
            # TODO make it so you can input those values from command line
            if options_arr[i] == '--collection' or options_arr[i] == '-c':
                # TODO idk if it works test later
                if tempval > 1:
                    # TODO check if link is good
                    url_of_steam_collection = options_arr[i+1]
                    collectionmode = True
                    localcopy_path_og = options_arr[i+2]

    if not changed_barotrauma_path:
        barotrauma_path = default_barotrauma_path
    if not changed_tool_path:
        tool_path = default_tool_path
    if not changed_steamcmd_path:
        steamcmd_path = default_steamcmd_path

    lastupdated_functionality = default_lastupdated_functionality

    steamdir_path = os.path.join(tool_path, "steamdir")
    if os.path.exists(steamdir_path):
        shutil.rmtree(steamdir_path)
    os.mkdir(steamdir_path)

    if not os.path.isabs(barotrauma_path):
        barotrauma_path = os.path.join(os.getcwd(), barotrauma_path)


    regularpackages = get_filelist_str(barotrauma_path)

    # TODO remove all previous mods, that arent used, from directory
    # we first need to get all managed mods
    old_managed_mods = ""
    managed_mods_path = os.path.join(tool_path, "managed_mods.txt")

    if os.path.exists(managed_mods_path):
        with open(managed_mods_path, "r", encoding='utf8') as f:
            old_managed_mods = f.read()

    # this will be paths to managed mods
    old_managed_mods = old_managed_mods.split('\n')
    if '' in old_managed_mods:
        old_managed_mods.remove('')

    # collection save file
    collection_file_path = os.path.join(tool_path, "collection_save.txt")

    collection_file = ""
    if flush_previous_col:
        if os.path.exists(collection_file_path):
            os.remove(collection_file_path)
        collectionmode = False
    else:
        if os.path.exists(collection_file_path):
            with open(collection_file_path, "r", encoding='utf8') as f:
                collection_file = f.read()
            arr = collection_file.split(" ")
            url_of_steam_collection = arr[0]
            localcopy_path_og = arr[1]
            collectionmode = True

    if collection_link != "" and localmods_path_colop != "":
        url_of_steam_collection = collection_link
        localcopy_path_og = localmods_path_colop
        collectionmode = True

    if collectionmode == False:
        localcopy_path_og = get_localcopy_path(regularpackages)
        modlist = get_listOfModsfromConfig(regularpackages,localcopy_path_og)
    else:
        print("[ModManager]Collection mode enabled, Downloading collection data (This might take a sec)")
        modlist = generatelistOfMods(url_of_steam_collection)
        with open(collection_file_path, "w", encoding='utf8') as f:
            f.write(url_of_steam_collection + " " + localcopy_path_og)

    localcopy_path = localcopy_path_og


    # modless?
    if len(modlist) == 0:
        print("[ModManager]No mods detected")
        return 

    if not os.path.isabs(tool_path):
        tool_path = os.path.join(os.getcwd(), tool_path)
    if not os.path.isabs(steamcmd_path):
        steamcmd_path = os.path.join(os.getcwd(), steamcmd_path)
    if not os.path.isabs(steamdir_path):
        steamdir_path = os.path.join(os.getcwd(), steamdir_path)
        

    # if os.path.isabs(localcopy_path):
    #     localmods_path = os.path.abspath(localcopy_path)
    # else:
    #     localmods_path = os.path.join(default_barotrauma_path, localcopy_path)

    if not os.path.isabs(localcopy_path):
        localcopy_path = os.path.join(os.getcwd(), localcopy_path)

    managed_mods = []
    for mod in modlist:
        managed_mods.append(os.path.join(localcopy_path_og, mod['ID']))

    not_managedmods = old_managed_mods
    # remove modwithdir
    for modwithdir in managed_mods:
        if modwithdir in not_managedmods:
            not_managedmods.remove(modwithdir)

    modlist = remove_duplicates(modlist)


    has_performancefix = False
    print("[ModManager]List of mods:")
    for mod in modlist:
        if str(mod["ID"]) == "2701251094":
            has_performancefix = True
        print(str(mod["ID"]) + ": " + mod["Name"])
    print("\n")

    if not has_performancefix and addperformacefix == True:
        WorkshopItem = {'Name': "Performance Fix", 'ID': "2701251094"}
        modlist.insert(0, WorkshopItem)

    regularpackages_new = "\n"
    # print new
    for mod in modlist:
        #  if barotrauma_path is inside of 
        temp_localcopy_path = localcopy_path_og
        if temp_localcopy_path.count(barotrauma_path) > 0:
            temp_localcopy_path = temp_localcopy_path.replace(barotrauma_path, "")

        if sys.platform == "win32":
            temp_localcopy_path = temp_localcopy_path.replace("\\", "/")
        else:
            temp_localcopy_path = temp_localcopy_path

        regularpackages_new += "\t\t\t<!--" + mod['Name'] + "-->\n"
        regularpackages_new += "\t\t\t<package\n"
        regularpackages_new += "\t\t\t\tpath=\"" + temp_localcopy_path + "/" + mod['ID'] + "/filelist.xml\" />\n"

    filelist_path = os.path.join(barotrauma_path, "config_player.xml")
    # TODO make it in bracket with using f.open or smth, and error handling
    with open(filelist_path, "r", encoding='utf8') as f:
        filelist_str = f.read()
    filelist_str = filelist_str.replace(regularpackages, regularpackages_new)
    with open(filelist_path, "w", encoding='utf8') as f:
        f.write(filelist_str)

    managed_mods_str = ""
    for managed_mod in managed_mods:
        managed_mods_str += managed_mod + "\n"
    with open(managed_mods_path, "w", encoding='utf8') as f:
        f.write(managed_mods_str)

    if lastupdated_functionality:
        # TODO fix this being so fucking slow
        modlist = get_modsnamelastupdated(modlist)

        localupdatedates = []
        localupdatedates_path = os.path.join(barotrauma_path, "localupdatedates.txt")
        if os.path.exists(localupdatedates_path):
            with open(localupdatedates_path, "r", encoding='utf8') as f:
                localupdatedates = f.readlines()
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
                            print("[ModManager]useing mod downloader on " + mod)
                            # update localupdatedates
                            localupdatedates[i][1] = time.strptime(datetime.datetime.now(),'%d %b, %Y @ %I:%M%p')
                            found = True
                            break
        # main part running moddlownloader
        if (not lastupdated_functionality) and (found == False):
            print("[ModManager]Starting steamcmd, Updating mod:" + str(mod["ID"]) + ": " + mod["Name"])
            # TODO make output of steamcmd less spammy/silent
            # TODO instead of steamcmd downloading one mod at the time, make it download all of them in one start of steamcmd using steamcmd scripts or cmd line arguments
            output = moddownloader(mod["ID"],tool_path, steamdir_path, steamcmd_path)
            print("\n")
            if output == 0:
                numberofupdatedmods += 1
            if lastupdated_functionality:
                # update localupdatedates
                localupdatedate = [mod, time.strptime(datetime.datetime.now(),'%d %b, %Y @ %I:%M%p')]
                localupdatedates.append(localupdatedate)   

        # TODO lastupdated_functionality
        if lastupdated_functionality:
            with open(localupdatedates_path, "w", encoding='utf8') as f:
                f.write()

    print("\n[ModManager]All "+ str(numberofupdatedmods) +" Mods have been updated")
    print("[ModManager]Downloading mods complete!")

    newinputdir = os.path.join(steamdir_path, "steamapps", "workshop", "content", "602960")
    # overwrite local copy with new copy downloaded above
    # removing for cleanup

    # base config
    baseconfig_path = os.path.join(tool_path, "BestDefaultConfigsTM")
    backup_option(baseconfig_path,newinputdir)


    backup_option(localcopy_path,newinputdir)

    # remove not_managedmods
    print("[ModManager]Removing " + str(len(not_managedmods)) + " not managed now mods!")
    for not_managedmod in not_managedmods:
        if os.path.exists(not_managedmod):
            shutil.rmtree(not_managedmod)

    robocopysubsttute(newinputdir, localcopy_path)
    shutil.rmtree(steamdir_path)
    print("[ModManager]Verifyed Mods!\n")

if __name__ == '__main__':
    print("\n")
    while(True):
        print("[ModManager]If you want to set up, or disable collection mode type \'c\', then enter.\n[ModManager]Do you want to update mods? ((Y)es / (n)o): ")
        newinput = input()
        if newinput.lower() == "yes" or newinput.lower() == "y":
            main()
            break
        elif newinput.lower() == "no" or newinput.lower() == "n":
            break
        elif newinput.lower() == "collection" or newinput.lower() == "c":
            print("[ModManager]Provide an collection link then press enter, or if you want to disable previously enabled collection mode, type 'n' then enter: ")
            op_collection_url = input()
            if op_collection_url.lower() != "n":
                print("[ModManager]Provide an localcopy path (if you dont know what to input, type 'LocalMods') then press enter: ")
                op_localcopy_path = input()
            else:
                op_collection_url = ""
                op_localcopy_path = ""
                flush_previous_col = True
            # TODO collection check, if link is valid
            main(op_collection_url, op_localcopy_path)
            break
        elif newinput.lower() == "kill":
            break
        print("[ModManager]Provide a valid anwser: \"y\" or \"yes\" / \"n\" or \"no\"")