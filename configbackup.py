import os
import datetime
from shutil import copyfile
import re


# global vars
current_time = datetime.datetime.now()
current_time = current_time.replace(second=0, microsecond=0)
current_time = str(current_time)[0:-3]
current_time = re.sub('[:]', '.', current_time)

def config_files_find(fileitem):
    return(fileitem.find("config") >= 0 and fileitem.find("default") == -1)

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
        moddir_x = os.path.join(modslocation, moddir)
        insidemoddir = os.listdir(moddir_x)
        if "Lua" in insidemoddir or "CSharp" in insidemoddir:
            # search in root
            for item in insidemoddir:
                if config_files_find(item):
                    configfilespathfrommodslocation.append(os.path.join(moddir, item))
        if "Lua" in insidemoddir:
            # search in lua
            moddir_x = os.path.join(moddir_x, "Lua")
            insidemoddir_x = os.listdir(moddir_x)
            for item in insidemoddir_x:
                if config_files_find(item):
                    configfilespathfrommodslocation.append(os.path.join(moddir, "Lua", item))
        if "CSharp" in insidemoddir:
            # search in CSharp
            moddir_x = os.path.join(moddir_x, "CSharp")
            insidemoddir_x = os.listdir(moddir_x)
            for item in insidemoddir_x:
                if config_files_find(item):
                    configfilespathfrommodslocation.append(os.path.join(moddir, "CSharp", item))
        if len(configfilespathfrommodslocation) <= 0:
            for item in insidemoddir:
                if config_files_find(item):
                    configfilespathfrommodslocation.append(os.path.join(moddir, item))
    return(configfilespathfrommodslocation)
    # output: config files path from mods location: configfilespathfrommodslocation

# create backup folders and copy files
def create_backup_folders_and_copy_files(configfilespathfrommodslocation, modslocation, backupfolder):
    # input: configfilespathfrommodslocation
    backupconfigpaths = []
    for configfile in configfilespathfrommodslocation:
        backupconfigpaths.append(os.path.join(backupfolder, configfile))
    for i in range(len(configfilespathfrommodslocation)):
        minput = os.path.join(modslocation, configfilespathfrommodslocation[i])
        moutput = backupconfigpaths[i]
        print(minput + " -> " + moutput)
        if os.path.exists(os.path.dirname(moutput)) == False:
            os.makedirs(os.path.dirname(moutput))
        copyfile(minput, moutput)
    # output: nothing/error

def backup_option(modslocation, backupfolder):
    # print what you do
    print("Moving configs from " + modslocation + " to " + backupfolder)
    configfilespathfrommodslocation = find_mods_that_have_Lua_folder_or_CSharp_folder(modslocation)
    create_backup_folders_and_copy_files(configfilespathfrommodslocation, modslocation,backupfolder)
    # print done
    print("Done backing up config files")

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
        print("Moving configs from " + backupfolder + " to " + modslocation)
        dir_list = os.listdir(backupfolder)


        backupconfigs = find_mods_that_have_Lua_folder_or_CSharp_folder(backupfolder)
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


if __name__ == '__main__':
    main()