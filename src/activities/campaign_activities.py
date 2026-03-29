"""Campaign pushing activities"""
import logging
import datetime
from src.activities.base_activity import BaseActivity

logger = logging.getLogger(__name__)


class CampaignActivities(BaseActivity):
    """Handles campaign pushing"""
    
    def push_campaign(self, formation: int = 3, duration: int = 1, 
                     pause_event=None, stop_event=None) -> bool:
        """Auto push campaign stages
        
        Args:
            formation: Formation number (1-5)
            duration: Minutes to wait between victory checks
            pause_event: Event to pause execution
            stop_event: Event to stop execution
        """
        logger.blue(f"Pushing campaign (formation {formation})...")
        
        self.controller.confirm_location('campaign', 
                                        region=self.controller.BOUNDARIES['campaignSelect'])
        
        # Start pushing loop
        start_time = datetime.datetime.now()
        
        while True:
            # Click begin if visible
            if self.image.is_visible('buttons/begin', confidence=0.7, retry=3, click=True):
                continue
            
            # Check if autobattle button is visible (formation selection screen)
            if self.image.is_visible('buttons/autobattle', confidence=0.95, retry=3, seconds=2,
                                    region=(214, 1774, 256, 112)):
                self._configure_battle_formation(formation)
            else:
                # Check for stop/pause
                if stop_event and stop_event.is_set():
                    logger.blue("Stop requested, ending push")
                    break
                if pause_event and pause_event.is_set():
                    logger.blue("Paused...")
                    pause_event.wait()  # Wait until unpaused
                
                # Change formation every x minutes if enabled
                cycle_minutes = self.config.getint('PUSH', 'cycleformation', fallback=0)
                if cycle_minutes > 0:
                    if datetime.datetime.now() - start_time >= datetime.timedelta(minutes=cycle_minutes):
                        formation += 1
                        if formation > 5:
                            formation = 1
                        logger.warning(f"Cycling to formation {formation} (every {cycle_minutes}min)")
                        self.controller.tap(550, 800)
                        self.controller.tap(550, 800)
                        self.controller.tap(550, 800)  # Click to prompt AutoBattle popup
                        self.image.click_image('buttons/exit', suppress=True, retry=3, seconds=2)
                        self._configure_battle_formation(formation)
                        start_time = datetime.datetime.now()  # Reset formation timer
                
                # Check autobattle counter
                if (self.image.is_visible('labels/autobattle_0', retry=3, suppress=True,
                                         region=(730, 1600, 50, 50)) or
                    self.image.is_visible('labels/autobattle_0_hidden', retry=3, suppress=True,
                                         region=(730, 1600, 50, 50))):
                    # No victory found
                    if not self.config.getboolean('PUSH', 'suppressSpam', fallback=False):
                        logger.warning(f"No victory found, checking again in {duration} minutes")
                    
                    # Wait for duration (minus time for configuring)
                    self.wait((duration * 60) - 50)
                else:
                    # Victory found! (autobattle counter is not 0)
                    self.controller.tap(550, 800)
                    self.controller.tap(550, 800)
                    self.controller.tap(550, 800)  # Click to prompt AutoBattle popup
                    
                    if self.image.is_visible('labels/autobattle'):
                        logger.green("Victory found! Loading formation for current stage...")
                        self.image.click_image('buttons/exit', suppress=True, retry=3, seconds=2)
                        start_time = datetime.datetime.now()  # Reset timer
                    elif not self.image.is_visible('buttons/pause', retry=3, 
                                                   region=(24, 1419, 119, 104)):
                        # Something went wrong
                        logger.error("AutoBattle screen not found, reloading auto-push...")
                        if not self.controller.recover():
                            raise RuntimeError("Recovery failed during campaign push. Shutting down.")
        
        logger.green("Campaign push complete")
        return True
        
    def _configure_battle_formation(self, formation: int) -> bool:
        """Configure battle formation
        
        Returns:
            bool: True if successful, False if no attempts left
        """
        logger.blue(f"Configuring formation {formation}...")
        
        # Check if ignoreformations is enabled
        if self.config.getboolean('ADVANCED', 'ignoreformations', fallback=False):
            logger.warning('ignoreformations enabled, skipping formation selection')
            self.image.click_image('buttons/autobattle', suppress=True, retry=3, 
                                  region=(214, 1774, 256, 112))
            # Click activate and verify autobattle label appears
            self.image.click_image('buttons/activate', retry=3, 
                                  region=(580, 1208, 300, 150))
            return True
        
        # Check if formations button is visible
        if self.image.is_visible('buttons/formations', region=(914, 1762, 102, 134), click=True, seconds=3, retry=5, retry_interval=0.3):
            
            # Switch to Popular tab if enabled
            if self.config.getboolean('ADVANCED', 'popularformations', fallback=False):
                self.controller.tap(800, 1650, seconds=2)
            
            # Select formation using calculation from old version
            # Formation positions: 425 + (formation * 175)
            formation_y = 425 + (formation * 175)
            self.controller.tap(850, formation_y, seconds=2)
            
            # Click Use button
            self.image.click_image('buttons/use', retry=5, seconds=2, suppress=True,
                                  retry_interval=0.3)
            
            # Configure Artifacts
            artifacts = None
            counter = 0
            while artifacts is None and counter <= 5:
                artifacts = self.image.is_visible('buttons/checkbox_checked', 
                                                  region=(230, 1100, 80, 80), 
                                                  suppress=True)
                counter += 1
            
            if counter >= 5:
                logger.error("Couldn't read artifact status")
            
            # Toggle artifacts if needed
            use_artifacts = self.config.getboolean('PUSH', 'useartifacts', fallback=True)
            if artifacts is not None and artifacts != use_artifacts:
                self.controller.tap(275, 1150)
            
            # Confirm formation
            self.image.click_image('buttons/confirm_small', retry=3, 
                                  region=(600, 1220, 250, 100), suppress=True)
            
            # Click autobattle button
            self.image.click_image('buttons/autobattle', retry=3, seconds=2, suppress=True,
                                  region=(214, 1774, 256, 112))
            
            # Confirm autobattle
            self.image.click_image('buttons/confirm', seconds=2, retry=5, suppress=True,
                                  retry_interval=0.3)
            self.image.click_image('buttons/confirm_campaign', seconds=2, retry=2, suppress=True)
            return True
            
        elif self.image.is_visible('labels/tower_no_attempts'):
            logger.warning('No attempts left for this tower, exiting...')
            return False
        else:
            logger.warning('Could not find Formations button')
            return True
