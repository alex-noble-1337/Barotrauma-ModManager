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
noconfirm = False

# My "Quality" code
# my IT teacher would kill me if she saw this...
available_modes = ["config_player", "collection"]
from BaroRewrites import content_types
from BaroRewrites import content_types_binary
configs = ['barotrauma', 'steamcmd', 'collection_link', 'mode',
           'localcopy_path', 'addperformancefix', 'max_saves', 'save_dir']

# TODO change this to import only individual commands
import shutil
import re
import time
import datetime
import xml.etree.ElementTree as ET
import pprint

import logging
import logging.config
logger = logging.getLogger(__name__)
import gettext
_ = gettext.gettext
# For naming of logs
current_time = datetime.datetime.now()
current_time = current_time.replace(second=0, microsecond=0)
current_time = str(current_time)[0:-3]

try:
    from rich.console import Console
    from rich.markdown import Markdown
except ImportError:
    print("Trying to Install required module: rich\n")
    os.system('python3 -m pip install rich')
    from rich.console import Console
    from rich.markdown import Markdown
console = Console()

try:
    import requests
except ImportError:
    print("Trying to Install required module: requests\n")
    os.system('python3 -m pip install requests')
    import requests

# load submodules
import SteamIOMM
import BaroRewrites
import BackupUtil
import ConfigRecoder

