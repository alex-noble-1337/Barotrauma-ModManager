#!/usr/bin/python
from xml.dom import minidom, getDOMImplementation
import base64
import gzip
import sys
import os
import re
import shutil
import xml.etree.ElementTree as ET

import requests
import json

import time
import datetime # for current time

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
            mod['ID'] = str(re.findall(pattern, collectionItemDetails)[0])
            if addnames:
                pattern = "(?<=id=" + mod['ID'] + "\"><div class=\"workshopItemTitle\">).*?(?=<\/div>)"
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
# modlist must be an array of oject with at minimum of 'ID' filed with assigned steamid of the mod
def get_modlist_data_webapi(modlist):
    new_modlist = modlist
    if modlist != []:
        adress_of_request = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
        option_tuple = {'itemcount': len(modlist)}
        for i in range(len(modlist)):
            option_tuple['publishedfileids[' + str(i) + ']'] = modlist[i]['ID']
        output = requests.post("https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/", option_tuple)
        if output.status_code == 200:
            data = json.loads(output.text)
            publishedfiledetails = data['response']['publishedfiledetails']
            for i in range(len(new_modlist)):
                for moddetails in publishedfiledetails:
                    if moddetails['publishedfileid'] == new_modlist[i]['ID']:
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
                        new_modlist[i]['steamworkshopid'] = new_modlist[i]['ID']
        elif output.status_code == 400:
            logger.error("BAD REQUEST! {0}".format(output.text))
            print(_("BAD REQUEST! Consult logfile for more deatails!"))
        else: 
            logger.critical("Connection to steam WebAPI FAILED!")
            raise Exception(_("Connection to steam WebAPI FAILED!"))

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
            WorkshopItem = {'ID': mods[i]}
            mods[i] = WorkshopItem

    mods = get_modlist_data_webapi(mods)

    if dependencies:
        for i in range(len(mods)):
            # download modsite html
            modurl = "https://steamcommunity.com/sharedfiles/filedetails/?id=" + str(mods[i]['ID'])
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

            # mods[i] = {'name': name, 'ID': mods[i]['ID']} #, 'LastUpdated': lastupdated} 
            else:
                print("[ModManager]Mod with a link: " + modurl + " not found!")

    return mods

def modlist_to_ModListsXml(managed_mods, corecontentpackage = "Vanilla"):
    modlist_xml = ET.Element('mods')
    modlist_xml.attrib['name'] = "Managed Mods"

    corecontentpackage_xml = ET.SubElement(modlist_xml, corecontentpackage)

    for managed_mod in managed_mods:
        pattern = "^\d*?$"
        if re.match(pattern, str(os.path.basename(managed_mod))):
            mod = ET.SubElement(modlist_xml, 'Workshop')
            mod.attrib['name'] = "TODO"
            mod.attrib['id'] = str(os.path.basename(managed_mod))
        else:
            mod = ET.SubElement(modlist_xml, 'Local')
            mod.attrib['name'] = str(os.path.basename(managed_mod))
    return modlist_xml
# This is probbably getting from ModListsXml created by barotrauma. TODO check
def textfilef(fileposition):
    with open(fileposition, "r") as textfile:
        name_of_the_file = ""
        name_arr = []
        id_arr = []
        comment_arr = []
        for line in textfile:
            if len(name_of_the_file) <= 0:
                pattern = "(?<=mods name=\").*?(?=\")"
                if re.search(pattern, line):
                    name_of_the_file = re.findall(pattern, line)
                    name_of_the_file = name_of_the_file[0]
                    continue
            else:
                pattern = "(?<=name=\").*?(?=\")"
                if re.search(pattern, line):
                    name_i = re.findall(pattern, line)
                    name_i = name_i[0]
                    name_arr.append(name_i)
                pattern = "(?<=id=\").*?(?=\")"
                if re.search(pattern, line):
                    id_i = re.findall(pattern, line)
                    id_i = id_i[0]
                    id_arr.append(id_i)
                pattern = "<Vanilla \\/>"
                if re.search("<Vanilla \\/>", line):
                    continue
                else:
                    pattern = "(?<=<!-- ).*?(?= -->)"
                    if re.search(pattern, line):
                        comment_i = re.findall(pattern, line)
                        comment_i = comment_i[0]
                        comment_arr.append(comment_i)
                    else:
                        comment_arr.append("")
        for i in range(len(name_arr)):
            output_file = output_file + str(name_arr[i] + "," + id_arr[i])
            if(len(comment_arr[i]) > 0):
                output_file = output_file + "," + comment_arr[i]
            if(i+1 < len(name_arr)):
                output_file += "\n"
    print(name_of_the_file)
    print(output_file)
    return output_file