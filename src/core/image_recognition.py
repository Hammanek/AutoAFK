"""
Image Recognition Module
Handles template matching and image detection using original tools.py approach
"""
import os
import sys
import logging
import time
from typing import Optional, Tuple
from PIL import Image
from pyscreeze import locate

logger = logging.getLogger(__name__)


class ImageRecognition:
    """Handles image recognition and template matching"""
    
    def __init__(self, device_manager, config):
        self.device = device_manager
        self.config = config
        self.img_dir = self._find_img_directory()
        
    def _find_img_directory(self) -> str:
        """Find img directory (handles both source and compiled versions)"""
        # Check if running as compiled executable
        if getattr(sys, 'frozen', False):
            # Running as compiled - check _internal first
            base_path = sys._MEIPASS
            internal_img = os.path.join(base_path, 'img')
            if os.path.exists(internal_img):
                return internal_img
        
        # Try multiple locations for source version
        possible_paths = [
            'img',
            '../img',
            '../../img',
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'img')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        logger.warning("img directory not found, using default")
        return 'img'
        
    def find_image(self, image_name: str, confidence: float = 0.9, 
                   region: Tuple[int, int, int, int] = (0, 0, 1080, 1920),
                   grayscale: bool = False) -> Optional[Tuple[int, int, int, int]]:
        """Find image on screen and return coordinates"""
        screenshot = self.device.get_screenshot()
        
        # Build image path
        image_path = os.path.join(self.img_dir, f"{image_name}.png")
        if not os.path.exists(image_path):
            logger.debug(f"Image not found: {image_path}")
            return None
            
        try:
            search_img = Image.open(image_path)
            result = locate(search_img, screenshot, grayscale=grayscale, 
                          confidence=confidence, region=region)
            return result
        except Exception as e:
            logger.debug(f"Image search error for {image_name}: {e}")
            return None
            
    def is_visible(self, image_name: str, confidence: float = 0.9, 
                   seconds: float = 1, retry: int = 1,
                   region: Tuple[int, int, int, int] = (0, 0, 1080, 1920),
                   suppress: bool = False, click: bool = False,
                   retry_interval: float = 1.0) -> bool:
        """Check if image is visible on screen, optionally click it
        
        Args:
            image_name: Name of image to find (without .png)
            confidence: Match confidence (0.0-1.0)
            seconds: Time to wait after finding/not finding image
            retry: Number of attempts
            region: Screen region to search (x, y, width, height)
            suppress: Suppress debug logging if not found
            click: Click on image if found
            retry_interval: Time to wait between retry attempts (default 1.0s)
        """
        for attempt in range(retry):
            result = self.find_image(image_name, confidence, region)
            if result is not None:
                if click:
                    # Click on the image
                    x, y, w, h = result
                    x_center = round(x + w / 2)
                    y_center = round(y + h / 2)
                    self.device.tap(x_center, y_center)
                time.sleep(seconds * self._get_multiplier())
                return True
            if attempt < retry - 1:
                time.sleep(retry_interval * self._get_multiplier())
                
        if not suppress:
            logger.debug(f"Image {image_name} not found after {retry} attempts")
            # Screenshot is saved manually when logger.error is called
            
        time.sleep(seconds * self._get_multiplier())
        return False
        
    def click_image(self, image_name: str, confidence: float = 0.9, 
                    seconds: float = 1, retry: int = 1,
                    region: Tuple[int, int, int, int] = (0, 0, 1080, 1920),
                    suppress: bool = False, grayscale: bool = False,
                    xyshift: Optional[Tuple[int, int]] = None,
                    retry_interval: float = 1.0) -> bool:
        """Find and click on image
        
        Args:
            image_name: Name of image to find (without .png)
            confidence: Match confidence (0.0-1.0)
            seconds: Time to wait after clicking/not finding
            retry: Number of attempts
            region: Screen region to search (x, y, width, height)
            suppress: Suppress debug logging if not found
            grayscale: Use grayscale matching
            xyshift: Offset to apply to click position (x, y)
            retry_interval: Time to wait between retry attempts (default 1.0s)
        """
        for attempt in range(retry):
            result = self.find_image(image_name, confidence, region, grayscale)
            
            if result is not None:
                x, y, w, h = result
                x_center = round(x + w / 2)
                y_center = round(y + h / 2)
                
                if xyshift:
                    x_center += xyshift[0]
                    y_center += xyshift[1]
                    
                self.device.tap(x_center, y_center)
                time.sleep(seconds * self._get_multiplier())
                return True
                
            if attempt < retry - 1:
                if not suppress:
                    logger.debug(f"Retrying {image_name} search: {attempt+1}/{retry}")
                time.sleep(retry_interval * self._get_multiplier())
                
        if not suppress:
            logger.debug(f"Image {image_name} not found")
            # Screenshot is saved manually when logger.error is called
        time.sleep(seconds * self._get_multiplier())
        return False
    
    def wait_for_image(self, image_name: str, timeout: float = 10.0, 
                      check_interval: float = 0.3, confidence: float = 0.9,
                      region: Tuple[int, int, int, int] = (0, 0, 1080, 1920)) -> bool:
        """Wait for image to appear with fast polling
        
        This is more efficient than wait() + is_visible() because it checks
        frequently and returns immediately when image is found.
        
        Args:
            image_name: Name of image to find (without .png)
            timeout: Maximum time to wait in seconds (default 10s)
            check_interval: Time between checks in seconds (default 0.3s)
            confidence: Match confidence (0.0-1.0)
            region: Screen region to search (x, y, width, height)
            
        Returns:
            bool: True if image found, False if timeout
            
        Example:
            # Instead of:
            self.wait(5)
            if self.image.is_visible('buttons/something'):
                ...
            
            # Use:
            if self.image.wait_for_image('buttons/something', timeout=5):
                ...
        """
        start_time = time.time()
        attempts = 0
        
        while (time.time() - start_time) < timeout:
            result = self.find_image(image_name, confidence, region)
            if result is not None:
                logger.debug(f"Image {image_name} found after {attempts} attempts ({time.time() - start_time:.1f}s)")
                return True
            
            attempts += 1
            time.sleep(check_interval * self._get_multiplier())
        
        logger.debug(f"Image {image_name} not found after {timeout}s timeout")
        return False
        
    def click_secure(self, image_name: str, secure_image: str, 
                     retry: int = 5, seconds: float = 1, confidence: float = 0.9,
                     region: Tuple[int, int, int, int] = (0, 0, 1080, 1920),
                     secure_region: Tuple[int, int, int, int] = (0, 0, 1080, 1920)) -> bool:
        """Keep clicking image until secure_image disappears"""
        secure_counter = 0
        
        for attempt in range(retry):
            result = self.find_image(image_name, confidence, region)
            secure_result = self.find_image(secure_image, confidence, secure_region)
            
            if result is not None and secure_result is not None:
                while secure_result is not None and secure_counter < 5:
                    x, y, w, h = result
                    x_center = round(x + w / 2)
                    y_center = round(y + h / 2)
                    self.device.tap(x_center, y_center)
                    time.sleep(2 * self._get_multiplier())
                    secure_result = self.find_image(secure_image, confidence, secure_region)
                    secure_counter += 1
                return True
                
            time.sleep(1 * self._get_multiplier())
            
        return False
        
    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get RGB color of pixel at coordinates"""
        screenshot = self.device.get_screenshot_array()
        return tuple(screenshot[y, x])
        
    def check_pixel(self, x: int, y: int, channel: int = 0) -> int:
        """Check specific color channel (0=R, 1=G, 2=B) at coordinates"""
        screenshot = self.device.get_screenshot_array()
        return screenshot[y, x, channel]
        
    def _get_multiplier(self) -> float:
        """Get loading multiplier from config"""
        return float(self.config.get('ADVANCED', 'loadingMuliplier', fallback='1.0'))
    
    def _save_debug_screenshot(self, context: str = "error"):
        """Save screenshot to debug folder with context-based filename
        
        Args:
            context: Description of the error context (e.g., "store_not_found", "inn_not_found")
        """
        try:
            import time
            import re
            debug_dir = 'debug'
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            
            screenshot = self.device.get_screenshot()
            
            # Clean context for filename - remove special chars, keep only alphanumeric and underscores
            clean_context = re.sub(r'[^a-zA-Z0-9_]', '_', context.lower())
            clean_context = re.sub(r'_+', '_', clean_context)  # Remove multiple underscores
            clean_context = clean_context.strip('_')  # Remove leading/trailing underscores
            
            # Limit length
            if len(clean_context) > 50:
                clean_context = clean_context[:50]
            
            timestamp = int(time.time())
            filename = f"{clean_context}_{timestamp}.png"
            screenshot.save(os.path.join(debug_dir, filename))
            logger.warning(f"Debug screenshot saved: {filename}")
        except Exception as e:
            logger.debug(f"Failed to save debug screenshot: {e}")
    
    def save_error_screenshot(self, error_message: str):
        """Public method to save screenshot when error occurs
        
        Args:
            error_message: The error message to use as context
        """
        self._save_debug_screenshot(error_message)
