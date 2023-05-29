#!/usr/bin/env python3

# CONFIGURATION if you dont wanna use arguments:
default_barotrauma_path = ""
default_tool_path = ""
default_steamcmd_path = "steamcmd"
default_steamdir_path = "/home/milord/testdirectory/steamdir"
addperformacefix = False
disablewarnings = False
# TODO Still testing and working on it
flush_previous_col = False
progressbar_functionality = False
debug_set_forced_cs = False
debug_dependencies_functionality = False

# My "Quality" code
import os # TODO change this to import only individual commands
import shutil # TODO change this to import only individual commands
import re # TODO change this to import only individual commands
import time # TODO change this to import only individual commands
import datetime # for current time
import subprocess # TODO change this to import only individual commands
import sys # TODO change this to import only individual commands
import io

import xml.etree.ElementTree as ET


# from ConfigRecoder import get_modsnamelastupdated 
from configbackup import backup_option
from ConfigRecoder import generatelistOfMods 
from ConfigRecoder import collectionf
from ConfigRecoder import get_modsData_individual
from configbackup import backupBarotraumaData

# dirty hack but who knows what causes this issue now :barodev: <- probbabbly them
def HOTFIX_steamcmdCRLF(steamdir_path: str, modlist):
    # find all xml files
    WINDOWS_LINE_ENDING = b'\r\n'
    UNIX_LINE_ENDING = b'\n'

    # all_xml_files = []
    for src_dir, dirs, files in os.walk(steamdir_path):
        for file_ in files:
            if file_[-4:] == ".xml":
                # all_xml_files.append()
                file_path = os.path.join(src_dir, file_)
                with open(file_path, 'rb') as open_file:
                    content = open_file.read()

                if sys.platform == 'win32':
                    # Unix ➡ Windows
                    content = content.replace(UNIX_LINE_ENDING, WINDOWS_LINE_ENDING)
                else:
                    # Windows ➡ Unix
                    content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

                with open(file_path, 'wb') as open_file:
                    open_file.write(content)

    for mod in modlist:
        filelist_path = os.path.join(steamdir_path, mod['ID'], "filelist.xml")
        if os.path.exists(filelist_path):
            with open(filelist_path, 'r') as open_file:
                filelist_str = open_file.read()

            element = ET.fromstring(filelist_str)
            if element.tag.lower() == "contentpackage":
                if element.attrib['name'] != mod['name']:
                    oldname = element.attrib['name']
                    element.attrib['name'] = mod['name']
                    # TODO make an escape invalid xml of old names
                    element.attrib['altnames'] = oldname

                    # why?
                    desired_order_list = ['name', 'steamworkshopid', 'corepackage', 'modversion', 'gameversion', 'installtime', 'altnames', 'expectedhash']
                    # workaround for bottom one
                    for desired_order_element in desired_order_list:
                        if desired_order_element not in element.attrib:
                            if 'installtime' == desired_order_element:
                                element.attrib['installtime'] = str(round(time.time()))
                            elif 'steamworkshopid' == desired_order_element:
                                element.attrib['steamworkshopid'] = mod['ID']
                            else:
                                element.attrib[desired_order_element] = ""
                    # i dont understand it, this is shit
                    # TOO BAD!
                    element.attrib = {k: element.attrib[k] for k in desired_order_list}

                    filelist_str = ET.tostring(element, encoding='utf-8', method='xml')


                    with open(filelist_path, 'wb') as open_file:
                        open_file.write(filelist_str)


