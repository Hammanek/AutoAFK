# Imports
import io
import random
import os
import numpy as np
from ppadb.client import Client
from AutoAFK import settings, args
from pyscreeze import locate
from subprocess import Popen, PIPE
import time, datetime, os, configparser, sys
from PIL import Image
from shutil import which
from platform import system
import scrcpy
import psutil
import win32gui
import win32con
import ctypes
from telegram import *

# Configs/settings
config = configparser.ConfigParser()
config.read(settings) # load settings
cwd = os.path.dirname(__file__) # variable for current directory of AutoAFK.exe
os.system('color')  # So colourful text works
connected = False
connect_counter = 1
max_fps = 5
bitrate = 8000000

# Start PPADB
adb = Client(host='127.0.0.1', port=5037)

# Connects to the ADB device using PPADB, allowing us to send commands via Python
# Then connects scrcpy for screen reading
# On success we go through our startup checks to make sure we are starting from the same point each time, and can recognise the template images
def connect_device():
    global device
    global connect_counter
    global connected  # So we don't reconnect with every new activity in the same session
    global config
    was_running = False
    config.read(settings) # Load settings

    # Check if emulator process is already running and try to run it if not
    if config.has_option('ADVANCED', 'emulatorpath') and not is_process_running(config.get('ADVANCED', 'emulatorpath').rsplit('\\', 1)[-1]):
        if config.get('ADVANCED', 'emulatorpath'):
            # Check if the file exists
            if os.path.exists(config.get('ADVANCED', 'emulatorpath')):
                # Run the executable file
                printGreen('Starting emulator...')
                Popen(config.get('ADVANCED', 'emulatorpath'), shell=False)
                minimize_window()
                wait(3)
                minimize_window()
    else: 
        was_running = True

    printGreen('Attempting to connect..')

    if connected is True: # Skip if we've ran through and connected succesfully already this session
        waitUntilGameActive() # but still confirm we start from the right place
        return

    # Run through the various methods to find the ADB device of the emulator, and point PPADB to the found device
    device = configureADB()

    # PPADB can throw errors occasionally for no good reason, here we try and catch them and retry for stability
    while connect_counter <= 3:
        try:
            device.shell('echo Hello World!') # Arbitrary test command
        except Exception as e:
            if str(e) == 'ERROR: \'FAIL\' 000edevice offline':
                printError('PPADB Error: ' + str(e) + ', retrying ' + str(connect_counter) + '/3')
                printBlue('Device present, but connection failed, this is usually a temporary error')
            elif str(e) == '\'NoneType\' object has no attribute \'shell\'':
                printError('PPADB Error: ' + str(e) + ', retrying ' + str(connect_counter) + '/3')
                printBlue('This usually means the port is wrong as there is no device present')
            elif str(e) == 'ERROR: \'FAIL\' 0006closed':
                printError('PPADB Error: ' + str(e) + ', retrying ' + str(connect_counter) + '/3')
                printBlue('The selected port is not responding, is ADB enabled? Retrying..')
            else:
                printError('PPADB Error: ' + str(e) + ', retrying ' + str(connect_counter) + '/3')
            wait(3)
            connect_counter += 1
            if connect_counter <= 3:
                device = configureADB()
        else:
            if device is not None:
                connected = True
                if not was_running:
                    minimize_window()
            break

    # Break after 3 retries
    if connect_counter >= 3:
        printError('No ADB device found, often due to ADB errors. Please try manually connecting your client. \nDebug lines:')
        print('Available devices:')
        if device != '':
            for device in adb.devices():
                print('    ' + device.serial)
            print('Defined device')
            print('    ' + device.serial)
        sys.exit(1)

    if connected is True:
        printGreen('Device: ' + str(device.serial) + ' successfully connected!')

        scrcpyClient = scrcpy.Client(device=device.serial)
        scrcpyClient.max_fps = max_fps
        scrcpyClient.bitrate = bitrate
        scrcpyClient.start(daemon_threaded=True)
        setattr(device, 'srccpy',  scrcpyClient)

        if config.getboolean('ADVANCED', 'debug') is True:
            print('\nDevice: ' + device.serial)
            print('scrcpy device: ' + str(scrcpyClient))
            print('Resolution: ' + device.shell('wm size'))
            print('DPI: ' + device.shell('wm density'))
            #save_scrcpy_screenshot('debug')

        resolutionCheck(device) # Four start up checks, so we have an exact position/screen configuration to start with
        afkRunningCheck()
        waitUntilGameActive()
        expandMenus()

