from tools import *
from AutoAFK import settings, pauseOrStopEventCheck, printWarning, printGreen, printBlue, printPurple, printInfo
import datetime
import shlex

d = datetime.datetime.now()

boundaries = {
    #locate
    'campaignSelect': (424, 1750, 232, 170),
    'darkforestSelect': (208, 1750, 226, 170),
    'ranhornSelect': (0, 1750, 210, 160),

    #campaign/auto battle
    'begin': (322, 1590, 442, 144),
    'multiBegin': (309, 1408, 467, 129),
    'autobattle': (214, 1774, 256, 112),
    'battle': (574, 1779, 300, 110),
    'battleLarge': (310, 1758, 464, 144),
    'formations': (914, 1762, 102, 134),
    'useAB': (604, 1754, 242, 84),
    'confirmAB': (600, 1220, 250, 100),
    'activateAB': (580, 1208, 300, 150),
    'autobattle0': (575,1020,100,100),
    'autobattleLabel': (200, 578, 684, 178),
    'exitAB': (600, 1270, 300, 100),
    'cancelAB': (218, 1275, 300, 100),
    'pauseBattle': (24, 1419, 119, 104),
    'exitBattle': (168, 886, 130, 116),
    'tryagain': (478, 892, 128, 120),
    'continueBattle': (766, 888, 172, 128),
    'taptocontinue': (374, 1772, 330, 62),
    'kingstowerLabel': (253, 0, 602, 100),
    'challengeTower': (356, 726, 364, 1024),
    'heroclassselect': (5, 1620, 130, 120),


    'collectAfk': (590, 1322, 270, 82),

    'mailLocate': (915, 515, 150, 150),
    'collectMail': (626, 1518, 305, 102),
    'backMenu': (0, 1720, 150, 200),

    'friends': (915, 670, 150, 150),
    'sendrecieve': (750, 1560, 306, 100),

    'exitMerc': (940, 340, 150, 150),

    'fastrewards': (872, 1612, 130, 106),
    'closeFR': (266, 1218, 236, 92),


    'challengeAoH': (294, 1738, 486, 140),
    'attackAoH': (714, 654, 180, 606),
    'battleAoH': (294, 1760, 494, 148),
    'skipAoH': (650, 1350, 200, 200),
    'defeat': (116, 720, 832, 212),

    'exitAoH': (930, 318, 126, 132),

    # Misc
    'inngiftarea': (160, 1210, 500, 100),
    'dialogue_left': (40, 1550, 200, 300)

}

def collectAFKRewards():
    printBlue('Attempting AFK Reward collection')
    confirmLocation('campaign', region=boundaries['campaignSelect'])
    if (isVisible('buttons/campaign_selected', region=boundaries['campaignSelect'])):
        clickXY(550, 1550)
        click('buttons/collect', 0.8, region=boundaries['collectAfk'])
        clickXY(550, 1800, seconds=1) # Click campaign in case we level up
        clickXY(550, 1800, seconds=1) # again for the time limited deal popup
        clickXY(550, 1800, seconds=1) # 3rd to be safe
        printGreen('    AFK Rewards collected!')
    else:
        printError('AFK Rewards chests not found, recovering and will try again')
        recover()
        collectAFKRewards() # In case there was a popup to trial new hero

def collectMail():
    printBlue('Attempting mail collection')
    if isVisible('buttons/mail', region=boundaries['mailLocate']):
        wait()
        # if (pixelCheck(1012, 610, 0) > 240): # We check if the pixel where the notification sits has a red value of higher than 240
        clickXY(960, 630, seconds=2) # Click Mail
        click('buttons/collect_all')
        clickXY(550, 1600) # Clear any popups
        click('buttons/back', region=boundaries['backMenu'])
        printGreen('    Mail collected!')
        # else:
        #     printWarning('    Mail notification not found')
    else:
        printError('Mail icon not found!')

def collectCompanionPoints(mercs=False):
    printBlue('Attempting to send/receive companion points')
    if isVisible('buttons/friends', region=boundaries['friends']):
        if (pixelCheck(1020, 688, 0) > 240):  # We check if the pixel where the notification sits has a red value of higher than 240
            clickXY(960, 810)
            click('buttons/sendandreceive', region=boundaries['sendrecieve'])
            if mercs is True:
                clickXY(720, 1760) # Short term
                clickXY(990, 190) # Manage
                clickXY(630, 1590) # Apply
                clickXY(750, 1410) # Auto lend
                click('buttons/exitmenu', region=boundaries['exitMerc'])
                printGreen('    Mercenaries lent out')
            click('buttons/back', region=boundaries['backMenu'])
            printGreen('    Friends Points Sent')
        else:
            printWarning('    Friends notification not found')

def collectFastRewards(count):
    printBlue('Attempting to collecting Fast Rewards ' + str(count) + 'x times')
    counter = 0
    confirmLocation('campaign', region=boundaries['campaignSelect'])
    if isVisible('buttons/fastrewards', region=boundaries['fastrewards']):
        if (pixelCheck(980, 1620, 0) > 220):  # We check if the pixel where the notification sits has a red value of higher than 240
            clickXY(950, 1660)
            while counter < count:
                clickXY(710, 1260, seconds=3)
                clickXY(550, 1800)
                counter = counter + 1
            click('buttons/close', region=boundaries['closeFR'])
            printGreen('    Fast Rewards Done')
        else:
            printWarning('    Fast Rewards already done')
    else:
        printError('    Fast Rewards icon not found!')

# Loads and exits a campaign abttle for dailies quest
def attemptCampaign():
    printBlue('Attempting Campaign battle')
    confirmLocation('campaign', region=boundaries['campaignSelect'])
    click('buttons/begin', seconds=2, retry=3, region=boundaries['begin'])
    # Check if we're multi or single stage
    multi = isVisible('buttons/begin', 0.7, retry=3, region=boundaries['multiBegin'])
    if multi:
        printGreen('    Multi stage detected')
        click('buttons/begin', 0.7, retry=5, seconds=2, region=boundaries['multiBegin']) # Second button to enter multi
    else:
        printGreen('    Single stage detected')
    # Start and exit battle
    # Weird amount of retries as when loading the game for the first time this screen can take a while to load, so it acts as a counter
    if isVisible('buttons/heroclassselect', retry=20, region=boundaries['heroclassselect']): # Confirm we're on the hero selection screen
        if multi: # Multi has different button for reasons
            click('buttons/beginbattle', 0.7, retry=3, seconds=3, region=boundaries['battle'])
        else:
            click('buttons/battle', 0.8, retry=3, seconds=3, region=boundaries['battle'])
        # Actions to exit an active fight and back out to the Campaign screen
        click('buttons/pause', retry=3, region=boundaries['pauseBattle']) # 3 retries as ulting heroes can cover the button
        click('buttons/exitbattle', retry=3, region=boundaries['exitBattle'])
        click('buttons/back', retry=3, seconds=3, suppress=True, region=boundaries['backMenu'])
        if confirmLocation('campaign', bool=True, region=boundaries['campaignSelect']):
            printGreen('    Campaign attempted successfully')
    else:
        printError('    Something went wrong, attempting to recover')
        recover()

# Handles the Bounty Board, calls dispatchSoloBounties() to handle solo dust/diamond recognition and dispatching
def handleBounties():
    printBlue('Handling Bounty Board')
    config.read(settings) # Has to be read here again to update
    confirmLocation('darkforest', region=boundaries['darkforestSelect'])
    clickXY(600, 1320)
    if isVisible('labels/bountyboard', retry=3):

        if config.getboolean('BOUNTIES', 'dispatchsolobounties'):
            clickXY(650, 1700) # Solo tab
            isVisible('buttons/collect_all', seconds=3, click=True)
            dispatchSoloBounties(remaining=config.getint('BOUNTIES', 'remaining'), maxrefreshes=config.getint('BOUNTIES', 'refreshes'))

        if config.getboolean('BOUNTIES', 'dispatchteambounties'):
            clickXY(950, 1700) # Team tab
            click('buttons/collect_all', seconds=2, suppress=True)
            click('buttons/dispatch', confidence=0.8, suppress=True, grayscale=True)
            click('buttons/confirm', suppress=True)

        if config.getboolean('BOUNTIES', 'dispatcheventbounties'):
            if isVisible('labels/event_bounty', click=True):
                click('buttons/collect_all', seconds=2, suppress=True)
                while isVisible('buttons/dispatch_bounties', click=True) == True:
                    clickXY(530, 1030, seconds=2)
                    clickXY(120, 1500)
                    click('buttons/dispatch', confidence=0.8, grayscale=True)

        click('buttons/back', region=boundaries['backMenu'])
        printGreen('    Bounties attempted successfully')
    else:
        printError('    Bounty Board not found, attempting to recover')
        recover()

