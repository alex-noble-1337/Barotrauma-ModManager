import os
import shutil
from lxml import etree as ET
import re
import ModManager
import xmldiff.main as xml_diff
from configbackup import config_files_find
import BaroRewrites

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

# 
def test_FIX_barodev_moment():
    namematters = False
    # check fixing of mods by comparing files with copy in Installed in config of deadelic
    os.makedirs("test_fix_barodev_moment", exist_ok=True)
    mod_dirs = {}
    if mod_dirs == {}:
        mod_dirs = os.listdir(steam_library_installedmods)
    mod_dirs_daedelic = os.listdir(daedalic_entertainment_ghmbh_installedmods)
    done = 0
    for mod_dir in mod_dirs:
        if mod_dir in mod_dirs_daedelic:
            full_path = os.path.join(steam_library_installedmods, mod_dir)
            full_path_output = os.path.join("test_fix_barodev_moment", mod_dir)
            if os.path.exists(full_path):
                # copy to "test_fix_barodev_moment"
                ModManager.robocopysubsttute(full_path, full_path_output)
                # run test_fix_barodev_moment
                modlist = [{'ID': os.path.basename(full_path)}]
                ModManager.get_modlist_data_webapi(modlist)
                mod = modlist[0]
                with open(os.path.join(daedalic_entertainment_ghmbh_installedmods, mod_dir, "filelist.xml"), 'r', encoding="utf8") as open_file:
                    dst_filelist_str = open_file.read()
                    dst_filelist_str = re.sub(" installtime=\".*?\"", "", dst_filelist_str)
                    dst_filelist_str = re.sub("corepackage=\"[Ff][Aa][Ll][Ss][Ee]\"", "corepackage=\"false\"", dst_filelist_str)
                    dst_filelist = ET.fromstring(dst_filelist_str, parser=ET.XMLParser(remove_comments=True))
                if not 'name' in mod:
                    mod['name'] = dst_filelist.attrib['name']
                if not namematters:
                    dst_filelist_str = re.sub("name=\".*?\"", "", dst_filelist_str)
                    dst_filelist = ET.fromstring(dst_filelist_str, parser=ET.XMLParser(remove_comments=True))
                dst_filelist = ET.ElementTree(dst_filelist)
                ModManager.FIX_barodev_moment(mod, full_path_output)
                # compare it, file by file to deadalic enterteiment
                # we only want to compare xml files of xml's that are loaded by the game so first get the list of files from filelist
                with open(os.path.join(full_path_output, "filelist.xml"), 'r', encoding="utf8") as open_file:
                    src_filelist_str = open_file.read()
                    src_filelist_str = re.sub(" installtime=\".*?\"", "", src_filelist_str)
                    src_filelist_str = re.sub("corepackage=\"[Ff][Aa][Ll][Ss][Ee]\"", "corepackage=\"false\"", src_filelist_str)
                    filelist = ET.fromstring(src_filelist_str, parser=ET.XMLParser(remove_comments=True))
                if not namematters:
                    src_filelist_str = re.sub("name=\".*?\"", "", src_filelist_str)
                    filelist = ET.fromstring(src_filelist_str, parser=ET.XMLParser(remove_comments=True))
                diff = xml_diff.diff_trees(ET.ElementTree(filelist), dst_filelist)
                if diff != []:
                    # TODO werid behaviour when no hash check it
                    if 'expectedhash' in filelist.attrib:
                        raise Exception(("diff --color \"{0}\" \"{1}\"\nFiles {0}, {1} not equal\n{2}/{3}\n{4}").format(os.path.join(full_path_output, "filelist.xml"), os.path.join(daedalic_entertainment_ghmbh_installedmods, mod_dir, "filelist.xml"), done, len(mod_dirs_daedelic), diff))
                else:
                    def_content = []
                    content_types = ["item","character","mapcreature","text",
                                     "uistyle","afflictions","structure",
                                     "upgrademodules","ruinconfig",
                                     "wreckaiconfig","backgroundcreatureprefabs",
                                     "levelobjectprefabs","particles","decals",
                                     "randomevents","eventmanagersettings",
                                     "locationtypes","mapgenerationparameters",
                                     "levelgenerationparameters",
                                     "cavegenerationparameters","outpostconfig",
                                     "npcsets","missions","traitormissions",
                                     "npcpersonalitytraits","npcconversations",
                                     "jobs","orders","corpses","sounds",
                                     "skillsettings","factions","itemassembly",
                                     "talents","talenttrees","startitems","tutorials"]
                    elements = filelist.getchildren()
                    for element in elements:
                        if element.tag.lower() in content_types:
                            if 'file' in element.attrib:
                                content = element.attrib['file'].replace("%ModDir%/", "")
                                content = BaroRewrites.CleanUpPath(content)
                                def_content.append(content)


                for src_dir1, dirs, files in os.walk(full_path_output):
                    for file_ in files:
                        xml_file = False
                        if os.path.basename(file_) != "filelist.xml":
                            src_dir = os.path.join(src_dir1, file_)
                            # TODO only define dcontent should matter, take a look
                            # apperently it does:
                            # https://github.com/Regalis11/Barotrauma/blob/c67f6688fdf4dcffa224711a0d4f4181d9a1fad4/Barotrauma/BarotraumaShared/SharedSource/ContentManagement/ContentPackage/ContentPackage.cs#L189
                            if src_dir.replace("test_fix_barodev_moment/" + mod_dir + "/", "") in def_content:
                                if not config_files_find(os.path.basename(file_)):
                                    WINDOWS_LINE_ENDING = b'\r\n'
                                    UNIX_LINE_ENDING = b'\n'
                                    with open(src_dir, 'rb') as open_file:
                                        src_file = open_file.read()
                                        # TODO line endings shoudnt matter, take a look at code
                                        src_file = src_file.replace(WINDOWS_LINE_ENDING, b'')
                                        src_file = src_file.replace(UNIX_LINE_ENDING, b'')
                                    dst_dir = src_dir.replace("test_fix_barodev_moment", daedalic_entertainment_ghmbh_installedmods, 1)
                                    with open(dst_dir, 'rb') as open_file:
                                        dst_file = open_file.read()
                                        # TODO line endings shoudnt matter, take a look at code
                                        dst_file = dst_file.replace(WINDOWS_LINE_ENDING, b'')
                                        dst_file = dst_file.replace(UNIX_LINE_ENDING, b'')
                                    if src_file != dst_file:
                                        raise Exception(("Files {0}, {1} not equal\nUse: diff --color \"{0}\" \"{1}\" to figure out whats wrong").format(src_dir, dst_dir))
            done += 1
            print("{0}/{1}".format(done, len(mod_dirs_daedelic)))
    # if nothing excepted, test has been completed sucessully

