# AutoAFK

Automated bot for AFK Arena game. Handles daily activities, arena battles, guild hunts, and more.

[![Support on Ko-fi](https://img.shields.io/badge/Support%20on-Ko--fi-FF5E5B?logo=ko-fi&logoColor=white)](https://ko-fi.com/afksupporter)

## Features

- ✅ Daily activities automation (26 activities)
- ✅ Arena battles (Arena of Heroes, Heroes of Esperia)
- ✅ Guild hunts and activities
- ✅ Bounty board management
- ✅ Shop purchases
- ✅ Tower pushing
- ✅ Labyrinth runs
- ✅ Campaign progression
- ✅ Summon management
- ✅ Auto-update system
- ✅ Headless mode support

## Quick Start

### 1. Download

Download the latest `AutoAFK.zip` from [Releases](https://github.com/Hammanek/AutoAFK/releases/latest)

### 2. Extract

Extract the entire folder to your desired location.

### 3. Configure

Rename `settings.ini.example` to `settings.ini` and edit the settings you want to enable/disable.

### 4. Run

Double-click `AutoAFK.exe`

## Requirements

- Windows 10/11 (64-bit)
- Android emulator or device with ADB enabled
- ADB is included in the release package
- No Python required (fully compiled)

## How do I run it?
Configure your Android emulator so that:
* ADB is enabled
* Resolution is 1920x1080
* DPI is 240
* AFK's language is set to English

## Configuration

Edit `settings.ini`:

### Daily Activities
```ini
[DAILIES]
collectrewards = True       # Collect AFK rewards
collectmail = True          # Collect mail
fastrewards = 0             # Fast rewards count (0 = disabled)
companionpoints = True      # Collect companion points
fountainoftime = True       # Use Fountain of Time
kingstower = True           # Attempt King's Tower
collectinn = True           # Collect from Inn
guildhunt = True            # Do guild hunts
storepurchases = True       # Make shop purchases
twistedrealm = True         # Do Twisted Realm
collectquests = True        # Collect quest rewards
runlab = True               # Run Labyrinth
levelup = True              # Auto level up heroes
summonhero = False          # Auto summon heroes
```

### Arena
```ini
[ARENA]
battlearena = True          # Battle in Arena of Heroes
arenabattles = 5            # Number of battles
arenaopponent = 1           # Opponent selection (1-4)
tscollect = True            # Collect Temporal Rift rewards
gladiatorcollect = True     # Collect Gladiator Arena rewards
```

### Bounties
```ini
[BOUNTIES]
dispatchsolobounties = True # Dispatch solo bounties
dispatchteambounties = True # Dispatch team bounties
dispatchdust = True         # Accept dust bounties
dispatchdiamonds = False    # Accept diamond bounties
dispatchshards = True       # Accept shard bounties
refreshes = 0               # Number of refreshes
remaining = 2               # Minimum remaining slots
```

### Shop
```ini
[SHOP]
arcanestaffs = True         # Buy Arcane Staffs
timegazer = True            # Buy Timegazer cards
dust_gold = True            # Buy dust with gold
shards_gold = True          # Buy shards with gold
poe = True                  # Buy from PoE shop
quick = True                # Quick purchase mode
```

### Events
```ini
[EVENTS]
fightoffates = False        # Do Fight of Fates
battleofblood = False       # Do Battle of Blood
circustour = False          # Do Circus Tour
heroesofesperia = False     # Do Heroes of Esperia
```

### Advanced
```ini
[ADVANCED]
port = 0                    # ADB port (0 = auto)
loadingmuliplier = 1.0      # Speed multiplier (1.0 = normal)
server = 0                  # Server selection
debug = False               # Debug mode
autoupdate = True           # Auto-update on startup
emulatorpath = C:\path\to\emulator.exe  # Emulator path for restart
```

## Headless Mode

The bot supports running without GUI for automation and scheduling.

### Daily Activities

Run all configured daily activities:
```batch
AutoAFK.exe --dailies
```

Or use the provided script:
```batch
start_dailies.bat
```

### Tower Pushing

Push all towers automatically:
```batch
AutoAFK.exe --autotower
```

Push a specific tower:
```batch
AutoAFK.exe --tower c    # Celestial Tower
```

Available tower codes:
- `kt` - King's Tower
- `lb` - Lightbearer Tower
- `m` - Mauler Tower
- `w` - Wilder Tower
- `gb` - Graveborn Tower
- `c` - Celestial Tower
- `h` - Hypogean Tower

### Scheduling with Task Scheduler

You can schedule the bot to run automatically using Windows Task Scheduler:

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 8:00 AM)
4. Action: Start a program
5. Program: `C:\path\to\AutoAFK.exe`
6. Arguments: `--dailies`
7. Save and test

## Updating

### Automatic Check

The bot checks for updates on startup and shows a notification if available.

### Manual Update

Run:
```batch
update.bat
```

The updater will:
1. Download the latest version
2. Backup your settings
3. Install the update
4. Restart the bot automatically

Note: Updater is fully compiled - no Python installation needed!

### Auto-Update

Enable in `settings.ini`:
```ini
[ADVANCED]
autoupdate = True
```

The bot will automatically update and restart when a new version is available.

## Troubleshooting

### Bot doesn't start

1. Check if ADB is working: `adb devices`
2. Check if device is connected
3. Check `settings.ini` configuration
4. Check logs in `logs/` folder

### ADB not found

ADB is included in the release package. If you have issues:
1. Make sure `adb.exe` and `AdbWinApi.dll` are in the same folder as `AutoAFK.exe`
2. Try restarting the emulator
3. Check if Windows Defender is blocking ADB

### Device not found

1. Run `adb devices` in command prompt to see connected devices
2. Make sure USB debugging is enabled (for physical devices)
3. Make sure ADB is enabled in emulator settings
4. Try restarting ADB: `adb kill-server` then `adb start-server`
5. If using emulator, set correct port in `settings.ini` under `[ADVANCED]` section:
   ```ini
   port = 5555  # or your emulator's port
   ```

### Activities not working

1. Check if game is running
2. Check if game is at campaign screen
3. Check image recognition settings
4. Check debug screenshots in `debug/` folder

### Update failed

1. Download manually from [Releases](https://github.com/Hammanek/AutoAFK/releases/latest)
2. Extract and replace all files except `settings.ini`
3. Run `AutoAFK.exe`

Note: Updater is fully compiled, no Python needed!

## Command-Line Arguments

### GUI Mode (default)
```batch
AutoAFK.exe
```

### Headless Modes

Run daily activities without GUI:
```batch
AutoAFK.exe --dailies
# or
start_dailies.bat
```

Push all towers automatically:
```batch
AutoAFK.exe --autotower
```

Push specific tower:
```batch
AutoAFK.exe --tower kt     # King's Tower
AutoAFK.exe --tower lb     # Lightbearer Tower
AutoAFK.exe --tower m      # Mauler Tower
AutoAFK.exe --tower w      # Wilder Tower
AutoAFK.exe --tower gb     # Graveborn Tower
AutoAFK.exe --tower c      # Celestial Tower
AutoAFK.exe --tower h      # Hypogean Tower
```

### All Arguments

```
-c, --config FILE       Use custom config file (default: settings.ini)
-d, --dailies           Run dailies without GUI
-at, --autotower        Push all towers automatically
-t, --tower NAME        Push specific tower (kt, lb, m, w, gb, c, h)
-l, --logging           Enable file logging
```

### Examples

```batch
# Run dailies with custom config
AutoAFK.exe --dailies --config my_settings.ini

# Push Celestial Tower with logging
AutoAFK.exe --tower c --logging

# Push all towers
AutoAFK.exe --autotower
```

## Support

- Report issues: [GitHub Issues](https://github.com/Hammanek/AutoAFK/issues)
- Support development: [Ko-fi](https://ko-fi.com/afksupporter) ☕

If you find this bot helpful, consider supporting its development!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/afksupporter)

## Disclaimer

This bot is for educational purposes only. Use at your own risk. The authors are not responsible for any consequences of using this bot.
