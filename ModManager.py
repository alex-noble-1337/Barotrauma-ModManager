#!/usr/bin/env python3
import sys
import os

# CONFIGURATION if you dont wanna use arguments:
default_barotrauma_path = os.getcwd()
default_tool_path = os.path.dirname(sys.argv[0])
default_steamcmd_path = "steamcmd"
default_steamdir_path = "/home/milord/testdirectory/steamdir"
default_addperformancefix = False

# debug
disablewarnings = False
# TODO Still testing and working on it
flush_previous_col = False
progressbar_functionality = False
debug_set_forced_cs = False
debug_dependencies_functionality = False
logging_on = True
warnings_as_errors = False

# My "Quality" code
# my IT teacher would kill me if she saw this...
available_modes = ["config_player", "collection"]
from BaroRewrites import content_types
from BaroRewrites import content_types_binary
configs = ['barotrauma', 'steamcmd', 'collection_link', 'mode',
           'localcopy_path', 'addperformancefix', 'max_saves', 'save_dir']

# TODO change this to import only individual commands
import os
import shutil
import re
from functools import reduce
import time
import datetime
import xml.etree.ElementTree as ET

import logging
import logging.config
logger = logging.getLogger(__name__)
import gettext
_ = gettext.gettext

# For nameing of logs
current_time = datetime.datetime.now()
current_time = current_time.replace(second=0, microsecond=0)
current_time = str(current_time)[0:-3]

try:
    import requests
    import json
except ImportError:
    print("Trying to Install required module: requests\n")
    os.system('python3 -m pip install requests json')

# load submodules
from BackupUtil import backup_option
import SteamIOMM
from BackupUtil import backupBarotraumaData
from ConfigRecoder import modlist_to_ModListsXml
import BaroRewrites


