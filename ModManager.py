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

# progress bar stuff
try:
    from tqdm import tqdm
except ImportError:
    print("Trying to Install required module: tqdm\n")
    os.system('python3 -m pip install tqdm')
from tqdm import tqdm


# from ConfigRecoder import get_modsnamelastupdated 
from configbackup import backup_option
from ConfigRecoder import generatelistOfMods 
from ConfigRecoder import collectionf
from ConfigRecoder import get_modsData_individual
from configbackup import backupBarotraumaData


# set up all default values and paths
def set_required_values():
    options_arr = sys.argv[1:]

    changed_barotrauma_path = False
    changed_tool_path = False
    changed_steamcmd_path = False
    collectionmode = False
    save_dir = ""
    max_saves = ""

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
                if tempval > 2:
                    if options_arr[i+1] == "pwd":
                        barotrauma_path = os.getcwd()
                        changed_barotrauma_path = True
                    else:
                        barotrauma_path = options_arr[i+1]
                        changed_barotrauma_path = True
                else:
                    barotrauma_path = os.getcwd()
                    changed_barotrauma_path = True
            
            # --toolpath or -t - path to the ModManager Direcotry where script can put all the "cashe" files. set it do default if you dont know where or what you are doing. Must be a path to THE FOLDER.  Does not accept ""
            if options_arr[i] == '--toolpath' or options_arr[i] == '-t':
                if tempval > 2:
                    if options_arr[i+1] == "pwd":
                        tool_path = os.getcwd()
                        changed_tool_path = True
                    else:
                        tool_path = options_arr[i+1]
                        changed_tool_path = True
                else:
                    tool_path = os.getcwd()
                    changed_tool_path = True

            # --steamcmdpath or -s - path to your steamcmd or steamcmd.exe. Must be a path to THE FOLDER, not the program itself.  Does not accept ""
            if options_arr[i] == '--steamcmdpath' or options_arr[i] == '-s':
                if tempval > 2:
                    if options_arr[i+1] == "pwd":
                        if sys.platform == 'win32':
                            location_with_steamcmd = os.path.join(os.getcwd(), "steamcmd.exe")
                        else:
                            location_with_steamcmd = os.path.join(os.getcwd(), "steamcmd.sh")
                        changed_steamcmd_path = True
                    else:
                        location_with_steamcmd = options_arr[i+1]
                        changed_steamcmd_path = True
                else:
                    location_with_steamcmd = options_arr[i+1]
                    changed_steamcmd_path = True

            # TODO add it to the documentaton
            if options_arr[i] == '--collection' or options_arr[i] == '-c':
                if tempval > 3:
                    # TODO check if link is good
                    collection_link = options_arr[i+1]
                    collectionmode = True
                    localcopy_path_override = options_arr[i+2]
                
             # TODO add it to the documentaton
            if options_arr[i] == '--performancefix' or options_arr[i] == '-p':
                if tempval >= 1:
                    global addperformacefix
                    addperformacefix = True

            # TODO add it to the documentaton
            if options_arr[i] == '--backup':
                if tempval >= 3:
                    # TODO check if link is good
                    max_saves = options_arr[i+1]
                    save_dir = options_arr[i+2]

    # setting up default values and path handling
    if not changed_barotrauma_path:
        barotrauma_path = default_barotrauma_path
    if not os.path.isabs(barotrauma_path):
        barotrauma_path = os.path.join(os.getcwd(), barotrauma_path)
    if not changed_tool_path:
        tool_path = default_tool_path
    if not changed_steamcmd_path:
        location_with_steamcmd = default_steamcmd_path
    if default_steamdir_path == "":
        steamdir_path = os.path.join(tool_path, "steamdir")
    else:
        steamdir_path = default_steamdir_path
    
    input_options = {'barotrauma': barotrauma_path, 'tool': tool_path, 'steamcmd': location_with_steamcmd, 'steamdir': steamdir_path, 'save_dir': save_dir, 'max_saves': max_saves}
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

