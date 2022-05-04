import sys
import traceback
from tkinter import *
from tkinter import font as FNT
from tkinter import filedialog as fd
from tkinter import ttk
import tkinter as TKIN
from collections import Counter
from PIL import Image, ImageTk
import subprocess, os, zipfile, requests, re, time, hexedit, webbrowser, itemdata
from os_layer import *


# set always the working dir to the correct folder for unix env
if not is_windows:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load and parse save directory
if not os.path.exists(gamesavedir_txt):
    with open(gamesavedir_txt, "w") as fh:
        fh.write(eldenring_savedata_dir)

with open(gamesavedir_txt, "r+") as fh:
    s_path = fh.readline()
    # before 1.44 old txt path was like this on windows: %APPDATA%\EldenRing\"
    # this convert env variables, transform to forward slash and escape spaces
    if s_path.startswith('"'):
        s_path = (
            s_path.strip()
            .replace('"', "")
            .replace("%APPDATA%", os.getenv("APPDATA"))
            .replace("\\", "/")
            .replace(" ", "\\ ")
        )
        if not s_path.endswith("/"):
            s_path = s_path + "/"
        fh.truncate(0)
        fh.seek(0)
        fh.write(s_path)
    gamedir = s_path


def get_steamid():
    """Get users steamID by pulling folder name."""
    try:
        for dir_name in os.listdir(eldenring_savedata_dir):
            steam_id = None
            if len(dir_name) == 17:
                steam_id = dir_name
                break

        if not steam_id:
            popup(
                "Steam ID not detected. Ensure your default game directory\nis set properly before performing any actions."
            )
            return None
        else:
            return steam_id
    except FileNotFoundError:
        popup(
            "Steam ID not detected. Ensure your default game directory\nis set properly before performing any actions."
        )
        return None


def import_save():
    """Opens file explorer to choose a save file to import, Then checks if the files steam ID matches users, and replaces it with users id"""
    if os.path.isdir(savedir) is False:
        os.makedirs(savedir)
    d = fd.askopenfilename()

    if len(d) < 1:
        return

    if not d.endswith(("ER0000.sl2")):
        popup("Select a valid save file!\nIt should be named: ER0000.sl2")
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

        id = user_steam_id
        newdir = "{}{}/{}/".format(savedir, name.replace(" ", "-"), id)
        cp_to_saves_cmd = lambda: copy_file(d, newdir)

        if os.path.isdir(newdir) is False:
            cmd_out = run_command(lambda: os.makedirs(newdir))

            if cmd_out[0] == "error":
                return
            lb.insert(END, "  " + name)
            cmd_out = run_command(cp_to_saves_cmd)
            if cmd_out[0] == "error":
                return
            create_notes(name, "{}{}/".format(savedir, name.replace(" ", "-")))

            file_id = hexedit.get_id(f"{newdir}/ER0000.sl2")
            if file_id != int(id):
                popup(
                    f"Steam ID of file did not match your own ID\nAutomatically patched file with your Steam ID\nFile ID: {file_id}\nYour ID: {id}"
                )
                hexedit.replace_id(f"{newdir}/ER0000.sl2", int(id))

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
    """Writes the original gamedir to text file"""
    global gamedir
    with open(gamesavedir_txt, "w") as fh:
        fh.write(eldenring_savedata_dir)
    with open(gamesavedir_txt, "r") as fh:
        gamedir = fh.readline()
    popup("Successfully reset default directory")


def create_notes(name, dir):
    """Create a notepad document in specified save slot."""
    name = name.replace(" ", "-")
    cmd = lambda: os.close(os.open(f"{dir}/notes.txt", os.O_CREAT))
    run_command(cmd)


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


def create_save():
    """Takes user input from the create save entry box and copies files from game save dir to the save-files dir of app"""
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
        cp_to_saves_cmd = lambda: copy_folder(gamedir, newdir)
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


def donothing():
    pass


def load_save_from_lb():
    """Fetches currently selected listbox item and copies files to game save dir."""
    if len(lb.curselection()) < 1:
        popup("No listbox item selected.")
        return
    name = fetch_listbox_entry(lb)[0]
    src_dir = "".join((savedir, name.replace(" ", "-"), "/"))
    comm = lambda: copy_folder(src_dir, gamedir)
    if not os.path.isdir(f"{savedir}{name}"):
        popup(
            "Save slot does not exist.\nDid you move or delete it from data/save-files?"
        )
        lb.delete(0, END)
        load_listbox(lb)
        return
    popup(
        "Are you sure?", buttons=True, functions=(lambda: run_command(comm), donothing)
    )