# set up all default values and paths
# TODO rework
def get_user_perfs():
    options_arr = sys.argv[1:]
    # stuff not in config: toolpath - configuration path (and path of cashe for now)
    # TODO defaults defined when user_perfs is created
    # configuration overrides, done via command line paramenters
    # then load config files
    # defaults:
    user_perfs = {'locale': 'en', 'old_managedmods': [], 'tool': default_tool_path,
                  'barotrauma': default_barotrauma_path, 'steamcmd': default_steamcmd_path,
                  'addperformancefix': default_addperformancefix}
    logging_config = {}
    logger.info("Default user_perfs are {0}".format(user_perfs))
    # toolpath or config path
    #  Must be a path to THE FOLDER.  Does not accept "" use "." instead
    for i in range(len(options_arr)):
        if options_arr[i] == '--toolpath' or options_arr[i] == '-t':
            # requires 1 argument
            if i + 1 >= len(options_arr):
                if options_arr[i+1] == ".":
                    user_perfs['tool'] = os.getcwd()
                    logger.info("Tool path is set as {0}".format(user_perfs['tool']))
                else:
                    user_perfs['tool'] = options_arr[i+1]
                    logger.info("Tool path is set as {0}".format(user_perfs['tool']))
    # TODO soon to replace toolpath
    user_perfs['config_path'] = os.path.join(user_perfs['tool'], "config.xml")
    logger.debug("config_path is set as {0}".format(user_perfs['config_path']))


    if os.path.exists(user_perfs['config_path']):
        with open(user_perfs['config_path'] , 'r', encoding="utf8") as f:
            config_xml = ET.fromstring(f.read())
        for val in configs:
            if val in configs and val in config_xml.attrib:
                if config_xml.attrib[val] != '':
                    if config_xml.attrib[val] == "True":
                        user_perfs[val] = True
                    elif config_xml.attrib[val] == "False":
                        user_perfs[val] = False
                    else:
                        user_perfs[val] = config_xml.attrib[val]
        # TODO get modlist(oldmanagedmods) in format same as ModLists(barotrauma generated)
        if 'localcopy_path' in user_perfs:
            for subconfig in config_xml:
                if subconfig.tag.lower() == 'mods':
                    for mod_xml in subconfig:
                        if mod_xml.tag in ['Workshop', 'Local']:
                            # TODO get type of its workshop from tag
                            mod = {'path': os.path.join(user_perfs['localcopy_path'], mod_xml.attrib['id']),
                                   'type': mod_xml.tag, 'id': mod_xml.attrib['id']}
                            # TODO get name from name attrib
                            if 'name' in mod_xml.attrib:
                                mod['name'] = mod_xml.attrib['name']
                            # TODO get id rather than full path
                            user_perfs['old_managedmods'].append(mod)
    
    # Logging
    if logging_on:
        # logging enabling and configuaration
        level = 'DEBUG'
        max_logs = 12
        logfile_path = os.path.join(user_perfs['tool'], "ModManagerLogs", current_time  + ".log")
        os.makedirs(os.path.dirname(logfile_path), exist_ok=True)
        filenames = os.listdir(os.path.dirname(logfile_path))
        logs = []
        for file_ in filenames:
            if file_[-4:] == ".log":
                logs.append(file_)
        logs = sorted(logs)
        if max_logs < len(logs):
            logs_todel = logs[0:len(logs) - max_logs]
            for log_todel in logs_todel:
                os.remove(os.path.join(os.path.dirname(logfile_path), log_todel))
        logging_config = { 
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': { 
                'standard': { 
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
            },
            'handlers': {
                'default': {
                    'level': level,
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler',
                },
                'file_handler': {
                    'level': level,
                    'filename': logfile_path,
                    'class': 'logging.FileHandler',
                    'formatter': 'standard'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['file_handler'],
                    'level': level,
                    'propagate': True
                },
            }
        }
        logging.config.dictConfig(logging_config)
        logging.disable(logging.NOTSET)

    # TODO go over this again, handing of command line arguments
    if len(options_arr) >= 1:
        for i in range(0,len(options_arr)):
            tempval = 1
            for j in range(i + 1,len(options_arr)):
                if (options_arr[j] == '--barotraumapath' or options_arr[j] == '-b' or options_arr[j] == '--toolpath' or options_arr[j] == '-t' or options_arr[j] == '--steamcmdpath' or
                   options_arr[j] == '-s' or options_arr[j] == '--collection' or options_arr[j] == '-c' or options_arr[j] == '--performancefix' or options_arr[j] == '-p' or
                   options_arr[j] == '--backup'):
                    break
                else:
                    tempval += 1

            # override installation dir
            if options_arr[i] == '--installdir' or options_arr[i] == '-o':
                if tempval >= 3:
                    user_perfs['localcopy_path_override'] = options_arr[i+1]
                    logger.info("Localcopy Path Override set {0}".format(user_perfs['localcopy_path_override']))

            # --barotraumapath or -b - path to your barotrauma install. Must be a path to THE FOLDER, not the program itself. Does not accept ""
            if options_arr[i] == '--barotraumapath' or options_arr[i] == '-b':
                if tempval >= 2:
                    if options_arr[i+1] == "pwd":
                        user_perfs['barotrauma'] = os.getcwd()
                    else:
                        user_perfs['barotrauma'] = options_arr[i+1]
                else:
                    user_perfs['barotrauma'] = os.getcwd()
                logger.info("Barotrauma path is set as {0}".format(user_perfs['barotrauma']))

            # --steamcmdpath or -s - path to your steamcmd or steamcmd.exe. Must be a path to THE FOLDER, not the program itself.  Does not accept ""
            if options_arr[i] == '--steamcmdpath' or options_arr[i] == '-s':
                if tempval >= 2:
                    if options_arr[i+1] == "pwd":
                        if sys.platform == 'win32':
                            user_perfs['steamcmd'] = os.path.join(os.getcwd(), "steamcmd.exe")
                        else:
                            user_perfs['steamcmd'] = os.path.join(os.getcwd(), "steamcmd.sh")
                    else:
                        user_perfs['steamcmd'] = options_arr[i+1]
                else:
                    user_perfs['steamcmd'] = options_arr[i+1]
                logger.info("Steamcmd path set as {0}".format(user_perfs['steamcmd']))

            # TODO '--collection to the documentaton
            if options_arr[i] == '--collection' or options_arr[i] == '-c':
                if tempval >= 3:
                    # TODO check if link is good
                    user_perfs['collection_link'] = options_arr[i+1]
                    user_perfs['localcopy_path'] = options_arr[i+2]
                logger.info("Collection link set from command line as {0}".format(user_perfs['collection_link']))
                logger.info("localcopy path override set from command line as {0}".format(user_perfs['localcopy_path']))

             # TODO add it to the documentaton
            if options_arr[i] == '--performancefix' or options_arr[i] == '-p':
                if tempval >= 1:
                    user_perfs['addperformancefix'] = True
                logger.info("performance fix enabled from command line!")

            # TODO add it to the documentaton
            if options_arr[i] == '--backup':
                if tempval >= 3:
                    # TODO check if link is good
                    user_perfs['max_saves'] = int(options_arr[i+1])
                    user_perfs['save_dir'] = options_arr[i+2]
                logger.info("save dir for backups is set: {0} and max backup ammout is set to: {1}".format(user_perfs['save_dir'], user_perfs['max_saves']))

    # setting up default values and path handling
    if not os.path.isabs(user_perfs['barotrauma']):
        user_perfs['barotrauma'] = os.path.abspath(user_perfs['barotrauma'])
    # TODO wtf is this
    if default_steamdir_path == "":
        user_perfs['steamdir'] = os.path.join(user_perfs['tool'], "steamdir")
    else:
        user_perfs['steamdir'] = default_steamdir_path
        logger.info("steamdir path overriden {0}".format(user_perfs['steamdir']))


    if 'collection_link' in user_perfs and 'localcopy_path' in user_perfs:
        user_perfs['mode'] = "collection"
        logger.info("Running in collection mode")
    else:
        if not 'mode' in user_perfs:
            user_perfs['mode'] = "config_player"
        elif not user_perfs['mode'] in available_modes:
            user_perfs['mode'] = "config_player"
        logger.info("Running in config_player mode")

    # default backup path
    user_perfs['backup_path'] = os.path.join(user_perfs['tool'], "backup")
    # TODO not yet finished, extemly slow due to being webscraping
    user_perfs['get_dependencies'] = debug_dependencies_functionality
    # user_perfs['config_collectionmode_path'] = os.path.join(user_perfs['tool'], "collection_save.txt")
    # user_perfs['managedmods_path'] = os.path.join(user_perfs['tool'], "managed_mods.txt")
    if flush_previous_col:
        user_perfs.pop('collection_link')
        user_perfs.pop('localcopy_path')
        logger.info("Collection mode configuration flushed")
    elif 'collection_link' in user_perfs and user_perfs['mode'] == "collection" and 'localcopy_path' in user_perfs:
        logger.info("Collection mode enabled from perfs, collection_link:{0}, mode:{1}, localcopy_path:{2}"
            .format(user_perfs['collection_link'], user_perfs['mode'], user_perfs['localcopy_path']))
    if 'localcopy_path_override' in user_perfs:
        user_perfs['localcopy_path'] = user_perfs['localcopy_path_override']
        logger.info("localcopy path override set as {0}".format(user_perfs['localcopy_path']))
        
    return user_perfs
