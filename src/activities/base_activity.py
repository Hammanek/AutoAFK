"""Base class for all game activities"""
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)


class BaseActivity:
    """Base class for game activities"""
    
    def __init__(self, 
                 device,
                 image_rec,
                 game_ctrl,
                 config,
                 notifier = None):
        self.device = device
        self.image = image_rec
        self.controller = game_ctrl
        self.config = config
        self.notifier = notifier
        
    def wait(self, seconds: float = 1) -> None:
        """Wait with loading multiplier from config"""
        multiplier = float(self.config.get('ADVANCED', 'loadingMuliplier', fallback='1.0'))
        time.sleep(seconds * multiplier)
    
    def notify(self, message: str, level: str = 'INFO') -> None:
        """Send notification"""
        if self.notifier:
            self.notifier.send(message, level)
            
    def safe_execute(self, func, *args, **kwargs):
        """Execute function with error handling and recovery"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            self.notify(f"Error in {func.__name__}: {e}", level='ERROR')
            
            # Attempt recovery
            if self.controller.recover(silent=True):
                logger.info("Recovered to campaign screen")
                return None
            else:
                raise
