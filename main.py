"""
AutoAFK - Modern modular architecture
Uses new modular backend with full functionality
"""
import os
import sys
import threading
import datetime
import logging
import argparse
import subprocess
from pathlib import Path

# Version - Update this when releasing new version
VERSION = "2.0.6"

# GitHub Repository
GITHUB_REPO = "Hammanek/AutoAFK"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

try:
    import customtkinter as ctk
except ImportError:
    print("Installing customtkinter...")
    os.system("pip install customtkinter")
    import customtkinter as ctk

from src.core.config import Config
from src.core.device_manager import DeviceManager
from src.core.image_recognition import ImageRecognition
from src.core.game_controller import GameController
from src.core.activity_manager import ActivityManager
from src.core.dailies_runner import execute_dailies
from src.activities.tower_activities import TowerPusher
from src.utils.logger import Logger
from src.utils.notifications import NotificationManager
from src.utils.version_checker import VersionChecker

# Set appearance - Modern dark theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")  # Modern blue theme

logger = Logger.get_logger(__name__)

# Global args variable
args = None


def initialize_core_modules(config: Config) -> tuple:
    """Initialize core modules (device, image recognition, game controller)
    
    Args:
        config: Configuration instance
        
    Returns:
        tuple: (device_manager, image_recognition, game_controller) or (None, None, None) on failure
    """
    device_manager = DeviceManager(config)
    if not device_manager.connect():
        logger.error("Failed to connect to device")
        return None, None, None
        
    image_recognition = ImageRecognition(device_manager, config)
    game_controller = GameController(device_manager, image_recognition, config)
    
    # Enable automatic screenshots on errors
    from src.utils.logger import set_device_manager
    set_device_manager(device_manager)
    
    return device_manager, image_recognition, game_controller


