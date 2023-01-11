#!/usr/bin/python
from xml.dom import minidom, getDOMImplementation
import base64
import gzip
import sys
import os
import re
import shutil
import requests

def get_htm_of_collection_site(link):
    response = requests.get(link, timeout=200)
    if response.status_code == 200:
        return response.text
    else:
        # coundt be bothered to do it other way
        return "ERROR"

def get_listOfMods(url_of_steam_collection, collection_site):
    if collection_site != "ERROR":
        pattern = "(?<=<a href=\"https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=).*?(?=\"><div class=\"workshopItemTitle\">)"
        arrx = re.findall(pattern, collection_site)
    return arrx

if len(sys.argv) >= 3:
    option = str(sys.argv[1])
    fileposition = str(sys.argv[2])
else:
    option = "-c"

if option == "-t" or option == "--textfile":
    output_file = ""
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

    with open(name_of_the_file + ".csv", "w+") as textfile:
        textfile.write(output_file)

elif option == "-c" or option == "--collection":
    print("Running in collection mode")
    url_of_steam_collection = "https://steamcommunity.com/sharedfiles/filedetails/?id=2800347733"
    collection_site = get_htm_of_collection_site(url_of_steam_collection)
    # get list of all mod's id's in the collection in an array
    modsids = get_listOfMods(url_of_steam_collection, collection_site)
    # iterate array to get names of mods
    mods = []
    for i in range(len(modsids)):
        # order names in the same array positions
        pattern = "(?<=id=" + str(modsids[i]) + "\"><div class=\"workshopItemTitle\">).*?(?=<\/div>)"
        name = str(re.findall(pattern, collection_site)[0])
        WorkshopItem = {'Name': name, 'ID': modsids[i]}
        mods.append(WorkshopItem)



    # Lua and cs
    runluaupdater = False
    for i in range(len(mods)):
        # remove Lua and cs from the list
        if mods[i]["ID"] == 2559634234 or mods[i]["ID"] == 2795927223:
            mods.pop(i)
            runluaupdater = True
        # check for lua dependendecies and populate time of update of workshop item
        else:
            modurl = "https://steamcommunity.com/sharedfiles/filedetails/?id=" + str(mods[i]["ID"])
            modsite = get_htm_of_collection_site(modurl)
<a href="https://steamcommunity.com/workshop/filedetails/?id=2559634234" target="_blank">.*?<div class="requiredItem">.*?Lua For Barotrauma



    # add all known "mods made for server" server mods eg Perf fix, midround respawner
    # add custom submarine mods
    # remove outdated mods, print to face and in file that mods
    # sort?
    print(mods)
    