def save_user_perfs(managed_mods, user_perfs, corecontentpackage = "Vanilla"):
    # managed_mods_str = ""
    # for managed_mod in managed_mods:
    #     managed_mods_str += managed_mod + "\n"
    # with open(managed_mods_path, "w", encoding='utf8') as f:
    #     f.write(managed_mods_str)
    config_xml = ET.Element("config")
    for val in configs:
        if val in user_perfs:
            config_xml.attrib[val] = str(user_perfs[val])
        else:
            config_xml.attrib[val] = ""
    
    config_xml.append(modlist_to_ModListsXml(managed_mods, corecontentpackage))
    ET.indent(config_xml, space="\t", level=0)
    with open(user_perfs['config_path'], 'wb') as open_file:
        open_file.write(ET.tostring(config_xml))

def get_config_player_str(barotrauma_path):
    try:
        config_player_path = os.path.join(barotrauma_path, "config_player.xml")
        with open(config_player_path, "r", encoding='utf8') as f:
            config_player_str = f.read()
    except Exception as e:
        print(_("[ModManager] Could not find the config_player.xml! Check your barotrauma path!"))
        print(_("[ModManager] Barotrauma path: {0}").format(config_player_path))
        print(e)
        logger.critical("Fatal Exception occured!\n" + e)
    return config_player_str 
