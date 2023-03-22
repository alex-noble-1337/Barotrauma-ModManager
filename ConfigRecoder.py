#!/usr/bin/python
from xml.dom import minidom, getDOMImplementation
import base64
import gzip
import sys
import os
import re
import shutil
import requests
import time
import datetime # for current time

headers = {'User-Agent': 'Mozilla/5.0'}
# delay between usage of function based on system clock + internal function delay
time_of_last_usage = 0
def get_htm_of_collection_site(link):
    global time_of_last_usage
    while True:
        if time_of_last_usage != 0 and int(round(time.time())) - time_of_last_usage < 15:
            time.sleep(int(round(time.time())) - time_of_last_usage)
        time_of_last_usage = int(round(time.time()))
        response = requests.get(link, timeout=200, headers=headers)
        if response.status_code == 200:
            output = response.text
            break
        else:
            # coundt be bothered to do it other way
            output = "ERROR"
            time.sleep(20)
    return output

def get_listOfMods(collection_site):
    if collection_site != "ERROR":
        pattern = "(?<=<a href=\"https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=).*?(?=\"><div class=\"workshopItemTitle\">)"
        arrx = re.findall(pattern, collection_site)
    return arrx

def get_modsname(collection_site):
    # get list of all mod's id's in the collection in an array
    modsids = get_listOfMods(collection_site)
    # iterate array to get names of mods
    mods = []
    for i in range(len(modsids)):
        # order names in the same array positions
        pattern = "(?<=id=" + str(modsids[i]) + "\"><div class=\"workshopItemTitle\">).*?(?=<\/div>)"
        name = re.findall(pattern, collection_site)
        name = str(name[0])
        modid = str(modsids[i])
        WorkshopItem = {'Name': name, 'ID': modid}
        mods.append(WorkshopItem)
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

def collectionf(url_of_steam_collection):
    # here
    collection_site = get_htm_of_collection_site(url_of_steam_collection)
    return collection_site

def get_modsnamelastupdated(mods):
    for i in range(len(mods)):
        if not isinstance(mods[i], dict):
            WorkshopItem = {'ID': mods[i]}
            mods[i] = WorkshopItem

    # Lua and cs
    runluaupdater = False
    lenmods = len(mods)
    todel = []
    for i in range(lenmods):
        # remove Lua and cs from the list
        if mods[i]['ID'] == "2559634234":
            todel.append(i)
            runluaupdater = True
            continue
        if mods[i]['ID'] == "2795927223":
            todel.append(i)
            runluaupdater = True
            continue
        else:
            # check for lua dependendecies and populate time of update of workshop item
            modurl = "https://steamcommunity.com/sharedfiles/filedetails/?id=" + str(mods[i]['ID'])
            modsite = get_htm_of_collection_site(modurl)
            pattern = "<a href=\"https://steamcommunity.com/workshop/filedetails/?id=2559634234\" target=\"_blank\">.*?<div class=\"requiredItem\">.*?Lua For Barotrauma.*?</a>"
            arrx = re.findall(pattern, modsite)
            pattern = "<a href=\"https://steamcommunity.com/workshop/filedetails/?id=2795927223\" target=\"_blank\">.*?<div class=\"requiredItem\">.*?Cs For Barotrauma.*?</a>"
            arry = re.findall(pattern, modsite)
            num = len(arrx) + len(arry)
            if num > 0:
                runluaupdater = True


            pattern = "(?<=<h1><span>Subscribe to download<\/span><br>).*?(?=<\/h1>)"
            name = re.findall(pattern, modsite)[0]
            WorkshopItem = {'Name': name, 'ID': mods[i]['ID']}

            if False:
                # lastupdated
                pattern = "(?<=<div class=\"detailsStatRight\">).*?(?=<\/div>)"
                lastupdated = re.findall(pattern, modsite)[1]
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

                WorkshopItem = {'Name': name, 'ID': mods[i]['ID'], 'LastUpdated': lastupdated}
            mods[i] = WorkshopItem

    # deleting because for cannot be in variable range or smth
    amout_of_deleted = 0
    for i in todel:
        mods.pop(i - amout_of_deleted)
        amout_of_deleted += 1

    # add all known "mods made for server" server mods eg Perf fix, midround respawner
    # add custom submarine mods
    # remove outdated mods, print to face and in file that mods
    # sort?
    return mods

def generatelistOfMods(url_of_steam_collection):
    collection_site = collectionf(url_of_steam_collection)
    mods = get_listOfMods(collection_site)
    mods = get_modsnamelastupdated(mods)
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
        regularpackages += "      <!--" + mod['Name'] + "-->\n"
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