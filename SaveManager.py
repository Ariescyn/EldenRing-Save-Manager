import sys
import traceback
from tkinter import *
from tkinter import font as FNT
from tkinter import filedialog as fd
from tkinter import ttk
import tkinter as TKIN
from collections import Counter
from PIL import Image, ImageTk
import subprocess, os, zipfile, requests, re, time, hexedit, webbrowser, itemdata, lzma, datetime, json
from os_layer import *
from pathlib import Path as PATH

# TODO + Notes
#   Replace all nested pop_up functions with new popup impplementation
# Left off with displaying file paths when opening save files in




# set always the working dir to the correct folder for unix env
if not is_windows:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))




class Config:

    def __init__(self):
        if not os.path.exists(post_update_file):
            with open(post_update_file, 'w') as ff:
                ff.write("True")

        with open(post_update_file, 'r') as f:
            x = f.read()
            self.post_update = (True if x == 'True' else False)




        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                dat = json.load(f)

                if not "custom_ids" in dat.keys():  # custom_ids was an addition to v1.5, must create for current users with existing config.json from v1.5
                    dat["custom_ids"] = {}
                    self.cfg = dat

                    with open(config_path, 'w') as f:
                        json.dump(self.cfg, f)

        if not os.path.exists(config_path):  # Build dictionary for first time
            dat = {}
            dat["post_update"] = True
            dat["gamedir"] = ""
            dat["steamid"] = ""
            dat["seamless-coop"] = False
            dat["custom_ids"] = {}

            self.cfg = dat
            with open(config_path, 'w') as f:
                json.dump(self.cfg, f)
        else:
            with open(config_path, 'r') as f:
                js = json.load(f)
                self.cfg = js
    def set_update(self, val):
        self.post_update = val
        with open(post_update_file, 'w') as f:
            f.write("True" if val else "False")

    def set(self,k,v):
        self.cfg[k] = v
        with open(config_path, 'w') as f:
            json.dump(self.cfg, f)

    def add_to(self,k,v):
        self.cfg[k].update(v)
        with open(config_path, 'w') as f:
            json.dump(self.cfg, f)

    def delete_custom_id(self, k):
        self.cfg['custom_ids'].pop(k)
        with open(config_path, 'w') as f:
            json.dump(self.cfg, f)

def archive_file(file, name, metadata, names):

    name = name.replace(" ", "_")

    if not os.path.exists(file):  # If you try to load a save from listbox, and it tries to archive the file already present in the gamedir, but it doesn't exist, then skip
        return


    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d__(%I.%M.%S)")
    name = f"{name}__{date}"
    os.makedirs(f"./data/archive/{name}")


    with open(file, "rb") as fhi, lzma.open(f"./data/archive/{name}/ER0000.xz", 'w') as fho:
        fho.write(fhi.read())
        names = [i for i in names if not i is None]
        formatted_names = ", ".join(names)
        meta = f"{metadata}\nCHARACTERS: {formatted_names}"

    meta_ls = [i for i in meta]
    try:
        x = meta.encode("ascii") # Will fail with UnicodeEncodeError if special characters exist
        with open(f"./data/archive/{name}/info.txt", 'w') as f:
            f.write(meta)
    except:
        for ind,i in enumerate(meta):
            try:
                x = i.encode("ascii")
                meta_ls[ind] = i
            except:
                meta_ls[ind] = '?'
        fixed_meta = ""
        for i in meta_ls:
            fixed_meta = fixed_meta + i

        with open(f"./data/archive/{name}/info.txt", 'w') as f:
            f.write(fixed_meta)


def unarchive_file(file):
    lzc = lzma.LZMACompressor()
    name = file.split("/")[-2]
    path = f"./data/recovered/{name}/"


    if not os.path.exists("./data/recovered/"):
        os.makedirs("./data/recovered/")
    if not os.path.exists(path):
        os.makedirs(path)

    with lzma.open(file, "rb") as f_in, open(f"{path}/{ext()}", "wb") as f_out:
        f_out.write(f_in.read())


def grab_metadata(file):
    """Used to grab metadata from archive info.txt"""
    with open(file.replace(" ", "__").replace(":", "."), 'r') as f:
        meta = f.read()
        popup(meta)


def change_default_steamid():


    def done():
        s_id = ent.get()
        if not len(s_id) == 17:
            popup("SteamID should be 17 digits long")
            return
        config.set("steamid", s_id)


        popup("Successfully changed default SteamID")
        popupwin.destroy()

    def cancel():
        popupwin.destroy()

    def validate(P):
        if len(P) == 0:
            return True
        elif len(P) < 18 and P.isdigit():
            return True
        else:
            # Anything else, reject it
            return False

    popupwin = Toplevel(root)
    popupwin.title("Set SteamID")
    vcmd = (popupwin.register(validate), "%P")
    # popupwin.geometry("200x70")

    s_id = config.cfg["steamid"]
    lab = Label(popupwin, text=f"Current ID: {s_id}\nEnter new ID:")
    lab.grid(row=0, column=0)
    ent = Entry(popupwin, borderwidth=5, validate="key", validatecommand=vcmd)
    ent.grid(row=1, column=0, padx=25, pady=10)
    x = root.winfo_x()
    y = root.winfo_y()
    popupwin.geometry("+%d+%d" % (x + 200, y + 200))
    but_done = Button(popupwin, text="Done", borderwidth=5, width=6, command=done)
    but_done.grid(row=2, column=0, padx=(25, 65), pady=(0, 15), sticky="w")
    but_cancel = Button(popupwin, text="Cancel", borderwidth=5, width=6, command=cancel)
    but_cancel.grid(row=2, column=0, padx=(70, 0), pady=(0, 15))


def import_save():
    """Opens file explorer to choose a save file to import, Then checks if the files steam ID matches users, and replaces it with users id"""

    if os.path.isdir(savedir) is False:
        os.makedirs(savedir)
    d = fd.askopenfilename()

    if len(d) < 1:
        return

    if not d.endswith(ext()):
        popup("Select a valid save file!\nIt should be named: ER0000.sl2/ER0000.co2")
        return




    def cancel():
        popupwin.destroy()

    def done():

        name = ent.get().strip()
        if len(name) < 1:
            popup("No name entered.")
            return
        isforbidden = False
        for char in name:
            if char in "~'{};:./\,:*?<>|-!@#$%^&()+":
                isforbidden = True
        if isforbidden is True:
            popup("Forbidden character used")
            return
        elif isforbidden is False:
            entries = []
            for entry in os.listdir(savedir):
                entries.append(entry)
            if name.replace(" ", "-") in entries:
                popup("Name already exists")
                return







        names = get_charnames(d)
        archive_file(d, name, "ACTION: Imported", names)

        newdir = "{}{}/".format(savedir, name.replace(" ", "-"))
        cp_to_saves_cmd = lambda: copy_file(d, newdir)

        if os.path.isdir(newdir) is False:
            cmd_out = run_command(lambda: os.makedirs(newdir))

            if cmd_out[0] == "error":
                print("---ERROR #1----")
                return

            lb.insert(END, "  " + name)
            cmd_out = run_command(cp_to_saves_cmd)
            if cmd_out[0] == "error":
                return
            create_notes(name, "{}{}/".format(savedir, name.replace(" ", "-")))

            file_id = hexedit.get_id(f"{newdir}/{ext()}")
            user_id = config.cfg["steamid"]
            if len(user_id) < 17:
                popupwin.destroy()
                return
            if file_id != int(user_id):
                popup(
                    f"File SteamID: {file_id}\nYour SteamID: {user_id}", buttons=True, button_names=("Patch with your ID", "Leave it"), b_width=(15,8), functions=(lambda:hexedit.replace_id(f"{newdir}/{ext()}", int(user_id)), donothing)
                )
                #hexedit.replace_id(f"{newdir}/ER0000.sl2", int(id))

            popupwin.destroy()

    popupwin = Toplevel(root)
    popupwin.title("Import")
    # popupwin.geometry("200x70")
    lab = Label(popupwin, text="Enter a Name:")
    lab.grid(row=0, column=0)
    ent = Entry(popupwin, borderwidth=5)
    ent.grid(row=1, column=0, padx=25, pady=10)
    x = root.winfo_x()
    y = root.winfo_y()
    popupwin.geometry("+%d+%d" % (x + 200, y + 200))
    but_done = Button(popupwin, text="Done", borderwidth=5, width=6, command=done)
    but_done.grid(row=2, column=0, padx=(25, 65), pady=(0, 15), sticky="w")
    but_cancel = Button(popupwin, text="Cancel", borderwidth=5, width=6, command=cancel)
    but_cancel.grid(row=2, column=0, padx=(70, 0), pady=(0, 15))


def open_folder():
    """Right-click open file location in listbox"""
    if len(lb.curselection()) < 1:
        popup("No listbox item selected.")
        return
    name = fetch_listbox_entry(lb)[0]
    cmd = lambda: open_folder_standard_exporer(f'{savedir}{name.replace(" ", "-")}')
    run_command(cmd)