# This function manages the ADB connection to Bluestacks.
# First it restarts ADB then checks for a port in settings.ini, after that we check for existing connected ADB devices
# If neither are found we run portScan() to find the active port and connect using that
def configureADB():
    # Load any new values (ie port changed and saved) into memory
    config.read(settings)

    adbpath = os.path.join(cwd, 'adb.exe') # Locate adb.exe in working directory
    if system() != 'Windows' or not os.path.exists(adbpath):
        adbpath = which('adb') # If we're not on Windows or can't find adb.exe in the working directory we try and find it in the PATH

    # Restarting the ADB server solves 90% of issues with it
    if config.getboolean('ADVANCED', 'adbrestart') is True:
        Popen([adbpath, "kill-server"], stdout=PIPE).communicate()[0]
        Popen([adbpath, "start-server"], stdout=PIPE).communicate()[0]
    else:
        printWarning('ADB Restart disabled')

    # First we check settings for a valid port and try that
    if config.getint('ADVANCED', 'port') != 0:
        port = config.get('ADVANCED', 'port')
        if port == '':
            port == 0 # So we don't throw a NaN error if the field's blank
        if ':' in str(port):
            printError('Port entered includes the : symbol, it should only be the last 4 or 5 digits not the full IP:Port address. Exiting..')
            sys.exit(1)
        if int(port) == 5037:
            printError('Port 5037 has been entered, this is the port of the ADB connection service not the emulator, check BlueStacks Settings - Preferences to get the ADB port number')
            sys.exit(1)
        printWarning('Port ' + str(config.get('ADVANCED', 'port')) + ' found in settings.ini, using that')
        device = '127.0.0.1:' + str(config.get('ADVANCED', 'port'))
        Popen([adbpath, 'connect', device], stdout=PIPE).communicate()[0]
        adb_device = adb.device('127.0.0.1:' + str(config.get('ADVANCED', 'port')))
        return adb_device

    # Second we list adb devices and see if something is there already, it will take the first device which may not be what we want so settings.ini port takes priority
    adb_devices = adb.devices()
    for device in adb_devices:
        if device is not None:
            adb_device = adb.device(device.serial) # If we find any we return that and move on
            return adb_device

    # Last step is to find the port ourselves, this is Windows only as it runs a PowerShell command
    if system() == 'Windows':
        device = '127.0.0.1:' + str(portScan())
        Popen([adbpath, 'connect', device], stdout=PIPE).communicate()[0]
        adb_device = adb.device(device)
        return adb_device

    # If none of the above work we exit
    printError('No device found! Exiting..')
    sys.exit(1)

# This takes all Listening ports opened by HD-Player.exe and tries to connect to them with ADB
def portScan():
    adbpath = os.path.join(cwd, 'adb.exe') # Locate adb.exe in working directory
    if system() != 'Windows' or not os.path.exists(adbpath):
        adbpath = which('adb') # If we're not on Windows or can't find adb.exe in the working directory we try and find it in the PATH

    printWarning('No ADB devices found connected already, and no configured port in settings. Manually scanning for the port..')

    # Powershell command that returns all listening ports in use by HD-Player.exe
    ports = Popen(["powershell.exe", "Get-NetTCPConnection -State Listen | Where-Object OwningProcess -eq (Get-Process hd-player | Select-Object -ExpandProperty Id) | Select-Object -ExpandProperty LocalPort"], stdout=PIPE).communicate()[0]
    if len(ports.decode().splitlines()) > 0:
        printWarning(str(len(ports.decode().splitlines())) + ' ports found, trying them..')

        # Scan ports
        for port in ports.decode().splitlines(): # Split by linebreak
            port = int(port)
            if port % 2 != 0: # ADB will only use odd port numbers
                connectmessage = Popen([adbpath, 'connect', '127.0.0.1:' + str(port)], stdout=PIPE).communicate()[0]
                if connectmessage.decode().split(' ')[0] == 'failed':
                    printError(connectmessage.decode().rstrip())
                elif connectmessage.decode().split(' ')[0] == 'connected':
                    printGreen(connectmessage.decode().rstrip())
                    return port
    else:
        printError('No ports found!')