class App(ctk.CTk):
    """Main application window - original style"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title(f"AutoAFK {VERSION}")
        self.geometry("800x540")
        self.resizable(False, False)  # Disable window resizing
        
        # Try to set icon
        icon_paths = [
            Path("img/auto.ico"),
            Path("_internal/img/auto.ico"),
            Path(sys._MEIPASS) / "img" / "auto.ico" if getattr(sys, 'frozen', False) else None
        ]
        
        for icon_path in icon_paths:
            if icon_path and icon_path.exists():
                try:
                    self.iconbitmap(str(icon_path))
                    break
                except:
                    pass
        
        # Config and core modules
        self.config = Config('settings.ini')
        
        # Initialize Logger
        from src.utils.logger import Logger as LoggerClass
        LoggerClass()  # Initialize logger singleton
        
        self.device_manager = None
        self.image_recognition = None
        self.game_controller = None
        self.daily_activities = None
        self.arena_activities = None
        self.legacy_activities = None
        self.notification_manager = None
        
        # Thread state
        self.dailies_thread_running = False
        self.activity_thread_running = False
        self.push_thread_running = False
        
        self.dailies_thread = None
        self.activity_thread = None
        self.push_thread = None
        
        self.dailies_stop_event = threading.Event()
        self.activity_stop_event = threading.Event()
        self.push_stop_event = threading.Event()
        
        self.dailies_pause_event = threading.Event()
        self.activity_pause_event = threading.Event()
        self.push_pause_event = threading.Event()
        
        # Windows
        self.shop_window = None
        self.activity_window = None
        self.advanced_window = None
        
        self._create_widgets()
        
    def _check_for_updates(self) -> None:
        """Check for updates in background thread to avoid blocking UI"""
        def check():
            try:
                update_available, current, latest = VersionChecker.check_for_updates()
                notes = VersionChecker.get_release_notes(latest) if (latest and update_available) else None

                def update_ui():
                    if not latest:
                        self.textbox.insert('end', '⚠️ Could not check for updates\n\n', 'warning')
                        return

                    if not update_available:
                        return

                    self.textbox.insert('end', '⚠️ UPDATE AVAILABLE!\n', 'yellow')
                    self.textbox.insert('end', f'Current version: {current}\n', 'warning')
                    self.textbox.insert('end', f'Latest version: {latest}\n\n', 'yellow')

                    if notes:
                        self.textbox.insert('end', f'Version {latest} changes:\n', 'yellow')
                        self.textbox.insert('end', f'{notes[:500]}{"..." if len(notes) > 500 else ""}\n\n', 'warning')

                    if self.config.getboolean('ADVANCED', 'autoupdate', fallback=False):
                        self.textbox.insert('end', '🔄 Auto-update enabled, starting updater...\n\n', 'orange')
                        self.after(2000, self._run_updater)
                    else:
                        self.textbox.insert('end', '💡 Run update.bat to update or download from:\n', 'blue')
                        self.textbox.insert('end', f'{VersionChecker.get_download_url()}\n\n', 'blue')

                self.after(0, update_ui)
            except Exception as e:
                logger.debug(f"Version check failed: {e}")

        threading.Thread(target=check, daemon=True).start()
    
    def _open_link(self, event) -> None:
        """Open URL in browser when clicked"""
        import webbrowser
        
        # Get all tags at click position
        tags = self.textbox.tag_names(f"@{event.x},{event.y}")
        
        # Find URL from stored links
        for tag in tags:
            if tag in self.link_urls:
                webbrowser.open(self.link_urls[tag])
                break
    
    def _get_tower_options_for_today(self) -> list:
        """Get available tower options based on day of week (UTC timezone)"""
        from datetime import datetime, timezone
        
        # Get current day in UTC (1=Monday, 7=Sunday)
        # Game uses UTC timezone for tower resets
        current_day = datetime.now(timezone.utc).isoweekday()
        
        # Tower availability by day
        tower_days = {
            1: ["Campaign", "King's Tower", "Lightbearer Tower"],
            2: ["Campaign", "King's Tower", "Mauler Tower"],
            3: ["Campaign", "King's Tower", "Wilder Tower", "Celestial Tower"],
            4: ["Campaign", "King's Tower", "Graveborn Tower", "Hypogean Tower"],
            5: ["Campaign", "King's Tower", "Lightbearer Tower", "Mauler Tower", "Celestial Tower"],
            6: ["Campaign", "King's Tower", "Wilder Tower", "Graveborn Tower", "Hypogean Tower"],
            7: ["Campaign", "King's Tower", "Lightbearer Tower", "Wilder Tower", "Mauler Tower", 
                "Graveborn Tower", "Hypogean Tower", "Celestial Tower"]
        }
        
        return tower_days.get(current_day, ["Campaign", "King's Tower"])
    
    def _run_updater(self) -> None:
        """Launch updater as a detached process with its own visible console window"""
        try:
            # Resolve base directory (works for both frozen exe and script)
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))

            updater_exe = os.path.join(base_dir, '_internal', 'AutoAFKUpdater.exe')
            updater_py = os.path.join(base_dir, 'AutoAFKUpdater.py')

            if os.path.exists(updater_exe):
                cmd = [updater_exe, '--auto']
            elif os.path.exists(updater_py):
                cmd = ['python', updater_py, '--auto']
            else:
                self.textbox.insert('end', '❌ Updater not found\n', 'error')
                return

            # Launch in a new visible console window, fully detached from this process
            # CREATE_NEW_CONSOLE gives user a window to see progress
            # CREATE_NEW_PROCESS_GROUP ensures it survives when AutoAFK.exe is killed
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
            )

            self.textbox.insert('end', '🔄 Updater started in separate window\n', 'orange')
            self.textbox.insert('end', '⏳ Bot will close in 5 seconds...\n', 'orange')
            self.textbox.see('end')
            self.after(5000, self.quit)

        except Exception as e:
            self.textbox.insert('end', f'❌ Failed to run updater: {e}\n', 'error')
        
    def _create_widgets(self) -> None:
        """Create all widgets - original layout"""
        
        # Dailies Frame
        self.dailiesFrame = ctk.CTkFrame(master=self, height=170, width=180)
        self.dailiesFrame.place(x=10, y=20)
        
        self.dailiesButton = ctk.CTkButton(
            master=self.dailiesFrame,
            text="Run Dailies",
            command=self.start_dailies_thread
        )
        self.dailiesButton.place(x=20, y=10)
        
        self.activitiesButton = ctk.CTkButton(
            master=self.dailiesFrame,
            text="Configure Dailies",
            fg_color=["#343638", "#343638"],  # Match dropdown menu color
            hover_color=["#3E4042", "#3E4042"],
            width=120,
            command=self.open_activitywindow
        )
        self.activitiesButton.place(x=30, y=50)
        
        self.dailiesShopButton = ctk.CTkButton(
            master=self.dailiesFrame,
            text="Store Options",
            fg_color=["#343638", "#343638"],  # Match dropdown menu color
            hover_color=["#3E4042", "#3E4042"],
            width=120,
            command=self.open_shopwindow
        )
        self.dailiesShopButton.place(x=30, y=90)
        
        self.advancedButton = ctk.CTkButton(
            master=self.dailiesFrame,
            text="Advanced Options",
            fg_color=["#343638", "#343638"],  # Match dropdown menu color
            hover_color=["#3E4042", "#3E4042"],
            width=120,
            command=self.open_advancedwindow
        )
        self.advancedButton.place(x=30, y=130)
        
        # PvP Frame
        self.arenaFrame = ctk.CTkFrame(master=self, height=130, width=180)
        self.arenaFrame.place(x=10, y=200)
        
        self.arenaButton = ctk.CTkButton(
            master=self.arenaFrame,
            text="Run Activity",
            command=self.start_activity_thread
        )
        self.arenaButton.place(x=20, y=15)
        
        self.activityFormationDropdown = ctk.CTkComboBox(
            master=self.arenaFrame,
            values=[
                "Arena of Heroes",
                "Arcane Labyrinth",
                "Fight of Fates",
                "Battle of Blood",
                "Heroes of Esperia",
                "Guild Hunts"
            ],
            width=160
        )
        self.activityFormationDropdown.place(x=10, y=55)
        
        self.pvpLabel = ctk.CTkLabel(
            master=self.arenaFrame,
            text='How many battles?'
        )
        self.pvpLabel.place(x=10, y=90)
        
        self.pvpEntry = ctk.CTkEntry(master=self.arenaFrame, height=20, width=40)
        self.pvpEntry.insert('end', self.config.get('ACTIVITIES', 'arena_battles', fallback='5'))
        self.pvpEntry.place(x=130, y=92)
        
        # Push Frame
        self.pushFrame = ctk.CTkFrame(master=self, height=180, width=180)
        self.pushFrame.place(x=10, y=340)
        
        self.pushButton = ctk.CTkButton(
            master=self.pushFrame,
            text="Auto Push",
            command=self.start_push_thread
        )
        self.pushButton.place(x=20, y=10)
        
        # Set tower options based on day of week
        tower_values = self._get_tower_options_for_today()
        
        self.pushLocationDropdown = ctk.CTkComboBox(
            master=self.pushFrame,
            values=tower_values,
            width=160
        )
        self.pushLocationDropdown.place(x=10, y=50)
        
        self.pushLabel = ctk.CTkLabel(
            master=self.pushFrame,
            text='Which formation?'
        )
        self.pushLabel.place(x=10, y=80)
        
        self.pushFormationDropdown = ctk.CTkComboBox(
            master=self.pushFrame,
            values=["1st", "2nd", "3rd", "4th", "5th"],
            width=80
        )
        # Load saved formation from config
        saved_formation_str = self.config.get('PUSH', 'formation', fallback='3')
        # Parse formation - handle both "3" and "3rd" formats
        if saved_formation_str.isdigit():
            saved_formation = int(saved_formation_str)
        else:
            # Extract number from "3rd" format
            saved_formation = int(saved_formation_str[0])
        formation_map = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}
        self.pushFormationDropdown.set(formation_map.get(saved_formation, "3rd"))
        self.pushFormationDropdown.place(x=10, y=110)
        
        # Textbox - Modern styling
        self.textbox = ctk.CTkTextbox(master=self, width=580, height=500)
        self.textbox.place(x=200, y=20)
        self.textbox.configure(
            text_color='#E8E8E8',           # Soft white
            fg_color='#1E1E1E',             # Dark background
            font=('Segoe UI', 13),          # Modern font
            border_width=2,
            border_color='#3A3A3A'          # Subtle border
        )
        
        # Configure tags - Modern minimalist color scheme
        self.textbox.tag_config("error", foreground="#EF4444")      # Bright red
        self.textbox.tag_config('warning', foreground="#F59E0B")    # Amber
        self.textbox.tag_config('green', foreground="#10B981")      # Emerald green
        self.textbox.tag_config('blue', foreground="#3B82F6")       # Blue
        self.textbox.tag_config('purple', foreground="#A855F7")     # Purple
        self.textbox.tag_config('yellow', foreground="#F59E0B")     # Amber
        self.textbox.tag_config('orange', foreground="#F97316")     # Orange
        
        # Configure clickable link tags
        self.textbox.tag_config('link', foreground="#3B82F6", underline=True)
        self.textbox.tag_bind('link', '<Button-1>', self._open_link)
        self.textbox.tag_bind('link', '<Enter>', lambda e: self.textbox.configure(cursor='hand2'))
        self.textbox.tag_bind('link', '<Leave>', lambda e: self.textbox.configure(cursor=''))
        
        # Store URLs for links
        self.link_urls = {}
        
        # Welcome message
        self.textbox.insert('end', f'AutoAFK {VERSION}\n', 'green')
        self.textbox.insert('end', '🔗 GitHub: ', 'info')
        
        # GitHub link (clickable)
        github_url = f'https://github.com/{GITHUB_REPO}'
        start_idx = self.textbox.index('end-1c')
        self.textbox.insert('end', f'{github_url}\n', 'link')
        end_idx = self.textbox.index('end-1c')
        github_tag = f'github_link_{id(github_url)}'
        self.textbox.tag_add(github_tag, start_idx, end_idx)
        self.link_urls[github_tag] = github_url
        
        self.textbox.insert('end', '☕ Support: ', 'info')
        
        # Ko-fi link (clickable)
        kofi_url = 'https://ko-fi.com/afksupporter'
        start_idx = self.textbox.index('end-1c')
        self.textbox.insert('end', f'{kofi_url}\n\n', 'link')
        end_idx = self.textbox.index('end-1c')
        kofi_tag = f'kofi_link_{id(kofi_url)}'
        self.textbox.tag_add(kofi_tag, start_idx, end_idx)
        self.link_urls[kofi_tag] = kofi_url
        
        # Check for updates
        self._check_for_updates()
        
        # Pause/Stop buttons
        self.pauseButton = ctk.CTkButton(
            master=self,
            text="⏸️",
            bg_color="#3B3B3B",
            fg_color="#1F6AA5",
            width=40,
            command=self.pause_all_thread,
            state="disabled",
            hover=False
        )
        self.pauseButton.place(x=690, y=25)
        self.pauseButton.place_forget()
        
        self.quitButton = ctk.CTkButton(
            master=self,
            text="⏹️",
            bg_color="#3B3B3B",
            fg_color=["#B60003", "#C03335"],
            width=40,
            command=self.stop_all_threads,
            state="disabled",
            hover=False
        )
        self.quitButton.place(x=735, y=25)
        self.quitButton.place_forget()
        
        # Setup logging redirect
        sys.stdout = STDOutRedirector(self.textbox)
        sys.stderr = STDOutRedirector(self.textbox)  # Also redirect errors
        
        # Redirect logger to GUI
        self._setup_logger_redirect()
        
        # Setup cleanup on close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _setup_logger_redirect(self) -> None:
        """Redirect logger output to GUI"""
        
        class GUIHandler(logging.Handler):
            def __init__(self, app):
                super().__init__()
                self.app = app
                
            def emit(self, record):
                try:
                    msg = self.format(record)
                    timestamp = '[' + datetime.datetime.now().strftime("%H:%M:%S") + '] '
                    
                    # Import custom levels
                    from src.utils.logger import BLUE, GREEN, PURPLE
                    
                    # Color based on level - check custom levels first
                    if record.levelno == GREEN:
                        self.app.textbox.insert('end', timestamp + msg + '\n', 'green')
                    elif record.levelno == BLUE:
                        self.app.textbox.insert('end', timestamp + msg + '\n', 'blue')
                    elif record.levelno == PURPLE:
                        self.app.textbox.insert('end', timestamp + msg + '\n', 'purple')
                    elif record.levelno >= logging.ERROR:
                        self.app.textbox.insert('end', timestamp + msg + '\n', 'error')
                    elif record.levelno >= logging.WARNING:
                        self.app.textbox.insert('end', timestamp + msg + '\n', 'warning')
                    elif record.levelno >= logging.INFO:
                        # Color INFO messages based on content
                        if 'collected' in msg.lower() or 'completed' in msg.lower() or 'success' in msg.lower():
                            self.app.textbox.insert('end', timestamp + msg + '\n', 'green')
                        elif 'starting' in msg.lower() or 'attempting' in msg.lower():
                            self.app.textbox.insert('end', timestamp + msg + '\n', 'blue')
                        else:
                            self.app.textbox.insert('end', timestamp + msg + '\n')
                    else:
                        self.app.textbox.insert('end', timestamp + msg + '\n')
                        
                    self.app.textbox.see('end')
                    self.app.update_idletasks()
                    
                    # Send to Discord if enabled
                    if hasattr(self.app, 'notification_manager') and self.app.notification_manager:
                        level_name = logging.getLevelName(record.levelno)
                        self.app.notification_manager.send(msg, level_name)
                except:
                    pass  # Ignore errors during logging
                
        # Add handler to root logger
        handler = GUIHandler(self)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)
    
    def _on_closing(self) -> None:
        """Cleanup when closing the application"""
        try:
            # Stop all threads
            self.stop_all_threads()
            
            # Cleanup ADB synchronously to ensure it completes
            try:
                if self.device_manager:
                    logger.info("Disconnecting and cleaning up ADB...")
                    self.device_manager.disconnect()
                    self.device_manager._kill_adb_processes()
                    # Give it a moment to complete
                    import time
                    time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Cleanup error: {e}")
            
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")
        finally:
            # Close the window
            self.destroy()
    
    def start_dailies_thread(self) -> None:
        """Start dailies thread"""
        if not self.dailies_thread_running:
            self.dailies_thread_running = True
            self.dailies_stop_event.clear()
            self.dailies_pause_event.clear()
            self.dailies_thread = threading.Thread(target=self.dailies)
            self.dailies_thread.start()
            self.button_state('disabled')
            self.stop_button_state('normal')
            
    def start_activity_thread(self) -> None:
        """Start activity thread"""
        if not self.activity_thread_running:
            self.activity_thread_running = True
            self.activity_stop_event.clear()
            self.activity_pause_event.clear()
            self.activity_thread = threading.Thread(target=self.activity_manager)
            self.activity_thread.start()
            self.button_state('disabled')
            self.stop_button_state('normal')
            
    def start_push_thread(self) -> None:
        """Start push thread"""
        if not self.push_thread_running:
            self.push_thread_running = True
            self.push_stop_event.clear()
            self.push_pause_event.clear()
            self.push_thread = threading.Thread(target=self.push)
            self.push_thread.start()
            self.button_state('disabled')
            self.stop_button_state('normal')

            
    def stop_all_threads(self) -> None:
        """Stop all threads"""
        print('WAR' + "Stop pressed, stopping after current action")
        self.dailies_thread_running = False
        self.activity_thread_running = False
        self.push_thread_running = False
        
        self.dailies_stop_event.set()
        self.activity_stop_event.set()
        self.push_stop_event.set()
        
    def pause_all_thread(self) -> None:
        """Pause all threads"""
        print('WAR' + "Pause pressed, pausing after current action")
        self.dailies_pause_event.set()
        self.activity_pause_event.set()
        self.push_pause_event.set()
        self.pauseButton.configure(text="▶️", command=self.resume_all_thread, fg_color="green")
        self.quitButton.configure(state='disabled')
        
    def resume_all_thread(self) -> None:
        """Resume all threads"""
        self.dailies_pause_event.clear()
        self.activity_pause_event.clear()
        self.push_pause_event.clear()
        self.pauseButton.configure(text="⏸️", command=self.pause_all_thread, fg_color="#1F6AA5")
        self.quitButton.configure(state='normal')
        
    def button_state(self, state: str) -> None:
        """Set button states"""
        self.dailiesButton.configure(state=state)
        self.arenaButton.configure(state=state)
        self.pushButton.configure(state=state)
        if state == 'normal':
            self.pauseButton.configure(state='disabled')
            self.quitButton.configure(state='disabled')
            self.pauseButton.place_forget()
            self.quitButton.place_forget()
            
    def stop_button_state(self, state: str) -> None:
        """Set stop button state"""
        if state == "normal":
            self.pauseButton.place(x=690, y=25)
            self.quitButton.place(x=735, y=25)
            self.pauseButton.lift()
            self.quitButton.lift()
        self.pauseButton.configure(state=state)
        self.quitButton.configure(state=state)
        
    def dailies(self) -> None:
        """Run dailies"""
        try:
            logger.info("Starting dailies...")
            
            # Initialize notification manager
            self.notification_manager = NotificationManager(self.config)
            
            # Initialize core modules
            self.device_manager, self.image_recognition, self.game_controller = \
                initialize_core_modules(self.config)
            
            if not self.device_manager:
                return
            
            # Initialize activity manager
            self.activity_manager = ActivityManager(
                self.device_manager, self.image_recognition, self.game_controller,
                self.config, self.notification_manager
            )
            
            # Execute dailies using shared function
            execute_dailies(self.activity_manager, self.dailies_pause_event, self.dailies_stop_event)
            
        except Exception as e:
            logger.error(f"Dailies error: {e}", exc_info=True)
        finally:
            self.dailies_thread_running = False
            self.button_state('normal')
            
    def activity_manager(self) -> None:
        """Run selected activity"""
        try:
            activity = self.activityFormationDropdown.get()
            battles = int(self.pvpEntry.get())
            
            # Save battles count to config
            self.config.set('ACTIVITIES', 'arena_battles', str(battles))
            self.config.save()
            
            logger.info(f"Starting {activity} ({battles} battles)...")
            
            # Initialize modules if not already done
            if not self.device_manager:
                self.notification_manager = NotificationManager(self.config)
                
                # Initialize core modules
                self.device_manager, self.image_recognition, self.game_controller = \
                    initialize_core_modules(self.config)
                
                if not self.device_manager:
                    logger.error("Failed to connect to device")
                    return
            
            # Initialize activity manager with all modules
            activity_mgr = ActivityManager(
                self.device_manager, self.image_recognition, self.game_controller,
                self.config, self.notification_manager
            )
            
            # Expand menus and wait for game
            self.game_controller.expand_menus()
            self.game_controller.wait_until_game_active()
            
            logger.info("Device connected, running activity...")
            
            # Run specific activity
            if activity == "Arena of Heroes":
                activity_mgr.arena.battle_arena_of_heroes(battles, 1, 
                                                         self.activity_pause_event,
                                                         self.activity_stop_event)
            elif activity == "Arcane Labyrinth":
                activity_mgr.labyrinth.handle_labyrinth()
            elif activity == "Fight of Fates":
                activity_mgr.misc.handle_fight_of_fates(battles)
            elif activity == "Battle of Blood":
                activity_mgr.misc.handle_battle_of_blood(battles)
            elif activity == "Heroes of Esperia":
                activity_mgr.misc.handle_heroes_of_esperia(battles, 4)
            elif activity == "Guild Hunts":
                activity_mgr.guild.handle_guild_hunts()
                
            logger.info("Activity completed!")
        except Exception as e:
            logger.error(f"Activity error: {e}", exc_info=True)
        finally:
            self.activity_thread_running = False
            self.button_state('normal')
            
    def push(self) -> None:
        """Run push"""
        try:
            location = self.pushLocationDropdown.get()
            formation = int(self.pushFormationDropdown.get()[0])
            
            # Save formation to config
            self.config.set('PUSH', 'formation', str(formation))
            self.config.save()
            
            logger.info(f"Auto-Pushing {location} using formation {formation}")
            
            # Initialize modules if not already done
            if not self.device_manager:
                self.notification_manager = NotificationManager(self.config)
                
                # Initialize core modules
                self.device_manager, self.image_recognition, self.game_controller = \
                    initialize_core_modules(self.config)
                
                if not self.device_manager:
                    logger.error("Failed to connect to device")
                    return
            
            # Expand menus and wait for game
            self.game_controller.expand_menus()
            self.game_controller.wait_until_game_active()
            
            logger.info("Device connected, starting push...")
            
            # Get duration from config
            duration = self.config.getint('PUSH', 'victoryCheck', fallback=1)
            
            # Create TowerPusher and run
            from src.activities.tower_activities import TowerPusher
            pusher = TowerPusher(self.device_manager, self.image_recognition, 
                                self.game_controller, self.config, self.notification_manager)
            
            if "Tower" in location:
                # Push tower
                pusher.push_tower(location, formation, duration, 
                                 pause_event=self.push_pause_event,
                                 stop_event=self.push_stop_event)
            else:
                # Push campaign
                pusher.push_campaign(formation, duration,
                                    pause_event=self.push_pause_event,
                                    stop_event=self.push_stop_event)
            
            logger.info("Push completed!")
            
        except Exception as e:
            logger.error(f"Push error: {e}", exc_info=True)
        finally:
            self.push_thread_running = False
            self.button_state('normal')
            
    def open_advancedwindow(self) -> None:
        """Open advanced window"""
        if self.advanced_window is None or not self.advanced_window.winfo_exists():
            self.advanced_window = AdvancedWindow(self)
            self.advanced_window.focus()
        else:
            self.advanced_window.focus()
            
    def open_shopwindow(self) -> None:
        """Open shop window"""
        if self.shop_window is None or not self.shop_window.winfo_exists():
            self.shop_window = ShopWindow(self)
            self.shop_window.focus()
        else:
            self.shop_window.focus()
            
    def open_activitywindow(self) -> None:
        """Open activity window"""
        if self.activity_window is None or not self.activity_window.winfo_exists():
            self.activity_window = ActivityWindow(self)
            self.activity_window.focus()
        else:
            self.activity_window.focus()


class ActivityWindow(ctk.CTkToplevel):
    """Activity configuration window - original style"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("745x560")
        self.resizable(False, False)  # Disable window resizing
        self.title('Dailies Configuration')
        self.attributes("-topmost", True)
        
        self.config = parent.config
        self.activity_widgets = {}
        self.arena_widgets = {}
        self.events_widgets = {}
        self.bounties_widgets = {}
        
        # Activities Frame
        self.activityFrame = ctk.CTkFrame(master=self, width=235, height=500)
        self.activityFrame.place(x=10, y=10)
        ctk.CTkLabel(master=self.activityFrame, text="Activities:", font=("Arial", 15, 'bold')).place(x=10, y=5)
        
        activities = [
            ("Collect AFK Rewards", "checkbox", "collectRewards", "DAILIES"),
            ("Collect Mail", "checkbox", "collectMail", "DAILIES"),
            ("Companion Points", "checkbox", "companionPoints", "DAILIES"),
            ("Auto lend mercs?", "checkbox", "lendMercs", "DAILIES", 40),
            ("Fast Rewards", "entry", "fastrewards", "DAILIES"),
            ("Attempt Campaign", "checkbox", "attemptCampaign", "DAILIES"),
            ("Fountain of Time", "checkbox", "fountainOfTime", "DAILIES"),
            ("King's Tower", "checkbox", "kingsTower", "DAILIES"),
            ("Collect Inn Gifts", "checkbox", "collectInn", "DAILIES"),
            ("Guild Hunts", "checkbox", "guildHunt", "DAILIES"),
            ("Store Purchases", "checkbox", "storePurchases", "DAILIES"),
            ("Shop Refreshes", "entry", "shoprefreshes", "DAILIES", 40),
            ("Twisted Realm", "checkbox", "twistedRealm", "DAILIES"),
            ("Run Lab", "checkbox", "runLab", "DAILIES"),
            ("Collect Quests", "checkbox", "collectQuests", "DAILIES"),
            ("Collect Merchants", "checkbox", "collectMerchants", "DAILIES"),
            ("Use Bag Consumables", "checkbox", "useBagConsumables", "DAILIES"),
        ]
        
        y_offset = 30
        start_y = 40
        y = start_y
        for item in activities:
            label_text, widget_type, config_key, section = item[:4]
            x_offset = item[4] if len(item) > 4 else 10
            
            label = ctk.CTkLabel(master=self.activityFrame, text=label_text)
            label.place(x=x_offset, y=y)
            if widget_type == "checkbox":
                cb = ctk.CTkCheckBox(master=self.activityFrame, text=None, onvalue=True, offvalue=False)
                cb.place(x=200, y=y)
                self.activity_widgets[config_key] = cb
                if self.config.getboolean(section, config_key, fallback=False):
                    cb.select()
            elif widget_type == "entry":
                entry = ctk.CTkEntry(master=self.activityFrame, height=20, width=25)
                entry.insert('end', self.config.get(section, config_key, fallback='0'))
                entry.place(x=200, y=y)
                self.activity_widgets[config_key] = entry
            y += y_offset
                
        # Arena Frame
        self.ArenaFrame = ctk.CTkFrame(master=self, width=235, height=280)
        self.ArenaFrame.place(x=255, y=10)
        ctk.CTkLabel(master=self.ArenaFrame, text="Arena:", font=("Arial", 15, 'bold')).place(x=10, y=5)
        
        arena_items = [
            ("Battle Arena of Heroes", "checkbox", "battleArena", "ARENA"),
            ("Number of Battles", "entry", "arenaBattles", "ARENA", 40),
            ("Which Opponent", "entry", "arenaOpponent", "ARENA", 40),
            ("Collect Daily TS loot", "checkbox", "tsCollect", "ARENA"),
            ("Collect Gladiator Coins", "checkbox", "gladiatorCollect", "ARENA"),
        ]
        
        y = 40
        for item in arena_items:
            label_text, widget_type, config_key, section = item[:4]
            x_offset = item[4] if len(item) > 4 else 10
            
            label = ctk.CTkLabel(master=self.ArenaFrame, text=label_text)
            label.place(x=x_offset, y=y)
            if widget_type == "checkbox":
                cb = ctk.CTkCheckBox(master=self.ArenaFrame, text=None, onvalue=True, offvalue=False)
                cb.place(x=200, y=y)
                self.arena_widgets[config_key] = cb
                if self.config.getboolean(section, config_key, fallback=False):
                    cb.select()
            elif widget_type == "entry":
                entry = ctk.CTkEntry(master=self.ArenaFrame, height=20, width=25)
                entry.insert('end', self.config.get(section, config_key, fallback='5'))
                entry.place(x=198, y=y)
                self.arena_widgets[config_key] = entry
            y += y_offset
                
        # Events Frame
        self.eventsFrame = ctk.CTkFrame(master=self, width=235, height=210)
        self.eventsFrame.place(x=255, y=300)
        ctk.CTkLabel(master=self.eventsFrame, text="Events:", font=("Arial", 15, 'bold')).place(x=10, y=5)
        
        events_items = [
            ("Fight of Fates", "checkbox", "fightOfFates", "EVENTS"),
            ("Battle of Blood", "checkbox", "battleOfBlood", "EVENTS"),
            ("Circus Tour", "checkbox", "circusTour", "EVENTS"),
            ("Heroes of Esperia", "checkbox", "heroesOfEsperia", "EVENTS"),
        ]
        
        y = 40
        for label_text, widget_type, config_key, section in events_items:
            label = ctk.CTkLabel(master=self.eventsFrame, text=label_text)
            label.place(x=10, y=y)
            cb = ctk.CTkCheckBox(master=self.eventsFrame, text=None, onvalue=True, offvalue=False)
            cb.place(x=200, y=y)
            self.events_widgets[config_key] = cb
            if self.config.getboolean(section, config_key, fallback=False):
                cb.select()
            y += y_offset
        
        # Bounties Frame
        self.BountiesFrame = ctk.CTkFrame(master=self, width=235, height=310)
        self.BountiesFrame.place(x=500, y=10)
        ctk.CTkLabel(master=self.BountiesFrame, text="Bounties:", font=("Arial", 15, 'bold')).place(x=10, y=5)
        
        bounties_items = [
            ("Enable solo bounties", "checkbox", "dispatchSoloBounties", "BOUNTIES"),
            ("Enable team bounties", "checkbox", "dispatchTeamBounties", "BOUNTIES"),
            ("Dispatch Dust", "checkbox", "dispatchDust", "BOUNTIES"),
            ("Dispatch Diamonds", "checkbox", "dispatchDiamonds", "BOUNTIES"),
            ("Dispatch Shards", "checkbox", "dispatchShards", "BOUNTIES"),
            ("Dispatch Juice", "checkbox", "dispatchJuice", "BOUNTIES"),
            ("Number of Refreshes", "entry", "refreshes", "BOUNTIES"),
            ("# Remaining to Dispatch All", "entry", "remaining", "BOUNTIES"),
            ("Enable event bounties", "checkbox", "dispatchEventBounties", "BOUNTIES"),
        ]
        
        y = 40
        for label_text, widget_type, config_key, section in bounties_items:
            label = ctk.CTkLabel(master=self.BountiesFrame, text=label_text)
            label.place(x=10, y=y)
            if widget_type == "checkbox":
                cb = ctk.CTkCheckBox(master=self.BountiesFrame, text=None, onvalue=True, offvalue=False)
                cb.place(x=200, y=y)
                self.bounties_widgets[config_key] = cb
                if self.config.getboolean(section, config_key, fallback=False):
                    cb.select()
            elif widget_type == "entry":
                entry = ctk.CTkEntry(master=self.BountiesFrame, height=20, width=25)
                entry.insert('end', self.config.get(section, config_key, fallback='0'))
                entry.place(x=200, y=y)
                self.bounties_widgets[config_key] = entry
            y += y_offset
        
        # Misc Frame
        self.MiscFrame = ctk.CTkFrame(master=self, width=235, height=180)
        self.MiscFrame.place(x=500, y=330)
        ctk.CTkLabel(master=self.MiscFrame, text="Misc:", font=("Arial", 15, 'bold')).place(x=10, y=5)
        
        misc_items = [
            ("Delay start by x minutes", "entry", "delayedstart", "DAILIES"),
            ("Hibernate system when done", "checkbox", "hibernate", "DAILIES"),
        ]
        
        y = 40
        for label_text, widget_type, config_key, section in misc_items:
            label = ctk.CTkLabel(master=self.MiscFrame, text=label_text)
            label.place(x=10, y=y)
            if widget_type == "checkbox":
                cb = ctk.CTkCheckBox(master=self.MiscFrame, text=None, onvalue=True, offvalue=False)
                cb.place(x=200, y=y)
                self.activity_widgets[config_key] = cb
                if self.config.getboolean(section, config_key, fallback=False):
                    cb.select()
            elif widget_type == "entry":
                entry = ctk.CTkEntry(master=self.MiscFrame, height=20, width=25)
                entry.insert('end', self.config.get(section, config_key, fallback='0'))
                entry.place(x=200, y=y)
                self.activity_widgets[config_key] = entry
            y += y_offset
                
        # Save button
        self.activitySaveButton = ctk.CTkButton(
            master=self,
            text="Save",
            fg_color=["#10B981", "#059669"],
            hover_color=["#059669", "#047857"],
            width=120,
            command=self.activity_save
        )
        self.activitySaveButton.place(x=320, y=520)
        
    def activity_save(self) -> None:
        """Save all settings"""
        for config_key, widget in self.activity_widgets.items():
            if isinstance(widget, ctk.CTkCheckBox):
                self.config.set('DAILIES', config_key, 'True' if widget.get() else 'False')
            else:
                self.config.set('DAILIES', config_key, widget.get())
                
        for config_key, widget in self.arena_widgets.items():
            if isinstance(widget, ctk.CTkCheckBox):
                self.config.set('ARENA', config_key, 'True' if widget.get() else 'False')
            else:
                self.config.set('ARENA', config_key, widget.get())
                
        for config_key, cb in self.events_widgets.items():
            self.config.set('EVENTS', config_key, 'True' if cb.get() else 'False')
        
        for config_key, widget in self.bounties_widgets.items():
            if isinstance(widget, ctk.CTkCheckBox):
                self.config.set('BOUNTIES', config_key, 'True' if widget.get() else 'False')
            else:
                self.config.set('BOUNTIES', config_key, widget.get())
            
        self.config.save()
        self.destroy()


