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
warnings_as_errors = False


# My "Quality" code
# TODO change this to import only individual commands
import os
import shutil
import re
from functools import reduce
import time
import datetime
import subprocess
import sys
import io
import xml.etree.ElementTree as ET

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import gettext
_ = gettext.gettext


# load submodules
from configbackup import backup_option
from ConfigRecoder import get_modlist_collection_site 
from ConfigRecoder import collectionf
from ConfigRecoder import get_modlist_data_webapi
from configbackup import backupBarotraumaData
import BaroRewrites

# written in 3-4h so this is probbabbly bad, if you curious why this is needed, uhhhh :barodev: <- probbabbly them
def FIX_barodev_moment(downloaded_mod, downloaded_mod_path):
    WINDOWS_LINE_ENDING = b'\r\n'
    UNIX_LINE_ENDING = b'\n'
    filelist_path = os.path.join(downloaded_mod_path, "filelist.xml")

    # get oldname or name for fixing Mods/oldname to %ModDir% 
    with open(filelist_path, 'r', encoding="utf8") as open_file:
        filelist_str = open_file.read()
    filelist = ET.fromstring(filelist_str)
    if filelist.tag.lower() == "contentpackage":
        name = ""
        oldname = ""
        if 'name' in filelist.attrib:
            name = filelist.attrib['name']
        if 'altnames' in filelist.attrib:
            oldname = filelist.attrib['altnames']
        def_content = []
        content_types = ["item","character","mapcreature","text",
                         "uistyle","afflictions","structure",
                         "upgrademodules","ruinconfig",
                         "wreckaiconfig","backgroundcreatureprefabs",
                         "levelobjectprefabs","particles","decals",
                         "randomevents","eventmanagersettings",
                         "locationtypes","mapgenerationparameters",
                         "levelgenerationparameters",
                         "cavegenerationparameters","outpostconfig",
                         "npcsets","missions","traitormissions",
                         "npcpersonalitytraits","npcconversations",
                         "jobs","orders","corpses","sounds",
                         "skillsettings","factions","itemassembly",
                         "talents","talenttrees","startitems","tutorials"]
        # definition_files = filelist.getchildren()
        for def_file in filelist:
            if def_file.tag.lower() in content_types:
                if 'file' in def_file.attrib:
                    def_file.attrib['file'] = def_file.attrib['file'].replace("Mods/" + name, "%ModDir%")
                    if oldname != "":
                        def_file.attrib['file'] = def_file.attrib['file'].replace("Mods/" + oldname, "%ModDir%")
                    content = def_file.attrib['file'].replace("%ModDir%/", "")
                    content = BaroRewrites.CleanUpPath(content)
                    def_content.append(content)

    old_paths = False
    for file_path in def_content:
        file_path = os.path.join(downloaded_mod_path, file_path)
        # TODO paths arent case sensitive
        if os.path.exists(file_path):
            with open(file_path, 'rb') as open_file:
                content = open_file.read()
            if sys.platform == 'win32':
                # Unix ➡ Windows
                content = content.replace(UNIX_LINE_ENDING, WINDOWS_LINE_ENDING)
                logger.info("Changed from unix to windows line endings in {0}".format(file_path))
            else:
                # Windows ➡ Unix
                content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
                logger.info("Changed from windows to unix line endings in {0}".format(file_path))
            with open(file_path, 'wb') as open_file:
                open_file.write(content)

            # fixing Mods/oldname to %ModDir% 
            with open(file_path, 'r', encoding="utf8") as open_file:
                content = open_file.read()
            if oldname != "":
                occurrences = re.finditer("Mods\\/((" + name + ")|(" + oldname + "))", content)
            else:
                occurrences = re.finditer("Mods\\/" + name, content)
            points = reduce(lambda x, y: x + [y.start()], occurrences, [])
            drift = 0
            for point in points:
                in_comment = False
                for i in range(point):
                    pointer = point - i
                    if content[pointer:pointer + 3] == "-->":
                        in_comment = False
                        break
                    if content[pointer:pointer + 4] == "<!--":
                        in_comment = True
                        break
                if in_comment != True:
                    replace_to = "Mods/" + name
                    test = content[point + drift:point + len(replace_to) + drift]
                    if content[point + drift:point + len(replace_to) + drift] == replace_to:
                        content = content[:point + drift] + "%ModDir%" + content[drift + point + len(replace_to):]
                        drift += len("%ModDir%") - len(replace_to)
                        old_paths = True
                    if oldname != "":
                        test = content[point:point + len(replace_to)]
                        replace_to = "Mods/" + oldname
                        if content[point:point + len(replace_to)] == replace_to:
                            content = content[:point] + "%ModDir%" + content[point + len(replace_to):]
                            drift += len("%ModDir%") - len(replace_to)
                            old_paths = True
            # if oldname != "":
            #     content = content.replace("Mods/" + oldname, "%ModDir%")
            with open(file_path, 'w', encoding="utf8") as open_file:
                open_file.write(content)
    if old_paths:
        if warnings_as_errors:
            raise Exception(_("Mod of id:{0} and name: {1} does have old paths! Stable behaviour cannot be made sure of! Remove if possible!").format(downloaded_mod['ID'], downloaded_mod['name']))
        else:
            print(_("Mod of id:{0} and name: {1} does have old paths! Stable behaviour cannot be made sure of! Remove if possible!").format(downloaded_mod['ID'], downloaded_mod['name']))


    desired_order_list = ['name', 'steamworkshopid', 'corepackage', 'modversion', 'gameversion', 'installtime', 'altnames', 'expectedhash']
    if os.path.exists(filelist_path):
        with open(filelist_path, 'r', encoding="utf8") as open_file:
            filelist_str = open_file.read()

        def_file = ET.fromstring(filelist_str)
        if def_file.tag.lower() == "contentpackage":
            if not 'name' in def_file.attrib:
                def_file.attrib['name'] = downloaded_mod['name']
            else:
                if 'name' in downloaded_mod:
                    if def_file.attrib['name'] != downloaded_mod['name']:
                        logger.info("Name of {0} was changed via steam! Applying workaround...".format(def_file.attrib['steamworkshopid']))
                        oldname = def_file.attrib['name']
                        def_file.attrib['name'] = downloaded_mod['name']
                        # if 'corepackage' in element.attrib:
                        #     if str(element.attrib['corepackage']) == 'False':
                        #         element.attrib['corepackage'] = 'False'
                        # TODO make an escape invalid xml of old names
                        test1 = oldname
                        test2 = downloaded_mod['name']
                        if test1 != test2:
                            def_file.attrib['altnames'] = oldname

                        # fixing False or FALSE or whatever to false
                        # for attribute in element.attrib:
                        #     if type(element.attrib[attribute]) is str:
                        #         if element.attrib[attribute].lower() == "false":
                        #             element.attrib[attribute] = "False"

                        # preserve the order as it was previously
                        # workaround for bottom one
                    else:
                        if 'altnames' in def_file.attrib:
                            def_file.attrib.pop('altnames')
                            logger.info("Removed altnames attrib!")
            if not 'steamworkshopid' in def_file.attrib:
                def_file.attrib['steamworkshopid'] = downloaded_mod['ID']
            else:
                if def_file.attrib['steamworkshopid'] != downloaded_mod['ID']:
                    if warnings_as_errors:
                        raise Exception(_("Mod of id:{0} and name: {1} steamid does not match one in workshop link! Remove it if possible").format(downloaded_mod['ID'], downloaded_mod['name']))
                    else:
                        print(_("Mod of id:{0} and name: {1} steamid does not match one in workshop link! Remove it if possible").format(downloaded_mod['ID'], downloaded_mod['name']))
                        # fix?
                        def_file.attrib['steamworkshopid'] = downloaded_mod['ID']
            if not 'corepackage' in def_file.attrib:
                def_file.attrib['corepackage'] = "false"
            if not 'modversion' in def_file.attrib:
                # TODO check what game assumes as default value
                def_file.attrib['modversion'] = "1.0.0"
            if not 'gameversion' in def_file.attrib:
                # TODO check what game assumes as default value
                def_file.attrib['gameversion'] = "1.0"
            if not 'installtime' in def_file.attrib:
                # install time means installation time of a mod https://github.com/Regalis11/Barotrauma/blob/6acac1d143d647ef10250364fe1e71039142539c/Libraries/Facepunch.Steamworks/Structs/UgcItem.cs#L198
                def_file.attrib['installtime'] = str(round(time.time()))
            if not 'expectedhash' in def_file.attrib:
                # we are srewed if this is missing
                if len(def_content) > 0:
                    if warnings_as_errors:
                        raise Exception(_("Mod of id:{0} and name: {1} does not have hash! Remove it if possible").format(downloaded_mod['ID'], downloaded_mod['name']))
                    else:
                        print(_("Mod of id:{0} and name: {1} does not have hash! Remove it if possible").format(downloaded_mod['ID'], downloaded_mod['name']))

            # i dont understand it, this is shit, too hacky
            # TOO BAD!
            def_file.attrib = {k: def_file.attrib[k] for k in desired_order_list if k in def_file.attrib}

            filelist_str = ET.tostring(def_file, encoding="utf-8", method="xml", xml_declaration=True)
            with open(filelist_path, 'wb') as open_file:
                open_file.write(filelist_str)

            # re-encode and fix some incosistencies with using ET
            with open(filelist_path, 'r') as open_file:
                filelist_str = open_file.read()
            filelist_str = filelist_str.replace('version=\'1.0\'', 'version=\"1.0\"')
            filelist_str = filelist_str.replace('encoding=\'utf-8\'', 'encoding=\"utf-8\"')
            # TODO check if encoding into dom is needed
            with open(filelist_path, 'w', encoding="utf-8-sig") as open_file:
                open_file.write(filelist_str)

