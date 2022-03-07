# EldenRing-Save-Manager
GUI app written entirely in Python.


Quick Backup and Restore when you dont need to make a save slot:
  
  1. Make sure you are at the main menu (after bandai namco screen and before you login to elden ring servers) or exit the game.
  2. click file > save backup.
  3. Load into the game and do as you wish.
  4. Repeat step 1.
  4. click file > restore backup.


Creating save slots to easily store and load various builds before RESPEC, etc.
  
  - When creating a save slot, enter a name for the save and click 'Done'. It will then appear in the list box.
  - This will copy the contents of your appdata/roaming/EldenRing folder and save a copy to data/save-files up for easy retrieval.
  - Simply select the save slot you want to load into the game and click 'Load Save'.
  - To delete a save slot, select the slot and click 'Delete Save'.
  - Right-click on a save slot to edit notes. Notepad will open and allow you to enter details related to the save, like rune count, levels etc.
  - Right-click on a save slot to rename a save file. Enter a new name and press Done. NOTE: Some characters are forbidden in save slot names. example: "~'{};:./\,:*?<>|-!@#$%^&()+
  - Right-click on a save slot to update a save slot. This will copy the contents of your most current save file in appdata/roaming/EldenRing and overwrite the      selected save slot.



This is my first GUI app and have been using it since DS3. Figured i would share it with all the issues of people losing their progress. i would love suggestions/advice! Email me at scyntacks94@gmail.com


I can easily modify this program to work with dark souls 3 or other games. Just let me know.

Icon used from https://www.deviantart.com/abdelrahman18/art/Elden-Ring-Icon-877626671
You can use this icon to replace the horrible default Elden Ring game icon.

NOTE: Never use someone elses save file or you'll get banned. The exe was compiled with pyinstaller and windows defender might report it as untrusted. This is a common issue with pyinstaller. Just click more info > run anyway. I am working to fix this by compiling it differently but it has been a real PAIN. Would appreciate advice.


![1 2](https://user-images.githubusercontent.com/68882322/157093926-c4476981-3a80-42a0-a7f0-717486706347.jpg)

Video of the app in action here: https://youtu.be/CO9h2gy9Qh8


Build from source:
  - pip install pillow pyinstaller
  - cd into folder with saveManager.py and data folder
    - make sure you have the data folder from the release in the same directory as the script
  - pyinstaller --onefile --icon=.\data\icon.ico --windowed .\SaveManager.py
