from tkinter import *
from tkinter import font as FNT
from PIL import Image, ImageTk
from tkinter import ttk
import subprocess
import os

# Directories
gamedir = "%APPDATA%\\EldenRing\\"
savedir = ".\\data\\save-files\\"
app_title = "Elden Ring Save Manager"
backupdir = ".\\data\\backup\\"
version = 'v1.1'
background_img = './data/background.png'
icon_file = './data/icon.ico'

# Positioning, Only used for previous .place() methods. Switched to grid() now
bk_p = (-140,20) # Background image position
cr_save_p = (65,55) # 'create save' label position
sv_ent_p = (157,55) # entry box to name save position
but_go_p = (297,51) # 'Done' button to confirm save position
lb_p = (465,50) # Listbox position
but_load_p = (503,395) # Load save slot button position
but_del_p = (580,395) # Delete save slot position


def create_notes(name,dir):
    """Create a notepad document in specified save slot."""
    name = name.replace(' ', '-')
    cmd = f'type nul > {dir}\\notes.txt'
    run_command(cmd)


def help_me():
    out = run_command("notepad ./data/readme.txt")


def load_listbox():
    """LOAD current save files and insert them into listbox. This is Used
        to load the listbox on startup and also after deleting an item from the listbox to refresh the entries."""
    if os.path.isdir(savedir) is True:
        for entry in os.listdir(savedir):
            lb.insert(END, "  " + entry.replace('-', ' '))


def save_backup():
    """Quickly save a backup of the current game save. Used from the menubar."""
    comm = "Xcopy {} {} /E /H /C /I /Y".format(gamedir,backupdir)
    if os.path.isdir(backupdir) is False:
        cmd_out1 = run_command("md {}".format(backupdir))
        if cmd_out1[0] == 'error':
            return
    cmd_out2 = run_command(comm)
    if cmd_out2[0] == 'error':
        return
    else:
        popup('Success')


def load_backup():
    """Quickly load a backup of the current game save. Used from the menubar."""
    comm = "Xcopy {} {} /E /H /C /I /Y".format(backupdir,gamedir)
    if os.path.isdir(backupdir) is False:
        cmd_out = run_command("md {}".format(backupdir))
        if cmd_out[0] == 'error':
            return
    popup('Overwrite existing save?',command=comm, buttons=True)


def create_save():
    """Takes user input from the create save entry box and copies files from game save dir to the save-files dir of app"""
    name = cr_save_ent.get()
    #newdir = ".\\saves\\\"{}\"".format(name)
    newdir = "{}{}".format(savedir,name.replace(' ', '-'))

    # Check the given name in the entry
    if len(name) < 1:
        popup('No name entered')

    isforbidden = False
    for char in name:
        if char in "~'{};:./\,:*?<>|-!@#$%^&()+":
            isforbidden = True
    if isforbidden is True:
        popup('Forbidden character used')

    # Make sure saves directory exists

    if os.path.isdir(savedir) is False:
        #subprocess.run("md .\\save-files", shell=True)
        cmd_out = run_command("md {}".format(savedir))
        if cmd_out[0] == 'error':
            return


    # If new save name doesnt exist, insert it into the listbox,
    # otherwise duplicates will appear in listbox even though the copy command will overwrite original save
    if len(name) > 0 and isforbidden is False:
        cp_to_saves_cmd = "Xcopy {} {} /E /H /C /I /Y".format(gamedir,newdir)
        # /E – Copy subdirectories, including any empty ones.
        # /H - Copy files with hidden and system file attributes.
        # /C - Continue copying even if an error occurs.
        # /I - If in doubt, always assume the destination is a folder. e.g. when the destination does not exist
        # /Y - Overwrite all without PROMPT (ex: yes no)
        if os.path.isdir(newdir) is False:
            cmd_out = run_command("md {}".format(newdir))
            if cmd_out[0]  == 'error':
                return
            lb.insert(END, "  " + name)
            cmd_out = run_command(cp_to_saves_cmd)
            if cmd_out[0] == 'error':
                return
            create_notes(name, newdir)
        else:
            popup('File already exists, OVERWRITE?', command=cp_to_saves_cmd, buttons=True)


def donothing():
    pass


def load_save_from_lb():
    """Fetches currently selected listbox item and copies files to game save dir."""
    if len(lb.curselection()) < 1:
        popup('No listbox item selected.')
        return
    name = fetch_listbox_entry()[0]
    comm = "Xcopy {}{}\\ {} /E /H /C /I /Y".format(savedir,name.replace(' ', '-'),gamedir)
    cmd_out = run_command(comm)
    if cmd_out[0] == 'error':
        return
    else:
        popup('Success')


def popup(text, command=None, functions=False, buttons=False):
    """text: Message to display on the popup window.
       command: Simply run the windows CMD command if you press yes.
       functions: Pass in external functions to be executed for yes/no"""

    def run_cmd():
        cmd_out = run_command(command)
        popupwin.destroy()
        if cmd_out[0] == 'error':
            popupwin.destroy()

    def dontrun_cmd():
        popupwin.destroy()


    def run_func(arg):
        arg()
        popupwin.destroy()


    # Toplevel object which will
    # be treated as a new window
    popupwin = Toplevel(root)
    popupwin.title("Manager")
    popupwin.geometry("200x70")
    Label(popupwin, text=text).pack()

    # Places popup window at center of the root window
    x = root.winfo_x()
    y = root.winfo_y()
    popupwin.geometry("+%d+%d" %(x+200,y+200))