# set up all default values and paths
# TODO rework
def get_user_perfs(config_path = None, options_arr = sys.argv[1:]):
    """
    returns user_perfs dict
    gets it from:
        - defaults
        - tool/config path from command line args
        - config file
        - then from command line args
    any value defined previously gets overrwritten by next option
    """
    # stuff not in config: toolpath - configuration path (and path of cashe for now)
    # TODO defaults defined when user_perfs is created
    # configuration overrides, done via command line paramenters
    # then load config files
    # defaults:
    user_perfs = {'locale': 'en', 'old_managedmods': [], 'tool': default_tool_path,
                  'barotrauma': default_barotrauma_path, 'steamcmd': default_steamcmd_path,
                  'addperformancefix': default_addperformancefix}
    logging_config = {}
    logger.info("DEFAULT user_perfs are {0}".format(str(user_perfs)))

    if config_path == None:
        user_perfs['config_path'] = os.path.join(os.path.dirname(sys.argv[0]), "config.xml")
    else:
        user_perfs['config_path'] = config_path
    # TODO soon to replace toolpath
    logger.debug("config_path is set as {0}".format(user_perfs['config_path']))
    # toolpath or config path
    #  Must be a path to THE FOLDER.  Does not accept "" use "." instead
    # arguments(-t. --toolpath etc), name of variables (optionally dict, first name of variable, second pretty name) 
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
    user_perfs['logging_path'] = os.path.join(user_perfs['tool'], "ModManagerLogs")

    user_perfs['logging_level'] = 'DEBUG'
    user_perfs['logging_max'] = 12

    # get config from file
    user_perfs = get_user_perfs_cfg(user_perfs)
    
    # Logging
    if logging_on:
        # logging enabling and configuaration
        logfile_path = os.path.join(user_perfs['logging_path'], current_time  + ".log")
        os.makedirs(os.path.dirname(logfile_path), exist_ok=True)
        filenames = os.listdir(os.path.dirname(logfile_path))
        logs = []
        for file_ in filenames:
            if file_[-4:] == ".log":
                logs.append(file_)
        logs = sorted(logs)
        if user_perfs['logging_max'] < len(logs):
            logs_todel = logs[0:len(logs) - user_perfs['logging_max']]
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
                    'level': user_perfs['logging_level'],
                    'formatter': 'standard',
                    'class': 'logging.StreamHandler',
                },
                'file_handler': {
                    'level': user_perfs['logging_level'],
                    'filename': logfile_path,
                    'class': 'logging.FileHandler',
                    'formatter': 'standard'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['file_handler'],
                    'level': user_perfs['logging_level'],
                    'propagate': True
                },
            }
        }
        logging.config.dictConfig(logging_config)
        logging.disable(logging.NOTSET)

    # get config from command line arguments
    command_line_args = ['--barotraumapath', '-b', '--toolpath', '-t', '--steamcmdpath', '-s', '--collection', '-c', '--performancefix', '-p',
                         '--backup', '--installdir', '-o', "--blacklist"]
    if len(options_arr) >= 1:
        for i in range(0,len(options_arr)):
            tempval = 1
            if options_arr[i] in command_line_args:
                for j in range(i + 1,len(options_arr)):
                    if options_arr[j] in command_line_args:
                        break
                    else:
                        tempval += 1

            # override installation dir
            if options_arr[i] == '--installdir' or options_arr[i] == '-o':
                if tempval >= 2:
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
                    # TODO use that varialbe later
                    collection_site = SteamIOMM.get_collectionsite(options_arr[i+1])
                    valid = SteamIOMM.check_collection_link(collection_site, noconfirm)
                    if valid:
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
                    user_perfs['max_saves'] = int(options_arr[i+1])
                    user_perfs['save_dir'] = options_arr[i+2]
                    logger.info("save dir for backups is set: {0} and max backup ammout is set to: {1}".format(user_perfs['save_dir'], user_perfs['max_saves']))

            # TODO add it to the documentaton
            if options_arr[i] == '--blacklist':
                if tempval >= 1:
                    user_perfs['blacklist'] = options_arr[i+1]
                    logger.info("blacklist is set: {0}".format(user_perfs['blacklist']))

            if options_arr[i] == '--noconfirm':
                if tempval >= 1:
                    noconfirm = True

            if options_arr[i] == '--removemods':
                if tempval >= 1:
                    user_perfs['remove_mods'] = True

    # setting up default values and path handling
    if not os.path.isabs(user_perfs['barotrauma']):
        user_perfs['barotrauma'] = os.path.abspath(user_perfs['barotrauma'])
    # TODO wtf is this
    if default_steamdir_path == "":
        user_perfs['steamdir'] = os.path.join(user_perfs['tool'], "steamdir")
    else:
        user_perfs['steamdir'] = default_steamdir_path
        logger.info("steamdir path overriden {0}".format(user_perfs['steamdir']))


    if 'collection_link' in user_perfs and ('localcopy_path' in user_perfs or 'localcopy_path_override' in user_perfs):
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
        if 'localcopy_path' in user_perfs:
            user_perfs['old_localcopy_path'] = user_perfs['localcopy_path']
            user_perfs.pop('localcopy_path')
        logger.info("Collection mode configuration flushed")
    elif 'collection_link' in user_perfs and user_perfs['mode'] == "collection" and 'localcopy_path' in user_perfs:
        logger.info("Collection mode enabled from perfs, collection_link:{0}, mode:{1}, localcopy_path:{2}"
            .format(user_perfs['collection_link'], user_perfs['mode'], user_perfs['localcopy_path']))
    if 'localcopy_path_override' in user_perfs:
        user_perfs['localcopy_path'] = user_perfs['localcopy_path_override']
        logger.info("localcopy path override set as {0}".format(user_perfs['localcopy_path']))
        
    return user_perfs
def get_user_perfs_cfg(user_perfs_in, config_path_in = None):
    if config_path_in == None:
        config_path = user_perfs_in['config_path']
    else:
        config_path = config_path_in
    user_perfs = user_perfs_in

    if os.path.exists(config_path):
        with open(config_path , 'r', encoding="utf8") as f:
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
                            if mod_xml.tag == 'Workshop':
                                mod = {'type': mod_xml.tag, 'id': mod_xml.attrib['id']}
                            else:
                                mod = {'type': mod_xml.tag, 'id': mod_xml.attrib['name'], 'name': mod_xml.attrib['name']}
                            if 'name' in mod_xml.attrib:
                                mod['name'] = mod_xml.attrib['name']
                            user_perfs['old_managedmods'].append(mod)
                if subconfig.tag.lower() == 'modserrors':
                    for mod_xml in subconfig:
                        if mod_xml.tag in ['Mod']:
                            # TODO optimize this
                            for i in range(len(user_perfs['old_managedmods'])):
                                if user_perfs['old_managedmods'][i]['id'] == mod_xml.attrib['id']:
                                    errors = mod_xml.attrib['errors'].replace(" ", "")
                                    errors = errors.replace("[", "")
                                    errors = errors.replace("]", "")
                                    errors = errors.replace("'", "")
                                    user_perfs['old_managedmods'][i]['errors'] = errors.split(",")
            user_perfs['old_localcopy_path'] = user_perfs['localcopy_path']
    return user_perfs
    
