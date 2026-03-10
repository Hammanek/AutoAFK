"""Summoning and hero acquisition activities"""
import logging
from src.activities.base_activity import BaseActivity

logger = logging.getLogger(__name__)


class SummonActivities(BaseActivity):
    """Handles hero summoning"""
    
    def execute(self):
        """Execute summon activities"""
        self.logger.info("Starting summon activities...")
        
        # Get settings
        auto_summon = self.config.getboolean('SUMMONS', 'auto_summon', fallback=False)
        
        if auto_summon:
            self.summon_hero_scrolls()
            
        self.logger.info("Summon activities completed")
        
    def summon_hero_scroll(self) -> bool:
        """Summon a single hero using scroll"""
        logger.blue("Attempting to summon a hero...")
        
        self.controller.confirm_location('ranhorn', 
                                        region=self.controller.BOUNDARIES['ranhornSelect'])
        self.controller.tap(210, 1650)  # The Noble Tavern
        
        # Check if tavern is inactive
        if self.image.is_visible('buttons/noble_tavern_inactive', click=True):
            pass
            
        # Navigate to scroll summon
        for i in range(4):
            self.controller.tap(900, 1600)  # Next
            if self.image.is_visible('buttons/summon_scroll', click=True):
                self.wait(1)
                self.controller.tap(550, 900)  # Flip card
                logger.green("Hero summoned")
                break
                
        self.controller.recover(silent=True)
        return True
        
    def _check_summon_rarity(self) -> str:
        """Check rarity of summoned hero"""
        self.img.wait(1)
        
        # Check card border colors
        card_positions = [
            (95, 550), (95, 900), (95, 1350),
            (410, 250), (410, 650), (410, 1100),
            (410, 1550), (729, 550), (729, 900), (729, 1350)
        ]
        
        for x, y in card_positions:
            pixel = self.img.get_pixel_color(x, y)
            r, g, b = pixel
            
            # Yellow border = Awakened (Red & Green > 200)
            if r > 200 and g > 200:
                return 'Awakened'
                
            # Purple border = Epic (Red & Blue > 200)
            if r > 200 and b > 200:
                return 'Epic'
                
        return 'Rare'
        
    def infinite_summons(self, woke: str = None, celehypo: str = None, x6_mode: bool = False) -> bool:
        """Perform infinite summons until specific heroes found"""
        logger.blue("Attempting to run Unlimited Summons...")
        
        import time
        from math import ceil
        
        counter = 0
        start_time = time.time()
        
        # Hero mappings
        wokes = {
            'Awakened Talene': 'aTalene', 'Gavus': 'Gavus', 'Maetria': 'Maetria',
            'Awakened Ezizh': 'aEzizh', 'Awakened Thane': 'aThane', 
            'Awakened Belinda': 'aBelinda', 'Awakened Brutus': 'aBrutus',
            'Awakened Safiya': 'aSafiya', 'Awakened Lyca': 'aLyca',
            'Awakened Solise': 'aSolise', 'Awakened Baden': 'aBaden',
            'Awakened Shemira': 'aShemira', 'Awakened Athalia': 'aAthalia',
            'Awakened Antandra': 'aAntandra', 'Awakened Lucius': 'aLucius',
            'Awakened Eironn': 'aEironn', 'Awakened Estrilda': 'aEstrilda',
            'Awakened Thoran': 'aThoran', 'Envydiel': 'envydiel', 'Eugene': 'eugene'
        }
        
        celehypos = {
            'Audrae': 'audrae', 'Canisa and Ruke': 'cruke', 'Daemia': 'daemia',
            'Ezizh': 'ezizh', 'Khazard': 'khazard', 'Lavatune': 'lavatune',
            'Liberta': 'liberta', 'Lucilla': 'lucilla', 'Lucretia': 'lucretia',
            'Mehira': 'mehira', 'Mezoth': 'mezoth', 'Mortas': 'mortas',
            'Olgath': 'olgath', 'Talene': 'talene', 'Tarnos': 'tarnos',
            'Elijah and Lailah': 'twins', 'Veithael': 'vei', 'Vyloris': 'vyloris',
            'Zahprael': 'zaph', 'Zikis': 'zikis', 'Aurelia': 'aurelia',
            'Lysander': 'lysander', 'Malkrie': 'malkrie', 'Serenmira': 'serenmira',
            'Zohra': 'zohra'
        }
        
        # Check for summons button
        if not self.image.is_visible('buttons/summons/summons_sidebar'):
            logger.warning("Can't see summons event button, scrolling...")
            self.controller.swipe(50, 800, 50, 500, duration=500, seconds=1)
            
        if self.image.is_visible('buttons/summons/summons_sidebar', retry=3, click=True):
            search = True
            if woke and celehypo:
                logger.blue(f"Searching for: {woke} and {celehypo}")
            else:
                logger.blue("Summoning until resources exhausted")
                
            self.controller.tap(700, 1700, seconds=2)  # Summon Again
            
            while search:
                # Perform summon
                if x6_mode:
                    self.controller.tap(680, 1820)
                    self.controller.tap(950, 1820, seconds=0.5)
                    self.controller.tap(950, 1820, seconds=0.5)
                    self.wait(2)
                else:
                    self.controller.tap(680, 1820, seconds=0.1)
                    if not self.image.is_visible('buttons/checkbox_checked', suppress=True, 
                                                 seconds=0.5):
                        self.controller.tap(425, 1170, seconds=0.5)
                        self.controller.tap(700, 1260, seconds=0)
                    self.controller.tap(950, 1820)
                    self.controller.tap(950, 1820)
                    self.wait(2)
                    
                # Check rarity
                found = self._return_card_pulls_rarity()
                counter += 1
                
                if found == "Awakened":
                    logger.warning("Awakened Found")
                    if self._summons_crash_detector('awakened'):
                        return False
                        
                    # Check if it's the one we want
                    if woke and woke in wokes:
                        if self.image.is_visible(f'summons/awakeneds/{wokes[woke]}', 
                                                confidence=0.85, seconds=0.5):
                            logger.green(f"{woke} found! Checking for {celehypo}")
                            
                            # Check celehypo
                            if celehypo and celehypo in celehypos:
                                if self.image.is_visible(f'summons/celehypos/{celehypos[celehypo]}', 
                                                        confidence=0.85):
                                    logger.green(f"{celehypo} found too! Recording and exiting...")
                                    self.image.click_image('buttons/summons/record', 
                                                          confidence=0.85, retry=3, seconds=3)
                                    self.image.click_image('buttons/summons/change', 
                                                          confidence=0.85, retry=3, seconds=3, 
                                                          suppress=True)
                                    self.image.click_image('buttons/summons/confirm', 
                                                          confidence=0.85, retry=3, seconds=3, 
                                                          suppress=True)
                                    search = False
                                else:
                                    logger.warning(f"{celehypo} not found, continuing...")
                    else:
                        # No specific hero search, just continue
                        pass
                        
                elif found == 'Epic':
                    if self._summons_crash_detector('epic'):
                        return False
                    logger.debug("Epic Found")
                    
                elif found == 'Rare':
                    if self._summons_crash_detector('rare'):
                        return False
                        
                # Check if we should stop (no specific heroes to find)
                if not woke and not celehypo and counter >= 1000:
                    logger.green("Summon limit reached (1000)")
                    break
                    
            # Calculate duration
            duration = time.time() - start_time
            hours = str(ceil(duration // 3600))
            minutes = str((ceil(duration // 60)) - (int(hours) * 60))
            
            logger.green("Unlimited Summons finished!")
            logger.green(f"In just {counter} pulls and {hours} hours {minutes} minutes!")
            return True
        else:
            logger.error("Could not find Unlimited Summons button")
            return False
            
    def _return_card_pulls_rarity(self) -> str:
        """Check rarity of summoned cards"""
        self.wait(1)
        
        # Card positions to check
        card_positions = [
            (95, 550), (95, 900), (95, 1350),
            (410, 250), (410, 650), (410, 1100),
            (410, 1550), (729, 550), (729, 900), (729, 1350)
        ]
        
        for x, y in card_positions:
            r = self.image.check_pixel(x, y, 0)  # Red channel
            g = self.image.check_pixel(x, y, 1)  # Green channel
            b = self.image.check_pixel(x, y, 2)  # Blue channel
            
            # Yellow border = Awakened (Red & Green > 200)
            if r > 200 and g > 200:
                return 'Awakened'
                
            # Purple border = Epic (Red & Blue > 200)
            if r > 200 and b > 200:
                return 'Epic'
                
        return 'Rare'
        
    def _summons_crash_detector(self, summon_type: str) -> bool:
        """Detect if game has crashed during summons"""
        if not hasattr(self, '_rare_counter'):
            self._rare_counter = 0
            self._epic_counter = 0
            self._awakened_counter = 0
            
        if summon_type == 'rare':
            self._rare_counter += 1
            self._epic_counter = 0
            self._awakened_counter = 0
        elif summon_type == 'epic':
            self._rare_counter = 0
            self._epic_counter += 1
            self._awakened_counter = 0
        elif summon_type == 'awakened':
            self._rare_counter = 0
            self._epic_counter = 0
            self._awakened_counter += 1
            
        if (self._rare_counter >= 10 or self._epic_counter >= 10 or 
            self._awakened_counter >= 10):
            logger.error("10 of same type in a row, something went wrong!")
            self.controller.recover()
            self._rare_counter = 0
            self._epic_counter = 0
            self._awakened_counter = 0
            return True
            
        return False
        
    def get_mercenaries(self) -> bool:
        """Rent mercenary heroes (Sunday only for custom mercs)"""
        logger.blue("Getting mercenaries...")
        
        # Check if Sunday for custom mercs
        import datetime
        is_sunday = datetime.datetime.now().isoweekday() == 7
        
        if is_sunday:
            logger.blue("Getting custom mercs (Sunday)...")
            
        self.controller.confirm_location('ranhorn', 
                                        region=self.controller.BOUNDARIES['ranhornSelect'])
        self.controller.tap(960, 810)  # Friends
        self.controller.tap(725, 1760, seconds=2)  # Short-Term
        
        if is_sunday:
            # Try to get Lan
            self.controller.tap(1000, 1600)
            if self.image.is_visible('mercs/lan', click=True):
                while self.image.is_visible('buttons/apply', click=True):
                    self.wait(1)
                logger.green("Lan mercenary rented")
                
        # Rent any available mercenaries
        rented = 0
        for _ in range(5):
            if self.image.is_visible('buttons/apply', suppress=True, retry=1):
                self.image.click_image('buttons/apply')
                self.wait(1)
                rented += 1
            else:
                break
                
        logger.green(f"Rented {rented} mercenaries")
        self.controller.recover(silent=True)
        return True