# Expands the left and right button menus
def expandMenus():
    while isVisible('buttons/downarrow', 0.8, suppress=True):
        click('buttons/downarrow', 0.8, retry=3)

# Checks if AFK Arena process is running, if not we launch it
def afkRunningCheck():
    if args['test']:
        # printError('AFK Arena Test Server is not running, launching..')
        device.shell('monkey -p  com.lilithgames.hgame.gp.id 1')
    elif not args['test']:
        # printError('AFK Arena is not running, launching..')
        device.shell('monkey -p com.lilithgame.hgame.gp 1')
    if config.getboolean('ADVANCED', 'debug') is True:
        print('Game check passed\n')

# Confirms that the game has loaded by checking for the campaign_selected button. We press a few buttons to navigate back if needed
# May also require a ClickXY over Campaign to clear Time Limited Deals that appear
def waitUntilGameActive():
    printWarning('Searching for Campaign screen..')
    loadingcounter = 0
    timeoutcounter = 0
    if args['dailies']:
        loaded = 3 # If we're running unattended we want to make real sure there's no delayed popups
    else:
        loaded = 1

    while loadingcounter < loaded:
        clickXY(420, 50) # Neutral location for closing reward pop ups etc, should never be an in game button here
        buttons = [os.path.join('buttons', 'campaign_unselected'), os.path.join('buttons', 'exitmenu_trial'), os.path.join('buttons', 'back')]
        for button in buttons:
            click(button, seconds=0, suppress=True)
        timeoutcounter += 1
        if isVisible('buttons/campaign_selected'):
            loadingcounter += 1
        if timeoutcounter > 60: # Long so patching etc doesn't lead to timeout
            printError('Timed out while loading!')
            sys.exit(1)
    printGreen('Game Loaded!')

# Checks we are running 1920x1080 (or 1080x1920 if we're in landscape mode) and 240 DPI.
def resolutionCheck(device):
    resolution_lines = device.shell('wm size').split('\n')
    physical_resolution = resolution_lines[0].split(' ')
    override_resolution = resolution_lines[1].split(' ')
    dpi_lines = device.shell('wm density').split('\n')
    dpi = dpi_lines[0].split(' ')

    if override_resolution[0] != '':
        if not str(override_resolution[2]).strip() == '1920x1080' and not str(override_resolution[2]).strip() == '1080x1920':
            printWarning('Unsupported Override Resolution! (' + str(override_resolution[2]).strip() + '). Please change your resolution to 1920x1080')
            printWarning('We will try and scale the image but non-16:9 formats will likely have issues with image detection')
    else:
        if not str(physical_resolution[2]).strip() == '1920x1080' and not str(physical_resolution[2]).strip() == '1080x1920':
            printWarning('Unsupported Physical Resolution! (' + str(physical_resolution[2]).strip() + '). Please change your resolution to 1920x1080')
            printWarning('We will try and scale the image but non-16:9 formats will likely have issues with image detection')

    if str(dpi[2]).strip() != '240':
        printError('Unsupported DPI! (' + str(dpi[2]).strip() + '). Please change your DPI to 240')
        printWarning('Continuining but this may cause errors with image detection')

    if config.getboolean('ADVANCED', 'debug') is True:
        print('Resolution check passed')

# Returns the last frame from scrcpy, if the resolution isn't 1080 we scale it but this will only work in 16:9 resolutions
def getFrame():
    im = Image.fromarray(device.srccpy.last_frame[:, :, ::-1])

    if not im.size == (1080, 1920) and not im.size == (1920, 1080):
        im = im.resize((1080, 1920))

    return im