# get from config_player.xml, everything inside <regularpackages/> </regularpackages>
def get_regularpackages(barotrauma_path):
    # trying to access filelist
    try:
        filelist_path = os.path.join(barotrauma_path, "config_player.xml")
        with open(filelist_path, "r", encoding='utf8') as f:
            filelist_str = f.read()
    except Exception as e:
        print("[ModManager] Could not find the config_player.xml! Check your barotrauma path!")
        print(e)

    pattern = "(?<=<regularpackages>)[\s\S]*?(?=<\/regularpackages>)"
    regularpackages = re.findall(pattern, filelist_str)
    if len(regularpackages) <= 0:
        # patch for </regularpackages>, just in case
        # TODO a bit stupid, so rework it
        # print("<regularpackages/>")
        # print("<regularpackages>\n\t\t</regularpackages>")
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
            # print(os.path.join(src_dir, file_))
            new_modificationtime = os.path.getmtime(os.path.join(src_dir, file_))
            if new_modificationtime > modificationtime:
                modificationtime = new_modificationtime

    # modificationtime = 1673542320
    return modificationtime

# get localcopy path from filelist
def get_localcopy_path(filelist_str):
    pattern = "(?<=path=\")(.*?)(?=\/filelist\.xml)"
    path = re.findall(pattern, filelist_str)
    if len(path) > 0:
        path = path[0].split("/")
        new_path = ""
        for i in range(len(path)-2):
            if sys.platform == "win32":
                new_path += path[i] + "/"
            else:
                new_path += path[i] + "/"
        new_path += path[len(path)-2]
        return new_path
    else:
        return ""

# find mods to update from config_player.xml
def get_listOfModsfromConfig(filelist_str,localcopy_path):
    # filelist.xml" />
    modlist = []
    filelist_str = filelist_str.splitlines()
    for ix in range(len(filelist_str)):
        if re.match(".*?<package.*?", filelist_str[ix]):
            # get name into mod_name
            if ix-1 >= 0:
                name_filelist_str = filelist_str[ix-1]
            else:
                name_filelist_str = ""
            pattern = "(?<=<!--)(.*?)(?=-->)"
            mod_name = re.findall(pattern, name_filelist_str)
            if len(mod_name) > 0:
                mod_name = mod_name[0]
            else:
                mod_name = ""

            # get id into mod_id
            id_filelist_str = filelist_str[ix+1]
            pattern = '(?<=path=")(.*?)(?=\/filelist\.xml)'
            mod_id = re.findall(pattern, id_filelist_str)
            if len(mod_id) > 0:
                mod_id = mod_id[0]
            else:
                mod_id = ""
            if sys.platform == "win32":
                mod_id = mod_id.replace('/', '\\')
            mod_id = mod_id.replace(localcopy_path + "/", "")


            modlist.append({'Name': mod_name, 'ID': mod_id})

    #         pattern = "(?<=<package)[\s\S]*?(?=\/filelist\.xml)"
    # modlist_str = re.findall(pattern, filelist_str)
    
    
    
    # for mod in modlist_str:
    #     pattern = "(?<=^)(.*?)(?=-->)"
    #     mod_name = re.findall(pattern, mod)
    #     if len(mod_name) > 0:
    #         mod_name = mod_name[0]
    #     else:
    #         mod_name = ""
    #     pattern = '(?<=path=")(.*?)(?=$)'
    #     mod_id = re.findall(pattern, mod)
    #     if len(mod_id) > 0:
    #         mod_id = mod_id[0]
    #     else:
    #         mod_id = ""
    #     if sys.platform == "win32":
    #         mod_id = mod_id.replace('/', '\\')
    #     mod_id = mod_id.replace(localcopy_path + "/", "")
        
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
            Exception("[ModManager] SteamCMD could not be found! check your paths!")