# Loops through the bounty board returning found Dispatch buttons for dispatcher() to handle
# maxrefreshes is how many times to refresh before hitting dispatch all
# remaining is how many leftover bounties we should use dispatch all on rather than refresh again
def dispatchSoloBounties(remaining=2, maxrefreshes=3):
    refreshes = 0
    while refreshes <= maxrefreshes:
        if refreshes > 0:
            printWarning('    Board refreshed (#' + str(refreshes) + ')')
        dispatcher(returnDispatchButtons()) # Send the list to the function to dispatch
        swipe(550, 800, 550, 500, duration=200, seconds=2) # scroll down
        dispatcher(returnDispatchButtons(scrolled=True)) # Send the list to the function to dispatch
        if refreshes >= 1: # quick read to see how many are left after the last dispatch, else we refresh the board needlessly before we do it
            if len(returnDispatchButtons(scrolled=True)) <= remaining: # if <=remaining bounties left we just dispatch all and continue
                printWarning('  ' + str(remaining) + ' or less bounties remaining, dispatching..')
                click('buttons/dispatch', confidence=0.8, suppress=True, grayscale=True)
                click('buttons/confirm', suppress=True)
                return
        if refreshes < maxrefreshes:
            clickXY(130, 300)
            clickXY(700, 1250)
        refreshes += 1
    printGreen('    ' + str(maxrefreshes) + ' refreshes done, dispatching remaining..')
    click('buttons/dispatch', confidence=0.8, suppress=True, grayscale=True)
    click('buttons/confirm', suppress=True)

# Recieves a list of Dispatch buttons Y coordinates and checks/dispatches the resource
def dispatcher(dispatches):
    # For loop over each button passed to the function
    for button in dispatches:
        # Names and Buttons
        bounty_types = {'dust': 'labels/bounties/dust', 'diamonds': 'labels/bounties/diamonds', 'juice': 'labels/bounties/juice',
            'shards': 'labels/bounties/shards', 'gold': 'labels/bounties/gold', 'soulstone': 'labels/bounties/soulstone'}
        # For each button we use `region=` to only check the resource in bounds to the left of it
        for resource, image in bounty_types.items():
            if isVisible(image, region=(30, button-100, 140, 160), seconds=0):
                if resource != 'gold' and resource != 'soulstone': # because there's no config setting for these
                    if config.getboolean('BOUNTIES', 'dispatch' + resource): # If it's enabled dispatch
                        printBlue('Dispatching ' + resource.title())
                        clickXY(900, button)
                        clickXY(350, 1150)
                        clickXY(750, 1150)
                break # Once resource is found and actions taken move onto the next button to save unnecessary checks


def handleArenaOfHeroes(count, opponent, app):
    counter = 0
    printBlue('Battling Arena of Heroes ' + str(count) + ' times')
    confirmLocation('darkforest', region=boundaries['darkforestSelect'])
    clickXY(740, 1100)
    clickXY(550, 50)
    if isVisible('labels/arenaofheroes_new'): # The label font changes for reasons
        click('labels/arenaofheroes_new', suppress=True)
        wait(1)
        click('buttons/challenge', retry=3, region=boundaries['challengeAoH']) # retries for animated button
        while counter < count:
            wait(1) # To avoid error when clickMultipleChoice returns no results
            selectOpponent(choice=opponent)
            # clickMultipleChoice('buttons/arenafight', count=4, confidence=0.98, region=boundries['attackAoH'], seconds=3) # Select 4th opponent
            while isVisible('buttons/heroclassselect', retry=3, region=boundaries['heroclassselect']): # This is rather than Battle button as that is animated and hard to read
                clickXY(550, 1800)
            click('buttons/skip', retry=5, confidence=0.8, suppress=True, region=boundaries['skipAoH']) # Retries as ulting heros can cover the button
            if returnBattleResults(type='arena'):
                printGreen('    Battle #' + str(counter+1) + ' Victory!')
                clickXY(600, 550) # Clear loot popup
            else:
                printError('    Battle #' + str(counter + 1) + ' Defeat!')
            clickXY(600, 550)  # Back to opponent selection
            counter = counter+1
            if pauseOrStopEventCheck(app.dailies_pause_event, app.dailies_stop_event):
                break  # Exit the loop if stop event is set
            if pauseOrStopEventCheck(app.activity_pause_event, app.activity_stop_event):
                break  # Exit the loop if stop event is set
        click('buttons/exitmenu', region=boundaries['exitAoH'])
        click('buttons/back', retry=3, region=boundaries['backMenu'])
        click('buttons/back', retry=3, region=boundaries['backMenu'])
        printGreen('    Arena battles complete')
    else:
        printError('Arena of Heroes not found, attempting to recover')
        recover()

def collectGladiatorCoins():
    printBlue('Collecting Gladiator Coins')
    confirmLocation('darkforest', region=boundaries['darkforestSelect'])
    clickXY(740, 1050)
    clickXY(550, 50)
    swipe(550, 800, 550, 500, duration=200, seconds=2) # scroll down
    if isVisible('labels/legendstournament_new'): # The label font changes for reasons
        click('labels/legendstournament_new', suppress=True)
        clickXY(550, 300, seconds=2)
        clickXY(50, 1850)
        click('buttons/back', region=boundaries['backMenu'])
        click('buttons/back', region=boundaries['backMenu'])
        printGreen('    Gladiator Coins collected')
    else:
        printError('    Legends Tournament not found, attempting to recover')
        recover()

def useBagConsumables():
    crashcounter = 0 # So we don't get stuck forever in the Use button loop
    printBlue('Using consumables from bag')
    clickXY(1000, 500, seconds=3)
    if isVisible('buttons/batchselect', click=True, retry=3):
        if isVisible('buttons/confirm_grey'):
            printWarning('Nothing selected/available! Returning..')
            click('buttons/back', region=boundaries['backMenu'])
            return
        clickXY(550, 1650, seconds=2)
        while not isVisible('buttons/use_batch'):
            clickXY(550, 1800, seconds=0) # 1 second check above is plenty so this is 0
            crashcounter += 1
            if crashcounter > 30:
                printError('Something went wrong (normally gear chests being selected), returning..')
                click('buttons/back', region=boundaries['backMenu'])
                click('buttons/back', region=boundaries['backMenu'])
                return
        clickXY(550, 1800) # Use
        clickXY(950, 1700) # 'All' Bag button to clear loot
        click('buttons/back', region=boundaries['backMenu'], suppress=True)
        printGreen('    Bag consumables used!')
    else:
        printError('    Bag not found, attempting to recover')
        recover()

def collectTSRewards():
    printBlue('Collecting Treasure Scramble daily loot')
    confirmLocation('darkforest', region=boundaries['darkforestSelect'])
    clickXY(750, 1100) # Open Arena of Heroes
    clickXY(550, 50) # Clear Arena Tickets
    ts_banners = ['labels/tsbanner_forest', 'labels/tsbanner_ice', 'labels/tsbanner_fog', 'labels/tsbanner_volcano']
    for banner in ts_banners: # Check the 4 debuffs
        if isVisible(banner, confidence=0.8, click=True):
            wait(2)
            if isVisible('buttons/ts_path', click=True):
                clickXY(370, 945) # Choose path
                clickXY(520, 1700) # Confirm path
                click('buttons/back', retry=3, region=boundaries['backMenu'])
                click('buttons/back', retry=3, region=boundaries['backMenu'])
                return
            else:
                clickXY(400, 50, seconds=2) # Clear Rank Up
                clickXY(400, 50, seconds=2) # Clear Loot
                click('buttons/back', retry=3, region=boundaries['backMenu'])
                click('buttons/back', retry=3, region=boundaries['backMenu'])
                printGreen('    Treasure Scramble daily loot collected!')
            return
    else:
        printError('    Treasure Scramble not found, attempting to recover')
        recover()

def collectFountainOfTime():
    printBlue('Collecting Fountain of Time')
    confirmLocation('darkforest', region=boundaries['darkforestSelect'])
    clickXY(850, 700, seconds=6)
    clickXY(850, 700, seconds=1)
    if isVisible('labels/temporalrift'):
        clickXY(550, 1800)
        clickXY(250, 1300)
        clickXY(700, 1350) # Collect
        clickXY(550, 1800, seconds=3) # Clear level up
        clickXY(550, 1800, seconds=3) # Clear limited deal
        clickXY(550, 1800, seconds=3) # Clear newly unlocked
        click('buttons/back', region=boundaries['backMenu'])
        printGreen('    Fountain of Time collected')
    else:
        printError('    Temporal Rift not found, attempting to recover')
        recover()