# set up all default values and paths
# TODO rework
def set_required_values():
    options_arr = sys.argv[1:]

    changed_barotrauma_path = False
    changed_tool_path = False
    changed_steamcmd_path = False
    collectionmode = False
    save_dir = ""
    max_saves = ""

    # TODO go over this again, handing of command line arguments
    if len(options_arr) >= 1:
        for i in range(0,len(options_arr)):
            tempval = 1
            for j in range(i + 1,len(options_arr)):
                if options_arr[j] == '--barotraumapath' or options_arr[j] == '-b' or options_arr[j] == '--toolpath' or options_arr[j] == '-t' or options_arr[j] == '--steamcmdpath' or options_arr[j] == '-s' or options_arr[j] == '--collection' or options_arr[j] == '-c' or options_arr[j] == '--performancefix' or options_arr[j] == '-p' or options_arr[j] == '--backup':
                    break
                else:
                    tempval += 1


            # --barotraumapath or -b - path to your barotrauma install. Must be a path to THE FOLDER, not the program itself. Does not accept ""
            if options_arr[i] == '--barotraumapath' or options_arr[i] == '-b':
                if tempval >= 2:
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
                if tempval >= 2:
                    if options_arr[i+1] == ".":
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
                if tempval >= 2:
                    if options_arr[i+1] == "pwd":
                        if sys.platform == 'win32':
                            location_with_steamcmd = os.path.join(os.getcwd(), "steamcmd.exe")
                        else:
                            location_with_steamcmd = os.path.join(os.getcwd(), "steamcmd.sh")
                        changed_steamcmd_path = True
                    else:
                        location_with_steamcmd = options_arr[i+1]
                        changed_steamcmd_path = True
                else:
                    location_with_steamcmd = options_arr[i+1]
                    changed_steamcmd_path = True

            # TODO '--collection to the documentaton
            if options_arr[i] == '--collection' or options_arr[i] == '-c':
                if tempval >= 3:
                    # TODO check if link is good
                    collection_link = options_arr[i+1]
                    collectionmode = True
                    localcopy_path_override = options_arr[i+2]
                
             # TODO add it to the documentaton
            if options_arr[i] == '--performancefix' or options_arr[i] == '-p':
                if tempval >= 1:
                    global addperformacefix
                    addperformacefix = True

            # TODO add it to the documentaton
            if options_arr[i] == '--backup':
                if tempval >= 3:
                    # TODO check if link is good
                    max_saves = options_arr[i+1]
                    save_dir = options_arr[i+2]

    # setting up default values and path handling
    if not changed_barotrauma_path:
        barotrauma_path = default_barotrauma_path
    if not os.path.isabs(barotrauma_path):
        barotrauma_path = os.path.join(os.getcwd(), barotrauma_path)
    if not changed_tool_path:
        tool_path = default_tool_path
    if not changed_steamcmd_path:
        location_with_steamcmd = default_steamcmd_path
    if default_steamdir_path == "":
        steamdir_path = os.path.join(tool_path, "steamdir")
    else:
        steamdir_path = default_steamdir_path
    
    input_options = {'barotrauma': barotrauma_path, 'tool': tool_path, 'steamcmd': location_with_steamcmd, 'steamdir': steamdir_path, 'save_dir': save_dir, 'max_saves': max_saves}
    return input_options

# yoinked from stackoverflow, works
def robocopysubsttute(root_src_dir, root_dst_dir, replace_option = False):
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

def get_config_player_str(barotrauma_path):
    try:
        config_player_path = os.path.join(barotrauma_path, "config_player.xml")
        with open(config_player_path, "r", encoding='utf8') as f:
            config_player_str = f.read()
    except Exception as e:
        print("[ModManager] Could not find the config_player.xml! Check your barotrauma path!")
        print("[ModManager] Barotrauma path: " + config_player_path)
        print(e)
    return config_player_str 

# config player IO
def get_mods_config_player(barotrauma_path):
    config_player_str = get_config_player_str(barotrauma_path) 

    root = ET.fromstring(config_player_str)
    modpaths = []
    for element in root:
        subelements = list(element)
        if len(subelements) > 0:
            for subelement in subelements:
                if subelement.tag == 'regularpackages':
                    subsubelements = list(subelement)
                    if len(subsubelements) > 0:
                        for subsubelement in subsubelements:
                            # just in case
                            if subsubelement.tag == "package":
                                mod = {'path': subsubelement.attrib['path']}
                                mod['ID'] = os.path.basename(os.path.dirname(mod['path']))
                                modpaths.append(mod)
    return modpaths

def set_mods_config_player(modlist, localcopy_path, barotrauma_path):
    config_player_str = get_config_player_str(barotrauma_path) 

    root = ET.fromstring(config_player_str)
    modpaths = []
    for element in root:
        for subelement in element:
            if subelement.tag == 'regularpackages':
                # remove all mods (subelements)
                for subsubelement in subelement:
                    subelement.remove(subsubelement)
                # add them according to the modlist
                for mod in modlist:
                    new_package = ET.SubElement(subelement, 'package')
                    new_package.attrib['path'] = localcopy_path + "/" + mod['ID'] + "/filelist.xml"
                    new_package.tail = '\n      \n      '
                    new_package.text = None
                    
    config_player_str = ET.tostring(root, encoding='utf-8', method='xml')

    with open(os.path.join(barotrauma_path, "config_player.xml"), 'wb') as open_file:
        open_file.write(config_player_str)