# Saves screenshot locally
def save_scrcpy_screenshot(name):
    image = getFrame()
    # Convert image back to bytearray
    byteIO = io.BytesIO()
    image.save(byteIO, format='PNG')
    image = byteIO.getvalue()
    with open(name + '.png', 'wb') as f:
        f.write(image)

# Wait command, default 1 second
# Loading multiplier is defined in settings, it is a decimally notated % multiplier. E.G:
# 0.9 will run with 90% of the default wait times
# 2.0 will run with 200% of the default wait times
# This is handy for slower machines where we need to wait for sections/images to load
def wait(seconds=1):
    time.sleep(seconds * float(config.get('ADVANCED', 'loadingMuliplier')))

# Performs a swipe from X1/Y1 to X2/Y2 at the speed defined in duration
def swipe(x1, y1, x2, y2, duration=100, seconds=1):
    device.input_swipe(x1, y1, x2, y2, duration)
    wait(seconds)

# Returns True if the image is found, False if not
# Confidence value can be reduced for images with animations
# Retry for retrying image search
def isVisible(image, confidence=0.9, seconds=1, retry=1, click=False, region=(0, 0, 1080, 1920), xyshift=None, suppress=False):
    counter = 0
    screenshot = getFrame()
    search = Image.open(os.path.join(cwd, 'img', image + '.png'))
    res = locate(search, screenshot, grayscale=False, confidence=confidence, region=region)

    if res == None and retry != 1:
        while counter < retry:
            screenshot = getFrame()
            res = locate(search, screenshot, grayscale=False, confidence=confidence, region=region)
            if res != None:
                if click is True:
                    x, y, w, h = res
                    x_center = round(x + w / 2)
                    y_center = round(y + h / 2)
                    if xyshift is not None:
                        x_center += xyshift[0]
                        y_center += xyshift[1]                    
                    device.input_tap(x_center, y_center)
                wait(seconds)
                return True
            wait()
            counter = counter + 1
    elif res != None:
        if click is True:
            x, y, w, h = res
            x_center = round(x + w / 2)
            y_center = round(y + h / 2)
            device.input_tap(x_center, y_center)
        wait(seconds)
        return True
    else:
        if suppress is not True and config.getboolean('ADVANCED', 'debug'):
            printWarning('Image:' + image + ' not found on screen, saving screenshot.')
            if not os.path.exists('debug'):
                os.makedirs('debug')
            save_scrcpy_screenshot('debug/' + image.replace("/", "_").replace("\\", "_").replace(".png", "") + "_" + str(time.time()))
        wait(seconds)
        return False

# Clicks on the given XY coordinates
def clickXY(x, y, seconds=1, rs=None, xrandom_shift=0, yrandom_shift=0):
    if rs is not None:
        xrandom_shift = rs
        yrandom_shift = rs
    device.input_tap(x + random.randint(0, xrandom_shift), y + random.randint(0, yrandom_shift))
    wait(seconds)

# If the given image is found, it will click on the center of it, if not returns "No image found"
# Confidence is how sure we are we have the right image, for animated icons we can lower the value
# Seconds is time to wait after clicking the image
# Retry will try and find the image x number of times, useful for animated or covered buttons, or to make sure the button is not skipped
# Suppress will disable warnings, sometimes we don't need to know if a button isn't found
def click(image,confidence=0.9, seconds=1, retry=1, suppress=False, grayscale=False, region=(0, 0, 1080, 1920), xyshift=None):
    counter = 0
    screenshot = getFrame()

    if config.getboolean('ADVANCED', 'debug') is True:
        suppress = False

    search = Image.open(os.path.join(cwd, 'img', image + '.png'))
    result = locate(search, screenshot, grayscale=grayscale, confidence=confidence, region=region)
    if result == None and retry != 1:
        while counter < retry:
            screenshot = getFrame()
            result = locate(search, screenshot, grayscale=grayscale, confidence=confidence, region=region)
            if result != None:
                x, y, w, h = result
                x_center = round(x + w / 2)
                y_center = round(y + h / 2)
                if xyshift is not None:
                    x_center += xyshift[0]
                    y_center += xyshift[1]                
                device.input_tap(x_center, y_center)
                wait(seconds)
                return
            if suppress is not True:
                printWarning('Retrying ' + image + ' search: ' + str(counter+1) + '/' + str(retry))
            counter = counter + 1
            wait(1)
    elif result != None:
        x, y, w, h = result
        x_center = round(x + w/2)
        y_center = round(y + h/2)
        device.input_tap(x_center, y_center)
        wait(seconds)
    else:
        if suppress is not True and config.getboolean('ADVANCED', 'debug'):
            printWarning('Image:' + image + ' not found on screen, saving screenshot.')
            if not os.path.exists('debug'):
                os.makedirs('debug')
            save_scrcpy_screenshot('debug/' + image.replace("/", "_").replace("\\", "_").replace(".png", "") + "_" + str(time.time()))
        wait(seconds)

