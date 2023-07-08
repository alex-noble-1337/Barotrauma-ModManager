import os
import datetime
from shutil import copyfile
import re
import shutil

# global vars
current_time = datetime.datetime.now()
current_time = current_time.replace(second=0, microsecond=0)
current_time = str(current_time)[0:-3]
current_time = re.sub('[:]', '.', current_time)
# configs
# backup folder location
backupfolder = "ConfigBackup"
# mods location
modslocation = "C:\\Users\\milord\\AppData\Local\\Daedalic Entertainment GmbH\\Barotrauma\\WorkshopMods\\Installed"

def config_files_find(filename):
    b_filename = filename.lower()
    check = False
    if b_filename.find("config") >= 0:
        check = True
    if b_filename.find("setting") >= 0:
        check = True
    if b_filename == "RunConfig.xml":
        check = True
    if b_filename == "configGui.lua":
        check = True
    return check
# find mods that have 'Lua' folder or 'CSharp' folder
# input: modslocation
# output: config files path from mods location: configfilespathfrommodslocation
def find_LuaCs_mods(modslocation):
    dir_list = os.listdir(modslocation)
    configfilespathfrommodslocation = []
    for moddir in dir_list:
        if os.path.isdir(os.path.join(modslocation, moddir)):
            moddir_x = os.path.join(modslocation, moddir)
            insidemoddir = os.listdir(moddir_x)
            if "Lua" in insidemoddir or "CSharp" in insidemoddir:
                # search in root
                for item in insidemoddir:
                    if config_files_find(item):
                        configfilespathfrommodslocation.append(os.path.join(modslocation, moddir, item))
            if "Lua" in insidemoddir:
                # search in lua
                moddir_x = os.path.join(moddir_x, "Lua")
                insidemoddir_x = os.listdir(moddir_x)
                for item in insidemoddir_x:
                    if config_files_find(item):
                        configfilespathfrommodslocation.append(os.path.join(modslocation, moddir, "Lua", item))
            if "CSharp" in insidemoddir:
                # search in CSharp
                moddir_x = os.path.join(moddir_x, "CSharp")
                insidemoddir_x = os.listdir(moddir_x)
                for item in insidemoddir_x:
                    if config_files_find(item):
                        configfilespathfrommodslocation.append(os.path.join(modslocation, moddir, "CSharp", item))
            if len(configfilespathfrommodslocation) <= 0:
                for item in insidemoddir:
                    if config_files_find(item):
                        configfilespathfrommodslocation.append(os.path.join(modslocation, moddir, item))
    return(configfilespathfrommodslocation)
# create backup folders and copy files
# input: configfilespathfrommodslocation
# output: nothing
def create_backup_folders_and_copy_files(configfilespathfrommodslocation, modslocation, backupfolder):
    backupconfigpaths = []
    for configfile in configfilespathfrommodslocation:
        temp = configfile.replace(modslocation, backupfolder)
        backupconfigpaths.append(temp)
    for i in range(len(configfilespathfrommodslocation)):
        minput = os.path.join(configfilespathfrommodslocation[i])
        moutput = backupconfigpaths[i]
        # print(minput + " -> " + moutput)
        if os.path.exists(os.path.dirname(moutput)) == False:
            os.makedirs(os.path.dirname(moutput))
        copyfile(minput, moutput)
def backup_option(modslocation, backupfolder):
    configfilespathfrommodslocation = find_LuaCs_mods(modslocation)
    logger.debug("[ConfigBackup]Moving configs from " + modslocation + " to " + backupfolder)
    create_backup_folders_and_copy_files(configfilespathfrommodslocation, modslocation,backupfolder)
    logger.debug("[ConfigBackup]Done backing up config files")

