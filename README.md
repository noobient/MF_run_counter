# MF Run Counter
Run counter for Diablo 2, created by oskros#1889 with ongoing development since August 2019.

You can find a video where the application is described in detail here: 
https://youtu.be/IV3H3pt6YDE


![GUI](https://github.com/oskros/MF_run_counter/blob/master/media/UI_showcase2.png?raw=true)

## How to use
NB: Working on Windows 7 and Windows 10 (I have not tested on any other OS, but probably it wouldn't work)
1) To run on your computer, go to releases (https://github.com/oskros/MF_run_counter/releases) and download the .exe file from the latest release. 
2) Place the .exe file in your preferred folder (don't place it in a folder that requires admin rights to write to)
3) You might be prompted by Windows not recognizing the application publisher (I am not going to pay 100$ a year for Windows to recognize me lol). Simply click "more info" and then "Run anyway" when Windows asks. See pictures below
    
    ![winblock1](https://github.com/oskros/MF_run_counter/blob/master/media/Unrecognized1.png?raw=true)
    ![winblock2](https://github.com/oskros/MF_run_counter/blob/master/media/Unrecognized2.png?raw=true)
4) You can make the application trusted by following the steps suggested here: https://www.windowscentral.com/how-disable-smartscreen-trusted-app-windows-10
5) The first time you run the .exe file, a config file is created in the same directory as the .exe, named "mf_config.ini", which can be edited in Notepad. While you can edit settings directly in the config file, I would recommend doing it from within the application. At first run, there is also a "Profiles" folder created, which stores save files for each of your created profiles.

## Features
### Automode
You can active automode in **Options -> Automode**. There are two types of automode
1) **Advanced:** Uses memory reading of the D2 "*Game.exe*" process to read from your client when you are in-game. When you enter a game, it will start a new run, and when you exit a game it will stop the run - Only recommended on single player, as it could be deemed cheating on multiplayer servers.    
Advanced automode is patch specific, and is currently supported for 1.13c, 1.13d, 1.14b, 1.14c and 1.14d. It also works together with D2SE.

2) **Simple:** Monitors the "*latest change time*" of your character save file. Your character is saved every time you exit a game, and thus a new run can be started - Unfortunately, there is no way to stop a run with this method and also it has two drawbacks:  
*2.a)* The game autosaves every 5 minutes, thus you cannot have runs longer than 5 min.  
*2.b)* The game autosaves every time you die  
To set-up automode, enter the game path to your character save folder and click 'Apply'. Also make sure the character name specified in your profile is exactly the same as your in-game name, otherwise the automode will fail to start.

### System wide hotkeys
You are able to customize hotkeys for each of the commands in the application. The hotkeys are system wide, so you do not need to place focus on the application to use them. However, this means that while the application is open, it overrides any other program using this specific hotkey.
It is possible to disable a command from having a hotkey by choosing "NO_BIND"  
There are 2 hidden hotkeys: *CTRL+SHIFT+PgDn* and *CTRL+SHIFT+PgUp* for switching between tabs in the app (eg. if you wanna confirm the drop you just added is in fact saved)

### Manual run counting (Optional)
Start a new run by using the assigned hotkey (default *ALT+Q*). In case a run is already active, this button will end it and start a new run.
End the run by using the assigned hotkey (default *ALT+W*).
In case of mistakes, the previous run can be deleted using the assigned hotkey (default *CTRL+DEL*)
If the user desires, the current run timer can be reset using the assigned hotkey (default *ALT+R*).

### Drop logging
You add a drop to the current run (or previous run if no run is currently active) by using the assigned hotkey (default *ALT+A*). It will then be listed in the "Drops" list for the run where it was found.
When adding a drop, the application will try and autocomplete the name of the drop using a full library of all available sets, uniques and runes.
In case a drop was added by mistake, it can be deleted by highlighting it and clicking the "Delete selection" button under the "Drops" tab, or by pressing the Delete button on your keyboard while the drop is highlighted (this hotkey is not system wide).

### Profiles
In the profile tab it is possible to create a separate run profile for each character and run type (eg. Chaos, Cows, Meph, etc.). In the profile tab you can view each saved session in the archive browser, where it is also possible to save the results to a .txt file or copy to clipboard. Profile data is saved as a .json under the "Profiles" folder that is created the first time you run the program.

