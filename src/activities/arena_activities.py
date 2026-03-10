"""Arena and PvP activities implementation"""
import logging
from src.activities.base_activity import BaseActivity

logger = logging.getLogger(__name__)


class ArenaActivities(BaseActivity):
    """Handles arena and PvP activities"""
    
    def battle_arena_of_heroes(self, count: int, opponent: int = 1, 
                               pause_event=None, stop_event=None) -> bool:
        """Battle in Arena of Heroes"""
        counter = 0
        logger.blue(f"Battling Arena of Heroes {count} times...")
        
        self.controller.confirm_location('darkforest', 
                                        region=self.controller.BOUNDARIES['darkforestSelect'])
        self.controller.tap(740, 1100)
        self.controller.tap(550, 50)  # Clear tickets popup
        
        if self.image.is_visible('labels/arenaofheroes'):
            self.image.click_image('labels/arenaofheroes', suppress=True)
            self.wait(1)
            self.image.click_image('buttons/challenge', retry=3, 
                                  region=self.controller.BOUNDARIES['challengeAoH'])
            
            while counter < count:
                # Check for pause/stop
                if self._check_pause_stop(pause_event, stop_event):
                    break
                    
                self.wait(1)
                self.controller.select_opponent(choice=opponent)
                
                # Wait for hero selection
                while self.image.is_visible('buttons/heroclassselect', retry=3,
                                           region=self.controller.BOUNDARIES['heroclassselect']):
                    self.controller.tap(550, 1800)
                    
                # Skip battle - wait for skip button and keep clicking until battle ends
                if self.image.wait_for_image('buttons/skip', timeout=5, check_interval=0.2,
                                            confidence=0.8, region=self.controller.BOUNDARIES['skipAoH']):
                    # Keep clicking skip until it disappears (battle ends)
                    while self.image.is_visible('buttons/skip', confidence=0.8, seconds=0.2,
                                               region=self.controller.BOUNDARIES['skipAoH']):
                        self.image.click_image('buttons/skip', confidence=0.8, seconds=0.2,
                                              region=self.controller.BOUNDARIES['skipAoH'])
                
                # Check results
                if self.controller.return_battle_results(battle_type='arena'):
                    logger.green(f"Battle #{counter+1} - Victory!")
                    self.controller.tap(600, 550)  # Clear loot popup
                else:
                    logger.error(f"Battle #{counter+1} - Defeat!")
                    
                self.controller.tap(600, 550)  # Back to opponent selection
                counter = counter + 1
                
            self.image.click_image('buttons/exitmenu', region=self.controller.BOUNDARIES['exitAoH'])
            self.image.click_image('buttons/back', retry=3, 
                                  region=self.controller.BOUNDARIES['backMenu'])
            self.image.click_image('buttons/back', retry=3, 
                                  region=self.controller.BOUNDARIES['backMenu'])
            logger.green("Arena battles complete")
            return True
        else:
            logger.error("Arena of Heroes not found, attempting to recover")
            self.controller.recover()
            return False
            
    def collect_gladiator_coins(self) -> bool:
        """Collect gladiator coins from Legends Tournament"""
        logger.blue("Collecting gladiator coins...")
        
        self.controller.confirm_location('darkforest', 
                                        region=self.controller.BOUNDARIES['darkforestSelect'])
        self.controller.tap(740, 1100)
        self.controller.tap(550, 50)
        
        # Scroll down to find Legends Tournament
        self.controller.swipe(550, 800, 550, 500, duration=200, seconds=2)
        
        if self.image.is_visible('labels/legendstournament_new', suppress=True):
            self.image.click_image('labels/legendstournament_new', suppress=True)
            self.controller.tap(550, 300, seconds=2)
            self.controller.tap(50, 1850)
            self.image.click_image('buttons/back', region=self.controller.BOUNDARIES['backMenu'])
            self.image.click_image('buttons/back', region=self.controller.BOUNDARIES['backMenu'])
            logger.green("Gladiator coins collected")
            return True
        else:
            logger.warning("Legends Tournament not found")
            self.controller.recover()
            return False
            
    def collect_treasure_scramble(self) -> bool:
        """Collect Treasure Scramble daily rewards"""
        logger.blue("Collecting Treasure Scramble rewards...")
        
        self.controller.confirm_location('darkforest', 
                                        region=self.controller.BOUNDARIES['darkforestSelect'])
        self.controller.tap(750, 1100)
        self.controller.tap(550, 50)  # Clear tickets
        self.controller.tap(550, 50)  # Clear overflow
        
        ts_banners = [
            'labels/tsbanner_forest',
            'labels/tsbanner_ice',
            'labels/tsbanner_fog',
            'labels/tsbanner_volcano',
            'labels/tsbanner_nature'
        ]
        
        for banner in ts_banners:
            if self.image.is_visible(banner, confidence=0.8):
                self.image.click_image(banner, confidence=0.8)
                self.wait(2)
                
                if self.image.is_visible('buttons/ts_path'):
                    self.image.click_image('buttons/ts_path')
                    self.controller.tap(370, 945)  # Choose path
                    self.controller.tap(520, 1700)  # Confirm
                    self.image.click_image('buttons/back', retry=3, 
                                          region=self.controller.BOUNDARIES['backMenu'])
                    self.image.click_image('buttons/back', retry=3, suppress=True,
                                          region=self.controller.BOUNDARIES['backMenu'])
                    return True
                else:
                    # Already collected
                    self.controller.tap(400, 50, seconds=2)  # Clear rank up
                    self.controller.tap(400, 50, seconds=2)  # Clear loot
                    self.image.click_image('buttons/back', retry=3, 
                                          region=self.controller.BOUNDARIES['backMenu'])
                    self.image.click_image('buttons/back', retry=3, suppress=True,
                                          region=self.controller.BOUNDARIES['backMenu'])
                    logger.green("Treasure Scramble rewards collected")
                    self.controller.recover(silent=True)
                    return True
                    
        logger.warning("Treasure Scramble not found")
        self.controller.recover()
        return False
        
    def _check_pause_stop(self, pause_event, stop_event) -> bool:
        """Check if pause or stop event is set"""
        if stop_event and stop_event.is_set():
            logger.blue("Stop event detected")
            return True
            
        if pause_event and pause_event.is_set():
            logger.blue("Paused, waiting to resume...")
            while pause_event.is_set():
                self.wait(1)
                if stop_event and stop_event.is_set():
                    return True
            logger.blue("Resumed")
            
        return False

