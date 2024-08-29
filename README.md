# AutoAFK
AutoAFK is a tool to automate android games via ADB using Python, Pyscreeze and OpenCV. The bot supports image recognition with fuzzy matching, as well as single pixel recognition to automate actions. All actions are done through ADB which means the window does not need to be in focus and you can continue to use your computer as normal while it runs.

While the bot is designed for AFK Arena the core logic will work for anything rendered in emulator.

![image](https://github.com/Fortigate/AutoAFK/assets/46250387/9879407b-340a-485b-90e3-068e395dca34)


Issues/Comments/Suggestions? [Join the Discord server!](https://dsc.gg/floofpire)

# What does it do?
In the current release you can select from the following tasks:

## Dailies Tasks
* Collect AFK rewards twice
* Collect mail if there is a notification
* Send/Recieve companion points if there is a notification, and optionally send mercs
* Collect Fast Rewards if available (The amount of times can be configured)
* Load and exit a campaign battle
* Collect and optionally dispatch bounty quests
* Load and battle in the Arena of Heroes (Amount of times configurable)
* Collect Gladiator Coins
* Collect Fountain of Time rewards
* Load and exit a tower battle
* Collect daily gifts from the inn
* Auto battle available Guild Hunts
* Battle Twisted Realm
* Collect available daily and weekly quest chests
* Clear Merchant menu free gifts & !'s
* Make customizable daily store purchases

## Arena Ticket spending
* Run a configurable number of Arena Tickets
 
## Auto push
* Auto load configured formation and push towers/campaign


# How do I run it?
Configure your MuMu Player client so that:
* ADB is enabled
* Resolution is 1920x1080
* DPI is 240
* AFK's language is set to English

Then download the latest [release](https://github.com/Hammanek/AutoAFK/releases/), unzip and run AutoAFK.exe.

# Road map
The following features will be added soon(tm)
* Automatically Run Lab
* Push Temporal Rift
* Discord notification on success/failure
* Run Fight of Fates / Battle of Blood
* Purchase selected Dimensional Gear
* Documentation on how to full automate launching, loading and running the script for managing accounts via cron

# AFK Journey automation integration
Download bot here - https://github.com/Fortigate/AutoAFK2
Use enable_afkjourney and afkjourney_cmd properties in settings.ini, see example use in files here.

# Telegram integration
Contact BotFather on Telegram, create your bot, get token and chat id.
Uses chat_id and token properties in settings.ini.

# I'm having an issue
Note that the bot is currently in Beta and stability is still being worked into the functions. If you having issues please create an issue here or ask on the Discord server.
