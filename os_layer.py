import os
import platform
import sys
import subprocess
import shutil
import re

# main variables, directories and settings
config_path = "./data/config.json"
savedir = "./data/save-files/"
app_title = "Elden Ring Save Manager"
backupdir = "./data/backup/"
update_dir = "./data/updates/"
post_update_file = "./data/post.update"
version = "v1.63"
v_num = 1.63  # Used for checking version for update
video_url = "https://youtu.be/RZIP0kYjvZM"
background_img = "./data/background.png"
icon_file = "./data/icon.ico"
bk_p = (-140, 20)  # Background image position
is_windows = any(platform.win32_ver()) or hasattr(sys, "getwindowsversion")




def open_folder_standard_exporer(path):
    """Note: os.startfile is only avaiable on Win platform"""
    if platform.system() == "Windows":
        os.startfile(path.replace("/", "\\"))
    else:
        subprocess.Popen(["xdg-open", path])


def open_textfile_in_editor(path):
    if is_windows:
        subprocess.run(f"notepad {path}", shell=True, capture_output=True, text=True)
    else:
        subprocess.Popen(["xdg-open", path])


def force_close_process(process):
    if is_windows:
        comm = f"taskkill /IM {process} -F"
        subprocess.run(comm, shell=True, capture_output=True, text=True)
    else:
        comm = f"pkill {process}"
        os.system(comm)


def copy_folder(src, dest):
    """
    if is_windows:
        cmd = f"Xcopy {src} {dest} /E /H /C /I /Y".format(gamedir,savedir,lst_box_choice)
        subprocess.run(comm, shell=True , capture_output=True, text=True)
    else:
        shutil.copytree(src, dest, dirs_exist_ok=True)
    """
    shutil.copytree(src, dest, dirs_exist_ok=True)


def copy_file(src, dst):
    shutil.copy(src, dst)


def delete_folder(folder):
    if folder is None or not isinstance(folder, str) or len(folder) < 5:
        raise Exception("UNSAFE FOLDER DELETE OPERATION. QUIT")
    shutil.rmtree(folder)