# get from config_player.xml, everything inside <regularpackages/> </regularpackages>
def get_regularpackages(barotrauma_path):
    # trying to access filelist
    try:
        filelist_path = os.path.join(barotrauma_path, "config_player.xml")
        with open(filelist_path, "r", encoding='utf8') as f:
            filelist_str = f.read()
    except Exception as e:
        print("[ModManager] Could not find the config_player.xml! Check your barotrauma path!")
        print("[ModManager] Barotrauma path: " + filelist_path)
        print(e)

    pattern = "<regularpackages>[\s\S]*?<\/regularpackages>"
    regularpackages = re.findall(pattern, filelist_str)

    if len(regularpackages) <= 0:
        # patch for </regularpackages>, just in case
        # TODO a bit stupid, so rework it
        # print("<regularpackages/>")
        # print("<regularpackages>\n\t\t</regularpackages>")
        filelist_str = filelist_str.replace("<regularpackages/>", "<regularpackages>\n\n\t</regularpackages>")
        filelist_str = filelist_str.replace("<regularpackages />", "<regularpackages>\n\n\t</regularpackages>")
        with open(filelist_path, "w", encoding='utf8') as f:
            f.write(filelist_str)
        pattern = "(?<=<regularpackages>)[\s\S]*?(?=<\/regularpackages>)"
        regularpackages = re.findall(pattern, filelist_str)
        
    if len(regularpackages) > 0:
        return regularpackages[0]
    else:
        raise Exception("[ModManager] Error during getting modlist from config_player.xml: Could not find regularpackages.\nFix it by removing everything from <regularpackages> to </regularpackages> and with those two, and replacing it with a single <regularpackages/>")

def get_recusive_modification_time_of_dir(origin_dir):
    modificationtime = 0
    for src_dir, dirs, files in os.walk(origin_dir):
        for file_ in files:
            new_modificationtime = os.path.getmtime(os.path.join(src_dir, file_))
            if new_modificationtime > modificationtime:
                modificationtime = new_modificationtime
    return modificationtime

def get_localcopy_path(filelist_str):
    localcopy_path = ""
    root = ET.fromstring(filelist_str)
    if root.tag == "regularpackages":
        if root.text != None:
            package = root[0]
            # werid, BUT just in case...
            if package.tag == 'package':
                localcopy_path = os.path.dirname(os.path.dirname(package.attrib['path']))
    return localcopy_path

def get_listOfModsfromConfig(filelist_str,localcopy_path, barotrauma_path):
    modlist = get_mods_config_player(barotrauma_path) 

    # reason i need to look in filelist is because of:
    #   - shit barotrauma devs (look up whole problem when you update modname on steam without updating the filelist.xml, this makes comments in filelist shit and not useful)
    #   - i can just get non-installed mods name's via api
    for mod in modlist:
        if os.path.isabs(mod['path']):
            filelist_path = mod['path']
        else:
            filelist_path = os.path.join(barotrauma_path, mod['path'])
        if os.path.exists(filelist_path):
            with open(filelist_path, 'r') as open_file:
                mod_filelist_str = open_file.read()
            mod_filelist = ET.fromstring(mod_filelist_str)
            if mod_filelist.tag.lower() == "contentpackage":
                mod['name'] = mod_filelist.attrib['name']
        
    return modlist

def sanitize_pathstr(path):
    path = str(path)
    path = path.replace(" ", "\\ ")
    return path

