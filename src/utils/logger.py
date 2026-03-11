"""Logging configuration and utilities"""
import logging
import sys
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# Global device manager for screenshot capture
_device_manager = None

def set_device_manager(device_manager):
    """Set global device manager for screenshot capture on errors"""
    global _device_manager
    _device_manager = device_manager

def add_notification_handler(notification_manager):
    """Add notification handler to send logs to Discord/Telegram"""
    if notification_manager:
        handler = NotificationHandler(notification_manager)
        handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(handler)

# Custom log levels matching old version colors
BLUE = 25      # Between INFO(20) and WARNING(30)
GREEN = 22     # Between INFO(20) and WARNING(30)
PURPLE = 23    # Between INFO(20) and WARNING(30)

# Add custom levels to logging
logging.addLevelName(BLUE, 'BLUE')
logging.addLevelName(GREEN, 'GREEN')
logging.addLevelName(PURPLE, 'PURPLE')


class ColoredFormatter(logging.Formatter):
    """Custom formatter with timestamps and clean output"""
    
    def format(self, record):
        # Add timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Format the message
        message = record.getMessage()
        
        # Return formatted message with timestamp
        return f"[{timestamp}] {message}"


class ScreenshotOnErrorHandler(logging.Handler):
    """Handler that saves screenshot on ERROR level logs"""
    
    def emit(self, record):
        """Save screenshot when error is logged"""
        global _device_manager
        
        # Skip screenshot if error is from device_manager (to avoid recursion)
        if 'device_manager' in record.name or 'Screenshot error' in record.getMessage():
            return
        
        if record.levelno >= logging.ERROR and _device_manager:
            try:
                # Save screenshot directly using device manager
                import re
                debug_dir = 'debug'
                if not os.path.exists(debug_dir):
                    os.makedirs(debug_dir)
                
                screenshot = _device_manager.get_screenshot()
                if not screenshot:
                    return
                
                # Clean error message for filename
                error_msg = record.getMessage()
                clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', error_msg.lower())
                clean_name = re.sub(r'_+', '_', clean_name)
                clean_name = clean_name.strip('_')
                
                # Limit length
                if len(clean_name) > 50:
                    clean_name = clean_name[:50]
                
                timestamp = int(time.time())
                filename = f"{clean_name}_{timestamp}.png"
                screenshot.save(os.path.join(debug_dir, filename))
                
                # Log that screenshot was saved (using print to avoid recursion)
                print(f"[DEBUG] Screenshot saved: {filename}")
            except Exception as e:
                # Don't let screenshot failure break logging
                print(f"[DEBUG] Screenshot save failed: {e}")


class NotificationHandler(logging.Handler):
    """Handler that sends log messages to Discord/Telegram"""
    
    def __init__(self, notification_manager):
        super().__init__()
        self.notification_manager = notification_manager
        
    def emit(self, record):
        """Send log message to notification services"""
        if not self.notification_manager:
            return
            
        try:
            msg = record.getMessage()
            level_name = logging.getLevelName(record.levelno)
            
            # Send all INFO and above messages
            if record.levelno >= logging.INFO:
                self.notification_manager.send(msg, level_name)
        except Exception:
            pass  # Silently ignore notification failures


# Add custom methods to Logger class
def blue(self, message, *args, **kwargs):
    """Log message in blue (action start)"""
    if self.isEnabledFor(BLUE):
        self._log(BLUE, message, args, **kwargs)

def green(self, message, *args, **kwargs):
    """Log message in green (success)"""
    if self.isEnabledFor(GREEN):
        self._log(GREEN, message, args, **kwargs)

def purple(self, message, *args, **kwargs):
    """Log message in purple (special actions)"""
    if self.isEnabledFor(PURPLE):
        self._log(PURPLE, message, args, **kwargs)

# Add methods to Logger class
logging.Logger.blue = blue
logging.Logger.green = green
logging.Logger.purple = purple


class Logger:
    """Centralized logging manager"""
    
    _instance: Optional['Logger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not Logger._initialized:
            self._setup_logging()
            Logger._initialized = True
            
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'afk_arena_bot_{timestamp}.log'
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Console handler with color prefixes
        # In compiled version, sys.stdout might be None, so check first
        if sys.stdout is not None:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            # Simple format without level name (will be added as prefix by ColoredFormatter)
            console_formatter = ColoredFormatter(
                '%(message)s'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # File handler with full details
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Screenshot handler for errors
        screenshot_handler = ScreenshotOnErrorHandler()
        screenshot_handler.setLevel(logging.ERROR)
        
        # Add handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(screenshot_handler)
        
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get logger instance for module"""
        return logging.getLogger(name)
