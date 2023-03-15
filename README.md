# AutoAFK
AutoAFK is a proof of concept Python based tool to automate Bluestacks games via ADB using Python and OpenCV. The bot supports image recognition with fuzzy matching, as well as pixel recognition to automate actions. All actions are done through ADB which means the window does not need to be in focus and you can continue to use your computer as normal while it runs.

While the bot is designed for AFK Arena the core logic will work for anything rendered in Bluestacks.

![image](https://user-images.githubusercontent.com/46250387/224131542-d555461c-3869-498c-a134-82b31cb8b0e6.png)


Issues/Comments/Suggestions? [Join the Discord server!](https://discord.gg/pfU7UB5A)

# What does it do?
The current Beta version will run the minimum in order to complete the dailies quests:
* Launch Game
* Collect AFK rewards twice
* Collect mail if there is a notification !
* Send/Recieve companion points if there is a notification !
* Collect Fast Rewards if available (The amount of times can be configured)
* Load and exit a campaign battle
* Collect and optionally dispatch bounty quests
* Load and battle in the Arena of Heroes (Amount of times configurable)
* Load and exit a tower battle
* Collect daily gifts from the inn
* Auto battle available Guild Hunts
* Collect available daily and weekly quest chests
* Clear Merchant menu free gifts & !'s
* Make daily store purchases

# Road map
The following features will be added soon(tm)
* switch servers for alts
* check Daily Quest Status to see if we need to run all tasks
* collect Fountain Of Time
* Run Fight of Fates / Battle of Blood
* Docmentation on how to full automate luanching, loading and running the script for running accounts with no oversight
* Discord notification on success/failure

# How do I run it?
Make sure that your Bluestacks is running in 1920x1080 and 240DPI with ADB enabled in settings, then download the latest release and run AutoAFK.exe.

# I'm having an issue
Note that the bot is currently in Beta and stability is still being worked into the functions. If you are receiving ADB errors you may need to manually connect your device using `./adb.exe connect localhost:xxxx` where xxxx is the port listed in Bluestacks ADB settings. If you still having issues create an issue here or ask on the Discord server.