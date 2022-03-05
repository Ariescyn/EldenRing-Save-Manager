# EldenRing-Save-Manager
GUI app written entirely in Python.


When drop trading with a friend:
  1. click file > save backup
  2. Go ingame, drop trade items to friend, exit game to main menu (or you can quit the game, up to you).
  3. click file > restore backup
  4. Done! Now your friend will have all of your items and you will still have all the items you gave him.


Creating save slots to easily store and load various builds before RESPEC, etc.
  
  - When creating a save slot, enter a name for the save and click 'Done'. It will then appear in the list box.
  - This will copy the contents of your appdata/roaming/EldenRing folder and back it up for easy retrieval.
  - Simply select the save slot you want to load into the game and click 'Load Save'.
  - To delete a save slot, select the slot and click 'Delete Save'.
  - Right-click on a save slot to edit notes. Notepad will open and allow you to enter details related to the save, like rune count, levels etc.




This is my first GUI app and i would love suggestions/advice! Email me at scyntacks94@gmail.com

The exe was compiled with pyinstaller and windows defender will most likely report it as a trojan. If anyone has a fix to this, please let me know.

The position of some GUI elements may be slightly off depending on your windows personalization setup. This is because i placed the elements with pixels and did not use the tkinter grid system. I will update it in the near future.
I can easily modify this program to work with dark souls 3 or other games. Just let me know.

Icon used from https://www.deviantart.com/abdelrahman18/art/Elden-Ring-Icon-877626671


![image](https://user-images.githubusercontent.com/68882322/156894674-4511043f-f643-4c64-abb2-cbfe0217b454.png)