class ShopWindow(ctk.CTkToplevel):
    """Shop configuration window - original style"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("430x440")
        self.resizable(False, False)  # Disable window resizing
        self.title('Shop Options')
        self.attributes("-topmost", True)
        
        self.config = parent.config
        self.checkboxes = {}
        
        # Gold Frame
        self.shopGoldFrame = ctk.CTkFrame(master=self, width=200, height=380)
        self.shopGoldFrame.place(x=10, y=10)
        ctk.CTkLabel(master=self.shopGoldFrame, text="Gold Purchases:", font=("Arial", 15, 'bold')).place(x=10, y=5)
        
        # Diamond Frame
        self.shopDiamondFrame = ctk.CTkFrame(master=self, width=200, height=380)
        self.shopDiamondFrame.place(x=220, y=10)
        ctk.CTkLabel(master=self.shopDiamondFrame, text="Diamond Purchases:", font=("Arial", 15, 'bold')).place(x=10, y=5)
        
        gold_items = [
            ('shards_gold', 'Shards', 40),
            ('dust', 'Dust', 70),
            ('silver_emblem', 'Silver Emblems', 100),
            ('gold_emblem', 'Gold Emblems', 130),
            ('poe_coins', 'POE Coins', 160),
        ]
        
        diamond_items = [
            ('timegazer', 'Timegazer Card', 40),
            ('arcanestaffs', 'Arcane Staffs', 70),
            ('baits', 'Baits', 100),
            ('cores', 'Cores', 130),
            ('dust_diamond', 'Dust', 160),
            ('elite_soulstone', 'Elite Soulstone', 190),
            ('rare_soulstone', 'Rare Soulstone', 220),
            ('superb_soulstone', 'Superb Soulstone', 250),
            ('quick', 'Ignore above, do quickbuy', 350),
        ]
        
        for key, text, y in gold_items:
            label = ctk.CTkLabel(master=self.shopGoldFrame, text=text)
            label.place(x=10, y=y)
            checkbox = ctk.CTkCheckBox(master=self.shopGoldFrame, text=None, onvalue=True, offvalue=False)
            checkbox.place(x=165, y=y)
            self.checkboxes[key] = checkbox
            if self.config.getboolean('SHOP', key, fallback=False):
                checkbox.select()
        
        for key, text, y in diamond_items:
            label = ctk.CTkLabel(master=self.shopDiamondFrame, text=text)
            label.place(x=10, y=y)
            checkbox = ctk.CTkCheckBox(master=self.shopDiamondFrame, text=None, onvalue=True, offvalue=False)
            checkbox.place(x=165, y=y)
            self.checkboxes[key] = checkbox
            if self.config.getboolean('SHOP', key, fallback=False):
                checkbox.select()
                
        # Save button
        self.shopSaveButton = ctk.CTkButton(
            master=self,
            text="Save",
            fg_color=["#10B981", "#059669"],
            hover_color=["#059669", "#047857"],
            width=120,
            command=self.shop_save
        )
        self.shopSaveButton.place(x=155, y=400)
        
    def shop_save(self) -> None:
        """Save shop settings"""
        for key, checkbox in self.checkboxes.items():
            self.config.set('SHOP', key, 'True' if checkbox.get() else 'False')
        self.config.save()
        self.destroy()


class AdvancedWindow(ctk.CTkToplevel):
    """Advanced configuration window - original style"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("350x430")
        self.resizable(False, False)  # Disable window resizing
        self.title('Advanced Options')
        self.attributes("-topmost", True)
        
        self.config = parent.config
        self.entries = {}
        self.checkboxes = {}
        
        self.advancedFrame = ctk.CTkFrame(master=self, width=330, height=370)
        self.advancedFrame.place(x=10, y=10)
        
        ctk.CTkLabel(
            master=self.advancedFrame,
            text="Advanced Options:",
            font=("Arial", 15, 'bold')
        ).place(x=10, y=5)
        
        # Port
        ctk.CTkLabel(master=self.advancedFrame, text='Port:').place(x=10, y=40)
        self.port_entry = ctk.CTkEntry(master=self.advancedFrame, height=25, width=45)
        self.port_entry.insert('end', self.config.get('ADVANCED', 'port', fallback='0'))
        self.port_entry.place(x=275, y=40)
        self.entries['port'] = self.port_entry
        
        # Loading Multiplier
        ctk.CTkLabel(master=self.advancedFrame, text='Delay multiplier:').place(x=10, y=70)
        self.multiplier_entry = ctk.CTkEntry(master=self.advancedFrame, height=25, width=45)
        self.multiplier_entry.insert('end', self.config.get('ADVANCED', 'loadingMuliplier', fallback='1.0'))
        self.multiplier_entry.place(x=275, y=70)
        self.entries['loadingMuliplier'] = self.multiplier_entry
        
        # Victory Check Frequency
        ctk.CTkLabel(master=self.advancedFrame, text='Victory Check Frequency:').place(x=10, y=100)
        self.victory_entry = ctk.CTkEntry(master=self.advancedFrame, height=25, width=45)
        self.victory_entry.insert('end', self.config.get('PUSH', 'victoryCheck', fallback='1'))
        self.victory_entry.place(x=275, y=100)
        self.entries['victoryCheck'] = self.victory_entry
        
        # Suppress victory check spam
        ctk.CTkLabel(master=self.advancedFrame, text='Suppress victory check spam?').place(x=10, y=130)
        self.suppress_cb = ctk.CTkCheckBox(master=self.advancedFrame, text=None, onvalue=True, offvalue=False)
        self.suppress_cb.place(x=295, y=130)
        if self.config.getboolean('PUSH', 'suppressSpam', fallback=False):
            self.suppress_cb.select()
        self.checkboxes['suppressSpam'] = self.suppress_cb
        
        # Use popular formations
        ctk.CTkLabel(master=self.advancedFrame, text='Use popular formations').place(x=10, y=160)
        self.popular_cb = ctk.CTkCheckBox(master=self.advancedFrame, text=None, onvalue=True, offvalue=False)
        self.popular_cb.place(x=295, y=160)
        if self.config.getboolean('ADVANCED', 'popularformations', fallback=False):
            self.popular_cb.select()
        self.checkboxes['popularformations'] = self.popular_cb
        
        # Debug
        ctk.CTkLabel(master=self.advancedFrame, text='Debug Mode').place(x=10, y=190)
        self.debug_cb = ctk.CTkCheckBox(master=self.advancedFrame, text=None, onvalue=True, offvalue=False)
        self.debug_cb.place(x=295, y=190)
        if self.config.getboolean('ADVANCED', 'debug', fallback=False):
            self.debug_cb.select()
        self.checkboxes['debug'] = self.debug_cb
        
        # Emulator path
        ctk.CTkLabel(master=self.advancedFrame, text='Emulator path:').place(x=10, y=220)
        self.emulator_entry = ctk.CTkEntry(master=self.advancedFrame, height=25, width=100)
        self.emulator_entry.insert('end', self.config.get('ADVANCED', 'emulatorpath', fallback=''))
        self.emulator_entry.place(x=220, y=220)
        self.entries['emulatorpath'] = self.emulator_entry
        
        # Save button
        self.saveButton = ctk.CTkButton(
            master=self,
            text="Save",
            fg_color=["#10B981", "#059669"],
            hover_color=["#059669", "#047857"],
            width=120,
            command=self.advanced_save
        )
        self.saveButton.place(x=110, y=390)
        
    def advanced_save(self) -> None:
        """Save advanced settings"""
        for key, entry in self.entries.items():
            if key == 'victoryCheck':
                self.config.set('PUSH', key, entry.get())
            else:
                self.config.set('ADVANCED', key, entry.get())
            
        for key, cb in self.checkboxes.items():
            if key == 'suppressSpam':
                self.config.set('PUSH', key, 'True' if cb.get() else 'False')
            else:
                self.config.set('ADVANCED', key, 'True' if cb.get() else 'False')
            
        self.config.save()
        self.destroy()


