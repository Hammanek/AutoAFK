"""Activity Manager - Centralized management of all activity modules"""
from typing import Optional
import logging

from src.activities.daily_activities import DailyActivities
from src.activities.arena_activities import ArenaActivities
from src.activities.guild_activities import GuildActivities
from src.activities.bounty_activities import BountyActivities
from src.activities.shop_activities import ShopActivities
from src.activities.tower_activities import TowerActivities
from src.activities.misc_activities import MiscActivities
from src.activities.summon_activities import SummonActivities
from src.activities.labyrinth_activities import LabyrinthActivities
from src.activities.campaign_activities import CampaignActivities

logger = logging.getLogger(__name__)


class ActivityManager:
    """Manages all activity modules"""
    
    def __init__(self, device_manager, image_recognition, game_controller, 
                 config, notification_manager=None):
        """Initialize all activity modules
        
        Args:
            device_manager: Device manager instance
            image_recognition: Image recognition instance
            game_controller: Game controller instance
            config: Configuration instance
            notification_manager: Optional notification manager
        """
        self.device_manager = device_manager
        self.image_recognition = image_recognition
        self.game_controller = game_controller
        self.config = config
        self.notification_manager = notification_manager
        
        # Initialize all activity modules
        self.daily = DailyActivities(device_manager, image_recognition, 
                                    game_controller, config, notification_manager)
        self.arena = ArenaActivities(device_manager, image_recognition,
                                    game_controller, config, notification_manager)
        self.guild = GuildActivities(device_manager, image_recognition,
                                    game_controller, config, notification_manager)
        self.bounty = BountyActivities(device_manager, image_recognition,
                                      game_controller, config, notification_manager)
        self.shop = ShopActivities(device_manager, image_recognition,
                                  game_controller, config, notification_manager)
        self.tower = TowerActivities(device_manager, image_recognition,
                                    game_controller, config, notification_manager)
        self.misc = MiscActivities(device_manager, image_recognition,
                                  game_controller, config, notification_manager)
        self.summon = SummonActivities(device_manager, image_recognition,
                                      game_controller, config, notification_manager)
        self.labyrinth = LabyrinthActivities(device_manager, image_recognition,
                                            game_controller, config, notification_manager)
        self.campaign = CampaignActivities(device_manager, image_recognition,
                                          game_controller, config, notification_manager)
        
        logger.debug("ActivityManager initialized with all modules")
    
    def get_all(self) -> dict:
        """Get all activity modules as dictionary
        
        Returns:
            dict: Dictionary with all activity modules
        """
        return {
            'daily': self.daily,
            'arena': self.arena,
            'guild': self.guild,
            'bounty': self.bounty,
            'shop': self.shop,
            'tower': self.tower,
            'misc': self.misc,
            'summon': self.summon,
            'labyrinth': self.labyrinth,
            'campaign': self.campaign
        }