# set up all default values and paths
# TODO rework
def get_user_perfs():
    options_arr = sys.argv[1:]
    changed_barotrauma_path = False
    changed_tool_path = False
    changed_steamcmd_path = False
    user_perfs = {'collectionmode': False}

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
                        user_perfs['barotrauma'] = os.getcwd()
                        changed_barotrauma_path = True
                    else:
                        user_perfs['barotrauma'] = options_arr[i+1]
                        changed_barotrauma_path = True
                else:
                    user_perfs['barotrauma'] = os.getcwd()
                    changed_barotrauma_path = True
                logger.info("Barotrauma path is set as {0}".format(user_perfs['barotrauma']))
            
            # --toolpath or -t - path to the ModManager Direcotry where script can put all the "cashe" files. set it do default if you dont know where or what you are doing. Must be a path to THE FOLDER.  Does not accept ""
            if options_arr[i] == '--toolpath' or options_arr[i] == '-t':
                if tempval >= 2:
                    if options_arr[i+1] == ".":
                        user_perfs['tool'] = os.getcwd()
                        changed_tool_path = True
                    else:
                        user_perfs['tool'] = options_arr[i+1]
                        changed_tool_path = True
                else:
                    user_perfs['tool'] = os.getcwd()
                    changed_tool_path = True
                logger.info("Tool path is set as {0}".format(user_perfs['tool']))

            # --steamcmdpath or -s - path to your steamcmd or steamcmd.exe. Must be a path to THE FOLDER, not the program itself.  Does not accept ""
            if options_arr[i] == '--steamcmdpath' or options_arr[i] == '-s':
                if tempval >= 2:
                    if options_arr[i+1] == "pwd":
                        if sys.platform == 'win32':
                            user_perfs['steamcmd'] = os.path.join(os.getcwd(), "steamcmd.exe")
                        else:
                            user_perfs['steamcmd'] = os.path.join(os.getcwd(), "steamcmd.sh")
                        changed_steamcmd_path = True
                    else:
                        user_perfs['steamcmd'] = options_arr[i+1]
                        changed_steamcmd_path = True
                else:
                    user_perfs['steamcmd'] = options_arr[i+1]
                    changed_steamcmd_path = True
                logger.info("Steamcmd path set as {0}".format(user_perfs['steamcmd']))

            # TODO '--collection to the documentaton
            if options_arr[i] == '--collection' or options_arr[i] == '-c':
                if tempval >= 3:
                    # TODO check if link is good
                    user_perfs['collection_link'] = options_arr[i+1]
                    user_perfs['collectionmode'] = True
                    user_perfs['localcopy_path_override'] = options_arr[i+2]
                logger.info("Collection link set from command line as {0}".format(user_perfs['collection_link']))
                logger.info("localcopy path override set from command line as {0}".format(user_perfs['localcopy_path_override']))
                
             # TODO add it to the documentaton
            if options_arr[i] == '--performancefix' or options_arr[i] == '-p':
                if tempval >= 1:
                    global addperformacefix
                    user_perfs['addperformacefix'] = True
                logger.info("performance fix enabled from command line!")

            # TODO add it to the documentaton
            if options_arr[i] == '--backup':
                if tempval >= 3:
                    # TODO check if link is good
                    user_perfs['max_saves'] = int(options_arr[i+1])
                    user_perfs['save_dir'] = options_arr[i+2]
                logger.info("save dir for backups is set: {0} and max backup ammout is set to: {1}".format(user_perfs['save_dir'], user_perfs['max_saves']))

    # setting up default values and path handling
    if not changed_barotrauma_path:
        user_perfs['barotrauma'] = default_barotrauma_path
        logger.info("barotrauma path set as default {0}".format(user_perfs['barotrauma']))
    if not os.path.isabs(user_perfs['barotrauma']):
        user_perfs['barotrauma'] = os.path.join(os.getcwd(), user_perfs['barotrauma'])
    if not changed_tool_path:
        user_perfs['tool'] = default_tool_path
        logger.info("tool path set as default {0}".format(user_perfs['tool']))
    if not changed_steamcmd_path:
        user_perfs['steamcmd'] = default_steamcmd_path
        logger.info("steamcmd path set as default {0}".format(user_perfs['steamcmd']))
    # TODO wtf is this
    if default_steamdir_path == "":
        user_perfs['steamdir'] = os.path.join(user_perfs['tool'], "steamdir")
    else:
        user_perfs['steamdir'] = default_steamdir_path
        logger.info("steamdir path overriden {0}".format(user_perfs['steamdir']))


    if 'collection_link' in user_perfs and 'localcopy_path_override' in user_perfs:
        user_perfs['mode'] = "collection"
        logger.info("Running in collection mode")
    else:
        user_perfs['mode'] = "config_player"
        logger.info("Running in config_player mode")


    user_perfs['backup_path'] = os.path.join(user_perfs['tool'], "backup")
    user_perfs['get_dependencies'] = debug_dependencies_functionality
    user_perfs['config_collectionmode_path'] = os.path.join(user_perfs['tool'], "collection_save.txt")
    user_perfs['managedmods_path'] = os.path.join(user_perfs['tool'], "managed_mods.txt")
    user_perfs['old_managedmods'] = get_old_managedmods(user_perfs['managedmods_path'])
    if flush_previous_col:
        if os.path.exists(user_perfs['config_collectionmode_path']):
            os.remove(user_perfs['config_collectionmode_path'])
        logger.info("Collection mode configuration flushed")
    elif os.path.exists(user_perfs['config_collectionmode_path']):
        collection_file = ""
        with open(user_perfs['config_collectionmode_path'], "r", encoding='utf8') as f:
            collection_file = f.read()
        arr = collection_file.split(" ", 1)
        user_perfs['collection_link'] = arr[0]
        user_perfs['localcopy_path_override'] = arr[1]
        user_perfs['mode'] = "collection"
        logger.info("Collection mode enabled from configuration")
    return user_perfs

