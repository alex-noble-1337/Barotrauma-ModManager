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

import gettext
_ = gettext.gettext

import xml.etree.ElementTree as ET


# from ConfigRecoder import get_modsnamelastupdated 
from configbackup import backup_option
from ConfigRecoder import get_modlist_collection_site 
from ConfigRecoder import collectionf
from ConfigRecoder import get_modlist_data_webapi
from configbackup import backupBarotraumaData

# written in 3-4h so this is probbabbly bad, if you curious why this is needed, uhhhh :barodev: <- probbabbly them
def FIX_barodev_moment(downloaded_mod, downloaded_mod_path):
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

    filelist_path = os.path.join(downloaded_mod_path, "filelist.xml")
    if os.path.exists(filelist_path):
        with open(filelist_path, 'r') as open_file:
            filelist_str = open_file.read()

        element = ET.fromstring(filelist_str)
        if element.tag.lower() == "contentpackage":
            if element.attrib['name'] != downloaded_mod['name']:
                oldname = element.attrib['name']
                element.attrib['name'] = downloaded_mod['name']
                if 'corepackage' in element.attrib:
                    if str(element.attrib['corepackage']) == 'False':
                        element.attrib['corepackage'] = 'false'
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
                            element.attrib['steamworkshopid'] = downloaded_mod['ID']
                        else:
                            element.attrib[desired_order_element] = ""
                # i dont understand it, this is shit
                # TOO BAD!
                element.attrib = {k: element.attrib[k] for k in desired_order_list}

                filelist_str = ET.tostring(element, encoding='utf-8', method='xml', xml_declaration=True)


                with open(filelist_path, 'wb') as open_file:
                    open_file.write(filelist_str)


# set up all default values and paths
# TODO rework
def set_required_values():
    options_arr = sys.argv[1:]
    changed_barotrauma_path = False
    changed_tool_path = False
    changed_steamcmd_path = False
    input_options = {'collectionmode': False}

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
                        input_options['barotrauma'] = os.getcwd()
                        changed_barotrauma_path = True
                    else:
                        input_options['barotrauma'] = options_arr[i+1]
                        changed_barotrauma_path = True
                else:
                    input_options['barotrauma'] = os.getcwd()
                    changed_barotrauma_path = True
            
            # --toolpath or -t - path to the ModManager Direcotry where script can put all the "cashe" files. set it do default if you dont know where or what you are doing. Must be a path to THE FOLDER.  Does not accept ""
            if options_arr[i] == '--toolpath' or options_arr[i] == '-t':
                if tempval >= 2:
                    if options_arr[i+1] == ".":
                        input_options['tool'] = os.getcwd()
                        changed_tool_path = True
                    else:
                        input_options['tool'] = options_arr[i+1]
                        changed_tool_path = True
                else:
                    input_options['tool'] = os.getcwd()
                    changed_tool_path = True

            # --steamcmdpath or -s - path to your steamcmd or steamcmd.exe. Must be a path to THE FOLDER, not the program itself.  Does not accept ""
            if options_arr[i] == '--steamcmdpath' or options_arr[i] == '-s':
                if tempval >= 2:
                    if options_arr[i+1] == "pwd":
                        if sys.platform == 'win32':
                            input_options['steamcmd'] = os.path.join(os.getcwd(), "steamcmd.exe")
                        else:
                            input_options['steamcmd'] = os.path.join(os.getcwd(), "steamcmd.sh")
                        changed_steamcmd_path = True
                    else:
                        input_options['steamcmd'] = options_arr[i+1]
                        changed_steamcmd_path = True
                else:
                    input_options['steamcmd'] = options_arr[i+1]
                    changed_steamcmd_path = True

            # TODO '--collection to the documentaton
            if options_arr[i] == '--collection' or options_arr[i] == '-c':
                if tempval >= 3:
                    # TODO check if link is good
                    input_options['collection_link'] = options_arr[i+1]
                    input_options['collectionmode'] = True
                    input_options['localcopy_path_override'] = options_arr[i+2]
                
             # TODO add it to the documentaton
            if options_arr[i] == '--performancefix' or options_arr[i] == '-p':
                if tempval >= 1:
                    global addperformacefix
                    input_options['addperformacefix'] = True

            # TODO add it to the documentaton
            if options_arr[i] == '--backup':
                if tempval >= 3:
                    # TODO check if link is good
                    input_options['max_saves'] = int(options_arr[i+1])
                    input_options['save_dir'] = options_arr[i+2]

    # setting up default values and path handling
    if not changed_barotrauma_path:
        input_options['barotrauma'] = default_barotrauma_path
    if not os.path.isabs(input_options['barotrauma']):
        input_options['barotrauma'] = os.path.join(os.getcwd(), input_options['barotrauma'])
    if not changed_tool_path:
        input_options['tool'] = default_tool_path
    if not changed_steamcmd_path:
        input_options['steamcmd'] = default_steamcmd_path
    if default_steamdir_path == "":
        input_options['steamdir'] = os.path.join(input_options['tool'], "steamdir")
    else:
        input_options['steamdir'] = default_steamdir_path
    
    # TODO
    if 'collection_link' in input_options and 'localcopy_path_override' in input_options:
        input_options['mode'] = "collection"
    else:
        input_options['mode'] = "config_player"
        # removed below cuz this conflicts with if user wants to have localcopy in pwd
        # input_options['localcopy_path_override'] = ""

    input_options['backup_path'] = os.path.join(input_options['tool'], "backup")
    input_options['get_dependencies'] = debug_dependencies_functionality
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
        print(_("[ModManager] Could not find the config_player.xml! Check your barotrauma path!"))
        print(_("[ModManager] Barotrauma path: " + config_player_path))
        print(_(e))
    return config_player_str 

