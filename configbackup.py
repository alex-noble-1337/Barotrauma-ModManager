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

def config_files_find(fileitem):
    b_fileitem = fileitem.lower()
    return(b_fileitem.find("config") >= 0 and b_fileitem.find("default") == -1 and (not b_fileitem == "RunConfig.xml".lower()) and (not b_fileitem == "configGui.lua".lower()))

# configs
# backup folder location
backupfolder = "ConfigBackup"
# mods location
modslocation = "C:\\Users\\milord\\AppData\Local\\Daedalic Entertainment GmbH\\Barotrauma\\WorkshopMods\\Installed"

# find mods that have 'Lua' folder or 'CSharp' folder
def find_mods_that_have_Lua_folder_or_CSharp_folder(modslocation):
    # input: modslocation
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
    # output: config files path from mods location: configfilespathfrommodslocation

# create backup folders and copy files
def create_backup_folders_and_copy_files(configfilespathfrommodslocation, modslocation, backupfolder):
    # input: configfilespathfrommodslocation
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
    # output: nothing/error

def backup_option(modslocation, backupfolder):
    # print what you do
    # print("[ConfigBackup]Moving configs from " + modslocation + " to " + backupfolder)
    configfilespathfrommodslocation = find_mods_that_have_Lua_folder_or_CSharp_folder(modslocation)
    create_backup_folders_and_copy_files(configfilespathfrommodslocation, modslocation,backupfolder)
    # print done
    # print("[ConfigBackup]Done backing up config files")

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
    configfilespathfrommodslocation = find_mods_that_have_Lua_folder_or_CSharp_folder(modslocation)
    return configfilespathfrommodslocation
def get_saves(savedir):
    path_arr = []
    for src_dir, dirs, files in os.walk(savedir):
        for file_ in files:
            # get .save s
            # get _CharacterData.xml s
            if file_.find(".save") >= 0 or file_.find("_CharacterData.xml") >= 0:
                src_file = os.path.join(src_dir, file_)
                path_arr.append(src_file)
    return path_arr

def backupBarotraumaData(barotrauma_dir, mods_dir, save_dir, backup_dir):
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

def main():
    # backup folder location
    global backupfolder
    backupfolder = "ConfigBackup"
    # mods location
    global modslocation
    modslocation = "LocalMods"

    option = "backup"
    if option == "backup":
        backup_option(modslocation, backupfolder)
    elif option == "bringback":
        # Newest
        dir_list = os.listdir(backupfolder)
        dir_list.sort(reverse=True)

        backupfolder = os.path.join(backupfolder, dir_list[0])
        # print("[ConfigBackup]Moving configs from " + backupfolder + " to " + modslocation)
        dir_list = os.listdir(backupfolder)


        backupconfigs = find_mods_that_have_Lua_folder_or_CSharp_folder(backupfolder, pattern)
        realconfigs = []
        for config in backupconfigs:
            realconfigs.append(os.path.join(modslocation, config))
        # print(backupconfigs)
        for i in range(len(backupconfigs)):
            minput = os.path.join(backupfolder, backupconfigs[i])
            moutput = realconfigs[i]
            print(minput + " -> " + moutput)
            if os.path.exists(os.path.dirname(moutput)) == False:
                os.makedirs(os.path.dirname(moutput))
                copyfile(minput, moutput)
            elif os.path.exists(moutput) == False:
                copyfile(minput, moutput)
            else:
                os.remove(moutput)
                copyfile(minput, moutput)

                

        # modsconfigs = find_mods_that_have_Lua_folder_or_CSharp_folder(modslocation)
        # modsconfigs1 = []
        # for config in modsconfigs:
        #     modsconfigs1.append(os.path.join(modslocation, config))
        # modsconfigs = modsconfigs1
        # print(modsconfigs)


# if __name__ == '__main__':
    # backupBarotraumaData("/mnt/Share/SteamLibrary/steamapps/common/Barotrauma", "/mnt/Share/milord/.local/share/Daedalic Entertainment GmbH/Barotrauma/WorkshopMods/Installed", "/mnt/Share/milord/.local/share/Daedalic Entertainment GmbH/Barotrauma", "Backup")
    # main()