#    popupwin.wm_transient(popupwin)

    # Runs for simple windows CMD execution
    if functions is False and buttons is True:
        but_yes = Button(popupwin, text='Yes', borderwidth=5, width=6, command=run_cmd).place(x=35, y=25)
        but_no = Button(popupwin, text='No', borderwidth=5, width=6, command=dontrun_cmd).place(x=105, y=25)
    # Runs external functions

                                                                            #lambda is anonymous function that wraps run_func() and passes the popup arguement functions tuple into run_func
                                                                            # Needed for executing functions passed into this popup function and still accessing the SCOPE of this popup
                                                                            # If i simply pass in a function to the command, and wanted that function to close the popup window after its done,
                                                                            # it would be out of the scope of that external function.
                                                                            # Will try object oriented approach next time, as SELF would be a good fix
    elif functions is not False and buttons is True:
        but_yes = Button(popupwin, text='Yes', borderwidth=5, width=6, command=lambda: run_func(functions[0])).place(x=35, y=25)
        but_no = Button(popupwin, text='No', borderwidth=5, width=6, command=lambda: run_func(functions[1])).place(x=105, y=25)
    # if text is the only arguement passed in, it will simply be a popup window to display text


def run_command(subprocess_command):
    """ Used throughout to run commands into subprocess and capture the output. Note that
        it is integrated with popup function for in app error reporting."""

    out = subprocess.run(subprocess_command, shell=True , capture_output=True, text=True)
    if len(out.stderr) > 0:
        popup(out.stderr)
        return ('error',out.stderr)

    else:
        return ('success',out.stdout)


def delete_save():
    name = fetch_listbox_entry()[0]
    comm = "rmdir {}{} /s /q".format(savedir,name)
    def yes():
        out = run_command(comm)
        lb.delete(0,END)
        load_listbox()
    def no():
        return
    popup(f'Delete {fetch_listbox_entry()[1]}?', functions=(yes,no), buttons=True)


def fetch_listbox_entry():
    """ Returns currently selected listbox entry.
        internal name is for use with save directories and within this script.
        Name is used for display within the listbox"""


    name = ''
    for i in lb.curselection():
        name = name + lb.get(i)
    internal_name = name.strip().replace(' ', '-')
    return (internal_name, name)


def about():
    popup(text='Author: Lance Fitz\nEmail: scyntacks94@gmail.com\nGithub: github.com/Ariescyn')




# ----- MAIN CONTENT -----

root = Tk()
root.resizable(width=False, height=False)
root.title('{} {}'.format(app_title, version))
root.geometry('740x541')
root.iconbitmap(icon_file)

#bg = ImageTk.PhotoImage(file='background.png')
bg_img = ImageTk.PhotoImage(image=Image.open(background_img))
background = Label(root, image=bg_img)

background.place(x=bk_p[0], y=bk_p[1], relwidth=1, relheight=1)
#background.grid(row=4, column=5)



menubar = Menu(root) # Create menubar attached to main window
root.config(menu=menubar) # menu is a parameter that lets you set a menubar for any given window

filemenu = Menu(menubar, tearoff=0) # Create file menu attached to menubar
filemenu.add_command(label="Save Backup", command=save_backup)
filemenu.add_command(label="Restore Backup", command=load_backup)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)

menubar.add_cascade(label="File", menu=filemenu) # add_cascade creates a new hierarchical menu by associating a given menu to a parent menu
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Basics", command=help_me)
helpmenu.add_command(label='About', command=about)
menubar.add_cascade(label="Help", menu=helpmenu)



create_save_lab = Label(root,text='Create Save:' )

#create_save_lab.place(x=cr_save_p[0],y=cr_save_p[1])
create_save_lab.grid(row=0, column=0, padx=(80,10), pady=(0,260))

cr_save_ent = Entry(root,borderwidth=5)
#cr_save_ent.place(x=sv_ent_p[0],y=sv_ent_p[1])
cr_save_ent.grid(row=0, column=1, pady=(0,260))

but_go = Button(root, text='Done', borderwidth=5, command=create_save)
#but_go.place(x=but_go_p[0],y=but_go_p[1])
but_go.grid(row=0,column=2, padx=(10,0), pady=(0,260))

lb = Listbox(root, borderwidth=3, width=25, height=16)
bolded = FNT.Font(weight='bold') # will use the default font
lb.config(font=bolded)

#lb.place(x=lb_p[0],y=lb_p[1])
lb.grid(row=0, column=3, padx=(110,0), pady=(30,0))


#-----------------------------------------------------------
# right click popup menu in listbox

def do_popup(event):
	try:
		rt_click_menu.tk_popup(event.x_root, event.y_root) # Grab x,y position of mouse cursor
	finally:
		rt_click_menu.grab_release()

def open_notes():
    name = fetch_listbox_entry()[0]
    if len(name) < 1:
        popup('Select a save slot first.')
        return
    cmd = f'notepad {savedir}{name}\\notes.txt'#.format(savedir)
    out = run_command(cmd)


rt_click_menu = Menu(lb, tearoff = 0)
rt_click_menu.add_command(label ="Edit Notes", command=open_notes)

lb.bind("<Button-3>", do_popup) # button 3 is right click, so when right clicking inside listbox, do_popup is executed at cursor position



load_listbox() # populates listbox with saves on runtime

but_load_save = Button(root, text='Load Save', borderwidth=5, command=load_save_from_lb)#.place(x=but_load_p[0], y=but_load_p[1])
but_delete_save = Button(root, text='Delete Save', borderwidth=5, command=delete_save)#.place(x=but_del_p[0], y=but_del_p[1])

but_load_save.grid(row=3, column=3, pady=(12,0))
but_delete_save.grid(row=3, column=3, padx=(215,0), pady=(12,0))


root.mainloop()