# config player IO
# config player Input
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
# config_player.xml output TODO NOT USED
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
        print(_("[ModManager] Could not find the config_player.xml! Check your barotrauma path!"))
        print(_("[ModManager] Barotrauma path: " + filelist_path))
        print(_(e))

    pattern = "<regularpackages>[\s\S]*?<\/regularpackages>"
    regularpackages = re.findall(pattern, filelist_str)

    if len(regularpackages) <= 0:
        # patch for </regularpackages>, just in case
        # TODO a bit stupid, so rework it
        # print(_("<regularpackages/>")
        # print(_("<regularpackages>\n\t\t</regularpackages>")
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

def get_modlist_regularpackages(filelist_str,localcopy_path, barotrauma_path):
    modlist = get_mods_config_player(barotrauma_path) 

    # reason i need to look in filelist is because of:
    #   - shit barotrauma devs (look up whole problem when you update modname on steam without updating the filelist.xml, this makes comments in filelist shit and not useful)
    #   - i can just get non-installed mods name's via api TODO, make it in config_player mode.
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
        Exception("[ModManager] SteamCMD could not be found! check your paths!\nPath to Steamcmd given: " + location_with_steamcmd)

def print_modlist(modlist):
    print(_("[ModManager] List of mods:"))
    for mod in modlist:
        if str(mod["ID"]) == "2701251094":
            has_performancefix = True
        print(_("[ModManager] "+ str(mod["ID"]) + ": " + mod['name']))
    print(_("\n"))
    print(_("\n"))

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

def create_new_regularpackages(modlist, localcopy_path_og, barotrauma_path):
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

def get_old_managedmods(managed_mods_path):
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

