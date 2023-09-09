#!/usr/bin/python
from xml.dom import minidom, getDOMImplementation
import base64
import gzip
import sys
import os
import re
import shutil
import xml.etree.ElementTree as ET
import subprocess
import io

try:
    import requests
except ImportError:
    print("Trying to Install required module: requests\n")
    os.system('python3 -m pip install requests')
    import requests

import json

import time
import datetime # for current time

import gettext
_ = gettext.gettext
import logging
import logging.config
logger = logging.getLogger(__name__)
# TODO fix circular import problems
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

# TODO use a fucking API instead i think
# TODO this is main bottleneck, need to optimize it
# TODO cant optimaize it more, because steamapi does not give Required items
# TODO maybe use wget?
headers = {'User-Agent': 'Mozilla/5.0'}
# delay between usage of function based on system clock + internal function delay
time_of_last_usage = 0
def get_htm_of_collection_site(link):
    # TODO add check if you have internet
    # TODO add more exceptions
    global time_of_last_usage
    retries = 0
    while True:
        if time_of_last_usage != 0 and int(round(time.time())) - time_of_last_usage < 15:
            time.sleep(int(round(time.time())) - time_of_last_usage)
        time_of_last_usage = int(round(time.time()))
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
    return output
def get_modlist_collection_site(collection_site):
    addnames = True
    mods = []
    if collection_site != "ERROR":
        # get list of all mod's id's in the collection in an array
        # modsids = get_listOfMods(collection_site)
        pattern = "<div class=\"collectionItemDetails\">"
        startposs = [m.start() for m in re.finditer(pattern, collection_site)]
        collectionItemDetailss = []
        if len(startposs) >= 0:
            for startpos in startposs:
                startpos += len(pattern)
                divsinside = 0
                endpos = 0
                for j in range(startpos, len(collection_site)):
                    string = collection_site[j] + collection_site[j+1] + collection_site[j+2] + collection_site[j+3] + collection_site[j+4]
                    if string == "<div ":
                        divsinside += 1
                    if string == "</div":
                        if divsinside != 0:
                            divsinside -= 1
                        else:
                            endpos = j
                            collectionItemDetailss.append(collection_site[startpos:endpos])
                            break
        else:
            # throw exeption invalid collection
            logger.critical("[ModManager]Could not find mods in the collection specified!")
            raise Exception(_("[ModManager]Could not find mods in the collection specified!"))

        # mods = []
        for collectionItemDetails in collectionItemDetailss:
            mod = {}
            pattern = "(?<=<a href=\"https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=).*?(?=\"><div class=\"workshopItemTitle\">)"
            mod['id'] = str(re.findall(pattern, collectionItemDetails)[0])
            if addnames:
                pattern = "(?<=id=" + mod['id'] + "\"><div class=\"workshopItemTitle\">).*?(?=<\/div>)"
                name = re.findall(pattern, collectionItemDetails)[0]
                # fixing of names special characters
                name = name.replace("--", "- -")
                name = name.replace("&amp;", "&")
                name = name.replace("&quot;", "\"")
                mod['name'] = name
            mods.append(mod)
    else:
        # throw exeption invalid collection
        logger.critical("[ModManager]There was en error downloading collection! Try re-launching ModManager again later!")
        raise Exception(_("[ModManager]There was en error downloading collection! Try re-launching ModManager again later!"))
    return mods
# modlist must be an array of oject with at minimum of 'id' filed with assigned steamid of the mod
def get_modlist_data_webapi(modlist):
    new_modlist = modlist
    if modlist != []:
        adress_of_request = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
        number_of_workshop_mods = 0
        option_tuple = {}
        for i in range(len(modlist)):
            mod = modlist[i]
            if not 'type' in mod:
                mod = set_mod_type(mod)
            if mod['type'] == "Workshop":
                option_tuple['publishedfileids[' + str(i) + ']'] = mod['id']
                number_of_workshop_mods += 1
        option_tuple['itemcount'] = number_of_workshop_mods
        output = requests.post(adress_of_request, option_tuple)
        if output.status_code == 200:
            data = json.loads(output.text)
            publishedfiledetails = data['response']['publishedfiledetails']
            for i in range(len(new_modlist)):
                for moddetails in publishedfiledetails:
                    if moddetails['publishedfileid'] == new_modlist[i]['id']:
                        if 'time_updated' in moddetails:
                            timestamp = moddetails['time_updated']
                        elif 'time_created' in moddetails:
                            timestamp = moddetails['time_created']
                        else:
                            logger.warning("No time of creation or update found! {0}".format(moddetails['publishedfileid']))
                            timestamp = 0
                        new_modlist[i]['LastUpdated'] = time.localtime(timestamp)
                        if 'file_size' in moddetails:
                            new_modlist[i]['file_size'] = moddetails['file_size']
                        if 'title' in moddetails:
                            if not 'name' in new_modlist[i]:
                                new_modlist[i]['name'] = moddetails['title']
                            elif moddetails['title'] != new_modlist[i]['name']:
                                new_modlist[i]['name'] = moddetails['title']
                        # TODO why????
                        new_modlist[i]['steamworkshopid'] = new_modlist[i]['id']
        elif output.status_code == 404:
            logger.critical("Connection to steam WebAPI FAILED! Consult logfile for more deatails!")
            raise Exception(_("Connection to steam WebAPI FAILED! Consult logfile for more deatails!"))
        else: 
            logger.error("BAD REQUEST! {0}".format(output.text))
            print(_("BAD REQUEST! Consult logfile for more deatails!"))

    return new_modlist
