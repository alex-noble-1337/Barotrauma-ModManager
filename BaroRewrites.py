# This is file of all functions that are requred by mod manager to properly function
# but are taken from barotrauma source code
# due to time constrains had to use chatgpt to translate from c# to python
# i feel bad about it
# so TODO fix it

import sys
import os
import pathlib
import xml.etree.ElementTree as ET
import time
import datetime
from functools import reduce
import shutil
import re

import gettext
_ = gettext.gettext
import logging
import logging.config
logger = logging.getLogger(__name__)

content_types = ["item","character","mapcreature","text", "uistyle","afflictions","structure", "upgrademodules",
                 "ruinconfig", "wreckaiconfig","backgroundcreatureprefabs", "levelobjectprefabs","particles","decals",
                 "randomevents","eventmanagersettings", "locationtypes","mapgenerationparameters", 
                 "levelgenerationparameters", "cavegenerationparameters","outpostconfig", "npcsets","missions",
                 "traitormissions", "npcpersonalitytraits","npcconversations", "jobs","orders","corpses","sounds",
                 "skillsettings","factions","itemassembly", "talents","talenttrees","startitems","tutorials"]


# written in 3-4h so this is probbabbly bad, if you curious why this is needed, uhhhh :barodev: <- probbabbly them
def FIX_barodev_moment(downloaded_mod, downloaded_mod_path, warnings_as_errors = False):
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
                    content = CleanUpPath(content)
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
                logger.debug("Changed from unix to windows line endings in {0}".format(file_path))
            else:
                # Windows ➡ Unix
                content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
                logger.debug("Changed from windows to unix line endings in {0}".format(file_path))
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
        logger.warn("Mod of id:{0} and name: {1} does have old paths! Stable behaviour cannot be made sure of! Remove if possible!"
                    .format(downloaded_mod['id'], downloaded_mod['name']))
        if warnings_as_errors:
            print(_("Treating warnings as errors:"))
            raise Exception(_("Mod of id:{0} and name: {1} does have old paths! Stable behaviour cannot be made sure of! Remove if possible!"
                              .format(downloaded_mod['id'], downloaded_mod['name'])))
        else:
            print(_("Mod of id:{0} and name: {1} does have old paths! Stable behaviour cannot be made sure of! Remove if possible!"
                    .format(downloaded_mod['id'], downloaded_mod['name'])))


    desired_order_list = ['name', 'steamworkshopid', 'corepackage', 'modversion', 'gameversion', 'installtime', 'altnames', 'expectedhash']
    if os.path.exists(filelist_path):
        with open(filelist_path, 'r', encoding="utf8") as open_file:
            filelist_str = open_file.read()

        def_file = ET.fromstring(filelist_str)
        if def_file.tag.lower() == "contentpackage":
            if not 'steamworkshopid' in def_file.attrib:
                def_file.attrib['steamworkshopid'] = downloaded_mod['id']
            else:
                if def_file.attrib['steamworkshopid'] != downloaded_mod['id']:
                    logger.warning("Mod of id:{0} and name: {1} steamid does not match one in workshop link! Remove it if possible"
                                   .format(downloaded_mod['id'], downloaded_mod['name']))
                    if warnings_as_errors:
                        raise Exception(_("Treating warnings as errors:") + "\n" 
                                      + _("Mod of id:{0} and name: {1} steamid does not match one in workshop link! Remove it if possible")
                                          .format(downloaded_mod['id'], downloaded_mod['name']))
                    else:
                        logger.info("Applying workaround for not matching steam id...")
                        # fix?
                        def_file.attrib['steamworkshopid'] = downloaded_mod['id']
            if not 'name' in def_file.attrib:
                def_file.attrib['name'] = downloaded_mod['name']
            else:
                if 'name' in downloaded_mod:
                    if def_file.attrib['name'] != downloaded_mod['name']:
                        logger.warning("Name of {0} was changed via steam! Applying workaround...".format(def_file.attrib['steamworkshopid']))
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
                            logger.warning("Removed altnames attrib!")
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
                    logger.warn("Mod of id:{0} and name: {1} does not have hash! Remove it if possible".format(downloaded_mod['id'], downloaded_mod['name']))
                    if warnings_as_errors:
                        raise Exception(_("Treating warnings as errors") + "\n" + _("Mod of id:{0} and name: {1} does not have hash! Remove it if possible").format(downloaded_mod['id'], downloaded_mod['name']))

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

# Expressions from c# that dont translate to python:
# this is:
# directory ?? "" or
# directory != null ? directory : ""
# or:
def directory_fixer(directory):
    # None is Null in python?
    if directory == None:
        return ""
    else:
        return directory
def get_user_data_dir():
    if sys.platform == "win32":
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        )
        dir_,_ = winreg.QueryValueEx(key, "Local AppData")
        ans = Path(dir_).resolve(strict=False)
    elif sys.platform == 'darwin':
        ans = Path('~/Library/Application Support/').expanduser()
    else:
        ans=pathlib.Path(os.getenv('XDG_DATA_HOME', "~/.local/share")).expanduser()
    return ans.joinpath()
# split in c# accepts arrays, but in python it only accepts strings
def separate(array,separator):
    results = []
    a = array[:]
    i = 0
    while i<=len(a)-len(separator):
        if a[i:i+len(separator)]==separator:
            results.append(a[:i])
            a = a[i+len(separator):]
            i = 0
        else: i+=1
    results.append(a)
    return results
