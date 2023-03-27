import os # TODO change this to import only individual commands
import shutil # TODO change this to import only individual commands
import re # TODO change this to import only individual commands
import sys # TODO change this to import only individual commands

# yoinked from stackoverflow, works
def robocopysubsttute(root_src_dir, root_dst_dir):
    # if replace_option:
    #     number_dirs = os.listdir(root_dst_dir)
    #     for number_dir in number_dirs:
    #         pattern = "^\d*?$"
    #         if re.match(pattern, number_dir):
    #             if os.path.exists(os.path.join(root_dst_dir, number_dir)):
    #                 shutil.rmtree(os.path.join(root_dst_dir, number_dir))
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
            shutil.copy2(src_file, dst_dir)


def copy_optimized(src_file, dst_file):
    if os.path.exists(dst_file):
        if not os.path.samefile(src_file, dst_file):
            os.remove(dst_file)
            shutil.copy2(src_file, dst_file)
    else:
        shutil.copy2(src_file, dst_file)

def get_fileswithextension(directory, extension):
    new_list = []
    files = os.listdir(directory)
    for filex in files:
        number = -1*len(extension)
        extensiontest = filex[number:]
        if extensiontest == extension:
            new_list.append(filex)
    return new_list

def zip_with_dir(input_path, name_of_zip):
    # create input directory
    zip_input_path = os.path.join(input_path, "..", "input")
    if os.path.exists(zip_input_path):
        shutil.rmtree(zip_input_path)
    os.mkdir(zip_input_path)
    # create name_of_zip within input directory
    input_name_of_zip_path = os.path.join(zip_input_path, name_of_zip)
    os.mkdir(input_name_of_zip_path)
    # copy all from input_path to name_of_zip
    robocopysubsttute(input_path, input_name_of_zip_path)
    # zip input
    name_of_zip_output = os.path.join(input_path, "..", name_of_zip)
    if os.path.exists(name_of_zip_output + ".zip"):
        os.remove(name_of_zip_output + ".zip")
    shutil.make_archive(name_of_zip_output, 'zip', zip_input_path)
    shutil.rmtree(zip_input_path)

if __name__ == '__main__':
    # get first argument as output path
    options_arr = sys.argv[1:]
    if len(options_arr) > 0:
        output_path = options_arr[0]
    else:
        output_path = "../release"
    # create ModManager dir in output path
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    output_path = os.path.join(output_path, "ModManager")
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    # copy BestDefaultConfigsTM to ModManager
    robocopysubsttute("BestDefaultConfigsTM", os.path.join(output_path, "BestDefaultConfigsTM"))
    # copy LICENSE to ModManager
    copy_optimized("LICENSE", os.path.join(output_path, "LICENSE"))
    # copy README.md to ModManager
    copy_optimized("README.md", os.path.join(output_path, "README.md"))
    # copy all py files except releasebuild.py into ModManager dir
    files_arr = get_fileswithextension(os.getcwd(), ".py")
    files_arr.remove("releasebuild.py")
    for file1 in files_arr:
        copy_optimized(file1, os.path.join(output_path, file1))
    # set all default_ values to default ("")
    with open(os.path.join(output_path, "ModManager.py"), "r", encoding='utf8') as f:
        ModManager_str = f.read()
    pattern = "default_.*?\".*?\""
    arrx = re.findall(pattern, ModManager_str)[0:4]
    arry = []
    pattern = "\".*?\""
    for old in arrx:
        new = re.sub(pattern, "\"\"", old)
        ModManager_str = ModManager_str.replace(old, new, 1)
    with open(os.path.join(output_path, "ModManager.py"), "w", encoding='utf8') as f:
        f.write(ModManager_str)
    # zip the folder
    zip_with_dir(output_path,"ModManager")
    # copy the download_scrpt_example.sh to output path
    copy_optimized("download_script_exmple.sh", os.path.join(output_path, "..", "download_script_exmple.sh"))