# function that uses steamcmd
# TODO make it use steamcmd process that runs in the bg and just has commands fed into it
time_of_last_usage = 0
def moddownloader(number_of_mod, tool_path, steamdir_path, location_with_steamcmd):
        if os.path.exists(location_with_steamcmd):
            command = location_with_steamcmd
            # san_steamdir_path = sanitize_pathstr(steamdir_path)
            # san_steamdir_path = "\"" + steamdir_path + "\""
            arguments = [command ,"+force_install_dir", steamdir_path, "+login anonymous", "+workshop_download_item 602960 " + str(number_of_mod), "validate", "+quit"]
            # TODO make its outpot less shit
            global time_of_last_usage
            if time_of_last_usage != 0 and int(round(time.time())) - time_of_last_usage < 1:
                time.sleep(int(round(time.time())) - time_of_last_usage)
            time_of_last_usage = int(round(time.time()))
            proc = subprocess.Popen(arguments, stdout=subprocess.PIPE)
            return proc
        else:
            Exception("[ModManager] SteamCMD could not be found! check your paths!")

def print_modlist(modlist):
    print("[ModManager] List of mods:")
    for mod in modlist:
        if str(mod["ID"]) == "2701251094":
            has_performancefix = True
        print("[ModManager] "+ str(mod["ID"]) + ": " + mod["name"])
    print("\n")
    print("\n")

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

def create_newfilelist(modlist, localcopy_path_og, barotrauma_path):
    regularpackages_new = "<regularpackages>\n"
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

        regularpackages_new += "      <!--" + mod['name'] + "-->\n"
        regularpackages_new += "      <package\n"
        regularpackages_new += "        path=\"" + temp_localcopy_path + "/" + mod['ID'] + "/filelist.xml\" />\n"
    regularpackages_new += "    </regularpackages>"
    return regularpackages_new

def save_managedmods(managed_mods, managed_mods_path):
    managed_mods_str = ""
    for managed_mod in managed_mods:
        managed_mods_str += managed_mod + "\n"
    with open(managed_mods_path, "w", encoding='utf8') as f:
        f.write(managed_mods_str)

def myprint(mssg, bar = 'bar'):
    if progressbar_functionality:
        bar.write(mssg)
    else:
        print(mssg)

