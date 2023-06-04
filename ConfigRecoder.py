#!/usr/bin/python
from xml.dom import minidom, getDOMImplementation
import base64
import gzip
import sys
import os
import re
import shutil
try:
    import requests
except ImportError:
    print("Trying to Install required module: requests\n")
    os.system('python3 -m pip install requests')
try:
    import json
except ImportError:
    print("Trying to Install required module: json\n")
    os.system('python3 -m pip install json')
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

# def get_listOfMods(collection_site):
#     if collection_site != "ERROR":
        
#     return arrx

def get_modlist_collection_site(collection_site):
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
            raise Exception("[ModManager]Could not find mods in the collection specified!")

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
    else:
        # throw exeption invalid collection
        raise Exception("[ModManager]There was en error downloading collection! Try re-launching ModManager again later!")
    return mods

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

# modlist must be an array of oject with at minimum of 'ID' filed with assigned steamid of the mod
def get_modlist_data_webapi(modlist):
    new_modlist = modlist
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
                    timestamp = 0
                new_modlist[i]['LastUpdated'] = time.localtime(timestamp)
                if 'file_size' in moddetails:
                    new_modlist[i]['file_size'] = moddetails['file_size']
                if 'title' in moddetails:
                    if not 'name' in new_modlist[i]:
                        new_modlist[i]['name'] = moddetails['title']
                    elif moddetails['title'] != new_modlist[i]['name']:
                        new_modlist[i]['name'] = moddetails['title']
                
    return new_modlist

def get_modname(modsite):
    pattern = "(?<=<h1><span>Subscribe to download<\/span><br>).*?(?=<\/h1>)"
    name = re.findall(pattern, modsite)[0]
    return name

def collectionf(url_of_steam_collection):
    # here
    collection_site = get_htm_of_collection_site(url_of_steam_collection)
    return collection_site

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

def main():
    moddirectory = "C:/Users/milord/AppData/Local/Daedalic Entertainment GmbH/Barotrauma/WorkshopMods/Installed"
    output_file = ""

    if len(sys.argv) >= 3:
        option = str(sys.argv[1])
        fileposition = str(sys.argv[2])
        url_of_steam_collection = str(sys.argv[2])
    else:
        option = "-c"
        url_of_steam_collection = "https://steamcommunity.com/sharedfiles/filedetails/?id=2800347733"

    if option == "-t" or option == "--textfile":
        # i dont remeber why i made this...
        # output_file = textfilef(fileposition, output_file)
        print("err")
    elif option == "-c" or option == "--collection":
        collection_site = collectionf(url_of_steam_collection)
        mods = get_listOfMods(collection_site)
        # getting names here because its more efficient than request
        # not really needed i think
        # mods = get_modsname(collection_site)

    

    # TODO find a way to only request lastupdated not whole cuz its to slow    
    mods = get_modsnamelastupdated(mods)

    print("Detected date, name of: " + str(len(mods)))
    lastupdated_f = ""
    regularpackages = "    <regularpackages>\n"
    # print new
    for mod in mods:
        regularpackages += "      <!--" + mod['name'] + "-->\n"
        lastupdated_f += mod['ID'] + ";" + str(time.strftime('%d %b, %Y @ %I:%M%p', mod['LastUpdated'])) + "\n"
        regularpackages += "      <package\n"
        regularpackages += "        path=\"" + moddirectory + "/" +  mod['ID'] + "/filelist.xml\" />\n"
    regularpackages += "    </regularpackages>\n"

    filex = open("lastupdated.txt", "w", encoding='utf8')
    filex.write(lastupdated_f)
    filex.close()
    print(regularpackages)
    output_file = regularpackages
    # return output_file


    file1 = open("regularpackages.xml", "w", encoding='utf8')
    file1.write(output_file)
    file1.close()

if __name__ == '__main__':
    main()