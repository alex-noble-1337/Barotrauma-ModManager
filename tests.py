import os
import shutil

import ModManager

steam_library_installedmods = "/mnt/Share/SteamLibrary/steamapps/workshop/content/602960"
daedalic_entertainment_ghmbh_installedmods = "/mnt/Share/milord/.local/share/Daedalic Entertainment GmbH/Barotrauma/WorkshopMods/Installed"

# first test output of all functions used in the program
# then test full functionality, run full program and test if output in localcopy folder is the same in both folders

# def test_get_recusive_modification_time_of_dir():
#     # idk how to test it
#     # mabe in conjuntion with other functions
#     print()
# def test_robocopysubsttute():
#     # idk how to test it
#     # mabe in conjunction with other functions
#     print()
# def test_moddownloader():
#     # idk how to test it
#     # mabe in conjuction with other functions
#     print()
# def test_get_not_managedmods():
#     # idk how to tes it, probbabbly with other functions
#     print()
# def test_get_up_to_date_mods():
#     # idk how to test it, probbabbly with other functions
#     print()
# def test_remove_up_to_date_mods():
#     # idk how to test it, probbabbly with other functions
#     print()
# def test_deleting_not_managedmods():
#     # simple function, idk if it needs testing
#     # mabe with other functions
#     print()



# def test_sanitize_pathstr():
#     # idk how to test it because i dont reember how it is used
#     print()
# def test_print_modlist():
#     # idk how to test it, probbabbly no point
#     print()
# def test_save_managedmods():
#     # idk how to test it, probbabbly no point
#     print()
# def test_get_old_managedmods():
#     # idk how to test it, probbabbly no point
#     print()
# def test_get_managedmods():
#     # idk how to test it, probbabbly no point
#     print()




def test_FIX_barodev_moment():
    # check fixing of mods by comparing files with copy in Installed in config of deadelic
    os.makedirs("test_fix_barodev_moment", exist_ok=True)
    mod_dirs = os.listdir(steam_library_installedmods)
    mod_dirs_daedelic = os.listdir(daedalic_entertainment_ghmbh_installedmods)
    for mod_dir in mod_dirs:
        for mod_dir_daedelic in mod_dirs_daedelic:
            if mod_dir == mod_dir_daedelic:
                full_path = os.path.join(steam_library_installedmods, mod_dir)
                full_path_output = os.path.join("test_fix_barodev_moment", mod_dir)
                if os.path.exists(full_path):
                    # copy to "test_fix_barodev_moment"
                    robocopysubsttute(full_path, full_path_output)
                    # run test_fix_barodev_moment
                    mod = {}
                    FIX_barodev_moment(mod, full_path_output)
                    # compare it, file by file to deadalic enterteiment
                    for src_dir, dirs, files in os.walk(root_src_dir):
                        for file_ in files:
                            src_dir = os.path.join(full_path_output, file_)
                            with open(src_dir, 'rb') as open_file:
                                src_file = open_file
                            dst_dir = os.path.join(daedalic_entertainment_ghmbh_installedmods, file_)
                            with open(dst_dir, 'rb') as open_file:
                                dst_file = open_file
                            if src_file != dst_file:
                                # TODO mabe generate diff output of 2 files?
                                raise Exception(("Files {src_dir}, {dst_dir} not equal"))
    # if nothing excepted, test has been completed sucessully

def test_get_user_perfs():
    # get input file/commands
    # compare to expected output
    # kinda lame, but i dont see how elese i can do it
    print()

def test_set_mods_config_player():
    # set regularpackages inside config_player, set names, and formatting
    # compare it to the expected output
    print()

def test_get_localcopy_path():
    # get localcopy from regularpackages
    # compare it to the expected output
    print()

def test_get_modlist_regularpackages():
    # get modlist from regularpackages
    # compare it to the expected output
    print()

def test_remove_duplicates():
    # get a list, remove duplicates
    # print time how long it took
    # check if it removed duplcates
    print()

def test_create_new_regularpackages():
    # check if its a valid xml
    print()

def test_download_modlist():
    # parse test modlist
    # check if mods align with the ones in my steam install download
    print()

def test_check_collection_link():
    # parse few collcetion links
    # check wich ones are good, and wich ones are not
    print()

def test_is_pure_lua_mod():
    # test that function with mods inside steam install workshop mods
    print()

# full run
def test_main():
    # run collection mode
    # run config_player mode
    # test if mods are in the steam collection
    print()