# usage of steamcmd on modlist
def download_modlist(modlist, tool_path, steamdir_path, location_with_steamcmd):
    numberofupdatedmods = 0
    # '], where l_bar='{desc}: {percentage:3.0f}%|' and r_bar='| {n_fmt}/{total_fmt}{postfix} [{elapsed}<{remaining}, ' '{rate_fmt}]
    total_time = 0
    # with tqdm(total=len(modlist), dynamic_ncols = True, ascii = True, unit="Mods", position=0, bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}Mods [E:{elapsed} R:{remaining}]", desc = "Update Progress: ", disable = not progressbar_functionality) as bar:
    iterator = 0
    # bar.update()

    # get total size of modlist
    modlist_file_size = 0
    for mod in modlist:
        if 'file_size' in mod:
            modlist_file_size += mod['file_size']
    completed_file_size = 0

    for mod in modlist:
        pattern = "^\d*?$"
        if re.match(pattern, mod["ID"]):
            one_time = int(round(time.time()))
            # main part running moddlownloader
            mssg = "[ModManager] Starting steamcmd, Updating mod:" + mod["ID"] + ": " + mod["name"]
            if progressbar_functionality == False:
                mssg += "     Update Progress: " + str(iterator+1) + "/" + str(len(modlist))
                if len(modlist) >= 3:
                    if iterator >= 3:
                        # TODO dirty quickfix
                        if completed_file_size > 0:
                            number = int(abs((modlist_file_size - completed_file_size)*(total_time / completed_file_size)))
                            mssg += " ETA:" + str(str(number//60) + ":" + str(number%60))
            print(mssg)
            # TODO make output of steamcmd less spammy/silent
            # TODO instead of steamcmd downloading one mod at the time, make it download all of them in one start of steamcmd using steamcmd scripts or cmd line arguments
            proc = moddownloader(mod["ID"],tool_path, steamdir_path, location_with_steamcmd)
            for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                line = line.rstrip()
                # steam connection check
                if re.match(".*?" + "Connecting anonymously to Steam Public...OK" + ".*?", line):
                    print("[ModManger] Connected to steam! Beginning mod download...")
                    # iterator += 1
                    # bar.update(iterator)
                    # bar.update()
                # starting download
                if re.match(".*?Downloading item " + mod["ID"] + ".*?", line):
                    print("[ModManager] Downloading mod: " + mod["name"] + " (" + mod["ID"] + ")")
                    # iterator += 1
                    # bar.update(iterator)
                    # bar.update()
                # download complete
                if re.match(".*?Success. Downloaded item " + mod["ID"] + ".*?", line):
                    # check if mod has been downloaded in correct path
                    if re.match(".*?\"" + steamdir_path + ".*?steamapps.*?workshop.*?content.*?602960.*?" + mod["ID"] + "\".*?", line):
                        print("[ModManager] Downloaded mod!")
                        # iterator += 1
                        # bar.update(iterator)
                        # bar.update()
                    else:
                        raise Exception("[ModManager] Steamcmd has downloaded mod in wrong directory! Please make sure that steamdir path is up to specifications in README\n[Steamcmd]" + str(line))
                # else:
            proc.wait()
            output = proc.returncode
            if output == 0:
                numberofupdatedmods += 1
                iterator += 1
                # bar.update(1)
                if 'file_size' in mod:
                    completed_file_size += mod['file_size']
                one_time -= int(round(time.time()))
                total_time += one_time
                print("")
            else:
                raise Exception("[ModManager] Steamcmd return code is not 0! That means steamcd had problems!" + str(proc.errors))
        else:
            iterator += 1
            print("[ModManager] Skipped mod!: " + mod["Name"] + " (" + mod["ID"] + ")")
            # bar.update(1)
            print("")
            # iterator += 1
            # bar.update(iterator)
    print("")
    return numberofupdatedmods

def get_old_managed_mods(tool_path, managed_mods_path):
    # we first need to get all managed mods
    old_managed_mods = ""

    if os.path.exists(managed_mods_path):
        with open(managed_mods_path, "r", encoding='utf8') as f:
            old_managed_mods = f.read()

    # this will be paths to managed mods
    old_managed_mods = old_managed_mods.split('\n')
    if '' in old_managed_mods:
        old_managed_mods.remove('')
    return old_managed_mods

def get_managedmods(modlist, localcopy_path_og):
    managed_mods = []
    for mod in modlist:
        managed_mods.append(os.path.join(localcopy_path_og, mod['ID']))
    return managed_mods

def set_not_managedmods(old_managed_mods, modlist, localcopy_path_og, managed_mods):
    not_managedmods = old_managed_mods
    # removeing mods that exist in modlist
    for modwithdir in managed_mods:
        if modwithdir in not_managedmods:
            not_managedmods.remove(modwithdir)
    return not_managedmods

def main(requiredpaths):
    warning_LFBnotinstalled = False
    warning_modlist20 = False
    warning_modlist30 = False

    barotrauma_path = requiredpaths['barotrauma']
    tool_path = requiredpaths['tool']
    location_with_steamcmd = requiredpaths['steamcmd']
    steamdir_path = requiredpaths['steamdir']
    save_dir = requiredpaths['save_dir']
    max_saves = requiredpaths['max_saves']
    if 'collection_link' in requiredpaths and 'localcopy_path_override' in requiredpaths:
        collectionmode = True
        localcopy_path_override = requiredpaths['localcopy_path_override']
        collection_link = requiredpaths['collection_link']
        lastupdated_functionality = True
    else:
        collectionmode = False
        localcopy_path_override = ""
        lastupdated_functionality = False
    regularpackages = get_regularpackages(barotrauma_path)
    managed_mods_path = os.path.join(tool_path, "managed_mods.txt")
    old_managed_mods = get_old_managed_mods(tool_path, managed_mods_path)


    # collection save file
    collection_file_path = os.path.join(tool_path, "collection_save.txt")
    if flush_previous_col:
        if os.path.exists(collection_file_path):
            os.remove(collection_file_path)
    elif os.path.exists(collection_file_path):
        collection_file = ""
        with open(collection_file_path, "r", encoding='utf8') as f:
            collection_file = f.read()
        arr = collection_file.split(" ")
        collection_link = arr[0]
        localcopy_path_override = arr[1]
        collectionmode = True
        
    # check collection link if it is valid
    isvalid_collection_link = False
    if collectionmode:
        if collection_link != "":
            if re.match("https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=", collection_link) != None:
                collection_site = collectionf(collection_link)
                if collection_site != "ERROR":
                    isvalid_collection_link = True
            else:
                # on not finding collection sleep 5 sec then procceed with config_player.xml mode
                print("[ModManager] Collection link is invalid!")
                time.sleep(5)

    modlist = []
    if addperformacefix == True:
        WorkshopItem = {'Name': "Performance Fix", 'ID': "2701251094"}
        modlist.insert(0, WorkshopItem)

    requreslua = False
    requrescs = False
    hascs = False
    haslua = False
    if isvalid_collection_link and localcopy_path_override != "":
        collectionmode = True
        lastupdated_functionality = True
        dependencies_functionality = debug_dependencies_functionality
        print("[ModManager] Collection mode ENABLED, Downloading collection data (This might take a sec)")
        localcopy_path_og = localcopy_path_override
        modlist = generatelistOfMods(collection_site, modlist, {'addnames': True, 'addlastupdated': lastupdated_functionality, 'dependencies': dependencies_functionality})
        with open(collection_file_path, "w", encoding='utf8') as f:
            f.write(collection_link + " " + localcopy_path_og)
        for mod in modlist:
            if 'dependencies' in mod:
                for dependency in mod['dependencies']:
                    if str(dependency) == "2559634234" and requreslua == False:
                        requreslua = True
                    if str(dependency) == "2795927223" and requrescs == False:
                        requrescs = True
            if mod['ID'] == '2795927223':
                hascs = True
    else:
        collectionmode = False
        lastupdated_functionality = False
        print("[ModManager] Collection mode DISABLED, Downloading data from config_player.xml")
        if localcopy_path_override == "":
            localcopy_path_og = get_localcopy_path(regularpackages)
        else:
            localcopy_path_og = localcopy_path_override
        modlist.extend(get_listOfModsfromConfig(regularpackages,localcopy_path_og, barotrauma_path))
    
    for mod in modlist:
        if mod['ID'] == '2795927223':
            hascs = True
        if mod['ID'] == '2559634234':
            haslua = True
    localcopy_path = localcopy_path_og

    if save_dir != "" and max_saves != "":
        max_saves = int(max_saves)
        backupBarotraumaData(barotrauma_path, localcopy_path_og, save_dir, os.path.join(tool_path, "backup"), max_saves)

    if (not requreslua) or (not requrescs):
        for mod in modlist:
            if mod['ID'] == '2559634234':
                requreslua = True
            if mod['ID'] == '2795927223':
                requrescs = True


    # if requreslua or requrescs:
    #     if not os.path.exists(os.path.join(barotrauma_path, "LuaCsSetupConfig.xml")):
    #         warning_LFBnotinstalled = True


    if requrescs:
        if hascs == False:
            # TODO kind hacky way to do this
            temp_luacs = [{'Name': "Cs For Barotrauma", 'ID': "2795927223"}]
            temp_luacs = get_modsData_individual(temp_luacs, lastupdated_functionality, lastupdated_functionality)
            modlist.extend(temp_luacs)


    modlist = remove_duplicates(modlist)
    # modless?
    if len(modlist) == 0:
        print("[ModManager] No mods detected")
        return 
    else:
        numberofmodsminusserverside = len(modlist) - int(haslua) - int(hascs)
        print_modlist(modlist)


    modlist_inlocalcopy = []
    for modid in os.listdir(localcopy_path):
        if re.match("^\d*?$", modid):
            modlist_inlocalcopy.append(modid)
            
    # TODO idk why im doing this 
    # 1. Path fixing
    if not os.path.isabs(tool_path):
        tool_path = os.path.join(os.getcwd(), tool_path)
    if not os.path.isabs(steamdir_path):
        steamdir_path = os.path.join(os.getcwd(), steamdir_path)
    newinputdir = os.path.join(steamdir_path, "steamapps", "workshop", "content", "602960")
    if os.path.exists(steamdir_path):
        shutil.rmtree(steamdir_path)
    os.mkdir(steamdir_path)
    steamdir_path = os.path.realpath(steamdir_path)
    if not os.path.isabs(localcopy_path):
        localcopy_path = os.path.join(os.getcwd(), localcopy_path)


    # 2. get managed mods and not managed mods
    managed_mods = get_managedmods(modlist, localcopy_path_og)
    not_managedmods = set_not_managedmods(old_managed_mods, modlist, localcopy_path_og, managed_mods)


    # 3. re-create config_player
    regularpackages_new = create_newfilelist(modlist, localcopy_path_og, barotrauma_path)
    filelist_path = os.path.join(barotrauma_path, "config_player.xml")
    with open(filelist_path, "r", encoding='utf8') as f:
        filelist_str = f.read()
    filelist_str = filelist_str.replace(regularpackages, regularpackages_new)
    with open(filelist_path, "w", encoding='utf8') as f:
        f.write(filelist_str)
    # TODO NEED to take a look how to post comments with ET, and how to format it accordingly
    # set_mods_config_player(modlist, localcopy_path, barotrauma_path)


    # 4. saving managed mods
    save_managedmods(managed_mods, managed_mods_path)


    # lastupdated functionality
    if collectionmode and lastupdated_functionality:
        remove_arr = []
        # TODO current slowing time is about 
        # TODO lastupdated skip for windows and mac
        for mod in modlist:
            if 'LastUpdated' in mod:
                if os.path.exists(os.path.join(localcopy_path, mod['ID'])):
                    modificationtime = get_recusive_modification_time_of_dir(os.path.join(localcopy_path, mod['ID']))
                    # conversion into time struct
                    modificationtime = time.localtime(modificationtime)
                    test = time.strftime('%d %b, %Y @ %I:%M%p', modificationtime)
                    # greater not equal because of possible steam errors
                    if  modificationtime > mod['LastUpdated'] and os.path.exists(os.path.join(localcopy_path, mod['ID'], "filelist.xml")):
                        # TODO check if all xml files are matching what is in filelist
                        # TODO thats a lazy way to do it
                        remove_arr.append(mod)
        for item_to_remove in remove_arr:
            if item_to_remove in modlist:
                modlist.remove(item_to_remove)


    # main part running moddlownloader
    numberofupdatedmods = download_modlist(modlist, tool_path, steamdir_path, location_with_steamcmd)
    print("\n")
    if collectionmode and lastupdated_functionality:
        print("[ModManager] Skipping download of " + str(len(remove_arr)) + " Already up to date Mods. (if any issues arrise please remove every mod from your localcopy directory)")
    print("[ModManager] All "+ str(numberofupdatedmods) +" Mods have been updated")
    print("[ModManager] Downloading mods complete!")


    # 1. config backup and conservation
    baseconfig_path = os.path.join(tool_path, "BestDefaultConfigsTM")
    backup_option(baseconfig_path,newinputdir)
    backup_option(localcopy_path,newinputdir)


    # 2. remove not_managedmods
    print("[ModManager] Removing " + str(len(not_managedmods)) + " not managed now mods!")
    for not_managedmod in not_managedmods:
        if os.path.exists(not_managedmod):
            shutil.rmtree(not_managedmod)


    # TODO HOTFIX
    HOTFIX_steamcmdCRLF(newinputdir, modlist)


    # 3. + numberofupdatedmods actually moving mods to localcopy
    for mod in modlist:
        robocopysubsttute(os.path.join(newinputdir, mod['ID']), os.path.join(localcopy_path, mod['ID']))


    # 4. finishing anc cleaning up
    # removing steamdir because steamcmd is piece of crap and it sometimes wont download mod if its in directory
    shutil.rmtree(steamdir_path)
    print("[ModManager] Mods Updated!\n")


    # checking if mod is pure server-side or client side
    numberofluamods = 0
    for mod in modlist:
        if os.path.exists(os.path.join(localcopy_path, mod['ID'], "filelist.xml")):
            with open(os.path.join(localcopy_path, mod['ID'], "filelist.xml"), "r", encoding='utf8') as f:
                filelist = f.readlines()
            xmlitems = 0
            for ix in range(2, len(filelist)):
                xmlitems += len(re.findall(".xml", filelist[ix]))
            if xmlitems <= 0:
                numberofluamods += 1


    if numberofmodsminusserverside - numberofluamods >= 30 and not disablewarnings:
        warning_modlist30 = True
    elif numberofmodsminusserverside - numberofluamods >= 20 and not disablewarnings:
        warning_modlist20 = True


    # TODO rework
    # this check is dumb because the BEST way to check if lua is installed is to have a script start a server, then run a lua mod
    # make then that lua mod
    # if warning_LFBnotinstalled:
    #     sys.stdout.write("\033[1;31m")
    #     print("[ModManager] WARNING Lua for barotrauma NOT INSTALLED, and is needed!\nInstall Lua for barotrauma then re-run script!")
    #     sys.stdout.write("\033[0;0m")
    #     time.sleep(20)


    if warning_modlist30:
        sys.stdout.write("\033[1;31m")
        print("[ModManager] I STRONGLY ADVISE TO SHORTEN YOUR MODLIST! It is very rare for players to join public game that has a lot of mods.\n[ModManager] Please shorten your modlist by removing unnesesary mods, or use group of mods inside of one package.")
        sys.stdout.write("\033[0;0m")
        time.sleep(30)
    elif warning_modlist20:
        sys.stdout.write("\033[1;31m")
        print("[ModManager] I advise to shorten your modlist! It is very rare for players to join public game that has a lot of mods.\n[ModManager] Please shorten your modlist by removing unnesesary mods, or use group of mods inside of one package.")
        sys.stdout.write("\033[0;0m")
        time.sleep(20)

if __name__ == '__main__':
    print("Wellcome to ModManager script!")
    # gotta have it here even if it pains me
    required_values = set_required_values()
    while(True):
        if os.path.exists(os.path.join(required_values['tool'], "collection_save.txt")):
            print("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands.")
            print("[ModManager] Steam collection mode enabled! Disable by entering collection sub-menu.")
            print("[ModManager] Do you want to update that collection of mods? ((Y)es / (n)o): ")
        else: 
            print("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands.")
            print("[ModManager] Steam collection mode disabled! Enable by entering collection sub-menu.")
            print("[ModManager] Do you want to update mods? ((Y)es / (n)o): ")
        user_command = input().lower()
        if user_command == "yes" or user_command == "y":
            main(required_values)
            break
        elif user_command == "no" or user_command == "n":
            break
        elif user_command == "collection" or user_command == "c":
            print("[ModManager] Provide an collection link then press enter, or if you want to disable previously enabled collection mode, type 'n' then enter: ")
            collection_url = input()
            if collection_url != "n":
                print("[ModManager] Provide an localcopy path (if you dont know what to input, type 'LocalMods') then press enter: ")
                localcopy_path = input()
            else:
                collection_url = ""
                localcopy_path = ""
            flush_previous_col = True
            # TODO collection check, if link is valid
            required_values['collection_link'] = collection_url
            required_values['localcopy_path_override'] = localcopy_path
            required_values['collectionmode'] = True
            main(required_values)
            break
        elif user_command == "help" or user_command == "h":
            # TODO rework it to get Available modes from readme
            print("[ModManager] Help menu:")
            print("[ModManager] README: https://github.com/Milord-ThatOneModder/Barotrauma-ModManager/blob/main/README.md")
            print("### Available modes ###")
            print("Collection mode:")
            print("\t- In collection mode your modlist as well as `config_player.xml` are fully managed by a ModManager")
            print("\t- For configuring the collection mode type `c` or `collection` then press `enter` when prompted (on ModManager start), then paste your collection link then press `enter`, then type your localcopy path, according to what ModManager is outputing (writting on console).")
            print("\t- To change collection link, type `c` or `collection` then press `enter`, then paste your new collection link then press enter, then type your path were you want to store your mods (`localcopy`), according to what ModManager is outputing.")
            print("\t- If you wish to stop using collection mode, just type `c` or `collection` then enter, then type `n` then `enter`.")
            print("config_player.xml mode:")
            print("\t- **IF YOU DONT KNOW WHAT `config_player.xml` IS OR YOU DONT KNOW ITS SYNTAX (or what xml even is), I RECOMEND USING COLLECTION MODE**")
            print("\t- Replace content of your server's `config_player.xml` to content of your personal machine (client)'s `config_player.xml`.")
            print("\t- Replace all occurences \"C:/Users/$yourusername$/AppData/Local/Daedalic Entertainment GmbH/Barotrauma/WorkshopMods/Installed\" (your personal machine mod's path) where \"$yourusername$\" is your user name on windows machine, to \"LocalMods\"\n\n")
            continue
        else:
            print("[ModManager] Provide a valid anwser: \"y\" or \"yes\" / \"n\" or \"no\"")
        