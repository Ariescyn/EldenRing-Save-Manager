# EldenRing-Save-Manager
GUI app written entirely in Python.


When making a quick save or backup:
  1. Exit game or go to main menu (just dont sign in after the Bandai Namco screen)
  2. alt-tab, click file > save backup
  3. Make sure the Game is exited or at the main menu (dont sign in) and alt-tab, file > restore backup


Creating save slots to easily store and load various builds before RESPEC, etc.
  
  - When creating a save slot, enter a name for the save and click 'Done'. It will then appear in the list box.
  - This will copy the contents of your appdata/roaming/EldenRing folder and back it up for easy retrieval.
  - Simply select the save slot you want to load into the game and click 'Load Save'.
  - To delete a save slot, select the slot and click 'Delete Save'.
  - Right-click on a save slot to edit notes. Notepad will open and allow you to enter details related to the save, like rune count, levels etc.




This is my first GUI app and have been using it since DS3. Figured i would share it with all the issues of people losing their progress. i would love suggestions/advice! Email me at scyntacks94@gmail.com


I can easily modify this program to work with dark souls 3 or other games. Just let me know.

Icon used from https://www.deviantart.com/abdelrahman18/art/Elden-Ring-Icon-877626671
You can use this icon to replace the horrible default Elden Ring game icon.

NOTE: Never use someone elses save file or you'll get banned. The exe was compiled with pyinstaller and windows defender might report it as untrusted. This is a common issue with pyinstaller. Just click more info > run anyway. I am working to fix this by compiling it differently but it has been a real PAIN. Would appreciate advice.


![v1 1-two](https://user-images.githubusercontent.com/68882322/156934436-a416d6a1-501b-4cc9-8a31-60d07d50b10a.png)

Video of the app in action here: https://youtu.be/CO9h2gy9Qh8


Build from source:
  - pip install pillow pyinstaller
  - cd into folder with saveManager.py and data folder
    - make sure you have the data folder from the release in the same directory as the script
  - pyinstaller --onefile --icon=.\data\icon.ico --windowed .\SaveManager.py