# def test_get_user_perfs():
#     # get input file/commands
#     # compare to expected output
#     # kinda lame, but i dont see how elese i can do it
#     print()

# not used now
# def test_set_mods_config_player():
#     # set regularpackages inside config_player, set names, and formatting
#     # check if its valid xml
#     print()

def test_get_localcopy_path():
    correct_localcopy = "LocalMods"
    with open("test_localcopy.xml", "r", encoding='utf8') as f:
        regularpackages = f.read()
    # get localcopy from regularpackages
    localcopy = ModManager.get_localcopy_path(regularpackages)
    # check it its valid xml
    if correct_localcopy != localcopy:
        raise Exception("Paths localcopy {correct_localcopy}(should be), {localcopy}(is now) not equal!")

def test_get_modlist_regularpackages():
    correct_modlist = [{'path': 'LocalMods/2559634234/filelist.xml', 'ID': '2559634234'}, {'path': 'LocalMods/2532991202/filelist.xml', 'ID': '2532991202'}, {'path': 'LocalMods/2526236489/filelist.xml', 'ID': '2526236489'}, {'path': 'LocalMods/2907491279/filelist.xml', 'ID': '2907491279'}, {'path': 'LocalMods/2764968387/filelist.xml', 'ID': '2764968387'}, {'path': 'LocalMods/2911392334/filelist.xml', 'ID': '2911392334'}, {'path': 'LocalMods/2776270649/filelist.xml', 'ID': '2776270649'}, {'path': 'LocalMods/2807556435/filelist.xml', 'ID': '2807556435'}, {'path': 'LocalMods/2564921308/filelist.xml', 'ID': '2564921308'}, {'path': 'LocalMods/2547888957/filelist.xml', 'ID': '2547888957'}, {'path': 'LocalMods/2161488150/filelist.xml', 'ID': '2161488150'}, {'path': 'LocalMods/2538084355/filelist.xml', 'ID': '2538084355'}, {'path': 'LocalMods/2831987252/filelist.xml', 'ID': '2831987252'}, {'path': 'LocalMods/2834851130/filelist.xml', 'ID': '2834851130'}, {'path': 'LocalMods/2909716869/filelist.xml', 'ID': '2909716869'}, {'path': 'LocalMods/2961385886/filelist.xml', 'ID': '2961385886'}, {'path': 'LocalMods/2085783214/filelist.xml', 'ID': '2085783214'}, {'path': 'LocalMods/2389600483/filelist.xml', 'ID': '2389600483'}, {'path': 'LocalMods/2788543375/filelist.xml', 'ID': '2788543375'}, {'path': 'LocalMods/2764140582/filelist.xml', 'ID': '2764140582'}, {'path': 'LocalMods/2852315967/filelist.xml', 'ID': '2852315967'}, {'path': 'LocalMods/2955139345/filelist.xml', 'ID': '2955139345'}, {'path': 'LocalMods/2544952900/filelist.xml', 'ID': '2544952900'}, {'path': 'LocalMods/2804655816/filelist.xml', 'ID': '2804655816'}, {'path': 'LocalMods/2912049119/filelist.xml', 'ID': '2912049119'}, {'path': 'LocalMods/2655920928/filelist.xml', 'ID': '2655920928'}, {'path': 'LocalMods/2948537269/filelist.xml', 'ID': '2948537269'}, {'path': 'LocalMods/2260683656/filelist.xml', 'ID': '2260683656'}, {'path': 'LocalMods/2972196919/filelist.xml', 'ID': '2972196919'}, {'path': 'LocalMods/2390137099/filelist.xml', 'ID': '2390137099'}, {'path': 'LocalMods/2838076686/filelist.xml', 'ID': '2838076686'}, {'path': 'LocalMods/2940102835/filelist.xml', 'ID': '2940102835'}]
    with open("test_localcopy.xml", "r", encoding='utf8') as f:
        regularpackages = f.read()
    # get modlist from regularpackages
    modlist = ModManager.get_modlist_regularpackages(regularpackages, "LocalMods")
    # compare it to the expected output
    if correct_modlist != modlist:
        raise Exception("Modlists {0}(should be), {1}(is now) not equal!".format(correct_modlist, modlist))

