"""Labyrinth and dungeon activities"""
import logging
from src.activities.base_activity import BaseActivity

logger = logging.getLogger(__name__)


class LabyrinthActivities(BaseActivity):
    """Handles labyrinth exploration"""
    
    def handle_labyrinth(self) -> bool:
        """Handle complete labyrinth run"""
        logger.info("Attempting to run Arcane Labyrinth...")
        
        lower_direction = ''  # Left or right for first battle
        upper_direction = ''  # Left or right for double battle at end
        
        self.controller.confirm_location('darkforest', 
                                        region=self.controller.BOUNDARIES['darkforestSelect'])
        self.controller.wait()
        self.controller.tap(400, 1150, seconds=3)  # Wait for lab screen to load
        
        # Check if already open
        if self.image.is_visible('labels/labfloor3', retry=3, confidence=0.8, seconds=3):
            logger.green("Lab already open! Continuing...")
            self.controller.tap(50, 1800, seconds=2)
            return True
            
        # Check if locked
        if self.image.is_visible('labels/lablocked', confidence=0.8, seconds=3):
            logger.green("Dismal Lab not unlocked! Continuing...")
            self.controller.tap(50, 1800, seconds=2)
            return True
            
        if self.image.is_visible('labels/lab', retry=3):
            
            # Check for Swept
            if self.image.is_visible('labels/labswept', retry=3, confidence=0.8, seconds=3):
                logger.green("Lab already swept! Continuing...")
                self.controller.tap(50, 1800, seconds=2)
                return True
                
            # Check for Sweep
            if self.image.is_visible('buttons/labsweep', retry=3, confidence=0.8, 
                                    click=True, seconds=3):
                logger.green("Sweep Available!")
                if self.image.is_visible('buttons/labsweepbattle', retry=3, confidence=0.8, 
                                        click=True, seconds=3):
                    self.controller.tap(720, 1450, seconds=3)  # Confirm
                    self.controller.tap(550, 1550, seconds=3)  # Clear Rewards
                    
                    if self.image.is_visible('labels/notice', retry=3, seconds=3):
                        self.controller.tap(550, 1250)
                        
                    self.controller.tap(550, 1550, seconds=5)  # Clear Roamer Deals
                    self.controller.tap(550, 1650)  # Clear Limited Offer
                    logger.green("Lab Swept!")
                    return True
            else:
                # Manual lab run
                logger.green("Sweep not found, attempting manual Lab run...")
                return self._manual_lab_run(lower_direction, upper_direction)
        else:
            logger.error("Can't find Lab screen!")
            self.controller.recover()
            return False
            
    def _manual_lab_run(self, lower_direction: str, upper_direction: str) -> bool:
        """Run labyrinth manually"""
        # Pre-run setup
        logger.info("Entering Lab...")
        self.controller.tap(750, 1100, seconds=2)  # Center of Dismal
        self.controller.tap(550, 1475, seconds=2)  # Challenge
        self.controller.tap(550, 1600, seconds=2)  # Begin Adventure
        self.controller.tap(700, 1250, seconds=6)  # Confirm
        self.controller.tap(550, 1600, seconds=3)  # Clear Debuff
        
        # Sweep floors
        logger.info("Sweeping floors...")
        self.controller.tap(950, 1600, seconds=2)  # Level Sweep
        self.controller.tap(550, 1550, seconds=8)  # Confirm
        self.controller.tap(550, 1600, seconds=2)  # Clear Resources Exceeded
        self.controller.tap(550, 1600, seconds=2)  # Again for safe measure
        self.controller.tap(550, 1600, seconds=3)  # Clear Loot
        self.controller.tap(550, 1250, seconds=5)  # Abandon Roamer
        self.controller.tap(530, 1450, seconds=5)  # Abandon Roamer #2
        self.controller.tap(550, 1570, seconds=2)  # Adventure complete
        
        # Check if swept completely
        if self.image.is_visible('labels/lab_end_flag', retry=3, 
                                region=(450, 400, 150, 220), confidence=0.8):
            logger.info("Lab Swept!")
            self.controller.tap(50, 1800, seconds=2)
            return True
            
        # Choose relics
        logger.info("Choosing relics...")
        for _ in range(6):
            self.controller.tap(550, 900)
            self.controller.tap(550, 1325, seconds=3)
            
        # Enter 3rd Floor
        logger.info("Entering 3rd Floor...")
        self.controller.tap(550, 550, seconds=2)  # Portal
        self.controller.tap(550, 1200, seconds=5)  # Enter
        self.controller.tap(550, 1600, seconds=2)  # Clear Debuff
        
        # Determine route
        self.controller.tap(400, 1400, seconds=2)
        if self.image.is_visible('labels/labguard', retry=2):
            logger.warning("Loot Route: Left")
            lower_direction = 'left'
        else:
            logger.warning("Loot Route: Right")
            lower_direction = 'right'
            self.controller.tap(550, 50, seconds=3)
            
        # Battle through floors
        if not self._battle_lab_floors(lower_direction, upper_direction):
            return False
            
        # Collect final rewards
        self.wait(6)
        self.controller.tap(550, 1650, seconds=3)  # Clear Value Bundle
        self.controller.tap(550, 550, seconds=3)  # Loot Chest
        self.controller.tap(550, 1650, seconds=2)  # Clear Loot
        self.controller.tap(550, 1650, seconds=2)  # Clear Notice
        self.controller.tap(550, 1650, seconds=2)  # One more for safe measure
        self.controller.tap(50, 1800, seconds=2)  # Exit
        
        logger.info("Manual Lab run complete!")
        return True
        
    def _battle_lab_floors(self, lower_direction: str, upper_direction: str) -> bool:
        """Battle through all lab floors"""
        # 1st Row (single)
        self._handle_lab_tile('lower', lower_direction, '1')
        if not self._do_lab_battle(1):
            return False
            
        # 2nd Row (multi)
        self._handle_lab_tile('lower', lower_direction, '2')
        if not self._do_lab_battle(1, first_of_multi=True):
            return False
        self.controller.tap(750, 1725, seconds=4)
        if not self._do_lab_battle(2):
            return False
            
        # 3rd Row (single relic)
        self._handle_lab_tile('lower', lower_direction, '3')
        if not self._do_lab_battle(1):
            return False
        self.controller.tap(550, 1350, seconds=2)  # Clear Relic
        
        # 4th Row (multi)
        self._handle_lab_tile('lower', lower_direction, '4')
        if not self._do_lab_battle(1, first_of_multi=True):
            return False
        self.controller.tap(750, 1725, seconds=4)
        if not self._do_lab_battle(1):
            return False
            
        # 5th Row (single)
        self._handle_lab_tile('lower', lower_direction, '5')
        if not self._do_lab_battle(1):
            return False
            
        # 6th Row (single relic)
        self._handle_lab_tile('lower', lower_direction, '6')
        if not self._do_lab_battle(1):
            return False
        self.controller.tap(550, 1350, seconds=2)  # Clear Relic
        
        # Determine upper route
        self.controller.swipe(550, 200, 550, 1800, duration=1000)
        self.controller.tap(400, 1450, seconds=2)
        if self.image.is_visible('labels/labpraeguard', retry=2):
            logger.warning("Loot Route: Left")
            upper_direction = 'left'
        else:
            logger.warning("Loot Route: Right")
            upper_direction = 'right'
            self.controller.tap(550, 50, seconds=2)
            
        # 7th Row (multi)
        self._handle_lab_tile('upper', upper_direction, '7')
        if not self._do_lab_battle(1, first_of_multi=True):
            return False
        self.controller.tap(750, 1725, seconds=4)
        if not self._do_lab_battle(1):
            return False
            
        # 8th Row (multi)
        self._handle_lab_tile('upper', upper_direction, '8')
        if not self._do_lab_battle(1, first_of_multi=True):
            return False
        self.controller.tap(750, 1725, seconds=4)
        if not self._do_lab_battle(1):
            return False
            
        # 9th Row (witches den or fountain)
        self._handle_lab_tile('upper', upper_direction, '9')
        if self.image.is_visible('labels/labwitchsden', retry=3):
            logger.warning("Clearing Witch's Den")
            self.controller.tap(550, 1500, seconds=3)
            self.controller.tap(300, 1600, seconds=4)
        if self.image.is_visible('labels/labfountain', retry=3):
            logger.warning("Clearing Divine Fountain")
            self.controller.tap(725, 1250, seconds=3)
            self.controller.tap(725, 1250, seconds=2)
            
        # 10th row (single boss)
        self._handle_lab_tile('upper', upper_direction, '10')
        if not self._do_lab_battle(1, pet=False):
            return False
            
        return True
        
    def _do_lab_battle(self, team: int, first_of_multi: bool = False, pet: bool = True) -> bool:
        """Execute a lab battle"""
        if self.image.is_visible('buttons/heroclassselect', retry=3):
            self._configure_lab_teams(team, pet)
            self.controller.tap(550, 1850, seconds=4)  # Battle
        else:
            logger.error("Battle Screen not found!")
            self.controller.recover()
            return False
            
        return self._return_lab_battle_result(first_of_multi)
        
    def _return_lab_battle_result(self, first_of_multi: bool = False) -> bool:
        """Check lab battle result"""
        counter = 0
        
        while counter < 15:
            # Check for resources exceeded
            if self.image.is_visible('labels/notice'):
                self.controller.tap(550, 1250)
                
            if self.image.is_visible('labels/victory'):
                logger.green("Lab Battle Victory!")
                if not first_of_multi:
                    self.controller.tap(550, 1850, seconds=5)
                return True
                
            if self.image.is_visible('labels/defeat'):
                logger.error("Lab Battle Defeat! Exiting...")
                self.controller.recover()
                return False
                
            counter += 1
            
        logger.error("Battle timer expired")
        self.controller.recover()
        return False
        
    def _configure_lab_teams(self, team: int, pet: bool = True):
        """Configure labyrinth teams"""
        if team == 1:
            self.controller.tap(1030, 1100, seconds=2)  # Clear Team
            self.controller.tap(550, 1250, seconds=2)  # Confirm
            # Select top 5 heroes (reverse order for positioning)
            self.controller.tap(930, 1300)  # Slot 5
            self.controller.tap(730, 1300)  # Slot 4
            self.controller.tap(530, 1300)  # Slot 3
            self.controller.tap(330, 1300)  # Slot 2
            self.controller.tap(130, 1300)  # Slot 1
            
            if pet:
                if self.image.is_visible('buttons/pet_empty', confidence=0.75, retry=3, 
                                        click=True, region=(5, 210, 140, 100)):
                    self.controller.tap(150, 1250, seconds=2)  # First Pet
                    self.controller.tap(750, 1800, seconds=4)  # Confirm
                    
        if team == 2:
            self.controller.tap(1030, 1100, seconds=2)  # Clear Team
            self.controller.tap(550, 1250, seconds=2)  # Confirm
            # Select heroes 6-10
            self.controller.tap(130, 1550)  # Slot 1
            self.controller.tap(330, 1550)  # Slot 2
            self.controller.tap(530, 1550)  # Slot 3
            self.controller.tap(730, 1550)  # Slot 4
            self.controller.tap(930, 1550)  # Slot 5
            
            if pet:
                if self.image.is_visible('buttons/pet_empty', confidence=0.75, retry=3, 
                                        click=True, region=(5, 210, 140, 100)):
                    self.controller.tap(350, 1250, seconds=2)  # Second Pet
                    self.controller.tap(750, 1800, seconds=4)  # Confirm
                    
    def _handle_lab_tile(self, elevation: str, side: str, tile: str):
        """Select and navigate to lab tile"""
        if tile in ['4', '6', '10']:
            logger.blue(f"Battling {elevation.capitalize()} Tile {tile}")
        else:
            logger.blue(f"Battling {elevation.capitalize()} {side.capitalize()} Tile {tile}")
            
        self.wait(1)
        
        # Tile coordinates based on elevation, side, and tile number
        if elevation == 'lower':
            if side == 'left':
                coords = {
                    '1': (400, 1450), '2': (250, 1250), '3': (400, 1050),
                    '4': (550, 850), '5': (400, 650), '6': (550, 450)
                }
            else:  # right
                coords = {
                    '1': (700, 1450), '2': (800, 1225), '3': (700, 1050),
                    '4': (550, 850), '5': (700, 650), '6': (550, 450)
                }
        else:  # upper
            if side == 'left':
                coords = {
                    '7': (400, 1450), '8': (250, 1250), '9': (400, 1100), '10': (550, 900)
                }
            else:  # right
                coords = {
                    '7': (700, 1450), '8': (800, 1225), '9': (700, 1100), '10': (550, 850)
                }
                
        if tile in coords:
            x, y = coords[tile]
            self.controller.tap(x, y, seconds=2)
            
            # Handle different tile types
            if tile in ['3', '6']:  # Relic tiles
                self.controller.tap(550, 1600, seconds=4)
            elif tile == '2' and elevation == 'lower':  # First multi
                self.controller.tap(550, 1500, seconds=4)
                if self.image.is_visible('labels/notice', confidence=0.8, retry=3):
                    self.controller.tap(450, 1150, seconds=2)  # Don't show again
                    self.controller.tap(725, 1250, seconds=4)  # Go
                self.controller.tap(750, 1500, seconds=4)  # Begin Battle
            elif tile in ['2', '4', '7', '8']:  # Multi battles
                if tile != '7' or side != 'left':  # 7 left already opened
                    self.controller.tap(550, 1500, seconds=4)  # Go
                self.controller.tap(750, 1500, seconds=4)  # Begin Battle
            elif tile == '10':  # Boss
                self.controller.tap(550, 1500, seconds=4)
            else:  # Single battles
                self.controller.tap(550, 1500, seconds=4)