def get_modlist_collection_site_legacy(collection_site, mods, input_options = {'addnames': True, 'addlastupdated': True, 'dependencies': True}):
    if 'addnames' not in input_options:
        input_options['addnames'] = False
    if 'addlastupdated' not in input_options:
        input_options['addlastupdated'] = False
    if 'dependencies' not in input_options:
        input_options['dependencies'] = False
    
    addnames = input_options['addnames']
    addlastupdated = input_options['addlastupdated']
    dependencies = input_options['dependencies']

    mods = get_modsData_collection(collection_site, mods, addnames)
    if addlastupdated or dependencies:
        mods = get_modlist_data(mods, addlastupdated, dependencies)
    return mods

# populate time of update of workshop item
def get_lastupdated_old(modsite):
    pattern = "(?<=<div class=\"detailsStatRight\">).*?(?=<\/div>)"
    lastupdated = re.findall(pattern, modsite)
    lastupdated = lastupdated[len(lastupdated) - 1]
    # Eg. 1 Oct, 2022 @ 3:51am
    if lastupdated[2] != " ":
        lastupdated = "0" + lastupdated
    # Eg. 11 Jan @ 1:15am
    if lastupdated[7] == "@":
        currentDateTime = datetime.datetime.now()
        date = currentDateTime.date()
        year = str(date.strftime("%Y"))
        lastupdated = lastupdated[0:6] + ", " + year + " " + lastupdated[7:]
    # Eg. 28 May, 2022 @ 9:58pm
    # Eg. 18 Jan 2023 @ 7:10pm
    if lastupdated[16] == ":":
        lastupdated = lastupdated[0:14] + " 0" + lastupdated[15:]
    lastupdated = time.strptime(lastupdated,'%d %b, %Y @ %I:%M%p')

    return lastupdated
def get_modname(modsite):
    pattern = "(?<=<h1><span>Subscribe to download<\/span><br>).*?(?=<\/h1>)"
    name = re.findall(pattern, modsite)[0]
    return name
