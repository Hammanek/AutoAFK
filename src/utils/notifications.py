"""Notification management for Discord, Telegram, and Desktop"""
import os
import requests
from typing import Optional
from textwrap import dedent
from pathlib import Path

from src.core.config import Config
from src.utils.logger import Logger

logger = Logger.get_logger(__name__)


class NotificationManager:
    """Manages notifications across multiple platforms"""
    
    def __init__(self, config: Config):
        self.config = config
        self.discord = None
        self.telegram = None
        self.desktop_enabled = True
        
        self._initialize_services()
        
    def _initialize_services(self):
        """Initialize notification services based on config"""
        # Discord
        if self.config.getboolean('DISCORD', 'enable', fallback=False):
            channel_id = self.config.get('DISCORD', 'channel_id', fallback='')
            token = self.config.get('DISCORD', 'token', fallback='')
            if channel_id and token:
                self.discord = DiscordNotifier(channel_id, token)
                logger.info("Discord notifications enabled")
                
        # Telegram
        if self.config.getboolean('TELEGRAM', 'enable', fallback=False):
            bot_token = self.config.get('TELEGRAM', 'token', fallback='')
            chat_id = self.config.get('TELEGRAM', 'chat_id', fallback='')
            disable_notification = self.config.getboolean('TELEGRAM', 'disable_notification', fallback=False)
            if bot_token and chat_id:
                self.telegram = TelegramNotifier(bot_token, chat_id, disable_notification)
                logger.info("Telegram notifications enabled")
                
    def send(self, message: str, level: str = 'INFO') -> None:
        """Send notification to all enabled services"""
        # Clean message for external services
        cleaned_message = self._clean_message(message)
        
        # Discord
        if self.discord:
            try:
                self.discord.send(cleaned_message)
            except Exception:
                pass  # Silently ignore notification failures
                
        # Telegram
        if self.telegram:
            try:
                self.telegram.send(cleaned_message)
            except Exception:
                pass  # Silently ignore notification failures
                
        # Desktop notification for important messages
        if self.desktop_enabled and level in ['ERROR', 'CRITICAL']:
            try:
                self._send_desktop(cleaned_message)
            except Exception:
                pass  # Silently ignore notification failures
    
    def send_notification(self, title: str, message: str) -> None:
        """Send Windows desktop notification"""
        try:
            from plyer import notification
            
            icon_paths = [
                Path('img/auto.ico'),
                Path('_internal/img/auto.ico')
            ]
            
            icon_path = None
            for path in icon_paths:
                if path.exists():
                    icon_path = str(path)
                    break
                    
            notification.notify(
                title=title,
                message=message[:256],  # Limit message length
                app_icon=icon_path,
                timeout=10
            )
        except ImportError:
            logger.debug("plyer not available for desktop notifications")
        except Exception as e:
            logger.debug(f"Desktop notification failed: {e}")
                
    def _clean_message(self, message: str) -> str:
        """Clean message by removing color codes"""
        prefixes = ['ERR', 'WAR', 'GRE', 'BLU', 'PUR', 'INF']
        for prefix in prefixes:
            if message.startswith(prefix):
                return message[3:].strip()
        return message
        
    def _send_desktop(self, message: str):
        """Send desktop notification"""
        try:
            from plyer import notification
            
            icon_paths = [
                Path('img/auto.ico'),
                Path('_internal/img/auto.ico')
            ]
            
            icon_path = None
            for path in icon_paths:
                if path.exists():
                    icon_path = str(path)
                    break
                    
            notification.notify(
                title='AutoAFK',
                message=message[:256],  # Limit message length
                app_icon=icon_path,
                timeout=5
            )
        except ImportError:
            logger.debug("plyer not available for desktop notifications")


class DiscordNotifier:
    """Discord webhook notifier"""
    
    def __init__(self, channel_id: str, token: str):
        self.webhook_url = f"https://discord.com/api/webhooks/{channel_id}/{token}"
        
    def send(self, message: str) -> dict:
        """Send message to Discord"""
        response = requests.post(
            url=self.webhook_url,
            json={"content": dedent(message)},
            timeout=10
        )
        
        return {
            "status_code": response.status_code,
            "response": response.text
        }


class TelegramNotifier:
    """Telegram bot notifier"""
    
    def __init__(self, bot_token: str, chat_id: str, disable_notification: bool = False):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.disable_notification = disable_notification
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
    def send(self, message: str) -> dict:
        """Send message to Telegram"""
        response = requests.post(
            url=self.api_url,
            json={
                "chat_id": self.chat_id,
                "text": dedent(message),
                "disable_web_page_preview": True,
                "disable_notification": self.disable_notification
            },
            timeout=10
        )
        
        return {
            "status_code": response.status_code,
            "response": response.text
        }
