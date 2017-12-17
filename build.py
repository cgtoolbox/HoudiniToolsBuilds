import os
import shutil

INSTALL_HEADER = """
Extract %BUILD% to $HOME/houdini16.0/ folder ( or your current version of Houdini ).
Use "Extract here" function.

File to install:
----------------
%BUILD_FILES%
----------------

Extra infos on install:
%DOC_LINK%

www.cgtoolbox.com
contact@cgtoolbox.com
"""

IGNORE_PATTERN = ["*.pyc"]


def main():

    root = os.path.dirname(os.getcwd())
    print("ROOT: " + root)
    
    projects = [d for d in os.listdir(root) if not d.startswith('.') \
                and os.path.isdir(root + os.sep + d)]

    print("Build:")
    print("-------")
    for i, proj in enumerate(projects):
        print("[{}] {}".format(i, proj))
    print("-------")

    p = input("Enter ID:")
    
    try:
        p = int(p)
    except:
        print("Invalid ID")
        return
    
    if p < 0 or p > len(projects):
        print("Invalid ID")
        return

    project = projects[p]
    build_infos = os.path.join(root, project, "build_infos.txt")
    src = os.path.join(root, project)
    print("Build infos: " + build_infos)

    if not os.path.exists(build_infos):
        print("Build info not found.")
        return

    with open(build_infos, 'r') as f:
        build_data = f.readlines()

    build_name = [d for d in build_data if d.startswith("$NAME")]
    if not build_name:
        print("No build name $NAME found.")
        return

    doc_link = ""
    doc_link_raw = [d for d in build_data if d.startswith("$DOC_LINK")]
    if doc_link_raw:
        doc_link = doc_link_raw[0].split(':')[-1]

    build_name = build_name[0].split(':')[-1].replace('\n', '')
    print("Build name: " + build_name)
    
    target = os.path.join(root, "HoudiniToolsBuilds", build_name)
    if not os.path.exists(target):
        os.makedirs(target)

    print("Build folder: " + target)
    installed_files = ""

    # copy files and folders to the build folder where the archive 
    # will be created from.
    for data in build_data:

        if data.startswith('#') or data.startswith('$'):
            continue

        data = data.replace('\n', '')

        installed_files += "$HOME/houdiniXX.X/" + data.replace(':', " => ") + "\n"

        tgt_root, src_data = data.split(':')
        tgt_root = tgt_root.split('/')
        src_data = src_data.split('/')

        tgt_folder = os.path.join(target, *tgt_root)
        src_file = os.path.join(src, *src_data) 

        if os.path.isfile(src_file):
            
            if "*." + src_file.split('.')[-1] in IGNORE_PATTERN:
                continue

            print("Copying file: " + src_file)

            if not os.path.exists(tgt_folder):
                os.makedirs(tgt_folder)

            tgt_file = os.path.join(tgt_folder, src_data[-1])
            shutil.copyfile(src_file, tgt_file)

        elif os.path.isdir(src_file):

            print("Copying folder: " + src_file)
            shutil.copytree(src_file, tgt_folder,
                            ignore=shutil.ignore_patterns(*IGNORE_PATTERN))

        else:
            print("File: {} not valid.".format(src_file))
            return False

        install_data = INSTALL_HEADER.replace("%BUILD%", build_name + ".zip")
        install_data = install_data.replace("%BUILD_FILES%", installed_files)
        install_data = install_data.replace("%DOC_LINK%", doc_link)

    # create common files and archive
    install_info = target + os.sep + build_name + "_INSTALL.txt"
    print("Writing intall infos: " + install_info)
    with open(install_info, 'w') as f:
        f.write(install_data)

    archive = os.path.join(root, "HoudiniToolsBuilds", "builds", build_name)

    print("Creating archive: " + archive)
    shutil.make_archive(archive, "zip", target)

    print("Cleaning build folder: " + target)
    shutil.rmtree(target)

    print("Build created successfully.")

if __name__ == "__main__":
    main()