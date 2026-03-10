"""Miscellaneous activities (events, etc.)"""
import logging
from src.activities.base_activity import BaseActivity

logger = logging.getLogger(__name__)


class MiscActivities(BaseActivity):
    """Handles miscellaneous activities like events"""
    
    def handle_fight_of_fates(self, battles: int = 3) -> bool:
        """Handle Fight of Fates event"""
        logger.blue(f"Attempting to run Fight of Fates {battles} times...")
        counter = 0
        
        self.image.click_image('buttons/events', confidence=0.8, retry=5, seconds=3, 
                              retry_interval=0.3)
        
        # Find Fight of Fates
        if self.image.is_visible('labels/fightoffates', click=True):
            visible = True
        else:
            self.controller.swipe(550, 600, 550, 300, duration=200, seconds=2)
            if self.image.is_visible('labels/fightoffates', click=True):
                visible = True
            else:
                visible = False
                
        if visible:
            while counter < battles:
                self.image.click_image('buttons/challenge_tr', confidence=0.8, 
                                      suppress=True, retry=3, seconds=15)
                
                # Drag heroes and skills until battle ends
                while not self.image.is_visible('labels/fightoffates_inside', confidence=0.95):
                    # Hero
                    self.controller.swipe(200, 1700, 290, 975, 200)
                    # Skill 1
                    self.controller.swipe(450, 1700, 550, 950, 200)
                    # Hero
                    self.controller.swipe(200, 1700, 290, 975, 200)
                    # Skill 2
                    self.controller.swipe(600, 1700, 550, 950, 200)
                    # Hero
                    self.controller.swipe(200, 1700, 290, 975, 200)
                    # Skill 3
                    self.controller.swipe(800, 1700, 550, 950, 200)
                    
                counter += 1
                logger.green(f"Fight of Fates Battle #{counter} complete")
                
            # Collect quests
            self.controller.tap(975, 125, seconds=2)
            self.controller.tap(650, 1650, seconds=1)  # Dailies tab
            self.controller.tap(940, 680, seconds=2)  # Collect
            self.controller.tap(980, 435, seconds=2)
            self.controller.tap(550, 250, seconds=2)  # Clear loot
            
            # Exit
            self.controller.tap(70, 1810, seconds=1)
            self.controller.tap(70, 1810, seconds=1)
            self.controller.tap(70, 1810, seconds=1)
            
            logger.green("Fight of Fates attempted successfully")
            return True
        else:
            logger.error("Fight of Fates not found")
            self.controller.recover()
            return False
            
    def handle_battle_of_blood(self, battles: int = 3) -> bool:
        """Handle Battle of Blood event"""
        logger.blue(f"Attempting to run Battle of Blood {battles} times...")
        battle_counter = 0
        bob_timeout = 0
        
        self.image.click_image('buttons/events', confidence=0.8, retry=3, seconds=3)
        
        # Find Battle of Blood
        if self.image.is_visible('labels/battleofblood_event_banner'):
            visible = True
        else:
            self.controller.swipe(550, 600, 550, 300, duration=200, seconds=2)
            if self.image.is_visible('labels/battleofblood_event_banner'):
                visible = True
            else:
                visible = False
                
        if visible:
            self.image.click_image('labels/battleofblood_event_banner')
            
            while battle_counter < battles:
                self.image.click_image('buttons/challenge_tr', confidence=0.8, 
                                      suppress=True, retry=3, seconds=7)
                
                # Stage 1: Place cards 1-2
                while not self.image.is_visible('labels/battleofblood_stage1', 
                                               region=(465, 20, 150, 55)):
                    self.wait(1)
                    bob_timeout += 1
                    if bob_timeout > 30:
                        logger.error("Battle of Blood timeout!")
                        self.controller.recover()
                        return False
                else:
                    self.wait(4)  # Card animations
                    bob_timeout = 0
                    self.controller.tap(550, 1250, seconds=1)
                    self.controller.tap(350, 1250, seconds=1)
                    self.controller.tap(550, 1850, seconds=1)
                    
                # Check for confirm dialog
                if self.image.is_visible('buttons/confirm_small', retry=3, 
                                        region=(600, 1240, 200, 80)):
                    self.controller.tap(325, 1200)
                    self.controller.tap(700, 1270)
                    
                # Stage 2: Place cards 3-4
                while not self.image.is_visible('labels/battleofblood_stage2', 
                                               region=(465, 20, 150, 55)):
                    self.wait(1)
                    bob_timeout += 1
                    if bob_timeout > 30:
                        logger.error("Battle of Blood timeout!")
                        self.controller.recover()
                        return False
                else:
                    self.wait(4)
                    bob_timeout = 0
                    self.controller.tap(550, 1250, seconds=1)
                    self.controller.tap(350, 1250, seconds=1)
                    self.controller.tap(550, 1850, seconds=1)
                    
                # Stage 3: Place card 5
                while not self.image.is_visible('labels/battleofblood_stage3', 
                                               region=(465, 20, 150, 55), confidence=0.95):
                    self.wait(1)
                    bob_timeout += 1
                    if bob_timeout > 30:
                        logger.error("Battle of Blood timeout!")
                        self.controller.recover()
                        return False
                else:
                    self.wait(4)
                    bob_timeout = 0
                    self.controller.tap(550, 1250, seconds=1)
                    self.controller.tap(550, 1850, seconds=8)
                    
                    battle_counter += 1
                    
                    # Check battle result
                    result = self.controller.return_battle_results('BoB')
                    if result:
                        logger.info(f"Victory! Battle of Blood Battle #{battle_counter} complete")
                    else:
                        logger.warning(f"Defeat! Battle of Blood Battle #{battle_counter} complete")
                    
            # Collect quests
            self.wait(2)
            self.controller.tap(150, 230, seconds=2)
            self.controller.tap(650, 1720)  # Dailies tab
            self.controller.tap(850, 720, seconds=3)
            self.controller.tap(920, 525, seconds=2)
            self.controller.tap(920, 525, seconds=2)
            self.controller.tap(550, 250, seconds=2)  # Clear loot
            
            # Exit
            self.controller.tap(70, 1810)
            self.controller.tap(70, 1810)
            self.controller.tap(70, 1810)
            
            if (self.controller.confirm_location('ranhorn', change=False, 
                                                region=self.controller.BOUNDARIES['ranhornSelect']) or
                self.controller.confirm_location('campaign', change=False, 
                                                region=self.controller.BOUNDARIES['campaignSelect'])):
                logger.green("Battle of Blood attempted successfully")
                return True
            else:
                logger.warning("Issue exiting Battle of Blood")
                self.controller.recover()
                return False
        else:
            logger.error("Battle of Blood not found")
            self.controller.recover()
            return False
            
    def handle_circus_tour(self, battles: int = 3) -> bool:
        """Handle Circus Tour event"""
        logger.blue("Attempting to run Circus Tour battles...")
        battle_counter = 1
        
        self.controller.confirm_location('ranhorn', 
                                        region=self.controller.BOUNDARIES['ranhornSelect'])
        self.image.click_image('buttons/events', confidence=0.8, retry=3, seconds=3)
        
        if self.image.is_visible('labels/circustour', retry=3, click=True):
            while battle_counter < battles:
                logger.info(f"Circus Tour battle #{battle_counter}")
                self.image.click_image('buttons/challenge_tr', confidence=0.8, retry=3, 
                                      suppress=True, seconds=3)
                
                # Clear dialogue on first battle
                if battle_counter == 1:
                    while self.image.is_visible('labels/dialogue_left', retry=2, 
                                               region=self.controller.BOUNDARIES['dialogue_left']):
                        logger.warning("Clearing dialogue...")
                        for _ in range(6):
                            self.controller.tap(550, 900)
                        self.wait(2)
                        self.image.click_image('buttons/challenge_tr', confidence=0.8, 
                                              retry=3, suppress=True, seconds=3)
                        
                self.image.click_image('buttons/battle_large', confidence=0.8, retry=3, 
                                      suppress=True, seconds=5)
                # Wait for skip button to appear
                if self.image.wait_for_image('buttons/skip', timeout=5, check_interval=0.2, confidence=0.8):
                    self.image.click_image('buttons/skip', confidence=0.8)
                self.controller.tap(550, 1800)  # Clear loot
                battle_counter += 1
                
            # Collect chests
            self.wait(3)
            self.controller.tap(500, 1600)  # First chest
            self.controller.tap(500, 1600)  # Clear loot
            self.controller.tap(900, 1600)  # Second chest
            self.controller.tap(900, 1600)  # Clear loot
            
            # Exit
            self.controller.tap(70, 1810, seconds=1)
            self.controller.tap(70, 1810, seconds=1)
            
            if self.controller.confirm_location('ranhorn', change=False, 
                                               region=self.controller.BOUNDARIES['ranhornSelect']):
                logger.info("Circus Tour attempted successfully")
                return True
            else:
                logger.warning("Issue exiting Circus Tour")
                self.controller.recover()
                return False
        else:
            logger.error("Circus Tour not found")
            self.controller.recover()
            return False
        
    def handle_heroes_of_esperia(self, count: int = 3, opponent: int = 4) -> bool:
        """Handle Heroes of Esperia battles"""
        logger.blue(f"Battling Heroes of Esperia {count} times (opponent {opponent})...")
        logger.warning("Note: this currently won't work in the Legends Tower")
        
        counter = 0
        error_counter = 0
        
        self.controller.confirm_location('darkforest', 
                                        region=self.controller.BOUNDARIES['darkforestSelect'])
        self.controller.tap(740, 1050)  # Open Arena of Heroes
        self.controller.tap(550, 50)  # Clear Tickets Popup
        
        if self.image.is_visible('labels/heroesofesperia', click=True, seconds=3):
            # Check if we've opened it yet
            if self.image.is_visible('buttons/join_hoe', confidence=0.8, retry=3, 
                                    region=(420, 1780, 250, 150)):
                logger.warning("Heroes of Esperia not opened! Entering...")
                self.controller.tap(550, 1850)  # Clear Info
                self.controller.tap(550, 1850, seconds=6)  # Click join
                self.controller.tap(550, 1140, seconds=3)  # Clear Placement
                self.controller.tap(1000, 1650, seconds=8)  # Collect all and wait for scroll
                self.controller.tap(550, 260, seconds=5)  # Character portrait to clear Loot
                self.controller.tap(550, 260, seconds=5)  # Character portrait to scroll back up
                
            # Start battles
            if self.image.is_visible('buttons/fight_hoe', retry=10, seconds=3, click=True,
                                    region=(400, 200, 400, 1500)):
                while counter < count:
                    self._select_hoe_opponent(opponent)
                    
                    # Check for ticket purchase screen
                    if self.image.is_visible('labels/hoe_buytickets', 
                                            region=(243, 618, 600, 120)):
                        logger.error("Ticket Purchase screen found, exiting")
                        self.controller.recover()
                        return False
                        
                    # Wait for battle screen and start
                    while self.image.is_visible('buttons/heroclassselect', 
                                               region=self.controller.BOUNDARIES['heroclassselect']):
                        self.controller.tap(550, 1800, seconds=0)
                        
                    # Skip battle - wait for skip button and keep clicking until battle ends
                    if self.image.wait_for_image('buttons/skip', timeout=3, check_interval=0.2,
                                                confidence=0.8, region=self.controller.BOUNDARIES['skipAoH']):
                        while self.image.is_visible('buttons/skip', confidence=0.8, 
                                                   region=self.controller.BOUNDARIES['skipAoH']):
                            self.image.click_image('buttons/skip', confidence=0.8, 
                                                  region=self.controller.BOUNDARIES['skipAoH'])
                        
                    # Check result
                    if self._return_hoe_battle_result():
                        logger.green(f"Battle #{counter + 1} Victory!")
                    else:
                        logger.warning(f"Battle #{counter + 1} Defeat!")
                        
                    # Wait for fight button again
                    while not self.image.is_visible('buttons/fight_hoe', seconds=3, click=True,
                                                    region=(400, 200, 400, 1500)):
                        if error_counter < 6:
                            self.controller.tap(420, 50)  # Neutral location
                            self.controller.tap(550, 1420)  # Rank up confirm button
                            error_counter += 1
                        else:
                            logger.error("Something went wrong post-battle")
                            self.controller.recover()
                            return False
                            
                    error_counter = 0
                    counter += 1
            else:
                logger.error("Heroes of Esperia Fight button not found!")
                self.controller.recover()
                return False
                
            # Exit and collect quests
            self.image.click_image('buttons/exitmenu', 
                                  region=self.controller.BOUNDARIES['exitAoH'])
            
            logger.info("Collecting Quests...")
            self.controller.tap(975, 300, seconds=2)  # Bounties
            self.controller.tap(975, 220, seconds=2)  # Quests
            self.controller.tap(850, 880, seconds=2)  # Top daily quest
            self.controller.tap(550, 420, seconds=2)  # Clear loot
            self.controller.tap(870, 1650, seconds=2)  # Season quests tab
            self.controller.tap(850, 880, seconds=2)  # Top season quest
            self.controller.tap(550, 420, seconds=2)  # Clear loot
            self.image.click_image('buttons/exitmenu', 
                                  region=self.controller.BOUNDARIES['exitAoH'], seconds=2)
            
            # Check for pass loot
            if self.image.check_pixel(550, 1850, 2) > 150:
                logger.info("Collecting Heroes of Esperia Pass loot")
                self.controller.tap(550, 1800, seconds=2)
                self.controller.tap(420, 50)
                
            # Exit
            self.image.click_image('buttons/back', retry=3, 
                                  region=self.controller.BOUNDARIES['backMenu'])
            self.image.click_image('buttons/back', retry=3, 
                                  region=self.controller.BOUNDARIES['backMenu'])
            self.image.click_image('buttons/back', retry=3, 
                                  region=self.controller.BOUNDARIES['backMenu'])
            
            logger.green("Heroes of Esperia battles complete")
            return True
        else:
            logger.error("Heroes of Esperia not found")
            self.controller.recover()
            return False
            
    def _select_hoe_opponent(self, choice: int):
        """Select opponent in Heroes of Esperia"""
        # Opponent positions from top to bottom
        positions = {
            1: (550, 500),
            2: (550, 750),
            3: (550, 1000),
            4: (550, 1250),
            5: (550, 1500)
        }
        
        if choice in positions:
            x, y = positions[choice]
            self.controller.tap(x, y, seconds=2)
        else:
            logger.warning(f"Invalid opponent choice {choice}, using default")
            self.controller.tap(550, 1250, seconds=2)
            
    def _return_hoe_battle_result(self) -> bool:
        """Check Heroes of Esperia battle result"""
        counter = 0
        
        while counter < 10:
            # Clear Rank Up message
            if self.image.is_visible('labels/hoe_ranktrophy', retry=5, 
                                    region=(150, 900, 350, 250)):
                self.controller.tap(550, 1200)
                
            if self.image.is_visible('labels/victory'):
                self.controller.tap(550, 700, seconds=3)
                return True
                
            if self.image.is_visible('labels/defeat'):
                self.controller.tap(550, 700, seconds=3)
                return False
                
            counter += 1
            
        logger.error("Battle timer expired")
        return False