### Grail logging
In the grail tab you can track your progress in completing the d2 holy grail of collecting all items (and runes). Every time you add a new item that hasn't been found before, you will get a pop-up asking if you wish to add it to your grail! Then it will appear in your found items with a "(\*)" in front of the name, to indicate it was a grailer.  
You can sync the grail progress made in the run counter with d2-holy-grail.herokuapp.com - Both in terms of syncing the run counter with the webpage, and also upload any progress back to the webpage again!  
In order to view your grail progress there is both a "Grail controller" view, which is similar to the one found on herokuapp, but also an "Item table" view, where you see all items in a table with tons of information about each item.  
You can also sync your local grail with already found items. Unfortunately, it is not possible to sync with any items added in your profiles prior to MF Run Counter v.1.2.0, sorry!

### Session timer
The session timer will run while Diablo is open. It will pause when Diablo is closed.

### Pausing
In case you need to take a break from the computer, the counter can be paused by using the assigned hotkey (default *CTRL+Space*). This will pause both the run timer (if a run is active) and the session timer.

### Saving and exporting results
The current session is saved automatically every 30 seconds (to prevent data loss in case of crashes) and also saved automatically when you close the app. You can click the "Archive session" button to reset the session and archive the session results to the profile. In the archive browser, it is possible to save a session or the full profile history to a .txt or .csv file, or copy to clipboard - Example of the .txt file is included below.
                  
        *Statistics*
        Character name: Tsssch
        Run type:       Andy
        Game mode:      Single Player
    
        Total session time:   00:24:20:0
        Total run time:       00:23:10:0
        Average run time:     00:00:34:7
        Fastest run time:     00:00:23:1
        Number of runs:       40
        Time spent in runs:   95.21%
    
        *Collected drops*
        Run  2 --- Atma's Scarab
        Run  6 --- Raven Frost 151/18
    
        *Run times*
        Run  1: 00:00:23:1
        Run  2: 00:00:42:0 --- Atma's Scarab
        Run  3: 00:00:25:0
        Run  4: 00:00:32:1
        Run  5: 00:00:32:3
        Run  6: 00:00:26:7 --- Raven Frost 151/18
                  
### Dragging
Window can be dragged on the Diablo 2 banner. Window position is saved in the config file, such that it opens where you closed it.

### Automatic check for updates
The program automatically checks if a new version is available on start-up, providing a link to the release pages where you can download it. This features can be disabled under *Options->General*