def test_remove_duplicates():
    modlist = []
    # get a list, remove duplicates
    modlist_new = ModManager.remove_duplicates(modlist)
    # TODO print time how long it took
    # check if it removed duplcates
    for mod in modlist:
        number = 0
        for mod_new in modlist_new:
            if mod == mod_new:
                number += 1
        if number <= 0:
            raise Exception("Mod {mod} not found, must have been removed by function.")
        if number >= 2:
            raise Exception("Mod {mod} hadnt had all its duplicates removed.")

def test_create_new_regularpackages():
    modlist = []
    localcopy_path = ""
    barotrauma_path = ""
    regularpackages = ModManager.set_modlist_regularpackages(modlist, localcopy_path, barotrauma_path)
    # check if its a valid xml
    try:
        tree = ET.fromstring(regularpackages)
    except ET.ParseError:
        raise Exception("XML is not good \n{regularpackages}")

def test_download_modlist():
    # parse test modlist
    modlist = []
    # check if mods align with the ones in my steam install download
    ModManager.download_modlist(modlist, "LocalMods", "steamcmd")
    names = os.listdir("LocalMods")
    for mod in modlist:
        found = False
        for name in names:
            if mod['ID'] == name:
                found = True
        if found == False:
            raise Exception("Mod {mod} not downloaded correctly!")