def openTower(name):
    printBlue('Opening ' + name + '.')
    confirmLocation('darkforest', region=boundaries['darkforestSelect'])
    wait(3) # Medium wait to make sure tower button is active when we click
    clickXY(500, 870, seconds=3) # Long pause for animation opening towers
    if isVisible('labels/kingstower', region=boundaries['kingstowerLabel'], retry=3, confidence=0.85):
        towers = {"King's Tower": [500, 870], "Lightbearer Tower": [300, 1000], "Wilder Tower": [800, 600], "Mauler Tower": [400, 1200],
                  "Graveborn Tower": [800, 1200], "Hypogean Tower": [600, 1500], "Celestial Tower": [300, 500]}
        for tower, location in towers.items():
            if tower == name:
                clickXY(location[0], location[1], seconds=3)
    else:
        printError('Tower selection screen not found.')
        recover()

# This is a long one, we have a whole host of fail safes because we want it to be as stable as possible
class towerPusher():
    towerOpen = False # for defining if we need to open tower or not

    # Loads selected formation, enables auto-battle and periodically checks for victory
    def pushTower(tower, formation=3, duration=1, app=None):
        while app.push_thread_running or args['tower'] or args['autotower']:
            # Open tower is needed then set it to enabled
            if towerPusher.towerOpen is False:
                openTower(tower)
                towerPusher.towerOpen = True

            # Two checks, one for the Challenge button in the tower screen and one for the AutoBattle button on the hero selection screen
            # Both checks we check for two positives in a row so they aren't detected in the background while AutoBattle is running
            # If found we run configureBattleFormation() to configure the formation and enable auto battle
            challengetimer = 0
            autobattletimer = 0
            # Challenge button
            while isVisible('buttons/challenge_plain', confidence=0.8, retry=3, seconds=2, region=boundaries['challengeTower']):
                challengetimer += 1
                if challengetimer >= 2:
                    click('buttons/challenge_plain', confidence=0.8, retry=3, seconds=3, region=boundaries['challengeTower'])
                    configureBattleFormation(formation)
                    challengetimer = 0
            # Autobattle button
            while isVisible('buttons/autobattle', 0.92, retry=3, seconds=2, region=boundaries['autobattle']):  # higher confidence so we don't find it in the background
                autobattletimer += 1
                if autobattletimer >= 2:
                    configureBattleFormation(formation)
                    autobattletimer = 0

            # We wait for the given duration (minus some time for configuring teams) then clickXY() to prompt the AutoBattle notice and check for victory
            wait((duration * 60)-30)

            if pauseOrStopEventCheck(app.push_pause_event, app.push_stop_event):
                towerPusher.towerOpen = False
                break

            clickXY(550, 1750)

            # Make sure the AutoBattle notice screen is visible
            if isVisible('labels/autobattle', retry=2, region=boundaries['autobattleLabel']): # Make sure the popup is visible
                # If it's 0 assume we haven't passed (not that bold an assumption..)
                if isVisible('labels/autobattle_0', retry=3, region=boundaries['autobattle0']):
                    if config.getboolean('PUSH', 'suppressspam') is False:
                        printWarning('No victory found, checking again in ' + str(config.get('PUSH', 'victoryCheck') + ' minutes.'))
                    click('buttons/cancel', retry=3, suppress=True, region=boundaries['cancelAB'])
                else: # If we don't see 0 we assume victory. We exit the battle, clear victory screen and clear time limited rewards screen
                    printGreen('Victory found! Loading the ' + str(config.get('PUSH', 'formation') + ' formation for the current stage..'))
                    click('buttons/exit', retry=3, suppress=True, region=boundaries['exitAB'])
                    click('buttons/pause', 0.8, retry=3, suppress=True, region=boundaries['pauseBattle'])  # 3 retries as ulting heroes can cover the button
                    click('buttons/exitbattle', retry=2, suppress=True, region=boundaries['exitBattle'])
                    click('labels/taptocontinue', retry=2, confidence=0.8, suppress=True, grayscale=True, region=boundaries['taptocontinue'])
                    wait(3)
                    clickXY(550, 1750) # To clear the Limited Rewards pop up every 20 stages
            else: # If after clicking we don't get the Auto Battle notice pop up something has gone wrong so we recover() and load pushTower() again
                printWarning('AutoBattle screen not found, reloading auto-push..')
                if recover() is True:
                    towerPusher.towerOpen = False
                    openTower(tower)
                    towerPusher.towerOpen = True

def pushCampaign(formation=3, duration=1,app=None):
    while app.push_thread_running:
        if (isVisible('buttons/begin', 0.7, retry=3, click=True)):
            continue

        if isVisible('buttons/autobattle', 0.95, retry=3, seconds=2, region=boundaries['autobattle']) and not isVisible('labels/autobattle'):
                configureBattleFormation(formation)
        else:
            if pauseOrStopEventCheck(app.push_pause_event, app.push_stop_event):
                break
            clickXY(550, 1750) # Click to prompt the AutoBattle popup
            if isVisible('labels/autobattle'):
                if isVisible('labels/autobattle_0', region=boundaries['autobattle0']): # If it's 0 continue
                    if config.getboolean('PUSH', 'suppressSpam') is False:
                        printWarning('No victory found, checking again in ' + str(config.get('PUSH', 'victoryCheck') + ' minutes.'))
                    click('buttons/cancel', retry=3, suppress=True, region=boundaries['cancelAB'])
                    wait((duration * 60) - 30) # Sleep for the wait duration
                else: # If it's not 0 we have passed a stage
                    printGreen('Victory found! Loading the ' + str(config.get('PUSH', 'formation') + ' formation for the current stage..'))
                    click('buttons/exit', suppress=True, retry=3, region=boundaries['exitAB'])
                    click('buttons/pause', confidence=0.8, retry=3, suppress=True, region=boundaries['pauseBattle'])  # 3 retries as ulting heroes can cover the button
                    click('buttons/exitbattle', suppress=True, retry=3, region=boundaries['exitBattle'])
                    click('labels/taptocontinue', confidence=0.8, suppress=True, grayscale=True, region=boundaries['taptocontinue'])
            else:
                recover()

def configureBattleFormation(formation):
    artifacts = None
    counter = 0
    if config.getboolean('ADVANCED', 'ignoreformations') is True:
        printWarning('ignoreformations enabled, skipping formation selection')
        click('buttons/autobattle', suppress=True, retry=3, region=boundaries['autobattle'])  # So we don't hit it in the background while autobattle is active
        clickSecure('buttons/activate', 'labels/autobattle', region=boundaries['activateAB'], secureregion=boundaries['autobattleLabel'])
        return
    elif isVisible('buttons/formations', region=boundaries['formations']):
        click('buttons/formations', seconds=3, retry=3, region=boundaries['formations'])
        if config.getboolean('ADVANCED', 'popularformations'): # Use popular formations tab
            clickXY(800, 1650, seconds=2)  # Change to 'Popular' tab
        clickXY(850, 425 + (formation * 175), seconds=2)
        click('buttons/use', retry=3, region=boundaries['useAB'], seconds=2)

        # Configure Artifacts
        while artifacts is None and counter <= 5: # loop because sometimes isVisible returns None here
            artifacts = isVisible('buttons/checkbox_checked', region=(230, 1100, 80, 80)) # Check checkbox status
            counter += 1
        if counter >= 5: # If still None after 5 tries give error and contiue without configuring
            printError('Couldn\'t read artifact status')
        if artifacts is not config.getboolean('PUSH', 'useartifacts') and artifacts is not None:
            if config.getboolean('PUSH', 'useartifacts'):
                printBlue('Enabling Artifact copying')
            else:
                printBlue('Disabling Artifact copying')
            clickXY(275, 1150) # clickXY not ideal here but my brain is fried so it'll do for now

        click('buttons/confirm_small', retry=3, region=boundaries['confirmAB'])
        click('buttons/autobattle', retry=3, region=boundaries['autobattle'])  # So we don't hit it in the background while autobattle is active
        clickSecure('buttons/activate', 'labels/autobattle', region=boundaries['activateAB'], secureregion=boundaries['autobattleLabel'])
    else:
        printWarning('Could not find Formations button')