class STDOutRedirector:
    """Redirect stdout to textbox with color support (using prefixes)"""
    
    def __init__(self, text_widget):
        self.text_space = text_widget
        
    def write(self, string: str) -> None:
        if not string:
            return
        
        # Handle empty lines (just newline) - no timestamp
        if string == '\n':
            self.text_space.insert('end', '\n')
            self.text_space.see('end')
            return
            
        # Check for color prefixes
        tag = None
        clean_string = string
        
        if string.startswith('ERR'):
            tag = 'error'
            clean_string = string[3:]
        elif string.startswith('WAR'):
            tag = 'warning'
            clean_string = string[3:]
        elif string.startswith('GRE'):
            tag = 'green'
            clean_string = string[3:]
        elif string.startswith('BLU'):
            tag = 'blue'
            clean_string = string[3:]
        elif string.startswith('PUR'):
            tag = 'purple'
            clean_string = string[3:]
        # Fallback for messages without prefix
        else:
            # Default to white/no color
            tag = None
            
        timestamp = '[' + datetime.datetime.now().strftime("%H:%M:%S") + '] '
        
        if tag:
            self.text_space.insert('end', timestamp + clean_string, tag)
        else:
            self.text_space.insert('end', timestamp + clean_string)
            
        self.text_space.see('end')
        
    def flush(self) -> None:
        pass


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description=f'AutoAFK {VERSION}')
    parser.add_argument('-c', '--config', 
                       default='settings.ini',
                       help='Path to configuration file (default: settings.ini)')
    parser.add_argument('-d', '--dailies', 
                       action='store_true',
                       help='Run dailies without GUI')
    parser.add_argument('-at', '--autotower',
                       action='store_true',
                       help='Run Auto-Towers function (push all towers)')
    parser.add_argument('-t', '--tower',
                       type=str,
                       help='Select a specific tower to push (kt, lb, m, w, gb, c, h)')
    parser.add_argument('-l', '--logging', 
                       action='store_true',
                       help='Enable file logging')
    return parser.parse_args()