def save_user_perfs_cfg(managed_mods, user_perfs, corecontentpackage = "Vanilla"):
    """saves mannaged_mods arr and user_perfs dict to the config.xml file in config_path defined in user_perfs"""
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
    
    config_xml.append(ConfigRecoder.modlist_to_ModListsXml(managed_mods, corecontentpackage))
    config_xml.append(ConfigRecoder.modlist_to_ModListsErrors(managed_mods))
    ET.indent(config_xml, space="\t", level=0)
    with open(user_perfs['config_path'], 'wb') as open_file:
        open_file.write(ET.tostring(config_xml))

def get_config_player_str(config_player_path: str):
    """
    returns string of config_player.xml from barotrauma directory.
    Prints formatted exception on not finding it to log and command line
    """
    fixed_path = config_player_path
    if not os.path.isabs(fixed_path):
        fixed_path = os.path.abspath(fixed_path)
    if os.path.isdir(fixed_path):
        fixed_path = os.path.join(fixed_path, "config_player.xml")
    try:
        with open(fixed_path, "r", encoding='utf8') as f:
            config_player_str = f.read()
    except Exception as e:
        logger.critical("Fatal Exception occured!\n" + str(e))
        raise Exception(_("[ModManager] Could not find the config_player.xml! Check your barotrauma path!\n[ModManager] Barotrauma path: {0}").format(fixed_path))
    return config_player_str 
def get_regularpackages(config_player_path: str):
    """
    everything inside <regularpackages/> </regularpackages> tags (with those tags) from config_player.xml in barotrauma directory
    config_player_path is path to config_player.xml directory
    """
    config_player_str = get_config_player_str(config_player_path)

    regularpackages = re.findall("<regularpackages>[\s\S]*?<\/regularpackages>", config_player_str)
    if len(regularpackages) <= 0:
        logger.warning("Couldnt find regularpackages! This probbabbly means the tag is closed (<regularpackages/>). Applying patch...")
        # patch for </regularpackages>, just in case
        regularpackages = re.findall("<regularpackages.*?/>", config_player_str)

    if len(regularpackages) > 0:
        return regularpackages[0]
    else:
        logger.critical(("[ModManager] Error during getting modlist from config_player.xml: Could not find regularpackages.\nFix it by removing everything from <regularpackages> to </regularpackages> and with those two, and replacing it with a single <regularpackages/>"))
        raise Exception(_(("[ModManager] Error during getting modlist from config_player.xml: Could not find regularpackages.\nFix it by removing everything from <regularpackages> to </regularpackages> and with those two, and replacing it with a single <regularpackages/>")))
def get_modlist_regularpackages(regularpackages: str, localcopy_path: str):
    """
    Uses xml parser to extract modlist from regularpackages
    returns: array of dicts that contain mod information: {id, type, path}, if they exist in localcopy: {id, type, installtime, modificationtime}
    """
    root = ET.fromstring(regularpackages)
    modlist = []
    for element in root:
        if element.tag == "package":
            mod = {'id': os.path.basename(os.path.dirname(element.attrib['path']))}
            mod = set_mod_type(mod)
            modlist.append(mod)

    # reason i need to look in filelist is because of:
    #   - shit barotrauma devs (look up Fix barodev problem when you update modname on steam without updating the filelist.xml, this makes comments in filelist shit and not useful)
    #   - i can just get non-installed mods name's via api 
    for mod in modlist:
        mod_path = os.path.join(localcopy_path, mod['id'])
        if os.path.isabs(mod_path):
            filelist_path = os.path.join(mod_path, "filelist.xml")
        else:
            filelist_path = os.path.join(os.path.abspath(mod_path), "filelist.xml")
        if os.path.exists(filelist_path):
            with open(filelist_path, 'r') as open_file:
                mod_filelist_str = open_file.read()
            mod_filelist = ET.fromstring(mod_filelist_str)
            if mod_filelist.tag.lower() == "contentpackage":
                mod['name'] = mod_filelist.attrib['name']
                if 'installtime' in mod_filelist.attrib:
                    mod['installtime'] = int(mod_filelist.attrib['installtime'])
        else:
            mod_data = ""
            if 'name' in mod:
                mod_data += "name: " + mod['name'] 
            mod_data += " " + filelist_path
            logger.warning("Cant find filelist! {0}".format(filelist_path))
            if (not 'name' in mod) and (mod['type'] == "Local"):
                # last resort option, if it coudnt find name
                mod['name'] = mod['id']
                logger.warning("Set name of id:{0} as {1}".format(mod['id'], mod['name']))
        
    return modlist