#   This function will keep clicking `image` until `secureimage` is no longer visible
#   This is useful as sometimes clicks are sent but not registered and can causes issues
def clickSecure(image, secureimage, retry=5, seconds=1, confidence=0.9, region=(0, 0, 1080, 1920), secureregion=(0, 0, 1080, 1920), grayscale=False, suppress=True):
    counter = 0
    secureCounter = 0
    screenshot = getFrame()

    search = Image.open(os.path.join(cwd, 'img', image + '.png'))
    searchSecure = Image.open(os.path.join(cwd, 'img', secureimage + '.png'))
    result = locate(search, screenshot, grayscale=grayscale, confidence=confidence, region=region)
    resultSecure = locate(searchSecure, screenshot, grayscale=grayscale, confidence=confidence, region=secureregion)

    if result == None and retry != 1:
        while counter < retry:
            screenshot = getFrame()
            result = locate(search, screenshot, grayscale=grayscale, confidence=confidence, region=region)
            resultSecure = locate(searchSecure, screenshot, grayscale=grayscale, confidence=confidence, region=secureregion)
            if result != None and resultSecure != None: # If both are found click
                while resultSecure != None: # While resultSecure is visible click result
                    if secureCounter > 4:
                        break
                    x, y, w, h = result
                    x_center = round(x + w / 2)
                    y_center = round(y + h / 2)
                    device.input_tap(x_center, y_center)
                    wait(2)
                    screenshot = getFrame()
                    resultSecure = locate(searchSecure, screenshot, grayscale=grayscale, confidence=confidence, region=secureregion)
                    secureCounter += 1
            if suppress is not True:
                printWarning('Retrying ' + image + ' search: ' + str(counter+1) + '/' + str(retry))
            counter = counter + 1
            wait(1)
    elif result != None and resultSecure != None: # If both are found click
        while resultSecure != None : # While resultSecure is visible click result
            if secureCounter > 4:
                break
            x, y, w, h = result
            x_center = round(x + w / 2)
            y_center = round(y + h / 2)
            device.input_tap(x_center, y_center)
            wait(2)
            screenshot = getFrame()
            resultSecure = locate(searchSecure, screenshot, grayscale=grayscale, confidence=confidence, region=secureregion)
            secureCounter += 1
    else:
        printError('printsecure failed')
        wait()

def clickWhileVisible(image, confidence=0.9, seconds=1, retry=5, region=(0, 0, 1080, 1920)):
    counter = 0

    while counter < retry:
        while isVisible(image=image, confidence=confidence, seconds=seconds, region=region):
            click(image=image, confidence=confidence, seconds=seconds, region=region, suppress=True)
            counter += 1
        break

    if counter > retry:
        printError('clickWhileVisible failed')