def get_modlist_regularpackages(regularpackages,localcopy_path):
    root = ET.fromstring(regularpackages)
    modlist = []
    for element in root:
        if element.tag == "package":
            mod = {'path': os.path.dirname(element.attrib['path'])}
            id_test = re.findall("\d*?$", mod['path'])
            if len(id_test) > 0:
                mod['id'] = id_test[0]
                mod['type'] = "Workshop"
            else:
                mod['type'] = "Local"
            modlist.append(mod)

    # reason i need to look in filelist is because of:
    #   - shit barotrauma devs (look up whole problem when you update modname on steam without updating the filelist.xml, this makes comments in filelist shit and not useful)
    #   - i can just get non-installed mods name's via api 
    for mod in modlist:
        if os.path.isabs(mod['path']):
            filelist_path = os.path.join(mod['path'], "filelist.xml")
        else:
            filelist_path = os.path.join(os.path.abspath(mod['path']), "filelist.xml")
        if os.path.exists(filelist_path):
            with open(filelist_path, 'r') as open_file:
                mod_filelist_str = open_file.read()
            mod_filelist = ET.fromstring(mod_filelist_str)
            if mod_filelist.tag.lower() == "contentpackage":
                mod['name'] = mod_filelist.attrib['name']
                if 'installtime' in mod_filelist.attrib:
                    mod['installtime'] = int(mod_filelist.attrib['installtime'])
                    mod['modificationtime'] = int(mod_filelist.attrib['installtime'])
        
    return modlist
# get from config_player.xml, everything inside <regularpackages/> </regularpackages>
def get_regularpackages(barotrauma_path):
    # trying to access filelist
    try:
        filelist_path = os.path.join(barotrauma_path, "config_player.xml")
        with open(filelist_path, "r", encoding='utf8') as f:
            filelist_str = f.read()
    except Exception as e:
        print(_("[ModManager] Could not find the config_player.xml! Check your barotrauma path!"))
        print(_("[ModManager] Barotrauma path:{0}").format(filelist_path))
        logger.critical("Fatal Exception occured!\n" + str(e))
        raise Exception("Fatal Exception occured!\n" + str(e))

    pattern = "<regularpackages>[\s\S]*?<\/regularpackages>"
    regularpackages = re.findall(pattern, filelist_str)

    if len(regularpackages) <= 0:
        logger.warning("Couldnt find regularpackages! This probbabbly means the tag is closed (<regularpackages/>)...")
        # patch for </regularpackages>, just in case
        pattern = "<regularpackages.*?/>"
        regularpackages = re.findall(pattern, filelist_str)

    if len(regularpackages) > 0:
        return regularpackages[0]
    else:
        logger.critical(("[ModManager] Error during getting modlist from config_player.xml: Could not find regularpackages.",
                        "\nFix it by removing everything from <regularpackages> to </regularpackages> and with those two, and replacing it with a single <regularpackages/>"))
        raise Exception(_(("[ModManager] Error during getting modlist from config_player.xml: Could not find regularpackages.",
                         "\nFix it by removing everything from <regularpackages> to </regularpackages> and with those two, and replacing it with a single <regularpackages/>")))
def get_localcopy_path(filelist_str):
    localcopy_path = ""
    root = ET.fromstring(filelist_str)
    if root.tag == "regularpackages":
        if root.text != None:
            for package in root:
                # werid, BUT just in case...
                if package.tag == 'package':
                    localcopy_path = os.path.dirname(os.path.dirname(package.attrib['path']))
                    break
    return localcopy_path
# config_player.xml output ET version TODO NEED to take a look how to post comments with ET, and how to format it accordingly
def TODOset_mods_config_player(modlist, localcopy_path, barotrauma_path):
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
                    new_package.attrib['path'] = localcopy_path + "/" + mod['id'] + "/filelist.xml"
                    new_package.tail = '\n      \n      '
                    new_package.text = None
                    
    config_player_str = ET.tostring(root, encoding='utf-8', method='xml')

    with open(os.path.join(barotrauma_path, "config_player.xml"), 'wb') as open_file:
        open_file.write(config_player_str)
