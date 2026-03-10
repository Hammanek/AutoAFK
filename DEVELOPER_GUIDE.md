# AutoAFK - Developer Guide

## Creating New Activities

This guide explains how to create new activity modules for the AutoAFK.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Creating a New Activity](#creating-a-new-activity)
4. [Available Methods](#available-methods)
5. [Best Practices](#best-practices)
6. [Examples](#examples)

---

## Architecture Overview

The bot uses a modular architecture with the following structure:

```
src/
├── core/                    # Core functionality
│   ├── device_manager.py    # ADB device control
│   ├── image_recognition.py # Image matching & clicking
│   ├── game_controller.py   # High-level game navigation
│   └── activity_manager.py  # Activity module registry
├── activities/              # Activity modules
│   ├── base_activity.py     # Base class for all activities
│   ├── daily_activities.py  # Daily tasks
│   ├── arena_activities.py  # PvP activities
│   └── ...                  # Other activity modules
└── utils/                   # Utilities
    └── logger.py            # Logging with color support
```

---

## Core Components

### 1. DeviceManager (`device_manager.py`)
Handles ADB communication with the device.

**Key Methods:**
- `tap(x, y)` - Tap at coordinates
- `swipe(x1, y1, x2, y2, duration)` - Swipe gesture
- `get_screenshot()` - Capture screen as PIL Image
- `check_pixel(x, y, channel)` - Get pixel color value (0=R, 1=G, 2=B)

### 2. ImageRecognition (`image_recognition.py`)
Handles image matching and clicking.

**Key Methods:**
- `is_visible(image_name, confidence=0.8, retry=1, click=False, region=None)` - Check if image exists
- `click_image(image_name, confidence=0.8, retry=1, seconds=1)` - Find and click image
- `wait_for_image(image_name, timeout=5, check_interval=0.3)` - Wait until image appears
- `save_error_screenshot(error_msg)` - Save debug screenshot

**Image Paths:**
- Images are stored in `img/buttons/` and `img/labels/`
- Reference without extension: `'buttons/confirm'` → `img/buttons/confirm.png`

### 3. GameController (`game_controller.py`)
High-level game navigation and control.

**Key Methods:**
- `confirm_location(location, change=True, region=None)` - Navigate to game location
- `recover(silent=False)` - Return to campaign screen
- `return_battle_results(battle_type='arena')` - Check battle outcome
- `select_opponent(choice=1, hoe=False)` - Select arena opponent
- `wait(seconds=1)` - Wait with loading multiplier

**Locations:**
- `'campaign'` - Campaign screen
- `'darkforest'` - Dark Forest screen
- `'ranhorn'` - Ranhorn screen

**Boundaries:**
All screen regions are defined in `GameController.BOUNDARIES` dictionary.

### 4. Logger (`logger.py`)
Colored logging system with automatic screenshot on errors.

**Log Levels:**
- `logger.blue(msg)` - Action start (e.g., "Attempting to collect mail")
- `logger.green(msg)` - Success (e.g., "Mail collected!")
- `logger.purple(msg)` - Special actions (e.g., shop purchases)
- `logger.warning(msg)` - Warnings
- `logger.error(msg)` - Errors (automatically saves screenshot)
- `logger.info(msg)` - General info

---

## Creating a New Activity

### Step 1: Create Activity File

Create a new file in `src/activities/` (e.g., `my_activity.py`):

```python
"""My custom activity module"""
import logging
from src.activities.base_activity import BaseActivity

logger = logging.getLogger(__name__)


class MyActivity(BaseActivity):
    """Handles my custom activity"""
    
    def my_function(self) -> bool:
        """
        Description of what this function does
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.blue("Starting my activity...")
        
        # Navigate to location
        self.controller.confirm_location('ranhorn', 
                                        region=self.controller.BOUNDARIES['ranhornSelect'])
        
        # Wait for screen to load
        self.wait(2)
        
        # Click button
        if self.image.is_visible('buttons/my_button', retry=3):
            self.image.click_image('buttons/my_button')
            logger.green("Activity completed!")
            return True
        else:
            logger.error("Button not found")
            self.controller.recover()
            return False
```

### Step 2: Register in ActivityManager

Edit `src/core/activity_manager.py`:

```python
from src.activities.my_activity import MyActivity

class ActivityManager:
    def __init__(self, device_manager, image_recognition, game_controller, 
                 config, notification_manager=None):
        # ... existing code ...
        
        # Add your activity
        self.my_activity = MyActivity(device_manager, image_recognition,
                                      game_controller, config, notification_manager)
```

### Step 3: Use in Dailies Runner (Optional)

Edit `src/core/dailies_runner.py` to add to daily routine:

```python
def execute_dailies(config, activity_manager, device_manager):
    # ... existing code ...
    
    # Add your activity
    if config.getboolean('DAILIES', 'myActivity', fallback=False):
        activity_manager.my_activity.my_function()
        device_manager.tap(20, 20)  # Clear popups
```

---

## Available Methods

### From BaseActivity

All activity classes inherit from `BaseActivity` and have access to:

```python
self.device        # DeviceManager instance
self.image         # ImageRecognition instance
self.controller    # GameController instance
self.config        # ConfigParser instance
self.notifier      # NotificationManager instance

self.wait(seconds=1)  # Wait with loading multiplier
```

### Image Recognition Patterns

#### Pattern 1: Simple Check
```python
if self.image.is_visible('buttons/collect'):
    self.image.click_image('buttons/collect')
```

#### Pattern 2: Wait for Image (RECOMMENDED)
```python
# Wait up to 5 seconds, checking every 0.3s
if self.image.wait_for_image('labels/store', timeout=5, check_interval=0.3):
    # Image found, continue
    pass
else:
    # Timeout, handle error
    logger.error("Store not found")
```

#### Pattern 3: Retry with Click
```python
# Try 3 times with 0.3s between attempts
if self.image.is_visible('buttons/confirm', retry=3, click=True):
    logger.green("Confirmed!")
```

#### Pattern 4: Region-Specific
```python
# Only search in specific screen region
if self.image.is_visible('buttons/back', 
                         region=self.controller.BOUNDARIES['backMenu']):
    self.image.click_image('buttons/back')
```

### Navigation Patterns

#### Pattern 1: Confirm Location
```python
# Navigate to location (will click if not there)
self.controller.confirm_location('campaign', 
                                region=self.controller.BOUNDARIES['campaignSelect'])
```

#### Pattern 2: Check Location Without Changing
```python
# Just check if we're at location
if self.controller.confirm_location('campaign', change=False):
    # We're at campaign screen
    pass
```

#### Pattern 3: Recover from Error
```python
if not self.image.is_visible('expected_screen'):
    logger.error("Screen not found")
    self.controller.recover()  # Return to campaign
    return False
```

### Tap Patterns

#### Pattern 1: Simple Tap
```python
self.controller.tap(550, 1800)  # Tap at coordinates
```

#### Pattern 2: Tap with Wait
```python
self.controller.tap(550, 1800, seconds=2)  # Tap and wait 2s
```

#### Pattern 3: Tap with Random Shift
```python
self.controller.tap(550, 1800, random_shift=10)  # ±10 pixels
```

#### Pattern 4: Clear Popups
```python
self.controller.tap(20, 20)  # Neutral location to clear popups
```

### Swipe Patterns

```python
# Swipe from (x1,y1) to (x2,y2) over duration ms
self.controller.swipe(550, 1500, 550, 1200, 500, seconds=2)
```

### Pixel Check Pattern

```python
# Check if pixel is red (notification indicator)
red_value = self.image.check_pixel(1020, 720, 0)  # 0=Red channel
if red_value > 220:
    # Red notification found
    pass
```

---

## Best Practices

### 1. Always Use Logging
```python
logger.blue("Starting activity...")  # Action start
logger.green("Success!")             # Success
logger.purple("Buying item...")      # Special action
logger.warning("Not found")          # Warning
logger.error("Failed")               # Error (auto-screenshot)
```

### 2. Use wait_for_image() Instead of wait()
```python
# ❌ BAD - Always waits 5 seconds
self.wait(5)
if self.image.is_visible('buttons/collect'):
    pass

# ✅ GOOD - Continues as soon as found (0.3-5s)
if self.image.wait_for_image('buttons/collect', timeout=5, check_interval=0.3):
    pass
```

### 3. Always Handle Errors
```python
if self.image.is_visible('expected_screen', retry=3):
    # Success path
    return True
else:
    # Error path
    logger.error("Screen not found")
    self.controller.recover()
    return False
```

### 4. Use Regions for Faster Matching
```python
# ✅ GOOD - Only searches in specific area
self.image.is_visible('buttons/back', 
                     region=self.controller.BOUNDARIES['backMenu'])
```

### 5. Clear Popups After Activities
```python
def my_activity(self):
    # ... activity code ...
    self.controller.tap(20, 20)  # Clear any popups
    return True
```

### 6. Use Config for Toggles
```python
if self.config.getboolean('DAILIES', 'myActivity', fallback=False):
    self.my_function()
```

### 7. Return Boolean for Success/Failure
```python
def my_activity(self) -> bool:
    """Returns True if successful, False otherwise"""
    if success:
        return True
    else:
        return False
```

### 8. Use Retry Interval for Faster Checks
```python
# ✅ GOOD - Checks every 0.3s instead of 1s
self.image.is_visible('buttons/confirm', retry=3, retry_interval=0.3)
```

---

## Examples

### Example 1: Simple Collection Activity

```python
def collect_daily_reward(self) -> bool:
    """Collect daily login reward"""
    logger.blue("Collecting daily reward...")
    
    # Navigate to ranhorn
    self.controller.confirm_location('ranhorn',
                                    region=self.controller.BOUNDARIES['ranhornSelect'])
    
    # Wait for screen to load
    self.wait(2)
    
    # Click daily reward icon
    self.controller.tap(960, 250, seconds=2)
    
    # Wait for reward screen
    if self.image.wait_for_image('buttons/collect', timeout=5, check_interval=0.3):
        self.image.click_image('buttons/collect')
        self.controller.tap(550, 1800)  # Clear popup
        logger.green("Daily reward collected!")
        return True
    else:
        logger.warning("No daily reward available")
        return False
```

### Example 2: Battle Activity with Loop

```python
def battle_arena(self, count: int) -> bool:
    """Battle in arena multiple times
    
    Args:
        count: Number of battles to perform
    """
    logger.blue(f"Battling arena {count} times...")
    
    self.controller.confirm_location('darkforest',
                                    region=self.controller.BOUNDARIES['darkforestSelect'])
    
    counter = 0
    while counter < count:
        # Click challenge button
        if self.image.is_visible('buttons/challenge', retry=3, click=True):
            self.wait(2)
            
            # Select opponent
            self.controller.select_opponent(choice=1)
            
            # Start battle
            self.image.click_image('buttons/battle', seconds=3)
            
            # Wait for battle to end and check result
            result = self.controller.return_battle_results('arena')
            
            if result:
                counter += 1
                logger.green(f"Battle #{counter} - Victory!")
            else:
                logger.warning(f"Battle #{counter} - Defeat")
                
            self.wait(2)
        else:
            logger.error("Challenge button not found")
            self.controller.recover()
            return False
    
    logger.green(f"Completed {counter} arena battles")
    return True
```

### Example 3: Shop Purchase Activity

```python
def purchase_shop_items(self) -> bool:
    """Purchase configured items from shop"""
    logger.blue("Purchasing shop items...")
    
    # Navigate to shop
    self.controller.confirm_location('ranhorn',
                                    region=self.controller.BOUNDARIES['ranhornSelect'])
    self.wait(2)
    self.controller.tap(440, 1750)  # Shop button
    
    # Wait for shop screen
    if self.image.wait_for_image('labels/store', timeout=5, check_interval=0.3):
        # Purchase dust if enabled
        if self.config.getboolean('SHOP', 'dust_gold', fallback=False):
            if self.image.is_visible('buttons/shop/dust', confidence=0.95, click=True):
                logger.purple("    Buying: Dust (Gold)")
                self.image.click_image('buttons/shop/purchase', suppress=True)
                self.controller.tap(550, 1220, seconds=2)
        
        # Purchase shards if enabled
        if self.config.getboolean('SHOP', 'shards_gold', fallback=False):
            if self.image.is_visible('buttons/shop/shards_gold', confidence=0.95, click=True):
                logger.purple("    Buying: Shards")
                self.image.click_image('buttons/shop/purchase', suppress=True)
                self.controller.tap(550, 1220, seconds=2)
        
        # Exit shop
        self.image.click_image('buttons/back')
        logger.green("Shop purchases completed")
        return True
    else:
        logger.error("Shop not found")
        self.controller.recover()
        return False
```

### Example 4: Activity with Error Recovery

```python
def collect_guild_rewards(self) -> bool:
    """Collect guild hunt rewards with error recovery"""
    logger.blue("Collecting guild rewards...")
    
    try:
        # Navigate to guild
        self.controller.confirm_location('ranhorn',
                                        region=self.controller.BOUNDARIES['ranhornSelect'])
        self.wait(2)
        self.controller.tap(380, 360, seconds=3)  # Guild button
        
        # Check if guild screen loaded
        if not self.image.wait_for_image('labels/guild', timeout=5, check_interval=0.3):
            logger.error("Guild screen not loaded")
            self.controller.recover()
            return False
        
        # Collect rewards
        if self.image.is_visible('buttons/collect_guild', retry=3):
            self.image.click_image('buttons/collect_guild')
            self.controller.tap(550, 1800)  # Clear popup
            logger.green("Guild rewards collected!")
        else:
            logger.warning("No guild rewards available")
        
        # Exit guild
        self.image.click_image('buttons/back', retry=3)
        return True
        
    except Exception as e:
        logger.error(f"Guild collection failed: {e}")
        self.controller.recover()
        return False
```

---

## Common Boundaries

Frequently used screen regions (from `GameController.BOUNDARIES`):

```python
# Location selectors
'campaignSelect': (424, 1750, 232, 170)
'darkforestSelect': (208, 1750, 226, 170)
'ranhornSelect': (0, 1750, 210, 160)

# Buttons
'begin': (322, 1590, 442, 144)
'battle': (574, 1779, 300, 110)
'backMenu': (0, 1720, 150, 200)
'heroclassselect': (5, 1620, 130, 120)

# Collections
'collectAfk': (590, 1322, 270, 82)
'mailLocate': (915, 515, 150, 150)
'friends': (915, 670, 150, 150)

# Arena
'challengeAoH': (294, 1738, 486, 140)
'skipAoH': (650, 1350, 200, 200)
```

---

## Testing Your Activity

1. **Add to settings.ini:**
```ini
[DAILIES]
myActivity = True
```

2. **Test in isolation:**
```python
# In main.py or test script
activity_manager.my_activity.my_function()
```

3. **Check logs:**
- Console output shows colored messages
- Log files in `logs/` folder
- Screenshots in `debug/` folder on errors

4. **Common issues:**
- Image not found → Check image exists in `img/` folder
- Wrong coordinates → Use screenshot to verify positions
- Timeout → Increase `timeout` or `retry` values
- Wrong region → Verify BOUNDARIES coordinates

---

## Tips & Tricks

1. **Use screenshot tool to find coordinates:**
   - Take screenshot with `device_manager.get_screenshot()`
   - Open in image editor to find pixel coordinates

2. **Test image matching:**
   ```python
   # Test if image is found
   result = self.image.is_visible('buttons/test', confidence=0.8)
   logger.info(f"Image found: {result}")
   ```

3. **Debug with screenshots:**
   ```python
   # Save screenshot for debugging
   self.image.save_error_screenshot("debug_checkpoint")
   ```

4. **Use suppress=True to avoid error logs:**
   ```python
   # Won't log error if not found
   self.image.click_image('buttons/optional', suppress=True)
   ```

5. **Chain operations:**
   ```python
   if (self.image.is_visible('screen1') and 
       self.image.is_visible('screen2')):
       # Both found
       pass
   ```

---

## Questions?

- Check existing activities in `src/activities/` for examples
- Review `base_activity.py` for inherited methods
- Check `image_recognition.py` for all image methods
- Review `game_controller.py` for navigation methods

Happy coding! 🎮