def main() -> None:
    """Main entry point"""
    global args
    args = parse_arguments()
    
    # If --dailies flag, run headless
    if args.dailies:
        run_dailies_headless()
    # If --tower or --autotower flag, run tower push
    elif args.tower or args.autotower:
        run_tower_push_headless()
    else:
        # Run GUI
        app = App()
        app.mainloop()


def run_dailies_headless() -> None:
    """Run dailies without GUI"""
    print(f"AutoAFK {VERSION} - Headless Mode")
    print("https://github.com/Hammanek/AutoAFK")
    print("☕ Support: https://ko-fi.com/afksupporter")
    print()
    
    try:
        # Load config
        config = Config(args.config if args.config else 'settings.ini')
        
        # Initialize Logger (this sets up all handlers including custom levels)
        from src.utils.logger import Logger
        Logger()  # Initialize logger singleton
        
        # Initialize components
        print("[INFO] Initializing...")
        notification_manager = NotificationManager(config)
        
        # Enable notifications for all log messages BEFORE initializing device
        from src.utils.logger import add_notification_handler
        add_notification_handler(notification_manager)
        
        # Initialize core modules
        device_manager, image_recognition, game_controller = initialize_core_modules(config)
        if not device_manager:
            print("[ERROR] Failed to connect to device")
            return
        
        # Initialize activity manager
        activity_manager = ActivityManager(
            device_manager, image_recognition, game_controller,
            config, notification_manager
        )
        
        print("[INFO] Starting dailies...")
        
        # Execute dailies using shared function
        execute_dailies(activity_manager, None, None)
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup ADB processes
        if 'device_manager' in locals() and device_manager:
            print()  # Empty line without timestamp
            print("[INFO] Cleaning up ADB processes...")
            device_manager.disconnect()
            device_manager._kill_adb_processes()


