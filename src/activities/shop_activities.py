"""Shop and merchant activities"""
import logging
from src.activities.base_activity import BaseActivity

logger = logging.getLogger(__name__)


class ShopActivities(BaseActivity):
    """Handles shop purchases and merchant"""
    
    def shop_purchases(self, shop_refreshes: int, skip_quick: int = 0) -> bool:
        """Handle shop purchases with refreshes"""
        if self.config.getboolean('SHOP', 'quick', fallback=False) and skip_quick == 0:
            return self._shop_purchases_quick(shop_refreshes)
            
        logger.info(f"Attempting store purchases (Refreshes: {shop_refreshes})")
        counter = 0
        
        self.controller.confirm_location('ranhorn', 
                                        region=self.controller.BOUNDARIES['ranhornSelect'])
        self.wait(2)
        self.controller.tap(440, 1750)
        
        # Wait for store screen (max 5s)
        if self.image.wait_for_image('labels/store', timeout=5, check_interval=0.3):
            # First purchases
            self._handle_shop_purchasing(counter)
            
            # Refresh purchases
            while counter < shop_refreshes:
                self.controller.tap(1000, 300)
                self.image.click_image('buttons/confirm', suppress=True, seconds=5)
                counter += 1
                logger.green(f"Refreshed store {counter} times")
                self._handle_shop_purchasing(counter)
                
            self.image.click_image('buttons/back')
            logger.green("Store purchases attempted")
            self.wait(2)  # Wait before next task as loading ranhorn can be slow
            return True
        else:
            logger.error("Store not found")
            self.controller.recover()
            return False
            
    def _shop_purchases_quick(self, shop_refreshes: int) -> bool:
        """Quick buy shop items"""
        logger.info(f"Attempting store quickbuys (Refreshes: {shop_refreshes})")
        counter = 0
        
        self.controller.confirm_location('ranhorn')
        self.wait(2)
        self.controller.tap(440, 1750, seconds=5)  # Wait for store to load
        
        # Check for store screen with more retries
        if self.image.is_visible('labels/store', retry=3):
            if self.image.is_visible('buttons/quickbuy', click=True):
                self.wait(1)
                self.image.click_image('buttons/purchase', seconds=5)
                self.controller.tap(970, 90, seconds=2)
                
                while counter < shop_refreshes:
                    self.controller.tap(1000, 300)
                    self.image.click_image('buttons/confirm', suppress=True, seconds=4)
                    self.image.click_image('buttons/quickbuy', seconds=2)
                    self.image.click_image('buttons/purchase', seconds=2)
                    self.controller.tap(970, 90)
                    counter += 1
                    
                self.image.click_image('buttons/back')
                logger.green("Store purchases attempted")
                return True
            else:
                logger.info("Quickbuy not found, switching to old style")
                self.image.click_image('buttons/back')
                return self.shop_purchases(shop_refreshes, 1)
        else:
            logger.error("Store not found")
            self.controller.recover()
            return False

    def _handle_shop_purchasing(self, counter: int):
        """Purchase items from shop based on config

        Args:
            counter: Current refresh counter (affects purchase limits)
        """
        # Re-read config for updated values
        self.config.read(self.config.get('DEFAULT', 'settings_file', fallback='settings.ini'))

        # Top row items with coordinates
        top_row = {
            'arcanestaffs': [180, 920],
            'cores': [425, 920],
            'timegazer': [650, 920],
            'baits': [875, 920]
        }

        # Bottom row items with image buttons
        bottom_row = {
            'dust_gold': 'buttons/shop/dust',
            'shards_gold': 'buttons/shop/shards_gold',
            'dust_diamond': 'buttons/shop/dust_diamonds',
            'elite_soulstone': 'buttons/shop/soulstone',
            'superb_soulstone': 'buttons/shop/superstone',
            'silver_emblem': 'buttons/shop/silver_emblems',
            'gold_emblem': 'buttons/shop/gold_emblems',
            'poe': 'buttons/shop/poe'
        }

        # Name translations for console output
        name_map = {
            'dust_gold': 'Dust (Gold)',
            'shards_gold': 'Shards',
            'dust_diamond': 'Dust (Diamonds)',
            'elite_soulstone': 'Elite Soulstone',
            'superb_soulstone': 'Superb Soulstone',
            'silver_emblem': 'Silver Emblems',
            'gold_emblem': 'Gold Emblems',
            'poe': 'Poe Coins (Gold)',
            'arcanestaffs': 'Arcane Staffs',
            'cores': 'Elemental Cores',
            'timegazer': 'Timegazer Card',
            'baits': 'Bait'
        }

        # Purchase top row items
        for item, pos in top_row.items():
            if self.config.getboolean('SHOP', item, fallback=False):
                # Purchase limits based on refresh counter
                if item == 'timegazer' and counter > 0:  # Only one TG card
                    continue
                if item == 'baits' and counter > 1:  # Only two baits
                    continue
                if (item == 'cores' or item == 'arcanestaffs') and counter > 2:  # Only three
                    continue

                logger.purple(f"    Buying: {name_map.get(item, item)}")
                self.controller.tap(pos[0], pos[1])
                self.image.click_image('buttons/shop/purchase', suppress=True)
                self.controller.tap(550, 1220, seconds=2)

        # Scroll down to see bottom rows
        self.controller.swipe(550, 1500, 550, 1200, 500, seconds=5)

        # Purchase bottom row items
        for item, button in bottom_row.items():
            if self.config.getboolean('SHOP', item, fallback=False):
                if self.image.is_visible(button, confidence=0.95, click=True):
                    logger.purple(f"    Buying: {name_map.get(item, item)}")
                    self.image.click_image('buttons/shop/purchase', suppress=True)
                    self.controller.tap(550, 1220)

        self.wait(3)  # Long wait else Twisted Realm isn't found after if enabled

    def clear_merchant(self) -> bool:
        """Collect merchant deals and nobles"""
        logger.blue("Attempting to collect merchant deals")

        self.controller.tap(120, 300, seconds=5)

        # Check for Fun in the Wild event
        if self.image.is_visible('buttons/funinthewild', click=True, seconds=2):
            self.controller.tap(250, 1820, seconds=2)  # Ticket
            self.controller.tap(250, 1820, seconds=2)  # Reward

        # Swipe to nobles section
        self.controller.swipe(1000, 1825, 100, 1825, 500)

        # Handle Noble Society
        if self.image.is_visible('buttons/noblesociety'):
            logger.purple("    Collecting Nobles")
            self.controller.tap(675, 1825)

            if self.image.is_visible('buttons/confirm_nobles', confidence=0.8, retry=2):
                logger.warning("Noble resource collection screen found, skipping Noble collection")
                self.controller.tap(70, 1810)
            else:
                # Champion rewards
                self.controller.tap(750, 1600)  # Icon
                self.controller.tap(440, 1470, seconds=0.5)
                self.controller.tap(440, 1290, seconds=0.5)
                self.controller.tap(440, 1100, seconds=0.5)
                self.controller.tap(440, 915, seconds=0.5)
                self.controller.tap(440, 725, seconds=0.5)
                self.controller.tap(750, 1600)  # Close icon

                # Twisted rewards
                self.controller.tap(600, 1600)  # Icon
                self.controller.tap(440, 1470, seconds=0.5)
                self.controller.tap(440, 1290, seconds=0.5)
                self.controller.tap(440, 1100, seconds=0.5)
                self.controller.tap(440, 915, seconds=0.5)
                self.controller.tap(440, 725, seconds=0.5)
                self.controller.tap(600, 1600)  # Close icon

                # Regal rewards
                self.controller.tap(450, 1600)  # Icon
                self.controller.tap(440, 1470, seconds=0.5)
                self.controller.tap(440, 1290, seconds=0.5)
                self.controller.tap(440, 1100, seconds=0.5)
                self.controller.tap(440, 915, seconds=0.5)
                self.controller.tap(440, 725, seconds=0.5)
                self.controller.tap(450, 1600)  # Close icon

            # Monthly Cards
            logger.purple("    Collecting Monthly Cards")
            self.controller.tap(180, 1600)

            # Monthly card
            self.controller.tap(300, 1000, seconds=3)
            self.controller.tap(560, 430)

            # Deluxe Monthly card
            self.controller.tap(850, 1000, seconds=3)
            self.controller.tap(560, 430)

        # Trade post
        if self.image.is_visible('buttons/tradepost', click=True):
            # Special Deal, no check as its active daily
            logger.purple("    Collecting Special Deal")
            self.image.click_image('buttons/dailydeals')
            self.controller.tap(150, 1625)
            self.controller.tap(150, 1625)
            
            # Daily Deal
            if self.image.is_visible('buttons/merchant_daily', confidence=0.8, retry=2, click=True):
                logger.purple("    Collecting Daily Deal")
                self.controller.swipe(550, 1400, 550, 1200, 500, seconds=3)
                self.image.click_image('buttons/dailydeals', confidence=0.8, retry=2)
                self.controller.tap(400, 1675, seconds=3)
            
            # Biweeklies (Wednesday only)
            import datetime
            if datetime.datetime.now().isoweekday() == 3:  # Wednesday
                if self.image.is_visible('buttons/merchant_biweekly', confidence=0.8, retry=2, click=True):
                    logger.purple("    Collecting Bi-weekly Deal")
                    self.controller.swipe(300, 1400, 200, 1200, 500, seconds=3)
                    self.controller.tap(200, 1200)
                    self.controller.tap(550, 1625, seconds=3)

        self.wait(1)
        self.controller.swipe(200, 1825, 450, 1825, 1000)
        self.wait(1)  # wait for the swipe to finish

        # Wishing Ship
        if self.image.is_visible('buttons/wishingship', click=True, seconds=2):
            # Yuexi (Monday only)
            import datetime
            if datetime.datetime.now().isoweekday() == 1:  # Monday
                logger.purple("    Collecting Yuexi")
                self.controller.tap(250, 1600)
                self.controller.tap(240, 880)
                self.controller.tap(150, 1625, seconds=2)
                self.controller.tap(950, 200)
                self.controller.tap(730, 1050)
                self.controller.tap(150, 1625, seconds=2)
                self.controller.tap(900, 400, seconds=2)
            
            # Clear Rhapsody bundles notification
            logger.purple("    Clearing Rhapsody bundles notification")
            self.controller.tap(620, 1600)
            self.controller.tap(980, 200)
            self.controller.tap(70, 1810)
            self.controller.tap(70, 1810)

        logger.green("Merchant deals collected")
        self.controller.recover(silent=True)
        return True
