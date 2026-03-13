"""Daily activities implementation"""
import logging
from src.activities.base_activity import BaseActivity

logger = logging.getLogger(__name__)


class DailyActivities(BaseActivity):
    """Handles daily activities"""
    
    def collect_afk_rewards(self) -> bool:
        """Collect AFK chest rewards"""
        logger.blue("Collecting AFK rewards...")
        
        self.controller.confirm_location('campaign', region=self.controller.BOUNDARIES['campaignSelect'])
        
        if self.image.is_visible('buttons/campaign_selected', 
                                 region=self.controller.BOUNDARIES['campaignSelect']):
            self.controller.tap(550, 1550)
            self.image.click_image('buttons/collect', confidence=0.8, 
                                  region=self.controller.BOUNDARIES['collectAfk'])
            
            # Clear popups
            self.controller.tap(550, 1800, seconds=1)
            self.controller.tap(550, 1800, seconds=1)
            self.controller.tap(550, 1800, seconds=1)
            
            logger.green("AFK rewards collected")
            return True
        else:
            logger.error("Campaign screen not found, recovering and retrying...")
            self.controller.recover()
            # Retry once in case there was a popup
            return self.collect_afk_rewards()
            
    def collect_mail(self) -> bool:
        """Collect mail rewards"""
        logger.blue("Collecting mail...")
        
        if self.image.is_visible('buttons/mail', region=self.controller.BOUNDARIES['mailLocate']):
            self.controller.wait()
            self.controller.tap(960, 630, seconds=2)
            self.image.click_image('buttons/collect_all')
            self.controller.tap(550, 1600)  # Clear popups
            
            # Delete mail if configured
            if self.config.getboolean('DAILIES', 'deletemail', fallback=False):
                self.controller.tap(300, 1600)
                self.controller.tap(700, 1260)
                
            self.image.click_image('buttons/back', region=self.controller.BOUNDARIES['backMenu'])
            logger.green("Mail collected!")
            return True
        else:
            logger.error("Mail icon not found!")
            return False
            
    def collect_companion_points(self, lend_mercs: bool = False) -> bool:
        """Send/receive companion points"""
        logger.blue("Collecting companion points...")
        
        if self.image.is_visible('buttons/friends', region=self.controller.BOUNDARIES['friends']):
            # Check for notification (red pixel)
            red_value = self.image.check_pixel(1020, 720, 0)
            if red_value > 220:
                self.controller.tap(960, 810)
                self.image.click_image('buttons/sendandreceive', 
                                      region=self.controller.BOUNDARIES['sendrecieve'])
                
                if lend_mercs:
                    self.controller.tap(720, 1760)  # Short term
                    self.controller.tap(990, 190)   # Manage
                    self.controller.tap(630, 1590)  # Apply
                    self.controller.tap(750, 1410)  # Auto lend
                    self.image.click_image('buttons/exitmenu')
                    logger.green("Mercenaries lent out")
                    
                self.image.click_image('buttons/back', region=self.controller.BOUNDARIES['backMenu'])
                logger.green("Friends Points Sent")
                return True
            else:
                logger.error("Friends notification not found")
                return True
        else:
            logger.warning("Friends icon not found")
            return False
            
    def collect_fast_rewards(self, count: int) -> bool:
        """Collect fast rewards"""
        logger.blue(f"Attempting to collecting Fast Rewards {count}x times")
        counter = 0
        
        self.controller.confirm_location('campaign', region=self.controller.BOUNDARIES['campaignSelect'])
        
        if self.image.is_visible('buttons/fastrewards', 
                                 region=self.controller.BOUNDARIES['fastrewards']):
            # Check for notification
            red1 = self.image.check_pixel(956, 1620, 0)
            red2 = self.image.check_pixel(860, 1615, 0)
            
            if red1 > 220 or red2 > 220:
                self.image.click_image('buttons/fastrewards', 
                                      region=self.controller.BOUNDARIES['fastrewards'])
                
                while counter < count:
                    self.controller.tap(710, 1260, seconds=3)
                    self.controller.tap(550, 1800)
                    counter = counter + 1
                    
                self.image.click_image('buttons/close', region=self.controller.BOUNDARIES['closeFR'])
                logger.green("Fast Rewards Done")
                return True
            else:
                logger.warning("Fast Rewards already done")
                return True
        else:
            logger.error("Fast Rewards icon not found!")
            return False
            
    def attempt_campaign(self) -> bool:
        """Start and exit a campaign battle for daily quest"""
        logger.blue("Attempting Campaign battle...")
        
        self.controller.confirm_location('campaign', region=self.controller.BOUNDARIES['campaignSelect'])
        
        self.image.click_image('buttons/begin', seconds=2, retry=3, 
                              region=self.controller.BOUNDARIES['begin'])
        
        # Check for multi-stage
        multi = self.image.is_visible('buttons/begin', confidence=0.7, retry=3,
                                     region=self.controller.BOUNDARIES['multiBegin'])
        if multi:
            self.image.click_image('buttons/begin', confidence=0.7, retry=5, seconds=2,
                                  region=self.controller.BOUNDARIES['multiBegin'],
                                  retry_interval=0.3)
            
        # Wait for hero selection screen (retry=20 as first load can be slow)
        if self.image.is_visible('buttons/heroclassselect', retry=20,
                                region=self.controller.BOUNDARIES['heroclassselect']):
            self.image.click_image('buttons/battle', confidence=0.8, retry=3, seconds=3,
                                  region=self.controller.BOUNDARIES['battle'])
            
            # Exit battle
            self.image.click_image('buttons/pause', retry=3)
            self.image.click_image('buttons/exitbattle', retry=3)
            self.image.click_image('buttons/back', retry=3, seconds=3, suppress=True,
                                  region=self.controller.BOUNDARIES['backMenu'])
            self.controller.tap(20, 20)  # Clear popups
            
            if self.controller.confirm_location('campaign', change=False,
                                               region=self.controller.BOUNDARIES['campaignSelect']):
                logger.green("Campaign attempted successfully")
                return True
        else:
            logger.error("Something went wrong, attempting to recover")
            self.controller.recover()
            return False
            
    def collect_fountain_of_time(self) -> bool:
        """Collect Fountain of Time rewards"""
        logger.blue("Collecting Fountain of Time...")
        
        self.controller.confirm_location('darkforest', 
                                        region=self.controller.BOUNDARIES['darkforestSelect'])
        self.controller.tap(800, 700)
        
        # Wait for collect button to appear (max 4s)
        if self.image.wait_for_image('buttons/collect_wide', timeout=4, check_interval=0.3):
            self.controller.tap(550, 1450)
            self.controller.tap(290, 70)
            
        # Wait for temporal rift screen (max 3s)
        if self.image.wait_for_image('labels/temporalrift', timeout=3, check_interval=0.3):
            self.controller.tap(550, 1800)
            self.controller.tap(250, 1300)
            self.controller.tap(700, 1350)  # Collect
            
            # Clear popups
            self.controller.tap(550, 1800, seconds=3)
            self.controller.tap(550, 1800, seconds=3)
            self.controller.tap(550, 1800, seconds=3)
            
            self.image.click_image('buttons/back', region=self.controller.BOUNDARIES['backMenu'])
            logger.green("Fountain of Time collected")
            return True
        else:
            logger.warning("Temporal Rift not found")
            self.controller.recover()
            return False
            
    def collect_inn_gifts(self) -> bool:
        """Collect inn gifts"""
        logger.blue("Attempting daily Inn gift collection")
        
        self.controller.confirm_location('ranhorn', 
                                        region=self.controller.BOUNDARIES['ranhornSelect'])
        self.controller.wait()
        self.controller.tap(500, 200, seconds=4)  # Wait for animation
        
        # Check for manage button (retry 3x like old version)
        if self.image.is_visible('buttons/manage', retry=3):
            checks = 0
            while checks < 3:
                if self.image.is_visible('buttons/inn_gift', confidence=0.75, 
                                        region=(160, 1210, 500, 100), seconds=2, click=True):
                    self.controller.tap(550, 1400, seconds=0.5)  # Clear loot
                    self.controller.tap(550, 1400, seconds=0.5)  # Clear loot
                    continue
                checks += 1
                self.controller.wait()
            logger.green("Inn Gifts collected")
            self.controller.recover(silent=True)
            return True
        else:
            logger.error("Inn not found, attempting to recover")
            self.controller.recover()
            return False
            
    def collect_quests(self) -> bool:
        """Collect daily and weekly quest rewards"""
        logger.blue("Collecting quest rewards...")
        
        # Open quests menu
        self.controller.tap(960, 250, seconds=2)
        
        if self.image.is_visible('labels/quests'):
            # Dailies
            self.controller.tap(400, 1650)
            if self.image.is_visible('labels/questcomplete'):
                logger.green("Daily quests found, collecting...")
                self.controller.tap(930, 680, seconds=4)  # Click top quest
                self.image.click_image('buttons/fullquestchest', seconds=3, retry=3, suppress=True)
                self.controller.tap(400, 1650)
                
            # Weeklies
            self.controller.tap(600, 1650)
            if self.image.is_visible('labels/questcomplete'):
                logger.green("Weekly quests found, collecting...")
                self.controller.tap(930, 680, seconds=4)  # Click top quest
                self.image.click_image('buttons/fullquestchest', seconds=3, retry=3, suppress=True)
                self.controller.tap(600, 1650, seconds=2)
                self.controller.tap(600, 1650)  # Second tap in case of Limited Rewards popup
            self.controller.tap(1000, 500, seconds=2) # 150 points chest
            self.controller.tap(600, 1650, seconds=2)
            self.controller.tap(600, 1650)  # Second tap in case of Limited Rewards popup
            
            self.image.click_image('buttons/back', retry=3)
            logger.green("Quest rewards collected")
            return True
        else:
            logger.warning("Quests screen not found")
            self.controller.recover()
            return False
            
    def use_bag_consumables(self) -> bool:
        """Use consumables from bag"""
        logger.blue("Using bag consumables...")
        
        self.controller.tap(1000, 500, seconds=3)
        
        if self.image.is_visible('buttons/batchselect', retry=3):
            self.image.click_image('buttons/batchselect')
            
            if self.image.is_visible('buttons/confirm_grey'):
                logger.warning("Nothing selected/available! Returning...")
                self.image.click_image('buttons/back', region=self.controller.BOUNDARIES['backMenu'])
                return True
                
            self.controller.tap(550, 1650, seconds=2)
            
            # Wait for use button (without suppress - let it throw error naturally)
            crash_counter = 0
            while not self.image.is_visible('buttons/use_batch'):
                self.controller.tap(550, 1800, seconds=0)
                crash_counter += 1
                if crash_counter > 30:
                    logger.error("Something went wrong (normally gear chests being selected), returning...")
                    self.image.click_image('buttons/back', region=self.controller.BOUNDARIES['backMenu'])
                    self.image.click_image('buttons/back', region=self.controller.BOUNDARIES['backMenu'])
                    return False
                    
            self.controller.tap(550, 1800)  # Use
            self.controller.tap(950, 1700)  # All button to clear loot
            self.image.click_image('buttons/back', region=self.controller.BOUNDARIES['backMenu'], suppress=True)
            logger.green("Bag consumables used!")
            return True
        else:
            logger.error("Bag not found, attempting to recover")
            self.controller.recover()
            return False
            
    def level_up_heroes(self) -> bool:
        """Auto level up heroes"""
        logger.blue("Attempting to level up...")
        
        self.controller.confirm_location('ranhorn', 
                                        region=self.controller.BOUNDARIES['ranhornSelect'])
        self.controller.tap(700, 1500, seconds=2)  # Resonating crystal
        
        self.image.click_image('buttons/confirm', suppress=True)  # Confirm slot unlock
        
        if self.image.is_visible('buttons/level_up'):
            self.controller.tap(520, 1860, seconds=2)  # Level up
            self.controller.tap(710, 1260, seconds=3)  # Confirm
            self.controller.tap(700, 50, seconds=2)   # Clear message
            
        self.controller.tap(20, 20)  # Neutral location to clear any popups
        
        if self.image.is_visible('buttons/strengthen'):
            while self.image.is_visible('buttons/strengthen', seconds=0.2):
                self.controller.tap(520, 1860)
            logger.green("Leveled up successfully")
        else:
            logger.warning("Not enough dust to level up")
            
        self.controller.recover(silent=True)
        return True
