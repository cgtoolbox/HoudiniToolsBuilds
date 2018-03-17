import os
import sys
import shutil
import qdarkstyle

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore
Qt = QtCore.Qt

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

class Builder(QtWidgets.QDialog):

    def __init__(self, list_of_proj, parent=None):
        super(Builder, self).__init__(parent=parent)

        self.proj_selected = -1

        main_layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle("Builder")
        self.setWindowIcon(QtGui.QIcon("package.png"))

        main_layout.addWidget(QtWidgets.QLabel(("Select a houdini python "
                                                "tool project to build:")))

        for i, prj in enumerate(list_of_proj):

            btn = QtWidgets.QPushButton(prj)
            btn.clicked.connect(lambda state, x=i: self.select_proj(x))
            main_layout.addWidget(btn)

        self.setLayout(main_layout)

    def select_proj(self, idx):

        self.proj_selected = idx
        self.close()

def main():

    root = os.path.dirname(os.getcwd())
    print("ROOT: " + root)
    
    projects = [d for d in os.listdir(root) if not d.startswith('.') \
                and os.path.isdir(root + os.sep + d) \
                and d != "HoudiniToolsBuilds"]
    
    app = QtWidgets.QApplication(sys.argv)
    w = Builder(projects)
    w.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    w.exec_()

    p = w.proj_selected
    if p == -1:
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

    build_name = build_name[0].split(':')[-1].replace('\n', '')
    print("Build name: " + build_name)

    doc_link = ""
    doc_link_raw = [d for d in build_data if d.startswith("$DOC_LINK")]
    if doc_link_raw:
        doc_link = doc_link_raw[0].split(':')[-1]

    version = ""
    version_raw = [d for d in build_data if d.startswith("$VERSION")]
    if version_raw:
        version_file = root + '/' + build_name + '/' + version_raw[0].split(':')[-1]
        version_file = version_file.replace('\n', '')
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                for li in f.readlines():
                    if li.startswith("__version__"):
                        version = li.split('=')[-1].strip().replace('.', '_')
                        version = '_v' + version.replace('"', '')
                        print("Code version: " + version)
                        break
    if version == "":
        print("Node code version found")
    
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

    archive = os.path.join(root, "HoudiniToolsBuilds", "builds", build_name + version)

    print("Creating archive: " + archive)
    shutil.make_archive(archive, "zip", target)

    print("Cleaning build folder: " + target)
    shutil.rmtree(target)

    print("Build created successfully: " + archive)

if __name__ == "__main__":
    main()