def get_modlist_data(mods, dependencies = False):
    # just in caaaaaase, lts put it here, i dont trust myself
    for i in range(len(mods)):
        if not isinstance(mods[i], dict):
            WorkshopItem = {'id': mods[i]}
            mods[i] = WorkshopItem

    mods = get_modlist_data_webapi(mods)

    if dependencies:
        for i in range(len(mods)):
            # download modsite html
            modurl = "https://steamcommunity.com/sharedfiles/filedetails/?id=" + str(mods[i]['id'])
            modsite = get_htm_of_collection_site(modurl)
            if modsite != "ERROR":

                    # TODO this is stupid
                    startpos = modsite.find("<div class=\"requiredItemsContainer\" id=\"RequiredItems\">")
                    requiredItems = ""
                    if startpos >= 0:
                        startpos += 56
                        divsinside = 0
                        endpos = 0
                        for j in range(startpos, len(modsite)):
                            string = modsite[j] + modsite[j+1] + modsite[j+2] + modsite[j+3] + modsite[j+4]
                            if string == "<div ":
                                divsinside += 1
                            if string == "</div":
                                if divsinside != 0:
                                    divsinside -= 1
                                else:
                                    endpos = j
                                    requiredItems = modsite[startpos:endpos]
                                    break
                    

                    pattern = "(?<=<a href=\"https:\\/\\/steamcommunity\\.com\\/workshop\\/filedetails\\/\\?id=).*?(?=\")"
                    requiredItems = re.findall(pattern, requiredItems)
                    mods[i]['dependencies'] = requiredItems

            # if addnames:
            #     mods[i]['name'] = get_modname(modsite)

            # mods[i] = {'name': name, 'id': mods[i]['id']} #, 'LastUpdated': lastupdated} 
            else:
                print("[ModManager]Mod with a link: " + modurl + " not found!")

    return mods

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
    modlist_workshop = []
    for mod in modlist:
        if not 'type' in mod:
            id_test = re.findall("\d+$", mod['id'])
            if len(id_test) >= 1:
                if len(id_test[0]) == len(mod['id']):
                    mod['id'] = id_test[0]
                    mod['type'] = "Workshop"
                else:
                    mod['type'] = "Local"
            else:
                mod['type'] = "Local"
        if mod['type'] == "Workshop":
            if 'file_size' in mod:
                modlist_file_size += mod['file_size']
            modlist_workshop.append(mod)
        else:
            print(_("[ModManager] Skipped mod!: {name:s} ({id:s})").format(**mod))
            # bar.update(1)
            print()
            # iterator += 1
            # bar.update(iterator)

    completed_file_size = 0
    for mod in modlist_workshop:
        if re.match("^\d*?$", mod['id']):
            one_time = int(round(time.time()))
            # main part running moddlownloader
            print(_("[ModManager] Starting steamcmd, Updating mod:{id:s}: {name:s}").format(**mod), end='')
            print("\t" + _("Update Progress: {0}/{1}").format(str(iterator+1), str(len(modlist_workshop))), end='')
            if len(modlist_workshop) >= 3:
                if iterator >= 3:
                    # TODO dirty quickfix
                    if completed_file_size > 0:
                        number = int(abs((modlist_file_size - completed_file_size)*(total_time / completed_file_size)))
                        print(" " + _("ETA:{0}:{1}").format(str(number//60), str(number%60)), end='')
            print()
            # TODO make output of steamcmd less spammy/silent
            # TODO instead of steamcmd downloading one mod at the time, make it download all of them in one start of steamcmd using steamcmd scripts or cmd line arguments
            proc = moddownloader(mod['id'], steamdir_path, location_with_steamcmd)
            for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                line = line.rstrip()
                logger.debug("Steamcmd output: {0}".format(line))
                # steam connection check
                if re.match(".*?" + "Connecting anonymously to Steam Public...OK" + ".*?", line):
                    print(_("[ModManger] Connected to steam! Beginning mod download..."))
                    # iterator += 1
                    # bar.update(iterator)
                    # bar.update()
                # starting download
                if re.match(".*?Downloading item " + mod['id'] + ".*?", line):
                    print(_("[ModManager] Downloading mod: {name:s} ({id:s})").format(**mod))
                    # iterator += 1
                    # bar.update(iterator)
                    # bar.update()
                # download complete
                if re.match(".*?Success. Downloaded item " + mod['id'] + ".*?", line):
                    # check if mod has been downloaded in correct path
                    if re.match(".*?\"" + steamdir_path + ".*?steamapps.*?workshop.*?content.*?602960.*?" + mod['id'] + "\".*?", line):
                        print(_("[ModManager] Downloaded mod!"))
                        # TODO get that path into an array so steamdir path is not needed, and ypu just move mods from wherever the steamcmd puts tgem
                        # iterator += 1
                        # bar.update(iterator)
                        # bar.update()
                    else:
                        logger.critical("[ModManager] Steamcmd has downloaded mod in wrong directory! Please make sure that steamdir path is up to specifications in README \
                                       \n[Steamcmd]{str:line}".format())
                        raise Exception(_("[ModManager] Steamcmd has downloaded mod in wrong directory! Please make sure that steamdir path is up to specifications in README \
                                         \n[Steamcmd]{str:line}".format()))
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
                logger.critical("[ModManager] Steamcmd return code is not 0! That means steamcd had problems!\n{0}".format(str(proc.errors)))
                raise Exception(_("[ModManager] Steamcmd return code is not 0! That means steamcd had problems!\n{0}".format(str(proc.errors))))
        # change timestamp
        filelist_path = os.path.join(steamdir_path, "steamapps", "workshop", "content", "602960", mod['id'], "filelist.xml")
        if os.path.exists(filelist_path):
            with open(filelist_path, 'r', encoding="utf8") as f:
                filelist_xml = ET.fromstring(f.read())
            filelist_xml.attrib['installtime'] = str(int(time.time()))
            filelist_str = ET.tostring(filelist_xml, encoding="utf-8", method="xml", xml_declaration=True)
            with open(filelist_path, 'wb') as f:
                f.write(filelist_str)
        else:
            logger.critical("Cant find filelist (mod id: {0})! {1}".format(mod['id'], filelist_path))
            print(_("Cant find filelist (mod id: {0})! {1}").format(mod['id'], filelist_path))
    return numberofupdatedmods

# return false on negative test resoult, on positive resoult return collection site string
def get_collectionsite(collection_link: str):
    isvalid_collection_link = False
    if re.match("https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=", collection_link) != None:
        collection_site = get_htm_of_collection_site(collection_link)
        if collection_site != "ERROR":
            isvalid_collection_link= True
    if isvalid_collection_link:
        return collection_site
    else:
        return isvalid_collection_link
def check_collection_link(collection_site, no_input = False):
    if collection_site == False:
        user_command = "no"
        if not no_input:
            user_command = input().lower()
            print(_("[ModManger] Collection link INVALID. Do you want to exit the script? ((Y)es / (n)o):"))
        if user_command == "yes" or user_command == "y":
            logger.critical("Collection link INVALID! Re-enable Collection mode.")
            raise Exception(_("Collection link INVALID! Re-enable Collection mode."))
        isvalid_collection_link = False
    else:
        isvalid_collection_link = True
    logger.info("Collection link validity check is: {0}".format(isvalid_collection_link))
    return isvalid_collection_link