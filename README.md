# EldenRing-Save-Manager
GUI app written entirely in Python.

## Usage
#### Windows
[Download Latest Release](https://github.com/Ariescyn/EldenRing-Save-Manager/releases/latest)

#### Linux / Proton / SteamDeck

Dependencies
```
python3 -m pip install Pillow tk requests
```
Fedora/DNF for 'ImageTk' from 'PIL'
```
sudo dnf install python3-pillow-tk.x86_64 python3-pillow.x86_64 
```
Run
```
python3 SaveManager.py
```

Pyinstaller
```
pyinstaller --onefile --windowed --icon=.\data\icon.ico .\SaveManager.py .\hexedit.py .\stat_progression.py .\itemdata.py .\os_layer.py
```

## Features:
- Edit item quantities
- Edit character stats
- Copy characters between save files
- Duplicate characters within the same save file
- rename characters in-game name
- automatically patch downloaded save files with your own Steam ID
- Fix corrupt save files by recalculating checksum values
- Create save and load backups 
- Create save slots for various builds before respec etc. 
- Edit notes attached to each save slot
- Update to the latest release with included updater
- Force quit EldenRing when the game locks up and even task manager wont end the process

You can [Donate](https://www.google.com) via PayPal if you want support me
![main](https://user-images.githubusercontent.com/68882322/171963417-fe931395-e0b5-4680-bebd-81ebc564bea3.jpg)

![save-editor](https://user-images.githubusercontent.com/68882322/163687699-334cf9d6-f956-4509-bebc-e549fe39fd3e.jpg)

![inventory editor](https://user-images.githubusercontent.com/68882322/164989037-1cc1256d-b833-478f-a7eb-84d4974d23f8.jpg)

![v1 40](https://user-images.githubusercontent.com/68882322/161843003-dfefa2fb-ca14-4401-970a-2875bb74c943.jpg)



Icon used from https://www.deviantart.com/abdelrahman18/art/Elden-Ring-Icon-877626671
You can use this icon to replace the horrible default Elden Ring game icon.



Walkthrough: https://youtu.be/RZIP0kYjvZM