def handleKingsTower():
    printBlue('Attempting Kings Tower battle')
    confirmLocation('darkforest', region=boundaries['darkforestSelect'])
    clickXY(500, 870, seconds=3) # Long pause for animation
    if isVisible('labels/kingstower'):
        clickXY(555, 585)
        click('buttons/challenge_plain', 0.7, retry=5, suppress=True, seconds=5) # lower confidence and retries for animated button
        # For reasons sometimes this button is 'beginbattle' and sometimes it is 'begin', so we use clickXY
        clickXY(700, 1850, seconds=2)
        # click('buttons/beginbattle', 0.8, seconds=3, retry=5)
        click('buttons/pause', 0.8, retry=5, suppress=True)
        click('buttons/exitbattle')
        click('buttons/back', retry=3, region=boundaries['backMenu'])
        click('buttons/back', retry=3, region=boundaries['backMenu'])
        if isVisible('buttons/back', retry=3, region=boundaries['backMenu']):
            click('buttons/back', region=boundaries['backMenu']) # Last one only needed for multifights
        printGreen('    Tower attempted successfully')
    else:
        printError('Tower screen not found, attempting to recover')
        recover()

def collectInnGifts():
    checks = 0
    printBlue('Attempting daily Inn gift collection')
    confirmLocation('ranhorn', region=boundaries['ranhornSelect'])
    wait()
    clickXY(500, 200, seconds=4)
    if isVisible('buttons/manage'):
        while checks < 3:
            if isVisible('buttons/inn_gift', confidence=0.75, click=True, region=boundaries['inngiftarea'], seconds=2):
                clickXY(550, 1400, seconds=0.5) # Clear loot
                clickXY(550, 1400, seconds=0.5) # Clear loot
                continue
            checks += 1
            wait()
        click('buttons/back', region=boundaries['backMenu'])
        printGreen('    Inn Gifts collected.')
        wait(2) # wait before next task as loading ranhorn can be slow
    else:
        printError('    Inn not found, attempting to recover')
        recover()

def handleShopPurchasing(counter):
    config.read(settings)  # re-load for any updated values
    toprow = {'arcanestaffs': [180, 920], 'cores': [425, 920], 'timegazer': [650, 920], 'baits': [875, 920]}
    bottomrow = {'dust_gold': 'buttons/shop/dust', 'shards_gold': 'buttons/shop/shards_gold', 'dust_diamond': 'buttons/shop/dust_diamonds', 'elite_soulstone': 'buttons/shop/soulstone',
                  'superb_soulstone': 'buttons/shop/superstone', 'silver_emblem': 'buttons/shop/silver_emblems', 'gold_emblem': 'buttons/shop/gold_emblems', 'poe': 'buttons/shop/poe'}

    # Prettify the names were outputting into console
    def nameTranslator(name):
        names = {'dust_gold': 'Dust (Gold)', 'shards_gold': 'Shards', 'dust_diamond': 'Dust (Diamonds)', 'elite_soulstone': 'Elite Soulstone',
                  'superb_soulstone': 'Superb Soulstone', 'silver_emblem': 'Silver Emblems', 'gold_emblem': 'Gold Emblems', 'poe': 'Poe Coins (Gold)',
                 'arcanestaffs': 'Arcane Staffs', 'cores': 'Elemental Cores', 'timegazer': 'Timegazer Card', 'baits': 'Bait'}
        for internal, external in names.items():
            if name == internal:
                return external


    # Purchase top row
    for item, pos in toprow.items():
        if config.getboolean('SHOP', item):
            if item == 'timegazer' and counter > 0: # only one TG card
                continue
            if item == 'baits' and counter > 1: # only two baits
                continue
            if (item == 'cores' or item == 'arcanestaffs') and counter > 2: # only three shards/staffs
                continue
            printPurple('    Buying: ' + nameTranslator(item))
            clickXY(pos[0], pos[1])
            click('buttons/shop/purchase', suppress=True)
            clickXY(550, 1220, seconds=2)

    # Scroll down so bottom row is visible
    swipe(550, 1500, 550, 1200, 500, seconds=5)

    # Purchase bottom 4 rows
    for item, button in bottomrow.items():
        if config.getboolean('SHOP', item):
            if isVisible(button, 0.95, click=True):
                printPurple('    Buying: ' + nameTranslator(item))
                click('buttons/shop/purchase', suppress=True)
                clickXY(550, 1220)
    wait(3) # Long wait else Twisted Realm isn't found after if enabled in Dailies

def shopPurchases(shoprefreshes,skipQuick=0):
    if config.getboolean('SHOP', 'quick') and skipQuick==0:
        shopPurchases_quick(shoprefreshes)
        return
    printBlue('Attempting store purchases (Refreshes: ' + str(shoprefreshes) + ')')
    counter = 0
    confirmLocation('ranhorn', region=boundaries['ranhornSelect'])
    wait(2)
    clickXY(440, 1750, seconds=5)
    if isVisible('labels/store'):
        # First purchases
        handleShopPurchasing(counter)
        # refresh purchases
        while counter < shoprefreshes:
            clickXY(1000, 300)
            click('buttons/confirm', suppress=True, seconds=5)
            counter += 1
            printGreen('    Refreshed store ' + str(counter) + ' times.')
            handleShopPurchasing(counter)
        click('buttons/back')
        printGreen('    Store purchases attempted.')
        wait(2) # wait before next task as loading ranhorn can be slow
    else:
        printError('Store not found, attempting to recover')
        recover()

def shopPurchases_quick(shoprefreshes):
    printBlue('Attempting store quickbuys (Refreshes: ' + str(shoprefreshes) + ')')
    counter = 0
    confirmLocation('ranhorn')
    wait(2)
    clickXY(440, 1750, seconds=5)
    if isVisible('labels/store'):
        if isVisible('buttons/quickbuy', click=True):
            wait(1)
            click('buttons/purchase', seconds=5)
            clickXY(970, 90, seconds=2)
            while counter < shoprefreshes:
                clickXY(1000, 300)
                click('buttons/confirm', suppress=True, seconds=2)
                click('buttons/quickbuy', seconds=2)
                click('buttons/purchase', seconds=2)
                clickXY(970, 90)
                counter += 1
            click('buttons/back')
            printGreen('Store purchases attempted.')
        else:
            printBlue('Quickbuy not found, switching to old style')
            click('buttons/back')
            shopPurchases(shoprefreshes,1)

    else:
        printError('Store not found, attempting to recover')
        recover()

def handleGuildHunts():
    printBlue('Attempting to run Guild Hunts')
    confirmLocation('ranhorn', region=boundaries['ranhornSelect'])
    clickXY(380, 360)
    wait(6)
    clickXY(550, 1800) # Clear chests
    # Collect any guild reward chests we have
    click('buttons/guild_chests', seconds=2)
    if isVisible('buttons/collect_guildchest'):
        click('buttons/collect_guildchest')
        clickXY(550, 1300)
        clickXY(900, 550)
        clickXY(550, 1800)  # Clear window
        wait(1)
    else:
        clickXY(550, 1800)  # Clear window
    clickXY(290, 860)
    # Wrizz check
    if isVisible('labels/wrizz'):
        if (isVisible('buttons/quickbattle')):
            printGreen('    Wrizz Found, collecting')
            click('buttons/quickbattle')
            clickXY(725, 1300)
            # So we don't get stuck on capped resources screen
            if isVisible('buttons/confirm'):
               click('buttons/confirm')
            clickXY(550, 500)
            clickXY(550, 500,seconds=2)
        else:
            printWarning('    Wrizz quick battle not found')
        # Soren Check
        clickXY(970, 890)
        if isVisible('buttons/quickbattle'):
            printGreen('    Soren Found, collecting')
            click('buttons/quickbattle')
            clickXY(725, 1300)
            # So we don't get stuck on capped resources screen
            if isVisible('buttons/confirm'):
               click('buttons/confirm')
            clickXY(550, 500)
            clickXY(550, 500, seconds=2)
        else:
            printWarning('    Soren quick battle not found')
        clickXY(70, 1810)
        clickXY(70, 1810)
        printGreen('    Guild Hunts checked successfully')
    else:
        printError('    Error opening Guild Hunts, attempting to recover')
        recover()

# Checks for completed quests and collects, then clicks the open chect and clears rewards
# Once for Dailies once for Weeklies
def collectQuests():
    printBlue('Attempting to collect quest chests')
    clickXY(960, 250)
    if isVisible('labels/quests'):
        clickXY(400, 1650) # Dailies
        if isVisible('labels/questcomplete'):
            printGreen('    Daily Quest(s) found, collecting..')
            clickXY(930, 680, seconds=4) # Click top quest
            click('buttons/fullquestchest', seconds=3, retry=3, suppress=True)
            clickXY(400, 1650)
        clickXY(600, 1650) # Weeklies
        if isVisible('labels/questcomplete'):
            printGreen('    Weekly Quest(s) found, collecting..')
            clickXY(930, 680, seconds=4) # Click top quest
            click('buttons/fullquestchest', seconds=3, retry=3, suppress=True)
            clickXY(600, 1650, seconds=2)
            clickXY(600, 1650)  # Second in case we get Limited Rewards popup
        click('buttons/back', retry=3)
        printGreen('    Quests collected')
    else:
        printError('    Quests screen not found, attempting to recover')
        recover()