def get_configs_barotraumadir(barotraumadir):
    path_arr = []
    # barotraumadir/serversettings.xml
    path = os.path.join(barotraumadir, "serversettings.xml")
    if os.path.exists(path):
        path_arr.append(path)
    # barotraumadir/config_player.xml
    path = os.path.join(barotraumadir, "config_player.xml")
    if os.path.exists(path):
        path_arr.append(path)
    # barotraumadir/LuaCsSetupConfig.xml
    path = os.path.join(barotraumadir, "LuaCsSetupConfig.xml")
    if os.path.exists(path):
        path_arr.append(path)
    # barotraumadir/hintmanager.xml
    path = os.path.join(barotraumadir, "hintmanager.xml")
    if os.path.exists(path):
        path_arr.append(path)
    # barotraumadir/creature_metrics.xml
    path = os.path.join(barotraumadir, "creature_metrics.xml")
    if os.path.exists(path):
        path_arr.append(path)
    # barotraumadir/Config/*
    path = os.path.join(barotraumadir, "Config")
    for src_dir, dirs, files in os.walk(path):
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            path_arr.append(src_file)
    # barotraumadir/Data/*
    path = os.path.join(barotraumadir, "Data")
    for src_dir, dirs, files in os.walk(path):
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            path_arr.append(src_file)

    return path_arr
def get_configs_localcopypath(modslocation):
    configfilespathfrommodslocation = find_LuaCs_mods(modslocation)
    return configfilespathfrommodslocation
def get_saves(savedir):
    path_arr = []
    for src_dir, dirs, files in os.walk(savedir):
        for file_ in files:
            if file_.find(".save") >= 0 or file_.find("_CharacterData.xml") >= 0:
                src_file = os.path.join(src_dir, file_)
                path_arr.append(src_file)
    return path_arr
def backupBarotraumaData(barotrauma_dir, mods_dir, save_dir, backup_dir, max_saves):
    if os.path.exists(backup_dir):
        directory_contents = os.listdir(backup_dir)
        if len(directory_contents) >= max_saves:
            directory_contents.sort()
            number_to_remove = len(directory_contents) - max_saves + 1
            for i in range(number_to_remove):
                shutil.rmtree(os.path.join(backup_dir, directory_contents[i]))
    # getting paths into reasonable length
    # TODO readme about how to bring back that folder paths
    files_path_arr = []
    files_path_arr_out = []
    files_path_arr_temp = get_configs_barotraumadir(barotrauma_dir)
    files_path_arr.extend(files_path_arr_temp)
    for i in range(len(files_path_arr_temp)):
        if barotrauma_dir[len(barotrauma_dir)-1] == '/' or  barotrauma_dir[len(barotrauma_dir)-1] == '\\':
            barotrauma_dir = barotrauma_dir[0:len(barotrauma_dir)-1]
        files_path_arr_temp[i] = os.path.join(backup_dir, current_time, files_path_arr_temp[i].replace(barotrauma_dir, "barotrauma_dir"))
    files_path_arr_out.extend(files_path_arr_temp)
    files_path_arr_temp = get_configs_localcopypath(mods_dir)
    files_path_arr.extend(files_path_arr_temp)
    for i in range(len(files_path_arr_temp)):
        if mods_dir[len(mods_dir)-1] == '/' or  mods_dir[len(mods_dir)-1] == '\\':
            mods_dir = mods_dir[0:len(mods_dir)-1]
        files_path_arr_temp[i] = os.path.join(backup_dir, current_time, files_path_arr_temp[i].replace(mods_dir, "mods_dir"))
    files_path_arr_out.extend(files_path_arr_temp)
    files_path_arr_temp = get_saves(save_dir)
    files_path_arr.extend(files_path_arr_temp)
    for i in range(len(files_path_arr_temp)):
        if save_dir[len(save_dir)-1] == '/' or  save_dir[len(save_dir)-1] == '\\':
            save_dir = save_dir[0:len(save_dir)-1]
        files_path_arr_temp[i] = os.path.join(backup_dir, current_time, files_path_arr_temp[i].replace(save_dir, "save_dir"))
    files_path_arr_out.extend(files_path_arr_temp)

    for i in range(len(files_path_arr)):
        file_path_arr = files_path_arr[i]
        file_path_arr_out = files_path_arr_out[i]
        # copy from file_path_arr to file_path_arr_out
        os.makedirs(os.path.dirname(file_path_arr_out),exist_ok=True)
        shutil.copy2(file_path_arr, file_path_arr_out)