def get_localcopy_path(regularpackages: str):
    """
    returns localcopy path (path to where mods should be installed) from config_player.xml
    """
    localcopy_path = ""
    root = ET.fromstring(regularpackages)
    if root.tag == "regularpackages":
        if root.text != None:
            for package in root:
                # werid, BUT just in case...
                if package.tag == 'package':
                    localcopy_path = os.path.dirname(os.path.dirname(package.attrib['path']))
                    break
    if localcopy_path == "":
        logger.critical("Localcopy path not found in config_player.xml!\nTake a look at your mod's paths in config_player, and make sure they are correctly set, or use localcopy path override option!")
        raise Exception(_("Localcopy path not found in config_player.xml!\nTake a look at your mod's paths in config_player, and make sure they are correctly set, or use localcopy path override option!"))
    
    if not os.path.isabs(localcopy_path):
        localcopy_path = os.path.abspath(localcopy_path)
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
def set_modlist_regularpackages(modlist, localcopy_path_og: str, barotrauma_path: str):
    """
    Outputs new regularpackages string (part of config_player thats enclosed in <regularpackages> tags) from: modlist array, localcopy_path
    and truncates path to the mod in that regularpackages string according to barotrauma_path
    """
    regularpackages_new = "<regularpackages>\n"
    # print new
    for mod in modlist:
        #  if barotrauma_path is inside of 
        temp_mod_path = os.path.join(localcopy_path_og, mod['id'])
        if temp_mod_path.count(barotrauma_path) > 0:
            if sys.platform == "win32":
                sep = "\\"
            else:
                sep = "/"
            temp_mod_path = temp_mod_path.replace(barotrauma_path + sep, "")
            logger.debug("Path for mod ({0}) is {1}".format(mod['id'], temp_mod_path))

        if sys.platform == "win32":
            temp_mod_path = temp_mod_path.replace("\\", "/")
        else:
            temp_mod_path = temp_mod_path

        modname_formatted = mod['name'].replace("--", "- -")
        modname_formatted = modname_formatted.replace("&", "&amp;")
        temp_mod_path = temp_mod_path.replace("&", "&amp;")
        regularpackages_new += "      <!--" + modname_formatted + "-->\n"
        regularpackages_new += "      <package\n"
        regularpackages_new += "        path=\"" + temp_mod_path + "/filelist.xml" + "\"/>\n"
    regularpackages_new += "    </regularpackages>"
    return regularpackages_new

def print_modlist(modlist):
    """
    prints formatted modlist (array of dicts that have mod data) requires at least id tag in mod dict
    """
    print(_("[ModManager] List of mods:"))
    for mod in modlist:
        if str(mod['id']) == "2701251094":
            has_performancefix = True
        mod_str = mod['id']
        if 'name' in mod:
            mod_str += ": " + mod['name']
        print(_("[ModManager] {0}").format(mod_str))
    print("\n")
def remove_duplicates(modlist):
    """
    returns modlist (array of dicts that have mod data) with all duplicate entries removed
    """
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
    """
    returns modlist (array of dicts that have mod data) with completed mod data (adds 'type')
    """
    managed_mods = []
    for mod in modlist:
        mod_b = mod
        if not 'type' in mod_b:
            mod_b = set_mod_type(mod_b)
        managed_mods.append(mod_b)
    return managed_mods