def get_not_managedmods(old_managed_mods, managed_mods):
    not_managedmods = old_managed_mods
    # removeing mods that exist in modlist
    for modwithdir in managed_mods:
        if modwithdir in not_managedmods:
            not_managedmods.remove(modwithdir)
    return not_managedmods

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
            mssg = "[ModManager] Starting steamcmd, Updating mod:" + mod["ID"] + ": " + mod['name']
            if progressbar_functionality == False:
                mssg += "     Update Progress: " + str(iterator+1) + "/" + str(len(modlist))
                if len(modlist) >= 3:
                    if iterator >= 3:
                        # TODO dirty quickfix
                        if completed_file_size > 0:
                            number = int(abs((modlist_file_size - completed_file_size)*(total_time / completed_file_size)))
                            mssg += " ETA:" + str(str(number//60) + ":" + str(number%60))
            print(_(mssg))
            # TODO make output of steamcmd less spammy/silent
            # TODO instead of steamcmd downloading one mod at the time, make it download all of them in one start of steamcmd using steamcmd scripts or cmd line arguments
            proc = moddownloader(mod["ID"],tool_path, steamdir_path, location_with_steamcmd)
            for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                line = line.rstrip()
                # steam connection check
                if re.match(".*?" + "Connecting anonymously to Steam Public...OK" + ".*?", line):
                    print(_("[ModManger] Connected to steam! Beginning mod download..."))
                    # iterator += 1
                    # bar.update(iterator)
                    # bar.update()
                # starting download
                if re.match(".*?Downloading item " + mod["ID"] + ".*?", line):
                    print(_("[ModManager] Downloading mod: " + mod['name'] + " (" + mod["ID"] + ")"))
                    # iterator += 1
                    # bar.update(iterator)
                    # bar.update()
                # download complete
                if re.match(".*?Success. Downloaded item " + mod["ID"] + ".*?", line):
                    # check if mod has been downloaded in correct path
                    if re.match(".*?\"" + steamdir_path + ".*?steamapps.*?workshop.*?content.*?602960.*?" + mod["ID"] + "\".*?", line):
                        print(_("[ModManager] Downloaded mod!"))
                        # TODO get that path into an array so steamdir path is not needed, and ypu just move mods from wherever the steamcmd puts tgem
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
                print(_(""))
            else:
                raise Exception("[ModManager] Steamcmd return code is not 0! That means steamcd had problems!" + str(proc.errors))
        else:
            iterator += 1
            print(_("[ModManager] Skipped mod!: " + mod['name'] + " (" + mod["ID"] + ")"))
            # bar.update(1)
            print(_(""))
            # iterator += 1
            # bar.update(iterator)
    print(_(""))
    return numberofupdatedmods

# return false on negative test resoult, on positive resoult return collection site string
def get_collectionsite(collection_link: str):
    isvalid_collection_link = False
    if re.match("https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=", collection_link) != None:
        collection_site = collectionf(collection_link)
        if collection_site != "ERROR":
            isvalid_collection_link= True
    if isvalid_collection_link:
        return collection_site
    else:
        return isvalid_collection_link
def check_collection_link(collection_site):
    if collection_site == False:
        print(_("[ModManger] Collection link INVALID. Do you want to exit the script? ((Y)es / (n)o):"))
        user_command = input().lower()
        if user_command == "no" or user_command == "n":
            raise Exception("Collection link INVALID! Re-enable Collection mode.")
        isvalid_collection_link = False
    else:
        isvalid_collection_link = True
    return isvalid_collection_link

def is_pure_lua_mod(mod_path: str):
    pure_lua_mod = False
    if os.path.exists(os.path.join(mod_path, "filelist.xml")):
        with open(os.path.join(mod_path, "filelist.xml"), "r", encoding='utf8') as f:
            filelist = f.readlines()
        xmlitems = 0
        for ix in range(2, len(filelist)):
            xmlitems += len(re.findall(".xml", filelist[ix]))
        if xmlitems <= 0:
            pure_lua_mod = True
    return pure_lua_mod

def get_up_to_date_mods(mods, localcopy_path):
    new_mods = mods
    remove_arr = []
    # TODO current slowing time is about 
    # TODO lastupdated skip for windows and mac
    for mod in new_mods:
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
    return remove_arr

# TODO name
# requres lastupdated value in mod object, return mods array that has only mods that requre update
def remove_up_to_date_mods(mods, remove_arr):
    for item_to_remove in remove_arr:
        if item_to_remove in new_mods:
            new_mods.remove(item_to_remove)
    return new_mods

def deleting_not_managedmods(not_managedmods):
    for not_managedmod in not_managedmods:
        if os.path.exists(not_managedmod):
            shutil.rmtree(not_managedmod)
    print(_("[ModManager] Removed " + str(len(not_managedmods)) + " not managed now mods!"))

def main(user_prefs):
    # TODO fix this stupid shit, idk if that is my ocd but this amout of variables looks wrong
    warning_LFBnotinstalled = False
    requreslua = False
    requrescs = False
    hascs = False
    haslua = False
    number_of_pure_lua_mods = 0
    modlist = []
    modlist_localcopy = []
    up_to_date_mods = []
    # paths so i dont have to repeat them 9999 times
    steamcmd_downloads = os.path.join(user_prefs['steamdir'], "steamapps", "workshop", "content", "602960")
    config_player_path = os.path.join(user_prefs['barotrauma'], "config_player.xml")
    recomended_configs = os.path.join(user_prefs['tool'], "BestDefaultConfigsTM")
    # "data":
    regularpackages = get_regularpackages(user_prefs['barotrauma'])
    # get "persistent values" (config)
    # TODO rework this, have only 1 config file
    config_collectionmode_path = os.path.join(user_prefs['tool'], "collection_save.txt")
    managedmods_path = os.path.join(user_prefs['tool'], "managed_mods.txt")
    old_managedmods = get_old_managedmods(managedmods_path)
    if flush_previous_col:
        if os.path.exists(config_collectionmode_path):
            os.remove(config_collectionmode_path)
    elif os.path.exists(config_collectionmode_path):
        collection_file = ""
        with open(config_collectionmode_path, "r", encoding='utf8') as f:
            collection_file = f.read()
        arr = collection_file.split(" ")
        user_prefs['collection_link'] = arr[0]
        user_prefs['localcopy_path_override'] = arr[1]
        user_prefs['mode'] = "collection"


    # clean up an creation of steamdir
    if os.path.exists(user_prefs['steamdir']):
        shutil.rmtree(user_prefs['steamdir'])
    os.mkdir(user_prefs['steamdir'])


    # check collection link if it is valid
    if user_prefs['mode'] == "collection":
        collection_site = get_collectionsite(user_prefs['collection_link'])
        isvalid_collection_link = check_collection_link(collection_site)
        
            
    if addperformacefix:
        modlist.insert(0, {'name': "Performance Fix", 'ID': "2701251094"})


    if isvalid_collection_link and user_prefs['mode'] == "collection":
        print(_("[ModManager] Collection mode ENABLED, Downloading collection data (This might take a sec)"))
        modlist = get_modlist_collection_site(collection_site, modlist, {'addnames': True, 'addlastupdated': True, 'dependencies': user_perfs['get_dependencies']})
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
        print(_("[ModManager] Collection mode DISABLED, Downloading data from config_player.xml"))
        if user_prefs['localcopy_path_override'] == "":
            user_prefs['localcopy_path_override'] = get_localcopy_path(regularpackages)
        modlist.extend(get_modlist_regularpackages(regularpackages,user_prefs['localcopy_path_override'], user_prefs['barotrauma']))


    # TODO remove duplicates once, try NOT to send duplicate requests for data to api
    modlist = get_modlist_data_webapi(modlist)

    
    for mod in modlist:
        if mod['ID'] == '2795927223':
            hascs = True
        if mod['ID'] == '2559634234':
            haslua = True


    # TODO changed below condition cuz it disslallowed pwd
    if 'save_dir' in user_prefs and 'max_saves' in user_prefs:
        backupBarotraumaData(user_prefs['barotrauma'], user_prefs['localcopy_path_override'], user_prefs['save_dir'], user_prefs['backup_path'], user_prefs['max_saves'])
    if requrescs and not hascs:
        # TODO kind hacky way to do this
        temp_luacs = [{'name': "Cs For Barotrauma", 'ID': "2795927223"}]
        temp_luacs = get_modlist_data_webapi(temp_luacs)
        modlist.extend(temp_luacs)


    modlist = remove_duplicates(modlist)


    # modless?
    if len(modlist) == 0:
        print(_("[ModManager] No mods detected"))
        return 
    else:
        numberofmods_minuslua = len(modlist) - int(haslua) - int(hascs)
        print_modlist(modlist)


    for modid in os.listdir(user_prefs['localcopy_path_override']):
        if re.match("^\d*?$", modid):
            modlist_localcopy.append(modid)

      
    # TODO idk why im doing this 
    # Path fixing
    if not os.path.isabs(user_prefs['tool']):
        user_prefs['tool'] = os.path.join(os.getcwd(), user_prefs['tool'])
    if not os.path.isabs(user_prefs['steamdir']):
        user_prefs['steamdir'] = os.path.join(os.getcwd(), user_prefs['steamdir'])
    if not os.path.isabs(user_prefs['localcopy_path_override']):
        user_prefs['localcopy_path_override'] = os.path.join(os.getcwd(), user_prefs['localcopy_path_override'])
    user_prefs['steamdir'] = os.path.realpath(user_prefs['steamdir'])


    managed_mods = get_managedmods(modlist, user_prefs['localcopy_path_override'])
    not_managedmods = get_not_managedmods(old_managedmods, managed_mods)


    # re-create config_player
    new_regularpackages = create_new_regularpackages(modlist, user_prefs['localcopy_path_override'], user_prefs['barotrauma'])
    with open(config_player_path, "r", encoding='utf8') as f:
        filelist_str = f.read()
    filelist_str = filelist_str.replace(regularpackages, new_regularpackages)
    with open(config_player_path, "w", encoding='utf8') as f:
        f.write(filelist_str)
    # TODO NEED to take a look how to post comments with ET, and how to format it accordingly
    # set_mods_config_player(modlist, localcopy_path, barotrauma_path)


    # save configs
    if isvalid_collection_link and user_prefs['mode'] == "collection":
        with open(config_collectionmode_path, "w", encoding='utf8') as f:
            f.write(user_prefs['collection_link'] + " " + user_prefs['localcopy_path_override'])
    save_managedmods(managed_mods, managedmods_path)


    # lastupdated functionality
    if user_prefs['mode'] == "collection":
        up_to_date_mods = get_up_to_date_mods(mods, localcopy_path)
        mods = remove_up_to_date_mods(mods, up_to_date_mods)


    # main part, running moddlownloader
    nr_updated_mods = download_modlist(modlist, user_prefs['tool'], user_prefs['steamdir'], user_prefs['steamcmd'])
    print(_("\n"))
    if user_prefs['mode'] == "collection":
        print(_("[ModManager] Skipping download of " + str(len(up_to_date_mods)) + " Already up to date Mods. (if any issues arrise please remove every mod from your localcopy directory)"))
    print(_("[ModManager] All "+ str(nr_updated_mods) +" Mods have been updated"))


    # config backup and conservation
    backup_option(recomended_configs, steamcmd_downloads)
    backup_option(user_prefs['localcopy_path_override'], steamcmd_downloads)


    deleting_not_managedmods(not_managedmods)


    # actually moving mods to localcopy
    for mod in modlist:
        mod_path = os.path.join(steamcmd_downloads, mod['ID'])
        FIX_barodev_moment(mod, mod_path)
        robocopysubsttute(mod_path, os.path.join(user_prefs['localcopy_path_override'], mod['ID']))


    # finishing anc cleaning up
    # removing steamdir because steamcmd is piece of crap and it sometimes wont download mod if its in directory
    shutil.rmtree(user_prefs['steamdir'])
    if len(up_to_date_mods) < nr_updated_mods:
        print(_("[ModManager] Mods Updated!\n"))
    else:
        print(_("[ModManager] All Mods were up to date!"))


    # accessing filelists of mods
    for mod in modlist:
        # checking if mod is pure server-side or client side
        if is_pure_lua_mod(os.path.join(user_prefs['localcopy_path_override'], mod['ID'])):
            number_of_pure_lua_mods += 1 


    # TODO rework
    # this check is dumb because the BEST way to check if lua is installed is to have a script start a server, then run a lua mod
    # so this is innacurate
    # check if there is Lua directory, and harmony is in barotrauma directory
    # if warning_LFBnotinstalled:
    #     sys.stdout.write("\033[1;31m")
    #     print(_("[ModManager] WARNING Lua for barotrauma NOT INSTALLED, and is needed!\nInstall Lua for barotrauma then re-run script!")
    #     sys.stdout.write("\033[0;0m")
    #     time.sleep(20)


    # warnings about long modlists
    if numberofmods_minuslua - number_of_pure_lua_mods >= 30 and not disablewarnings:
        sys.stdout.write("\033[1;31m")
        print(_("[ModManager] I STRONGLY ADVISE TO SHORTEN YOUR MODLIST! It is very rare for players to join public game that has a lot of mods.\n[ModManager] Please shorten your modlist by removing unnesesary mods, or use group of mods inside of one package."))
        sys.stdout.write("\033[0;0m")
        time.sleep(30)
    elif numberofmods_minuslua - number_of_pure_lua_mods >= 20 and not disablewarnings:
        sys.stdout.write("\033[1;31m")
        print(_("[ModManager] I advise to shorten your modlist! It is very rare for players to join public game that has a lot of mods.\n[ModManager] Please shorten your modlist by removing unnesesary mods, or use group of mods inside of one package."))
        sys.stdout.write("\033[0;0m")
        time.sleep(20)

if __name__ == '__main__':
    print(_("Wellcome to ModManager script!"))
    # gotta have it here even if it pains me
    required_values = set_required_values()
    while(True):
        if os.path.exists(os.path.join(required_values['tool'], "collection_save.txt")):
            print(_("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands."))
            print(_("[ModManager] Steam collection mode enabled! Disable by entering collection sub-menu."))
            print(_("[ModManager] Do you want to update that collection of mods? ((Y)es / (n)o): "))
        else: 
            print(_("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands."))
            print(_("[ModManager] Steam collection mode disabled! Enable by entering collection sub-menu."))
            print(_("[ModManager] Do you want to update mods? ((Y)es / (n)o): "))
        user_command = input().lower()
        if user_command == "yes" or user_command == "y":
            main(required_values)
            break
        elif user_command == "no" or user_command == "n":
            break
        elif user_command == "collection" or user_command == "c":
            print(_("[ModManager] Provide an collection link then press enter, or if you want to disable previously enabled collection mode, type 'n' then enter: "))
            collection_url = input()
            if collection_url != "n":
                print(_("[ModManager] Provide an localcopy path (if you dont know what to input, type 'LocalMods') then press enter: "))
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
            print(_("[ModManager] Help menu:"))
            print(_("[ModManager] README: https://github.com/Milord-ThatOneModder/Barotrauma-ModManager/blob/main/README.md"))
            print(_("### Available modes ###"))
            print(_("Collection mode:"))
            print(_("\t- In collection mode your modlist as well as `config_player.xml` are fully managed by a ModManager"))
            print(_("\t- For configuring the collection mode type `c` or `collection` then press `enter` when prompted (on ModManager start), then paste your collection link then press `enter`, then type your localcopy path, according to what ModManager is outputing (writting on console)."))
            print(_("\t- To change collection link, type `c` or `collection` then press `enter`, then paste your new collection link then press enter, then type your path were you want to store your mods (`localcopy`), according to what ModManager is outputing."))
            print(_("\t- If you wish to stop using collection mode, just type `c` or `collection` then enter, then type `n` then `enter`."))
            print(_("config_player.xml mode:"))
            print(_("\t- **IF YOU DONT KNOW WHAT `config_player.xml` IS OR YOU DONT KNOW ITS SYNTAX (or what xml even is), I RECOMEND USING COLLECTION MODE**"))
            print(_("\t- Replace content of your server's `config_player.xml` to content of your personal machine (client)'s `config_player.xml`."))
            print(_("\t- Replace all occurences \"C:/Users/$yourusername$/AppData/Local/Daedalic Entertainment GmbH/Barotrauma/WorkshopMods/Installed\" (your personal machine mod's path) where \"$yourusername$\" is your user name on windows machine, to \"LocalMods\"\n\n"))
            continue
        else:
            print(_("[ModManager] Provide a valid anwser: \"y\" or \"yes\" / \"n\" or \"no\""))