def set_modlist_regularpackages(modlist, localcopy_path_og, barotrauma_path):
    regularpackages_new = "<regularpackages>\n"
    # print new
    for mod in modlist:
        #  if barotrauma_path is inside of 
        temp_mod_path = mod['path']
        if temp_mod_path.count(barotrauma_path) > 0:
            temp_mod_path = temp_mod_path.replace(barotrauma_path + os.sep, "")

        if sys.platform == "win32":
            temp_mod_path = temp_mod_path.replace("\\", "/")
        else:
            temp_mod_path = temp_mod_path

        modname_formatted = mod['name'].replace("--", "- -")
        regularpackages_new += "      <!--" + modname_formatted + "-->\n"
        regularpackages_new += "      <package\n"
        regularpackages_new += "        path=\"" + temp_mod_path + "/filelist.xml" + "\"/>\n"
    regularpackages_new += "    </regularpackages>"
    return regularpackages_new

def print_modlist(modlist):
    print(_("[ModManager] List of mods:"))
    for mod in modlist:
        if str(mod['id']) == "2701251094":
            has_performancefix = True
        print(_("[ModManager] {id:s}: {name:s}").format(**mod))
    print("\n")
    print("\n")
def remove_duplicates(modlist):
    toremove = []
    modlist_copy = modlist
    modlist_copy = sorted(modlist_copy, key=lambda mod: mod['id'])
    for i in range(1, len(modlist_copy)):
        if modlist_copy[i]['id'] == modlist_copy[i-1]['id']:
            toremove.append(modlist_copy[i])    
    modlist.reverse()
    for remove in toremove:
        if remove in modlist:
            modlist.remove(remove)
    modlist.reverse()
    return modlist
def get_managed_modlist(modlist, localcopy_path_og):
    managed_mods = []
    for mod in modlist:
        mod_b = mod
        if not 'path' in mod_b:
            if 'id' in mod_b:
                mod_b['path'] = os.path.join(localcopy_path_og, mod_b['id'])
            else:
                mod_b['path'] = os.path.join(localcopy_path_og, mod_b['name'])
        if not 'type' in mod_b:
            pattern = "^\d*?$"
            if re.match(pattern, str(os.path.basename(mod['path']))):
                mod_b['type'] = "Workshop"
            else:
                mod_b['type'] = "Local"
        managed_mods.append(mod_b)
    return managed_mods
def get_not_managed_modlist(old_managed_modlist, managed_modlist):
    not_managed_modlist = old_managed_modlist
    # removeing mods that exist in modlist
    # TODO sloooooow
    for modwithdir in managed_modlist:
        for old_modwithdir in old_managed_modlist:
            path_mod = modwithdir['path']
            path_old_mod = old_modwithdir['path']
            if not os.path.isabs(path_mod):
                path_mod = os.path.abspath(path_mod)
            if not os.path.isabs(path_old_mod):
                path_old_mod = os.path.abspath(path_mod)
            if path_mod == path_old_mod:
                not_managed_modlist.remove(old_modwithdir)
    return not_managed_modlist
def deleting_not_managed_modlist(not_managed_modlist):
    removed_count = 0
    for not_managedmod in not_managed_modlist:
        if os.path.exists(not_managedmod['path']):
            shutil.rmtree(not_managedmod['path'])
            removed_count += 1
    print(_("[ModManager] Removed {0} not managed now mods!").format(str(removed_count)))
# check, both if they exist and if they are up to date
# made it that way to...uhhhh idk
# also appends modificationtime if not present
def get_up_to_date_mods(mods, localcopy_path):
    remove_arr = []
    # TODO current slowing time is about 
    # TODO lastupdated skip for windows and mac
    for mod in mods:
        if 'LastUpdated' in mod:
            if os.path.exists(mod['path']):
                if not 'modificationtime' in mod:
                    mod['modificationtime'] = get_recusive_modification_time_of_dir(os.path.join(localcopy_path, mod['id']))
                # conversion into time struct
                mod['modificationtime'] = time.localtime(mod['modificationtime'])
                test = time.strftime('%d %b, %Y @ %I:%M%p', mod['modificationtime'])
                # greater not equal because of possible steam errors
                if  mod['modificationtime'] > mod['LastUpdated'] and os.path.exists(os.path.join(mod['path'], "filelist.xml")):
                    # TODO check if all xml files are matching what is in filelist
                    # TODO thats a lazy way to do it
                    remove_arr.append(mod)
    return remove_arr