# Checks the 5 locations we find arena battle buttons in and selects the based on choice parameter
# If the choice is outside the found buttons we return the last button found
# if HoE is true we just check the blue pixel value for the 5 buttons
def selectOpponent(choice, seconds=1, hoe=False):
    screenshot = getFrame()
    search = Image.open(os.path.join(cwd, 'img', 'buttons', 'arenafight.png'))

    if hoe is False: # Arena
        locations = {(715, 650, 230, 130), (715, 830, 230, 130), (715, 1000, 230, 130), (715, 1180, 230, 130), (715, 1360, 230, 130)} # 5 regions for the buttons
    else: # HoE
        locations = {(850, 680), (850, 840), (850, 1000), (850, 1160), (850, 1320)}  # 5 regions for the buttons
    battleButtons = []

    # Check each location and add Y coordinate to array (as X doesnt change we don't need it)
    for loc in locations:
        if hoe is False:
            res = locate(search, screenshot, grayscale=False, confidence=0.9, region=loc)
            if res != None:
                battleButtons.append(loc[1] + (loc[3]/2)) # Half the height so we have the middle of the button
        else:
            res = pixelCheck(loc[0], loc[1], 2, seconds=0) # Check blue pixel value
            if res > 150: # If the blue value is more than 150 we have a button
                battleButtons.append(loc[1]) # Append Y coord as X is static (also I can't work out how to sort with both)
    battleButtons.sort() # sort results from top to bottom

    if len(battleButtons) == 0:
        printError('No opponents found!')
        return

    if choice > len(battleButtons): # If the choice is higher than the amount of results we take the last result in the list
        clickXY(820, battleButtons[len(battleButtons)-1])
        wait(seconds)
        return True
    else:
        clickXY(820, battleButtons[choice-1])
        wait(seconds)
        return True

# Scans the coordinates from the two arrays, if a 'Dispatch' button is found returns the X and Y of the center of the button as an array
# We have two arrays as when we scroll down in the bounty list the buttons are offset compared to the unscrolled list
def returnDispatchButtons(scrolled=False):
    screenshot = getFrame()
    search = Image.open(os.path.join(cwd, 'img', 'buttons', 'dispatch_bounties.png'))
    locations = {(820, 430, 170, 120), (820, 650, 170, 120), (820, 860, 170, 120), (820, 1070, 170, 120), (820, 1280, 170, 120)} # Location of the first 5 buttons
    locations_scrolled = {(820, 460, 170, 160), (820, 670, 170, 160), (820, 880, 170, 160), (820, 1090, 170, 160), (820, 1300, 170, 160)} # Location of the first 5 buttons after scrolling down
    dispatchButtons = []
    wait()

    # Different locations if we scrolled down
    if scrolled is True:
        locations = locations_scrolled
    # Check each location and add Y coordinate to array (as X doesnt change we don't need it)
    for loc in locations:
        res = locate(search, screenshot, grayscale=False, confidence=0.9, region=loc)
        if res != None:
            dispatchButtons.append(round(loc[1] + (loc[3]/2))) # Half the height so we have the middle of the button

    dispatchButtons.sort()
    return dispatchButtons

# Checks the pixel at the XY coordinates
# C Variable is array from 0 to 2 for RGB value
def pixelCheck(x, y, c, seconds=1):
    im = getFrame()
    screenshot = np.asarray(im) # Make it an array

    wait(seconds)
    return screenshot[y, x, c]

# Used to confirm which game screen we're currently sitting in, and change to if we're not.
# Optionally with 'bool' flag we can return boolean for if statements
def confirmLocation(location, change=True, bool=False, region=(0,0, 1080, 1920)):
    detected = ''
    locations = {'campaign_selected': 'campaign', 'darkforest_selected': 'darkforest', 'ranhorn_selected': 'ranhorn'}
    regions = [(424, 1750, 232, 170), (208, 1750, 226, 170), (0, 1750, 210, 160)]

    screenshot = getFrame()
    idx = 0

    for location_button, string in locations.items():
        search = Image.open(os.path.join(cwd, 'img', 'buttons', location_button + '.png'))
        res = locate(search, screenshot, grayscale=False, confidence=0.8, region=regions[idx])
        if res != None:
            detected = string
            break
        idx += 1

    if detected == location and bool is True:
        return True
    elif detected != location and change is True and bool is False:
        click(os.path.join('buttons', location + '_unselected'), region=region, suppress=True)
    elif detected != location and bool is True:
        return False