def get_modlist_data_oldmanagedmods(modlist, old_managed_modlist):
    # essentially merges modlist and old_managed_modlist
    return_modlist = []
    for mod in modlist:
        buffer = mod.copy()
        for old_managed_mod in old_managed_modlist:
            if 'id' in mod and 'id' in old_managed_mod:
                if mod['id'] == old_managed_mod['id']:
                    buffer.update(old_managed_mod)
        return_modlist.append(buffer)
    return return_modlist
    
def get_not_managed_modlist(old_managed_modlist, managed_modlist, localcopy_path: str):
    """
    returns modlist containing mods that were removed from previous running of ModManager
    """
    not_managed_modlist = old_managed_modlist
    # removeing mods that exist in modlist
    # TODO sloooooow
    for modwithdir in managed_modlist:
        for old_modwithdir in old_managed_modlist:
            path_mod = os.path.join(localcopy_path, modwithdir['id'])
            path_old_mod = os.path.join(localcopy_path, old_modwithdir['id'])
            if not os.path.isabs(path_mod):
                path_mod = os.path.abspath(path_mod)
            if not os.path.isabs(path_old_mod):
                path_old_mod = os.path.abspath(path_mod)
            if os.path.realpath(path_mod) == os.path.realpath(path_old_mod):
                not_managed_modlist.remove(old_modwithdir)
    return not_managed_modlist
def deleting_not_managed_modlist(not_managed_modlist, localcopy_path):
    """
    Deletes all mods found in not_managed_modlist array
    """
    removed_count = 0
    for not_managedmod in not_managed_modlist:
        mod_path = os.path.join(localcopy_path, not_managedmod['id'])
        if os.path.exists(mod_path):
            shutil.rmtree(mod_path)
            removed_count += 1
    print(_("[ModManager] Removed {0} not managed now mods!").format(str(removed_count)))
def get_up_to_date_mods(mods, localcopy_path):
    """
    requires: LastUpdated time object in modlist's mod dict
    check, both if they exist and if they are up to date
    made it that way to...uhhhh idk
    also appends modificationtime if not present
    returns: modlist (array of dicts that have mod data) that are updated, and exist in localcopy_path
    """
    remove_arr = []
    # TODO current slowing time is about 
    # TODO lastupdated skip for windows and mac
    for mod in mods:
        if 'LastUpdated' in mod:
            mod_path = os.path.join(localcopy_path, mod['id'])
            if os.path.exists(mod_path):
                if not 'installtime' in mod:
                    mod['installtime'] = get_recusive_modification_time_of_dir(mod_path)
                # conversion into time struct
                mod['installtime'] = time.localtime(mod['installtime'])
                test = time.strftime('%d %b, %Y @ %I:%M%p', mod['installtime'])
                # greater not equal because of possible steam errors
                if  mod['installtime'] > mod['LastUpdated'] and os.path.exists(os.path.join(mod_path, "filelist.xml")):
                    # TODO check if all xml files are matching what is in filelist
                    # TODO thats a lazy way to do it
                    remove_arr.append(mod)
                    logger.debug("Mod {0} ({1}) is up to date".format(mod['name'], mod['id']))
    return remove_arr
def is_serverside_mod(mod_path: str):
    """
    returns True if mod will not appear in server description on server browser
    returns False if mod will appear in server description on server browser, or if it cant find filelist
    """
    pure_lua_mod = False
    filelist_path = os.path.join(mod_path, "filelist.xml")
    if os.path.exists(filelist_path):
        with open(filelist_path, "r", encoding='utf8') as f:
            filelist_str = f.read()
        filelist = ET.fromstring(filelist_str)
        xmlitems = 0
        for mod in filelist:
            if mod.tag.lower() in content_types or mod.tag.lower() in content_types_binary:
                xmlitems += 1
        if xmlitems <= 0:
            pure_lua_mod = True
    else:
        logger.warning("Cant find filelist! path:{0}".format(filelist_path))
    return pure_lua_mod
def set_mod_type(mod):
    """
    returns mod dict with 'type' set to appropiriate value. "Workshop" or "Local"
    """
    id_test = re.findall("\d+$", mod['id'])
    if len(id_test) >= 1:
        if len(id_test[0]) == len(mod['id']):
            mod['id'] = id_test[0]
            mod['type'] = "Workshop"
        else:
            mod['type'] = "Local"
    else:
        mod['type'] = "Local"
    return mod