def is_serverside_mod(mod_path: str):
    pure_lua_mod = False
    if os.path.exists(os.path.join(mod_path, "filelist.xml")):
        with open(os.path.join(mod_path, "filelist.xml"), "r", encoding='utf8') as f:
            filelist_str = f.read()
        filelist = ET.fromstring(filelist_str)
        xmlitems = 0
        for mod in filelist:
            if mod.tag.lower() in content_types or mod.tag.lower() in content_types_binary:
                xmlitems += 1
        if xmlitems <= 0:
            pure_lua_mod = True
    return pure_lua_mod

# TODO name
# requres lastupdated value in mod object, return mods array that has only mods that requre update returns all items that arent in remove_arr
def remove_all_occurences_from_arr(arr, remove_arr):
    new_arr = arr
    for item_to_remove in remove_arr:
        if item_to_remove in new_arr:
            new_arr.remove(item_to_remove)
    return new_arr
# TODO rework it so its just getting installation time form filelist used to get update time of a mod (directory)
def get_recusive_modification_time_of_dir(origin_dir):
    modificationtime = 0
    for src_dir, dirs, files in os.walk(origin_dir):
        for file_ in files:
            new_modificationtime = os.path.getmtime(os.path.join(src_dir, file_))
            if new_modificationtime > modificationtime:
                modificationtime = new_modificationtime
    logger.debug("Timestamp for {0} is {1}".format(origin_dir, modificationtime))
    return modificationtime
def sanitize_pathstr(path):
    path = str(path)
    path = path.replace(" ", "\\ ")
    return path
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
                    logger.debug("Removed directory {0}".format(dst_dir))
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
        logger.debug("Copied directory {0} to {1}".format(src_dir, dst_dir))