# This function will cycle through known buttons to try and return us to the Campaign screen so we can start from a known location
# It will try 8 times and if we haven't gotten back in that time we exit as we are lost
def recover(silent=False):
    recoverCounter = 0
    while not isVisible('buttons/campaign_selected'):
        # printPurple('recovery: ' + str(recoverCounter))
        clickXY(300, 50) # Neutral location for closing reward pop ups etc, should never be an in game button here
        click('buttons/back', suppress=True, seconds=0.5, region=(0, 1500, 250, 419))
        click('buttons/back_narrow', suppress=True, seconds=0.5, region=(0, 1500, 250, 419))
        click('buttons/exitmenu', suppress=True, seconds=0.5, region=(700, 0, 379, 500))
        click('buttons/confirm_small', suppress=True, seconds=0.5)  #region=(200, 750, 600, 649))
        click('buttons/confirm_stageexit', suppress=True, seconds=0.5, region=(200, 750, 600, 649))
        click('buttons/exit', suppress=True, seconds=0.5, region=(578, 1250, 290, 88))
        click('buttons/campaign_unselected', suppress=True, seconds=0.5, region=(424, 1750, 232, 170))
        recoverCounter += 1
        if recoverCounter > 7:
            break
    if confirmLocation('campaign', bool=True):
        clickXY(550, 1900) # Click in case we found Campaign in the background (basically if a campaign attempt fails)
        if not silent: printGreen('Recovered succesfully')
        return True
    else:
        if not silent: printError('Recovery failed, exiting')
        #if config.getboolean('ADVANCED', 'debug'):
        if not os.path.exists('debug'):
            os.makedirs('debug')
            save_scrcpy_screenshot('debug/recovery_failed_' + str(time.time()))
        exit(0)

# Delay start so it starts after reset
def delayed_start(delay_minutes=0):

    if delay_minutes > 0: delay_minutes = delay_minutes+0.1

    # Get the current time
    current_time = datetime.datetime.now()

    # Calculate the target start time (add delay to current time)
    target_time = current_time + datetime.timedelta(minutes=delay_minutes)

    while current_time < target_time:
        # Print message indicating remaining time
        remaining_time = target_time - current_time
        printWarning(f"Script will start in {remaining_time.seconds // 60} minutes")

        # Sleep for a short duration (avoid tight loop)
        time.sleep(60)

        # Update current time
        current_time = datetime.datetime.now()

# Check if a process with a given name is currently running
def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return True
    return False

# Minimize window
def minimize_window():
    count = 0
    while count < 25:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        if "MuMu" in title or "Bluestacks" in title:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            break
        count += 1
        time.sleep(0.2)  # Sleep for 200 milliseconds

def hide_console():
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    SW_HIDE = 0
    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        user32.ShowWindow(hWnd, SW_HIDE)

def writeToLog(text):
    if args['logging'] is True:
        with open((args['config']).split('.')[0] + '.log', 'a') as log:
            line = '[' + datetime.now().strftime("%d/%m/%y %H:%M:%S") + '] ' + text + '\n'
            log.write(line)

# Coloured text for the console
def printError(text):
    if args['dailies']:
        print(text)
    else:
        print('ERR' + text)
    writeToLog(text)

    # Save error screenshot
    words = text.split()
    result = "_".join(words[:2])
    current_datetime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"error_{result}_{current_datetime}"
    save_scrcpy_screenshot(filename)

def printGreen(text):
    if args['dailies']:
        print(text)
    else:
        print('GRE' + text)
    writeToLog(text)

def printWarning(text):
    if args['dailies']:
        print(text)
    else:
        print('WAR' + text)
    writeToLog(text)

def printBlue(text):
    if args['dailies']:
        print(text)
    else:
        print('BLU' + text)
    writeToLog(text)

def printPurple(text):
    if args['dailies']:
        print(text)
    else:
        print('PUR' + text)
    writeToLog(text)

def printInfo(text):
    print(text,end='')
    writeToLog(text)