def popup(
    text,
    command=None,
    functions=False,
    buttons=False,
    button_names=("Yes", "No"),
    title="Manager",
):
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

    popupwin = Toplevel(root)
    popupwin.title(title)
    # popupwin.geometry("200x75")
    lab = Label(popupwin, text=text)
    lab.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
    # Places popup window at center of the root window
    x = root.winfo_x()
    y = root.winfo_y()
    popupwin.geometry("+%d+%d" % (x + 200, y + 200))

    # Runs for simple windows CMD execution
    if functions is False and buttons is True:
        but_yes = Button(
            popupwin, text=button_names[0], borderwidth=5, width=6, command=run_cmd
        ).grid(row=1, column=0, padx=(10, 0), pady=(0, 10))
        but_no = Button(
            popupwin, text=button_names[1], borderwidth=5, width=6, command=dontrun_cmd
        ).grid(row=1, column=1, padx=(10, 10), pady=(0, 10))

    elif functions is not False and buttons is True:
        but_yes = Button(
            popupwin,
            text=button_names[0],
            borderwidth=5,
            width=6,
            command=lambda: run_func(functions[0]),
        ).grid(row=1, column=0, padx=(10, 0), pady=(0, 10))
        but_no = Button(
            popupwin,
            text=button_names[1],
            borderwidth=5,
            width=6,
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


def about():
    popup(
        text="Author: Lance Fitz\nEmail: scyntacks94@gmail.com\nGithub: github.com/Ariescyn"
    )


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
    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.")
        return
    cmd = lambda: copy_folder(gamedir, "".join((savedir, lst_box_choice)))
    popup(text="Are you sure?", buttons=True, command=cmd)


def change_default_dir():
    """Opens file explorer for user to choose new default elden ring directory. Writes changes to GameSaveDir.txt"""
    global gamedir
    newdir = fd.askdirectory()
    if len(newdir) < 1:  # User presses cancel
        return

    # Check if selected directory contains 17 digit steamid folder and GraphicsConfig.xml
    if (
        os.path.exists(f"{newdir}/GraphicsConfig.xml")
        and len(re.findall(r"\d{17}", str(os.listdir(newdir)))) > 0
    ):
        with open(gamesavedir_txt, "w") as fh:
            fh.write(newdir)
        gamedir = newdir
        popup(f"Directory set to:\n {newdir}")
    else:
        popup(
            "Cant find savedata in this Directory.\nThe selected folder should contain GraphicsConfig.xml and\na folder named after your 17 digit SteamID"
        )


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
        file = f"{savedir}{name}/{user_steam_id}/ER0000.sl2"
        names = hexedit.get_names(file)
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

        src_file = f"{savedir}{name1}/{user_steam_id}/ER0000.sl2"
        dest_file = f"{savedir}{name2}/{user_steam_id}/ER0000.sl2"

        src_ind = int(src_char.split(".")[0])
        dest_ind = int(dest_char.split(".")[0])

        # Duplicate names check
        src_char_real = src_char.split(". ")[1]
        dest_names = hexedit.get_names(dest_file)
        src_names = hexedit.get_names(src_file)

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
        backup_path = r"./data/temp/ER0000.sl2"

        # If performing operations on the same file. Changes name to random, copies character to specified slot, then rewrites the name and re-populates the dropdown entries
        if src_file == dest_file:
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

    mainloop()


def quick_restore():
    """Copies the selected save file in temp to selected listbox item"""
    lst_box_choice = fetch_listbox_entry(lb)[0]
    if len(lst_box_choice) < 1:
        popup("No listbox item selected.")
        return
    src = f"./data/temp/{lst_box_choice}"
    dest = f"{savedir}{lst_box_choice}"
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
        dest_names = names
        dest_names.pop(slot_ind - 1)

        if new_name in dest_names:
            popup("Save can not have duplicate names")
            return

        rename_char(path, new_name, slot_ind)
        popup("Successfully Renamed Character")
        drop["menu"].delete(0, "end")
        rwin.destroy()

    name = fetch_listbox_entry(lb)[0]
    if name == "":
        popup("No listbox item selected.")
        return
    path = f"{savedir}{name}/{user_steam_id}/ER0000.sl2"
    names = hexedit.get_names(path)
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


def changelog():
    # out = run_command("notepad ./data/changelog.txt")
    info = ""
    with open("./data/changelog.txt", "r") as f:
        dat = f.readlines()
        for line in dat:
            info = info + line
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
        file = f"{savedir}{name}/{user_steam_id}/ER0000.sl2"
        try:
            hexedit.set_stats(file, char_slot, stats)
            hexedit.set_attributes(file, char_slot, [vig, min, end])
            pop_up("Success!")
        except Exception as e:
            pop_up("Something went wrong!: ", e)

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
        file = f"{savedir}{name}/{user_steam_id}/ER0000.sl2"
        names = hexedit.get_names(file)
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
        file = f"{savedir}{name}/{user_steam_id}/ER0000.sl2"

        try:
            stats = hexedit.get_stats(file, char_slot)[0]
        except Exception as e:
            pop_up("Can't get stats, go in-game and\nload into the character first.")
            return

        # entries = [vig_ent, min_ent, end_ent, str_ent, dex_ent, int_ent, fai_ent, arc_ent]
        if 0 in stats:
            pop_up("Can't get stats, go in-game and\nload into the character first.")
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
    helpmenu.add_command(
        label="Important Info",
        command=lambda: pop_up(
            "\u2022 Offline use only! Using this feature may get you banned."
        ),
    )
    helpmenu.add_command(
        label="Watch Video", command=lambda: webbrowser.open_new_tab(stat_edit_video)
    )
    menubar.add_cascade(label="Help", menu=helpmenu)

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
    global user_steam_id

    def done():

        file = f"{savedir}{name}/{user_steam_id}/ER0000.sl2"
        id = ent.get()
        x = re.findall(r"\d{17}", str(id))
        if len(x) < 1:
            popup("Your id should be a 17 digit number.")
            return
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

    popupwin = Toplevel(root)
    popupwin.title("Set SteamID")
    vcmd = (popupwin.register(validate), "%P")
    # popupwin.geometry("200x70")
    lab = Label(popupwin, text="Enter your ID:")
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

    name = fetch_listbox_entry(lb)[0]
    if name == "":
        popup("No listbox item selected.")
        popupwin.destroy()


def inventory_editor():
    itemdb = itemdata.Items()

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
        file = f"{savedir}{name}/{user_steam_id}/ER0000.sl2"
        names = hexedit.get_names(file)
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
        elif len(P) < 3 and P.isdigit() and int(P) > 0:
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

        dest_file = f"{savedir}{name}/{user_steam_id}/ER0000.sl2"
        char_ind = int(char.split(".")[0])

        qty = qty_ent.get()
        if qty == "":
            pop_up("Set a quantity first.")
            return
        else:
            qty = int(qty)
        itemid = itemdb.db[cat_vars.get()].get(item)

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
        """Populates the item dropdown by getting category"""
        cat = cat_vars.get()
        items = itemdb.get_item_ls(cat)

        dropdown3["menu"].delete(0, "end")  # remove full list
        for i in items:
            if len(i) > 1:
                dropdown3["menu"].add_command(label=i, command=TKIN._setit(i_vars, i))
        i_vars.set("Items")  # default value set

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
    helpmenu.add_command(
        label="Important Info",
        command=lambda: pop_up(
            "\u2022 Offline use only! Using this feature may get you banned.\n\n\u2022 You must have at least 1 of the selected item in your inventory."
        ),
    )
    # helpmenu.add_command(label='Watch Video', command=lambda:webbrowser.open_new_tab(stat_edit_video))
    menubar.add_cascade(label="Help", menu=helpmenu)

    # warn_lab = Label(popupwin,text='Note: You must already have at least 1 of the selected item in your inventory' )
    # qty_lab.config(font=bolded)
    # warn_lab.grid(row=0, column=0, padx=(55,0), pady=(10,10))

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


menubar = Menu(root)  # Create menubar attached to main window
root.config(
    menu=menubar
)  # menu is a parameter that lets you set a menubar for any given window

filemenu = Menu(menubar, tearoff=0)  # Create file menu attached to menubar
filemenu.add_command(label="Save Backup", command=save_backup)
filemenu.add_command(label="Restore Backup", command=load_backup)
filemenu.add_command(label="Import Save File", command=import_save)
filemenu.add_separator()
filemenu.add_command(label="Force quit EldenRing", command=forcequit)
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(
    label="File", menu=filemenu
)  # add_cascade creates a new hierarchical menu by associating a given menu to a parent menu


editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Change Default Directory", command=change_default_dir)
editmenu.add_command(label="Reset To Default Directory", command=reset_default_dir)
editmenu.add_command(label="Check for updates", command=update_app)
menubar.add_cascade(label="Edit", menu=editmenu)

toolsmenu = Menu(menubar, tearoff=0)
toolsmenu.add_command(label="Character Manager", command=char_manager)
toolsmenu.add_command(label="Stat Editor", command=stat_editor)
toolsmenu.add_command(label="Inventory Editor", command=inventory_editor)
menubar.add_cascade(label="Tools", menu=toolsmenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Readme", command=help_me)
helpmenu.add_command(label="About", command=about)
helpmenu.add_command(
    label="Watch Video", command=lambda: webbrowser.open_new_tab(video_url)
)
helpmenu.add_command(label="Changelog", command=changelog)
menubar.add_cascade(label="Help", menu=helpmenu)


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
rt_click_menu.add_command(label="Edit Notes", command=open_notes)
rt_click_menu.add_command(label="Rename Save", command=rename_slot)
rt_click_menu.add_command(label="Rename Characters", command=rename_characters)
rt_click_menu.add_command(label="Update", command=update_slot)
rt_click_menu.add_command(label="Quick Backup", command=quick_backup)
rt_click_menu.add_command(label="Quick Restore", command=quick_restore)
rt_click_menu.add_command(label="Change SteamID", command=set_steam_id)
rt_click_menu.add_command(label="Open File Location", command=open_folder)
# rt_click_menu.add_command(label=)
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

user_steam_id = get_steamid()
update_app(True)

# Every release comes with PostUpdate.check, and will be deleted after the app is launched for the first time
if os.path.exists("./data/PostUpdate.check"):
    changelog()
    os.remove("./data/PostUpdate.check")


root.mainloop()
