"""Tower and Twisted Realm activities"""
import logging
import datetime
from src.activities.base_activity import BaseActivity

logger = logging.getLogger(__name__)


class TowerActivities(BaseActivity):
    """Handles tower and twisted realm activities"""
    
    def handle_kings_tower(self) -> bool:
        """Attempt King's Tower battle"""
        logger.blue("Attempting King's Tower battle...")
        
        self.controller.confirm_location('darkforest', 
                                        region=self.controller.BOUNDARIES['darkforestSelect'])
        self.controller.tap(500, 870)  # Long pause for animation
        
        # Wait for tower screen (max 3s)
        if self.image.wait_for_image('labels/kingstower', timeout=3, check_interval=0.3):
            self.controller.tap(555, 585)
            self.image.click_image('buttons/challenge_plain', confidence=0.7, retry=5, 
                                  suppress=True, seconds=5, retry_interval=0.3)
            
            # Begin battle button (sometimes 'beginbattle', sometimes 'begin')
            self.controller.tap(700, 1850, seconds=2)
            
            # Exit battle
            self.image.click_image('buttons/pause', confidence=0.8, retry=5, suppress=True,
                                  retry_interval=0.3)
            self.image.click_image('buttons/exitbattle')
            self.image.click_image('buttons/back', retry=3, 
                                  region=self.controller.BOUNDARIES['backMenu'])
            self.image.click_image('buttons/back', retry=3, 
                                  region=self.controller.BOUNDARIES['backMenu'])
            
            # Last back only needed for multifights
            if self.image.is_visible('buttons/back', retry=3, 
                                    region=self.controller.BOUNDARIES['backMenu']):
                self.image.click_image('buttons/back', 
                                      region=self.controller.BOUNDARIES['backMenu'])
                
            logger.green("Tower attempted successfully")
            return True
        else:
            logger.error("Tower screen not found")
            self.controller.recover()
            return False
    
    def handle_twisted_realm(self) -> bool:
        """Attempt Twisted Realm battle"""
        logger.blue("Attempting to run Twisted Realm")
        
        self.controller.confirm_location('ranhorn', 
                                        region=self.controller.BOUNDARIES['ranhornSelect'])
        self.controller.tap(380, 360, seconds=6)
        self.controller.tap(550, 1800)  # Clear chests
        self.controller.tap(775, 875, seconds=2)
        self.controller.tap(550, 600, seconds=3)
        
        if self.image.is_visible('buttons/nextboss'):
            logger.green("    Twisted Realm found, battling")
            
            if self.image.is_visible('buttons/challenge_tr', retry=5, confidence=0.8, 
                                    suppress=True):
                self.controller.tap(550, 1850, seconds=2)
                self.image.click_image('buttons/autobattle', retry=5, seconds=3, 
                                      suppress=True)
                
                if self.image.is_visible('buttons/checkbox_blank'):
                    self.controller.tap(300, 975)  # Activate Skip Battle Animations
                    
                self.controller.tap(700, 1300, seconds=6)
                self.controller.tap(550, 1300)
                self.controller.tap(550, 1800)
                self.controller.tap(70, 1800)
                self.controller.tap(70, 1800)
                self.controller.tap(70, 1800)
                
                logger.green("    Twisted Realm attempted successfully")
                self.wait(3)  # wait before next task as loading ranhorn can be slow
                self.controller.recover(silent=True)
            else:
                self.controller.tap(70, 1800)
                self.controller.tap(70, 1800)
                logger.warning("    Challenge button not found, attempting to recover")
                self.controller.recover()
        else:
            logger.warning("    Error opening Twisted Realm, attempting to recover")
            # TODO Add 'Calculating' confirmation to exit safely
            self.controller.recover()
    
    def push_tower(self, tower: str, formation: int = 3, duration: int = 1,
                  pause_event=None, stop_event=None) -> bool:
        """Push specific tower
        
        Args:
            tower: Tower name
            formation: Formation number (1-5)
            duration: Minutes to wait between victory checks
            pause_event: Event to pause execution
            stop_event: Event to stop execution
        """
        logger.blue(f"Pushing {tower} tower (formation {formation})...")
        
        # Open tower
        tower_open = False
        
        # Start pushing loop
        start_time = datetime.datetime.now()
        
        while True:
            # Open tower if needed
            if not tower_open:
                if not self._open_tower(tower):
                    return False
                tower_open = True
                
                # Check if tower has floors available
                if (not self.image.is_visible('buttons/challenge_plain', confidence=0.8, retry=3, seconds=2) and
                    self.image.is_visible('labels/tower_screen', suppress=True)):
                    logger.warning("No floors available, exiting...")
                    return False
            
            # Change formation every x minutes if enabled
            cycle_minutes = self.config.getint('PUSH', 'cycleformation', fallback=0)
            if cycle_minutes > 0:
                if datetime.datetime.now() - start_time >= datetime.timedelta(minutes=cycle_minutes):
                    formation += 1
                    if formation > 5:
                        formation = 1
                    logger.warning(f"Cycling to formation {formation} (every {cycle_minutes}min)")
                    self.controller.tap(550, 800)
                    self.controller.tap(550, 800)  # Click to prompt AutoBattle popup
                    self.image.click_image('buttons/exit', suppress=True, retry=3)
                    start_time = datetime.datetime.now()  # Reset formation timer
            
            # Two checks for buttons - check for two positives in a row
            # Challenge button (tower screen)
            challengetimer = 0
            autobattletimer = 0
            
            while self.image.is_visible('buttons/challenge_plain', confidence=0.8, retry=3, seconds=2,
                                       region=(356, 726, 364, 1024)):
                challengetimer += 1
                if challengetimer >= 2:
                    self.image.click_image('buttons/challenge_plain', confidence=0.8, retry=3, seconds=3,
                                          region=(356, 726, 364, 1024))
                    self._configure_battle_formation(formation)
                    challengetimer = 0
            
            # Autobattle button (hero selection screen)
            while self.image.is_visible('buttons/autobattle', confidence=0.92, retry=3, seconds=2,
                                       region=(214, 1774, 256, 112)):
                autobattletimer += 1
                if autobattletimer >= 2:
                    self._configure_battle_formation(formation)
                    autobattletimer = 0
            
            # Wait for duration (minus time for configuring)
            self.wait((duration * 60) - 50)
            
            # Check for stop/pause after wait
            if stop_event and stop_event.is_set():
                logger.blue("Stop requested, ending push")
                tower_open = False
                break
            if pause_event and pause_event.is_set():
                logger.blue("Paused...")
                pause_event.wait()
            
            # Check autobattle counter
            if (self.image.is_visible('labels/autobattle_0', retry=3, suppress=True,
                                     region=(730, 1600, 50, 50)) or
                self.image.is_visible('labels/autobattle_0_hidden', retry=3, suppress=True,
                                     region=(730, 1600, 50, 50))):
                # No victory found
                if not self.config.getboolean('PUSH', 'suppressSpam', fallback=False):
                    logger.warning(f"No victory found, checking again in {duration} minutes")
            else:
                # Victory found! (autobattle counter is not 0)
                self.wait(2)
                self.controller.tap(300, 50)  # Close offer popup
                self.controller.tap(550, 800)
                self.controller.tap(550, 800)  # Click to prompt AutoBattle popup
                
                if self.image.is_visible('labels/autobattle_tower'):
                    logger.green("Victory found! Loading formation for current stage...")
                    self.image.click_image('buttons/exit', suppress=True, retry=3, seconds=2)
                    self.controller.tap(550, 1750)  # Clear Limited Rewards popup (every 20 stages)
                    start_time = datetime.datetime.now()  # Reset timer
                elif not self.image.is_visible('buttons/pause', retry=3, 
                                               region=(24, 1419, 119, 104)):
                    # Something went wrong
                    logger.error("AutoBattle screen not found, reloading auto-push...")
                    if self.controller.recover():
                        # Reopen tower
                        tower_open = False
                    else:
                        return False
        
        logger.green("Tower push complete")
        return True
        
    def _open_tower(self, tower: str) -> bool:
        """Open specific tower"""
        self.controller.confirm_location('darkforest', 
                                        region=self.controller.BOUNDARIES['darkforestSelect'])
        self.wait(3)  # Medium wait to make sure tower button is active
        self.controller.tap(500, 870, seconds=3)  # Long pause for animation opening towers
        
        # Wait for tower screen (max 3s)
        if self.image.is_visible('labels/kingstower', retry=3, confidence=0.85,
                                region=self.controller.BOUNDARIES['kingstowerLabel']):
            # Map full tower names to short names
            tower_name_map = {
                "King's Tower": 'kings',
                'Lightbearer Tower': 'lightbearer',
                'Mauler Tower': 'mauler',
                'Wilder Tower': 'wilder',
                'Graveborn Tower': 'graveborn',
                'Celestial Tower': 'celestial',
                'Hypogean Tower': 'hypogean'
            }
            
            # Convert to short name if needed
            tower_key = tower_name_map.get(tower, tower.lower())
            
            # Select tower (positions from old version)
            tower_positions = {
                'kings': (500, 870),
                'lightbearer': (300, 1000),
                'mauler': (400, 1200),
                'wilder': (800, 600),
                'graveborn': (800, 1200),
                'celestial': (300, 500),
                'hypogean': (600, 1500)
            }
            
            if tower_key in tower_positions:
                x, y = tower_positions[tower_key]
                self.controller.tap(x, y, seconds=3)
                return True
            else:
                logger.error(f"Unknown tower: {tower}")
                return False
        else:
            logger.error("Tower screen not found")
            self.controller.recover()
            return False
    
    def _configure_battle_formation(self, formation: int):
        """Configure battle formation and start autobattle"""
        artifacts = None
        counter = 0
        
        if self.config.getboolean('ADVANCED', 'ignoreformations', fallback=False):
            logger.warning("ignoreformations enabled, skipping formation selection")
            self.image.click_image('buttons/autobattle', suppress=True, retry=3,
                                  region=(214, 1774, 256, 112))
            self.image.click_secure('buttons/activate', 'labels/autobattle',
                                   region=(580, 1208, 300, 150),
                                   secure_region=(200, 578, 684, 178))
            return
        elif self.image.is_visible('buttons/formations', region=(914, 1762, 102, 134), click=True, seconds=3, retry=5):
            
            if self.config.getboolean('ADVANCED', 'popularformations', fallback=False):
                self.controller.tap(800, 1650, seconds=2)  # Change to 'Popular' tab
                
            self.controller.tap(850, 425 + (formation * 175), seconds=2)
            self.image.click_image('buttons/use', retry=5, seconds=2, suppress=True)
            
            # Configure Artifacts
            while artifacts is None and counter <= 5:
                artifacts = self.image.is_visible('buttons/checkbox_checked',
                                                 region=(230, 1100, 80, 80), suppress=True)
                counter += 1
                
            if counter >= 5:
                logger.error("Couldn't read artifact status")
                
            if artifacts is not None and artifacts != self.config.getboolean('PUSH', 'useartifacts', fallback=False):
                self.controller.tap(275, 1150)
                
            self.image.click_image('buttons/confirm_small', retry=3,
                                  region=(600, 1220, 250, 100), suppress=True)
            self.image.click_image('buttons/autobattle', retry=3,
                                  region=(214, 1774, 256, 112), seconds=2, suppress=True)
            self.image.click_image('buttons/confirm', seconds=2, retry=5, suppress=True)
            self.image.click_image('buttons/confirm_campaign', seconds=2, retry=2, suppress=True)
        elif self.image.is_visible('labels/tower_no_attempts'):
            logger.warning("No attempts left for this tower, exiting...")
            import sys
            sys.exit(0)
        else:
            logger.warning("Could not find Formations button")