def run_tower_push_headless() -> None:
    """Run tower push without GUI"""
    print(f"AutoAFK {VERSION} - Tower Push Mode")
    print("https://github.com/Hammanek/AutoAFK")
    print("☕ Support: https://ko-fi.com/afksupporter")
    print()
    
    try:
        # Load config
        config = Config(args.config if args.config else 'settings.ini')
        
        # Initialize Logger (this sets up all handlers including custom levels)
        from src.utils.logger import Logger
        Logger()  # Initialize logger singleton
        
        # Initialize components
        print("[INFO] Initializing...")
        notification_manager = NotificationManager(config)
        
        # Enable notifications for all log messages BEFORE initializing device
        from src.utils.logger import add_notification_handler
        add_notification_handler(notification_manager)
        
        # Initialize core modules
        device_manager, image_recognition, game_controller = initialize_core_modules(config)
        if not device_manager:
            print("[ERROR] Failed to connect to device")
            return
        
        # Initialize tower pusher
        pusher = TowerPusher(device_manager, image_recognition, game_controller,
                            config, notification_manager)
        
        # Get push settings
        formation = int(str(config.get('PUSH', 'formation', fallback='3'))[0:1])
        duration = config.getint('PUSH', 'victoryCheck', fallback=1)
        
        print(f"[INFO] Formation: {formation}, Victory Check: {duration} minutes")
        
        # Auto-tower mode (push all towers)
        if args.autotower:
            print("[INFO] Starting Auto-Towers (all towers)...")
            towers = [
                "King's Tower",
                "Lightbearer Tower", 
                "Mauler Tower",
                "Wilder Tower",
                "Graveborn Tower",
                "Celestial Tower",
                "Hypogean Tower"
            ]
            
            for tower in towers:
                print(f"\n[INFO] Pushing {tower}...")
                pusher.push_tower(tower, formation, duration)
                
        # Single tower mode
        elif args.tower:
            # Map short names to full names
            tower_map = {
                'kt': "King's Tower",
                'lb': 'Lightbearer Tower',
                'm': 'Mauler Tower',
                'w': 'Wilder Tower',
                'gb': 'Graveborn Tower',
                'c': 'Celestial Tower',
                'h': 'Hypogean Tower'
            }
            
            tower_name = tower_map.get(args.tower.lower(), args.tower)
            print(f"[INFO] Pushing {tower_name}...")
            pusher.push_tower(tower_name, formation, duration)
            
    except KeyboardInterrupt:
        print("\n[INFO] Tower push stopped by user")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup ADB processes
        if 'device_manager' in locals() and device_manager:
            print()  # Empty line without timestamp
            print("[INFO] Cleaning up ADB processes...")
            device_manager.disconnect()
            device_manager._kill_adb_processes()


if __name__ == '__main__':
    main()