def test_check_collection_link():
    # parse few collcetion links
    collection_link_list = [{'link': "2901361", 'expected': False}, {'link': "https://steamcommunity.com/sharedfiles/filedetails/?id=2952301361", 'expected': True}]
    # check wich ones are good, and wich ones are not
    for collection_link in collection_link_list:
        collection_site = ModManager.get_collectionsite(collection_link['link'])
        expected = ModManager.check_collection_link(collection_site, True)
        if expected != collection_link['expected']:
            raise Exception("Check not successufl! {collection_link}")

def test_is_pure_lua_mod():
    # test that function with mods inside steam install workshop mods
    modlist = [{'ID': "2658872348", 'expected': True},{'ID': "2544952900", 'expected': False}] # ...
    for mod in modlist:
        if mod['expected'] != ModManager.is_pure_lua_mod(os.path.join(daedalic_entertainment_ghmbh_installedmods, mod['ID'])):
            raise Exception("Check not successfull! {0}".format(mod['ID']))

# full run
def test_main():
    localcopy_dir = ""
    # run collection mod
    user_perfs = {}
    ModManager.main(user_perfs)
    # test if those are good
    mod_dirs = os.listdir(steam_library_installedmods)
    mod_dirs_daedelic = os.listdir(daedalic_entertainment_ghmbh_installedmods)
    for mod_dir in mod_dirs:
        for mod_dir_daedelic in mod_dirs_daedelic:
            if mod_dir == mod_dir_daedelic:
                full_path = os.path.join(steam_library_installedmods, mod_dir)
                full_path_output = os.path.join(localcopy_dir, mod_dir)
                if os.path.exists(full_path):
                    # copy to "test_fix_barodev_moment"
                    # run test_fix_barodev_moment
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
    # run config_player mode
    user_perfs = {}
    ModManager.main(user_perfs)
    # test if those are good
    mod_dirs = os.listdir(steam_library_installedmods)
    mod_dirs_daedelic = os.listdir(daedalic_entertainment_ghmbh_installedmods)
    for mod_dir in mod_dirs:
        for mod_dir_daedelic in mod_dirs_daedelic:
            if mod_dir == mod_dir_daedelic:
                full_path = os.path.join(steam_library_installedmods, mod_dir)
                full_path_output = os.path.join(localcopy_dir, mod_dir)
                if os.path.exists(full_path):
                    # copy to "test_fix_barodev_moment"
                    # run test_fix_barodev_moment
                    mod = {}
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


def get_all_content_types():
    with open("Vanilla.xml", 'r', encoding="utf8") as open_file:
        src_filelist_str = open_file.read()
        src_filelist_str = re.sub(" installtime=\".*?\"", "", src_filelist_str)
        src_filelist_str = re.sub("corepackage=\"[Ff][Aa][Ll][Ss][Ee]\"", "corepackage=\"false\"", src_filelist_str)
        filelist = ET.fromstring(src_filelist_str)
    elements = filelist.getchildren()
    xml_tags = []
    for element in elements:
        if not element.tag.lower() in xml_tags:
            if 'file'in element.attrib:
                if os.path.basename(element.attrib['file'])[-4:] == ".xml":
                    xml_tags.append(element.tag.lower())
    for xml_tag in xml_tags:
        print("\"{0}\",".format(xml_tag.lower()), end='')

if __name__ == '__main__':
    test_get_localcopy_path()
    test_get_modlist_regularpackages()
    test_remove_duplicates()
    test_create_new_regularpackages()
    test_download_modlist()
    test_check_collection_link()
    test_is_pure_lua_mod()
    # somewhat works
    test_FIX_barodev_moment()
    # what? you expect me to run by hand? im lazy
    # test_main()
        # with open("config_player.xml", 'r', encoding="utf8") as f:
    #     file_str = f.read()
    #     config_player_xml = ET.fromstring(file_str)
    # print(config_player_xml)
        # user_perfs = get_user_perfs()
    # save_managedmods(user_perfs['old_managedmods'], user_perfs)