# yoinked from stackoverflow, works
def robocopysubsttute(root_src_dir, root_dst_dir, replace_option = False):
    if replace_option:
        number_dirs = os.listdir(root_dst_dir)
        for number_dir in number_dirs:
            pattern = "^\d*?$"
            if re.match(pattern, number_dir):
                root_dst_number_dir = os.path.join(root_dst_dir, number_dir)
                if os.path.exists(dst_dir):
                    shutil.rmtree(dst_dir)
                    logger.info("Removed directory {0}".format(dst_dir))
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
            shutil.copy(src_file, dst_dir)
        logger.info("Copied directory {0} to {1}".format(src_dir, dst_dir))

def get_config_player_str(barotrauma_path):
    try:
        config_player_path = os.path.join(barotrauma_path, "config_player.xml")
        with open(config_player_path, "r", encoding='utf8') as f:
            config_player_str = f.read()
    except Exception as e:
        print(_("[ModManager] Could not find the config_player.xml! Check your barotrauma path!"))
        print(_("[ModManager] Barotrauma path: {0}").format(config_player_path))
        print(e)
    return config_player_str 

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
        print(_("[ModManager] Barotrauma path:").format(filelist_path))
        print(e)

    pattern = "<regularpackages>[\s\S]*?<\/regularpackages>"
    regularpackages = re.findall(pattern, filelist_str)

    if len(regularpackages) <= 0:
        logger.info("Couldnt find regularpackages! This probbabbly means the tag is closed (<regularpackages/>)...")
        # patch for </regularpackages>, just in case
        # TODO a bit stupid, so rework it
        filelist_str = filelist_str.replace("<regularpackages/>", "<regularpackages>\n\n\t</regularpackages>")
        filelist_str = filelist_str.replace("<regularpackages />", "<regularpackages>\n\n\t</regularpackages>")
        with open(filelist_path, "w", encoding='utf8') as f:
            f.write(filelist_str)
        pattern = "(?<=<regularpackages>)[\s\S]*?(?=<\/regularpackages>)"
        regularpackages = re.findall(pattern, filelist_str)
        logger.info("Applied <regularpackages/> patch.")
        
    if len(regularpackages) > 0:
        return regularpackages[0]
    else:
        raise Exception("[ModManager] Error during getting modlist from config_player.xml: Could not find regularpackages.\nFix it by removing everything from <regularpackages> to </regularpackages> and with those two, and replacing it with a single <regularpackages/>")