def forcequit():
    comm = lambda: force_close_process("eldenring.exe")
    popup(text="Are you sure?", buttons=True, command=comm)


def update_app(on_start=False):
    """Gets redirect URL of latest release, then pulls the version number from URL and makes a comparison"""

    try:
        version_url = (
            "https://github.com/Ariescyn/EldenRing-Save-Manager/releases/latest"
        )
        r = requests.get(version_url)  # Get redirect url
        ver = float(r.url.split("/")[-1].split("v")[1])
    except:
        popup("Can not check for updates. Check your internet connection.")
        return
    if ver > v_num:
        popup(
            text=f" Release v{str(ver)} Available\nClose the program and run the Updater.",
            buttons=True,
            functions=(root.quit, donothing),
            button_names=("Exit Now", "Cancel"),
        )

    if on_start is True:
        return
    else:
        popup("Current version up to date")
        return


def reset_default_dir():
    """DEPRECIATED! writes the original gamedir to text file"""
    global gamedir
    with open(gamesavedir_txt, "w") as fh:
        fh.write(eldenring_savedata_dir)
    with open(gamesavedir_txt, "r") as fh:
        gamedir = fh.readline()
    popup("Successfully reset default directory")



def help_me():
    # out = run_command("notepad ./data/readme.txt")
    info = ""
    with open("./data/readme.txt", "r") as f:
        dat = f.readlines()
        for line in dat:
            info = info + line
    popup(info)


def load_listbox(lstbox):
    """LOAD current save files and insert them into listbox. This is Used
    to load the listbox on startup and also after deleting an item from the listbox to refresh the entries."""
    if os.path.isdir(savedir) is True:
        for entry in os.listdir(savedir):
            lstbox.insert(END, "  " + entry.replace("-", " "))


def create_save():
    """Takes user input from the create save entry box and copies files from game save dir to the save-files dir of app"""
    if len(config.cfg['gamedir']) < 2:
        popup("Set your Default Game Directory first")
        return
    name = cr_save_ent.get().strip()
    newdir = "{}{}".format(savedir, name.replace(" ", "-"))

    # Check the given name in the entry
    if len(name) < 1:
        popup("No name entered")

    isforbidden = False
    for char in name:
        if char in "~'{};:./\,:*?<>|-!@#$%^&()+":
            isforbidden = True
    if isforbidden is True:
        popup("Forbidden character used")

    if os.path.isdir(savedir) is False:
        # subprocess.run("md .\\save-files", shell=True)
        cmd_out = run_command(lambda: os.makedirs(savedir))
        if cmd_out[0] == "error":
            return

    # If new save name doesnt exist, insert it into the listbox,
    # otherwise duplicates will appear in listbox even though the copy command will overwrite original save
    if len(name) > 0 and isforbidden is False:

        path = "{}/{}".format(config.cfg["gamedir"], ext())

        nms = get_charnames(path)
        archive_file(path, name, "ACTION: Clicked Create Save", nms)


        cp_to_saves_cmd = lambda: copy_file(path,newdir)
        # /E – Copy subdirectories, including any empty ones.
        # /H - Copy files with hidden and system file attributes.
        # /C - Continue copying even if an error occurs.
        # /I - If in doubt, always assume the destination is a folder. e.g. when the destination does not exist
        # /Y - Overwrite all without PROMPT (ex: yes no)
        if os.path.isdir(newdir) is False:
            cmd_out = run_command(lambda: os.makedirs(newdir))
            if cmd_out[0] == "error":
                return
            lb.insert(END, "  " + name)
            cmd_out = run_command(cp_to_saves_cmd)
            if cmd_out[0] == "error":
                return
            create_notes(name, newdir)
        else:
            popup(
                "File already exists, OVERWRITE?", command=cp_to_saves_cmd, buttons=True
            )
        #save_path = f"{newdir}/{user_steam_id}/ER0000.sl2"
        #nms = get_charnames(save_path)
        #archive_file(save_path, f"ACTION: Create save\nCHARACTERS: {nms}")


def donothing():
    pass


def load_save_from_lb():
    """Fetches currently selected listbox item and copies files to game save dir."""

    if len(config.cfg["gamedir"]) < 2:
        popup("Set your Default Game Directory first")
        return
    def wrapper(comm):
        """Archives savefile in gamedir and runs command to overwrite. This function is then passed into popup function."""
        #path = f"{gamedir}/{user_steam_id}/ER0000.sl2"
        path = "{}/{}".format(config.cfg["gamedir"],ext())
        if not os.path.exists(path):
            run_command(comm)
        else:
            nms = get_charnames(path)
            archive_file(path, "None", "ACTION: Loaded save and overwrite current save file in EldenRing game directory", nms)
            run_command(comm)

    if len(lb.curselection()) < 1:
        popup("No listbox item selected.")
        return
    name = fetch_listbox_entry(lb)[0]
    src_dir = "".join((savedir, name.replace(" ", "-"), "/"))



    comm = lambda: copy_folder(src_dir, str(config.cfg["gamedir"]))
    if not os.path.isdir(f"{savedir}{name}"):
        popup(
            "Save slot does not exist.\nDid you move or delete it from data/save-files?"
        )
        lb.delete(0, END)
        load_listbox(lb)
        return
    popup(
        "Are you sure?", buttons=True, functions=(lambda: wrapper(comm), donothing)
    )


def popup(
    text,
    command=None,
    functions=False,
    buttons=False,
    button_names=("Yes", "No"),
    b_width=(6,6),
    title="Manager",
    parent_window=None):
    """text: Message to display on the popup window.
    command: Simply run the windows CMD command if you press yes.
    functions: Pass in external functions to be executed for yes/no"""
    def run_cmd():
        cmd_out = run_command(command)
        popupwin.destroy()
        if cmd_out[0] == "error":
            popupwin.destroy()

    def dontrun_cmd():
        popupwin.destroy()

    def run_func(arg):
        arg()
        popupwin.destroy()
    if parent_window is None:
        parent_window = root
    popupwin = Toplevel(parent_window)
    popupwin.title(title)
    # popupwin.geometry("200x75")
    lab = Label(popupwin, text=text)
    lab.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
    # Places popup window at center of the root window
    x = parent_window.winfo_x()
    y = parent_window.winfo_y()
    popupwin.geometry("+%d+%d" % (x + 200, y + 200))

    # Runs for simple windows CMD execution
    if functions is False and buttons is True:
        but_yes = Button(
            popupwin, text=button_names[0], borderwidth=5, width=b_width[0], command=run_cmd
        ).grid(row=1, column=0, padx=(10, 0), pady=(0, 10))
        but_no = Button(
            popupwin, text=button_names[1], borderwidth=5, width=b_width[1], command=dontrun_cmd
        ).grid(row=1, column=1, padx=(10, 10), pady=(0, 10))

    elif functions is not False and buttons is True:
        but_yes = Button(
            popupwin,
            text=button_names[0],
            borderwidth=5,
            width=b_width[0],
            command=lambda: run_func(functions[0]),
        ).grid(row=1, column=0, padx=(10, 0), pady=(0, 10))
        but_no = Button(
            popupwin,
            text=button_names[1],
            borderwidth=5,
            width=b_width[1],
            command=lambda: run_func(functions[1]),
        ).grid(row=1, column=1, padx=(10, 10), pady=(0, 10))
    # if text is the only arguement passed in, it will simply be a popup window to display text


def run_command(subprocess_command, optional_success_out="OK"):
    """Used throughout to run commands into subprocess and capture the output. Note that
    it is integrated with popup function for in app error reporting."""
    try:
        subprocess_command()
    except Exception as e:
        traceback.print_exc()
        str_err = "".join(traceback.format_exc())
        popup(str_err)
        return ("error", str_err)
    return ("Successfully completed operation", optional_success_out)


def delete_save():
    """Removes entire directory in save-files dir"""
    name = fetch_listbox_entry(lb)[0]
    comm = lambda: delete_folder(f"{savedir}{name}")

    def yes():
        path = f"{savedir}{name}/{ext()}"
        chars = get_charnames(path)
        archive_file(path, name, "ACTION: Delete save file in Manager", chars)
        out = run_command(comm)
        lb.delete(0, END)
        load_listbox(lb)

    def no():
        return

    popup(f"Delete {fetch_listbox_entry(lb)[1]}?", functions=(yes, no), buttons=True)


def fetch_listbox_entry(lstbox):
    """Returns currently selected listbox entry.
    internal name is for use with save directories and within this script.
    Name is used for display within the listbox"""

    name = ""
    for i in lstbox.curselection():
        name = name + lstbox.get(i)
    internal_name = name.strip().replace(" ", "-")
    return (internal_name, name)


