"""
Game Controller Module
High-level game control functions
"""
import os
import logging
import time
import random

logger = logging.getLogger(__name__)


class GameController:
    """High-level game control and navigation"""
    
    # Screen boundaries for different UI elements
    BOUNDARIES = {
        # Location selectors
        'campaignSelect': (424, 1750, 232, 170),
        'darkforestSelect': (208, 1750, 226, 170),
        'ranhornSelect': (0, 1750, 210, 160),
        
        # Campaign/Auto battle
        'begin': (322, 1590, 442, 144),
        'multiBegin': (309, 1408, 467, 129),
        'autobattle': (214, 1774, 256, 112),
        'battle': (574, 1779, 300, 110),
        'battleLarge': (310, 1758, 464, 144),
        'formations': (914, 1762, 102, 134),
        'useAB': (600, 1630, 240, 100),
        'confirmAB': (600, 1220, 250, 100),
        'activateAB': (580, 1208, 300, 150),
        'autobattle0': (730, 1600, 50, 50),
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
        
        # AFK Rewards
        'collectAfk': (590, 1322, 270, 82),
        
        # Mail
        'mailLocate': (915, 515, 150, 150),
        'collectMail': (626, 1518, 305, 102),
        'backMenu': (0, 1720, 150, 200),
        
        # Friends
        'friends': (915, 670, 150, 150),
        'sendrecieve': (750, 1560, 306, 100),
        'exitMerc': (940, 340, 150, 150),
        
        # Fast Rewards
        'fastrewards': (700, 1612, 400, 106),
        'closeFR': (266, 1218, 236, 92),
        
        # Arena of Heroes
        'challengeAoH': (294, 1738, 486, 140),
        'attackAoH': (714, 654, 180, 606),
        'battleAoH': (294, 1760, 494, 148),
        'skipAoH': (650, 1350, 200, 200),
        'defeat': (116, 720, 832, 212),
        'exitAoH': (930, 318, 126, 132),
        
        # Misc
        'inngiftarea': (160, 1210, 500, 100),
        'dialogue_left': (40, 1550, 200, 300),
    }
    
    def __init__(self, device_manager, image_recognition, config):
        self.device = device_manager
        self.image = image_recognition
        self.config = config
        
    def tap(self, x: int, y: int, seconds: float = 1, random_shift: int = 0):
        """Tap at coordinates with optional random shift"""
        if random_shift > 0:
            x += random.randint(0, random_shift)
            y += random.randint(0, random_shift)
        self.device.tap(x, y)
        self.wait(seconds)
        
    def long_press(self, x: int, y: int, duration_ms: int = 1000, seconds: float = 1):
        """Long press at coordinates"""
        self.device.long_press(x, y, duration_ms)
        self.wait(seconds)
        
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 100, seconds: float = 1):
        """Swipe from point to point"""
        try:
            self.device.swipe(x1, y1, x2, y2, duration)
            self.wait(seconds)
        except Exception as e:
            logger.error(f"Swipe error: {e}, params: x1={x1}, y1={y1}, x2={x2}, y2={y2}, duration={duration}, seconds={seconds}")
            raise
        
    def confirm_location(self, location: str, change: bool = True, 
                        region: tuple = None) -> bool:
        """Confirm and navigate to game location (campaign/darkforest/ranhorn)"""
        locations = {
            'campaign': ('buttons/campaign_selected', 'buttons/campaign_unselected', (424, 1750, 232, 170)),
            'darkforest': ('buttons/darkforest_selected', 'buttons/darkforest_unselected', (208, 1750, 226, 170)),
            'ranhorn': ('buttons/ranhorn_selected', 'buttons/ranhorn_unselected', (0, 1750, 210, 160))
        }
        
        if location not in locations:
            logger.warning(f"Unknown location: {location}")
            return False
            
        selected_btn, unselected_btn, btn_region = locations[location]
        
        # Use btn_region if no custom region specified
        if region is None:
            region = btn_region
        
        # Check if already at location
        if self.image.is_visible(selected_btn, region=btn_region, suppress=True):
            return True
            
        # Navigate to location if change=True
        if change:
            self.image.click_image(unselected_btn, region=region, suppress=True)
            self.wait(2)
            return self.image.is_visible(selected_btn, region=btn_region, suppress=True)
            
        return False
        
    def recover(self, silent: bool = False) -> bool:
        """Try to recover to campaign screen"""
        if not silent:
            logger.warning("Attempting to recover to campaign screen...")
            
        recover_counter = 0
        
        while not self.image.is_visible('buttons/campaign_selected', suppress=True):
            # Try various buttons to get back to campaign
            self.tap(300, 50, seconds=0)  # Clear popups
            self.image.click_image('buttons/back', suppress=True, seconds=0.5, 
                                  region=(0, 1500, 250, 419))
            self.image.click_image('buttons/confirm_small', suppress=True, seconds=0.5)
            self.image.click_image('buttons/confirm_stageexit', suppress=True, seconds=0.5)
            self.image.click_image('buttons/back_narrow', suppress=True, seconds=1,
                                  region=(0, 1500, 250, 419))
            self.image.click_image('buttons/confirm_stageexit', suppress=True, seconds=0.5)
            self.image.click_image('buttons/exitmenu', suppress=True, seconds=0.5,
                                  region=(700, 0, 379, 500))
            self.image.click_image('buttons/confirm_small', suppress=True, seconds=0.5)
            self.image.click_image('buttons/exit', suppress=True, seconds=0.5)
            self.image.click_image('buttons/campaign_unselected', suppress=True, seconds=0.5,
                                  region=(424, 1750, 232, 170))
            
            recover_counter += 1
            if recover_counter > 7:
                break
        
        # Final check - are we at campaign?
        if self.confirm_location('campaign', change=True):
            self.tap(550, 1900)  # Clear any popups
            if not silent:
                logger.info("Recovered successfully")
            return True
        else:
            if not silent:
                logger.error("Recovery failed")
            return False
        
    def expand_menus(self):
        """Expand collapsed side menus"""
        while self.image.is_visible('buttons/downarrow', confidence=0.8, suppress=True, click=True, retry=3):
            pass
            
    def wait_until_game_active(self):
        """Wait for game to load and navigate to campaign"""
        logger.info("Waiting for game to load...")
        
        # First quick check - if game is already loaded, return immediately
        if self.image.is_visible('buttons/campaign_selected', suppress=True):
            logger.info("Game already loaded and at campaign screen")
            return True
        
        loading_counter = 0
        timeout_counter = 0
        max_timeout = 60
        required_checks = 2  # Reduced from 3 to 2 for faster detection
        
        while loading_counter < required_checks:
            # Clear popups
            self.tap(420, 50, seconds=0)
            
            # Try back buttons
            buttons = ['buttons/campaign_unselected', 'buttons/exitmenu_trial', 'buttons/back']
            for button in buttons:
                self.image.click_image(button, seconds=0, suppress=True)
                
            timeout_counter += 1
            if timeout_counter > max_timeout:
                logger.error("Timed out waiting for game to load")
                return False
                
            # Check if campaign is visible
            if self.image.is_visible('buttons/campaign_selected', suppress=True):
                loading_counter += 1
                if loading_counter >= required_checks:
                    break  # Exit immediately when confirmed
            else:
                # Reset counter if not visible (ensures consecutive detections)
                loading_counter = 0
                
            # Clear time-limited deals
            self.tap(540, 1900, seconds=0)
            
            # Small wait between checks to avoid hammering
            self.wait(0.5)
            
        logger.info("Game loaded successfully")
        return True
        
    def select_opponent(self, choice: int = 1, hoe: bool = False) -> bool:
        """Select arena opponent by position (1-5)"""
        if hoe:
            # Heroes of Esperia - check blue pixel
            locations = [(850, 680), (850, 840), (850, 1000), (850, 1160), (850, 1320)]
            battle_buttons = []
            
            for x, y in locations:
                blue_value = self.image.check_pixel(x, y, 2)  # Blue channel
                if blue_value > 150:
                    battle_buttons.append(y)
        else:
            # Arena of Heroes - find battle buttons
            regions = [
                (715, 650, 230, 130),
                (715, 830, 230, 130),
                (715, 1000, 230, 130),
                (715, 1180, 230, 130),
                (715, 1360, 230, 130)
            ]
            battle_buttons = []
            
            for region in regions:
                if self.image.find_image('buttons/arenafight', confidence=0.9, region=region):
                    battle_buttons.append(region[1] + (region[3] / 2))
                    
        if not battle_buttons:
            logger.error("No opponents found")
            return False
            
        battle_buttons.sort()
        idx = len(battle_buttons) - 1 if choice > len(battle_buttons) else choice - 1
        self.tap(820, int(battle_buttons[idx]))
        return True
        
    def return_battle_results(self, battle_type: str = 'arena') -> bool:
        """Check if battle was won or lost"""
        self.wait(2)
        
        # Check for victory
        if self.image.is_visible('labels/victory', suppress=True):
            return True
            
        # Check for defeat
        if self.image.is_visible('labels/defeat', suppress=True):
            return False
            
        # Default to victory if unclear
        return True
        
    def wait(self, seconds: float = 1):
        """Wait with loading multiplier"""
        multiplier = float(self.config.get('ADVANCED', 'loadingMuliplier', fallback='1.0'))
        time.sleep(seconds * multiplier)