def remove_all_occurences_from_arr(arr, remove_arr):
    """
    returns array with all occurences of elements in remove_arr, removed
    """
    new_arr = arr.copy()
    for item_to_remove in remove_arr:
        if item_to_remove in new_arr:
            new_arr.remove(item_to_remove)
    return new_arr
def get_recusive_modification_time_of_dir(origin_dir):
    """
    returns highest modification time timestamp of a directory files
    """
    modificationtime = 0
    for src_dir, dirs, files in os.walk(origin_dir):
        for file_ in files:
            new_modificationtime = os.path.getmtime(os.path.join(src_dir, file_))
            if new_modificationtime > modificationtime:
                modificationtime = new_modificationtime
    logger.debug("Timestamp for dir: {0} is {1}".format(origin_dir, modificationtime))
    return modificationtime
def sanitize_pathstr(path):
    path = str(path)
    path = path.replace(" ", "\\ ")
    return path
def robocopysubsttute(root_src_dir, root_dst_dir, replace_option = False):
    """
    yoinked from stackoverflow, works
    recuively move directory to desination directory
    """
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
    logger.info("Aqquired user perfs: {0}".format(str(pprint.pformat(user_perfs))))
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
    regularpackages = get_regularpackages(config_player_path)
    # clean up an creation of steamdir
    if os.path.exists(user_perfs['steamdir']):
        shutil.rmtree(user_perfs['steamdir'])
    os.makedirs(user_perfs['steamdir'] ,exist_ok = True)
    if 'localcopy_path' in user_perfs and 'localcopy_path_override' in user_perfs:
        user_perfs['localcopy_path'] = user_perfs['localcopy_path_override']
        logger.info("localcopy path override set as {0}".format(user_perfs['localcopy_path']))
        if not os.path.isabs(user_perfs['localcopy_path']):
            user_perfs['localcopy_path'] = os.path.abspath(user_perfs['localcopy_path'])

    # check collection link if it is valid TODO, move it to WHEN collection link is inputted
    isvalid_collection_link = False
    if 'collection_link' in user_perfs:
        collection_site = SteamIOMM.get_collectionsite(user_perfs['collection_link'])
        isvalid_collection_link = SteamIOMM.check_collection_link(collection_site, noconfirm)
    
    if user_perfs['addperformancefix']:
        modlist.insert(0, {'name': "Performance Fix", 'id': "2701251094"})
        logger.debug("Performance fix has been added to modlist {0}".format(str(modlist)))

    if 'remove_mods' in user_perfs:
        print(_("[ModManager] Removal mode ENABLED, Removing mods!"))
        modlist = []
    else:
        if isvalid_collection_link and user_perfs['mode'] == "collection":
            print(_("[ModManager] Collection mode ENABLED, Downloading collection data (This might take a sec)"))
            modlist.extend(SteamIOMM.get_modlist_collection_site(collection_site))
        else:
            # Hotfix TODO
            if ((regularpackages.replace("</regularpackages>", "")).replace("<regularpackages>","")).strip() \
            == "" or regularpackages.strip() == "<regularpackages/>" or regularpackages.strip() == "<regularpackages />":
                logger.warning("regularpackages empty!")
                save_user_perfs_cfg(modlist, user_perfs)
                print(_("[ModManager] No mods detected"))
                return 
            else:
                print(_("[ModManager] Collection mode DISABLED, Downloading data from config_player.xml"))
                if not 'localcopy_path' in user_perfs:
                    user_perfs['localcopy_path'] = get_localcopy_path(regularpackages)
                if user_perfs['localcopy_path'] == "":
                    user_perfs['localcopy_path'] = get_localcopy_path(regularpackages)
                if 'localcopy_path_override' in user_perfs:
                    user_perfs['localcopy_path'] = user_perfs['localcopy_path_override']
                    if not os.path.isabs(user_perfs['localcopy_path']):
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

    if 'remove_mods' in user_perfs:
        if user_perfs['remove_mods'] == True:
            modlist = []

    if 'save_dir' in user_perfs and 'max_saves' in user_perfs:
        BackupUtil.backupBarotraumaData(user_perfs['barotrauma'], user_perfs['localcopy_path'], user_perfs['save_dir'], user_perfs['backup_path'], user_perfs['max_saves'])
    if requrescs and not hascs:
        temp_luacs = [{'name': "Cs For Barotrauma", 'id': "2795927223"}]
        temp_luacs = get_modlist_data_webapi(temp_luacs)
        modlist.extend(temp_luacs)


    modlist = remove_duplicates(modlist)


    # modless? TODO is that really nessesarty anymore?
    if len(modlist) == 0 and not 'remove_mods' in user_perfs:
        save_user_perfs_cfg(modlist, user_perfs)
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
    modlist = get_modlist_data_oldmanagedmods(modlist, user_perfs['old_managedmods'])
    not_managedmods = get_not_managed_modlist(user_perfs['old_managedmods'], modlist, user_perfs['localcopy_path'])
    buffer = []
                
    # blacklist thing
    if 'blacklist' in user_perfs:
        if re.match(user_perfs['blacklist'], "https.*?"):
            link = user_perfs['blacklist']
            while True:
                response = requests.get(link, timeout=200, headers=headers)
                if response.status_code == 200:
                    output = response.text
                    break
                else:
                    output = "ERROR"
                    if retries >= 3:
                        break
                    else:
                        retries += 1
        else:
            output = "ERROR"
        if str(output) != "ERROR":
            # TODO convert string to array?
            blkls_arr = output
            modlist_cpy = modlist
            # array should have only steamids of a mod
            for mod in modlist:
                if mod['id'] in blkls_arr:
                    modlist_cpy.pop(mod)
            modlist = modlist_cpn
                    
                


                

    # re-create config_player
    new_regularpackages = set_modlist_regularpackages(modlist, user_perfs['localcopy_path'], user_perfs['barotrauma'])
    filelist_str = get_config_player_str(user_perfs['barotrauma'])
    filelist_str = filelist_str.replace(regularpackages, new_regularpackages)
    with open(config_player_path, "w", encoding='utf8') as f:
        f.write(filelist_str)


    save_user_perfs_cfg(modlist, user_perfs)


    # lastupdated functionality
    up_to_date_mods = []
    up_to_date_mods = get_up_to_date_mods(modlist, user_perfs['localcopy_path'])
    modlist_to_update = remove_all_occurences_from_arr(modlist, up_to_date_mods)


    # main part, running moddlownloader
    nr_updated_mods = SteamIOMM.download_modlist(modlist_to_update, user_perfs['steamdir'], user_perfs['steamcmd'])
    if nr_updated_mods == 0:
        print(_("[ModManager] All {0} mod are up to date! (if any issues arrise please remove every mod from your {1} directory)").format(str(len(modlist)), user_perfs['localcopy_path']))
    if nr_updated_mods > 0:
        print("\n")
        arg1 = str(nr_updated_mods)
        arg2 = str(user_perfs['localcopy_path'])
        print(_("[ModManager] Skipping download of {0} Already up to date Mods. (if any issues arrise please remove every mod from your \"{1}\" directory)").format(arg1, arg2))
    logger.info("Updated Mods: {0}/{1}".format(str(nr_updated_mods), str(len(modlist))))


    # config backup and conservation
    BackupUtil.backup_option(os.path.join(user_perfs['tool'], "BestDefaultConfigsTM"), steamcmd_downloads)
    BackupUtil.backup_option(user_perfs['localcopy_path'], steamcmd_downloads)


    deleting_not_managed_modlist(not_managedmods, user_perfs['localcopy_path'])

    # actually moving mods to localcopy
    for mod in modlist_to_update:
        if 'type' in mod:
            if mod['type'] == 'Workshop':
                mod_path = os.path.join(steamcmd_downloads, mod['id'])
                mod['errors'] = BaroRewrites.FIX_barodev_moment(mod, mod_path)
                robocopysubsttute(mod_path, os.path.join(user_perfs['localcopy_path'], mod['id']))

    save_user_perfs_cfg(modlist, user_perfs)

    # accessing filelists of mods
    for mod in modlist:
        mod_path = os.path.join(user_perfs['localcopy_path'], mod['id'])
        if os.path.exists(mod_path):
            BaroRewrites.FIX_barodev_moment(mod, mod_path)
        # checking if mod is pure server-side or client side
        if is_serverside_mod(os.path.join(user_perfs['localcopy_path'], mod['id'])):
            number_of_pure_lua_mods += 1
        if 'errors' in mod:
            BaroRewrites.interpret_errors(mod['errors'], mod)


    # finishing anc cleaning up
    # removing steamdir because steamcmd is piece of crap and it sometimes wont download mod if its in directory
    shutil.rmtree(user_perfs['steamdir'])
    if len(up_to_date_mods) <= nr_updated_mods:
        print(_("[ModManager] All {0} Mods have been updated").format(str(nr_updated_mods)))
    else:
        print(_("[ModManager] All Mods were up to date!"))

        


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
        time.sleep(20)
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
    while(True):
        if 'collection_link' in user_perfs and 'localcopy_path' in user_perfs:
            print(_("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands."))
            print(_("[ModManager] Steam collection mode enabled! Disable by entering collection sub-menu."))
            if not noconfirm:
                print(_("[ModManager] Do you want to update that collection of mods? ((Y)es / (n)o): "))
            if 'localcopy_path_override' in user_perfs:
                user_perfs['localcopy_path'] = user_perfs['localcopy_path_override']
        else: 
            print(_("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands."))
            print(_("[ModManager] Steam collection mode disabled! Enable by entering collection sub-menu."))
            if not noconfirm:
                print(_("[ModManager] Do you want to update mods? ((Y)es / (n)o): "))
        user_command = input().lower()
        if user_command == "yes" or user_command == "y" or noconfirm:
            modmanager(user_perfs)
            break
        elif user_command == "no" or user_command == "n":
            break
        elif user_command == "collection" or user_command == "c":
            while True:
                print(_("[ModManager] Provide an collection link then press enter, or if you want to disable previously enabled collection mode, type 'n' then enter: "))
                collection_url = input()
                # TODO use that varialbe later
                collection_site = SteamIOMM.get_collectionsite(collection_url)
                if collection_url != "n":
                    valid = SteamIOMM.check_collection_link(collection_site, noconfirm)
                    if valid:
                        print(_("[ModManager] Provide an localcopy path (if you dont know what to input, type 'LocalMods') then press enter: "))
                        if not 'localcopy_path_override' in user_perfs:
                            user_perfs['localcopy_path'] = input()
                            user_perfs['collection_link'] = collection_url
                            user_perfs['mode'] = "collection"
                            break
                        else:
                            user_perfs['localcopy_path'] = user_perfs['localcopy_path_override']
                            user_perfs['collection_link'] = collection_url
                            user_perfs['mode'] = "collection"
                            break
                    else:
                        print(_("[ModManager] Collection link invalid! Try again!"))
                else:
                    if 'collection_link' in user_perfs:
                        user_perfs.pop('collection_link')
                    user_perfs['mode'] = 'config_player'
                    break
            flush_previous_col = True
            modmanager(user_perfs)
            break
        elif user_command == "help" or user_command == "h":
            # TODO rework it to get Available modes from readme
            print("[ModManager] Help menu:")
            print("[ModManager] README: https://github.com/Milord-ThatOneModder/Barotrauma-ModManager/blob/main/README.md")
            if user_perfs['locale'] == 'en':
                readme_file = "README.md"
            else:
                readme_file = "README." + user_perfs['locale'] + ".md"
                if not os.path.exists(os.path.join(user_perfs['tool'], readme_file)):
                    readme_file = "README.md"
            with open(os.path.join(user_perfs['tool'], readme_file), 'r', encoding="utf8") as f:
                print(console.print(Markdown(f.read())))
            print("\n\n")
            continue
        # elif user_command == "exit":
        #     print("Exiting the mod manager")
        else:
            print(_("[ModManager] Provide a valid anwser: \"y\" or \"yes\" / \"n\" or \"no\""))

if __name__ == '__main__':
    logging.disable(logging.CRITICAL)
    main()