### Color themes
Three different themes for the application have been created, which the user can choose between under Options 
    ![winblock1](https://github.com/oskros/MF_run_counter/blob/master/media/color_themes.png?raw=true)

### Extra options
In the Options tab you can turn on or off specific features in the application, and change the colour theme


### Sundering charms

If you try to use an existing `grail.json`, first you need to edit the file for sundering charms to work.

Close the application, then open `grail.json`, and find the following block:

<details>

```json
  {
    "Item": "Hellfire Torch",
    "Base Item": "Large Charm",
    "Item Group 0": "Unique Other",
    "Item Group 1": "Charms",
    "Item Group 2": "All",
    "Item Class": "Charm",
    "Quality": "",
    "Rarity": "Unique",
    "Class restriction": "",
    "TC": "1",
    "QLVL": "110",
    "Roll rarity": "",
    "Roll chance": "",
    "Drop Andariel": "FALSE",
    "Drop Duriel": "FALSE",
    "Drop Mephisto": "FALSE",
    "Drop Diablo": "FALSE",
    "Drop Pindleskin": "FALSE",
    "Found": false
  },
```

</details>

After this, insert the following:

<details>

```json
  {
    "Item": "Black Cleft",
    "Base Item": "Grand Charm",
    "Item Group 0": "Unique Other",
    "Item Group 1": "Charms",
    "Item Group 2": "All",
    "Item Class": "Charm",
    "Quality": "",
    "Rarity": "Unique",
    "Class restriction": "",
    "TC": "1",
    "QLVL": "70",
    "Roll rarity": "",
    "Roll chance": "",
    "Drop Andariel": "TRUE",
    "Drop Duriel": "TRUE",
    "Drop Mephisto": "TRUE",
    "Drop Diablo": "TRUE",
    "Drop Pindleskin": "TRUE",
    "Found": false
  },
  {
    "Item": "Bone Break",
    "Base Item": "Grand Charm",
    "Item Group 0": "Unique Other",
    "Item Group 1": "Charms",
    "Item Group 2": "All",
    "Item Class": "Charm",
    "Quality": "",
    "Rarity": "Unique",
    "Class restriction": "",
    "TC": "1",
    "QLVL": "70",
    "Roll rarity": "",
    "Roll chance": "",
    "Drop Andariel": "TRUE",
    "Drop Duriel": "TRUE",
    "Drop Mephisto": "TRUE",
    "Drop Diablo": "TRUE",
    "Drop Pindleskin": "TRUE",
    "Found": false
  },
  {
    "Item": "Cold Rupture",
    "Base Item": "Grand Charm",
    "Item Group 0": "Unique Other",
    "Item Group 1": "Charms",
    "Item Group 2": "All",
    "Item Class": "Charm",
    "Quality": "",
    "Rarity": "Unique",
    "Class restriction": "",
    "TC": "1",
    "QLVL": "70",
    "Roll rarity": "",
    "Roll chance": "",
    "Drop Andariel": "TRUE",
    "Drop Duriel": "TRUE",
    "Drop Mephisto": "TRUE",
    "Drop Diablo": "TRUE",
    "Drop Pindleskin": "TRUE",
    "Found": false
  },
  {
    "Item": "Crack of the Heavens",
    "Base Item": "Grand Charm",
    "Item Group 0": "Unique Other",
    "Item Group 1": "Charms",
    "Item Group 2": "All",
    "Item Class": "Charm",
    "Quality": "",
    "Rarity": "Unique",
    "Class restriction": "",
    "TC": "1",
    "QLVL": "70",
    "Roll rarity": "",
    "Roll chance": "",
    "Drop Andariel": "TRUE",
    "Drop Duriel": "TRUE",
    "Drop Mephisto": "TRUE",
    "Drop Diablo": "TRUE",
    "Drop Pindleskin": "TRUE",
    "Found": false
  },
  {
    "Item": "Flame Rift",
    "Base Item": "Grand Charm",
    "Item Group 0": "Unique Other",
    "Item Group 1": "Charms",
    "Item Group 2": "All",
    "Item Class": "Charm",
    "Quality": "",
    "Rarity": "Unique",
    "Class restriction": "",
    "TC": "1",
    "QLVL": "70",
    "Roll rarity": "",
    "Roll chance": "",
    "Drop Andariel": "TRUE",
    "Drop Duriel": "TRUE",
    "Drop Mephisto": "TRUE",
    "Drop Diablo": "TRUE",
    "Drop Pindleskin": "TRUE",
    "Found": false
  },
  {
    "Item": "Rotting Fissure",
    "Base Item": "Grand Charm",
    "Item Group 0": "Unique Other",
    "Item Group 1": "Charms",
    "Item Group 2": "All",
    "Item Class": "Charm",
    "Quality": "",
    "Rarity": "Unique",
    "Class restriction": "",
    "TC": "1",
    "QLVL": "70",
    "Roll rarity": "",
    "Roll chance": "",
    "Drop Andariel": "TRUE",
    "Drop Duriel": "TRUE",
    "Drop Mephisto": "TRUE",
    "Drop Diablo": "TRUE",
    "Drop Pindleskin": "TRUE",
    "Found": false
  },
```

</details>

Save your `grail.json`, and start the app again. Open _Grail / Grail controller_, navigate to _Unique Other_, check one of the sundering charms, then close and re-open the Grail controller again. If you've done everything right, the checked charm should remain checked:

![sundering charms](https://github.com/noobient/MF_run_counter/blob/master/media/sundering.png?raw=true)

You have to do this only once, and it should work afterwards.

## Building

Download and install the latest 64-bit version of [Python](https://www.python.org/). Use the following install options:

<details>

![python install](https://github.com/noobient/MF_run_counter/blob/master/media/python01.png?raw=true)
![python install](https://github.com/noobient/MF_run_counter/blob/master/media/python02.png?raw=true)
![python install](https://github.com/noobient/MF_run_counter/blob/master/media/python03.png?raw=true)

</details>

If you want compression, download the latest 64-bit release of [UPX](https://github.com/upx/upx/releases/latest), then add it to PATH.

Install the required Python packages:

```
pip install --upgrade --force-reinstall -r requirements.txt
```

Then you can build the app:

```
cd build_exe
./onefile_exe.bat
```