def clearMerchant():
    printBlue('Attempting to collect merchant deals')
    clickXY(120, 300, seconds=5)
    if isVisible('buttons/funinthewild', click=True, seconds=2):
        clickXY(250, 1820, seconds=2) # Ticket
        clickXY(250, 1820, seconds=2) # Reward
    swipe(1000, 1825, 100, 1825, 500)
    swipe(1000, 1825, 100, 1825, 500, seconds=3)
    if isVisible('buttons/noblesociety'):
        printPurple('    Collecting Nobles')
        # Nobles
        clickXY(675, 1825)
        if isVisible('buttons/confirm_nobles', 0.8, retry=2):
            printWarning('Noble resource collection screen found, skipping Noble collection')
            clickXY(70, 1810)
        else:
            # Champion
            clickXY(750, 1600) # Icon
            clickXY(440, 1470, seconds=0.5)
            clickXY(440, 1290, seconds=0.5)
            clickXY(440, 1100, seconds=0.5)
            clickXY(440, 915, seconds=0.5)
            clickXY(440, 725, seconds=0.5)
            clickXY(750, 1600) # Icon
            # Twisted
            clickXY(600, 1600) # Icon
            clickXY(440, 1470, seconds=0.5)
            clickXY(440, 1290, seconds=0.5)
            clickXY(440, 1100, seconds=0.5)
            clickXY(440, 915, seconds=0.5)
            clickXY(440, 725, seconds=0.5)
            clickXY(600, 1600) # Icon
            # Regal
            clickXY(450, 1600) # Icon
            clickXY(440, 1470, seconds=0.5)
            clickXY(440, 1290, seconds=0.5)
            clickXY(440, 1100, seconds=0.5)
            clickXY(440, 915, seconds=0.5)
            clickXY(440, 725, seconds=0.5)
            clickXY(450, 1600) # Icon
        # Monthly Cards
        printPurple('    Collecting Monthly Cards')
        clickXY(400, 1825)
        # Monthly
        clickXY(300, 1000, seconds=3)
        clickXY(560, 430)
        # Deluxe Monthly
        clickXY(850, 1000, seconds=3)
        clickXY(560, 430)
        # Daily Deals
        swipe(200, 1825, 450, 1825, 1000, seconds=2)
        clickXY(400, 1825)
        # Special Deal, no check as its active daily
        printPurple('    Collecting Special Deal')
        click('buttons/dailydeals')
        clickXY(150, 1625)
        clickXY(150, 1625)
        # Daily Deal
        if isVisible('buttons/merchant_daily', confidence=0.8, retry=2, click=True):
            printPurple('    Collecting Daily Deal')
            swipe(550, 1400, 550, 1200, 500, seconds=3)
            click('buttons/dailydeals', confidence=0.8, retry=2)
            clickXY(400, 1675, seconds=2)
        # Biweeklies
        if d.isoweekday() == 3: # Wednesday
            if isVisible('buttons/merchant_biweekly', confidence=0.8, retry=2, click=True):
                printPurple('    Collecting Bi-weekly Deal')
                swipe(300, 1400, 200, 1200, 500, seconds=3)
                clickXY(200, 1200)
                clickXY(550, 1625, seconds=2)
        # Yuexi
        if d.isoweekday() == 1: # Monday
            printPurple('    Collecting Yuexi')
            clickXY(200, 1825)
            clickXY(240, 880)
            clickXY(150, 1625, seconds=2)
        # Clear Rhapsody bundles notification
        printPurple('    Clearing Rhapsody bundles notification')
        swipe(200, 1825, 1000, 1825, 450, seconds=2)
        if isVisible('labels/wishing_ship', confidence=0.8, retry=2, click=True):
            clickXY(620, 1600)
            clickXY(980, 200)
            clickXY(70, 1810)
            clickXY(70, 1810)
        printGreen('    Merchant deals collected')
        recover(True)
    else:
        printError('    Noble screen not found, attempting to recover')
        recover()

# Opens Twisted Realm and runs it once with whatever formation is loaded
def handleTwistedRealm():
    printBlue('Attempting to run Twisted Realm')
    confirmLocation('ranhorn', region=boundaries['ranhornSelect'])
    clickXY(380, 360, seconds=6)
    clickXY(550, 1800) # Clear chests
    clickXY(775, 875, seconds=2)
    clickXY(550, 600, seconds=3)
    if isVisible('buttons/nextboss'):
        printGreen('    Twisted Realm found, battling')
        if isVisible('buttons/challenge_tr', retry=3, confidence=0.8):
            clickXY(550, 1850, seconds=2)
            click('buttons/autobattle', retry=3, seconds=2)
            if isVisible('buttons/checkbox_blank'):
                clickXY(300, 975)  # Activate Skip Battle Animations
            clickXY(700, 1300, seconds=6)
            clickXY(550, 1300)
            clickXY(550, 1800)
            clickXY(70, 1800)
            clickXY(70, 1800)
            clickXY(70, 1800)
            printGreen('    Twisted Realm attempted successfully')
            wait(3)  # wait before next task as loading ranhorn can be slow
            recover(True)
        else:
            clickXY(70, 1800)
            clickXY(70, 1800)
            printError('    Challenge button not found, attempting to recover')
            recover()
    else:
        printError('    Error opening Twisted Realm, attempting to recover')
        # TODO Add 'Calculating' confirmation to exit safely
        recover()

# Opens a Fight of Fates battle and then cycles between dragging heroes and dragging skills until we see the battle end screen
# Collects quests at the end
def handleFightOfFates(battles=3):
    printBlue('Attempting to run Fight of Fates ' + str(battles) + ' times')
    counter = 0
    expandMenus() # Expand left menu again as it can shut after other dailies activities
    click('buttons/fightoffates', confidence=0.8, retry=5, seconds=3)
    if isVisible('labels/fightoffates'):
        while counter < battles:
            click('buttons/challenge_tr', confidence=0.8, suppress=True, retry=3, seconds=15)
            while not isVisible('labels/fightoffates', confidence=0.95):
                # Hero
                swipe(200, 1700, 290, 975, 200)
                # Skill 1
                swipe(450, 1700, 550, 950, 200)
                # Hero
                swipe(200, 1700, 290, 975, 200)
                # Skill 2
                swipe(600, 1700, 550, 950, 200)
                # Hero
                swipe(200, 1700, 290, 975, 200)
                # Skill 3
                swipe(800, 1700, 550, 950, 200)
            counter = counter + 1
            printGreen('    Fight of Fates Battle #' + str(counter) + ' complete')
        # Click quests
        clickXY(975, 125, seconds=2)
        # select dailies tab
        clickXY(650, 1650, seconds=1)
        # Collect Dailies
        clickXY(940, 680, seconds=2)
        clickXY(980, 435, seconds=2)
        # clear loot
        clickXY(550, 250, seconds=2)
        # Back twice to exit
        clickXY(70, 1650, seconds=1)
        clickXY(70, 1810, seconds=1)
        printGreen('    Fight of Fates attempted successfully')
    else:
        printWarning('Fight of Fates not found, recovering..')
        recover()