def rename_slot():
    """Renames the name in save file listbox"""

    def cancel():
        popupwin.destroy()

    def done():
        new_name = ent.get()
        if len(new_name) < 1:
            popup("No name entered.")
            return
        isforbidden = False
        for char in new_name:
            if char in "~'{};:./\,:*?<>|-!@#$%^&()+":
                isforbidden = True
        if isforbidden is True:
            popup("Forbidden character used")
            return
        elif isforbidden is False:
            entries = []
            for entry in os.listdir(savedir):
                entries.append(entry)
            if new_name in entries:
                popup("Name already exists")
                return

            else:
                newnm = new_name.replace(" ", "-")
                cmd = lambda: os.rename(
                    f"{savedir}{lst_box_choice}", f"{savedir}{newnm}"
                )
                run_command(cmd)
                lb.delete(0, END)
                load_listbox(lb)
                popupwin.destroy()

    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.")
        return

    popupwin = Toplevel(root)
    popupwin.title("Rename")
    # popupwin.geometry("200x70")
    lab = Label(popupwin, text="Enter new Name:")
    lab.grid(row=0, column=0)
    ent = Entry(popupwin, borderwidth=5)
    ent.grid(row=1, column=0, padx=25, pady=10)
    x = root.winfo_x()
    y = root.winfo_y()
    popupwin.geometry("+%d+%d" % (x + 200, y + 200))
    but_done = Button(popupwin, text="Done", borderwidth=5, width=6, command=done)
    but_done.grid(row=2, column=0, padx=(25, 65), pady=(0, 15), sticky="w")
    but_cancel = Button(popupwin, text="Cancel", borderwidth=5, width=6, command=cancel)
    but_cancel.grid(row=2, column=0, padx=(70, 0), pady=(0, 15))


def update_slot():
    """Update the selected savefile with the current elden ring savedata"""
    def do(file):
        names = get_charnames(file)
        archive_file(file, lst_box_choice, "ACTION: Clicked Update save-file in Manager", names)

        copy_file(f"{config.cfg['gamedir']}/{ext()}", f"{savedir}{lst_box_choice}")


    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.")
        return
    path = f"{savedir}{lst_box_choice}/{ext()}"

    popup(text="This will take your current save in-game\nand overwrite this save slot\nAre you sure?", buttons=True, command=lambda: do(path))


def change_default_dir():
    """Opens file explorer for user to choose new default elden ring directory. Writes changes to GameSaveDir.txt"""

    newdir = fd.askdirectory()
    if len(newdir) < 1:  # User presses cancel
        return

    folder = newdir.split("/")[-1]
    f_id = re.findall(r"\d{17}", folder)

    if len(f_id) == 0:
        popup("Please select the directory named after your 17 digit SteamID")
        return


    else:

        config.set("gamedir", newdir)

        popup(f"Directory set to:\n {newdir}\n")


def rename_char(file, nw_nm, dest_slot):
    """Wrapper for hexedit.change_name for error handling"""
    try:
        x = hexedit.change_name(file, nw_nm, dest_slot)
        if x == "error":
            raise Exception
    except Exception:
        popup("Error renaming character. This may happen\nwith short names like '4'.")
        raise


def char_manager():
    """Entire character manager window for copying characters between save files"""

    def readme():
        info = ""
        with open("./data/copy-readme.txt", "r") as f:
            dat = f.readlines()
            for line in dat:
                info = info + line
        popup(info)
        # run_command("notepad ./data/copy-readme.txt")

    def open_video():
        webbrowser.open_new_tab(video_url)

    def get_char_names(lstbox, drop, v):
        """Populates dropdown menu containing the name of characters in a save file"""
        v.set("Character")
        name = fetch_listbox_entry(lstbox)[0]
        if len(name) < 1:
            return
        file = f"{savedir}{name}/{ext()}"
        names = get_charnames(file)



        drop["menu"].delete(0, "end")  # remove full list

        index = 1
        for ind, opt in enumerate(names):
            if not opt is None:
                opt = f"{index}. {opt}"
                drop["menu"].add_command(label=opt, command=TKIN._setit(v, opt))
                index += 1
            elif opt is None:
                opt = f"{ind + 1}. "
                drop["menu"].add_command(label=opt, command=TKIN._setit(v, opt))
                index += 1

    def do_copy():
        def pop_up(txt, bold=True):
            """Basic popup window used only for parent function"""
            win = Toplevel(popupwin)
            win.title("Manager")
            lab = Label(win, text=txt)
            if bold is True:
                lab.config(font=bolded)
            lab.grid(row=0, column=0, padx=15, pady=15, columnspan=2)
            x = popupwin.winfo_x()
            y = popupwin.winfo_y()
            win.geometry("+%d+%d" % (x + 200, y + 200))

        src_char = vars1.get()  # "1. charname"
        dest_char = vars2.get()
        if src_char == "Character" or dest_char == "Character":
            pop_up("Select a character first")
            return

        if src_char.split(".")[1] == " " or dest_char.split(".")[1] == " ":
            pop_up(
                "Can't write to empty slot.\nGo in-game and create a character to overwrite."
            )
            return

        name1 = fetch_listbox_entry(lb1)[0]  # Save file name. EX: main
        name2 = fetch_listbox_entry(lb2)[0]

        if len(name1) < 1 or len(name2) < 1:
            pop_up(txt="Slot not selected")
            return
        if src_char == "Character" or dest_char == "Character":
            pop_up(txt="Character not selected")
            return

        src_file = f"{savedir}{name1}/{ext()}"
        dest_file = f"{savedir}{name2}/{ext()}"

        src_ind = int(src_char.split(".")[0])
        dest_ind = int(dest_char.split(".")[0])

        # Duplicate names check
        src_char_real = src_char.split(". ")[1]
        dest_names = get_charnames(dest_file)
        nms = [i for i in dest_names]  # For archive_file only
        src_names = get_charnames(src_file)

        # If there are two or more of the name name in a destination file, quits
        rmv_none = [i for i in dest_names if not i is None]
        if max(Counter(rmv_none).values()) > 1:
            pop_up(
                "Sorry, can't handle writing to file with duplcate character names.",
                bold=False,
            )
            return

        src_names.pop(src_ind - 1)
        dest_names.pop(dest_ind - 1)
        backup_path = r"./data/temp/{}".format(ext())

        # If performing operations on the same file. Changes name to random, copies character to specified slot, then rewrites the name and re-populates the dropdown entries
        if src_file == dest_file:
            archive_file(dest_file, name2, "ACTION: Copy Character", nms)
            cmd = lambda: copy_file(src_file, backup_path)
            x = run_command(cmd)
            rand_name = hexedit.random_str()
            rename_char(backup_path, rand_name, src_ind)  # Change backup to random name
            hexedit.copy_save(backup_path, src_file, src_ind, dest_ind)
            rename_char(src_file, rand_name, dest_ind)
            get_char_names(lb1, dropdown1, vars1)
            get_char_names(lb2, dropdown2, vars2)
            vars1.set("Character")
            vars2.set("Character")
            pop_up(
                txt="Success!\nDuplicate names not supported\nGenerated a new random name",
                bold=False,
            )
            return

        # If source name in destination file, copies source file to temp folder, changes the name of copied save to random, then copies source character of
        #  copied file to destination save file, and rewrites names on destination file
        elif src_char_real in dest_names:
            archive_file(dest_file, name2, "ACTION: Copy character", nms)
            cmd = lambda: copy_file(src_file, backup_path)
            x = run_command(cmd)
            rand_name = hexedit.random_str()
            rename_char(backup_path, rand_name, src_ind)

            hexedit.copy_save(backup_path, dest_file, src_ind, dest_ind)
            rename_char(dest_file, rand_name, dest_ind)

            get_char_names(lb1, dropdown1, vars1)
            get_char_names(lb2, dropdown2, vars2)
            vars1.set("Character")
            vars2.set("Character")
            pop_up(
                txt="Duplicate names not supported\nGenerated a new random name",
                bold=False,
            )
            return

        archive_file(dest_file, name2, f"ACTION: Copy character", nms)
        hexedit.copy_save(src_file, dest_file, src_ind, dest_ind)
        rename_char(dest_file, src_char_real, dest_ind)

        get_char_names(lb1, dropdown1, vars1)
        get_char_names(lb2, dropdown2, vars2)

        vars1.set("Character")
        vars2.set("Character")

        pop_up(txt="Success!")

    def cancel():
        popupwin.destroy()

    # Main GUI content
    popupwin = Toplevel(root)
    popupwin.title("Character Manager")
    popupwin.resizable(width=True, height=True)
    popupwin.geometry("620x500")

    bolded = FNT.Font(weight="bold")  # will use the default font

    x = root.winfo_x()
    y = root.winfo_y()
    popupwin.geometry("+%d+%d" % (x + 200, y + 200))

    menubar = Menu(popupwin)
    popupwin.config(
        menu=menubar
    )  # menu is a parameter that lets you set a menubar for any given window

    helpmen = Menu(menubar, tearoff=0)
    helpmen.add_command(label="Readme", command=readme)
    helpmen.add_command(label="Watch Video", command=open_video)
    menubar.add_cascade(label="Help", menu=helpmen)

    srclab = Label(popupwin, text="Source File")
    srclab.config(font=bolded)
    srclab.grid(row=0, column=0, padx=(70, 0), pady=(20, 0))

    lb1 = Listbox(popupwin, borderwidth=3, width=15, height=10, exportselection=0)
    lb1.config(font=bolded)
    lb1.grid(row=1, column=0, padx=(70, 0), pady=(0, 0))
    load_listbox(lb1)

    destlab = Label(popupwin, text="Destination File")
    destlab.config(font=bolded)
    destlab.grid(row=0, column=1, padx=(175, 0), pady=(20, 0))

    lb2 = Listbox(popupwin, borderwidth=3, width=15, height=10, exportselection=0)
    lb2.config(font=bolded)
    lb2.grid(row=1, column=1, padx=(175, 0), pady=(0, 0))
    load_listbox(lb2)

    opts = [""]
    opts2 = [""]
    vars1 = StringVar(popupwin)
    vars1.set("Character")

    vars2 = StringVar(popupwin)
    vars2.set("Character")

    dropdown1 = OptionMenu(popupwin, vars1, *opts)
    dropdown1.grid(row=4, column=0, padx=(70, 0), pady=(20, 0))

    dropdown2 = OptionMenu(popupwin, vars2, *opts2)
    dropdown2.grid(row=4, column=1, padx=(175, 0), pady=(20, 0))

    but_select1 = Button(
        popupwin, text="Select", command=lambda: get_char_names(lb1, dropdown1, vars1)
    )
    but_select1.grid(row=3, column=0, padx=(70, 0), pady=(10, 0))

    but_select2 = Button(
        popupwin, text="Select", command=lambda: get_char_names(lb2, dropdown2, vars2)
    )
    but_select2.grid(row=3, column=1, padx=(175, 0), pady=(10, 0))

    but_copy = Button(popupwin, text="Copy", command=do_copy)
    but_copy.config(font=bolded)
    but_copy.grid(row=5, column=1, padx=(175, 0), pady=(50, 0))

    but_cancel = Button(popupwin, text="Cancel", command=cancel)
    but_cancel.config(font=bolded)
    but_cancel.grid(row=5, column=0, padx=(70, 0), pady=(50, 0))

    #mainloop()