class TowerPusher:
    """Tower pushing automation class"""
    
    def __init__(self, device_manager, image_recognition, game_controller, config, notification_manager):
        self.device_manager = device_manager
        self.image = image_recognition
        self.controller = game_controller
        self.config = config
        self.notification_manager = notification_manager
        self.tower_activities = TowerActivities(device_manager, image_recognition, 
                                               game_controller, config, notification_manager)
        
        # Import CampaignActivities for push_campaign
        from src.activities.campaign_activities import CampaignActivities
        self.campaign_activities = CampaignActivities(device_manager, image_recognition,
                                                     game_controller, config, notification_manager)
        
    def push_tower(self, tower: str, formation: int = 3, duration: int = 1,
                  pause_event=None, stop_event=None):
        """Push tower wrapper"""
        if self.notification_manager:
            self.notification_manager.send(f"🗼 Starting tower push: {tower}", level='INFO')
        
        result = self.tower_activities.push_tower(tower, formation, duration,
                                                 pause_event, stop_event)
        
        if result and self.notification_manager:
            self.notification_manager.send(f"✅ Tower push complete: {tower}", level='INFO')
        elif not result and self.notification_manager:
            self.notification_manager.send(f"❌ Tower push failed: {tower}", level='ERROR')
        
        return result
    
    def push_campaign(self, formation: int = 3, duration: int = 1,
                     pause_event=None, stop_event=None):
        """Push campaign wrapper"""
        return self.campaign_activities.push_campaign(formation, duration,
                                                      pause_event, stop_event)