def modmanager(user_perfs):
    logger.info("User perfs: {0}".format(str(user_perfs)))
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
    # "data":
    regularpackages = get_regularpackages(user_perfs['barotrauma'])
    # clean up an creation of steamdir
    if os.path.exists(user_perfs['steamdir']):
        shutil.rmtree(user_perfs['steamdir'])
    os.makedirs(user_perfs['steamdir'] ,exist_ok = True)
    if 'localcopy_path' in user_perfs and 'localcopy_path_override' in user_perfs:
        user_perfs['localcopy_path'] = user_perfs['localcopy_path_override']
        logger.info("localcopy path override set as {0}".format(user_perfs['localcopy_path']))
        if not os.path.isabs(user_perfs['localcopy_path']):
            user_perfs['localcopy_path'] = os.path.abspath(user_perfs['localcopy_path'])

    # check collection link if it is valid
    isvalid_collection_link = False
    if 'collection_link' in user_perfs:
        collection_site = SteamIOMM.get_collectionsite(user_perfs['collection_link'])
        isvalid_collection_link = SteamIOMM.check_collection_link(collection_site)
        logger.info("Collection link validity check is: {0}".format(isvalid_collection_link))
    
            
    if user_perfs['addperformancefix']:
        modlist.insert(0, {'name': "Performance Fix", 'id': "2701251094"})
        logger.debug("Perfromance fix has been added to modlist {0}".format(str(modlist)))


    if isvalid_collection_link and user_perfs['mode'] == "collection":
        print(_("[ModManager] Collection mode ENABLED, Downloading collection data (This might take a sec)"))
        modlist.extend(SteamIOMM.get_modlist_collection_site(collection_site))
    else:
        print(_("[ModManager] Collection mode DISABLED, Downloading data from config_player.xml"))
        if not 'localcopy_path' in user_perfs:
            user_perfs['localcopy_path'] = get_localcopy_path(regularpackages)
        if user_perfs['localcopy_path'] == "":
            user_perfs['localcopy_path'] = get_localcopy_path(regularpackages)
        if 'localcopy_path_override' in user_perfs:
            user_perfs['localcopy_path'] = user_perfs['localcopy_path_override']
        if os.path.isabs(user_perfs['localcopy_path']):
            user_perfs['localcopy_path'] = os.path.abspath(user_perfs['localcopy_path'])
        modlist.extend(get_modlist_regularpackages(regularpackages, user_perfs['localcopy_path']))


    # TODO remove duplicates once, try NOT to send duplicate requests for data to api
    modlist = SteamIOMM.get_modlist_data_webapi(modlist)

    
    for mod in modlist:
        if 'dependencies' in mod:
            for dependency in mod['dependencies']:
                if str(dependency) == "2559634234" and requreslua == False:
                    requreslua = True
                if str(dependency) == "2795927223" and requrescs == False:
                    requrescs = True
        if mod['id'] == '2559634234':
            haslua = True
        if mod['id'] == '2795927223':
            hascs = True


    # TODO todo changed below condition cuz it disslallowed pwd
    if 'save_dir' in user_perfs and 'max_saves' in user_perfs:
        backupBarotraumaData(user_perfs['barotrauma'], user_perfs['localcopy_path'], user_perfs['save_dir'], user_perfs['backup_path'], user_perfs['max_saves'])
    if requrescs and not hascs:
        # TODO kind hacky way to do this
        temp_luacs = [{'name': "Cs For Barotrauma", 'id': "2795927223"}]
        temp_luacs = get_modlist_data_webapi(temp_luacs)
        modlist.extend(temp_luacs)


    modlist = remove_duplicates(modlist)


    # modless?
    if len(modlist) == 0:
        not_managedmods = get_not_managed_modlist(user_perfs['old_managedmods'], modlist)
        deleting_not_managed_modlist(not_managedmods)
        save_user_perfs(modlist, user_perfs)
        print(_("[ModManager] No mods detected"))
        return 
    else:
        numberofmods_minuslua = len(modlist) - int(haslua) - int(hascs)
        print_modlist(modlist)


    for modid in os.listdir(user_perfs['localcopy_path']):
        if re.match("^\d*?$", modid):
            modlist_localcopy.append(modid)

      
    # TODO idk why im doing this 
    # Path fixing
    if not os.path.isabs(user_perfs['tool']):
        user_perfs['tool'] = os.path.join(os.getcwd(), user_perfs['tool'])
    if not os.path.isabs(user_perfs['steamdir']):
        user_perfs['steamdir'] = os.path.join(os.getcwd(), user_perfs['steamdir'])
    if not os.path.isabs(user_perfs['localcopy_path']):
        user_perfs['localcopy_path'] = os.path.abspath(user_perfs['localcopy_path'])
    user_perfs['steamdir'] = os.path.realpath(user_perfs['steamdir'])


    modlist = get_managed_modlist(modlist, user_perfs['localcopy_path'])
    not_managedmods = get_not_managed_modlist(user_perfs['old_managedmods'], modlist)
    buffer = []
                


    # re-create config_player
    new_regularpackages = set_modlist_regularpackages(modlist, user_perfs['localcopy_path'], user_perfs['barotrauma'])
    with open(config_player_path, "r", encoding='utf8') as f:
        filelist_str = f.read()
    filelist_str = filelist_str.replace(regularpackages, new_regularpackages)
    with open(config_player_path, "w", encoding='utf8') as f:
        f.write(filelist_str)


    # save configs
    # if isvalid_collection_link and user_perfs['mode'] == "collection":
    #     with open(user_perfs['config_collectionmode_path'], "w", encoding='utf8') as f:
    #         f.write(user_perfs['collection_link'] + " " + user_perfs['localcopy_path'])
    save_user_perfs(modlist, user_perfs)


    # lastupdated functionality
    up_to_date_mods = []
    up_to_date_mods = get_up_to_date_mods(modlist, user_perfs['localcopy_path'])
    modlist_to_update = remove_all_occurences_from_arr(modlist, up_to_date_mods)


    # main part, running moddlownloader
    nr_updated_mods = SteamIOMM.download_modlist(modlist_to_update, user_perfs['steamdir'], user_perfs['steamcmd'])
    print("\n")
    print(_("[ModManager] Skipping download of {0} Already up to date Mods. (if any issues arrise please remove every mod from your localcopy directory)")
            .format(str(len(up_to_date_mods))))


    # config backup and conservation
    backup_option(os.path.join(user_perfs['tool'], "BestDefaultConfigsTM"), steamcmd_downloads)
    backup_option(user_perfs['localcopy_path'], steamcmd_downloads)


    deleting_not_managed_modlist(not_managedmods)


    # actually moving mods to localcopy
    for mod in modlist_to_update:
        mod_path = os.path.join(steamcmd_downloads, mod['id'])
        BaroRewrites.FIX_barodev_moment(mod, mod_path)
        robocopysubsttute(mod_path, os.path.join(user_perfs['localcopy_path'], mod['id']))
    
    # TODO installed_mods
    for mod in modlist:
        if os.path.exists(mod['path']):
            BaroRewrites.FIX_barodev_moment(mod, mod['path'])


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
        if is_serverside_mod(os.path.join(user_perfs['localcopy_path'], mod['id'])):
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
        print("\033[1;31m" + _("[ModManager] I STRONGLY ADVISE TO SHORTEN YOUR MODLIST! It is very rare for players to join public game that has a lot of mods.") + "\033[0;0m")
        print("\033[1;31m" + _("[ModManager] Please shorten your modlist by removing unnesesary mods, or use group of mods inside of one package.") + "\033[0;0m")
        time.sleep(30)
    elif numberofmods_minuslua - number_of_pure_lua_mods >= 20 and not disablewarnings:
        print("\033[1;31m" + _("[ModManager] I advise to shorten your modlist! It is very rare for players to join public game that has a lot of mods.") + "\033[0;0m")
        print("\033[1;31m" + _("[ModManager] Please shorten your modlist by removing unnesesary mods, or use group of mods inside of one package.") + "\033[0;0m")
        time.sleep(20)