def print_modlist(modlist):
    print("[ModManager] List of mods:")
    for mod in modlist:
        if str(mod["ID"]) == "2701251094":
            has_performancefix = True
        print("[ModManager] "+ str(mod["ID"]) + ": " + mod["Name"])
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

def create_newfilelist(modlist, localcopy_path_og, barotrauma_path):
    regularpackages_new = "\n"
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

        regularpackages_new += "      <!--" + mod['Name'] + "-->\n"
        regularpackages_new += "      <package\n"
        regularpackages_new += "        path=\"" + temp_localcopy_path + "/" + mod['ID'] + "/filelist.xml\" />\n"
    regularpackages_new += "    "
    return regularpackages_new

def save_managedmods(managed_mods, managed_mods_path):
    managed_mods_str = ""
    for managed_mod in managed_mods:
        managed_mods_str += managed_mod + "\n"
    with open(managed_mods_path, "w", encoding='utf8') as f:
        f.write(managed_mods_str)

def myprint(mssg, bar = 'bar'):
    if progressbar_functionality:
        bar.write(mssg)
    else:
        print(mssg)

# usage of steamcmd on modlist
def download_modlist(modlist, tool_path, steamdir_path, location_with_steamcmd):
    numberofupdatedmods = 0
    # '], where l_bar='{desc}: {percentage:3.0f}%|' and r_bar='| {n_fmt}/{total_fmt}{postfix} [{elapsed}<{remaining}, ' '{rate_fmt}]
    total_time = 0
    with tqdm(total=len(modlist), dynamic_ncols = True, ascii = True, unit="Mods", position=0, bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}Mods [E:{elapsed} R:{remaining}]", desc = "Update Progress: ", disable = not progressbar_functionality) as bar:
        iterator = 0
        # bar.update()
        for mod in modlist:
            pattern = "^\d*?$"
            if re.match(pattern, mod["ID"]):
                one_time = int(round(time.time()))
                # main part running moddlownloader
                mssg = "[ModManager] Starting steamcmd, Updating mod:" + mod["ID"] + ": " + mod["Name"]
                if progressbar_functionality == False:
                    mssg += "     Update Progress: " + str(iterator+1) + "/" + str(len(modlist))
                    number = int(abs((len(modlist) - iterator - 1)*(total_time / len(modlist))))
                    mssg += " ETA:" + str(str(number//60) + ":" + str(number%60))
                myprint(mssg, bar)
                # TODO make output of steamcmd less spammy/silent
                # TODO instead of steamcmd downloading one mod at the time, make it download all of them in one start of steamcmd using steamcmd scripts or cmd line arguments
                proc = moddownloader(mod["ID"],tool_path, steamdir_path, location_with_steamcmd)
                for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
                    line = line.rstrip()
                    # steam connection check
                    if re.match(".*?" + "Connecting anonymously to Steam Public...OK" + ".*?", line):
                        # myprint("[Steamcmd]" + line)
                        myprint("[ModManger]Connected to steam! Beginning mod download...", bar)
                        # iterator += 1
                        # bar.update(iterator)
                        # bar.update()
                    # starting download
                    if re.match(".*?Downloading item " + mod["ID"] + ".*?", line):
                        # myprint("[Steamcmd]" + line)
                        myprint("[ModManager] Downloading mod: " + mod["Name"] + " (" + mod["ID"] + ")", bar)
                        # iterator += 1
                        # bar.update(iterator)
                        # bar.update()
                    # download complete
                    if re.match(".*?Success. Downloaded item " + mod["ID"] + ".*?", line):
                        # check if mod has been downloaded in correct path
                        if re.match(".*?\"" + steamdir_path + ".*?steamapps.*?workshop.*?content.*?602960.*?" + mod["ID"] + "\".*?", line):
                            myprint("[ModManager] Downloaded mod!", bar)
                            # iterator += 1
                            # bar.update(iterator)
                            # bar.update()
                        else:
                            raise Exception("[ModManager] Steamcmd has downloaded mod in wrong directory! Please make sure that steamdir path is up to specifications in README\n[Steamcmd]" + str(line))
                    # else:
                        # myprint(line)
                proc.wait()
                output = proc.returncode
                if output == 0:
                    numberofupdatedmods += 1
                    iterator += 1
                    bar.update(1)
                    one_time -= int(round(time.time()))
                    total_time += one_time
                    myprint("", bar)
                else:
                    raise Exception("[ModManager] Steamcmd return code is not 0! That means steamcd had problems!" + str(proc.errors))
            else:
                iterator += 1
                myprint("[ModManager] Skipped mod!: " + mod["Name"] + " (" + mod["ID"] + ")", bar)
                bar.update(1)
                myprint("", bar)
            # iterator += 1
            # bar.update(iterator)
    print("")
    return numberofupdatedmods

def get_old_managed_mods(tool_path, managed_mods_path):
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

def set_not_managedmods(old_managed_mods, modlist, localcopy_path_og, managed_mods):
    not_managedmods = old_managed_mods
    # removeing mods that exist in modlist
    for modwithdir in managed_mods:
        if modwithdir in not_managedmods:
            not_managedmods.remove(modwithdir)
    return not_managedmods

def main(requiredpaths):
    global max_value
    max_value = 1

    warning_LFBnotinstalled = False
    warning_modlistislong = False
    warning_modlistissuperlong = False

    barotrauma_path = requiredpaths['barotrauma']
    tool_path = requiredpaths['tool']
    location_with_steamcmd = requiredpaths['steamcmd']
    steamdir_path = requiredpaths['steamdir']
    if 'collection_link' in requiredpaths and 'localcopy_path_override' in requiredpaths:
        collectionmode = True
        localcopy_path_override = requiredpaths['localcopy_path_override']
        collection_link = requiredpaths['collection_link']
        lastupdated_functionality = True
    else:
        collectionmode = False
        lastupdated_functionality = False
    save_dir = requiredpaths['save_dir']
    max_saves = requiredpaths['max_saves']

    regularpackages = get_regularpackages(barotrauma_path)
    old_regularpackages = regularpackages
    managed_mods_path = os.path.join(tool_path, "managed_mods.txt")
    old_managed_mods = get_old_managed_mods(tool_path, managed_mods_path)


    # collection save file
    collection_file_path = os.path.join(tool_path, "collection_save.txt")
    if flush_previous_col:
        if os.path.exists(collection_file_path):
            os.remove(collection_file_path)
    elif os.path.exists(collection_file_path):
        collection_file = ""
        with open(collection_file_path, "r", encoding='utf8') as f:
            collection_file = f.read()
        arr = collection_file.split(" ")
        collection_link = arr[0]
        localcopy_path_override = arr[1]
        
    # check collection link if it is valid
    isvalid_collection_link = False
    if collection_link != "":
        if re.match("https:\/\/steamcommunity\.com\/sharedfiles\/filedetails\/\?id=", collection_link):
            collection_site = collectionf(collection_link)
            if collection_site != "ERROR":
                isvalid_collection_link = True

    modlist = []
    if addperformacefix == True:
        WorkshopItem = {'Name': "Performance Fix", 'ID': "2701251094"}
        modlist.insert(0, WorkshopItem)

    requreslua = False
    requrescs = False
    hascs = False
    if isvalid_collection_link and localcopy_path_override != "":
        collectionmode = True
        lastupdated_functionality = True
        dependencies_functionality = debug_dependencies_functionality
        print("[ModManager] Collection mode ENABLED, Downloading collection data (This might take a sec)")
        localcopy_path_og = localcopy_path_override
        modlist = generatelistOfMods(collection_site, modlist, {'addnames': True, 'addlastupdated': lastupdated_functionality, 'dependencies': dependencies_functionality})
        with open(collection_file_path, "w", encoding='utf8') as f:
            f.write(collection_link + " " + localcopy_path_og)
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
        collectionmode = False
        lastupdated_functionality = False
        print("[ModManager] Collection mode DISABLED, Downloading data from config_player.xml")
        if localcopy_path_override == "":
            localcopy_path_og = get_localcopy_path(regularpackages)
        else:
            localcopy_path_og = localcopy_path_override
        modlist.extend(get_listOfModsfromConfig(regularpackages,localcopy_path_og))
    
    for mod in modlist:
        if mod['ID'] == '2795927223':
            hascs = True
        if mod['ID'] == '2559634234':
            haslua = True
    localcopy_path = localcopy_path_og

    if save_dir != "" and max_saves != "":
        max_saves = int(max_saves)
        backupBarotraumaData(barotrauma_path, localcopy_path_og, save_dir, os.path.join(tool_path, "backup"), max_saves)

    if (not requreslua) or (not requrescs):
        for mod in modlist:
            if mod['ID'] == '2559634234':
                requreslua = True
            if mod['ID'] == '2795927223':
                requrescs = True

    if requreslua or requrescs:
        if not os.path.exists(os.path.join(barotrauma_path, "LuaCsSetupConfig.xml")):
            warning_LFBnotinstalled = True
        # else:
        #     if requrescs:
        #         if debug_set_forced_cs:
        #             with open(os.path.join(barotrauma_path, "LuaCsSetupConfig.xml"), "r", encoding='utf8') as LuaCsSetupConfigf:
        #                 LuaCsSetupConfig = LuaCsSetupConfigf.read()
        #             LuaCsSetupConfig = LuaCsSetupConfig.replace("ForceCsScripting Value=\"Boolean\">False", "ForceCsScripting Value=\"Boolean\">True")
        #             with open(os.path.join(barotrauma_path, "LuaCsSetupConfig.xml"), "w", encoding='utf8') as LuaCsSetupConfigf:
        #                 LuaCsSetupConfigf.write(LuaCsSetupConfig)

    if requrescs:
        if hascs == False:
            # TODO kind hacky way to do this
            temp_luacs = [{'Name': "Cs For Barotrauma", 'ID': "2795927223"}]
            temp_luacs = get_modsData_individual(temp_luacs, lastupdated_functionality, lastupdated_functionality)
            modlist.extend(temp_luacs)

    modlist = remove_duplicates(modlist)
    # modless?
    if len(modlist) == 0:
        print("[ModManager] No mods detected")
        return 
    else:
        numberofmodsminusserverside = len(modlist) - int(haslua) - int(hascs)
        print_modlist(modlist)
    
    modlist_inlocalcopy = []
    for modid in os.listdir(localcopy_path):
        if re.match("^\d*?$", modid):
            modlist_inlocalcopy.append(modid)
            # if os.path.exists(os.path.join(localcopy_path, "filelist.xml")):
                # check if mods update time is lower than modified time of file if so remove it from modlist
            
    
    # # more and equal to 20
    # if warning_modlistislong:
    #     sys.stdout.write("\033[1;31m")
    #     print("[ModManager] I advise to shorten your modlist! It is very rare for players to join public game that has a lot of mods.\nPlease shorten your modlist by removing unnesesary mods, or use group of mods inside of one package.")
    #     sys.stdout.write("\033[0;0m")
    #     time.sleep(20/2)
    # # more and equal to 30
    # if warning_modlistissuperlong:
    #     sys.stdout.write("\033[1;31m")
    #     print("[ModManager] I STRONGLY ADVISE TO SHORTEN YOUR MODLIST! It is very rare for players to join public game that has a lot of mods.\nPlease shorten your modlist by removing unnesesary mods, or use group of mods inside of one package.")
    #     sys.stdout.write("\033[0;0m")
    #     time.sleep(30/2)

    # 1. Path fixing
    if not os.path.isabs(tool_path):
        tool_path = os.path.join(os.getcwd(), tool_path)
    # if not os.path.isabs(location_with_steamcmd):
    #     location_with_steamcmd = os.path.join(os.getcwd(), location_with_steamcmd)
    if not os.path.isabs(steamdir_path):
        steamdir_path = os.path.join(os.getcwd(), steamdir_path)
    newinputdir = os.path.join(steamdir_path, "steamapps", "workshop", "content", "602960")
    if os.path.exists(steamdir_path):
        shutil.rmtree(steamdir_path)
    os.mkdir(steamdir_path)
    steamdir_path = os.path.realpath(steamdir_path)
    # if os.path.isabs(localcopy_path):
    #     localmods_path = os.path.abspath(localcopy_path)
    # else:
    #     localmods_path = os.path.join(default_barotrauma_path, localcopy_path)
    if not os.path.isabs(localcopy_path):
        localcopy_path = os.path.join(os.getcwd(), localcopy_path)

    # 2. get managed mods and not managed mods
    managed_mods = get_managedmods(modlist, localcopy_path_og)
    not_managedmods = set_not_managedmods(old_managed_mods, modlist, localcopy_path_og, managed_mods)

    # 3. re-create config_player
    regularpackages_new = create_newfilelist(modlist, localcopy_path_og, barotrauma_path)
    filelist_path = os.path.join(barotrauma_path, "config_player.xml")
    with open(filelist_path, "r", encoding='utf8') as f:
        filelist_str = f.read()
    filelist_str = filelist_str.replace(regularpackages, regularpackages_new)
    with open(filelist_path, "w", encoding='utf8') as f:
        f.write(filelist_str)


    # 4. saving managed mods
    save_managedmods(managed_mods, managed_mods_path)

    # lastupdated functionality
    if collectionmode and lastupdated_functionality:
        remove_arr = []
        # TODO current slowing time is about 
        # TODO lastupdated skip for windows and mac
        for mod in modlist:
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
        for item_to_remove in remove_arr:
            if item_to_remove in modlist:
                modlist.remove(item_to_remove)

    # main part running moddlownloader
    numberofupdatedmods = download_modlist(modlist, tool_path, steamdir_path, location_with_steamcmd)
    print("\n")
    if collectionmode and lastupdated_functionality:
        print("[ModManager] Skipping download of " + str(len(remove_arr)) + " Already up to date Mods. (if any issues arrise please remove every mod from your localcopy directory)")
    print("[ModManager] All "+ str(numberofupdatedmods) +" Mods have been updated")
    print("[ModManager] Downloading mods complete!")

    # 1. config backup and conservation
    baseconfig_path = os.path.join(tool_path, "BestDefaultConfigsTM")
    backup_option(baseconfig_path,newinputdir)
    backup_option(localcopy_path,newinputdir)

    # 2. remove not_managedmods
    print("[ModManager] Removing " + str(len(not_managedmods)) + " not managed now mods!")
    for not_managedmod in not_managedmods:
        if os.path.exists(not_managedmod):
            shutil.rmtree(not_managedmod)

    # 3. + numberofupdatedmods actually moving mods to localcopy
    for mod in modlist:
        robocopysubsttute(os.path.join(newinputdir, mod['ID']), os.path.join(localcopy_path, mod['ID']))


    # 4. finishing anc cleaning up
    # removing steamdir because steamcmd is piece of crap and it sometimes wont download mod if its in directory
    shutil.rmtree(steamdir_path)
    print("[ModManager] Mods Updated!\n")

    # checking if mod is pure server-side or client side
    numberofluamods = 0
    for mod in modlist:
        if os.path.exists(os.path.join(localcopy_path, mod['ID'], "filelist.xml")):
            with open(os.path.join(localcopy_path, mod['ID'], "filelist.xml"), "r", encoding='utf8') as f:
                filelist = f.readlines()
            xmlitems = 0
            for ix in range(2, len(filelist)):
                xmlitems += len(re.findall(".xml", filelist[ix]))
            if xmlitems <= 0:
                numberofluamods += 1
    
    if numberofmodsminusserverside - numberofluamods >= 30 and not disablewarnings:
        warning_modlistissuperlong = True
    elif numberofmodsminusserverside - numberofluamods >= 20 and not disablewarnings:
        warning_modlistislong = True

    if warning_LFBnotinstalled:
        sys.stdout.write("\033[1;31m")
        print("[ModManager] WARNING Lua for barotrauma NOT INSTALLED, and is needed!\nInstall Lua for barotrauma then re-run script!")
        sys.stdout.write("\033[0;0m")
        time.sleep(20)

    # more and equal to 30
    if warning_modlistissuperlong:
        sys.stdout.write("\033[1;31m")
        print("[ModManager] I STRONGLY ADVISE TO SHORTEN YOUR MODLIST! It is very rare for players to join public game that has a lot of mods.\n[ModManager] Please shorten your modlist by removing unnesesary mods, or use group of mods inside of one package.")
        sys.stdout.write("\033[0;0m")
        time.sleep(30)
    # more and equal to 30
    elif warning_modlistislong:
        sys.stdout.write("\033[1;31m")
        print("[ModManager] I advise to shorten your modlist! It is very rare for players to join public game that has a lot of mods.\n[ModManager] Please shorten your modlist by removing unnesesary mods, or use group of mods inside of one package.")
        sys.stdout.write("\033[0;0m")
        time.sleep(20)

if __name__ == '__main__':
    print("Wellcome to ModManager script!")
    requiredpaths = set_required_values()
    # print("\n")
    while(True):
        if os.path.exists(os.path.join(requiredpaths['tool'], "collection_save.txt")):
            print("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands.")
            print("[ModManager] Steam collection mode enabled! Disable by entering collection sub-menu.")
            print("[ModManager] Do you want to update that collection of mods? ((Y)es / (n)o): ")
        else: 
            print("[ModManager] Type \'h\' or \'help\' then enter for help and information about commands.")
            print("[ModManager] Steam collection mode disabled! Disable by entering collection sub-menu.")
            print("[ModManager] Do you want to update mods? ((Y)es / (n)o): ")
        newinput = input()
        if newinput.lower() == "yes" or newinput.lower() == "y":
            main(requiredpaths)
            break
        elif newinput.lower() == "no" or newinput.lower() == "n":
            break
        elif newinput.lower() == "collection" or newinput.lower() == "c":
            print("[ModManager] Provide an collection link then press enter, or if you want to disable previously enabled collection mode, type 'n' then enter: ")
            op_collection_url = input()
            if op_collection_url.lower() != "n":
                print("[ModManager] Provide an localcopy path (if you dont know what to input, type 'LocalMods') then press enter: ")
                op_localcopy_path = input()
            else:
                op_collection_url = ""
                op_localcopy_path = ""
            flush_previous_col = True
            # TODO collection check, if link is valid
            requiredpaths['collection_link'] = op_collection_url
            requiredpaths['localcopy_path_override'] = op_localcopy_path
            requiredpaths['collectionmode'] = True
            main(requiredpaths)
            break
        elif newinput.lower() == "kill" or newinput.lower() == "exit":
            break
        elif newinput.lower() == "help" or newinput.lower() == "h":
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
            print("\t- Replace all occurences \"C:/Users/$yourusername$/AppData/Local/Daedalic Entertainment GmbH/Barotrauma/WorkshopMods/Installed\" (your personal machine mod's path) where \"$yourusername$\" is your user name on windows machine, to \"LocalMods\"")
            continue
        print("[ModManager] Provide a valid anwser: \"y\" or \"yes\" / \"n\" or \"no\"")
        