def rename_characters():
    """Opens popup window and renames character of selected listbox item"""

    def do():
        choice = vars.get()
        choice_real = choice.split(". ")[1]
        slot_ind = int(choice.split(".")[0])
        new_name = name_ent.get()
        if len(new_name) > 16:
            popup("Name too long. Maximum of 16 characters")
            return
        if len(new_name) < 1:
            popup("Enter a name first")
            return
        if len(new_name) < 3:
            popup("Minimum 3 characters")
            return

        # Duplicate names check
        dest_names = [i for i in names]
        dest_names.pop(slot_ind - 1)

        if new_name in dest_names:
            popup("Save can not have duplicate names")
            return

        archive_file(path, choice_real, "ACTION: Rename Character", names)
        rename_char(path, new_name, slot_ind)
        popup("Successfully Renamed Character")
        drop["menu"].delete(0, "end")
        rwin.destroy()

    name = fetch_listbox_entry(lb)[0]
    if name == "":
        popup("No listbox item selected.")
        return
    path = f"{savedir}{name}/{ext()}"
    names = get_charnames(path)
    if names is False:
        popup("FileNotFoundError: This is a known issue.\nPlease try re-importing your save file.")


    chars = []
    for ind, i in enumerate(names):
        if i != None:
            chars.append(f"{ind +1}. {i}")

    rwin = Toplevel(root)
    rwin.title("Rename Character")
    rwin.resizable(width=False, height=False)
    rwin.geometry("200x150")

    bolded = FNT.Font(weight="bold")  # will use the default font
    x = root.winfo_x()
    y = root.winfo_y()
    rwin.geometry("+%d+%d" % (x + 200, y + 200))

    opts = chars
    vars = StringVar(rwin)
    vars.set("Character")

    drop = OptionMenu(rwin, vars, *opts)
    drop.grid(row=0, column=0, padx=(35, 0), pady=(10, 0))

    name_ent = Entry(rwin, borderwidth=5)
    name_ent.grid(row=1, column=0, padx=(35, 0), pady=(10, 0))

    but_go = Button(rwin, text="Rename", borderwidth=5, command=do)
    but_go.grid(row=2, column=0, padx=(35, 0), pady=(10, 0))


def changelog(run=False):
    info = ""
    with open("./data/changelog.txt", "r") as f:
        dat = f.readlines()
        for line in dat:
            info = info + f"\n\u2022 {line}\n"
    if run:
        popup(info, title="Changelog")
        return
    if config.post_update:
        popup(info, title="Changelog")