# this is:
# startPath = saveFolder.EndsWith('/') ? saveFolder : $"{saveFoler}/";
def path_addslashend(saveFolder: str):
    # TODO use trim to make sure that there are no white space at the end of the string
    if saveFolder.trim()[-1] == '/':
        return saveFolder
    else:
        return saveFolder + '/'

# https:#github.com/evilfactory/LuaCsForBarotrauma/blob/6b149e0498b9b634847c867ec6a211532f609c7b/Barotrauma/BarotraumaShared/SharedSource/Utils/ToolBox.cs#L32
# Toolbox.cs -> ToolBox/IsProperFilenameCase
def isProperFilenameCase(filename: str):
    if sys.platform == 'win32':
        return True
    else:
        corrected = True
        CorrectFilenameCase(filename, corrected)
        return (not corrected)

class SaveUtil:
    def DefaultSaveFolder():
        if sys.platform == 'darwin':
            #"/*user*/Library/Application Support/Daedalic Entertainment GmbH/" on Mac
            return Path.Combine(os.path.expanduser("~"), "Library", "Application Support", "Daedalic Entertainment GmbH", "Barotrauma")
        else:
            #"C:/Users/*user*/AppData/Local/Daedalic Entertainment GmbH/" on Windows
            #"/home/*user*/.local/share/Daedalic Entertainment GmbH/" on Linux
            return os.path.join(get_user_data_dir(), "Daedalic Entertainment GmbH", "Barotrauma")

# https:#github.com/evilfactory/LuaCsForBarotrauma/blob/6b149e0498b9b634847c867ec6a211532f609c7b/Barotrauma/BarotraumaShared/SharedSource/Utils/ToolBox.cs#L46
# unfortunetly had to use chatgpt due to time and skill constraints
# TODO please check and correct this
def CorrectFilenameCase(filename, directory="", corrected=False):
    delimiters = ['/', '\\']
    subDirs = separate(filename, delimiters)
    originalFilename = filename
    filename = ""

    if not sys.platform == 'win32':
        if os.path.exists(originalFilename):
            return originalFilename

    startPath = directory_fixer(directory)

    saveFolder = SaveUtil.DefaultSaveFolder()
    saveFolder =  saveFolder.replace('\\', '/')
    if originalFilename.replace('\\', '/').startswith(saveFolder):
        startPath = saveFolder if saveFolder.endswith('/') else f"{saveFolder}/"
        filename = startPath
        subDirs = subDirs[len(saveFolder.split('/')):]
    elif os.path.isabs(originalFilename):
        # TODO: incorrect assumption or...? Figure out what this was actually supposed to fix, if anything. Might've been a perf thing.
        return originalFilename  # assume that rooted paths have correct case since these are generated by the game

    for i, subDir in enumerate(subDirs):
        if i == len(subDirs) - 1 and (not subDir or subDir.isspace()):
            break

        subDir = subDir.rstrip()
        enumPath = os.path.join(startPath, filename)

        if not filename.strip():
            enumPath = "./" if not startPath.strip() else startPath

        filePaths = [os.path.basename(f) for f in os.listdir(enumPath)]

        if any(s == subDir for s in filePaths):
            filename += subDir
        else:
            correctedPaths = [s for s in filePaths if s.lower() == subDir.lower()]
            if correctedPaths:
                corrected = True
                filename += correctedPaths[0]
            else:
                # DebugConsole.ThrowError(f"File \"{originalFilename}\" not found!")
                corrected = False
                return originalFilename

        if i < len(subDirs) - 1:
            filename += "/"

    return filename

# https:#github.com/evilfactory/LuaCsForBarotrauma/blob/6b149e0498b9b634847c867ec6a211532f609c7b/Barotrauma/BarotraumaShared/SharedSource/Utils/ToolBox.cs#L601
#:barodev: <summary>
#:barodev: Cleans up a path by replacing backslashes with forward slashes, and
#:barodev: optionally corrects the casing of the path. Recommended when serializing
#:barodev: paths to a human-readable file to force case correction on all platforms.
#:barodev: Also useful when working with paths to files that currently don't exist,
#:barodev: i.e. case cannot be corrected.
#:barodev: </summary>
#:barodev: <param name="path">Path to clean up</param>
#:barodev: <param name="correctFilenameCase">Should the case be corrected to match the filesystem?</param>
#:barodev: <param name="directory">Directories that the path should be found in, not returned.</param>
#:barodev: <returns>Path with corrected slashes, and corrected case if requested.</returns>
def CleanUpPathCrossPlatform(path, correct_filename_case=True, directory=""):
    if not path:
        return ""

    path = path.replace('\\', '/')
    if path.startswith("file:", 0, 5):
        path = path[5:]

    while "#" in path:
        path = path.replace("#", "/")

    if correct_filename_case:
        corrected_path = CorrectFilenameCase(path, directory)
        if corrected_path:
            path = corrected_path

    return path

# https:#github.com/evilfactory/LuaCsForBarotrauma/blob/6b149e0498b9b634847c867ec6a211532f609c7b/Barotrauma/BarotraumaShared/SharedSource/Utils/ToolBox.cs#L633C30-L633C41
#:barodev: <summary>
#:barodev: Cleans up a path by replacing backslashes with forward slashes, and
#:barodev: corrects the casing of the path on non-Windows platforms. Recommended
#:barodev: when loading a path from a file, to make sure that it is found on all
#:barodev: platforms when attempting to open it.
#:barodev: </summary>
#:barodev: <param name="path">Path to clean up</param>
#:barodev: <returns>Path with corrected slashes, and corrected case if required by the platform.</returns>
def CleanUpPath(path):
    return CleanUpPathCrossPlatform(path, correct_filename_case=not (sys.platform == 'win32'))