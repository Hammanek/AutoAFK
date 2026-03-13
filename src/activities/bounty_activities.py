"""Bounty board and dispatch activities"""
import logging
from src.activities.base_activity import BaseActivity

logger = logging.getLogger(__name__)


class BountyActivities(BaseActivity):
    """Handles bounty board dispatches"""
    
    def handle_bounties(self) -> bool:
        """Handle bounty board dispatches"""
        logger.blue("Handling Bounty Board...")
        
        self.controller.confirm_location('darkforest', 
                                        region=self.controller.BOUNDARIES['darkforestSelect'])
        self.controller.tap(600, 1320)
        
        if self.image.is_visible('labels/bountyboard', retry=3):
            # Solo bounties
            if self.config.getboolean('BOUNTIES', 'dispatchsolobounties', fallback=False):
                self.controller.tap(650, 1700)  # Solo tab
                self.image.click_image('buttons/collect_all', seconds=3, suppress=True)
                
                remaining = self.config.getint('BOUNTIES', 'remaining', fallback=2)
                refreshes = self.config.getint('BOUNTIES', 'refreshes', fallback=3)
                self._dispatch_solo_bounties(remaining=remaining, max_refreshes=refreshes)
                
            # Team bounties
            if self.config.getboolean('BOUNTIES', 'dispatchteambounties', fallback=False):
                self.controller.tap(950, 1700)  # Team tab
                self.image.click_image('buttons/collect_all', seconds=2, suppress=True)
                self.image.click_image('buttons/dispatch', confidence=0.8, suppress=True, 
                                      grayscale=True)
                self.image.click_image('buttons/confirm', suppress=True)
                
            # Event bounties
            if self.config.getboolean('BOUNTIES', 'dispatcheventbounties', fallback=False):
                if self.image.is_visible('labels/event_bounty', click=True):
                    self.image.click_image('buttons/collect_all', seconds=2, suppress=True)
                    
                    while self.image.is_visible('buttons/dispatch_bounties', click=True):
                        self.controller.tap(530, 1030, seconds=2)
                        self.controller.tap(120, 1500)
                        self.image.click_image('buttons/dispatch', confidence=0.8, 
                                              grayscale=True)
                        
            self.image.click_image('buttons/back', region=self.controller.BOUNDARIES['backMenu'])
            logger.green("Bounties attempted successfully")
            self.controller.recover(silent=True)
            return True
        else:
            logger.error("Bounty Board not found")
            self.controller.recover()
            return False
            
    def _dispatch_solo_bounties(self, remaining: int = 2, max_refreshes: int = 3):
        """Dispatch solo bounties with refreshes"""
        refreshes = 0
        
        while refreshes <= max_refreshes:
            if refreshes > 0:
                logger.warning(f"Board refreshed (#{refreshes})")
                
            # Dispatch visible bounties
            self._dispatcher(self._return_dispatch_buttons())
            
            # Scroll and dispatch more
            self.controller.swipe(550, 800, 550, 500, duration=200, seconds=2)
            self._dispatcher(self._return_dispatch_buttons(scrolled=True))
            
            # Check if we should dispatch remaining
            if refreshes >= 1:
                if len(self._return_dispatch_buttons(scrolled=True)) <= remaining:
                    logger.warning(f"{remaining} or less bounties remaining, dispatching...")
                    self.image.click_image('buttons/dispatch', confidence=0.8, 
                                          suppress=True, grayscale=True)
                    self.image.click_image('buttons/confirm', suppress=True)
                    return
                    
            # Refresh if not at max
            if refreshes < max_refreshes:
                self.controller.tap(90, 250)
                self.controller.tap(700, 1250)
                
            refreshes += 1
            
        logger.info(f"{max_refreshes} refreshes done, dispatching remaining...")
        self.image.click_image('buttons/dispatch', confidence=0.8, suppress=True, 
                              grayscale=True)
        self.image.click_image('buttons/confirm', suppress=True)
        
    def _return_dispatch_buttons(self, scrolled: bool = False) -> list:
        """Find dispatch buttons on screen"""
        locations = [(820, 430, 170, 120), (820, 650, 170, 120), (820, 860, 170, 120), 
                    (820, 1070, 170, 120), (820, 1280, 170, 120)]
        locations_scrolled = [(820, 460, 170, 160), (820, 670, 170, 160), (820, 880, 170, 160), 
                             (820, 1090, 170, 160), (820, 1300, 170, 160)]
        
        dispatch_buttons = []
        locs = locations_scrolled if scrolled else locations
        
        for loc in locs:
            if self.image.find_image('buttons/dispatch_bounties', confidence=0.9, 
                                    region=loc):
                # Return Y coordinate of button center
                dispatch_buttons.append(round(loc[1] + (loc[3] / 2)))
        
        dispatch_buttons.sort()
        return dispatch_buttons
        
    def _dispatcher(self, dispatch_list: list):
        """Dispatch bounties from list of button positions"""
        bounty_types = {
            'dust': 'labels/bounties/dust',
            'diamonds': 'labels/bounties/diamonds',
            'juice': 'labels/bounties/juice',
            'shards': 'labels/bounties/shards',
            'gold': 'labels/bounties/gold',
            'soulstone': 'labels/bounties/soulstone'
        }
        
        for button_y in dispatch_list:
            # Check resource type for this bounty
            for resource, image in bounty_types.items():
                if self.image.is_visible(image, region=(30, button_y - 100, 140, 160), 
                                        suppress=True):
                    # Check if we should dispatch this resource
                    if resource not in ['gold', 'soulstone']:
                        if self.config.getboolean('BOUNTIES', f'dispatch{resource}', fallback=False):
                            logger.blue(f"Dispatching {resource.title()}")
                            self.controller.tap(900, button_y)
                            self.controller.tap(350, 1150)
                            self.controller.tap(750, 1150)
                    else:
                        # Always dispatch gold and soulstone
                        logger.blue(f"Dispatching {resource.title()}")
                        self.controller.tap(900, button_y)
                        self.controller.tap(350, 1150)
                        self.controller.tap(750, 1150)
                    break  # Move to next button