def stat_editor():
    def recalc_lvl():
        # entries = [vig_ent, min_ent, end_ent, str_ent, dex_ent, int_ent, fai_ent, arc_ent]
        lvl = 0
        try:
            for ent in entries:
                lvl += int(ent.get())
            lvl_var.set(f"Level: {lvl - 79}")
        except Exception as e:
            return

    def set_stats():
        stats = []
        try:
            for ent in entries:
                stats.append(int(ent.get()))
        except Exception as e:
            pop_up(f"Error: Make sure all fields are completed.\n{e}")
            return
        if sum(stats) - 79 < 5:
            pop_up("Character level too low.")
            return

        vig = stats[0]
        min = stats[1]
        end = stats[2]

        char = vars.get().split(". ")[1]
        char_slot = int(vars.get().split(".")[0])
        name = fetch_listbox_entry(lb1)[0]
        file = f"{savedir}{name}/{ext()}"
        try:
            nms = get_charnames(file)
            archive_file(file, name, "ACTION: Edit stats", nms)
            hexedit.set_stats(file, char_slot, stats)
            hexedit.set_attributes(file, char_slot, [vig, min, end])
            pop_up("Success!")
        except Exception as e:
            pop_up("Something went wrong!: ", e)
            return

    def pop_up(txt, bold=True):
        """Basic popup window used only for parent function"""
        win = Toplevel(popupwin)
        win.title("Manager")
        lab = Label(win, text=txt)
        if bold is True:
            lab.config(font=bolded)
        lab.grid(row=0, column=0, padx=15, pady=15, columnspan=2)
        x = popupwin.winfo_x()
        y = popupwin.winfo_y()
        win.geometry("+%d+%d" % (x + 200, y + 200))

    def validate(P):
        if len(P) == 0:
            return True
        elif len(P) < 3 and P.isdigit() and int(P) > 0:
            return True
        else:
            # Anything else, reject it
            return False

    def get_char_names(lstbox, drop, v):
        """Populates dropdown menu containing the name of characters in a save file"""
        v.set("Character")
        name = fetch_listbox_entry(lstbox)[0]
        if len(name) < 1:
            return
        file = f"{savedir}{name}/{ext()}"
        names = get_charnames(file)

        if names is False:
            popup("FileNotFoundError: This is a known issue.\nPlease try re-importing your save file.")

        drop["menu"].delete(0, "end")  # remove full list

        index = 1
        for ind, opt in enumerate(names):
            if not opt is None:
                opt = f"{index}. {opt}"
                drop["menu"].add_command(label=opt, command=TKIN._setit(v, opt))
                index += 1
            elif opt is None:
                opt = f"{ind + 1}. "
                drop["menu"].add_command(label=opt, command=TKIN._setit(v, opt))
                index += 1

    def get_char_stats():
        char = vars.get()

        if char == "Character":
            pop_up("Select a Character first")
            return

        char = vars.get().split(". ")[1]
        char_slot = int(vars.get().split(".")[0])
        name = fetch_listbox_entry(lb1)[0]
        file = f"{savedir}{name}/{ext()}"

        try:
            stats = hexedit.get_stats(file, char_slot)[0]
        except Exception as e:
            pop_up("Can't get stats, go in-game and\nload into the character first or try leveling up once.")
            return

        # entries = [vig_ent, min_ent, end_ent, str_ent, dex_ent, int_ent, fai_ent, arc_ent]
        if 0 in stats:
            pop_up("Can't get stats, go in-game and\nload into the character first or try leveling up once.")
            return

        for stat, entry in list(zip(stats, entries)):
            entry.delete(0, END)
            entry.insert(1, stat)
        lvl = sum(stats) - 79
        lvl_var.set(f"Level: {lvl}")

    # Main GUI content STAT
    popupwin = Toplevel(root)
    popupwin.title("Stat Editor")
    popupwin.resizable(width=True, height=True)
    popupwin.geometry("580x550")
    vcmd = (popupwin.register(validate), "%P")
    bolded = FNT.Font(weight="bold")  # will use the default font
    x = root.winfo_x()
    y = root.winfo_y()
    popupwin.geometry("+%d+%d" % (x + 200, y + 200))

    menubar = Menu(popupwin)
    popupwin.config(menu=menubar)
    helpmenu = Menu(menubar, tearoff=0)
    #helpmenu.add_command(label="Important Info", command=lambda: pop_up("\u2022 Offline use only! Using this feature may get you banned."))
    #helpmenu.add_command(label="Watch Video", command=lambda: webbrowser.open_new_tab(stat_edit_video))
    menubar.add_cascade(label="MAY BE UNSAFE ONLINE!", menu=helpmenu)

    # MAIN SAVE FILE LISTBOX
    lb1 = Listbox(popupwin, borderwidth=3, width=15, height=10, exportselection=0)
    lb1.config(font=bolded)
    lb1.grid(row=0, column=0, padx=(55, 0), pady=(35, 295), sticky="n")
    load_listbox(lb1)

    # SELECT LISTBOX ITEM BUTTON
    but_select1 = Button(
        popupwin, text="Select", command=lambda: get_char_names(lb1, dropdown1, vars)
    )
    but_select1.grid(row=0, column=0, padx=(55, 0), pady=(50, 0))

    # DROPDOWN MENU STUFF
    opts = [""]
    vars = StringVar(popupwin)
    vars.set("Character")
    dropdown1 = OptionMenu(popupwin, vars, *opts)
    dropdown1.grid(row=0, column=0, padx=(55, 0), pady=(120, 0))

    # GET STATS BUTTON
    but_getstats = Button(popupwin, text="Get Stats", command=get_char_stats)
    but_getstats.grid(row=0, column=0, padx=(55, 0), pady=(210, 0))

    # VIGOR
    vig_lab = Label(popupwin, text="VIGOR:")
    vig_lab.config(font=bolded)
    vig_lab.grid(row=0, column=1, padx=(60, 0), pady=(35, 0), sticky="n")

    vig_ent = Entry(
        popupwin, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    vig_ent.grid(row=0, column=1, padx=(160, 0), pady=(35, 0), sticky="n")

    # MIND
    min_lab = Label(popupwin, text="MIND:")
    min_lab.config(font=bolded)
    min_lab.grid(row=0, column=1, padx=(60, 0), pady=(75, 0), sticky="n")

    min_ent = Entry(
        popupwin, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    min_ent.grid(row=0, column=1, padx=(160, 0), pady=(75, 0), sticky="n")

    # ENDURANCE
    end_lab = Label(popupwin, text="END:")
    end_lab.config(font=bolded)
    end_lab.grid(row=0, column=1, padx=(60, 0), pady=(115, 0), sticky="n")

    end_ent = Entry(
        popupwin, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    end_ent.grid(row=0, column=1, padx=(160, 0), pady=(115, 0), sticky="n")

    # STRENGTH
    str_lab = Label(popupwin, text="STR:")
    str_lab.config(font=bolded)
    str_lab.grid(row=0, column=1, padx=(60, 0), pady=(155, 0), sticky="n")

    str_ent = Entry(
        popupwin, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    str_ent.grid(row=0, column=1, padx=(160, 0), pady=(155, 0), sticky="n")

    # DEXTERITY
    dex_lab = Label(popupwin, text="DEX:")
    dex_lab.config(font=bolded)
    dex_lab.grid(row=0, column=1, padx=(60, 0), pady=(195, 0), sticky="n")

    dex_ent = Entry(
        popupwin, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    dex_ent.grid(row=0, column=1, padx=(160, 0), pady=(195, 0), sticky="n")

    # INTELLIGENCE
    int_lab = Label(popupwin, text="INT:")
    int_lab.config(font=bolded)
    int_lab.grid(row=0, column=1, padx=(60, 0), pady=(235, 0), sticky="n")

    int_ent = Entry(
        popupwin, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    int_ent.grid(row=0, column=1, padx=(160, 0), pady=(235, 0), sticky="n")

    # FAITH
    fai_lab = Label(popupwin, text="FAITH:")
    fai_lab.config(font=bolded)
    fai_lab.grid(row=0, column=1, padx=(60, 0), pady=(275, 0), sticky="n")

    fai_ent = Entry(
        popupwin, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    fai_ent.grid(row=0, column=1, padx=(160, 0), pady=(275, 0), sticky="n")

    # ARCANE
    arc_lab = Label(popupwin, text="ARC:")
    arc_lab.config(font=bolded)
    arc_lab.grid(row=0, column=1, padx=(60, 0), pady=(315, 0), sticky="n")

    arc_ent = Entry(
        popupwin, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    arc_ent.grid(row=0, column=1, padx=(160, 0), pady=(315, 0), sticky="n")

    # lIST OF ALL ENTRIES
    entries = [vig_ent, min_ent, end_ent, str_ent, dex_ent, int_ent, fai_ent, arc_ent]

    # BOX THAT SHOWS CHAR LEVEL
    lvl_var = StringVar()
    lvl_var.set("Level: ")
    lvl_box = Entry(
        popupwin, borderwidth=2, width=10, textvariable=lvl_var, state=DISABLED
    )
    lvl_box.config(font=bolded)
    lvl_box.grid(row=0, column=1, padx=(70, 0), pady=(355, 0), sticky="n")

    # RECALCULATE LVL BUTTON
    but_recalc_lvl = Button(popupwin, text="Recalc", command=recalc_lvl)
    but_recalc_lvl.grid(row=0, column=1, padx=(220, 0), pady=(355, 0), sticky="n")

    # SET STATS BUTTON
    but_set_stats = Button(popupwin, text="Set Stats", command=set_stats)
    but_set_stats.config(font=bolded)
    but_set_stats.grid(row=0, column=1, padx=(0, 135), pady=(450, 0), sticky="n")


def set_steam_id():

    def done():

        file = f"{savedir}{name}/{ext()}"
        id = ent.get()
        x = re.findall(r"\d{17}", str(id))
        if len(x) < 1:
            popup("Your id should be a 17 digit number.")
            return
        nms = get_charnames(file)
        archive_file(file, name, "ACTION: Changed SteamID", nms)
        hexedit.replace_id(file, int(x[0]))
        popup("Successfully changed SteamID")
        popupwin.destroy()

    def cancel():
        popupwin.destroy()

    def validate(P):
        if len(P) == 0:
            return True
        elif len(P) < 18 and P.isdigit():
            return True
        else:
            # Anything else, reject it
            return False

    name = fetch_listbox_entry(lb)[0]
    if name == "":
        popup("No listbox item selected.")
        popupwin.destroy()
    cur_id = hexedit.get_id(f"{savedir}{name}/{ext()}")

    popupwin = Toplevel(root)
    popupwin.title("Set SteamID")
    vcmd = (popupwin.register(validate), "%P")
    # popupwin.geometry("200x70")
    id_lab = Label(popupwin, text=f"Current ID: {cur_id}")
    id_lab.grid(row=0, column=0)
    lab = Label(popupwin, text="Enter new ID:")
    lab.grid(row=1, column=0)

    ent = Entry(popupwin, borderwidth=5, validate="key", validatecommand=vcmd)
    ent.grid(row=2, column=0, padx=25, pady=10)
    x = root.winfo_x()
    y = root.winfo_y()
    popupwin.geometry("+%d+%d" % (x + 200, y + 200))
    but_done = Button(popupwin, text="Done", borderwidth=5, width=6, command=done)
    but_done.grid(row=3, column=0, padx=(25, 65), pady=(0, 15), sticky="w")
    but_cancel = Button(popupwin, text="Cancel", borderwidth=5, width=6, command=cancel)
    but_cancel.grid(row=3, column=0, padx=(70, 0), pady=(0, 15))


def inventory_editor():

    def pop_up(txt, bold=True):
        """Basic popup window used only for parent function"""
        win = Toplevel(popupwin)
        win.title("Manager")
        lab = Label(win, text=txt)
        if bold is True:
            lab.config(font=bolded)
        lab.grid(row=0, column=0, padx=15, pady=15, columnspan=2)
        x = popupwin.winfo_x()
        y = popupwin.winfo_y()
        win.geometry("+%d+%d" % (x + 200, y + 200))


    def get_char_names(lstbox, drop, v):
        """Populates dropdown menu containing the name of characters in a save file"""
        v.set("Character")
        name = fetch_listbox_entry(lstbox)[0]
        if len(name) < 1:
            return
        file = f"{savedir}{name}/{ext()}"
        names = get_charnames(file)
        if names is False:
            popup("FileNotFoundError: This is a known issue.\nPlease try re-importing your save file.")
        drop["menu"].delete(0, "end")  # remove full list

        index = 1
        for ind, opt in enumerate(names):
            if not opt is None:
                opt = f"{index}. {opt}"
                drop["menu"].add_command(label=opt, command=TKIN._setit(v, opt))
                index += 1
            elif opt is None:
                opt = f"{ind + 1}. "
                drop["menu"].add_command(label=opt, command=TKIN._setit(v, opt))
                index += 1


    def validate(P):
        if len(P) == 0:
            return True
        elif len(P) < 4 and P.isdigit() and int(P) > 0:
            return True
        else:
            # Anything else, reject it
            return False


    def add():
        char = c_vars.get()  # "1. charname"
        if char == "Character" or char == "":
            pop_up("Character not selected")
            return

        item = i_vars.get()
        if item == "Items" or item == "":
            pop_up("Select an item first.")
            return

        if char.split(".")[1] == " ":
            pop_up(
                "Can't write to empty slot.\nGo in-game and create a character to overwrite."
            )
            return

        name = fetch_listbox_entry(lb1)[0]  # Save file name. EX: main
        if len(name) < 1:
            pop_up(txt="Slot not selected")
            return

        dest_file = f"{savedir}{name}/{ext()}"
        char_ind = int(char.split(".")[0])

        qty = qty_ent.get()
        if qty == "":
            pop_up("Set a quantity first.")
            return
        else:
            qty = int(qty)
        itemid = itemdb.db[cat_vars.get()].get(item)
        archive_file(dest_file, name, "ACTION: Add inventory items", get_charnames(dest_file))
        x = hexedit.additem(dest_file, char_ind, itemid, qty)
        # x = hexedit.additem(dest_file,char_ind,item, qty)
        if x is None:
            pop_up(
                "Unable to set quantity. Ensure you have at least 1 of the selected items."
            )
        else:
            pop_up("Successfully added items")
        return


    def populate_items(*args):
        global itemdb
        """Populates the item dropdown by getting category"""

        cat = cat_vars.get()
        itemdb = itemdata.Items()
        items = itemdb.get_item_ls(cat)

        dropdown3["menu"].delete(0, "end")  # remove full list
        for i in items:
            if len(i) > 1:
                dropdown3["menu"].add_command(label=i, command=TKIN._setit(i_vars, i))
        i_vars.set("Items")  # default value set


    def manual_search():
        popupwin.destroy()
        find_itemid()


    def add_custom_id():
        def done():
            name = name_ent.get()
            ids = [id_ent1.get(), id_ent2.get()]
            if len(ids[0]) < 1 or len(ids[1]) < 1:
                return
            id = [ int(ids[0]), int(ids[1]) ]
            try:
                config.add_to("custom_ids", {name:id})
            except exception as e:
                popup(f"Error:\n\n{repr(e)}")
                return

            idwin.destroy()
            popupwin.destroy()
            inventory_editor()


        def validate_id(P):
            if len(P) > 0 and len(P) < 4 and P.isdigit():
                return True
            else:
                return False

        def validate_name(P):
            if len(P) > 0 and len(P) < 29 and P.isdigit() is False:
                return True
            else:
                return False
        idwin = Toplevel(root)
        idwin.title("Add Custom ID")
        vcmd_id = (idwin.register(validate_id), "%P")
        vcmd_name = (idwin.register(validate_name), "%P")
        # popupwin.geometry("200x70")

        x = root.winfo_x()
        y = root.winfo_y()
        idwin.geometry("+%d+%d" % (x + 200, y + 200))

        name_lab = Label(idwin, text="Item Name: ")
        name_lab.grid(row=0, column=0, padx=(0,0), pady=(10,0))
        name_ent = Entry(idwin, borderwidth=5, width=25, validate="key", validatecommand=vcmd_name)
        name_ent.grid(row=1, column=0, padx=(20,20), pady=(10,0))


        id_lab = Label(idwin, text="ID: ")
        id_lab.grid(row=2, column=0, padx=(20,0), pady=(15,15), sticky='w')

        id_ent1 = Entry(idwin, borderwidth=5, width=3, validate="key", validatecommand=vcmd_id)
        id_ent1.grid(row=2, column=0, padx=(50,0), pady=(15,15), sticky='w')

        id_ent2 = Entry(idwin, borderwidth=5, width=3, validate="key", validatecommand=vcmd_id)
        id_ent2.grid(row=2, column=0,  padx=(80,0), pady=(15,15), sticky='w')


        but_done = Button(idwin, text="Add", borderwidth=5, width=6, command=done)
        but_done.grid(row=2, column=0, sticky='w', padx=(120,0), pady=(15,15))


    def find_itemid():

        def validate(P):
            if len(P) == 0:
                return True
            elif len(P) < 4 and P.isdigit() and int(P) > 0:
                return True
            else:
                return False


        def open_save(pos):
            path = fd.askopenfilename()
            if pos == 1:
                file_paths[0] = path
                s1_label.config(text=path)

            if pos == 2:
                file_paths[1] = path
                s2_label.config(text=path)

            if pos == 3:
                file_paths[2] = path
                s3_label.config(text=path)

            window.lift()

        def name_id_popup(id):
            def add_custom_id(id):
                name = name_ent.get()
                if len(name) > 16:
                    popup("Name too long", parent_window=window)
                    return

                try:

                    config.add_to("custom_ids", {name:id})
                    window.destroy()
                    inventory_editor()


                except Exception as e:
                    popup(f"Something went wrong.\nvalues: {name, id}\nError: {e}")
                    return
                popupwin.destroy()

            popupwin = Toplevel(window)
            popupwin.title("Add Item ID")
            vcmd = (popupwin.register(validate), "%P")
            # popupwin.geometry("200x70")

            lab = Label(popupwin, text=f"Item ID: {id}\nEnter item name:")
            lab.grid(row=0, column=0)
            name_ent = Entry(popupwin, borderwidth=5)
            name_ent.grid(row=1, column=0, padx=25, pady=10)
            x = window.winfo_x()
            y = window.winfo_y()
            popupwin.geometry("+%d+%d" % (x + 200, y + 200))
            but_done = Button(popupwin, text="Add", borderwidth=5, width=6, command=lambda: add_custom_id(id))
            but_done.grid(row=2, column=0, padx=(25, 65), pady=(0, 15), sticky="w")
            but_cancel = Button(popupwin, text="Cancel", borderwidth=5, width=6, command=lambda: popupwin.destroy())
            but_cancel.grid(row=2, column=0, padx=(70, 0), pady=(0, 15))


        def search():

            valid = True
            # VALIDATE USER INPUTS

            if len([i for i in file_paths if not i == 0]) < 3:
                popup("Not all save files selected.", parent_window=window)
                return

            if len(q1_ent.get())< 1 or len(q2_ent.get()) < 1 or len(q3_ent.get()) < 1:
                popup("Enter a quantity for all save files.", parent_window=window)
                return

            for p in file_paths:
                if not os.path.exists(p):
                    valid = False
            if not valid:
                popup("Invalid paths")
                return


            item_id = hexedit.search_itemid(file_paths[0], file_paths[1], file_paths[2], q1_ent.get(), q2_ent.get(), q3_ent.get())
            if item_id is None:
                popup("Unable to find item ID")
                return
            name_id_popup(item_id)


        def callback(url):
            webbrowser.open_new(url)




        file_paths = [0,0,0]

        window = Toplevel(root)
        window.title("Inventory Editor")
        window.resizable(width=True, height=True)
        window.geometry("530x580")

        vcmd = (window.register(validate), "%P")

        bolded = FNT.Font(weight="bold")  # will use the default font

        x = root.winfo_x()
        y = root.winfo_y()
        window.geometry("+%d+%d" % (x + 200, y + 200))

        menubar = Menu(window)
        window.config(menu=menubar)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Search", command=find_itemid)
        menubar.add_cascade(label="Manually add item", menu=helpmenu)

        s1_label = Label(window, text="Save file #1:")
        s1_label.pack()
        q1_ent = Entry(window, borderwidth=5, width=3, validate="key", validatecommand=vcmd)
        q1_ent.pack()

        s2_label = Label(window, text="Save file #2:")
        s2_label.pack()
        q2_ent = Entry(window, borderwidth=5, width=3, validate="key", validatecommand=vcmd)
        q2_ent.pack()


        s3_label = Label(window, text="Save file #3:")
        s3_label.pack()
        q3_ent = Entry(window, borderwidth=5, width=3, validate="key", validatecommand=vcmd)
        q3_ent.pack()


        but_open1 = Button(window, text="Open #1", command=lambda:open_save(1))
        but_open1.pack()

        but_open2 = Button(window, text="Open #2", command=lambda:open_save(2))
        but_open2.pack()

        but_open3 = Button(window, text="Open #3", command=lambda:open_save(3))
        but_open3.pack()

        but_search = Button(window, text="Search", command=search)
        but_search.pack()

        part1 = "\n\n----- HOW TO -----\n\n1. Make two copies of a save file\n\n2. Load into the saves and change the value of the item you want\n  so they are all different\n\n3. Now select each save file and enter the quantity for each item\n\nNOTE: You must do this with the FIRST character slot\n\n"
        part2 = f"\n\n # You can post the item IDs on you found on Nexus so other users can add them"
        help_lab = Label(window, text=part1+part2)
        help_lab.pack()

        post_but = Button(window, text= "Post", command=lambda: callback("https://www.nexusmods.com/eldenring/mods/214?tab=bugs"))
        post_but.pack()


    def remove_id():

        def done():
            name = fetch_listbox_entry(lb1)[1].strip()
            if len(name) < 1:
                return
            try:
                config.delete_custom_id(name)
            except Exception as e:
                popup(f"Error: Unable to delete Item\n\n{repr(e)}")
            idwin.destroy()
            popupwin.destroy()
            inventory_editor()

        idwin = Toplevel(root)
        idwin.title("Remove Custom ID")
        # popupwin.geometry("200x70")

        x = root.winfo_x()
        y = root.winfo_y()
        idwin.geometry("+%d+%d" % (x + 200, y + 200))


        lb1 = Listbox(idwin, borderwidth=3, width=15, height=10, exportselection=0)
        lb1.config(font=bolded)
        lb1.grid(row=0, column=0, padx=(0,0), pady=(20, 20))
        for i in config.cfg["custom_ids"]:
            lb1.insert(END, "  " + i)

        but_done = Button(idwin, text="Delete", borderwidth=5, width=6, command=done)
        but_done.grid(row=1, column=0, sticky='w', padx=(100,0), pady=(0,15))
        but_cancel = Button(idwin, text="Cancel", borderwidth=5, width=6, command=lambda: idwin.destroy())
        but_cancel.grid(row=1, column=0, sticky='w', padx=(200,100), pady=(0,15))








    # Main GUI content STAT
    popupwin = Toplevel(root)
    popupwin.title("Inventory Editor")
    popupwin.resizable(width=True, height=True)
    popupwin.geometry("530x540")

    vcmd = (popupwin.register(validate), "%P")

    bolded = FNT.Font(weight="bold")  # will use the default font

    x = root.winfo_x()
    y = root.winfo_y()
    popupwin.geometry("+%d+%d" % (x + 200, y + 200))

    menubar = Menu(popupwin)
    popupwin.config(menu=menubar)
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Search", command=manual_search)
    helpmenu.add_command(label="Add item by ID", command=add_custom_id)
    helpmenu.add_command(label="Remove Custom Item", command=remove_id)
    helpmenu.add_command(label="View Master Spreadsheet", command=lambda:webbrowser.open_new_tab("https://github.com/Ariescyn/EldenRing-Save-Manager/blob/main/ALL_ITEM_IDS.md"))
    menubar.add_cascade(label="Custom Items", menu=helpmenu)


    # MAIN SAVE FILE LISTBOX
    lb1 = Listbox(popupwin, borderwidth=3, width=15, height=10, exportselection=0)
    lb1.config(font=bolded)
    lb1.grid(row=1, column=0, padx=(155, 0), pady=(35, 15))
    load_listbox(lb1)

    # SELECT LISTBOX ITEM BUTTON
    but_select1 = Button(
        popupwin, text="Select", command=lambda: get_char_names(lb1, dropdown1, c_vars)
    )
    # but_select1.config(bg='grey', fg='white')
    but_select1.grid(row=2, column=0, padx=(155, 0), pady=(0, 10))

    # CHARACTER DROPDOWN MENU
    opts = [""]
    c_vars = StringVar(popupwin)
    c_vars.set("Character")
    dropdown1 = OptionMenu(popupwin, c_vars, *opts)
    dropdown1.grid(row=3, column=0, padx=(155, 0), pady=(0, 10))

    # CATEGORY DROPDOWN
    opts1 = itemdb.categories
    cat_vars = StringVar(popupwin)
    cat_vars.set("Category")
    dropdown2 = OptionMenu(popupwin, cat_vars, *opts1)

    cat_vars.trace("w", populate_items)
    dropdown2.grid(row=4, column=0, padx=(155, 0), pady=(0, 10))

    # ITEM DROPDOWN
    opts2 = [""]
    i_vars = StringVar(popupwin)
    i_vars.set("Items")
    dropdown3 = OptionMenu(popupwin, i_vars, *opts2)
    dropdown3.grid(row=5, column=0, padx=(155, 0), pady=(0, 10))

    qty_ent = Entry(
        popupwin, borderwidth=5, width=3, validate="key", validatecommand=vcmd
    )
    qty_ent.grid(row=5, column=0, padx=(345, 0), pady=(0, 10))

    # SELECT LISTBOX ITEM BUTTON
    but_set = Button(popupwin, text="Set", command=add)
    but_set.config(font=bolded)
    but_set.grid(row=6, column=0, padx=(155, 0), pady=(22, 10))


def recovery():
    def do_popup(event):
        try:
            rt_click_menu.tk_popup(
                event.x_root, event.y_root
            )  # Grab x,y position of mouse cursor
        finally:
            rt_click_menu.grab_release()



    def recover():
        name = fetch_listbox_entry(lb1)[1].strip().replace(" ", "__").replace(":", ".")
        path = f"./data/archive/{name}/ER0000.xz"
        folder_path = f"./data/recovered/{name}/"
        try:
            unarchive_file(path)
            popup("Succesfully recovered save file.", functions=(lambda:open_folder_standard_exporer(folder_path), donothing), buttons=True, button_names=("Open", "Cancel"))
        except FileNotFoundError as e:
            popup(e)


    def pop_up(txt, bold=True):
        """Basic popup window used only for parent function"""
        pwin = Toplevel(win)
        pwin.title("Manager")
        lab = Label(pwin, text=txt)
        if bold is True:
            lab.config(font=bolded)
        lab.grid(row=0, column=0, padx=15, pady=15, columnspan=2)
        x = win.winfo_x()
        y = win.winfo_y()
        pwin.geometry("+%d+%d" % (x + 200, y + 200))


    win = Toplevel(root)
    win.title("Recovery")
    win.resizable(width=True, height=True)
    win.geometry("530x640")


    #bolded = FNT.Font(weight="bold")  # will use the default font

    x = root.winfo_x()
    y = root.winfo_y()
    win.geometry("+%d+%d" % (x + 200, y + 200))

    menubar = Menu(win)
    win.config(menu=menubar)
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(
        label="Readme",
        command=lambda: pop_up(
            """\u2022 This tool recovers ruined save files in case of user error.\n
                \u2022 Every time you modify/create/delete a save file, before the action is performed, a copy is created, compressed and stored in data/archive.\n
                \u2022 The original file size of 28mb is compressed to 2mb. To recover a file, simply select a file and click Restore.\n
                \u2022 Restored save files are in the data/recovered directory.\n
                \u2022 Right-click on a save in the listbox to get additional file info.
                """
        ),
    )
    menubar.add_cascade(label="Help", menu=helpmenu)




    # LISTBOX
    lb1 = Listbox(win, borderwidth=3, width=32, height=25, exportselection=0)
    lb1.config(font=bolded)
    lb1.grid(row=1, column=0, padx=(120, 0), pady=(35, 15))
    if os.path.isdir("./data/archive/") is True:
        lb1.delete(0, END)
        entries = sorted(PATH("./data/archive/").iterdir(), key=os.path.getmtime)

        for entry in reversed(entries):
            lb1.insert(END, "  " + str(entry).replace("\\", "/").split("archive/")[1].replace("__", " ").replace(".", ":"))

    rt_click_menu = Menu(lb1, tearoff=0)
    rt_click_menu.add_command(label="Get Info", command=lambda:grab_metadata(f"./data/archive/{fetch_listbox_entry(lb1)[1].strip()}/info.txt"   )  )

    lb1.bind("<Button-3>", do_popup)



    # SELECT LISTBOX ITEM BUTTON
    but_select1 = Button(win, text="Recover", command=recover)
    but_select1.grid(row=2, column=0, padx=(120, 0), pady=(0, 10))


def get_charnames(file):
    """wrapper for hexedit.get_names"""



    out = hexedit.get_names(file)
    if out is False:
        popup(f"Error: Unable to get character names.\nDoes the following path exist?\n{file}")
    else:
        return out


def finish_update():
    if os.path.exists("./data/GameSaveDir.txt"):  # Legacy file for pre v1.5 versions
        os.remove("./data/GameSaveDir.txt")


    if config.post_update:  # Will be ran on first launch after running update.exe

        if not os.path.exists("./data/save-files-pre-V1.5-BACKUP"): # NONE OF THIS WILL BE RUN ON v1.5+
            try:
                copy_folder(savedir, "./data/save-files-pre-V1.5-BACKUP")
            except Exception as e:
                traceback.print_exc()
                str_err = "".join(traceback.format_exc())
                popup(str_err)

            for dir in os.listdir(savedir):  # Reconstruct save-file structure for pre v1.5 versions

                try:
                    id = re.findall(r"\d{17}", str(os.listdir(f"{savedir}{dir}/")))
                    if len(id) < 1:
                        continue

                    shutil.move(f"{savedir}{dir}/{id[0]}/{ext()}", f"{savedir}{dir}/{ext()}")
                    for i in ["GraphicsConfig.xml", "notes.txt", "steam_autocloud.vdf"]:
                        if os.path.exists(f"{savedir}{dir}/{i}"):
                            os.remove(f"{savedir}{dir}/{i}")

                    delete_folder(f"{savedir}{dir}/{id[0]}")
                except Exception as e:
                    traceback.print_exc()
                    str_err = "".join(traceback.format_exc())
                    popup(str_err)
                    continue



def seamless_coop():
    x = lambda: 'Enabled' if config.cfg['seamless-coop'] else 'Disabled'
    popup(f"Enable this option to support the seamless Co-op mod .co2 extension\nIt's recommended to use a separate copy of the Manager just for seamless co-op.\n\nCurrent State: {x()}", buttons=True, button_names=("Enable", "Disable"), functions=(lambda:config.set("seamless-coop", True), lambda:config.set("seamless-coop", False)))


def ext():
    if config.cfg["seamless-coop"]:
        return "ER0000.co2"
    elif config.cfg["seamless-coop"] is False:
        return "ER0000.sl2"



# ----- LEGACY FUNCTIONS (NO LONGER USED) -----

def quick_restore():
    """Copies the selected save file in temp to selected listbox item"""
    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.")
        return
    src = f"./data/temp/{lst_box_choice}"
    dest = f"{savedir}{lst_box_choice}"
    file = f"{dest}/{user_steam_id}/{ext()}" # USER_STEAM_ID no longer used
    archive_file(file,lst_box_choice, "ACTION: Quick Restore", get_charnames(file))
    cmd = lambda: copy_folder(src, dest)
    x = run_command(cmd)
    if x[0] != "error":
        popup("Successfully restored backup.")


def quick_backup():
    """Creates a backup of selected listbox item to temp folder"""
    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.")
        return

    src = f"{savedir}{lst_box_choice}"
    dest = f"./data/temp/{lst_box_choice}"
    cmd = lambda: copy_folder(src, dest)
    x = run_command(cmd)
    if x[0] != "error":
        popup("Successfully created backup.")


def save_backup():
    """Quickly save a backup of the current game save. Used from the menubar."""
    comm = lambda: copy_folder(gamedir, backupdir)

    if os.path.isdir(backupdir) is False:
        cmd_out1 = run_command(lambda: os.makedirs(backupdir))
        if cmd_out1[0] == "error":
            return
    cmd_out2 = run_command(comm)
    if cmd_out2[0] == "error":
        return
    else:
        popup("Backup saved successfully")


def load_backup():
    """Quickly load a backup of the current game save. Used from the menubar."""
    comm = lambda: copy_folder(backupdir, gamedir)
    if os.path.isdir(backupdir) is False:
        run_command(lambda: os.makedirs(backupdir))

    if len(re.findall(r"\d{17}", str(os.listdir(backupdir)))) < 1:
        popup("No backup found")

    else:
        popup("Overwrite existing save?", command=comm, buttons=True)


def create_notes(name, dir):
    """Create a notepad document in specified save slot."""

    return
    name = name.replace(" ", "-")
    cmd = lambda: os.close(os.open(f"{dir}/notes.txt", os.O_CREAT))
    run_command(cmd)


def about():
    popup(text="Author: Lance Fitz\nEmail: scyntacks94@gmail.com\nGithub: github.com/Ariescyn")



# ----- MAIN GUI CONTENT -----


root = Tk()
root.resizable(width=False, height=False)
root.title("{} {}".format(app_title, version))

root.geometry("830x561")
try:
    root.iconbitmap(icon_file)
except Exception:
    print("Unix doesn't support .ico - setting the background as app icon")
    root.iconphoto(True, PhotoImage(background_img))

# FANCY STUFF
bg_img = ImageTk.PhotoImage(image=Image.open(background_img))
background = Label(root, image=bg_img)

background.place(x=bk_p[0], y=bk_p[1], relwidth=1, relheight=1)

# Images used on button widgets
done_img = ImageTk.PhotoImage(
    image=Image.open("./data/assets/but_done.png").resize((50, 30))
)
load_save_img = ImageTk.PhotoImage(
    image=Image.open("./data/assets/but_load_save.png").resize((85, 40))
)
delete_save_img = ImageTk.PhotoImage(
    image=Image.open("./data/assets/but_delete_save.png").resize((85, 40))
)


menubar = Menu(root)
root.config(
    menu=menubar
)

# FILE MENU
filemenu = Menu(menubar, tearoff=0)

#filemenu.add_command(label="Save Backup", command=save_backup)
#filemenu.add_command(label="Restore Backup", command=load_backup)

filemenu.add_command(label="Import Save File", command=import_save)
filemenu.add_command(label="seamless Co-op Mode", command=seamless_coop)
filemenu.add_command(label="Force quit EldenRing", command=forcequit)
filemenu.add_separator()
filemenu.add_command(label="Donate", command=lambda:webbrowser.open_new_tab("https://www.paypal.com/donate/?hosted_button_id=H2X24U55NUJJW"))
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)



# EDIT MENU
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Change Default Directory", command=change_default_dir)
#editmenu.add_command(label="Reset To Default Directory", command=reset_default_dir)
editmenu.add_command(label="Change Default SteamID", command=change_default_steamid)
editmenu.add_command(label="Check for updates", command=update_app)
menubar.add_cascade(label="Edit", menu=editmenu)

# TOOLS MENU
toolsmenu = Menu(menubar, tearoff=0)
toolsmenu.add_command(label="Character Manager", command=char_manager)
toolsmenu.add_command(label="Stat Editor", command=stat_editor)
toolsmenu.add_command(label="Inventory Editor", command=inventory_editor)
toolsmenu.add_command(label="File Recovery", command=recovery)
menubar.add_cascade(label="Tools", menu=toolsmenu)

# HELP MENU
helpmenu = Menu(menubar, tearoff=0)
#helpmenu.add_command(label="Readme", command=help_me)
#helpmenu.add_command(label="About", command=about)
helpmenu.add_command(label="Watch Video", command=lambda: webbrowser.open_new_tab(video_url))
helpmenu.add_command(label="Changelog", command=lambda:changelog(run=True))
helpmenu.add_command(label="Report Bug", command=lambda:popup("Report bugs on Nexus, GitHub or email me at scyntacks94@gmail.com"))
menubar.add_cascade(label="Help", menu=helpmenu)

#
create_save_lab = Label(root, text="Create Save:", font=("Impact", 15))
create_save_lab.config(fg="grey")
create_save_lab.grid(row=0, column=0, padx=(80, 10), pady=(0, 260))

cr_save_ent = Entry(root, borderwidth=5)
# cr_save_ent.config(bg='grey')
cr_save_ent.grid(row=0, column=1, pady=(0, 260))

but_go = Button(root, text="Done", image=done_img, borderwidth=0, command=create_save)
but_go.grid(row=0, column=2, padx=(10, 0), pady=(0, 260))

lb = Listbox(root, borderwidth=3, width=25, height=16)
bolded = FNT.Font(weight="bold")  # will use the default font
lb.config(font=bolded)
lb.grid(row=0, column=3, padx=(110, 0), pady=(30, 0))


# -----------------------------------------------------------
# right click popup menu in listbox


def do_popup(event):
    try:
        rt_click_menu.tk_popup(
            event.x_root, event.y_root
        )  # Grab x,y position of mouse cursor
    finally:
        rt_click_menu.grab_release()


def open_notes():
    name = fetch_listbox_entry(lb)[0]
    if len(name) < 1:
        popup("No listbox item selected.")
        return
    cmd = lambda: open_textfile_in_editor(f"{savedir}{name}/notes.txt")
    out = run_command(cmd)


rt_click_menu = Menu(lb, tearoff=0)
#rt_click_menu.add_command(label="Edit Notes", command=open_notes)
rt_click_menu.add_command(label="Rename Save", command=rename_slot)
rt_click_menu.add_command(label="Rename Characters", command=rename_characters)
rt_click_menu.add_command(label="Update", command=update_slot)
#rt_click_menu.add_command(label="Quick Backup", command=quick_backup)
#rt_click_menu.add_command(label="Quick Restore", command=quick_restore)
rt_click_menu.add_command(label="Change SteamID", command=set_steam_id)
rt_click_menu.add_command(label="Open File Location", command=open_folder)
lb.bind(
    "<Button-3>", do_popup
)  # button 3 is right click, so when right clicking inside listbox, do_popup is executed at cursor position

load_listbox(lb)  # populates listbox with saves on runtime

but_load_save = Button(
    root,
    text="Load Save",
    image=load_save_img,
    borderwidth=0,
    command=load_save_from_lb,
)
but_delete_save = Button(
    root,
    text="Delete Save",
    image=delete_save_img,
    borderwidth=0,
    command=delete_save,
)

but_load_save.grid(row=3, column=3, pady=(12, 0))
but_delete_save.grid(row=3, column=3, padx=(215, 0), pady=(12, 0))







# INITIALIZE APP
config = Config()
itemdb = itemdata.Items()
if not os.path.exists("./data/save-files"):
    os.makedirs("./data/save-files")

update_app(True)

if len(config.cfg["steamid"]) != 17:
    popup("SteamID not set. Click edit > Change default SteamID to set.")



changelog()
finish_update()
config.set_update(False)
root.mainloop()