# TODO rework it so its just getting installation time form filelist
def get_recusive_modification_time_of_dir(origin_dir):
    modificationtime = 0
    for src_dir, dirs, files in os.walk(origin_dir):
        for file_ in files:
            new_modificationtime = os.path.getmtime(os.path.join(src_dir, file_))
            if new_modificationtime > modificationtime:
                modificationtime = new_modificationtime
    logger.info("Timestamp for {0} is {1}".format(origin_dir, modificationtime))
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

def get_modlist_regularpackages(regularpackages):
    root = ET.fromstring(regularpackages)
    modlist = []
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
                                modlist.append(mod)

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
def moddownloader(number_of_mod, steamdir_path, location_with_steamcmd):
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
# usage of steamcmd on modlist
def download_modlist(modlist, steamdir_path, location_with_steamcmd):
    numberofupdatedmods = 0
    total_time = 0
    iterator = 0

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
            print(_("[ModManager] Starting steamcmd, Updating mod:{ID:s}: {name:s}").format(**mod), end='')
            if progressbar_functionality == False:
                print("\t" + _("Update Progress: {0}/{1}").format(str(iterator+1), str(len(modlist))), end='')
                if len(modlist) >= 3:
                    if iterator >= 3:
                        # TODO dirty quickfix
                        if completed_file_size > 0:
                            number = int(abs((modlist_file_size - completed_file_size)*(total_time / completed_file_size)))
                            print(" " + _("ETA:{0}:{1}").format(str(number//60), str(number%60)), end='')
            print()
            # TODO make output of steamcmd less spammy/silent
            # TODO instead of steamcmd downloading one mod at the time, make it download all of them in one start of steamcmd using steamcmd scripts or cmd line arguments
            proc = moddownloader(mod["ID"], steamdir_path, location_with_steamcmd)
            for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                line = line.rstrip()
                logger.info("Steamcmd output: {0}".format(line))
                # steam connection check
                if re.match(".*?" + "Connecting anonymously to Steam Public...OK" + ".*?", line):
                    print(_("[ModManger] Connected to steam! Beginning mod download..."))
                    # iterator += 1
                    # bar.update(iterator)
                    # bar.update()
                # starting download
                if re.match(".*?Downloading item " + mod["ID"] + ".*?", line):
                    print(_("[ModManager] Downloading mod: {name:s} ({ID:s})").format(**mod))
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
                print()
            else:
                raise Exception("[ModManager] Steamcmd return code is not 0! That means steamcd had problems!" + str(proc.errors))
        else:
            iterator += 1
            print(_("[ModManager] Skipped mod!: {name:s} ( + {ID:s})").format(**mod))
            # bar.update(1)
            print()
            # iterator += 1
            # bar.update(iterator)
    print()
    return numberofupdatedmods

def print_modlist(modlist):
    print(_("[ModManager] List of mods:"))
    for mod in modlist:
        if str(mod["ID"]) == "2701251094":
            has_performancefix = True
        print(_("[ModManager] {ID:s}: {name:s}").format(**mod))
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

def set_modlist_regularpackages(modlist, localcopy_path_og, barotrauma_path):
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
            raise Exception(_("Collection link INVALID! Re-enable Collection mode."))
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
    new_mods = mods
    for item_to_remove in remove_arr:
        if item_to_remove in new_mods:
            new_mods.remove(item_to_remove)
    return new_mods

def deleting_not_managedmods(not_managedmods):
    for not_managedmod in not_managedmods:
        if os.path.exists(not_managedmod):
            shutil.rmtree(not_managedmod)
    print(_("[ModManager] Removed {0} not managed now mods!").format(str(len(not_managedmods))))

def main(user_perfs):
    logger.info("User perfs: ".format(str(user_perfs)))
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
    steamcmd_downloads = os.path.join(user_perfs['steamdir'], "steamapps", "workshop", "content", "602960")
    config_player_path = os.path.join(user_perfs['barotrauma'], "config_player.xml")
    recomended_configs = os.path.join(user_perfs['tool'], "BestDefaultConfigsTM")
    # "data":
    regularpackages = get_regularpackages(user_perfs['barotrauma'])
    # clean up an creation of steamdir
    if os.path.exists(user_perfs['steamdir']):
        shutil.rmtree(user_perfs['steamdir'])
    os.mkdir(user_perfs['steamdir'])


    # check collection link if it is valid
    if user_perfs['mode'] == "collection":
        collection_site = get_collectionsite(user_perfs['collection_link'])
        isvalid_collection_link = check_collection_link(collection_site)
        logger.info("Collection link validity check is: {0}".format(isvalid_collection_link))
        
            
    if addperformacefix:
        modlist.insert(0, {'name': "Performance Fix", 'ID': "2701251094"})
        logger.info("Perfromance fix has been added to modlist {0}".format(str(modlist)))


    if isvalid_collection_link and user_perfs['mode'] == "collection":
        print(_("[ModManager] Collection mode ENABLED, Downloading collection data (This might take a sec)"))
        modlist.extend(get_modlist_collection_site(collection_site))
    else:
        print(_("[ModManager] Collection mode DISABLED, Downloading data from config_player.xml"))
        if user_perfs['localcopy_path_override'] == "":
            user_perfs['localcopy_path_override'] = get_localcopy_path(regularpackages)
        modlist.extend(get_modlist_regularpackages(regularpackages))


    # TODO remove duplicates once, try NOT to send duplicate requests for data to api
    modlist = get_modlist_data_webapi(modlist)

    
    for mod in modlist:
        if 'dependencies' in mod:
            for dependency in mod['dependencies']:
                if str(dependency) == "2559634234" and requreslua == False:
                    requreslua = True
                if str(dependency) == "2795927223" and requrescs == False:
                    requrescs = True
        if mod['ID'] == '2559634234':
            haslua = True
        if mod['ID'] == '2795927223':
            hascs = True


    # TODO todo changed below condition cuz it disslallowed pwd
    if 'save_dir' in user_perfs and 'max_saves' in user_perfs:
        backupBarotraumaData(user_perfs['barotrauma'], user_perfs['localcopy_path_override'], user_perfs['save_dir'], user_perfs['backup_path'], user_perfs['max_saves'])
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


    for modid in os.listdir(user_perfs['localcopy_path_override']):
        if re.match("^\d*?$", modid):
            modlist_localcopy.append(modid)

      
    # TODO idk why im doing this 
    # Path fixing
    if not os.path.isabs(user_perfs['tool']):
        user_perfs['tool'] = os.path.join(os.getcwd(), user_perfs['tool'])
    if not os.path.isabs(user_perfs['steamdir']):
        user_perfs['steamdir'] = os.path.join(os.getcwd(), user_perfs['steamdir'])
    if not os.path.isabs(user_perfs['localcopy_path_override']):
        user_perfs['localcopy_path_override'] = os.path.join(os.getcwd(), user_perfs['localcopy_path_override'])
    user_perfs['steamdir'] = os.path.realpath(user_perfs['steamdir'])


    managed_mods = get_managedmods(modlist, user_perfs['localcopy_path_override'])
    not_managedmods = get_not_managedmods(user_perfs['old_managedmods'], managed_mods)


    # re-create config_player
    new_regularpackages = set_modlist_regularpackages(modlist, user_perfs['localcopy_path_override'], user_perfs['barotrauma'])
    with open(config_player_path, "r", encoding='utf8') as f:
        filelist_str = f.read()
    filelist_str = filelist_str.replace(regularpackages, new_regularpackages)
    with open(config_player_path, "w", encoding='utf8') as f:
        f.write(filelist_str)
    # TODO NEED to take a look how to post comments with ET, and how to format it accordingly
    # set_mods_config_player(modlist, localcopy_path, barotrauma_path)


    # save configs
    if isvalid_collection_link and user_perfs['mode'] == "collection":
        with open(user_perfs['config_collectionmode_path'], "w", encoding='utf8') as f:
            f.write(user_perfs['collection_link'] + " " + user_perfs['localcopy_path_override'])
    save_managedmods(managed_mods, user_perfs['managedmods_path'])


    # lastupdated functionality
    if user_perfs['mode'] == "collection":
        up_to_date_mods = get_up_to_date_mods(modlist, user_perfs['localcopy_path_override'])
        modlist = remove_up_to_date_mods(modlist, up_to_date_mods)


    # main part, running moddlownloader
    nr_updated_mods = download_modlist(modlist, user_perfs['steamdir'], user_perfs['steamcmd'])
    print("\n")
    print(_("[ModManager] Skipping download of {0} Already up to date Mods. (if any issues arrise please remove every mod from your localcopy directory)").format(str(len(up_to_date_mods))))


    # config backup and conservation
    backup_option(recomended_configs, steamcmd_downloads)
    backup_option(user_perfs['localcopy_path_override'], steamcmd_downloads)


    deleting_not_managedmods(not_managedmods)


    # actually moving mods to localcopy
    for mod in modlist:
        mod_path = os.path.join(steamcmd_downloads, mod['ID'])
        FIX_barodev_moment(mod, mod_path)
        robocopysubsttute(mod_path, os.path.join(user_perfs['localcopy_path_override'], mod['ID']))


    # finishing anc cleaning up
    # removing steamdir because steamcmd is piece of crap and it sometimes wont download mod if its in directory
    shutil.rmtree(user_perfs['steamdir'])
    if len(up_to_date_mods) <= nr_updated_mods:
        print(_("[ModManager] All {0} Mods have been updated").format(str(nr_updated_mods)))
    else:
        print(_("[ModManager] All Mods were up to date!"))


    # accessing filelists of mods
    for mod in modlist:
        # checking if mod is pure server-side or client side
        if is_pure_lua_mod(os.path.join(user_perfs['localcopy_path_override'], mod['ID'])):
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
    logger.info("Number of mods: {0}".format(numberofmods_minuslua - number_of_pure_lua_mods))
    if numberofmods_minuslua - number_of_pure_lua_mods >= 30 and not disablewarnings:
        sys.stdout.write("\033[1;31m")
        print(_("[ModManager] I STRONGLY ADVISE TO SHORTEN YOUR MODLIST! It is very rare for players to join public game that has a lot of mods."))
        print(_("[ModManager] Please shorten your modlist by removing unnesesary mods, or use group of mods inside of one package."))
        sys.stdout.write("\033[0;0m")
        time.sleep(30)
    elif numberofmods_minuslua - number_of_pure_lua_mods >= 20 and not disablewarnings:
        sys.stdout.write("\033[1;31m")
        print(_("[ModManager] I advise to shorten your modlist! It is very rare for players to join public game that has a lot of mods."))
        print(_("[ModManager] Please shorten your modlist by removing unnesesary mods, or use group of mods inside of one package."))
        sys.stdout.write("\033[0;0m")
        time.sleep(20)

if __name__ == '__main__':
    print(_("Wellcome to ModManager script!"))
    # gotta have it here even if it pains me
    user_perfs = get_user_perfs()
    logger.info("Aqquired user perfs")
    while(True):
        if os.path.exists(os.path.join(user_perfs['tool'], "collection_save.txt")):
            print(_("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands."))
            print(_("[ModManager] Steam collection mode enabled! Disable by entering collection sub-menu."))
            print(_("[ModManager] Do you want to update that collection of mods? ((Y)es / (n)o): "))
        else: 
            print(_("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands."))
            print(_("[ModManager] Steam collection mode disabled! Enable by entering collection sub-menu."))
            print(_("[ModManager] Do you want to update mods? ((Y)es / (n)o): "))
        user_command = input().lower()
        if user_command == "yes" or user_command == "y":
            main(user_perfs)
            break
        elif user_command == "no" or user_command == "n":
            break
        elif user_command == "collection" or user_command == "c":
            print(_("[ModManager] Provide an collection link then press enter, or if you want to disable previously enabled collection mode, type 'n' then enter: "))
            collection_url = input()
            if collection_url != "n":
                print(_("[ModManager] Provide an localcopy path (if you dont know what to input, type 'LocalMods') then press enter: "))
                if not 'localcopy_path_override' in user_perfs:
                    user_perfs['localcopy_path_override'] = input()
                    # TODO collection check, if link is valid
                    user_perfs['collection_link'] = collection_url
                    user_perfs['collectionmode'] = True
            else:
                if 'collection_link' in user_perfs:
                    user_perfs.pop('collection_link')
                if 'collectionmode' in user_perfs:
                    user_perfs.pop('collectionmode')
            flush_previous_col = True
            main(user_perfs)
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
            print(_("[ModManager] Provide a valid anwser: \"y\" or \"yes\" / \"n\" or \"no\""))