# Basic support for dailies quests, we simply choose the 5 cards from the top row of our hand
# Ater starting a battle we read the Stage 1/2/3 text at the top to determine when our opponent has placed their cards and to continue with placing ours
# Timeout is probably 10 seconds longer than the stage timer so if we exceed that something has gone wrong
# A round can take between 40 seconds or over 2 minutes depending on if our opponent is afk or not, at the end we collect daily quests
def handleBattleofBlood(battles=3):
    printBlue('Attempting to run Battle of Blood ' + str(battles) + ' times')
    battlecounter = 0 # Number of battles we want to run
    bob_timeout = 0 # Timer for tracking if something has gone wrong with placing cards
    expandMenus() # Expand left menu again as it can shut after other dailies activities
    click('buttons/events', confidence=0.8, retry=3, seconds=3)
    if isVisible('labels/battleofblood_event_banner', click=True):
        while battlecounter < battles:
            click('buttons/challenge_tr', confidence=0.8, suppress=True, retry=3, seconds=7)
            # Place cards 1-2, click ready
            while not isVisible('labels/battleofblood_stage1', region=(465, 20, 150, 55)):
                wait(1)
                bob_timeout += 1
                if bob_timeout > 30:
                    printError('Battle of Blood timeout!')
                    recover()
                    return
            else:
                wait(4) # For the card animations
                bob_timeout = 0 # reset timer
                clickXY(550, 1250, seconds=1)
                clickXY(350, 1250, seconds=1)
                clickXY(550, 1850, seconds=1)
            if isVisible('buttons/confirm_small', retry=3, region=(600, 1220, 200, 80)):
                clickXY(325, 1200)
                clickXY(700, 1270)
            # Place cards 3-4, click ready
            while not isVisible('labels/battleofblood_stage2', region=(465, 20, 150, 55)):
                wait(1)
                bob_timeout += 1
                if bob_timeout > 30:
                    printError('Battle of Blood timeout!')
                    recover()
                    return
            else:
                wait(4) # For the card animations
                bob_timeout = 0 # reset timer
                clickXY(550, 1250, seconds=1)
                clickXY(350, 1250, seconds=1)
                clickXY(550, 1850, seconds=1)
            # Place card 5, click ready
            while not isVisible('labels/battleofblood_stage3', region=(465, 20, 150, 55), confidence=0.95): # higher confidence so we don't get confused with battleofblood_stage2.png
                wait(1)
                bob_timeout += 1
                if bob_timeout > 30:
                    printError('Battle of Blood timeout!')
                    recover()
                    return
            else:
                wait(4) # For the card animations
                bob_timeout = 0 # reset timer
                clickXY(550, 1250, seconds=1)
                clickXY(550, 1850, seconds=8)
                # Return Battle Report
                battlecounter += 1
                result = returnBattleResults('BoB')
                if result is True:
                    printGreen('    Victory! Battle of Blood Battle #' + str(battlecounter) + ' complete')
                else:
                    printError('    Defeat! Battle of Blood Battle #' + str(battlecounter) + ' complete')
        # Click quests
        wait(2) # wait for animations to settle from exting last battle
        clickXY(150, 230, seconds=2)
        # select dailies tab
        clickXY(650, 1720, seconds=1)
        # Collect Dailies
        clickXY(850, 720, seconds=3)
        clickXY(920, 525, seconds=2)
        clickXY(920, 525, seconds=2)
        # clear loot
        clickXY(550, 250, seconds=2)
        # Back twice to exit
        clickXY(70, 1810, seconds=1) # Exit Quests
        clickXY(70, 1810, seconds=1) # Exit BoB
        clickXY(70, 1810, seconds=1) # Exit Events screen
        if confirmLocation('ranhorn', bool=True, region=boundaries['ranhornSelect']):
            printGreen('    Battle of Blood attempted successfully')
        else:
            printWarning('Issue exiting Battle of Blood, recovering..')
            recover()
    else:
        printWarning('Battle of Blood not found, recovering..')
        recover()

def handleCircusTour(battles = 3):
    battlecounter = 1
    printBlue('Attempting to run Circus Tour battles')
    confirmLocation('ranhorn', region=boundaries['ranhornSelect']) # Trying to fix 'buttons/events not found' error
    expandMenus() # Expand left menu again as it can shut after other dailies activities
    click('buttons/events', confidence=0.8, retry=3, seconds=3)
    if isVisible('labels/circustour', retry=3, click=True):
        while battlecounter < battles:
            printGreen('    Circus Tour battle #' + str(battlecounter))
            click('buttons/challenge_tr', confidence=0.8, retry=3, suppress=True, seconds=3)
            if battlecounter == 1:
                # If Challenge is covered by text we clear it
                while isVisible('labels/dialogue_left', retry=2, region=boundaries['dialogue_left']):
                    printWarning('    Clearing dialogue..')
                    clickXY(550, 900) # Clear dialogue box on new boss rotation
                    clickXY(550, 900) # Only need to do this on the first battle
                    clickXY(550, 900)
                    clickXY(550, 900)
                    clickXY(550, 900)
                    clickXY(550, 900, seconds=2)
                    click('buttons/challenge_tr', confidence=0.8, retry=3, suppress=True, seconds=3)
            click('buttons/battle_large', confidence=0.8, retry=3, suppress=True, seconds=5)
            click('buttons/skip', confidence=0.8, retry=5, seconds=5)
            clickXY(550, 1800) # Clear loot
            battlecounter += 1
        wait(3)
        clickXY(500, 1600) # First chest
        clickXY(500, 1600) # Twice to clear loot popup
        clickXY(900, 1600) # Second chest
        clickXY(900, 1600) # Twice to clear loot popup
        # Back twice to exit
        clickXY(70, 1810, seconds=1)
        clickXY(70, 1810, seconds=1)
        if confirmLocation('ranhorn', bool=True, region=boundaries['ranhornSelect']):
            printGreen('    Circus Tour attempted successfully')
        else:
            printWarning('Issue exiting Circus Tour, recovering..')
            recover()
    else:
        printWarning('Circus Tour not found, recovering..')
        recover()

def handleLab():
    printBlue('Attempting to run Arcane Labyrinth')
    lowerdirection = '' # for whether we go left or right for the first battle
    upperdirection = '' # For whether we go left or right to get the double battle at the end
    confirmLocation('darkforest', region=boundaries['darkforestSelect'])
    wait()
    clickXY(400, 1150, seconds=3)
    if isVisible('labels/labfloor3', retry=3, confidence=0.8, seconds=3):
        printGreen('Lab already open! Continuing..')
        clickXY(50, 1800, seconds=2)  # Exit Lab Menu
        return
    if isVisible('labels/lablocked', confidence=0.8, seconds=3):
        printGreen('Dismal Lab not unlocked! Continuing..')
        clickXY(50, 1800, seconds=2)  # Exit Lab Menu
        return
    if isVisible('labels/lab', retry=3):
        # Check for Swept
        if isVisible('labels/labswept', retry=3, confidence=0.8, seconds=3):
            printGreen('Lab already swept! Continuing..')
            clickXY(50, 1800, seconds=2)  # Exit Lab Menu
            return
        # Check for Sweep
        if isVisible('buttons/labsweep', retry=3, confidence=0.8, click=True, seconds=3):
            printGreen('    Sweep Available!')
            if isVisible('buttons/labsweepbattle', retry=3, confidence=0.8, click=True, seconds=3):
                clickXY(720, 1450, seconds=3) # Click Confirm
                clickXY(550, 1550, seconds=3) # Clear Rewards
                if isVisible('labels/notice', retry=3, seconds=3):  # And again for safe measure
                    clickXY(550, 1250)
                clickXY(550, 1550, seconds=5) # Clear Roamer Deals, long wait for the Limited Offer to pop up for Lab completion
                clickXY(550, 1650) # Clear Limited Offer
                printGreen('    Lab Swept!')
                return
        else: # Else we run lab manually
            printGreen('    Sweep not found, attempting manual Lab run..')

            # Pre-run set up
            printGreen('    Entering Lab')
            clickXY(750, 1100, seconds=2) # Center of Dismal
            clickXY(550, 1475, seconds=2) # Challenge
            clickXY(550, 1600, seconds=2) # Begin Adventure
            clickXY(700, 1250, seconds=6) # Confirm
            clickXY(550, 1600, seconds=3) # Clear Debuff
            # TODO Check Dismal Floor 1 text
            printGreen('    Sweeping to 2nd Floor')
            clickXY(950, 1600, seconds=2) # Level Sweep
            clickXY(550, 1550, seconds=8) # Confirm, long wait for animations
            clickXY(550, 1600, seconds=2) # Clear Resources Exceeded message
            clickXY(550, 1600, seconds=2) # And again for safe measure
            clickXY(550, 1600, seconds=3) # Clear Loot
            clickXY(550, 1250, seconds=5) # Abandon Roamer
            printGreen('    Choosing relics')
            clickXY(550, 900) # Relic 1
            clickXY(550, 1325, seconds=3) # Choose
            clickXY(550, 900) # Relic 2
            clickXY(550, 1325, seconds=3) # Choose
            clickXY(550, 900) # Relic 3
            clickXY(550, 1325, seconds=3) # Choose
            clickXY(550, 900) # Relic 4
            clickXY(550, 1325, seconds=3) # Choose
            clickXY(550, 900) # Relic 5
            clickXY(550, 1325, seconds=3) # Choose
            clickXY(550, 900) # Relic 6
            clickXY(550, 1325, seconds=3) # Choose
            printGreen('    Entering 3rd Floor')
            clickXY(550, 550, seconds=2) # Portal to 3rd Floor
            clickXY(550, 1200, seconds=5) # Enter
            clickXY(550, 1600, seconds=2) # Clear Debuff
            # TODO Check Dismal Floor 3 text

            # Check which route we are taking, as to avoid the cart
            clickXY(400, 1400, seconds=2) # Open first tile on the left
            if isVisible('labels/labguard', retry=2):
                printWarning('    Loot Route: Left')
                lowerdirection = 'left'
            else:
                printWarning('    Loot Route: Right')
                lowerdirection = 'right'
                clickXY(550, 50, seconds=3)  # Back to Lab screen

            # 1st Row (single)
            handleLabTile('lower', lowerdirection, '1')
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                configureLabTeams(1)
                clickXY(550, 1850, seconds=4)  # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab') is False:
                return

            # 2nd Row (multi)
            handleLabTile('lower', lowerdirection, '2')
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab', firstOfMulti=True) is False:
                return
            clickXY(750, 1725, seconds=4) # Continue to second battle
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                configureLabTeams(2)
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab') is False:
                return

            # 3rd Row (single relic)
            handleLabTile('lower', lowerdirection, '3')
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab') is False:
                return
            clickXY(550, 1350, seconds=2) # Clear Relic reward

            # 4th Row (multi)
            handleLabTile('lower', lowerdirection, '4')
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab', firstOfMulti=True) is False:
                return
            clickXY(750, 1725, seconds=4) # Continue to second battle
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab') is False:
                return

            # 5th Row (single)
            handleLabTile('lower', lowerdirection, '5')
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab') is False:
                return

            # 6th Row (single relic)
            handleLabTile('lower', lowerdirection, '6')
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab') is False:
                return
            clickXY(550, 1350, seconds=2) # Clear Relic reward

            # Check which route we are taking for the upper tiles
            swipe(550, 200, 550, 1800, duration=1000)
            clickXY(400, 1450, seconds=2) # First tile on the left
            if isVisible('labels/labpraeguard', retry=2):
                printWarning('    Loot Route: Left')
                upperdirection = 'left'
            else:
                printWarning('    Loot Route: Right')
                upperdirection = 'right'
                clickXY(550, 50, seconds=2)  # Back to Lab screen

            # 7th Row (multi)
            handleLabTile('upper', upperdirection, '7')
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab', firstOfMulti=True) is False:
                return
            clickXY(750, 1725, seconds=4) # Continue to second battle
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab') is False:
                return

            # 8th Row (multi)
            handleLabTile('upper', upperdirection, '8')
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab', firstOfMulti=True) is False:
                return
            clickXY(750, 1725, seconds=4) # Continue to second battle
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                # configureLabTeams(2, pet=False)  # We've lost heroes to Thoran etc by now, so lets re-pick 5 strongest heroes
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab') is False:
                return

            # 9th Row (witches den or fountain)
            handleLabTile('upper', upperdirection, '9')
            if isVisible('labels/labwitchsden', retry=3):
                printWarning('    Clearing Witch\'s Den')
                clickXY(550, 1500, seconds=3)  # Go
                clickXY(300, 1600, seconds=4)  # Abandon
            if isVisible('labels/labfountain', retry=3):
                printWarning('    Clearing Divine Fountain')
                clickXY(725, 1250, seconds=3)  # Confirm
                clickXY(725, 1250, seconds=2) # Go

            # 10th row (single boss)
            handleLabTile('upper', upperdirection, '10')
            if isVisible('buttons/heroclassselect', retry=3):  # Check we're at the battle screen
                configureLabTeams(1, pet=False) # We've lost heroes to Thoran etc by now, so lets re-pick 5 strongest heroes
                clickXY(550, 1850, seconds=4) # Battle
            else:
                printError('Battle Screen not found! Exiting')
                recover()
                return
            if returnBattleResults(type='lab') is False:
                return

            wait(6) # Long pause for Value Bundle to pop up
            clickXY(550, 1650, seconds=3) # Clear Value Bundle for completing lab
            clickXY(550, 550, seconds=3) # Loot Chest
            clickXY(550, 1650, seconds=2) # Clear Loot
            clickXY(550, 1650, seconds=2) # Clear Notice
            clickXY(550, 1650, seconds=2) # One more for safe measure
            clickXY(50, 1800, seconds=2) # Click Back to Exit
            printGreen("    Manual Lab run complete!")
    else:
        printError("Can't find Lab screen! Exiting..")
        recover()