def main():
    print(_("Wellcome to ModManager script!"))
    # gotta have it here even if it pains me
    user_perfs = get_user_perfs()
    # TEST
    # user_perfs['localcopy_path_override'] = "LocalMods"
    logger.info("Aqquired user perfs: {0}".format(str(user_perfs)))
    while(True):
        if 'collection_link' in user_perfs and 'localcopy_path' in user_perfs:
            print(_("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands."))
            print(_("[ModManager] Steam collection mode enabled! Disable by entering collection sub-menu."))
            print(_("[ModManager] Do you want to update that collection of mods? ((Y)es / (n)o): "))
            if 'localcopy_path_override' in user_perfs:
                user_perfs['localcopy_path'] = user_perfs['localcopy_path_override']
        else: 
            print(_("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands."))
            print(_("[ModManager] Steam collection mode disabled! Enable by entering collection sub-menu."))
            print(_("[ModManager] Do you want to update mods? ((Y)es / (n)o): "))
        user_command = input().lower()
        if user_command == "yes" or user_command == "y":
            modmanager(user_perfs)
            break
        elif user_command == "no" or user_command == "n":
            break
        elif user_command == "collection" or user_command == "c":
            print(_("[ModManager] Provide an collection link then press enter, or if you want to disable previously enabled collection mode, type 'n' then enter: "))
            collection_url = input()
            if collection_url != "n":
                print(_("[ModManager] Provide an localcopy path (if you dont know what to input, type 'LocalMods') then press enter: "))
                if not 'localcopy_path_override' in user_perfs:
                    user_perfs['localcopy_path'] = input()
                    # TODO collection check, if link is valid
                    user_perfs['collection_link'] = collection_url
                    user_perfs['mode'] = "collection"
                else:
                    user_perfs['localcopy_path'] = user_perfs['localcopy_path_override']
                    user_perfs['collection_link'] = collection_url
                    user_perfs['mode'] = "collection"
            else:
                if 'collection_link' in user_perfs:
                    user_perfs.pop('collection_link')
                user_perfs['mode'] = 'config_player'
            flush_previous_col = True
            modmanager(user_perfs)
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

if __name__ == '__main__':
    logging.disable(logging.CRITICAL)
    main()