# Clears selected team and replaces it with top5 heroes, and 6th-10th for team2, selects pets from the first and second slots
def configureLabTeams(team, pet=True):
    if team == 1:
        clickXY(1030, 1100, seconds=2)  # Clear Team
        clickXY(550, 1250, seconds=2)  # Confirm
        clickXY(930, 1300)  # Slot 5 (Reverse order as our top heroes tend to be squishy so they get back line)
        clickXY(730, 1300)  # Slot 4
        clickXY(530, 1300)  # Slot 3
        clickXY(330, 1300)  # Slot 2
        clickXY(130, 1300)  # Slot 1
        if pet is True:
            if isVisible('buttons/pet_empty', confidence=0.75, retry=3, click=True, region=(5, 210, 140, 100)):
                clickXY(150, 1250, seconds=2) # First Pet
                clickXY(750, 1800, seconds=4) # Confirm
    if team == 2:
        clickXY(1030, 1100, seconds=2)  # Clear Team
        clickXY(550, 1250, seconds=2)  # Confirm
        clickXY(130, 1550)  # Slot 1
        clickXY(330, 1550)  # Slot 2
        clickXY(530, 1550)  # Slot 3
        clickXY(730, 1550)  # Slot 4
        clickXY(930, 1550)  # Slot 5
        if pet is True:
            if isVisible('buttons/pet_empty', confidence=0.75, retry=3, click=True, region=(5, 210, 140, 100)):
                clickXY(350, 1250, seconds=2) # Second Pet
                clickXY(750, 1800, seconds=4) # Confirm

# Will select the correct Lab tile and take us to the battle screen
# Elevation is either Upper or Lower dependon on whether we have scrolled the screen up or not for the scond half
# Side is left or right, we choose once at the start and once after scrolling up to get both multi fights
# Tile is the row of the tile we're aiming for, from 1 at the bottom to 10 at the final boss
def handleLabTile(elevation, side, tile):
    if tile == '4' or tile == '6' or tile == '10':
        printBlue('    Battling ' + elevation.capitalize() + ' Tile ' + tile)
    else:
        printBlue('    Battling ' + elevation.capitalize() + ' ' + side.capitalize() + ' Tile ' + tile)
    wait(1)
    if elevation == 'lower':
        if side == 'left':
            if tile == '1': # Single
                clickXY(400, 1450, seconds=2) # Tile
                clickXY(550, 1500, seconds=4)  # Go
            if tile == '2': # Multi
                clickXY(250, 1250, seconds=2) # Tile
                clickXY(550, 1500, seconds=4) # Click Go
                if isVisible('labels/notice', confidence=0.8, retry=3): # 'High Difficulty popup at first multi'
                    clickXY(450, 1150, seconds=2)  # Don't show this again
                    clickXY(725, 1250, seconds=4)  # Go
                clickXY(750, 1500, seconds=4) # Click Begin Battle
            if tile == '3': # Single
                clickXY(400, 1050, seconds =2) # Tile
                clickXY(550, 1600, seconds=4)  # Go (lower for relic)
            if tile == '4': # Multi
                clickXY(550, 850, seconds=2) # Tile
                clickXY(550, 1500, seconds=4) # Click Go
                clickXY(750, 1500, seconds=4) # Click Begin Battle
            if tile == '5': # Single
                clickXY(400, 650, seconds=2) # Tile
                clickXY(550, 1500, seconds=4)  # Go
            if tile == '6': # Single
                clickXY(550, 450, seconds=2) # Tile
                clickXY(550, 1600, seconds=4)  # Go (lower for relic)
        if side == 'right':
            if tile == '1': # Single
                clickXY(700, 1450, seconds=2) # Tile
                clickXY(550, 1500, seconds=4)  # Go
            if tile == '2': # Multi
                clickXY(800, 1225, seconds=2) # Tile
                clickXY(550, 1500, seconds=4) # Click Go
                if isVisible('labels/notice', confidence=0.8, retry=3): # 'High Difficulty popup at first multi'
                    clickXY(450, 1150, seconds=2)  # Don't show this again
                    clickXY(725, 1250, seconds=4)  # Go
                clickXY(750, 1500, seconds=4) # Click Begin Battle
            if tile == '3': # Single
                clickXY(700, 1050, seconds=2) # Tile
                clickXY(550, 1600, seconds=4)  # Go (lower for relic)
            if tile == '4': # Multi
                clickXY(550, 850, seconds=2) # Tile
                clickXY(550, 1500, seconds=4) # Click Go
                clickXY(750, 1500, seconds=4) # Click Begin Battle
            if tile == '5': # Single
                clickXY(700, 650, seconds=2) # Tile
                clickXY(550, 1500, seconds=4)  # Go
            if tile == '6':
                clickXY(550, 450, seconds=2) # Tile
                clickXY(550, 1600, seconds=4)  # Go (lower for relic)
    if elevation == 'upper':
        if side == 'left':
            if tile == '7': # Multi
                clickXY(400, 1450, seconds=2) # Tile
                # No Go as we opened the tile to check direction
                clickXY(750, 1500, seconds=4) # Click Begin Battle
            if tile == '8': # Multi
                clickXY(250, 1250, seconds=2) # Tile
                clickXY(550, 1500, seconds=4)  # Go
                clickXY(750, 1500, seconds=4) # Click Begin Battle
            if tile == '9':  # Witches Den or Well
                clickXY(400, 1100, seconds=2)  # Tile
            if tile == '10': # Single
                clickXY(550, 900, seconds=2) # Tile
                clickXY(550, 1500, seconds=4)  # Go
        if side == 'right':
            if tile == '7': # Multi
                clickXY(700, 1450, seconds=2) # Tile
                clickXY(550, 1500, seconds=4) # Go
                clickXY(750, 1500, seconds=4) # Click Begin Battle
            if tile == '8': # Multi
                clickXY(800, 1225, seconds=2) # Tile
                clickXY(550, 1500, seconds=4)  # Go
                clickXY(750, 1500, seconds=4) # Click Begin Battle
            if tile == '9':  # Witches Den or Well
                clickXY(700, 1100, seconds=2)  # Tile
            if tile == '10': # Single
                clickXY(550, 850, seconds=2) # Tile
                clickXY(550, 1500, seconds=4)  # Go

# Returns result of a battle, diferent types for the different types of post-battle screens, count for number of battles in Arena
# firstOfMulti is so we don't click to clear loot after a lab battle, which would exit us from the battle screen for the second fight
def returnBattleResults(type, firstOfMulti=False):
    counter = 0

    if type == 'BoB':
        while counter < 30:
            if isVisible('labels/victory'):
                # printGreen('    Battle of Blood Victory!')
                clickXY(550, 1850, seconds=3)  # Clear window
                return True
            if isVisible('labels/defeat'):
                # printError('    Battle of Blood Defeat!')
                clickXY(550, 1850, seconds=3)  # Clear window
                return False
            counter += 1
        printError('Battletimer expired')
        recover()
        return False

    # Here we don't clear the result by clicking at the bottom as there is the battle report there
    if type == 'HoE':
        while counter < 10:
            # Clear Rank Up message
            if isVisible('labels/hoe_ranktrophy', retry=5, region=(150, 900, 350, 250)):
                clickXY(550, 1200)
            if isVisible('labels/victory'):
                # printGreen('    Battle of Blood Victory!')
                clickXY(550, 700, seconds=3)  # Clear window
                return True
            if isVisible('labels/defeat'):
                # printError('    Battle of Blood Defeat!')
                clickXY(550, 700, seconds=3)  # Clear window
                return False
            counter += 1
        printError('Battletimer expired')
        return False

    if type == 'lab':
        while counter < 15:
            # For 'resources exceeded' message
            if isVisible('labels/notice'):
                clickXY(550, 1250)
            if isVisible('labels/victory'):
                printGreen('    Lab Battle Victory!')
                if firstOfMulti is False:  # Else we exit before second battle while trying to collect loot
                    clickXY(550, 1850, seconds=5)  # Clear loot popup and wait for Lab to load again
                return
            if isVisible('labels/defeat'):
                # TODO Use Duras Tears so we can continue
                printError('    Lab Battle  Defeat! Exiting..')
                recover()
                return False
            counter += 1
        printError('Battletimer expired')
        recover()
        return False

    if type == 'arena':
        while counter < 10:
            if isVisible('labels/rewards'):
                return True
            if isVisible('labels/defeat'):
                return False
            wait(1)
            counter += 1
        printError('Arena battle timed out!')
        return False

    if type == 'campaign':
        if isVisible('labels/victory', confidence=0.75, retry=2):
            printGreen('    Victory!')
            return True
        elif isVisible('labels/defeat', confidence=0.8):
            printError('    Defeat!')
            return False
        else:
            return 'Unknown'

def handleHeroesofEsperia(count=3, opponent=4):
    counter = 0
    errorcounter = 0
    printBlue('Battling Heroes of Esperia ' + str(count) + ' times')
    printWarning('Note: this currently won\'t work in the Legends Tower')
    confirmLocation('darkforest', region=boundaries['darkforestSelect'])
    clickXY(740, 1050) # Open Arena of Heroes
    clickXY(550, 50) # Clear Tickets Popup
    if isVisible('labels/heroesofesperia', click=True, seconds=3):
        # Check if we've opened it yet
        if isVisible('buttons/join_hoe', 0.8, retry=3, region=(420, 1780, 250, 150)):
            printWarning('Heroes of Esperia not opened! Entering..')
            clickXY(550, 1850) # Clear Info
            clickXY(550, 1850, seconds=6) # Click join
            clickXY(550, 1140, seconds=3) # Clear Placement
            clickXY(1000, 1650, seconds=8) # Collect all and wait for scroll
            clickXY(550, 260, seconds=5) # Character portrait to clear Loot
            clickXY(550, 260, seconds=5) # Character portrait to scroll back up
        # Start battles
        if isVisible('buttons/fight_hoe', retry=10, seconds=3, click=True, region=(400, 200, 400, 1500)):
            while counter < count:
                selectOpponent(choice=opponent, hoe=True)
                if isVisible('labels/hoe_buytickets', region=(243, 618, 600, 120)): # Check for ticket icon pixel
                    printError('Ticket Purchase screen found, exiting')
                    recover()
                    return
                while isVisible('buttons/heroclassselect', region=boundaries['heroclassselect']): # This is rather than Battle button as that is animated and hard to read
                    clickXY(550, 1800, seconds=0)
                clickWhileVisible('buttons/skip', confidence=0.8, region=boundaries['skipAoH'])
                if returnBattleResults(type='HoE'):
                    printGreen('    Battle #' + str(counter + 1) + ' Victory!')
                else:
                    printError('    Battle #' + str(counter + 1) + ' Defeat!')

                # Lots of things/animations can happen after a battle so we keep clicking until we see the fight button again
                while not isVisible('buttons/fight_hoe', seconds=3, click=True, region=(400, 200, 400, 1500)):
                    if errorcounter < 6:
                        clickXY(420, 50)  # Neutral location
                        clickXY(550, 1420)  # Rank up confirm button
                        errorcounter += 1
                    else:
                        printError('Something went wrong post-battle, recovering')
                        recover()
                        return
                errorcounter = 0
                counter += 1
        else:
            printError('Heroes of Esperia Fight button not found! Recovering')
            recover()
            return
        click('buttons/exitmenu', region=boundaries['exitAoH'])
        printGreen('    Collecting Quests')
        clickXY(975, 300, seconds=2) # Bounties
        clickXY(975, 220, seconds=2) # Quests
        clickXY(850, 880, seconds=2) # Top daily quest
        clickXY(550, 420, seconds=2) # Click to clear loot
        clickXY(870, 1650, seconds=2) # Season quests tab
        clickXY(850, 880, seconds=2) # Top season quest
        clickXY(550, 420, seconds=2) # Click to clear loot
        click('buttons/exitmenu', region=boundaries['exitAoH'], seconds=2)
        if pixelCheck(550, 1850, 2) > 150:
            printGreen('    Collecting Heroes of Esperia Pass loot')
            clickXY(550, 1800, seconds=2) # Collect all at the pass screen
            clickXY(420, 50) # Click to clear loot
        click('buttons/back', retry=3, region=boundaries['backMenu'])
        click('buttons/back', retry=3, region=boundaries['backMenu'])
        click('buttons/back', retry=3, region=boundaries['backMenu'])
        printGreen('    Heroes of Esperia battles complete')
    else:
        printError('Heroes of Esperia not found, attempting to recover')
        recover()
        
def afkjourney():
    Popen(['adb', 'shell', 'am', 'force-stop', 'com.lilithgame.hgame.gp'])
    afkjourney_cmd = config.get('ADVANCED', 'afkjourney_cmd')

    # Split the string by spaces
    cmd_parts = shlex.split(afkjourney_cmd)

    # Extract the file path
    file_path = cmd_parts[2]

    # Check if the file exists
    if os.path.exists(file_path):
        print('')
        printBlue('Attempting to run AFK Journey dailies')
        process = Popen(config.get('ADVANCED', 'afkjourney_cmd'), stdout=PIPE, text=True)
        for line in process.stdout:
            if line.strip():  # Check if the line is not empty
                printInfo(line)
        process.wait()
        printGreen('AFK Journey dailies done!')  